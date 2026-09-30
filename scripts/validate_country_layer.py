#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
HIER = ROOT / "data" / "hierarchy" / "countries"
REGISTRY = ROOT / "data" / "id-registry.json"

COUNTRIES = {
    "BN": "brunei",
    "KH": "cambodia",
    "LA": "laos",
    "ID": "indonesia",
    "MY": "malaysia",
    "MM": "myanmar",
    "PH": "philippines",
    "SG": "singapore",
    "TH": "thailand",
    "TL": "timor-leste",
    "VN": "vietnam",
}
PROFILE_FIELDS = [
    "history", "geography", "religion", "languages", "ethnography",
    "economy", "political_system", "culture", "summary", "narrow",
]
NATURE_FIELDS = ["flora", "fauna", "dangerous_animals", "poisonous_plants"]
SECOND_CHUNK = {"PH", "SG", "TH", "TL", "VN"}
REGIONAL_REQUIRED_FIELDS = [
    "name", "languages_spoken", "climate_summary", "best_period_general",
    "last_verified", "narrow", "geography", "transport", "safety",
    "local_reference_provenance",
]
GEO_NODE_REQUIRED_KEYS = {
    "id", "canonical_id", "kind", "name_ru", "name_local", "slug",
    "parent_id", "axis", "object_ids", "notes_ru",
}
DYNAMIC_SOURCE_FIELDS = {
    "visa_for_russian_passport": lambda t, s: (t.get("visa_for_russian_passport") or {}).get("source_ids"),
    "land_borders": lambda t, s: (t.get("land_borders") or {}).get("source_ids"),
    "airports": lambda t, s: t.get("airports_source_ids"),
    "international_air_links": lambda t, s: t.get("international_air_links_source_ids"),
    "transport_rules": lambda t, s: (t.get("transport_rules") or {}).get("source_ids"),
    "camping_rules": lambda t, s: (t.get("camping_rules") or {}).get("source_ids"),
    "drone_rules": lambda t, s: (t.get("drone_rules") or {}).get("source_ids"),
    "laws_and_prohibitions": lambda t, s: t.get("laws_source_ids"),
    "tourist_permits": lambda t, s: (t.get("tourist_permits") or {}).get("source_ids"),
    "currency": lambda t, s: (t.get("currency") or {}).get("source_ids"),
    "safety": lambda t, s: s.get("source_ids"),
}

def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def present(value):
    return value not in (None, "", [], {})

registry = load(REGISTRY)
registry_sources = registry.get("sources") or {}
registry_geo = registry.get("geo") or {}

report = {}
for code, slug in COUNTRIES.items():
    path = SRC / f"{slug}.json"
    if not path.exists():
        fail(f"{code}: missing source file {path}")
    doc = load(path)
    meta = doc.get("meta") or {}
    if meta.get("country_code") != code:
        fail(f"{code}: country_code mismatch")

    overview = doc.get("overview") or {}
    for field in PROFILE_FIELDS:
        if not present(overview.get(field)):
            fail(f"{code}: missing country profile field {field}")

    nature = doc.get("nature") or {}
    for field in NATURE_FIELDS:
        if not present(nature.get(field)):
            fail(f"{code}: missing country nature field {field}")

    if not present(doc.get("climate")):
        fail(f"{code}: missing climate")

    travel = doc.get("travel") or {}
    required_travel = [
        "visa_for_russian_passport", "land_borders", "airports",
        "international_air_links", "transport_rules", "camping_rules",
        "drone_rules", "laws_and_prohibitions", "tourist_permits", "currency",
    ]
    for field in required_travel:
        if not present(travel.get(field)):
            fail(f"{code}: missing travel field {field}")

    source_rows = doc.get("sources") or []
    source_by_id = {}
    for row in source_rows:
        short_id = row.get("id")
        canonical_id = row.get("canonical_id")
        if not short_id or not canonical_id:
            fail(f"{code}: source without id/canonical_id")
        expected = registry_sources.get(f"country:{code.lower()}:{short_id}")
        # Older canonical country-source rows (notably Cambodia/Laos) predate
        # source-ID registry coverage. Their canonical_id remains authoritative.
        # If a registry mapping exists, it must agree; absence alone is not an error.
        if expected is not None and expected != canonical_id:
            fail(f"{code}: source registry mismatch {short_id}: {expected} != {canonical_id}")
        source_by_id[short_id] = row

    for field, resolver in DYNAMIC_SOURCE_FIELDS.items():
        ids = resolver(travel, doc.get("safety") or {})
        if not ids:
            fail(f"{code}: dynamic field {field} lacks source_ids")
        missing = [x for x in ids if x not in source_by_id]
        if missing:
            fail(f"{code}: dynamic field {field} references unknown source_ids {missing}")

    if code in SECOND_CHUNK:
        if not present(travel.get("criminal_liability")):
            fail(f"{code}: missing traveller criminal_liability layer")
        criminal_ids = travel.get("criminal_law_source_ids") or []
        if not criminal_ids:
            fail(f"{code}: criminal_liability lacks source_ids")
        missing = [x for x in criminal_ids if x not in source_by_id]
        if missing:
            fail(f"{code}: criminal_liability references unknown source_ids {missing}")

    # Regional research and formal geography are canonical requirements for every
    # published country, not only for the second migration chunk.
    regions = travel.get("regions") or []
    if not regions:
        fail(f"{code}: regional stage has no travel.regions")

    hierarchy_path = HIER / f"{slug}.json"
    if not hierarchy_path.exists():
        fail(f"{code}: missing formal regional hierarchy {hierarchy_path}")
    hierarchy = load(hierarchy_path)
    hierarchy_meta = hierarchy.get("meta") or {}
    if hierarchy_meta.get("country_code") != code:
        fail(f"{code}: hierarchy country_code mismatch")

    nodes = hierarchy.get("nodes") or []
    if not nodes:
        fail(f"{code}: formal regional hierarchy has no nodes")
    node_ids = [node.get("id") for node in nodes]
    canonical_ids = [node.get("canonical_id") for node in nodes]
    if any(not node_id for node_id in node_ids) or len(node_ids) != len(set(node_ids)):
        fail(f"{code}: hierarchy has blank or duplicate node IDs")
    if any(not geo_id for geo_id in canonical_ids) or len(canonical_ids) != len(set(canonical_ids)):
        fail(f"{code}: hierarchy has blank or duplicate canonical geo IDs")

    node_id_set = set(node_ids)
    country_parent = f"country:{code.lower()}"
    legacy_region_names = set()
    for node in nodes:
        missing_keys = GEO_NODE_REQUIRED_KEYS - set(node)
        if missing_keys:
            fail(f"{code}: geo node {node.get('id')!r} missing keys {sorted(missing_keys)}")
        if not present(node.get("name_ru")) or not present(node.get("slug")) or not present(node.get("axis")):
            fail(f"{code}: geo node {node.get('id')!r} lacks identity fields")
        if not isinstance(node.get("object_ids"), list):
            fail(f"{code}: geo node {node.get('id')!r} object_ids must be an array")
        parent_id = node.get("parent_id")
        if parent_id != country_parent and parent_id not in node_id_set:
            fail(f"{code}: geo node {node.get('id')!r} has unknown parent {parent_id!r}")
        expected_geo_id = registry_geo.get(node.get("id"))
        if expected_geo_id is not None and expected_geo_id != node.get("canonical_id"):
            fail(
                f"{code}: geo registry mismatch {node.get('id')}: "
                f"{expected_geo_id} != {node.get('canonical_id')}"
            )
        legacy_region_names.update(node.get("legacy_region_names") or [])

    for region in regions:
        for field in REGIONAL_REQUIRED_FIELDS:
            if not present(region.get(field)):
                fail(f"{code}: region {region.get('name')!r} missing required field {field}")
        provenance = region.get("local_reference_provenance") or {}
        if not provenance.get("source_refs") or not provenance.get("checked_at"):
            fail(f"{code}: region {region.get('name')!r} has incomplete provenance")
        if region.get("name") not in legacy_region_names:
            fail(f"{code}: region {region.get('name')!r} has no canonical hierarchy node")

    # Lower-level locality profiles may intentionally remain logistics-only route
    # hubs. They are not promoted into administrative geography without evidence.

    report[code] = {
        "profile_fields": len(PROFILE_FIELDS),
        "source_count": len(source_rows),
        "dynamic_fields_sourced": len(DYNAMIC_SOURCE_FIELDS),
        "criminal_law_layer": code not in SECOND_CHUNK or bool(travel.get("criminal_liability")),
        "regional_profiles": len(regions),
        "geo_nodes": len(nodes),
        "regional_geo_contract": True,
    }

print(json.dumps({"status": "ok", "countries": report}, ensure_ascii=False, indent=2))
