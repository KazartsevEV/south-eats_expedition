#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def bounds(features):
    if not features:
        return None
    lats = [f["coordinates"]["lat"] for f in features]
    lons = [f["coordinates"]["lon"] for f in features]
    return {"west": min(lons), "south": min(lats), "east": max(lons), "north": max(lats)}


def file_entry(path: Path, release: Path):
    raw = path.read_bytes()
    return {
        "path": path.relative_to(release).as_posix(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def build(root: Path):
    latest = load(root / "latest.json")
    release = root / latest["release_id"]
    manifest_path = release / "manifest.json"
    manifest = load(manifest_path)

    geo_rows = load(release / "geo" / "index.json").get("entities", [])
    geo_ids = {row["id"] for row in geo_rows}
    objects = [load(p) for p in sorted((release / "objects").glob("*/*.json"))]

    object_features = []
    viewpoint_features = []
    by_country = defaultdict(list)
    by_region = defaultdict(list)
    vp_by_country = defaultdict(list)
    vp_by_region = defaultdict(list)

    for obj in objects:
        geo = obj.get("geo") or {}
        point = geo.get("primary_location")
        country_id = geo.get("country_id")
        region_ids = [g for g in (geo.get("region_ids") or []) if g in geo_ids]
        if valid_point(point):
            feature = {
                "id": obj["id"],
                "layer": "object",
                "country_id": country_id,
                "geo_ids": region_ids,
                "coordinates": {"lat": point["lat"], "lon": point["lon"]},
                "detail": f"objects/{obj['id'].split('_')[1]}/{obj['id']}.json",
            }
            object_features.append(feature)
            if country_id:
                by_country[country_id].append(feature)
            for geo_id in region_ids:
                by_region[geo_id].append(feature)

        for index, viewpoint in enumerate((obj.get("visual_recon") or {}).get("viewpoints") or [], start=1):
            if not isinstance(viewpoint, dict) or not valid_point(viewpoint.get("coordinates")):
                continue
            vp = {
                "id": f"{obj['id']}:vp:{index:02d}",
                "object_id": obj["id"],
                "country_id": country_id,
                "geo_ids": region_ids,
                "coordinates": {
                    "lat": viewpoint["coordinates"]["lat"],
                    "lon": viewpoint["coordinates"]["lon"],
                },
                "detail": f"objects/{obj['id'].split('_')[1]}/{obj['id']}.json",
            }
            viewpoint_features.append(vp)
            if country_id:
                vp_by_country[country_id].append(vp)
            for geo_id in region_ids:
                vp_by_region[geo_id].append(vp)

    maps = release / "maps"
    dump(maps / "indexes" / "objects.json", {"count": len(object_features), "features": object_features})
    dump(maps / "indexes" / "viewpoints.json", {"count": len(viewpoint_features), "features": viewpoint_features})

    geography = []
    for row in geo_rows:
        names = row.get("names") or {}
        label_en = names.get("en") or names.get("primary") or row.get("name")
        geography.append({
            "id": row["id"],
            "kind": row.get("kind"),
            "parent_id": row.get("parent_id"),
            "label_en": label_en,
        })
    dump(maps / "indexes" / "geography.json", {"count": len(geography), "features": geography})

    sea_manifest = {
        "scope": "sea",
        "label_language": "en",
        "object_index": "maps/indexes/objects.json",
        "viewpoint_index": "maps/indexes/viewpoints.json",
        "geography_index": "maps/indexes/geography.json",
    }
    dump(maps / "sea" / "manifest.json", sea_manifest)

    country_manifests = {}
    country_ids = sorted(row["id"] for row in geo_rows if row.get("kind") == "country")
    for country_id in country_ids:
        code = country_id.removeprefix("geo_")
        object_path = f"maps/countries/{code}/objects.json"
        viewpoint_path = f"maps/countries/{code}/viewpoints.json"
        dump(release / object_path, {"count": len(by_country[country_id]), "features": by_country[country_id]})
        dump(release / viewpoint_path, {"count": len(vp_by_country[country_id]), "features": vp_by_country[country_id]})
        manifest_rel = f"maps/countries/{code}/manifest.json"
        dump(release / manifest_rel, {
            "scope": "country",
            "country_id": country_id,
            "label_language": "en",
            "bounds": bounds(by_country[country_id]),
            "object_index": object_path,
            "viewpoint_index": viewpoint_path,
        })
        country_manifests[country_id] = manifest_rel

    region_manifests = {}
    for geo_id in sorted(g for g in geo_ids if g not in country_ids):
        object_path = f"maps/regions/{geo_id}/objects.json"
        viewpoint_path = f"maps/regions/{geo_id}/viewpoints.json"
        dump(release / object_path, {"count": len(by_region[geo_id]), "features": by_region[geo_id]})
        dump(release / viewpoint_path, {"count": len(vp_by_region[geo_id]), "features": vp_by_region[geo_id]})
        manifest_rel = f"maps/regions/{geo_id}/manifest.json"
        dump(release / manifest_rel, {
            "scope": "region",
            "geo_id": geo_id,
            "label_language": "en",
            "bounds": bounds(by_region[geo_id]),
            "object_index": object_path,
            "viewpoint_index": viewpoint_path,
        })
        region_manifests[geo_id] = manifest_rel

    dump(maps / "index.json", {
        "sea": "maps/sea/manifest.json",
        "countries": country_manifests,
        "regions": region_manifests,
    })

    # Keep the legacy manifest contract intact; only add a discoverable maps entry.
    manifest["maps"] = {"index": "maps/index.json", "sea": "maps/sea/manifest.json"}

    # Rebuild inventory and exclude only the release-root manifest itself.
    manifest["files"] = [
        file_entry(path, release)
        for path in sorted(release.rglob("*.json"))
        if path != manifest_path
    ]
    manifest.setdefault("totals", {})["files"] = len(manifest["files"])
    manifest["totals"]["map_object_features"] = len(object_features)
    manifest["totals"]["map_viewpoints"] = len(viewpoint_features)
    dump(manifest_path, manifest)

    print(json.dumps({
        "status": "ok",
        "release_id": latest["release_id"],
        "objects": len(object_features),
        "viewpoints": len(viewpoint_features),
        "countries": len(country_manifests),
        "regions": len(region_manifests),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="public/cdn/v2")
    args = parser.parse_args()
    build(Path(args.root))
