#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from release_context import get_release_context

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "public" / "cdn" / "v2")
ID_REGISTRY_PATH = ROOT / "data" / "id-registry.json"

OBJECT_ID_RE = re.compile(r"^obj_[a-z]{2}_[0-9]{4}$")
GEO_ID_RE = re.compile(r"^geo_[a-z]{2}(?:_[0-9]{4})?$")
LOD_ID_RE = re.compile(r"^lod_[a-z]{2}_[0-9]{4}$")
SRC_ID_RE = re.compile(r"^src_[0-9]{6}$")
MEDIA_ID_RE = re.compile(r"^med_[a-z]{2}_[0-9a-f]{12}$")

REQUIRED_OBJECT_KEYS = {
    "id",
    "kind",
    "slug",
    "status",
    "names",
    "summary",
    "classification",
    "geo",
    "narrative",
    "visit",
    "traveler_reports",
    "visual_recon",
    "media",
    "relations",
    "freshness",
    "qa",
}
REQUIRED_QA_CHECKS = {
    "language",
    "classification",
    "geo",
    "coordinates",
    "elevation",
    "narrative",
    "sources",
    "access",
    "water",
    "overnight",
    "traveler_reports",
    "visual_recon",
    "gallery_min_5",
    "editorial_rebuild",
}


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(release: Path, rel: str):
    path = release / rel
    if not path.exists():
        fail(f"missing canonical file: {rel}")
    return path


def collect_refs(value, key_name):
    out = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == key_name and isinstance(child, list):
                out.extend(x for x in child if isinstance(x, str))
            out.extend(collect_refs(child, key_name))
    elif isinstance(value, list):
        for child in value:
            out.extend(collect_refs(child, key_name))
    return out


def validate_coordinate_payload(point, context):
    if point is None:
        return
    if not isinstance(point, dict):
        fail(f"{context}: point must be object or null")
    lat = point.get("lat")
    lon = point.get("lon")
    if lat is None and lon is None:
        return
    if not isinstance(lat, (int, float)) or isinstance(lat, bool) or not (-90 <= lat <= 90):
        fail(f"{context}: invalid latitude {lat!r}")
    if not isinstance(lon, (int, float)) or isinstance(lon, bool) or not (-180 <= lon <= 180):
        fail(f"{context}: invalid longitude {lon!r}")
    coordinate_type = point.get("coordinate_type")
    if not coordinate_type:
        fail(f"{context}: coordinate_type required when coordinates exist")
    if not isinstance(point.get("source_refs"), list):
        fail(f"{context}: source_refs must be an array")
    if not isinstance(point.get("elevation_source_refs"), list):
        fail(f"{context}: elevation_source_refs must be an array")
    if (
        point.get("elevation_m") is not None
        or point.get("elevation_range_m") is not None
    ) and not point.get("elevation_source_refs"):
        fail(f"{context}: elevation present without elevation_source_refs")


OBJECT_ELEVATION_REFERENCE_TYPES = {
    "site",
    "summit",
    "highest_point",
    "characteristic",
    "range",
    "water_surface",
    "unknown",
}

def validate_object_elevation(value, context):
    if value is None:
        return False
    if not isinstance(value, dict):
        fail(f"{context}: object_elevation must be object or null")
    representative = value.get("representative_m")
    min_m = value.get("min_m")
    max_m = value.get("max_m")
    numeric = []
    for label, item in [("representative_m", representative), ("min_m", min_m), ("max_m", max_m)]:
        if item is not None:
            if not isinstance(item, (int, float)) or isinstance(item, bool):
                fail(f"{context}: invalid {label} {item!r}")
            numeric.append(item)
    if not numeric:
        fail(f"{context}: object_elevation has no elevation value")
    if min_m is not None and max_m is not None and min_m > max_m:
        fail(f"{context}: min_m must not exceed max_m")
    reference_type = value.get("reference_type")
    if reference_type not in OBJECT_ELEVATION_REFERENCE_TYPES:
        fail(f"{context}: unsupported reference_type {reference_type!r}")
    source_refs = value.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs:
        fail(f"{context}: object_elevation requires source_refs")
    if not value.get("accuracy"):
        fail(f"{context}: object_elevation requires accuracy")
    return True


def main():
    context = get_release_context(PUBLIC)
    release_id = context["release_id"]
    release = context["release"]
    manifest = load(require_file(release, "manifest.json"))
    registry = load(ID_REGISTRY_PATH)

    for key in [
        "project_id",
        "title",
        "schema_version",
        "dataset_version",
        "generated_at",
        "default_language",
        "countries",
        "taxonomy",
        "search",
        "home",
    ]:
        if key not in manifest:
            fail(f"manifest missing canonical field: {key}")

    if manifest.get("project_id") != "expedition_sea":
        fail("manifest project_id must be expedition_sea")
    if manifest.get("default_language") != "ru":
        fail("manifest default_language must be ru")
    if manifest.get("dataset_version") != release_id:
        fail("manifest dataset_version must match release_id")

    # Manifest entrypoints must resolve inside the release.
    for row in manifest.get("countries") or []:
        for key in ["profile", "climate", "travel_rules", "indexes", "search_index"]:
            rel = row.get(key)
            if not rel:
                fail(f"country manifest row missing {key}: {row}")
            require_file(release, rel)
    taxonomy_manifest = manifest.get("taxonomy") or {}
    for key in ["classes", "tags", "transport_modes", "surface_types", "source_types"]:
        rel = taxonomy_manifest.get(key)
        if not rel:
            fail(f"manifest taxonomy missing {key}")
        require_file(release, rel)
    require_file(release, manifest["search"])
    require_file(release, manifest["home"])

    for rel in [
        "schema/schema-version.json",
        "schema/enums.json",
        "schema/geodata-contract.json",
        "geo/index.json",
        "taxonomy/object-classes.json",
        "taxonomy/tags.json",
        "taxonomy/transport-modes.json",
        "taxonomy/surface-types.json",
        "taxonomy/source-types.json",
        "search/global.json",
        "views/home.json",
        "qa/global.json",
    ]:
        require_file(release, rel)

    class_rows = load(release / "taxonomy" / "object-classes.json").get("classes") or []
    class_ids = {row.get("id") for row in class_rows}
    if not class_ids or None in class_ids:
        fail("canonical object class taxonomy is empty or contains blank IDs")

    tag_rows = load(release / "taxonomy" / "tags.json").get("tags") or []
    tag_ids = {row.get("id") for row in tag_rows}
    if None in tag_ids:
        fail("canonical tag taxonomy contains blank ID")

    geo_index = load(release / "geo" / "index.json")
    if geo_index.get("crs") != "WGS84" or geo_index.get("epsg") != 4326:
        fail("geo/index.json must declare WGS84 / EPSG:4326")
    geo_rows = geo_index.get("entities") or []
    geo_ids = {row.get("id") for row in geo_rows}
    if not geo_ids or None in geo_ids:
        fail("canonical geo index is empty or invalid")
    for geo_id in geo_ids:
        if not GEO_ID_RE.match(geo_id):
            fail(f"invalid canonical geo ID: {geo_id}")
        entity = load(require_file(release, f"geo/entities/{geo_id}.json"))
        if entity.get("id") != geo_id:
            fail(f"geo entity id mismatch: {geo_id}")
        parent_id = entity.get("parent_id")
        if parent_id is not None and parent_id not in geo_ids:
            fail(f"geo entity {geo_id} references unknown parent {parent_id}")

    canonical_source_files = list((release / "sources").glob("src_*.json"))
    source_ids = set()
    for path in canonical_source_files:
        entity = load(path)
        source_id = entity.get("id")
        if not source_id or not SRC_ID_RE.match(source_id):
            fail(f"invalid canonical source ID in {path.relative_to(release)}")
        if source_id in source_ids:
            fail(f"duplicate canonical source ID: {source_id}")
        source_ids.add(source_id)
    if len(source_ids) != (manifest.get("totals") or {}).get("canonical_sources"):
        fail("canonical source count differs from manifest")

    canonical_lodging_files = list((release / "infrastructure" / "lodging").glob("[a-z][a-z]/lod_*.json"))
    lodging_ids = set()
    for path in canonical_lodging_files:
        entity = load(path)
        lodging_id = entity.get("id")
        if not lodging_id or not LOD_ID_RE.match(lodging_id):
            fail(f"invalid canonical lodging ID in {path.relative_to(release)}")
        if lodging_id in lodging_ids:
            fail(f"duplicate canonical lodging ID: {lodging_id}")
        lodging_ids.add(lodging_id)
    if len(lodging_ids) != (manifest.get("totals") or {}).get("canonical_lodging"):
        fail("canonical lodging count differs from manifest")

    media_files = list((release / "media").glob("[a-z][a-z]/med_*.json"))
    media_ids = set()
    for path in media_files:
        entity = load(path)
        media_id = entity.get("id")
        if not media_id or not MEDIA_ID_RE.match(media_id):
            fail(f"invalid canonical media ID in {path.relative_to(release)}")
        if media_id in media_ids:
            fail(f"duplicate canonical media ID: {media_id}")
        media_url = entity.get("url")
        if not media_url:
            fail(f"{media_id}: canonical media lacks direct image url")
        lowered_media_url = str(media_url).lower()
        if "/wiki/file:" in lowered_media_url or "/wiki/file%3a" in lowered_media_url:
            fail(f"{media_id}: media.url points to a Wikimedia description page instead of image media")
        media_ids.add(media_id)
    if len(media_ids) != (manifest.get("totals") or {}).get("canonical_media"):
        fail("canonical media count differs from manifest")

    search_doc = load(release / "search" / "global.json")
    search_rows = search_doc.get("objects") or []
    if search_doc.get("count") != len(search_rows):
        fail("search/global count mismatch")
    if len(search_rows) != (manifest.get("totals") or {}).get("canonical_objects"):
        fail("canonical object count differs from manifest")

    object_ids = []
    country_codes = {row.get("code") for row in manifest.get("countries") or []}
    for row in search_rows:
        object_id = row.get("id")
        if not object_id or not OBJECT_ID_RE.match(object_id):
            fail(f"invalid canonical object ID: {object_id}")
        object_ids.append(object_id)
        if set(row) & {"narrative", "visit", "traveler_reports", "visual_recon", "freshness"}:
            fail(f"search/global contains full object payload: {object_id}")
        class_id = row.get("class_id")
        if class_id not in class_ids:
            fail(f"search object {object_id} uses unknown class {class_id}")
        unknown_tags = set(row.get("tag_ids") or []) - tag_ids
        if unknown_tags:
            fail(f"search object {object_id} uses unknown tags: {sorted(unknown_tags)}")
        unknown_geo = set(row.get("geo_ids") or []) - geo_ids
        if unknown_geo:
            fail(f"search object {object_id} uses unknown geo refs: {sorted(unknown_geo)}")
        cover = row.get("cover_media_id")
        if cover is not None and cover not in media_ids:
            fail(f"search object {object_id} references unknown cover media {cover}")
        preview_asset = row.get("preview_asset")
        if not preview_asset:
            fail(f"search object {object_id} is missing local preview_asset")
        preview_path = PUBLIC / preview_asset
        if not preview_path.is_file():
            fail(f"search object {object_id} preview binary is missing: {preview_asset}")
        if preview_path.suffix.lower() != ".webp" or preview_path.stat().st_size < 256:
            fail(f"search object {object_id} has invalid preview binary: {preview_asset}")

        parts = object_id.split("_")
        code = parts[1]
        if code not in country_codes:
            fail(f"object {object_id} country code is not present in manifest")
        object_path = require_file(release, f"objects/{code}/{object_id}.json")
        obj = load(object_path)
        if obj.get("id") != object_id:
            fail(f"object id mismatch in {object_path.relative_to(release)}")
        missing_keys = REQUIRED_OBJECT_KEYS - set(obj)
        if missing_keys:
            fail(f"{object_id} missing canonical keys: {sorted(missing_keys)}")
        if obj.get("kind") != "attraction":
            fail(f"{object_id}: kind must be attraction")
        if not (obj.get("summary") or {}).get("narrow"):
            fail(f"{object_id}: summary.narrow required")
        classification = obj.get("classification") or {}
        if classification.get("class_id") not in class_ids:
            fail(f"{object_id}: invalid class_id")
        if not isinstance(classification.get("tag_ids"), list):
            fail(f"{object_id}: tag_ids must be an array")

        geo = obj.get("geo") or {}
        if geo.get("country_id") not in geo_ids:
            fail(f"{object_id}: unknown country_id")
        for geo_id in geo.get("region_ids") or []:
            if geo_id not in geo_ids:
                fail(f"{object_id}: unknown region_id {geo_id}")
        nearest = geo.get("nearest_place_id")
        if nearest is not None and nearest not in geo_ids:
            fail(f"{object_id}: unknown nearest_place_id {nearest}")
        validate_coordinate_payload(geo.get("primary_location"), f"{object_id}:primary_location")
        for index, point in enumerate(geo.get("geo_points") or []):
            validate_coordinate_payload(point, f"{object_id}:geo_points[{index}]")
        has_object_elevation = validate_object_elevation(
            geo.get("object_elevation"),
            f"{object_id}:object_elevation",
        )

        narrative = obj.get("narrative") or {}
        if not isinstance(narrative.get("sections"), list) or not narrative.get("sections"):
            fail(f"{object_id}: narrative.sections must be non-empty")
        for section in narrative.get("sections") or []:
            if not section.get("section_id") or section.get("content") in (None, "", [], {}):
                fail(f"{object_id}: malformed narrative section")

        visit = obj.get("visit") or {}
        for key in ["entry", "access_options", "water", "supplies", "overnight", "lodging_ids", "rules", "seasonality"]:
            if key not in visit:
                fail(f"{object_id}: visit missing {key}")
        for lodging_id in visit.get("lodging_ids") or []:
            if lodging_id not in lodging_ids:
                fail(f"{object_id}: unknown lodging ref {lodging_id}")

        media = obj.get("media") or {}
        cover_id = media.get("cover_id")
        if cover_id is not None and cover_id not in media_ids:
            fail(f"{object_id}: unknown cover media {cover_id}")
        if media.get("preview_asset") != row.get("preview_asset"):
            fail(f"{object_id}: canonical media.preview_asset diverges from search preview")
        gallery_ids = media.get("gallery_ids") or []
        if len(gallery_ids) != len(set(gallery_ids)):
            fail(f"{object_id}: duplicate media IDs in gallery")
        for media_id in gallery_ids:
            if media_id not in media_ids:
                fail(f"{object_id}: unknown gallery media {media_id}")

        for source_id in collect_refs(obj, "source_refs") + collect_refs(obj, "elevation_source_refs"):
            if source_id not in source_ids:
                fail(f"{object_id}: unknown canonical source ref {source_id}")

        qa = obj.get("qa") or {}
        checks = qa.get("checks") or {}
        if set(checks) != REQUIRED_QA_CHECKS:
            fail(f"{object_id}: QA check set mismatch: {sorted(checks)}")
        if bool(checks.get("elevation")) != bool(has_object_elevation):
            fail(f"{object_id}: elevation QA must reflect geo.object_elevation, not GPS-point elevation")
        if bool(checks.get("gallery_min_5")) != (len(gallery_ids) >= 5):
            fail(f"{object_id}: gallery_min_5 QA must reflect at least five unique gallery media refs")
        qa_path = require_file(release, f"qa/objects/{code}/{object_id}.json")
        qa_doc = load(qa_path)
        if qa_doc.get("object_id") != object_id:
            fail(f"{object_id}: object QA file mismatch")
        card = load(require_file(release, f"views/object-cards/{object_id}.json"))
        if card != row:
            fail(f"{object_id}: object card view diverges from canonical search row")

    if len(object_ids) != len(set(object_ids)):
        fail("duplicate canonical object IDs")

    # Registry must preserve one-to-one permanent IDs for all migrated objects.
    registry_object_values = list((registry.get("objects") or {}).values())
    if len(registry_object_values) != len(set(registry_object_values)):
        fail("object ID registry has duplicate canonical IDs")
    if set(object_ids) != set(registry_object_values):
        fail("canonical object set differs from persistent object ID registry")

    for country_row in manifest.get("countries") or []:
        code = country_row["code"]
        indexes = load(release / country_row["indexes"])
        if indexes.get("country_id") != f"geo_{code}":
            fail(f"{code}: country indexes country_id mismatch")
        if set(indexes.get("object_ids") or []) != {
            oid for oid in object_ids if oid.startswith(f"obj_{code}_")
        }:
            fail(f"{code}: country object index mismatch")
        for geo_id in indexes.get("geo_ids") or []:
            if geo_id not in geo_ids:
                fail(f"{code}: unknown geo index ref {geo_id}")
        for lodging_id in indexes.get("lodging_ids") or []:
            if lodging_id not in lodging_ids:
                fail(f"{code}: unknown lodging index ref {lodging_id}")
        for media_id in indexes.get("media_ids") or []:
            if media_id not in media_ids:
                fail(f"{code}: unknown media index ref {media_id}")

        profile = load(release / country_row["profile"])
        rich_food_rows = [
            row for row in (profile.get("street_food") or [])
            if isinstance(row, dict) and row.get("media_id")
        ]
        rich_festival_rows = [
            row for row in (profile.get("festivals") or [])
            if isinstance(row, dict) and row.get("media_id")
        ]
        for index, row in enumerate(rich_food_rows, start=1):
            if not row.get("name") or not row.get("description"):
                fail(f"{code}: rich street-food row {index} lacks name/description")
            if not row.get("price_usd_range"):
                fail(f"{code}: rich street-food row {index} lacks approximate market/street-food price")
            media_id = row.get("media_id")
            if not media_id or media_id not in media_ids:
                fail(f"{code}: rich street-food row {index} lacks valid canonical media ref")
            if not row.get("checked_at") or not row.get("source_refs"):
                fail(f"{code}: rich street-food row {index} lacks checked_at/source_refs")
            unknown_refs = set(row.get("source_refs") or []) - source_ids
            if unknown_refs:
                fail(f"{code}: rich street-food row {index} uses unknown source refs {sorted(unknown_refs)}")

        for index, row in enumerate(rich_festival_rows, start=1):
            if not row.get("name") or not row.get("description"):
                fail(f"{code}: rich festival row {index} lacks name/description")
            media_id = row.get("media_id")
            if not media_id or media_id not in media_ids:
                fail(f"{code}: rich festival row {index} lacks valid canonical media ref")
            if not row.get("checked_at") or not row.get("source_refs"):
                fail(f"{code}: rich festival row {index} lacks checked_at/source_refs")
            unknown_refs = set(row.get("source_refs") or []) - source_ids
            if unknown_refs:
                fail(f"{code}: rich festival row {index} uses unknown source refs {sorted(unknown_refs)}")

        travel_rules = load(release / country_row["travel_rules"])
        for key, value in travel_rules.items():
            if key == "country_id":
                continue
            if not isinstance(value, dict):
                fail(f"{code}: dynamic travel field {key} must be an object")
            if "source_refs" not in value or "checked_at" not in value:
                fail(f"{code}: dynamic travel field {key} lacks source_refs/checked_at")

        require_file(release, f"routes/{code}/index.json")
        require_file(release, f"infrastructure/poi/{code}/index.json")
        require_file(release, f"infrastructure/transport/{code}/index.json")
        require_file(release, f"media/{code}/index.json")
        require_file(release, f"qa/countries/{code}.json")
        require_file(release, f"views/countries/{code}.json")

    global_qa = load(release / "qa" / "global.json")
    if global_qa.get("objects_total") != len(object_ids):
        fail("qa/global object count mismatch")

    print(json.dumps({
        "status": "ok",
        "release_id": release_id,
        "schema_version": manifest.get("schema_version"),
        "canonical_objects": len(object_ids),
        "canonical_geo_entities": len(geo_ids),
        "canonical_sources": len(source_ids),
        "canonical_lodging": len(lodging_ids),
        "canonical_media": len(media_ids),
        "countries": len(country_codes),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
