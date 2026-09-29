#!/usr/bin/env python3
"""Build deterministic map/site read models from the canonical CDN layer."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


LAYER_ZOOM = {
    "admin.country": [3, 7], "admin.region": [5, 10],
    "settlement.capital": [3, 14], "settlement.city": [5, 14],
    "settlement.town": [7, 14], "settlement.village": [8, 14],
    "hydrography.river": [3, 14], "hydrography.stream": [10, 18],
    "hydrography.lake": [5, 16], "physical.island": [5, 16],
    "physical.mountain": [5, 16], "physical.range": [5, 14],
    "protected_area": [5, 16], "object": [7, 18], "route": [7, 18],
    "poi.water": [13, 18], "poi.supplies": [13, 18], "poi.fuel": [13, 18],
    "poi.parking": [10, 18], "poi.trailhead": [10, 18], "poi.pier": [10, 18],
    "lodging": [10, 18], "camping": [10, 18], "viewpoint": [13, 18],
}


def bounds(points):
    if not points:
        return None
    return {"west": min(p[1] for p in points), "south": min(p[0] for p in points),
            "east": max(p[1] for p in points), "north": max(p[0] for p in points)}


def page(title: str, view_path: str, map_path: str | None = None):
    map_meta = f'<meta name="expedition-map" content="/{map_path}">' if map_path else ""
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="expedition-view" content="/{view_path}">{map_meta}</head>
<body><main id="app"><h1>{title}</h1><p>Данные страницы загружаются из производного JSON-представления.</p></main>
<script type="module">const p=document.querySelector('meta[name="expedition-view"]').content;
fetch(p).then(r=>r.json()).then(v=>document.querySelector('#app').dataset.ready=String(Boolean(v)));
</script></body></html>'''


def build_expedition_layers(release: Path, schema_version: str):
    objects = [load(p) for p in sorted((release / "objects").glob("*/*.json"))]
    geo_index = load(release / "geo" / "index.json").get("entities", [])
    countries = sorted((load(release / "manifest.json").get("published_countries") or []))
    by_country, by_region = defaultdict(list), defaultdict(list)
    all_points = []
    object_features = []
    for obj in objects:
        loc = (obj.get("geo") or {}).get("primary_location") or {}
        lat, lon = loc.get("lat"), loc.get("lon")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            point = [lat, lon]; all_points.append(point)
            feature = {"id": obj["id"], "layer": "object", "coordinates": {"lat": lat, "lon": lon},
                       "detail": f"objects/{obj['id'].split('_')[1]}/{obj['id']}.json"}
            object_features.append(feature)
            code = obj["id"].split("_")[1]
            by_country[code].append(feature)
            for region in (obj.get("geo") or {}).get("region_ids") or []:
                by_region[region].append(feature)

    dump(release / "schema" / "object-contract.json", {"schema_version": schema_version, "canonical": True, "required": ["id", "kind", "slug", "status", "classification", "geo", "media"]})
    dump(release / "schema" / "country-contract.json", {"schema_version": schema_version, "files": ["profile.json", "climate.json", "travel-rules.json", "indexes.json"]})
    dump(release / "schema" / "infrastructure-contract.json", {"schema_version": schema_version, "id_prefixes": ["poi_", "lod_", "trn_"], "canonical": True})
    dump(release / "schema" / "route-contract.json", {"schema_version": schema_version, "id_prefix": "rte_", "canonical": True})
    dump(release / "schema" / "source-contract.json", {"schema_version": schema_version, "id_prefix": "src_", "canonical": True})
    dump(release / "schema" / "media-contract.json", {"schema_version": schema_version, "id_prefix": "med_", "delivery_modes": ["remote_static", "mirrored_cache"], "gallery_binaries_in_git": False})
    dump(release / "schema" / "gallery-contract.json", {"schema_version": schema_version, "published_minimum": 5, "object_fields": ["preview_media_id", "cover_id", "gallery_ids"], "loading": {"grid": "local_preview_only", "gallery": "lazy", "preload": ["previous", "current", "next"]}})
    dump(release / "schema" / "map-contract.json", {"schema_version": schema_version, "canonical_inputs": ["geo", "objects", "infrastructure", "routes", "visual_recon"], "derived": True, "layers": [{"id": k, "minzoom": v[0], "maxzoom": v[1]} for k, v in LAYER_ZOOM.items()]})
    dump(release / "schema" / "preview-contract.json", {"format": "webp", "mime_type": "image/webp", "target": {"width": 960, "height": 640, "aspect_ratio": "3:2"}, "path": "assets/previews/<cc>/<object_id>.webp", "required_for_published": True})

    dump(release / "maps" / "indexes" / "objects.json", {"count": len(object_features), "features": object_features})
    for name in ["settlements", "hydrography", "infrastructure", "routes", "viewpoints"]:
        dump(release / "maps" / "indexes" / f"{name}.json", {"count": 0, "features": []})
    layers = {"layers": [{"id": k, "minzoom": v[0], "maxzoom": v[1]} for k, v in LAYER_ZOOM.items()]}
    dump(release / "maps" / "sea" / "bounds.json", bounds(all_points))
    dump(release / "maps" / "sea" / "layers.json", layers)
    dump(release / "maps" / "sea" / "style.json", {"version": 8, "name": "Expedition SEA", "sources": {}, "layers": []})
    dump(release / "maps" / "sea" / "manifest.json", {"scope": "sea", "bounds": "maps/sea/bounds.json", "layers": "maps/sea/layers.json", "object_index": "maps/indexes/objects.json"})
    country_maps, region_maps = {}, {}
    for code in [c.lower() for c in countries]:
        root = release / "maps" / "countries" / code
        dump(root / "bounds.json", bounds([[f["coordinates"]["lat"], f["coordinates"]["lon"]] for f in by_country[code]]))
        dump(root / "layers.json", layers)
        dump(root / "manifest.json", {"scope": "country", "country": code, "bounds": f"maps/countries/{code}/bounds.json", "layers": f"maps/countries/{code}/layers.json"})
        country_maps[code] = f"maps/countries/{code}/manifest.json"
    for region, features in sorted(by_region.items()):
        root = release / "maps" / "regions" / region
        dump(root / "bounds.json", bounds([[f["coordinates"]["lat"], f["coordinates"]["lon"]] for f in features]))
        dump(root / "layers.json", layers)
        dump(root / "manifest.json", {"scope": "region", "geo_id": region, "bounds": f"maps/regions/{region}/bounds.json", "layers": f"maps/regions/{region}/layers.json"})
        region_maps[region] = f"maps/regions/{region}/manifest.json"
    dump(release / "maps" / "index.json", {"sea": "maps/sea/manifest.json", "countries": country_maps, "regions": region_maps})
    dump(release / "views" / "maps" / "sea.json", {"map": "maps/sea/manifest.json"})
    for code, path in country_maps.items(): dump(release / "views" / "maps" / "countries" / f"{code}.json", {"map": path})
    for region, path in region_maps.items(): dump(release / "views" / "maps" / "regions" / f"{region}.json", {"map": path})

    (release / "site" / "index.html").parent.mkdir(parents=True, exist_ok=True)
    (release / "site" / "index.html").write_text(page("Expedition Southeast Asia", "views/home.json", "maps/sea/manifest.json"), encoding="utf-8")
    (release / "site" / "map" / "index.html").parent.mkdir(parents=True, exist_ok=True)
    (release / "site" / "map" / "index.html").write_text(page("Карта Юго-Восточной Азии", "views/maps/sea.json", "maps/sea/manifest.json"), encoding="utf-8")
    for code in country_maps:
        for suffix, title, view in [("index.html", code.upper(), f"views/countries/{code}.json"), ("map/index.html", f"Карта {code.upper()}", f"views/maps/countries/{code}.json")]:
            target = release / "site" / "countries" / code / suffix; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(page(title, view, country_maps[code]), encoding="utf-8")
    for region, map_path in region_maps.items():
        for suffix, title, view in [("index.html", region, f"views/regions/{region}.json"), ("map/index.html", f"Карта {region}", f"views/maps/regions/{region}.json")]:
            target = release / "site" / "regions" / region / suffix; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(page(title, view, map_path), encoding="utf-8")
    for obj in objects:
        code = obj["id"].split("_")[1]
        target = release / "site" / "objects" / code / obj["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page((obj.get("names") or {}).get("primary", obj["id"]), f"objects/{code}/{obj['id']}.json"), encoding="utf-8")
    for view in sorted((release / "views" / "classes").glob("*.json")):
        target = release / "site" / "classes" / view.stem / "index.html"; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(page(view.stem, f"views/classes/{view.name}"), encoding="utf-8")
    for view in sorted((release / "views" / "tags").glob("*.json")):
        target = release / "site" / "tags" / view.stem / "index.html"; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(page(view.stem, f"views/tags/{view.name}"), encoding="utf-8")
    return {"map_country_manifests": len(country_maps), "map_region_manifests": len(region_maps), "map_object_features": len(object_features)}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "public" / "cdn" / "v2"
    latest = load(root / "latest.json")
    print(json.dumps(build_expedition_layers(root / latest["release_id"], latest["schema_version"]), indent=2))
