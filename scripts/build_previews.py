#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import shutil
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
USER_AGENT = "ExpeditionSoutheastAsiaPreviewBuilder/1.0 (+https://github.com/KazartsevEV/south-eats_expedition)"


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


def download_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        normalized_url(url),
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        data = response.read(MAX_DOWNLOAD_BYTES + 1)
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise RuntimeError(f"image exceeds {MAX_DOWNLOAD_BYTES} bytes")
        if not data:
            raise RuntimeError("empty response")
        return data


def build_webp(source_url: str, output: Path):
    data = download_bytes(source_url)
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
    objects_by_media: dict[str, list[str]] = defaultdict(list)
    required_files: set[Path] = set()

    for row in rows:
        object_id = row.get("id")
        media_id = row.get("cover_media_id")
        if not object_id or not media_id:
            failures.append(f"{object_id or '<missing-id>'}: cover_media_id is required for local preview")
            continue
        cc = object_country(object_id)
        media_path = release / "media" / cc / f"{media_id}.json"
        if not media_path.exists():
            failures.append(f"{object_id}: missing canonical media {media_path.relative_to(CDN)}")
            continue
        media_doc = load(media_path)
        source_url = media_doc.get("url")
        if not source_url:
            failures.append(f"{object_id}: cover media {media_id} has no URL")
            continue

        preview_rel = f"previews/{cc}/{media_id}.webp"
        preview_path = CDN / preview_rel
        required_files.add(preview_path)
        preview_by_object[object_id] = preview_rel
        objects_by_media[media_id].append(object_id)

        if not preview_path.exists() or preview_path.stat().st_size < 256:
            try:
                build_webp(source_url, preview_path)
            except Exception as exc:
                failures.append(f"{object_id}: {media_id}: {source_url}: {exc}")
                continue

        media_doc["preview_asset"] = preview_rel
        media_doc["preview"] = {
            "format": "webp",
            "max_width": MAX_SIZE[0],
            "max_height": MAX_SIZE[1],
            "derived_from": source_url,
        }
        dump(media_path, media_doc)

        object_path = release / "objects" / cc / f"{object_id}.json"
        if not object_path.exists():
            failures.append(f"{object_id}: canonical object file missing")
            continue
        object_doc = load(object_path)
        object_doc.setdefault("media", {})["preview_asset"] = preview_rel
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
                "media_id": media_id,
                "preview_asset": preview_by_object[object_ids[0]],
                "object_ids": object_ids,
            }
            for media_id, object_ids in sorted(objects_by_media.items())
        ],
    }
    dump(PREVIEW_ROOT / "index.json", index)
    print(json.dumps({"status": "ok", "release_id": release_id, "previews": len(preview_by_object)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
