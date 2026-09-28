#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
PUBLIC = ROOT / "public" / "cdn" / "v2"
ID_REGISTRY_PATH = ROOT / "data" / "id-registry.json"
HIERARCHY = ROOT / "data" / "hierarchy" / "countries"
FORMAL_CANONICAL_GEO_CODES = {"KH", "LA"}
COUNTRY_SOURCE_CANONICAL_CODES = {"KH", "LA"}

GENERATED_AT = "2026-09-29T00:35:00+04:00"
DEFAULT_LANGUAGE = "ru"

CLASS_ID_MAP = {
    "archaeological_site": "archaeology.site",
    "historic_city": "settlement.historic_city",
    "national_park": "nature.national_park",
    "island": "nature.island",
    "religious_site": "religion.sacred_site",
    "cultural_landscape": "heritage.cultural_landscape",
    "cave": "nature.cave",
    "living_settlement": "ethnography.living_settlement",
    "protected_area": "nature.reserve",
    "lake": "nature.lake",
    "karst": "nature.karst",
    "museum": "heritage.museum",
    "city": "settlement.city",
    "forest": "nature.jungle",
    "industrial_heritage": "heritage.industrial",
    "market": "ethnography.market",
    "megalithic_site": "archaeology.megalith",
    "mountain": "nature.mountain",
    "plateau": "nature.plateau",
    "volcano": "nature.volcano",
    "wildlife_site": "nature.wildlife_site",
    "historic_building": "architecture.historic_building",
    "mangrove": "nature.mangrove",
    "memorial_site": "heritage.memorial",
    "monument": "heritage.monument",
    "natural_landscape": "nature.landscape",
    "palace": "architecture.palace",
    "river": "nature.river",
    "waterfall": "nature.waterfall",
    "wetland": "nature.wetland",
}

TRANSPORT_MODES = [
    "public_transport",
    "taxi",
    "ride_hailing",
    "car",
    "moped",
    "motorcycle",
    "boat",
    "ferry",
    "walking",
    "bicycle",
    "other",
]
SURFACE_TYPES = ["paved", "gravel", "dirt", "trail", "stairs", "mixed", "unknown"]
SOURCE_TYPES = [
    "project_material",
    "government_official",
    "park_authority",
    "museum",
    "archaeological_service",
    "unesco",
    "academic",
    "university",
    "map_osm",
    "official_map",
    "traveler_report",
    "reddit",
    "forum",
    "blog",
    "youtube",
    "google_maps",
    "social_media",
    "other",
]
GEO_KINDS = {
    "country",
    "region",
    "province",
    "state",
    "district",
    "island",
    "archipelago",
    "city",
    "town",
    "village",
    "settlement",
    "protected_area",
    "geographic_area",
}
COORDINATE_TYPES = {
    "center",
    "entrance",
    "trailhead",
    "summit",
    "viewpoint",
    "pier",
    "parking",
    "cave_entrance",
    "waterfall_base",
    "archaeological_core",
    "temple_entrance",
}


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_entry(path: Path, release: Path):
    payload = path.read_bytes()
    return {
        "path": path.relative_to(release).as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def require_id(registry: dict, section: str, legacy_id: str) -> str:
    value = (registry.get(section) or {}).get(legacy_id)
    if not value:
        raise RuntimeError(f"missing persistent ID registry entry: {section} / {legacy_id}")
    return value


def remap_source_refs(values, registry):
    out = []
    for value in values or []:
        canonical = require_id(registry, "sources", value)
        if canonical not in out:
            out.append(canonical)
    return out


def remap_geo_sources(geo, registry):
    geo = json.loads(json.dumps(geo or {}, ensure_ascii=False))
    for point in [geo.get("primary_location")] + list(geo.get("points") or []):
        if not isinstance(point, dict):
            continue
        point["source_refs"] = remap_source_refs(point.get("source_refs"), registry)
        point["elevation_source_refs"] = remap_source_refs(point.get("elevation_source_refs"), registry)
    object_elevation = geo.get("object_elevation")
    if isinstance(object_elevation, dict):
        object_elevation["source_refs"] = remap_source_refs(object_elevation.get("source_refs"), registry)
    return geo


def remap_visual_sources(visual, registry):
    visual = json.loads(json.dumps(visual or {}, ensure_ascii=False))
    for row in visual.get("viewpoints") or []:
        if isinstance(row, dict):
            row["source_refs"] = remap_source_refs(row.get("source_refs"), registry)
    return visual


def canonical_point(point):
    if not isinstance(point, dict):
        return None
    coordinates = point.get("coordinates")
    if not isinstance(coordinates, dict):
        return None
    return {
        "lat": coordinates.get("lat"),
        "lon": coordinates.get("lon"),
        "elevation_m": coordinates.get("elevation_m"),
        "elevation_range_m": coordinates.get("elevation_range_m"),
        "coordinate_type": point.get("type"),
        "accuracy": point.get("accuracy") or "unknown",
        "elevation_accuracy": point.get("elevation_accuracy") or "unknown",
        "source_refs": point.get("source_refs") or [],
        "elevation_source_refs": point.get("elevation_source_refs") or [],
        "checked_at": point.get("checked_at"),
    }


def narrative_sections(story, source_refs):
    story = story or {}
    allowed = {"overview", "history", "culture", "geography", "geology", "ethnography", "myths_beliefs"}
    structured = story.get("sections")
    if isinstance(structured, list) and structured:
        rows = []
        for raw in structured:
            if not isinstance(raw, dict):
                continue
            section_id = raw.get("section_id")
            content = raw.get("content")
            if section_id not in allowed:
                raise RuntimeError(f"unknown canonical narrative section: {section_id}")
            if content in (None, "", [], {}):
                continue
            rows.append({
                "section_id": section_id,
                "content": content,
                "source_refs": list(dict.fromkeys((raw.get("source_refs") or []) + list(source_refs))),
            })
        if rows:
            return rows
    rows = []
    mapping = [
        ("narrative", "overview", None),
        ("culture_ethnography", "culture", "Legacy combined section retained under culture until country research splits it."),
        ("geography_geology", "geography", "Legacy combined section retained under geography until country research splits it."),
        ("myths_legends_beliefs", "myths_beliefs", None),
    ]
    for key, section_id, migration_note in mapping:
        value = story.get(key)
        if value in (None, "", [], {}):
            continue
        row = {"section_id": section_id, "content": value, "source_refs": list(source_refs)}
        if migration_note:
            row["migration_note"] = migration_note
        rows.append(row)
    return rows


def access_options(logistics):
    logistics = logistics or {}
    raw_modes = logistics.get("modes") or {}
    mode_aliases = {
        "public_transport": "public_transport",
        "taxi_ridehail": "ride_hailing",
        "taxi": "taxi",
        "ride_hailing": "ride_hailing",
        "car": "car",
        "moped": "moped",
        "motorcycle": "motorcycle",
        "boat": "boat",
        "ferry": "ferry",
        "walking": "walking",
        "bicycle": "bicycle",
    }
    options = []
    if isinstance(raw_modes, dict):
        for raw_mode, note in raw_modes.items():
            if note in (None, "", [], {}):
                continue
            mode = mode_aliases.get(raw_mode, "other")
            options.append({
                "origin": None,
                "modes": [mode],
                "legs": [{
                    "mode": mode,
                    "distance_km": None,
                    "duration_min": None,
                    "surface": None,
                    "condition": None,
                    "seasonality": None,
                    "elevation_gain_m": None,
                    "elevation_loss_m": None,
                    "trailhead": None,
                    "navigation": None,
                    "fords": None,
                    "notes": note,
                }],
            })
    return options


def traveler_reports_list(value):
    if value in (None, "", [], {}):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        recurring = value.get("recurring_issues")
        if isinstance(recurring, list):
            rows = [
                {
                    "kind": "aggregated_recurring_issue",
                    "summary": item,
                    "source_refs": [],
                }
                for item in recurring
                if item not in (None, "")
            ]
            other = {k: v for k, v in value.items() if k != "recurring_issues" and v not in (None, "", [], {})}
            if other:
                rows.append({
                    "kind": "legacy_aggregate",
                    "data": other,
                    "source_refs": [],
                })
            return rows
        return [{"kind": "legacy_aggregate", "data": value, "source_refs": []}]
    return [{"kind": "legacy_note", "summary": str(value), "source_refs": []}]


def media_id_for(country_code: str, row: dict) -> str:
    identity = row.get("url") or row.get("static_url") or row.get("source_page")
    if not identity:
        identity = json.dumps(row, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha1(str(identity).encode("utf-8")).hexdigest()[:12]
    return f"med_{country_code.lower()}_{digest}"


def source_files_by_code(published_codes):
    result = {}
    for path in sorted(SRC.glob("*.json")):
        try:
            data = load(path)
        except Exception:
            continue
        code = ((data.get("meta") or {}).get("country_code") or "").upper()
        if code in published_codes:
            result[code] = (path, data)
    missing = sorted(published_codes - set(result))
    if missing:
        raise RuntimeError(f"missing source files for published countries: {missing}")
    return result


def wrap_dynamic(value, checked_at, source_refs=None, note=None):
    source_refs = list(dict.fromkeys(source_refs or []))
    return {
        "value": value,
        "source_refs": source_refs,
        "checked_at": checked_at,
        "qa": {
            "source_refs_complete": bool(source_refs),
            "note": note or ("Country-level fact has normalized canonical source refs." if source_refs else "Country-level fact still requires fact-level source normalization."),
        },
    }


def build():
    latest = load(PUBLIC / "latest.json")
    release = PUBLIC / latest["release_id"]
    if not release.exists():
        raise RuntimeError(f"release does not exist: {release}")

    registry = load(ID_REGISTRY_PATH)
    countries_doc = load(release / "countries.json")
    legacy_countries = countries_doc.get("countries") or []
    published_codes = {row["country_code"] for row in legacy_countries}
    sources_by_code = source_files_by_code(published_codes)
    country_slug_by_code = {row["country_code"]: row["slug"] for row in legacy_countries if row.get("country_code") and row.get("slug")}
    source_object_by_country_name = {}
    for code, (_, source_doc) in sources_by_code.items():
        for row in ((source_doc.get("travel") or {}).get("objects") or []):
            if row.get("name"):
                source_object_by_country_name[(code, row.get("name"))] = row
    formal_hierarchy = {}
    for code in sorted(published_codes & FORMAL_CANONICAL_GEO_CODES):
        slug = country_slug_by_code.get(code)
        path = HIERARCHY / f"{slug}.json" if slug else None
        if path and path.exists():
            doc = load(path)
            if (doc.get("meta") or {}).get("country_code") != code:
                raise RuntimeError(f"formal hierarchy country mismatch: {path}")
            formal_hierarchy[code] = doc

    legacy_search = load(release / "search" / "objects.json").get("objects") or []
    legacy_places = load(release / "places.json").get("places") or []
    legacy_types = load(release / "object-types.json").get("object_types") or []
    legacy_taxonomy = load(release / "taxonomy.json")
    legacy_lodging = load(release / "infrastructure" / "lodging" / "index.json").get("lodging") or []
    legacy_sources = load(release / "sources" / "index.json").get("sources") or []

    type_labels = {row.get("value"): row.get("label_ru") for row in legacy_types}
    object_rows_by_country = defaultdict(list)
    geo_entities = {}
    media_registry = {}
    canonical_search = []
    canonical_objects = {}
    canonical_lodging_ids_by_country = defaultdict(list)
    canonical_media_ids_by_country = defaultdict(list)
    canonical_geo_ids_by_country = defaultdict(list)
    canonical_object_ids_by_country = defaultdict(list)
    formal_geo_refs_by_object = defaultdict(list)
    country_source_ids_by_code = defaultdict(dict)

    # Canonical country and legacy-place geography.
    place_id_by_country_name_kind = {}
    for code in sorted(published_codes):
        source = sources_by_code[code][1]
        country_id = f"geo_{code.lower()}"
        geo_entities[country_id] = {
            "id": country_id,
            "kind": "country",
            "names": {"primary": (source.get("meta") or {}).get("country")},
            "slug": code.lower(),
            "parent_id": None,
            "geo_path": [country_id],
            "description": {
                "narrow": (source.get("overview") or {}).get("narrow")
                or (source.get("overview") or {}).get("summary"),
                "body": (source.get("overview") or {}).get("summary"),
            },
            "cover_media_id": None,
            "legacy_ids": [f"country:{code.lower()}"],
        }
        canonical_geo_ids_by_country[code].append(country_id)

    for place in legacy_places:
        code = place.get("country_code")
        legacy_id = place.get("id")
        if not code or not legacy_id:
            continue
        if code in formal_hierarchy:
            continue
        geo_id = require_id(registry, "geo", legacy_id)
        country_id = f"geo_{code.lower()}"
        kind = "geographic_area"
        if place.get("kind") == "region":
            kind = "geographic_area"
        elif place.get("kind") == "city_or_route_hub":
            kind = "geographic_area"
        if kind not in GEO_KINDS:
            kind = "geographic_area"
        entity = {
            "id": geo_id,
            "kind": kind,
            "names": {"primary": place.get("name")},
            "slug": place.get("slug"),
            "parent_id": country_id,
            "geo_path": [country_id, geo_id],
            "description": {
                "narrow": place.get("narrow"),
                "body": None,
            },
            "cover_media_id": None,
            "legacy_ids": [legacy_id],
            "migration": {
                "source_kind": place.get("kind"),
                "note": "Legacy route regions/hubs are kept as geographic_area until formal administrative or settlement identity is verified.",
            },
        }
        geo_entities[geo_id] = entity
        canonical_geo_ids_by_country[code].append(geo_id)
        place_id_by_country_name_kind[(code, place.get("name"), place.get("kind"))] = geo_id

    for code, doc in formal_hierarchy.items():
        country_id = f"geo_{code.lower()}"
        nodes = doc.get("nodes") or []
        node_by_id = {node["id"]: node for node in nodes}
        canonical_id_by_node = {}
        for node in nodes:
            node_id = node["id"]
            canonical_id = node.get("canonical_id")
            if not canonical_id:
                raise RuntimeError(f"{code}: formal geography node missing canonical_id: {node_id}")
            canonical_id_by_node[node_id] = canonical_id
        if len(set(canonical_id_by_node.values())) != len(canonical_id_by_node):
            raise RuntimeError(f"{code}: duplicate canonical geo IDs in formal hierarchy")

        path_cache = {}
        def formal_geo_path(node_id, stack=None):
            if node_id in path_cache:
                return path_cache[node_id]
            stack = set(stack or [])
            if node_id in stack:
                raise RuntimeError(f"{code}: formal geography cycle at {node_id}")
            stack.add(node_id)
            node = node_by_id[node_id]
            parent = node.get("parent_id")
            if parent == f"country:{code.lower()}":
                out = [country_id, canonical_id_by_node[node_id]]
            elif parent in node_by_id:
                out = formal_geo_path(parent, stack) + [canonical_id_by_node[node_id]]
            else:
                raise RuntimeError(f"{code}: unknown formal geography parent {parent}")
            path_cache[node_id] = out
            return out

        for node in nodes:
            node_id = node["id"]
            geo_id = canonical_id_by_node[node_id]
            parent = node.get("parent_id")
            parent_id = country_id if parent == f"country:{code.lower()}" else canonical_id_by_node[parent]
            kind = node.get("kind") or "geographic_area"
            if kind not in GEO_KINDS:
                kind = "geographic_area"
            geo_entities[geo_id] = {
                "id": geo_id,
                "kind": kind,
                "names": {"primary": node.get("name_ru") or node.get("name_local") or node_id, "local": node.get("name_local")},
                "slug": node.get("slug"),
                "parent_id": parent_id,
                "geo_path": formal_geo_path(node_id),
                "description": {"narrow": node.get("notes_ru"), "body": None},
                "cover_media_id": None,
                "legacy_ids": [node_id],
                "migration": {"source_kind": "formal_hierarchy", "axis": node.get("axis"), "status": "formalized"},
                "provenance": {"checked_at": (doc.get("meta") or {}).get("checked_at"), "sources": doc.get("sources") or []},
            }
            canonical_geo_ids_by_country[code].append(geo_id)
            for old_object_id in node.get("object_ids") or []:
                for ref in formal_geo_path(node_id)[1:]:
                    if ref not in formal_geo_refs_by_object[(code, old_object_id)]:
                        formal_geo_refs_by_object[(code, old_object_id)].append(ref)

    # Canonical sources coexist with legacy source files during the compatibility phase.
    canonical_source_ids = set()
    for row in legacy_sources:
        old_id = row.get("id")
        if not old_id:
            continue
        source_id = require_id(registry, "sources", old_id)
        detail_path = row.get("detail_path")
        if not detail_path:
            raise RuntimeError(f"legacy source missing detail_path: {old_id}")
        detail = load(release / detail_path)
        entity = dict(detail)
        entity["id"] = source_id
        entity["legacy_ids"] = [old_id]
        entity["referenced_by"] = [
            require_id(registry, "objects", legacy_object_id)
            for legacy_object_id in (detail.get("referenced_by") or [])
        ]
        dump(release / "sources" / f"{source_id}.json", entity)
        canonical_source_ids.add(source_id)

    source_type_map = {
        "government": "government_official",
        "airport_official": "other",
        "international_organization": "other",
        "secondary_climatology": "other",
        "scientific_database": "other",
        "academic": "academic",
        "university": "university",
    }
    for code in sorted(published_codes & COUNTRY_SOURCE_CANONICAL_CODES):
        country_source = sources_by_code[code][1]
        for row in country_source.get("sources") or []:
            short_id = row.get("id")
            source_id = row.get("canonical_id")
            if not short_id or not source_id:
                raise RuntimeError(f"{code}: country source missing id/canonical_id: {short_id}")
            if source_id in canonical_source_ids:
                raise RuntimeError(f"{code}: duplicate canonical source ID: {source_id}")
            dump(release / "sources" / f"{source_id}.json", {
                "id": source_id,
                "type": source_type_map.get(row.get("kind"), "other"),
                "title": row.get("title"),
                "publisher": row.get("publisher"),
                "url": row.get("url"),
                "language": row.get("language"),
                "published_at": row.get("published_at"),
                "accessed_at": row.get("accessed"),
                "authority": "high" if row.get("kind") in {"government", "international_organization", "airport_official"} else "medium",
                "used_for": row.get("used_for") or [],
                "notes": row.get("notes"),
                "referenced_by": [],
                "legacy_ids": [f"country:{code.lower()}:{short_id}"],
            })
            canonical_source_ids.add(source_id)
            country_source_ids_by_code[code][short_id] = source_id

    # Canonical lodging copies use persistent IDs and country-code paths.
    canonical_lodging_ids = set()
    for row in legacy_lodging:
        old_id = row.get("id")
        code = row.get("country_code")
        if not old_id or not code:
            continue
        lodging_id = require_id(registry, "lodging", old_id)
        detail_path = row.get("detail_path")
        if not detail_path:
            raise RuntimeError(f"legacy lodging missing detail_path: {old_id}")
        detail = load(release / detail_path)
        entity = {
            "id": lodging_id,
            "kind": "lodging",
            "country_id": f"geo_{code.lower()}",
            "names": {"primary": detail.get("name")},
            "area": detail.get("area"),
            "coordinates": detail.get("coordinates"),
            "price_for_two": detail.get("price_for_two"),
            "checked_at": detail.get("checked_at"),
            "contacts": detail.get("contact"),
            "website_or_social": detail.get("social_or_web"),
            "features": detail.get("features") or [],
            "traveler_reports": detail.get("traveler_reports") or [],
            "source_refs": [],
            "legacy_source": detail.get("source"),
            "relations": {
                "legacy_ids": [old_id],
                "referenced_by": [
                    require_id(registry, "objects", legacy_object_id)
                    for legacy_object_id in (detail.get("referenced_by") or [])
                ],
            },
            "qa": {
                "source_refs_complete": False,
                "note": "Legacy lodging source must be normalized into canonical source_refs in the country research pass.",
            },
        }
        dump(release / "infrastructure" / "lodging" / code.lower() / f"{lodging_id}.json", entity)
        canonical_lodging_ids.add(lodging_id)
        canonical_lodging_ids_by_country[code].append(lodging_id)

    for legacy_row in legacy_search:
        code = legacy_row.get("country_code")
        if not code:
            raise RuntimeError(f"object without country_code: {legacy_row.get('id')}")
        old_object_id = legacy_row.get("id")
        object_id = require_id(registry, "objects", old_object_id)
        detail_path = legacy_row.get("detail_path")
        detail = load(release / detail_path)

        legacy_type = (detail.get("identity") or {}).get("object_type")
        class_id = CLASS_ID_MAP.get(legacy_type)
        if not class_id:
            raise RuntimeError(f"unmapped object class: {legacy_type}")

        source_refs = remap_source_refs((detail.get("provenance") or {}).get("source_refs"), registry)
        legacy_geo = remap_geo_sources(detail.get("geo"), registry)
        primary_location = canonical_point(legacy_geo.get("primary_location"))
        object_elevation = legacy_geo.get("object_elevation")
        geo_points = [
            canonical_point(point)
            for point in (legacy_geo.get("points") or [])
            if canonical_point(point) is not None
        ]

        location = detail.get("location") or {}
        if code in formal_hierarchy:
            region_ids = list(formal_geo_refs_by_object.get((code, old_object_id), []))
            nearest_place_id = next((geo_id for geo_id in reversed(region_ids) if (geo_entities.get(geo_id) or {}).get("kind") in {"city", "town", "village", "settlement"}), None)
            geo_ids = [f"geo_{code.lower()}"] + region_ids
        else:
            region_id = place_id_by_country_name_kind.get((code, location.get("region"), "region"))
            nearest_place_id = place_id_by_country_name_kind.get((code, location.get("nearest_hub"), "city_or_route_hub"))
            region_ids = [region_id] if region_id else []
            geo_ids = [f"geo_{code.lower()}"]
            if region_id:
                geo_ids.append(region_id)
            if nearest_place_id and nearest_place_id not in geo_ids:
                geo_ids.append(nearest_place_id)

        gallery = (detail.get("media") or {}).get("gallery") or []
        media_ids = []
        for media_row in gallery:
            if not isinstance(media_row, dict):
                continue
            media_id = media_id_for(code, media_row)
            media_ids.append(media_id)
            existing = media_registry.get(media_id)
            if existing is None:
                media_registry[media_id] = {
                    "id": media_id,
                    "kind": "image",
                    "country_id": f"geo_{code.lower()}",
                    "url": media_row.get("url") or media_row.get("static_url"),
                    "source_page": media_row.get("source_page"),
                    "provider": media_row.get("provider"),
                    "license": media_row.get("license"),
                    "artist": media_row.get("artist"),
                    "checked_at": media_row.get("last_checked"),
                    "source_refs": [],
                    "referenced_by": [object_id],
                }
            elif object_id not in existing["referenced_by"]:
                existing["referenced_by"].append(object_id)
            if media_id not in canonical_media_ids_by_country[code]:
                canonical_media_ids_by_country[code].append(media_id)

        old_lodging_ids = (detail.get("visit") or {}).get("lodging_ids") or []
        lodging_ids = [require_id(registry, "lodging", value) for value in old_lodging_ids]
        logistics = (detail.get("visit") or {}).get("logistics") or {}
        operations = (detail.get("visit") or {}).get("operations") or {}
        visual_recon = remap_visual_sources(detail.get("visual_recon"), registry)
        source_object = source_object_by_country_name.get((code, (detail.get("identity") or {}).get("name")))
        story_payload = dict(detail.get("story") or {})
        source_sections = ((((source_object or {}).get("traveler_card") or {}).get("annotation") or {}).get("sections"))
        if isinstance(source_sections, list) and source_sections:
            story_payload["sections"] = source_sections
        sections = narrative_sections(story_payload, source_refs)
        reports = traveler_reports_list((detail.get("visit") or {}).get("traveler_reports"))
        language_review = ((source_object or {}).get("qa") or {}).get("language_review") or {}

        checks = {
            "language": bool((detail.get("identity") or {}).get("narrow") or sections) and (code != "KH" or language_review.get("status") == "reviewed"),
            "classification": bool(class_id),
            "geo": bool(geo_ids),
            "coordinates": bool(primary_location and primary_location.get("lat") is not None and primary_location.get("lon") is not None),
            "elevation": bool(
                isinstance(object_elevation, dict)
                and (
                    object_elevation.get("representative_m") is not None
                    or object_elevation.get("min_m") is not None
                    or object_elevation.get("max_m") is not None
                )
            ),
            "narrative": bool(sections),
            "sources": bool(source_refs),
            "access": bool(access_options(logistics) or logistics.get("access")),
            "water": bool(logistics.get("water")),
            "overnight": bool(logistics.get("overnight_and_camping")),
            "traveler_reports": bool(reports),
            "visual_recon": bool(visual_recon.get("best_time") or visual_recon.get("viewpoints")),
        }
        status = "passed" if all(checks.values()) else "incomplete"

        canonical = {
            "id": object_id,
            "kind": "attraction",
            "slug": (detail.get("meta") or {}).get("slug") or legacy_row.get("slug"),
            "status": "published",
            "names": {"primary": (detail.get("identity") or {}).get("name")},
            "summary": {"narrow": (detail.get("identity") or {}).get("narrow")},
            "classification": {
                "class_id": class_id,
                "tag_ids": (detail.get("identity") or {}).get("tags") or [],
            },
            "geo": {
                "country_id": f"geo_{code.lower()}",
                "region_ids": region_ids,
                "nearest_place_id": nearest_place_id,
                "nearest_place_name_raw": location.get("nearest_hub"),
                "primary_location": primary_location,
                "geo_points": geo_points,
                "object_elevation": object_elevation,
            },
            "narrative": {"sections": sections},
            "visit": {
                "entry": {
                    "hours": operations.get("hours"),
                    "ticket": operations.get("ticket"),
                    "closure_notes": operations.get("closure_notes"),
                    "status": operations.get("status"),
                    "official_url": operations.get("official_url"),
                    "notes": logistics.get("access"),
                    "source_refs": source_refs,
                    "checked_at": operations.get("last_verified"),
                },
                "access_options": access_options(logistics),
                "water": {
                    "summary": logistics.get("water"),
                    "quality": "unknown",
                    "last_reliable_source": None,
                    "distance_m": None,
                    "natural_sources": [],
                    "source_refs": source_refs,
                },
                "supplies": None,
                "overnight": {
                    "status": "unclear",
                    "summary": logistics.get("overnight_and_camping"),
                    "source_refs": source_refs,
                },
                "lodging_ids": lodging_ids,
                "rules": {
                    "permit_or_guide": logistics.get("permit_or_guide"),
                    "access_requirements": logistics.get("access_requirements"),
                    "source_refs": source_refs,
                    "checked_at": operations.get("last_verified"),
                },
                "seasonality": (detail.get("visit") or {}).get("climate"),
            },
            "traveler_reports": reports,
            "visual_recon": visual_recon,
            "media": {
                "cover_id": media_ids[0] if media_ids else None,
                "gallery_ids": media_ids,
            },
            "relations": {
                "legacy_ids": [old_object_id],
                "legacy_detail_path": detail_path,
            },
            "freshness": {
                "checked_at": operations.get("last_verified"),
                "source_file": (detail.get("provenance") or {}).get("source_country_file"),
                "source_refs": source_refs,
            },
            "qa": {
                "status": status,
                "checks": checks,
                "last_reviewed_at": operations.get("last_verified"),
            },
        }
        dump(release / "objects" / code.lower() / f"{object_id}.json", canonical)
        canonical_objects[object_id] = canonical
        canonical_object_ids_by_country[code].append(object_id)

        search_row = {
            "id": object_id,
            "kind": "attraction",
            "title": canonical["names"]["primary"],
            "narrow": canonical["summary"]["narrow"],
            "class_id": class_id,
            "geo_ids": geo_ids,
            "coordinates": (
                {
                    "lat": primary_location.get("lat"),
                    "lon": primary_location.get("lon"),
                }
                if primary_location and primary_location.get("lat") is not None and primary_location.get("lon") is not None
                else None
            ),
            "tag_ids": canonical["classification"]["tag_ids"],
            "cover_media_id": canonical["media"]["cover_id"],
        }
        canonical_search.append(search_row)
        object_rows_by_country[code].append(search_row)

    # Media entities and indexes.
    for media_id, entity in sorted(media_registry.items()):
        code = entity["country_id"].split("_", 1)[1].upper()
        dump(release / "media" / code.lower() / f"{media_id}.json", entity)
    for code in sorted(published_codes):
        dump(release / "media" / code.lower() / "index.json", {
            "country": code.lower(),
            "media_ids": canonical_media_ids_by_country[code],
        })
        dump(release / "routes" / code.lower() / "index.json", {
            "country": code.lower(),
            "route_ids": [],
            "qa": {
                "status": "migration_queue",
                "note": "Legacy route_meta remains access/logistics metadata until a route has route-level distance, waypoints and source_refs.",
            },
        })
        dump(release / "infrastructure" / "poi" / code.lower() / "index.json", {
            "country": code.lower(),
            "poi_ids": [],
            "qa": {"status": "migration_queue"},
        })
        dump(release / "infrastructure" / "transport" / code.lower() / "index.json", {
            "country": code.lower(),
            "transport_ids": [],
            "qa": {"status": "migration_queue"},
        })

    # Geo entities and index.
    for geo_id, entity in sorted(geo_entities.items()):
        dump(release / "geo" / "entities" / f"{geo_id}.json", entity)
    dump(release / "geo" / "index.json", {
        "crs": "WGS84",
        "epsg": 4326,
        "entities": [
            {
                "id": geo_id,
                "kind": entity.get("kind"),
                "name": (entity.get("names") or {}).get("primary"),
                "parent_id": entity.get("parent_id"),
                "path": f"geo/entities/{geo_id}.json",
            }
            for geo_id, entity in sorted(geo_entities.items())
        ],
    })

    # Country split: stable profile, climate, dynamic travel rules, and refs-only indexes.
    country_manifest_rows = []
    for country_row in legacy_countries:
        code = country_row["country_code"]
        source_path, source = sources_by_code[code]
        meta = source.get("meta") or {}
        overview = source.get("overview") or {}
        travel = source.get("travel") or {}
        checked_at = meta.get("last_updated")
        source_map = country_source_ids_by_code.get(code) or {}
        source_rows = {row.get("id"): row for row in (source.get("sources") or []) if row.get("id")}
        def refs_for(*topics):
            wanted = set(topics)
            out = []
            for short_id, row in source_rows.items():
                if wanted.intersection(set(row.get("used_for") or [])):
                    canonical = source_map.get(short_id)
                    if canonical and canonical not in out:
                        out.append(canonical)
            return out
        def refs_from_ids(ids):
            return [source_map[source_id] for source_id in (ids or []) if source_id in source_map]

        profile = {
            "id": f"geo_{code.lower()}",
            "code": code.lower(),
            "names": {"primary": meta.get("country")},
            "history": overview.get("history"),
            "geography": overview.get("geography"),
            "religions": overview.get("religion"),
            "languages": overview.get("languages"),
            "ethnography": overview.get("ethnography"),
            "economy": overview.get("economy"),
            "political_system": overview.get("political_system"),
            "culture": overview.get("culture"),
            "cuisine": (travel.get("food") or {}).get("budget_food_summary"),
            "street_food": (travel.get("food") or {}).get("street_food"),
            "festivals": travel.get("festivals"),
            "nature": source.get("nature"),
            "natural_risks": (source.get("safety") or {}).get("common_traveler_risks"),
            "summary": overview.get("summary"),
            "narrow": overview.get("narrow"),
            "source_file": source_path.name,
            "source_refs": list(dict.fromkeys(refs_for("country_profile", "economy", "poverty", "demography", "administrative_structure", "ethnography", "languages", "religion", "culture", "heritage", "official_language", "state_religion", "political_system"))),
            "field_source_refs": {
                "history": refs_from_ids(overview.get("history_source_ids")),
                "geography": refs_from_ids((overview.get("geography") or {}).get("source_ids")),
                "religions": refs_from_ids((overview.get("religion") or {}).get("source_ids")),
                "languages": refs_from_ids((overview.get("languages") or {}).get("source_ids")),
                "ethnography": refs_from_ids((overview.get("ethnography") or {}).get("source_ids")),
                "economy": refs_from_ids((overview.get("economy") or {}).get("source_ids")),
                "political_system": refs_from_ids(overview.get("political_system_source_ids")),
                "culture": refs_from_ids((overview.get("culture") or {}).get("source_ids")),
            },
        }
        dump(release / "countries" / code.lower() / "profile.json", profile)
        climate_refs = refs_for("air_temperature", "sea_temperature", "climate")
        dump(release / "countries" / code.lower() / "climate.json", {
            "country_id": f"geo_{code.lower()}",
            "data": source.get("climate"),
            "source_refs": climate_refs,
            "checked_at": checked_at,
            "qa": {"source_refs_complete": bool(climate_refs), "note": "Climate source refs normalized from the research source." if climate_refs else "Climate fact-level source normalization remains queued."},
        })
        visa_refs = refs_from_ids((travel.get("visa_for_russian_passport") or {}).get("source_ids")) or refs_for("visa", "entry")
        border_refs = refs_from_ids((travel.get("land_borders") or {}).get("source_ids")) or refs_for("entry")
        airport_refs = refs_from_ids(travel.get("airports_source_ids")) or refs_for("airport")
        air_link_refs = refs_from_ids(travel.get("international_air_links_source_ids")) or refs_for("air_connectivity")
        transport_refs = refs_from_ids((travel.get("transport_rules") or {}).get("source_ids")) or refs_for("transport_rules", "road_traffic_law")
        camping_refs = refs_from_ids((travel.get("camping_rules") or {}).get("source_ids")) or refs_for("camping_rules", "protected_areas")
        drone_refs = refs_from_ids((travel.get("drone_rules") or {}).get("source_ids"))
        law_refs = refs_from_ids(travel.get("laws_source_ids")) or refs_for("heritage_law", "environmental_rules")
        currency_refs = refs_from_ids((travel.get("currency") or {}).get("source_ids")) or refs_for("currency", "exchange_rate")
        safety_refs = refs_from_ids((source.get("safety") or {}).get("source_ids")) or refs_for("safety")
        dump(release / "countries" / code.lower() / "travel-rules.json", {
            "country_id": f"geo_{code.lower()}",
            "visa": wrap_dynamic(travel.get("visa_for_russian_passport"), checked_at, visa_refs),
            "visa_run": wrap_dynamic(((travel.get("visa_for_russian_passport") or {}).get("visa_run")), checked_at, visa_refs),
            "borders": wrap_dynamic(travel.get("land_borders"), checked_at, border_refs),
            "airports": wrap_dynamic(travel.get("airports"), checked_at, airport_refs),
            "international_air_links": wrap_dynamic(travel.get("international_air_links"), checked_at, air_link_refs),
            "transport_rules": wrap_dynamic(travel.get("transport_rules"), checked_at, transport_refs),
            "camping": wrap_dynamic(travel.get("camping_rules"), checked_at, camping_refs),
            "drones": wrap_dynamic(travel.get("drone_rules"), checked_at, drone_refs, "No sufficiently authoritative country-wide drone rule was normalized in this pass; object/site-specific restrictions remain authoritative." if not drone_refs else None),
            "laws_and_prohibitions": wrap_dynamic(travel.get("laws_and_prohibitions"), checked_at, law_refs),
            "permits": wrap_dynamic(travel.get("tourist_permits"), checked_at, refs_for("permit", "permits")),
            "currency": wrap_dynamic(travel.get("currency"), checked_at, currency_refs),
            "safety_snapshot": wrap_dynamic(source.get("safety"), checked_at, safety_refs),
        })
        indexes = {
            "country_id": f"geo_{code.lower()}",
            "object_ids": canonical_object_ids_by_country[code],
            "geo_ids": canonical_geo_ids_by_country[code],
            "route_ids": [],
            "lodging_ids": sorted(set(canonical_lodging_ids_by_country[code])),
            "poi_ids": [],
            "transport_ids": [],
            "media_ids": canonical_media_ids_by_country[code],
        }
        dump(release / "countries" / code.lower() / "indexes.json", indexes)
        country_manifest_rows.append({
            "id": f"geo_{code.lower()}",
            "code": code.lower(),
            "profile": f"countries/{code.lower()}/profile.json",
            "climate": f"countries/{code.lower()}/climate.json",
            "travel_rules": f"countries/{code.lower()}/travel-rules.json",
            "indexes": f"countries/{code.lower()}/indexes.json",
            "search_index": f"search/{code.lower()}.json",
        })

    # Taxonomy and schema contract.
    class_counts = Counter(row["class_id"] for row in canonical_search)
    class_rows = []
    for legacy_type, class_id in sorted(CLASS_ID_MAP.items(), key=lambda item: item[1]):
        if legacy_type not in type_labels and class_counts[class_id] == 0:
            continue
        class_rows.append({
            "id": class_id,
            "label_ru": type_labels.get(legacy_type) or legacy_type,
            "legacy_type": legacy_type,
            "objects_count": class_counts[class_id],
        })
    dump(release / "taxonomy" / "object-classes.json", {
        "classes": class_rows,
        "rule": "Exactly one class_id per object; tags carry secondary dimensions.",
    })

    tag_counts = Counter()
    for row in canonical_search:
        tag_counts.update(row.get("tag_ids") or [])
    dump(release / "taxonomy" / "tags.json", {
        "tags": [{"id": key, "objects_count": value} for key, value in sorted(tag_counts.items())],
    })
    dump(release / "taxonomy" / "transport-modes.json", {"values": TRANSPORT_MODES})
    dump(release / "taxonomy" / "surface-types.json", {"values": SURFACE_TYPES})
    dump(release / "taxonomy" / "source-types.json", {"values": SOURCE_TYPES})

    dump(release / "schema" / "schema-version.json", {
        "schema_version": latest["schema_version"],
        "dataset_version": latest["release_id"],
        "canonical_contract": "expedition-sea",
        "compatibility_layer": "legacy read-model retained during migration",
    })
    dump(release / "schema" / "enums.json", {
        "geo_kinds": sorted(GEO_KINDS),
        "coordinate_types": sorted(COORDINATE_TYPES),
        "object_elevation_reference_types": [
            "site",
            "summit",
            "highest_point",
            "characteristic",
            "range",
            "water_surface",
            "unknown",
        ],
        "transport_modes": TRANSPORT_MODES,
        "surface_types": SURFACE_TYPES,
        "overnight_status": [
            "official",
            "allowed",
            "permission_required",
            "tolerated_in_practice",
            "prohibited",
            "unclear",
        ],
        "water_quality": [
            "potable",
            "filter_required",
            "treatment_required",
            "technical_only",
            "unknown",
        ],
    })

    # Compact canonical search.
    canonical_search.sort(key=lambda row: (row["title"] or "").casefold())
    dump(release / "search" / "global.json", {
        "schema_version": latest["schema_version"],
        "count": len(canonical_search),
        "objects": canonical_search,
    })
    for code in sorted(published_codes):
        rows = sorted(object_rows_by_country[code], key=lambda row: (row["title"] or "").casefold())
        dump(release / "search" / f"{code.lower()}.json", {
            "country": code.lower(),
            "count": len(rows),
            "objects": rows,
        })

    # Derived views from canonical entities only.
    home = {
        "project_id": "expedition_sea",
        "title": "Expedition Southeast Asia",
        "default_language": DEFAULT_LANGUAGE,
        "countries": [
            {
                "id": row["id"],
                "code": row["code"],
                "profile": row["profile"],
                "search_index": row["search_index"],
            }
            for row in country_manifest_rows
        ],
        "search": "search/global.json",
    }
    dump(release / "views" / "home.json", home)

    for country_row in country_manifest_rows:
        code = country_row["code"]
        upper = code.upper()
        dump(release / "views" / "countries" / f"{code}.json", {
            "country_id": country_row["id"],
            "profile": country_row["profile"],
            "climate": country_row["climate"],
            "travel_rules": country_row["travel_rules"],
            "indexes": country_row["indexes"],
            "objects": object_rows_by_country[upper],
        })

    for row in canonical_search:
        dump(release / "views" / "object-cards" / f"{row['id']}.json", row)

    class_groups = defaultdict(list)
    tag_groups = defaultdict(list)
    region_groups = defaultdict(list)
    for row in canonical_search:
        class_groups[row["class_id"]].append(row)
        for tag_id in row.get("tag_ids") or []:
            tag_groups[tag_id].append(row)
        for geo_id in row.get("geo_ids") or []:
            region_groups[geo_id].append(row)

    for class_id, rows in class_groups.items():
        dump(release / "views" / "classes" / f"{class_id}.json", {
            "class_id": class_id,
            "count": len(rows),
            "object_ids": [row["id"] for row in rows],
        })
    for tag_id, rows in tag_groups.items():
        dump(release / "views" / "tags" / f"{tag_id}.json", {
            "tag_id": tag_id,
            "count": len(rows),
            "object_ids": [row["id"] for row in rows],
        })
    for geo_id, rows in region_groups.items():
        dump(release / "views" / "regions" / f"{geo_id}.json", {
            "geo_id": geo_id,
            "count": len(rows),
            "object_ids": [row["id"] for row in rows],
        })

    # Canonical QA queue.
    global_missing = Counter()
    country_qa_rows = []
    for code in sorted(published_codes):
        objects = [canonical_objects[oid] for oid in canonical_object_ids_by_country[code]]
        missing = defaultdict(list)
        passed = 0
        for obj in objects:
            checks = (obj.get("qa") or {}).get("checks") or {}
            for key, ok in checks.items():
                if not ok:
                    missing[key].append(obj["id"])
                    global_missing[key] += 1
            if (obj.get("qa") or {}).get("status") == "passed":
                passed += 1
            dump(release / "qa" / "objects" / code.lower() / f"{obj['id']}.json", {
                "object_id": obj["id"],
                **obj["qa"],
            })

        country_payload = {
            "country": code.lower(),
            "objects_total": len(objects),
            "objects_passed": passed,
            "objects_incomplete": len(objects) - passed,
            "missing": dict(sorted(missing.items())),
        }
        dump(release / "qa" / "countries" / f"{code.lower()}.json", country_payload)
        country_qa_rows.append(country_payload)

        by_class = defaultdict(list)
        for obj in objects:
            by_class[obj["classification"]["class_id"]].append(obj)
        for class_id, rows in by_class.items():
            class_missing = defaultdict(list)
            for obj in rows:
                for key, ok in ((obj.get("qa") or {}).get("checks") or {}).items():
                    if not ok:
                        class_missing[key].append(obj["id"])
            dump(release / "qa" / "classes" / code.lower() / f"{class_id}.json", {
                "country": code.lower(),
                "class_id": class_id,
                "objects_total": len(rows),
                "objects_passed": sum(1 for obj in rows if (obj.get("qa") or {}).get("status") == "passed"),
                "missing": dict(sorted(class_missing.items())),
            })

    dump(release / "qa" / "global.json", {
        "schema_version": latest["schema_version"],
        "objects_total": len(canonical_objects),
        "objects_passed": sum(1 for obj in canonical_objects.values() if (obj.get("qa") or {}).get("status") == "passed"),
        "objects_incomplete": sum(1 for obj in canonical_objects.values() if (obj.get("qa") or {}).get("status") != "passed"),
        "missing_counts": dict(sorted(global_missing.items())),
        "countries": country_qa_rows,
        "next_work_rule": "country -> class -> object -> research -> normalization -> GPS/elevation -> sources -> object QA -> class QA -> country QA",
    })

    manifest_path = release / "manifest.json"
    manifest = load(manifest_path)
    manifest["project_id"] = "expedition_sea"
    manifest["title"] = "Expedition Southeast Asia"
    manifest["dataset_version"] = latest["release_id"]
    manifest["generated_at"] = GENERATED_AT
    manifest["default_language"] = DEFAULT_LANGUAGE
    manifest["countries"] = country_manifest_rows
    manifest["taxonomy"] = {
        "classes": "taxonomy/object-classes.json",
        "tags": "taxonomy/tags.json",
        "transport_modes": "taxonomy/transport-modes.json",
        "surface_types": "taxonomy/surface-types.json",
        "source_types": "taxonomy/source-types.json",
    }
    manifest["search"] = "search/global.json"
    manifest["home"] = "views/home.json"
    manifest["canonical_layer"] = {
        "status": "migration_active",
        "canonical_roots": [
            "geo",
            "countries",
            "objects",
            "infrastructure",
            "routes",
            "media",
            "sources",
            "taxonomy",
        ],
        "derived_roots": ["search", "views", "qa"],
        "legacy_compatibility_read_model": True,
    }
    manifest.setdefault("totals", {}).update({
        "canonical_objects": len(canonical_objects),
        "canonical_geo_entities": len(geo_entities),
        "canonical_lodging": len(canonical_lodging_ids),
        "canonical_sources": len(canonical_source_ids),
        "canonical_media": len(media_registry),
    })
    manifest["files"] = [
        file_entry(path, release)
        for path in sorted(release.rglob("*.json"))
        if path.name != "manifest.json"
    ]
    manifest["totals"]["files"] = len(manifest["files"])
    dump(manifest_path, manifest)

    print(json.dumps({
        "status": "ok",
        "release_id": latest["release_id"],
        "schema_version": latest["schema_version"],
        "canonical_objects": len(canonical_objects),
        "canonical_geo_entities": len(geo_entities),
        "canonical_lodging": len(canonical_lodging_ids),
        "canonical_sources": len(canonical_source_ids),
        "canonical_media": len(media_registry),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
