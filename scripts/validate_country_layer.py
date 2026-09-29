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
}
PROFILE_FIELDS = [
    "history", "geography", "religion", "languages", "ethnography",
    "economy", "political_system", "culture", "summary", "narrow",
]
NATURE_FIELDS = ["flora", "fauna", "dangerous_animals", "poisonous_plants"]
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
        if expected != canonical_id:
            fail(f"{code}: source registry mismatch {short_id}: {expected} != {canonical_id}")
        source_by_id[short_id] = row

    for field, resolver in DYNAMIC_SOURCE_FIELDS.items():
        ids = resolver(travel, doc.get("safety") or {})
        if not ids:
            fail(f"{code}: dynamic field {field} lacks source_ids")
        missing = [x for x in ids if x not in source_by_id]
        if missing:
            fail(f"{code}: dynamic field {field} references unknown source_ids {missing}")

    hierarchy_path = HIER / f"{slug}.json"
    if not hierarchy_path.exists():
        fail(f"{code}: missing formal hierarchy")
    hierarchy = load(hierarchy_path)
    nodes = hierarchy.get("nodes") or []
    if not nodes:
        fail(f"{code}: empty formal hierarchy")
    node_ids = {n.get("id") for n in nodes}
    if None in node_ids or len(node_ids) != len(nodes):
        fail(f"{code}: invalid/duplicate hierarchy node IDs")
    for node in nodes:
        cid = node.get("canonical_id")
        if not cid:
            fail(f"{code}: hierarchy node {node.get('id')} missing canonical_id")
        if registry_geo.get(node.get("id")) != cid:
            fail(f"{code}: geo registry mismatch for {node.get('id')}")
        parent = node.get("parent_id")
        if parent != f"country:{code.lower()}" and parent not in node_ids:
            fail(f"{code}: hierarchy node {node.get('id')} has unknown parent {parent}")

    object_names = {row.get("name") for row in (travel.get("objects") or []) if row.get("name")}
    # Coverage uses legacy object IDs from the generated country source relation.
    # Formal hierarchy must not silently lose an existing attraction.
    # When an object has no source-level id, coverage is checked later by augment_hierarchy.
    hierarchy_object_ids = {oid for n in nodes for oid in (n.get("object_ids") or [])}
    if not hierarchy_object_ids and object_names:
        fail(f"{code}: formal hierarchy contains no object references")

    report[code] = {
        "profile_fields": len(PROFILE_FIELDS),
        "source_count": len(source_rows),
        "hierarchy_nodes": len(nodes),
        "dynamic_fields_sourced": len(DYNAMIC_SOURCE_FIELDS),
    }

print(json.dumps({"status": "ok", "countries": report}, ensure_ascii=False, indent=2))
