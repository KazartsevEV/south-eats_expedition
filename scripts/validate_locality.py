#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_context import get_release_context


LOCAL_PROFILE_KEYS = {
    "tides",
    "marine",
    "local_crime",
    "diseases",
}
LOCAL_CLIMATE_KEYS = {
    "tides",
    "marine",
}
REGION_REQUIRED_KEYS = ("geography", "climate", "transport")
LOCALITY_REQUIRED_KEYS = ()
VALID_COVERAGE_ROLES = {"structural", "regional_profile", "locality_profile"}


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
latest = get_release_context(root)
release = latest["release"]
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

    data = value.get("data") or {}
    sea_series = data.get("sea_temp_mean_c_by_month")
    if has_value(sea_series) and not has_value(data.get("reference_location")):
        findings.append({
            "file": path.relative_to(release).as_posix(),
            "field": "data.sea_temp_mean_c_by_month",
            "reason": "country-level monthly sea series must be explicitly scoped by data.reference_location",
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
    role = entity.get("coverage_role") or "structural"
    missing = []

    if role not in VALID_COVERAGE_ROLES:
        missing.append("coverage_role")
        required = ()
    elif role == "regional_profile":
        required = REGION_REQUIRED_KEYS
    elif role == "locality_profile":
        required = LOCALITY_REQUIRED_KEYS
    else:
        required = ()

    missing.extend(key for key in required if not has_value(entity.get(key)))

    refs = ((entity.get("provenance") or {}).get("source_refs") or [])
    if not refs:
        missing.append("provenance.source_refs")
    if not has_value((entity.get("provenance") or {}).get("checked_at")):
        missing.append("provenance.checked_at")

    description = entity.get("description") or {}
    if role in {"regional_profile", "locality_profile"} and not has_value(description.get("narrow")):
        missing.append("description.narrow")

    if role == "locality_profile":
        primary = entity.get("primary_location")
        location_status = entity.get("primary_location_status") or {}
        if not has_value(primary):
            if location_status.get("status") not in {"unresolved", "not_applicable"} or not has_value(location_status.get("reason")):
                missing.append("primary_location_or_explicit_status")
        climate = entity.get("climate") or {}
        if climate and not has_value(climate.get("annual_reference")) and not has_value(climate.get("annual_reference_status")):
            missing.append("climate.annual_reference_or_status")

    if missing:
        geo_gaps.append({
            "id": geo_id,
            "name": (entity.get("names") or {}).get("primary"),
            "kind": entity.get("kind"),
            "parent_id": entity.get("parent_id"),
            "coverage_role": role,
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
        "ownership": "country=macro climate context plus explicitly scoped reference-location series; geo=regional/local climate, nature, safety occurrence and route-level relevance",
        "coverage_roles": {
            "structural": ["provenance.source_refs", "provenance.checked_at"],
            "regional_profile": list(REGION_REQUIRED_KEYS) + [
                "description.narrow",
                "provenance.source_refs",
                "provenance.checked_at",
            ],
            "locality_profile": [
                "description.narrow",
                "primary_location_or_explicit_status",
                "provenance.source_refs",
                "provenance.checked_at",
                "climate.annual_reference_or_status_when_climate_present",
            ],
        },
    },
}
print(json.dumps(result, ensure_ascii=False, indent=2))

if args.strict and findings:
    raise SystemExit(1)
if args.strict_geo and geo_gaps:
    raise SystemExit(1)
