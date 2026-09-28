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

COORDINATE_TYPES = {
    "center", "entrance", "trailhead", "summit", "viewpoint", "pier", "parking",
    "cave_entrance", "waterfall_base", "archaeological_core", "temple_entrance",
}

def validate_point(point, context):
    if point is None:
        return
    if not isinstance(point, dict):
        fail(f"{context}: geodata point is not an object")
    point_type = point.get("type")
    if point_type not in COORDINATE_TYPES:
        fail(f"{context}: invalid coordinate type {point_type!r}")
    coords = point.get("coordinates") or {}
    lat = coords.get("lat")
    lon = coords.get("lon")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool) or not (-90 <= lat <= 90):
        fail(f"{context}: invalid latitude {lat!r}")
    if not isinstance(lon, (int, float)) or isinstance(lon, bool) or not (-180 <= lon <= 180):
        fail(f"{context}: invalid longitude {lon!r}")
    elevation = coords.get("elevation_m")
    if elevation is not None and (not isinstance(elevation, (int, float)) or isinstance(elevation, bool)):
        fail(f"{context}: invalid elevation {elevation!r}")
    accuracy = point.get("accuracy")
    if accuracy not in {"high", "medium", "approximate", "unknown"}:
        fail(f"{context}: invalid accuracy {accuracy!r}")
    if not (point.get("gps") or {}).get("decimal"):
        fail(f"{context}: missing human-readable decimal GPS")

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
lodging_index_path = release / "infrastructure" / "lodging" / "index.json"
if not lodging_index_path.exists():
    fail("missing normalized lodging index")
lodging_rows = load(lodging_index_path).get("lodging") or []
lodging_ids = {row.get("id") for row in lodging_rows if row.get("id")}
source_index_path = release / "sources" / "index.json"
if not source_index_path.exists():
    fail("missing normalized source index")
source_rows = load(source_index_path).get("sources") or []
source_ids = {row.get("id") for row in source_rows if row.get("id")}
if len(source_ids) != len(source_rows):
    fail("source index contains empty or duplicate ids")
for row in source_rows:
    path = row.get("detail_path")
    if not path or not (release / path).exists():
        fail(f"source detail missing: {row.get('id')} -> {path}")
if len(lodging_ids) != len(lodging_rows):
    fail("lodging index contains empty or duplicate ids")
for row in lodging_rows:
    path = row.get("detail_path")
    if not path or not (release / path).exists():
        fail(f"lodging detail missing: {row.get('id')} -> {path}")

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

geodata_contract_path = release / "schema" / "geodata-contract.json"
if not geodata_contract_path.exists():
    fail("missing schema/geodata-contract.json")
geodata_contract = load(geodata_contract_path)
if geodata_contract.get("crs") != "WGS84" or geodata_contract.get("epsg") != 4326:
    fail("geodata contract must be WGS84 / EPSG:4326")

# Contract: story is emitted once; legacy source prose keys must not leak.
for row in objects:
    detail = load(release / row["detail_path"])
    if "why_go" in detail or "annotation" in detail:
        fail(f"duplicate prose field leaked into {row['detail_path']}")
    story = (detail.get("story") or {}).get("narrative")
    if not story:
        fail(f"missing canonical story in {row['detail_path']}")
    identity = detail.get("identity") or {}
    if "accommodation" in (detail.get("visit") or {}):
        fail(f"embedded accommodation leaked into {row['detail_path']}")
    if "photo_video" in (detail.get("media") or {}):
        fail(f"embedded photo_video leaked into {row['detail_path']}")
    provenance = detail.get("provenance") or {}
    if "sources" in provenance:
        fail(f"embedded sources leaked into {row['detail_path']}")
    for source_id in provenance.get("source_refs") or []:
        if source_id not in source_ids:
            fail(f"unknown source reference {source_id} in {row['detail_path']}")
    visual_recon = detail.get("visual_recon") or {}
    if not isinstance(visual_recon, dict):
        fail(f"invalid visual_recon in {row['detail_path']}")
    for lodging_id in (detail.get("visit") or {}).get("lodging_ids") or []:
        if lodging_id not in lodging_ids:
            fail(f"unknown lodging reference {lodging_id} in {row['detail_path']}")
    if not identity.get("narrow"):
        fail(f"missing narrow in {row['detail_path']}")
    if not identity.get("object_type"):
        fail(f"missing object_type in {row['detail_path']}")
    geo = detail.get("geo") or {}
    if geo.get("crs") != "WGS84" or geo.get("epsg") != 4326:
        fail(f"invalid/missing WGS84 contract in {row['detail_path']}")
    primary = geo.get("primary_location")
    validate_point(primary, row["detail_path"] + ":primary_location")
    for index, point in enumerate(geo.get("points") or []):
        validate_point(point, row["detail_path"] + f":points[{index}]")
    search_coords = row.get("coordinates")
    detail_coords = (primary or {}).get("coordinates")
    if search_coords != detail_coords:
        fail(f"search/detail coordinate mismatch in {row['detail_path']}")

print(json.dumps({
    "status": "ok",
    "release_id": release_id,
    "schema_version": manifest.get("schema_version"),
    "source_files": len(sources),
    "published_countries": manifest.get("published_countries"),
    **checks,
    "manifest_files": len(manifest.get("files", [])),
}, ensure_ascii=False, indent=2))
