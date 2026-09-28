#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "public/cdn/v2")
LATEST = ROOT / "latest.json"

def load(p):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)

if not LATEST.exists(): fail(f"missing {LATEST}")
latest = load(LATEST)
release_id = latest.get("release_id")
if not release_id: fail("latest.json missing release_id")
release = ROOT / release_id
manifest_path = release / "manifest.json"
if not manifest_path.exists(): fail(f"missing manifest {manifest_path}")
manifest = load(manifest_path)
if manifest.get("release_id") != release_id: fail("latest/manifest release_id mismatch")
if manifest.get("schema_version") != latest.get("schema_version"): fail("latest/manifest schema_version mismatch")

for p in sorted(release.rglob("*.json")):
    try: load(p)
    except Exception as e: fail(f"invalid JSON {p}: {e}")

for item in manifest.get("files", []):
    rel = item.get("path")
    if not rel: fail("manifest file item missing path")
    p = release / rel
    if not p.exists(): fail(f"manifest references missing file: {rel}")
    b = p.read_bytes()
    if len(b) != item.get("bytes"): fail(f"size mismatch: {rel}")
    sha = hashlib.sha256(b).hexdigest()
    if sha != item.get("sha256"): fail(f"sha256 mismatch: {rel}")

countries = load(release / "countries.json")
objects = load(release / "search/objects.json")
places = load(release / "search/places.json")
qa = load(release / "qa.json")

def seq(obj):
    if isinstance(obj, list): return obj
    if isinstance(obj, dict):
        for k in ("countries","items","objects","places","results"):
            if isinstance(obj.get(k), list): return obj[k]
    fail("cannot identify list payload")

country_rows = seq(countries)
object_rows = seq(objects)
place_rows = seq(places)

expected = manifest.get("totals", {})
if len(country_rows) != expected.get("countries"): fail(f"country count {len(country_rows)} != {expected.get('countries')}")
if len(object_rows) != expected.get("objects"): fail(f"object count {len(object_rows)} != {expected.get('objects')}")
if len(place_rows) != expected.get("places"): fail(f"place count {len(place_rows)} != {expected.get('places')}")
if qa.get("failures") not in ({}, None): fail(f"qa failures present: {qa.get('failures')}")

def first_key(row, keys):
    if not isinstance(row, dict): return None
    for k in keys:
        if row.get(k): return str(row[k])
    return None

ids = [first_key(r,("id","object_id","slug")) for r in object_rows]
ids = [x for x in ids if x]
if len(ids) != len(set(ids)): fail("duplicate object id/slug in search index")

print(json.dumps({
    "status":"ok",
    "release_id":release_id,
    "countries":len(country_rows),
    "objects":len(object_rows),
    "places":len(place_rows),
    "manifest_files":len(manifest.get("files", []))
}, ensure_ascii=False, indent=2))
