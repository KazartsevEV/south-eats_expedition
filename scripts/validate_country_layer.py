#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
HIER = ROOT / "data" / "hierarchy" / "countries"
GEO_NODES = ROOT / "data" / "geo" / "nodes"
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
REGIONAL_REQUIRED_FIELDS = [
    "name", "languages_spoken", "climate_summary", "best_period_general",
    "last_verified", "narrow", "geography", "transport", "safety",
    "local_reference_provenance",
]
GEO_NODE_REQUIRED_KEYS = {
    "id", "canonical_id", "kind", "name_ru", "name_local", "slug",
    "parent_id", "axis", "object_ids",
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

def validate_geojson_coordinates(value, label):
    if not isinstance(value, list) or not value:
        fail(f"{label}: geometry coordinates must be a non-empty array")
    if isinstance(value[0], (int, float)):
        if len(value) < 2:
            fail(f"{label}: coordinate pair is incomplete")
        lon, lat = value[0], value[1]
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            fail(f"{label}: coordinate outside WGS84 range: {lon}, {lat}")
        return
    for child in value:
        validate_geojson_coordinates(child, label)

def validate_geometry_doc(code, geo_id, doc):
    if doc.get("type") != "FeatureCollection" or not (doc.get("features") or []):
        fail(f"{code}: geometry for {geo_id} must be a non-empty FeatureCollection")
    for index, feature in enumerate(doc.get("features") or []):
        geometry = (feature or {}).get("geometry") or {}
        if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            fail(f"{code}: geometry {geo_id} feature {index} must be Polygon/MultiPolygon")
        validate_geojson_coordinates(
            geometry.get("coordinates"),
            f"{code}: geometry {geo_id} feature {index}",
        )

def validate_node_geometry(code, node, known_source_ids, known_geo_ids):
    geometry_meta = node.get("geometry") or {}
    if geometry_meta.get("status") != "available":
        return False
    geo_id = node.get("canonical_id")
    if not geometry_meta.get("source_refs") or not geometry_meta.get("checked_at"):
        fail(f"{code}: geo node {node.get('id')!r} has incomplete geometry provenance")
    unknown = sorted(set(geometry_meta.get("source_refs") or []) - known_source_ids)
    if unknown:
        fail(f"{code}: geo node {node.get('id')!r} geometry references unknown canonical sources {unknown}")
    if geometry_meta.get("accuracy") == "approximate" and not (
        geometry_meta.get("coverage_basis") or geometry_meta.get("note")
    ):
        fail(f"{code}: approximate geo node {node.get('id')!r} lacks coverage_basis/note")

    path = GEO_NODES / f"{geo_id}.geojson"
    if path.exists():
        validate_geometry_doc(code, geo_id, load(path))
        return True

    basis = geometry_meta.get("coverage_basis") or []
    if not basis:
        fail(f"{code}: geo node {node.get('id')!r} declares geometry but has neither file nor coverage_basis")
    for basis_geo_id in basis:
        if basis_geo_id not in known_geo_ids:
            fail(f"{code}: geo node {node.get('id')!r} references unknown geometry basis {basis_geo_id}")
        basis_path = GEO_NODES / f"{basis_geo_id}.geojson"
        if not basis_path.exists():
            fail(f"{code}: geo node {node.get('id')!r} basis file is missing: {basis_path}")
        validate_geometry_doc(code, basis_geo_id, load(basis_path))
    return True

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
    canonical_source_ids = set()
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
        canonical_source_ids.add(canonical_id)

    for field, resolver in DYNAMIC_SOURCE_FIELDS.items():
        ids = resolver(travel, doc.get("safety") or {})
        if not ids:
            fail(f"{code}: dynamic field {field} lacks source_ids")
        missing = [x for x in ids if x not in source_by_id]
        if missing:
            fail(f"{code}: dynamic field {field} references unknown source_ids {missing}")

    criminal = travel.get("criminal_liability")
    if not present(criminal):
        fail(f"{code}: missing traveller criminal_liability layer")
    if not isinstance(criminal, dict):
        fail(f"{code}: criminal_liability must be an object")
    items = criminal.get("items") or []
    if not isinstance(items, list) or not items:
        fail(f"{code}: criminal_liability.items must be a non-empty list")
    if any(key in criminal for key in ("scope", "offence", "what_counts", "penalty", "nuance")):
        fail(f"{code}: criminal_liability contains legacy/internal presentation fields")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"{code}: criminal_liability.items[{index}] must be an object")
        for field in ("title", "rule", "source_ids"):
            if not present(item.get(field)):
                fail(f"{code}: criminal_liability.items[{index}] missing {field}")
        if any(key in item for key in ("offence", "what_counts", "penalty", "nuance", "scope")):
            fail(f"{code}: criminal_liability.items[{index}] contains legacy/internal presentation fields")
        item_missing = [x for x in (item.get("source_ids") or []) if x not in source_by_id]
        if item_missing:
            fail(f"{code}: criminal_liability.items[{index}] references unknown source_ids {item_missing}")

    criminal_ids = travel.get("criminal_law_source_ids") or []
    if not criminal_ids:
        fail(f"{code}: criminal_liability lacks source_ids")
    missing = [x for x in criminal_ids if x not in source_by_id]
    if missing:
        fail(f"{code}: criminal_liability references unknown source_ids {missing}")
    item_source_ids = {x for item in items for x in (item.get("source_ids") or [])}
    unlisted = sorted(item_source_ids - set(criminal_ids))
    if unlisted:
        fail(f"{code}: criminal_liability item source_ids missing from criminal_law_source_ids {unlisted}")

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
    geometry_nodes = 0
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
        profile = node.get("profile") or {}
        if profile:
            if not profile.get("source_refs") or not profile.get("checked_at"):
                fail(f"{code}: geo node {node.get('id')!r} profile has incomplete provenance")
            profile_unknown = sorted(set(profile.get("source_refs") or []) - canonical_source_ids)
            if profile_unknown:
                fail(f"{code}: geo node {node.get('id')!r} profile references unknown canonical sources {profile_unknown}")
        geometry_known_sources = set(canonical_source_ids)
        if hierarchy_meta.get("canonical_source_id"):
            geometry_known_sources.add(hierarchy_meta.get("canonical_source_id"))
        if validate_node_geometry(code, node, geometry_known_sources, set(canonical_ids)):
            geometry_nodes += 1
        legacy_region_names.update(node.get("legacy_region_names") or [])

    if code == "PH" and geometry_nodes != len(nodes):
        fail(f"{code}: every published geo node must have validated geometry: {geometry_nodes}/{len(nodes)}")

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
        "criminal_law_layer": bool(travel.get("criminal_liability")),
        "criminal_law_items": len((travel.get("criminal_liability") or {}).get("items") or []),
        "regional_profiles": len(regions),
        "geo_nodes": len(nodes),
        "geometry_nodes": geometry_nodes,
        "regional_geo_contract": True,
    }

print(json.dumps({"status": "ok", "countries": report}, ensure_ascii=False, indent=2))
