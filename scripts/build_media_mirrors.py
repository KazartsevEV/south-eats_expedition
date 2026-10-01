#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
CDN = ROOT / "public" / "cdn" / "v2"
MIRROR_ROOT = CDN / "media-mirror"

MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
MIRROR_MAX_SIZE = (1920, 1920)
WEBP_QUALITY = 84
USER_AGENT = "ExpeditionSoutheastAsiaMediaMirror/1.0 (+https://github.com/KazartsevEV/south-eats_expedition)"
WIKIMEDIA_DELAY_SECONDS = 0.6
_last_wikimedia_request = 0.0


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def normalized_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%:@()+,;=-_.~")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def host_of(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def is_wikimedia(url: str) -> bool:
    host = host_of(url)
    return host.endswith("wikimedia.org") or host.endswith("wikipedia.org")


def wikimedia_file_name(source_url: str, source_page: str | None) -> str | None:
    if source_page:
        decoded_page = urllib.parse.unquote(source_page)
        marker = "/wiki/File:"
        if marker in decoded_page:
            return decoded_page.split(marker, 1)[1]
    decoded_url = urllib.parse.unquote(source_url)
    if "/wiki/Special:FilePath/" in decoded_url:
        return decoded_url.split("/wiki/Special:FilePath/", 1)[1].split("?", 1)[0]
    if "/wiki/Special:Redirect/file/" in decoded_url:
        return decoded_url.split("/wiki/Special:Redirect/file/", 1)[1].split("?", 1)[0]
    if host_of(source_url) == "upload.wikimedia.org":
        return urllib.parse.unquote(urllib.parse.urlsplit(source_url).path.rsplit("/", 1)[-1])
    return None


def fetch_url_for(source_url: str, source_page: str | None) -> str:
    filename = wikimedia_file_name(source_url, source_page)
    if filename:
        filename = urllib.parse.quote(urllib.parse.unquote(filename), safe="()_',.-")
        return (
            "https://commons.wikimedia.org/wiki/Special:Redirect/file/"
            f"{filename}?width={MIRROR_MAX_SIZE[0]}"
        )
    return source_url


def throttle_wikimedia():
    global _last_wikimedia_request
    now = time.monotonic()
    remaining = WIKIMEDIA_DELAY_SECONDS - (now - _last_wikimedia_request)
    if remaining > 0:
        time.sleep(remaining)
    _last_wikimedia_request = time.monotonic()


def download_bytes(url: str) -> bytes:
    attempts = 5 if is_wikimedia(url) else 3
    delays = [3, 8, 18, 35, 60]
    last_error = None
    for attempt in range(attempts):
        if is_wikimedia(url):
            throttle_wikimedia()
        req = urllib.request.Request(
            normalized_url(url),
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read(MAX_DOWNLOAD_BYTES + 1)
                if len(data) > MAX_DOWNLOAD_BYTES:
                    raise RuntimeError(f"image exceeds {MAX_DOWNLOAD_BYTES} bytes")
                if not data:
                    raise RuntimeError("empty response")
                return data
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts - 1:
                raise
            retry_after = exc.headers.get("Retry-After")
            try:
                wait = max(float(retry_after), delays[attempt]) if retry_after else delays[attempt]
            except (TypeError, ValueError):
                wait = delays[attempt]
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(delays[attempt])
    raise RuntimeError(f"download failed: {last_error}")


def write_mirror(source_url: str, source_page: str | None, output: Path):
    fetch_url = fetch_url_for(source_url, source_page)
    data = download_bytes(fetch_url)
    try:
        with Image.open(io.BytesIO(data)) as src:
            try:
                src.seek(0)
            except EOFError:
                pass
            img = ImageOps.exif_transpose(src)
            img.thumbnail(MIRROR_MAX_SIZE, Image.Resampling.LANCZOS)
            if img.mode not in {"RGB", "RGBA"}:
                if "A" in img.getbands():
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
            output.parent.mkdir(parents=True, exist_ok=True)
            tmp = output.with_suffix(".tmp.webp")
            img.save(tmp, "WEBP", quality=WEBP_QUALITY, method=6)
            tmp.replace(output)
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"cannot decode image: {exc}") from exc


def media_files(release: Path):
    for country_dir in sorted((release / "media").glob("[a-z][a-z]")):
        if not country_dir.is_dir():
            continue
        for path in sorted(country_dir.glob("med_*.json")):
            yield country_dir.name, path


def main():
    latest = load(CDN / "latest.json")
    release_id = latest["release_id"]
    release = CDN / release_id

    failures = []
    required_files: set[Path] = set()
    mirror_rows = []

    for cc, media_path in media_files(release):
        media = load(media_path)
        media_id = media.get("id")
        source_url = media.get("url")
        if not media_id or not source_url:
            failures.append(f"{media_path.relative_to(release)}: missing id/url")
            continue

        mirror_rel = f"media-mirror/{cc}/{media_id}.webp"
        mirror_path = CDN / mirror_rel
        required_files.add(mirror_path)

        if not mirror_path.exists() or mirror_path.stat().st_size < 256:
            try:
                write_mirror(source_url, media.get("source_page"), mirror_path)
            except Exception as exc:
                failures.append(f"{media_id}: {source_url}: {exc}")
                continue

        media["mirror_asset"] = mirror_rel
        media["mirror"] = {
            "format": "webp",
            "max_width": MIRROR_MAX_SIZE[0],
            "max_height": MIRROR_MAX_SIZE[1],
            "quality": WEBP_QUALITY,
            "derived_from": source_url,
        }
        dump(media_path, media)
        mirror_rows.append({
            "media_id": media_id,
            "country": cc,
            "mirror_asset": mirror_rel,
        })

    if failures:
        raise RuntimeError("media mirror build failed:\n" + "\n".join(failures))

    if MIRROR_ROOT.exists():
        for path in MIRROR_ROOT.rglob("*.webp"):
            if path not in required_files:
                path.unlink()
        for directory in sorted((p for p in MIRROR_ROOT.rglob("*") if p.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    dump(MIRROR_ROOT / "index.json", {
        "release_id": release_id,
        "count": len(mirror_rows),
        "format": "webp",
        "max_size": {"width": MIRROR_MAX_SIZE[0], "height": MIRROR_MAX_SIZE[1]},
        "items": sorted(mirror_rows, key=lambda row: row["media_id"]),
    })
    print(json.dumps({
        "status": "ok",
        "release_id": release_id,
        "mirrors": len(mirror_rows),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
