#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CDN = PUBLIC / "cdn" / "v2"
INDEX = PUBLIC / "index.html"
RENDERER_DICTIONARY = PUBLIC / "ui" / "renderer.ru.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"renderer-data-driven validation failed: {message}")


latest = load(CDN / "latest.json")
release_id = latest.get("release_id")
if not isinstance(release_id, str) or not release_id:
    fail("latest.json has no release_id")

release = CDN / release_id
index_text = INDEX.read_text(encoding="utf-8")

for forbidden in ("var COUNTRY=", "var FIELD_LABELS=", "var VALUE_LABELS="):
    if forbidden in index_text:
        fail(f"legacy renderer hardcode remains: {forbidden}")

dictionary = load(RENDERER_DICTIONARY)
if dictionary.get("schema") != "expedition_renderer_dictionary/v1":
    fail("renderer dictionary schema mismatch")
if dictionary.get("locale") != "ru":
    fail("renderer dictionary locale mismatch")
if not isinstance(dictionary.get("field_labels"), dict) or not dictionary["field_labels"]:
    fail("renderer field_labels missing")
if not isinstance(dictionary.get("value_labels"), dict):
    fail("renderer value_labels missing")

region = load(release / "region" / "southeast-asia.json")
countries = region.get("countries") or []
if len(countries) != 11:
    fail(f"expected 11 region countries, got {len(countries)}")

country_literals: set[str] = set()
for row in countries:
    for key in ("name_ru", "name_en", "name_local"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            country_literals.add(value.strip())
    if not row.get("country_code") or not row.get("flag"):
        fail(f"country renderer metadata incomplete: {row!r}")

search = load(release / "search" / "global.json")
objects = search.get("objects") or []
object_literals = {
    row["title"].strip()
    for row in objects
    if isinstance(row, dict)
    and isinstance(row.get("title"), str)
    and len(row["title"].strip()) >= 6
}

hardcoded_countries = sorted(value for value in country_literals if value in index_text)
hardcoded_objects = sorted(value for value in object_literals if value in index_text)

if hardcoded_countries:
    fail("country content hardcoded in index.html: " + ", ".join(hardcoded_countries))
if hardcoded_objects:
    fail("object content hardcoded in index.html: " + ", ".join(hardcoded_objects[:20]))

print(
    json.dumps(
        {
            "status": "ok",
            "release_id": release_id,
            "countries": len(countries),
            "objects": len(objects),
            "field_labels": len(dictionary["field_labels"]),
            "value_labels": len(dictionary["value_labels"]),
            "renderer_country_object_literals": 0,
        },
        ensure_ascii=False,
    )
)
