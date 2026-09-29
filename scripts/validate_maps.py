#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "public/cdn/v2")
latest = json.loads((root / "latest.json").read_text(encoding="utf-8"))
release = root / latest["release_id"]

def load(rel):
    path = release / rel
    if not path.is_file(): raise SystemExit(f"ERROR: missing map reference: {rel}")
    return json.loads(path.read_text(encoding="utf-8"))

index = load("maps/index.json")
object_ids = {p.stem for p in (release / "objects").glob("*/*.json")}
features = load("maps/indexes/objects.json").get("features", [])
for row in features:
    if row.get("id") not in object_ids: raise SystemExit(f"ERROR: unknown map object: {row.get('id')}")
    point = row.get("coordinates") or {}; lat, lon = point.get("lat"), point.get("lon")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90 or not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        raise SystemExit(f"ERROR: invalid map coordinate: {row.get('id')}")
for rel in [index.get("sea"), *(index.get("countries") or {}).values(), *(index.get("regions") or {}).values()]:
    manifest = load(rel)
    bounds = load(manifest["bounds"])
    if bounds and not (bounds["west"] <= bounds["east"] and bounds["south"] <= bounds["north"]):
        raise SystemExit(f"ERROR: invalid bounds: {rel}")
    load(manifest["layers"])
print(json.dumps({"status": "ok", "countries": len(index.get("countries") or {}), "regions": len(index.get("regions") or {}), "objects": len(features)}, indent=2))
