#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
CDN = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "public" / "cdn" / "v2")

def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

# Source guard: never accept empty/truncated JSON again.
sources = sorted(SRC.glob("*.json"))
if not sources:
    fail("no source country files")
for path in sources:
    if path.stat().st_size < 10_000:
        fail(f"source suspiciously small: {path} ({path.stat().st_size} bytes)")
    try:
        doc = load(path)
    except Exception as exc:
        fail(f"invalid source JSON {path}: {exc}")
    if not (doc.get("meta") or {}).get("country"):
        fail(f"source missing meta.country: {path}")
    if not isinstance((doc.get("travel") or {}).get("objects"), list):
        fail(f"source missing travel.objects: {path}")

latest_path = CDN / "latest.json"
if not latest_path.exists():
    fail(f"missing {latest_path}")
latest = load(latest_path)
release_id = latest.get("release_id")
if not release_id:
    fail("latest.json missing release_id")
release = CDN / release_id
manifest_path = release / "manifest.json"
if not manifest_path.exists():
    fail(f"missing {manifest_path}")
manifest = load(manifest_path)

if manifest.get("release_id") != release_id:
    fail("latest/manifest release_id mismatch")
if manifest.get("schema_version") != latest.get("schema_version"):
    fail("latest/manifest schema_version mismatch")

# Every generated JSON must parse.
for path in sorted(release.rglob("*.json")):
    try:
        load(path)
    except Exception as exc:
        fail(f"invalid generated JSON {path}: {exc}")

# Manifest integrity.
for item in manifest.get("files", []):
    rel = item.get("path")
    if not rel:
        fail("manifest file entry missing path")
    path = release / rel
    if not path.exists():
        fail(f"manifest references missing file: {rel}")
    payload = path.read_bytes()
    if len(payload) != item.get("bytes"):
        fail(f"size mismatch: {rel}")
    if hashlib.sha256(payload).hexdigest() != item.get("sha256"):
        fail(f"sha256 mismatch: {rel}")

countries = load(release / "countries.json").get("countries", [])
objects = load(release / "search" / "objects.json").get("objects", [])
places = load(release / "search" / "places.json").get("places", [])
qa = load(release / "qa.json")

totals = manifest.get("totals") or {}
checks = {
    "countries": len(countries),
    "objects": len(objects),
    "places": len(places),
}
for key, actual in checks.items():
    if actual != totals.get(key):
        fail(f"{key} count {actual} != manifest {totals.get(key)}")

ids = [row.get("id") for row in objects]
if any(not x for x in ids):
    fail("object search index contains row without id")
if len(ids) != len(set(ids)):
    fail("duplicate object id in search index")

place_ids = [row.get("id") for row in places]
if any(not x for x in place_ids):
    fail("place search index contains row without id")
if len(place_ids) != len(set(place_ids)):
    duplicates = sorted({x for x in place_ids if place_ids.count(x) > 1})
    fail(f"duplicate place id in search index: {duplicates[:20]}")

# Reference release is expected to have full coverage of the fields requested
# for object cards. Single-image galleries are allowed and explicitly marked.
failures = qa.get("failures") or {}
if failures:
    fail(f"QA coverage failures: {json.dumps(failures, ensure_ascii=False)}")

# Contract: story is emitted once; legacy source prose keys must not leak.
for row in objects:
    detail = load(release / row["detail_path"])
    if "why_go" in detail or "annotation" in detail:
        fail(f"duplicate prose field leaked into {row['detail_path']}")
    story = (detail.get("story") or {}).get("narrative")
    if not story:
        fail(f"missing canonical story in {row['detail_path']}")
    identity = detail.get("identity") or {}
    if not identity.get("narrow"):
        fail(f"missing narrow in {row['detail_path']}")
    if not identity.get("object_type"):
        fail(f"missing object_type in {row['detail_path']}")

print(json.dumps({
    "status": "ok",
    "release_id": release_id,
    "schema_version": manifest.get("schema_version"),
    "source_files": len(sources),
    "published_countries": manifest.get("published_countries"),
    **checks,
    "manifest_files": len(manifest.get("files", [])),
}, ensure_ascii=False, indent=2))
