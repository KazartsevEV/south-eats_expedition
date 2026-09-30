#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from release_context import get_release_context

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "public" / "cdn" / "v2")

def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

latest = get_release_context(PUBLIC)
release = latest["release"]

required = [
    "project.json",
    "region/southeast-asia.json",
    "page-layouts.json",
    "taxonomy/tree.json",
    "geography/tree.json",
    "navigation/tree.json",
    "hierarchy-status.json",
]
for rel in required:
    if not (release / rel).exists():
        fail(f"missing hierarchy file: {rel}")

project = load(release / "project.json")
region = load(release / "region" / "southeast-asia.json")
taxonomy = load(release / "taxonomy" / "tree.json")
geography = load(release / "geography" / "tree.json")
navigation = load(release / "navigation" / "tree.json")
status = load(release / "hierarchy-status.json")
types = load(release / "object-types.json")["object_types"]
objects = load(release / "search" / "objects.json")["objects"]
object_geography_doc = load(release / "search" / "object-geography.json")
places = load(release / "search" / "places.json")["places"]

if len(object_geography_doc.get("objects") or []) != len(objects):
    fail("object-geography index count mismatch")
for row in objects:
    gids=row.get("geography_ids") or []
    if not gids:
        fail(f"object missing geography_ids: {row.get('id')}")
    if f"country:{row['country_code'].lower()}" not in gids:
        fail(f"object geography lacks country root: {row.get('id')}")

place_ids = [p.get("id") for p in places]
if any(not x for x in place_ids):
    fail("place index contains empty id")
if len(place_ids) != len(set(place_ids)):
    duplicates = sorted({x for x in place_ids if place_ids.count(x) > 1})
    fail(f"duplicate place ids: {duplicates[:20]}")

# Top levels are fixed before descending.
countries = project.get("countries") or []
if len(countries) != 11:
    fail(f"project country catalog must contain 11 countries, got {len(countries)}")
codes = [c.get("country_code") for c in countries]
if len(codes) != len(set(codes)):
    fail("duplicate country code in project catalog")
if {c.get("country_code") for c in (region.get("countries") or [])} != set(codes):
    fail("region country set differs from project country set")

for country in countries:
    page = country.get("page_path")
    if not page or not (release / page).exists():
        fail(f"country page missing for {country.get('country_code')}: {page}")

# Taxonomy: each released primary class belongs to exactly one family.
released_types = {row["value"]: row for row in types}
seen = {}
taxonomy_count = 0
for family in ((taxonomy.get("root") or {}).get("children") or []):
    for child in family.get("children") or []:
        value = child.get("value")
        if value in seen:
            fail(f"class appears in two taxonomy families: {value}")
        seen[value] = family.get("id")
        taxonomy_count += int(child.get("count") or 0)
        page = child.get("page_path")
        if not page or not (release / page).exists():
            fail(f"class page missing: {value} -> {page}")
missing = sorted(set(released_types) - set(seen))
if missing:
    fail(f"released classes missing from taxonomy tree: {missing}")
if taxonomy_count != len(objects):
    fail(f"taxonomy leaf counts {taxonomy_count} != object count {len(objects)}")

# Geography: exactly one country node per catalog country. Lower nesting is not inferred.
geo_root = geography.get("root") or {}
geo_countries = geo_root.get("children") or []
geo_codes = {node.get("id","").split(":")[-1].upper() for node in geo_countries}
if geo_codes != set(codes):
    fail(f"geography country set mismatch: {sorted(geo_codes)} vs {sorted(codes)}")
for country_node in geo_countries:
    page = country_node.get("page_path")
    if not page or not (release / page).exists():
        fail(f"geography country page missing: {page}")
    for place in country_node.get("children") or []:
        p = place.get("page_path")
        if not p or not (release / p).exists():
            fail(f"geography page missing: {place.get('id')} -> {p}")

# Navigation: project -> SEA -> 11 countries -> geography/classes.
nav_root = navigation.get("root") or {}
if nav_root.get("id") != "project:expedition-south-east":
    fail("navigation root is not project:expedition-south-east")
regions = nav_root.get("children") or []
if len(regions) != 1 or regions[0].get("id") != "region:southeast-asia":
    fail("navigation must have one Southeast Asia region under project root")
nav_countries = regions[0].get("children") or []
if {n.get("id","").split(":")[-1].upper() for n in nav_countries} != set(codes):
    fail("navigation country set mismatch")

# Every released object must be reachable through its country's class branch.
def collect_object_ids(node):
    out = set()
    if node.get("kind") in {"object", "object_ref"} and node.get("id"):
        out.add(node["id"])
    for child in node.get("children") or []:
        out.update(collect_object_ids(child))
    return out

reachable = set()
for country in nav_countries:
    branches = {b.get("id","").split(":")[-1]: b for b in country.get("children") or []}
    class_branch = branches.get("classes")
    geo_branch = branches.get("geography")
    if class_branch is None or geo_branch is None:
        fail(f"country lacks geography/classes branches: {country.get('id')}")
    reachable.update(collect_object_ids(class_branch))

object_ids = {o["id"] for o in objects}
missing_objects = sorted(object_ids - reachable)
if missing_objects:
    fail(f"objects unreachable through country class branches: {missing_objects[:20]}")

def validate_nav_pages(node):
    kind=node.get("kind")
    if kind in {"class_family","country_class"}:
        path=node.get("path")
        if not path or not (release / path).exists():
            fail(f"navigation node page missing: {node.get('id')} -> {path}")
    for child in node.get("children") or []:
        validate_nav_pages(child)

for country in nav_countries:
    validate_nav_pages(country)

for family in ((taxonomy.get("root") or {}).get("children") or []):
    family_page=release / "pages" / "families" / f"{family.get('value')}.json"
    if not family_page.exists():
        fail(f"global family page missing: {family.get('value')}")

# Page contracts must cover all renderer levels.
layouts = load(release / "page-layouts.json").get("layouts") or {}
expected_layouts = {"project","region","country","geography","class_family","class","country_class","object"}
if set(layouts) != expected_layouts:
    fail(f"page layout set mismatch: {sorted(layouts)}")

levels = status.get("levels") or {}
for key in ["project","region","country_catalog","taxonomy_families","geography_contract","country_pages","geography_pages","object_geography_index","class_family_pages","country_class_pages","object_classes","object_cards"]:
    if key not in levels:
        fail(f"hierarchy status missing level: {key}")

print(json.dumps({
    "status":"ok",
    "release_id":latest["release_id"],
    "schema_version":latest["schema_version"],
    "countries":len(countries),
    "objects":len(objects),
    "released_classes":len(released_types),
    "taxonomy_classes":len(seen),
    "geography_country_nodes":len(geo_countries),
    "reachable_objects":len(reachable & object_ids),
}, ensure_ascii=False, indent=2))
