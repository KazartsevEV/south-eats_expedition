#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


LOCAL_PROFILE_KEYS = {
    "tides",
    "marine",
    "local_crime",
    "diseases",
}
LOCAL_CLIMATE_KEYS = {
    "sea_temp_mean_c_by_month",
    "tides",
    "marine",
}
REGION_REQUIRED_KEYS = ("geography", "climate", "health", "safety", "transport")
LOCALITY_REQUIRED_KEYS = ("geography", "climate", "transport", "primary_location")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path + (key,), child
            yield from walk(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + (str(index),))


def has_value(value):
    return value not in (None, "", [], {})


parser = argparse.ArgumentParser()
parser.add_argument("root", nargs="?", default="public/cdn/v2")
parser.add_argument("--country", help="Limit locality ownership/coverage audit to one ISO alpha-2 code.")
parser.add_argument("--strict", action="store_true", help="Fail on country/locality ownership violations.")
parser.add_argument("--strict-geo", action="store_true", help="Fail when required geo coverage is incomplete.")
args = parser.parse_args()

country_filter = args.country.lower() if args.country else None
root = Path(args.root)
latest = load(root / "latest.json")
release = root / latest["release_id"]
findings = []

country_paths = sorted((release / "countries").glob("*/profile.json"))
if country_filter:
    country_paths = [p for p in country_paths if p.parent.name == country_filter]

for path in country_paths:
    value = load(path)
    for key_path, child in walk(value):
        if key_path[-1] in LOCAL_PROFILE_KEYS and has_value(child):
            findings.append({
                "file": path.relative_to(release).as_posix(),
                "field": ".".join(key_path),
            })

climate_paths = sorted((release / "countries").glob("*/climate.json"))
if country_filter:
    climate_paths = [p for p in climate_paths if p.parent.name == country_filter]

for path in climate_paths:
    value = load(path)
    for key_path, child in walk(value):
        if key_path[-1] in LOCAL_CLIMATE_KEYS and has_value(child):
            findings.append({
                "file": path.relative_to(release).as_posix(),
                "field": ".".join(key_path),
            })

geo_gaps = []
geo_index = load(release / "geo" / "index.json")
for row in geo_index.get("entities", []):
    geo_id = row.get("id")
    if not geo_id or row.get("kind") == "country" or row.get("status") == "legacy_route_hub":
        continue
    parts = geo_id.split("_")
    if len(parts) < 2:
        continue
    code = parts[1].lower()
    if country_filter and code != country_filter:
        continue

    entity = load(release / row["path"])
    country_id = f"geo_{code}"
    is_region = entity.get("parent_id") == country_id
    required = REGION_REQUIRED_KEYS if is_region else LOCALITY_REQUIRED_KEYS
    missing = [key for key in required if not has_value(entity.get(key))]

    refs = ((entity.get("provenance") or {}).get("source_refs") or [])
    if not refs:
        missing.append("provenance.source_refs")

    if not is_region:
        climate = entity.get("climate") or {}
        if not has_value(climate.get("annual_reference")) and not has_value(climate.get("annual_reference_status")):
            missing.append("climate.annual_reference_or_status")

    if missing:
        geo_gaps.append({
            "id": geo_id,
            "name": (entity.get("names") or {}).get("primary"),
            "kind": entity.get("kind"),
            "parent_id": entity.get("parent_id"),
            "level": "region" if is_region else "locality",
            "missing": missing,
        })

status = "ok"
if findings:
    status = "needs_migration"
if geo_gaps:
    status = "needs_geo_work" if status == "ok" else status

result = {
    "status": status,
    "release_id": latest["release_id"],
    "country": country_filter,
    "country_locality_findings": len(findings),
    "findings": findings,
    "geo_coverage_gaps": len(geo_gaps),
    "geo_gaps": geo_gaps,
    "rules": {
        "ownership": "country=macro context and non-localized country hazard inventories; geo=local climate/nature/safety occurrence and route-level relevance",
        "region_required": list(REGION_REQUIRED_KEYS) + ["provenance.source_refs"],
        "locality_required": list(LOCALITY_REQUIRED_KEYS) + [
            "provenance.source_refs",
            "climate.annual_reference_or_status",
        ],
    },
}
print(json.dumps(result, ensure_ascii=False, indent=2))

if args.strict and findings:
    raise SystemExit(1)
if args.strict_geo and geo_gaps:
    raise SystemExit(1)
