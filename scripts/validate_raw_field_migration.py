#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from release_context import get_release_context

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "public" / "cdn" / "v2")
SRC = ROOT / "data" / "source"

def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

ctx = get_release_context(PUBLIC)
release = ctx["release"]
sources_index = load(release / "sources" / "index.json")
canonical_urls = {row.get("url") for row in sources_index.get("sources") or [] if row.get("url")}

# Every source URL still carried by the normalized source layer must survive
# into canonical sources. This catches the old-only donor provenance loss.
source_urls_checked = 0
for path in sorted(SRC.glob("*.json")):
    doc = load(path)
    for obj in ((doc.get("travel") or {}).get("objects") or []):
        for row in obj.get("sources") or []:
            url = row.get("url") if isinstance(row, dict) else None
            if not url:
                continue
            source_urls_checked += 1
            if url not in canonical_urls:
                fail(f"canonical sources lost URL from {path.name} / {obj.get('name')}: {url}")

source_object_by_country_name = {}
for path in sorted(SRC.glob("*.json")):
    doc = load(path)
    code = ((doc.get("meta") or {}).get("country_code") or "").upper()
    for source_obj in ((doc.get("travel") or {}).get("objects") or []):
        for name in (source_obj.get("name"), source_obj.get("display_name")):
            if name:
                source_object_by_country_name[(code, name)] = source_obj

objects_checked = 0
language_values_checked = 0
for object_path in sorted((release / "objects").glob("*/*.json")):
    obj = load(object_path)
    rel = ((obj.get("relations") or {}).get("legacy_detail_path"))
    if not rel:
        fail(f"{obj.get('id')}: missing legacy_detail_path")
    legacy = load(release / rel)
    code = obj["id"].split("_")[1].upper()
    source_obj = source_object_by_country_name.get((code, (obj.get("names") or {}).get("primary")))
    logistics = (legacy.get("visit") or {}).get("logistics") or {}
    operations = (legacy.get("visit") or {}).get("operations") or {}
    safety_old = (legacy.get("visit") or {}).get("safety") or {}

    visit = obj.get("visit") or {}
    entry = visit.get("entry") or {}
    if entry.get("typical_visit_hours") != logistics.get("typical_visit_hours"):
        fail(f"{obj['id']}: typical_visit_hours migration mismatch")

    access_serialized = json.dumps(visit.get("access_options") or [], ensure_ascii=False)
    for key in ("public_transport", "last_mile", "mobility_notes", "terrain_and_movement"):
        old_value = logistics.get(key)
        expected = None
        if old_value not in (None, "", [], {}):
            if not (isinstance(old_value, str) and old_value in access_serialized):
                expected = old_value
        if entry.get(key) != expected:
            fail(f"{obj['id']}: {key} migration mismatch")

    op = entry.get("operational_status") or {}
    for key in (
        "access_mode",
        "access_status",
        "current_alert",
        "security_access_status",
        "security_region",
        "security_snapshot_as_of",
        "status_snapshot",
    ):
        if op.get(key) != operations.get(key):
            fail(f"{obj['id']}: operational_status.{key} migration mismatch")

    safety = ((visit.get("rules") or {}).get("safety") or {})
    for key, default in (
        ("crime_context", None),
        ("main_risks", []),
        ("sensitive_areas", []),
        ("confidence", None),
    ):
        expected = safety_old.get(key)
        if expected in (None, "") and default == []:
            expected = []
        if expected is None and default is not None:
            expected = default
        if safety.get(key) != expected:
            fail(f"{obj['id']}: safety.{key} migration mismatch")

    # Display-name migrations must retain the source object's QA/provenance
    # rather than falling back to the broad legacy bibliography.
    if source_obj and source_obj.get("display_name"):
        expected_verification = source_obj.get("verification") or {}
        if (obj.get("qa") or {}).get("verification") != expected_verification:
            fail(f"{obj['id']}: display-name object lost verification metadata")
        source_fact_review = ((source_obj.get("qa") or {}).get("fact_source_review") or {})
        if source_fact_review.get("status") == "passed":
            canonical_fact_review = ((obj.get("qa") or {}).get("fact_source_review") or {})
            if canonical_fact_review.get("status") != "passed":
                fail(f"{obj['id']}: display-name object lost passed fact_source_review")
            raw_logistics = ((source_obj.get("traveler_card") or {}).get("logistics") or {})
            expected_water_refs = ((raw_logistics.get("water_structured") or {}).get("source_refs") or [])
            expected_overnight_refs = ((raw_logistics.get("overnight") or {}).get("source_refs") or [])
            if ((visit.get("water") or {}).get("source_refs") or []) != expected_water_refs:
                fail(f"{obj['id']}: strict water source scoping was not preserved")
            if ((visit.get("overnight") or {}).get("source_refs") or []) != expected_overnight_refs:
                fail(f"{obj['id']}: strict overnight source scoping was not preserved")

    # Legacy practical language lists must live on referenced geo entities,
    # never be duplicated back onto the attraction.
    old_languages = ((legacy.get("location") or {}).get("languages_spoken") or [])
    if old_languages:
        geo = obj.get("geo") or {}
        candidate_ids = []
        if geo.get("nearest_place_id"):
            candidate_ids.append(geo["nearest_place_id"])
        candidate_ids.extend(reversed(geo.get("region_ids") or []))
        spoken = set()
        for geo_id in candidate_ids:
            path = release / "geo" / "entities" / f"{geo_id}.json"
            if path.exists():
                spoken.update(((load(path).get("languages") or {}).get("spoken") or []))
        missing = [value for value in old_languages if value not in spoken]
        if missing:
            fail(f"{obj['id']}: geo language migration lost {missing}")
        language_values_checked += len(old_languages)

    # Build-CDN visual fallback: old best_light is allowed to populate only
    # best_time when no structured scouting value existed.
    legacy_visual = legacy.get("visual_recon") or {}
    if (obj.get("visual_recon") or {}).get("best_time") != legacy_visual.get("best_time"):
        fail(f"{obj['id']}: visual_recon.best_time migration mismatch")

    objects_checked += 1

if objects_checked != 211:
    fail(f"expected 211 canonical objects, checked {objects_checked}")

print(json.dumps({
    "status": "ok",
    "release_id": ctx["release_id"],
    "schema_version": ctx["schema_version"],
    "objects_checked": objects_checked,
    "source_urls_checked": source_urls_checked,
    "language_values_checked": language_values_checked,
}, ensure_ascii=False, indent=2))
