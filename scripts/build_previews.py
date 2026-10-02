#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
CDN = ROOT / "public" / "cdn" / "v2"
PREVIEW_ROOT = CDN / "previews"
MAX_DOWNLOAD_BYTES = 40 * 1024 * 1024
MAX_SIZE = (720, 480)
USER_AGENT = "ExpeditionSoutheastAsiaPreviewBuilder/1.2 (+https://github.com/KazartsevEV/south-eats_expedition)"
WIKIMEDIA_DELAY_SECONDS = 1.25
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


def is_wikimedia(url: str) -> bool:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    return host.endswith("wikimedia.org")


def wikimedia_thumbnail_url(source_url: str, source_page: str | None) -> str:
    filename = None
    if source_page and "/wiki/File:" in source_page:
        filename = source_page.split("/wiki/File:", 1)[1]
    elif "upload.wikimedia.org" in source_url:
        filename = urllib.parse.unquote(urllib.parse.urlsplit(source_url).path.rsplit("/", 1)[-1])
    if not filename:
        return source_url
    filename = urllib.parse.quote(urllib.parse.unquote(filename), safe="()_',.-")
    return f"https://commons.wikimedia.org/wiki/Special:Redirect/file/{filename}?width={MAX_SIZE[0]}"


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


def build_webp(source_url: str, output: Path, source_page: str | None = None):
    fetch_url = wikimedia_thumbnail_url(source_url, source_page) if is_wikimedia(source_url) else source_url
    data = download_bytes(fetch_url)
    try:
        with Image.open(io.BytesIO(data)) as src:
            try:
                src.seek(0)
            except EOFError:
                pass
            img = ImageOps.exif_transpose(src)
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            if img.mode not in {"RGB", "RGBA"}:
                if "A" in img.getbands():
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
            output.parent.mkdir(parents=True, exist_ok=True)
            tmp = output.with_suffix(".tmp.webp")
            img.save(tmp, "WEBP", quality=80, method=6)
            tmp.replace(output)
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"cannot decode image: {exc}") from exc


def object_country(object_id: str) -> str:
    parts = object_id.split("_")
    if len(parts) < 3 or parts[0] != "obj":
        raise RuntimeError(f"unexpected object id: {object_id}")
    return parts[1]


def patch_search_file(path: Path, preview_by_object: dict[str, str]):
    if not path.exists():
        return
    doc = load(path)
    changed = False
    for row in doc.get("objects") or []:
        object_id = row.get("id")
        preview = preview_by_object.get(object_id)
        if preview and row.get("preview_asset") != preview:
            row["preview_asset"] = preview
            changed = True
    if changed:
        dump(path, doc)


def media_candidates(release: Path, cc: str, object_doc: dict, cover_media_id: str) -> list[tuple[str, Path, dict]]:
    media = object_doc.get("media") or {}
    ids = [cover_media_id] + list(media.get("gallery_ids") or [])
    seen = set()
    out = []
    for media_id in ids:
        if not media_id or media_id in seen:
            continue
        seen.add(media_id)
        media_path = release / "media" / cc / f"{media_id}.json"
        if not media_path.exists():
            continue
        media_doc = load(media_path)
        if media_doc.get("url"):
            out.append((media_id, media_path, media_doc))
    return out


def main():
    latest = load(CDN / "latest.json")
    release_id = latest["release_id"]
    release = CDN / release_id
    global_search_path = release / "search" / "global.json"
    search = load(global_search_path)
    rows = search.get("objects") or []
    if not rows:
        raise RuntimeError("search/global.json has no objects")

    failures = []
    preview_by_object: dict[str, str] = {}
    preview_source_by_object: dict[str, str] = {}
    required_files: set[Path] = set()

    for row in rows:
        object_id = row.get("id")
        cover_media_id = row.get("cover_media_id")
        if not object_id:
            failures.append("<missing-id>: object id is required for local preview")
            continue

        cc = object_country(object_id)
        object_path = release / "objects" / cc / f"{object_id}.json"
        if not object_path.exists():
            failures.append(f"{object_id}: canonical object file missing")
            continue
        object_doc = load(object_path)

        if not cover_media_id:
            if object_doc.get("status") == "draft":
                continue
            failures.append(f"{object_id}: cover_media_id is required for local preview")
            continue

        preview_rel = f"previews/{cc}/{object_id}.webp"
        preview_path = CDN / preview_rel
        required_files.add(preview_path)
        preview_by_object[object_id] = preview_rel

        candidates = media_candidates(release, cc, object_doc, cover_media_id)
        if not candidates:
            failures.append(f"{object_id}: no usable cover/gallery media URLs for local preview")
            continue

        chosen_media_id = None
        chosen_media_path = None
        chosen_media_doc = None

        if preview_path.exists() and preview_path.stat().st_size >= 256:
            chosen_media_id, chosen_media_path, chosen_media_doc = candidates[0]
        else:
            candidate_errors = []
            for media_id, media_path, media_doc in candidates:
                source_url = media_doc.get("url")
                try:
                    build_webp(source_url, preview_path, media_doc.get("source_page"))
                    chosen_media_id = media_id
                    chosen_media_path = media_path
                    chosen_media_doc = media_doc
                    break
                except Exception as exc:
                    candidate_errors.append(f"{media_id}: {source_url}: {exc}")
            if chosen_media_id is None:
                failures.append(f"{object_id}: all preview candidates failed: " + " | ".join(candidate_errors))
                continue

        preview_source_by_object[object_id] = chosen_media_id
        source_url = chosen_media_doc.get("url")
        chosen_media_doc["preview_asset"] = preview_rel
        chosen_media_doc["preview"] = {
            "format": "webp",
            "max_width": MAX_SIZE[0],
            "max_height": MAX_SIZE[1],
            "derived_from": source_url,
            "object_id": object_id,
        }
        dump(chosen_media_path, chosen_media_doc)

        object_doc.setdefault("media", {})["preview_asset"] = preview_rel
        object_doc["media"]["preview_source_media_id"] = chosen_media_id
        dump(object_path, object_doc)

    if failures:
        raise RuntimeError("preview build failed:\n" + "\n".join(failures))

    patch_search_file(global_search_path, preview_by_object)
    for cc in sorted({object_country(x) for x in preview_by_object}):
        patch_search_file(release / "search" / f"{cc}.json", preview_by_object)

    for object_id, preview_rel in preview_by_object.items():
        card_path = release / "views" / "object-cards" / f"{object_id}.json"
        if card_path.exists():
            card = load(card_path)
            card["preview_asset"] = preview_rel
            dump(card_path, card)

    if PREVIEW_ROOT.exists():
        for path in PREVIEW_ROOT.rglob("*.webp"):
            if path not in required_files:
                path.unlink()
        for directory in sorted((p for p in PREVIEW_ROOT.rglob("*") if p.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    index = {
        "release_id": release_id,
        "count": len(preview_by_object),
        "format": "webp",
        "max_size": {"width": MAX_SIZE[0], "height": MAX_SIZE[1]},
        "items": [
            {
                "object_id": object_id,
                "source_media_id": preview_source_by_object[object_id],
                "preview_asset": preview_by_object[object_id],
            }
            for object_id in sorted(preview_by_object)
        ],
    }
    dump(PREVIEW_ROOT / "index.json", index)
    print(json.dumps({"status": "ok", "release_id": release_id, "previews": len(preview_by_object)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
