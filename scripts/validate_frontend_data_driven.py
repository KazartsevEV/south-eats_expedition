#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CDN = PUBLIC / "cdn" / "v2"
INDEX = PUBLIC / "index.html"
RENDERER = PUBLIC / "ui" / "renderer.ru.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


latest = load(CDN / "latest.json")
release_id = latest.get("release_id")
if not isinstance(release_id, str) or not release_id:
    raise SystemExit("latest.json has no release_id")
release = CDN / release_id

search = load(release / "search" / "global.json")
region = load(release / "region" / "southeast-asia.json")
geo = load(release / "geo" / "index.json")
dictionary = load(RENDERER)
html = INDEX.read_text(encoding="utf-8")
errors: list[str] = []

if dictionary.get("schema") != "expedition_renderer_dictionary/v1":
    fail(errors, "renderer dictionary schema mismatch")
if dictionary.get("locale") != "ru":
    fail(errors, "renderer dictionary locale mismatch")

required_dictionaries = (
    "field_labels",
    "value_labels",
    "access_mode_labels",
    "water_quality_labels",
    "overnight_labels",
    "drone_labels",
    "geo_kind_labels",
    "region_section_labels",
    "narrative_section_labels",
    "narrative_type_labels",
)
for key in required_dictionaries:
    value = dictionary.get(key)
    if not isinstance(value, dict) or not value:
        fail(errors, f"renderer dictionary missing non-empty {key}")

for forbidden in (
    "var COUNTRY=",
    "var FIELD_LABELS=",
    "var VALUE_LABELS=",
    "var MODE_LABELS=",
    "var WATER_LABELS=",
    "var OVERNIGHT_LABELS=",
    "var DRONE_LABELS=",
):
    if forbidden in html:
        fail(errors, "legacy renderer hardcode remains: " + forbidden)

for required in (
    "maybe(base+'region/southeast-asia.json')",
    "j('./ui/renderer.ru.json')",
    "state.renderer=all[7]",
    "async function detail(id)",
    "CDN+state.release+'/objects/'+ccOf(id)+'/'+id+'.json'",
    "if(p[0]==='object'&&p[1])return renderObject(p[1])",
):
    if required not in html:
        fail(errors, "missing generic JSON-driven renderer fragment: " + required)

countries = region.get("countries") or []
objects = search.get("objects") or []
geo_rows = geo.get("entities") or []
if not countries:
    fail(errors, "region country catalog is empty")
if not isinstance(objects, list):
    fail(errors, "global object search layer is invalid")
if not isinstance(geo_rows, list):
    fail(errors, "geo index is invalid")

def present(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None

country_literals: set[str] = set()
country_structural: set[str] = set()
for row in countries:
    if not isinstance(row, dict):
        fail(errors, "country catalog row is not an object")
        continue
    for key in ("name_ru", "name_en", "name_local"):
        value = present(row.get(key))
        if value:
            country_literals.add(value)
    for key in ("slug", "page_path"):
        value = present(row.get(key))
        if value:
            country_structural.add(value)
    if not present(row.get("country_code")):
        fail(errors, "country catalog row has no country_code")

object_ids: set[str] = set()
object_titles: set[str] = set()
for row in objects:
    if not isinstance(row, dict):
        continue
    value = present(row.get("id"))
    if value:
        object_ids.add(value)
    title = present(row.get("title"))
    if title:
        object_titles.add(title)

geo_ids: set[str] = set()
geo_names: set[str] = set()
for row in geo_rows:
    if not isinstance(row, dict):
        continue
    value = present(row.get("id"))
    if value:
        geo_ids.add(value)
    value = present(row.get("name"))
    if value:
        geo_names.add(value)
    names = row.get("names")
    if isinstance(names, dict):
        for candidate in names.values():
            value = present(candidate)
            if value:
                geo_names.add(value)

checks = (
    ("country content", country_literals),
    ("country structural content", country_structural),
    ("object ids", object_ids),
    ("object titles", object_titles),
    ("geo ids", geo_ids),
    ("geo names", geo_names),
)
for label, values in checks:
    hits = sorted(value for value in values if len(value) >= 4 and value in html)
    if hits:
        fail(errors, f"{label} hardcoded in frontend: " + ", ".join(hits[:20]))

literal_object_ids = sorted(set(re.findall(r"obj_[a-z]{2}_[0-9]{4}", html)))
if literal_object_ids:
    fail(errors, "concrete object IDs hardcoded in frontend: " + ", ".join(literal_object_ids[:20]))

if errors:
    raise SystemExit("\n".join(errors))

print(json.dumps({
    "status": "ok",
    "release_id": release_id,
    "countries_checked": len(countries),
    "objects_checked": len(objects),
    "geo_entities_checked": len(geo_rows),
    "renderer_dictionaries": len(required_dictionaries),
    "frontend": "json-driven-country-object-geo",
}, ensure_ascii=False))
