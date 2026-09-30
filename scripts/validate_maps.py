#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from release_context import get_release_context


def load(path: Path):
    if not path.is_file():
        raise SystemExit(f"ERROR: missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def valid_point(value):
    if not isinstance(value, dict):
        return False
    lat, lon = value.get("lat"), value.get("lon")
    return (
        isinstance(lat, (int, float))
        and not isinstance(lat, bool)
        and isinstance(lon, (int, float))
        and not isinstance(lon, bool)
        and -90 <= lat <= 90
        and -180 <= lon <= 180
    )


root = Path(sys.argv[1] if len(sys.argv) > 1 else "public/cdn/v2")
latest = get_release_context(root)
release = latest["release"]
manifest = load(release / "manifest.json")
index = load(release / "maps" / "index.json")
geo_rows = load(release / "geo" / "index.json").get("entities", [])
geo_ids = {row["id"] for row in geo_rows}
country_ids = {row["id"] for row in geo_rows if row.get("kind") == "country"}

objects = [load(p) for p in sorted((release / "objects").glob("*/*.json"))]
object_by_id = {row["id"]: row for row in objects}

expected_objects = {}
expected_viewpoints = {}
for obj in objects:
    point = (obj.get("geo") or {}).get("primary_location")
    if valid_point(point):
        expected_objects[obj["id"]] = obj
    for idx, viewpoint in enumerate((obj.get("visual_recon") or {}).get("viewpoints") or [], start=1):
        if isinstance(viewpoint, dict) and valid_point(viewpoint.get("coordinates")):
            expected_viewpoints[f"{obj['id']}:vp:{idx:02d}"] = obj

global_objects = load(release / "maps" / "indexes" / "objects.json")
global_viewpoints = load(release / "maps" / "indexes" / "viewpoints.json")
object_features = global_objects.get("features") or []
viewpoint_features = global_viewpoints.get("features") or []

if {f.get("id") for f in object_features} != set(expected_objects):
    raise SystemExit("ERROR: map object coverage does not match canonical objects with valid primary_location")
if {f.get("id") for f in viewpoint_features} != set(expected_viewpoints):
    raise SystemExit("ERROR: viewpoint coverage does not match canonical viewpoints with coordinates")

for feature in object_features:
    obj = expected_objects[feature["id"]]
    if not valid_point(feature.get("coordinates")):
        raise SystemExit(f"ERROR: invalid map coordinates: {feature['id']}")
    expected_geo = set((obj.get("geo") or {}).get("region_ids") or [])
    if set(feature.get("geo_ids") or []) != expected_geo & geo_ids:
        raise SystemExit(f"ERROR: map geo membership mismatch: {feature['id']}")
    country_id = (obj.get("geo") or {}).get("country_id")
    if feature.get("country_id") != country_id:
        raise SystemExit(f"ERROR: map country membership mismatch: {feature['id']}")

for feature in viewpoint_features:
    if feature.get("object_id") not in object_by_id:
        raise SystemExit(f"ERROR: unknown viewpoint object: {feature.get('id')}")
    if not valid_point(feature.get("coordinates")):
        raise SystemExit(f"ERROR: invalid viewpoint coordinates: {feature.get('id')}")

inventory = {row.get("path"): row for row in (manifest.get("files") or [])}
required_manifests = [index.get("sea")]
required_manifests += list((index.get("countries") or {}).values())
required_manifests += list((index.get("regions") or {}).values())

for rel in required_manifests:
    if not rel:
        raise SystemExit("ERROR: empty map manifest reference")
    map_manifest = load(release / rel)
    if map_manifest.get("label_language") != "en":
        raise SystemExit(f"ERROR: map labels are not English: {rel}")
    if rel not in inventory:
        raise SystemExit(f"ERROR: nested map manifest missing from release inventory: {rel}")
    object_index = map_manifest.get("object_index")
    viewpoint_index = map_manifest.get("viewpoint_index")
    if not object_index or not viewpoint_index:
        raise SystemExit(f"ERROR: scoped feature sources missing: {rel}")
    scoped_objects = load(release / object_index).get("features") or []
    scoped_viewpoints = load(release / viewpoint_index).get("features") or []

    if map_manifest.get("scope") == "country":
        country_id = map_manifest.get("country_id")
        if country_id not in country_ids:
            raise SystemExit(f"ERROR: invalid country map: {rel}")
        if any(f.get("country_id") != country_id for f in scoped_objects):
            raise SystemExit(f"ERROR: foreign object in country map: {rel}")

    if map_manifest.get("scope") == "region":
        geo_id = map_manifest.get("geo_id")
        if geo_id not in geo_ids:
            raise SystemExit(f"ERROR: invalid region map: {rel}")
        if any(geo_id not in (f.get("geo_ids") or []) for f in scoped_objects):
            raise SystemExit(f"ERROR: object outside region map: {rel}")
        if any(geo_id not in (f.get("geo_ids") or []) for f in scoped_viewpoints):
            raise SystemExit(f"ERROR: viewpoint outside region map: {rel}")

print(json.dumps({
    "status": "ok",
    "release_id": latest["release_id"],
    "map_objects": len(object_features),
    "viewpoints": len(viewpoint_features),
    "map_manifests": len(required_manifests),
}, indent=2))
