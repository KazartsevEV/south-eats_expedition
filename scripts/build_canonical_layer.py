#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from release_context import get_release_context

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
PUBLIC = ROOT / "public" / "cdn" / "v2"
ID_REGISTRY_PATH = ROOT / "data" / "id-registry.json"
HIERARCHY = ROOT / "data" / "hierarchy" / "countries"
GEO_COUNTRIES = ROOT / "data" / "geo" / "countries"
GEO_NODES = ROOT / "data" / "geo" / "nodes"
FORMAL_CANONICAL_GEO_CODES = {"BN", "KH", "LA", "ID", "MY", "MM", "PH", "SG", "TH", "TL", "VN"}
COUNTRY_SOURCE_CANONICAL_CODES = {"BN", "KH", "LA", "ID", "MY", "MM", "PH", "SG", "TH", "TL", "VN"}

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


def collect_source_refs(value):
    refs = []

    def walk(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if key == "source_refs" and isinstance(child, list):
                    refs.extend(item for item in child if isinstance(item, str) and item)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return list(dict.fromkeys(refs))


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
    drone = visual.get("drone")
    if isinstance(drone, dict):
        drone["source_refs"] = remap_source_refs(drone.get("source_refs"), registry)
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
    structured = logistics.get("access_options")
    if isinstance(structured, list) and structured:
        return json.loads(json.dumps(structured, ensure_ascii=False))
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
    latest = get_release_context(PUBLIC)
    release = latest["release"]
    if not release.exists():
        raise RuntimeError(f"release does not exist: {release}")

    registry = load(ID_REGISTRY_PATH)
    countries_doc = load(release / "countries.json")
    legacy_countries = countries_doc.get("countries") or []
    published_codes = {row["country_code"] for row in legacy_countries}
    sources_by_code = source_files_by_code(published_codes)
    country_slug_by_code = {row["country_code"]: row["slug"] for row in legacy_countries if row.get("country_code") and row.get("slug")}
    source_object_by_country_name = {}
    region_profile_by_country_name = {}
    locality_profile_by_country_name = {}
    for code, (_, source_doc) in sources_by_code.items():
        travel = source_doc.get("travel") or {}
        for row in travel.get("objects") or []:
            if row.get("name"):
                source_object_by_country_name[(code, row.get("name"))] = row
        for row in travel.get("regions") or []:
            if row.get("name"):
                region_profile_by_country_name[(code, row.get("name"))] = row
        for row in travel.get("localities") or []:
            if row.get("name"):
                locality_profile_by_country_name[(code, row.get("name"))] = row
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
        geometry_path = None
        geometry_source = GEO_COUNTRIES / f"{code.lower()}.geojson"
        if geometry_source.exists():
            geometry_path = f"geo/geometries/{country_id}.geojson"
            dump(release / geometry_path, load(geometry_source))
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
            "geometry_path": geometry_path,
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
        source_locality = locality_profile_by_country_name.get((code, place.get("name")))
        kind = "geographic_area"
        if place.get("kind") == "region":
            kind = "geographic_area"
        elif place.get("kind") == "city_or_route_hub":
            requested_kind = (source_locality or {}).get("kind")
            kind = requested_kind if requested_kind in GEO_KINDS else "geographic_area"
        if kind not in GEO_KINDS:
            kind = "geographic_area"
        entity = {
            "id": geo_id,
            "kind": kind,
            "names": {"primary": place.get("name"), "ru": ((locality_profile_by_country_name.get((code, place.get("name"))) or {}).get("name_ru") or (region_profile_by_country_name.get((code, place.get("name"))) or {}).get("name_ru"))},
            "slug": place.get("slug"),
            "parent_id": country_id,
            "geo_path": [country_id, geo_id],
            "description": {
                "narrow": place.get("narrow"),
                "body": None,
            },
            "cover_media_id": None,
            "primary_location": (locality_profile_by_country_name.get((code, place.get("name"))) or {}).get("primary_location"),
            "legacy_ids": [legacy_id],
            "migration": {
                "source_kind": place.get("kind"),
                "note": "Служебные маршрутные регионы и узлы временно сохраняются как geographic_area, пока не подтверждена их точная административная или поселенческая принадлежность.",
            },
        }
        region_profile = region_profile_by_country_name.get((code, place.get("name")))
        if region_profile:
            entity["languages"] = {
                "spoken": region_profile.get("languages_spoken") or [],
                "notes": region_profile.get("language_notes"),
            }
            climate_detail = dict(region_profile.get("climate_detail") or region_profile.get("climate") or {})
            if region_profile.get("climate_summary") and not climate_detail.get("summary"):
                climate_detail["summary"] = region_profile.get("climate_summary")
            if region_profile.get("best_period_general") and not climate_detail.get("best_period_general"):
                climate_detail["best_period_general"] = region_profile.get("best_period_general")
            entity["climate"] = climate_detail
            for field in ("geography", "relief", "geology", "hydrology", "coast", "marine", "nature", "health", "safety", "history", "ethnography", "culture", "myths_beliefs", "architecture", "transport"):
                if region_profile.get(field) not in (None, "", [], {}):
                    entity[field] = region_profile.get(field)
            entity["freshness"] = {"checked_at": ((region_profile.get("local_reference_provenance") or {}).get("checked_at")) or region_profile.get("last_verified")}
            local_prov = region_profile.get("local_reference_provenance") or {}
            region_source_refs = list(dict.fromkeys((local_prov.get("source_refs") or []) + (region_profile.get("source_refs") or [])))
            entity["provenance"] = {
                "source_urls": region_profile.get("language_source_urls") or [],
                "source_refs": region_source_refs,
                "qa": {
                    "source_refs_complete": bool(region_source_refs),
                    "note": "У региональной справки есть канонические ссылки на источники." if region_source_refs else "Существующая региональная справка перенесена из исходных данных страны; привязка источников к отдельным фактам ещё требует нормализации.",
                },
            }
            entity["migration"]["local_reference_status"] = "migrated_existing_region_profile"
        locality_profile = locality_profile_by_country_name.get((code, place.get("name")))
        if locality_profile:
            entity["relations"] = {
                "source_region_names": locality_profile.get("regions") or [],
                "source_object_names": locality_profile.get("object_names") or [],
            }
            local_profile = locality_profile.get("profile") or {}
            if local_profile:
                if local_profile.get("summary"):
                    entity["description"]["narrow"] = local_profile.get("summary")
                for field in ("history", "culture", "geography", "geology", "ethnography", "myths_beliefs", "climate", "transport", "languages", "nature", "marine", "health", "safety", "architecture", "relief", "hydrology", "coast"):
                    if local_profile.get(field) not in (None, "", [], {}):
                        entity[field] = local_profile.get(field)
                entity["provenance"] = local_profile.get("provenance") or entity.get("provenance")
                if (local_profile.get("provenance") or {}).get("checked_at"):
                    entity["freshness"] = {"checked_at": (local_profile.get("provenance") or {}).get("checked_at")}
                entity["migration"]["local_reference_status"] = "migrated_existing_locality_profile"
            else:
                entity["migration"]["local_reference_status"] = "locality_linkage_migrated"
        local_profile_payload = (locality_profile or {}).get("profile") or {}
        if locality_profile and (local_profile_payload or locality_profile.get("primary_location")):
            entity["coverage_role"] = "locality_profile"
        elif region_profile:
            entity["coverage_role"] = "regional_profile"
        else:
            entity["coverage_role"] = "structural"
        if entity["coverage_role"] == "locality_profile" and not entity.get("primary_location"):
            entity["primary_location_status"] = {
                "status": "unresolved",
                "reason": "No reliable locality coordinate is stored in the canonical research layer; parent or object coordinates must not be substituted.",
            }
        entity.setdefault("provenance", {})
        entity["provenance"]["source_refs"] = list(dict.fromkeys(
            (entity["provenance"].get("source_refs") or []) + collect_source_refs(entity)
        ))
        geo_entities[geo_id] = entity
        canonical_geo_ids_by_country[code].append(geo_id)
        place_id_by_country_name_kind[(code, place.get("name"), place.get("kind"))] = geo_id

    # Add source-only real localities without deleting legacy composite route hubs.
    for code, (_, source_doc) in sources_by_code.items():
        if code in formal_hierarchy:
            continue
        country_id = f"geo_{code.lower()}"
        for locality in ((source_doc.get("travel") or {}).get("localities") or []):
            if not locality.get("canonical_id"):
                continue
            name = locality.get("name")
            existing_id = place_id_by_country_name_kind.get((code, name, "city_or_route_hub"))
            if existing_id:
                continue
            legacy_id = locality.get("legacy_id")
            if not legacy_id:
                raise RuntimeError(f"{code}: source-only locality missing legacy_id: {name}")
            geo_id = require_id(registry, "geo", legacy_id)
            if geo_id != locality.get("canonical_id"):
                raise RuntimeError(f"{code}: locality canonical_id mismatch for {name}: {geo_id} != {locality.get('canonical_id')}")
            region_names = locality.get("regions") or []
            parent_id = country_id
            if region_names:
                parent_id = place_id_by_country_name_kind.get((code, region_names[0], "region")) or country_id
            kind = locality.get("kind") or "settlement"
            if kind not in GEO_KINDS:
                kind = "settlement"
            profile = locality.get("profile") or {}
            entity = {
                "id": geo_id,
                "kind": kind,
                "names": {"primary": name, "ru": locality.get("name_ru")},
                "slug": locality.get("slug"),
                "parent_id": parent_id,
                "geo_path": [country_id, parent_id, geo_id] if parent_id != country_id else [country_id, geo_id],
                "description": {"narrow": profile.get("summary"), "body": None},
                "cover_media_id": None,
                "primary_location": locality.get("primary_location"),
                "legacy_ids": [legacy_id],
                "relations": {
                    "source_region_names": region_names,
                    "source_object_names": locality.get("object_names") or [],
                },
                "migration": {
                    "source_kind": "source_locality",
                    "status": "canonical_locality",
                    "note": "Real locality created from researched source data; legacy composite route hubs are retained separately for compatibility.",
                },
            }
            for field in ("history", "culture", "geography", "geology", "ethnography", "myths_beliefs", "climate", "transport", "languages", "nature", "marine", "health", "safety", "architecture", "relief", "hydrology", "coast"):
                if profile.get(field) not in (None, "", [], {}):
                    entity[field] = profile.get(field)
            if profile.get("provenance"):
                entity["provenance"] = profile.get("provenance")
                entity["freshness"] = {"checked_at": (profile.get("provenance") or {}).get("checked_at")}
            entity["coverage_role"] = "locality_profile" if (profile or locality.get("primary_location")) else "structural"
            if entity["coverage_role"] == "locality_profile" and not entity.get("primary_location"):
                entity["primary_location_status"] = {
                    "status": "unresolved",
                    "reason": "No reliable locality coordinate is stored in the canonical research layer; parent or object coordinates must not be substituted.",
                }
            entity.setdefault("provenance", {})
            entity["provenance"]["source_refs"] = list(dict.fromkeys(
                (entity["provenance"].get("structural_source_refs") or [])
                + (entity["provenance"].get("research_source_refs") or [])
                + (entity["provenance"].get("source_refs") or [])
            ))
            geo_entities[geo_id] = entity
            canonical_geo_ids_by_country[code].append(geo_id)
            place_id_by_country_name_kind[(code, name, "city_or_route_hub")] = geo_id

    # Rebuild the legacy region -> locality tree from explicit source relations.
    for code, (_, source_doc) in sources_by_code.items():
        country_id = f"geo_{code.lower()}"
        for locality in ((source_doc.get("travel") or {}).get("localities") or []):
            locality_id = place_id_by_country_name_kind.get((code, locality.get("name"), "city_or_route_hub"))
            if not locality_id or locality_id not in geo_entities:
                continue
            region_names = locality.get("regions") or []
            if not region_names:
                continue
            parent_id = place_id_by_country_name_kind.get((code, region_names[0], "region"))
            if not parent_id or parent_id not in geo_entities:
                continue
            geo_entities[locality_id]["parent_id"] = parent_id
            geo_entities[locality_id]["geo_path"] = [country_id, parent_id, locality_id]
            geo_entities[locality_id]["migration"]["parent_status"] = "migrated_from_source_locality_relation"
            replacements = locality.get("replaced_by") or []
            if replacements:
                geo_entities[locality_id]["migration"]["status"] = "legacy_route_hub"
                geo_entities[locality_id]["migration"]["replaced_by"] = replacements

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
            entity = {
                "id": geo_id,
                "kind": kind,
                "names": {"primary": node.get("name_ru") or node.get("name_local") or node_id, "local": node.get("name_local")},
                "slug": node.get("slug"),
                "parent_id": parent_id,
                "geo_path": formal_geo_path(node_id),
                "description": {"narrow": node.get("notes_ru"), "body": None},
                "cover_media_id": None,
                "primary_location": node.get("primary_location"),
                "legacy_ids": [node_id],
                "migration": {"source_kind": "formal_hierarchy", "axis": node.get("axis"), "status": "formalized"},
                "coverage_role": "structural",
                "provenance": {
                    "checked_at": (doc.get("meta") or {}).get("checked_at"),
                    "sources": doc.get("sources") or [],
                    "structural_source_refs": [((doc.get("meta") or {}).get("canonical_source_id"))]
                    if (doc.get("meta") or {}).get("canonical_source_id") else [],
                    "research_source_refs": [],
                    "source_refs": [((doc.get("meta") or {}).get("canonical_source_id"))]
                    if (doc.get("meta") or {}).get("canonical_source_id") else [],
                },
            }

            geometry_source = GEO_NODES / f"{geo_id}.geojson"
            if geometry_source.exists():
                geometry_path = f"geo/geometries/{geo_id}.geojson"
                dump(release / geometry_path, load(geometry_source))
                entity["geometry_path"] = geometry_path
            if node.get("geometry") not in (None, "", [], {}):
                entity["geometry"] = node.get("geometry")

            hierarchy_profile = node.get("profile") or {}
            if hierarchy_profile:
                if hierarchy_profile.get("narrow"):
                    entity["description"]["narrow"] = hierarchy_profile.get("narrow")
                for field in ("geography", "relief", "geology", "hydrology", "coast", "marine", "nature", "health", "safety", "history", "ethnography", "culture", "myths_beliefs", "architecture", "transport", "climate", "languages"):
                    if hierarchy_profile.get(field) not in (None, "", [], {}):
                        entity[field] = hierarchy_profile.get(field)
                hierarchy_profile_refs = list(dict.fromkeys(
                    (hierarchy_profile.get("source_refs") or []) + collect_source_refs(hierarchy_profile)
                ))
                structural_refs = entity["provenance"].get("structural_source_refs") or []
                entity["provenance"]["research_source_refs"] = hierarchy_profile_refs
                entity["provenance"]["source_refs"] = list(dict.fromkeys(structural_refs + hierarchy_profile_refs))
                if hierarchy_profile.get("checked_at"):
                    entity["provenance"]["research_checked_at"] = hierarchy_profile.get("checked_at")
                    entity["freshness"] = {"checked_at": hierarchy_profile.get("checked_at")}
                entity["migration"]["hierarchy_profile_status"] = (
                    "researched_profile" if hierarchy_profile_refs else "profile_requires_source_normalization"
                )
                if hierarchy_profile_refs:
                    entity["coverage_role"] = "regional_profile"

            # A formal hierarchy must not discard already researched regional/locality content.
            # Hierarchy nodes carry stable identity/parentage; descriptive facts remain sourced
            # from the existing country research layer and are merged into the canonical geo entity.
            region_names = list(node.get("legacy_region_names") or [])
            locality_names = list(node.get("legacy_locality_names") or [])
            region_profile = next(
                (region_profile_by_country_name.get((code, name)) for name in region_names
                 if region_profile_by_country_name.get((code, name))),
                None,
            )
            locality_profile = next(
                (locality_profile_by_country_name.get((code, name)) for name in locality_names
                 if locality_profile_by_country_name.get((code, name))),
                None,
            )

            if region_profile:
                if region_profile.get("narrow"):
                    entity["description"]["narrow"] = region_profile.get("narrow")
                entity["languages"] = {
                    "spoken": region_profile.get("languages_spoken") or [],
                    "notes": region_profile.get("language_notes"),
                }
                climate_detail = dict(region_profile.get("climate_detail") or region_profile.get("climate") or {})
                if region_profile.get("climate_summary") and not climate_detail.get("summary"):
                    climate_detail["summary"] = region_profile.get("climate_summary")
                if region_profile.get("best_period_general") and not climate_detail.get("best_period_general"):
                    climate_detail["best_period_general"] = region_profile.get("best_period_general")
                if climate_detail:
                    entity["climate"] = climate_detail
                for field in ("geography", "relief", "geology", "hydrology", "coast", "marine", "nature", "health", "safety", "history", "ethnography", "culture", "myths_beliefs", "architecture", "transport"):
                    if region_profile.get(field) not in (None, "", [], {}):
                        entity[field] = region_profile.get(field)
                local_prov = region_profile.get("local_reference_provenance") or {}
                region_source_refs = list(dict.fromkeys(
                    (local_prov.get("source_refs") or [])
                    + (region_profile.get("source_refs") or [])
                    + collect_source_refs(region_profile)
                ))
                structural_refs = entity["provenance"].get("structural_source_refs") or []
                entity["provenance"].update({
                    "source_urls": region_profile.get("language_source_urls") or [],
                    "research_source_refs": region_source_refs,
                    "source_refs": list(dict.fromkeys(structural_refs + region_source_refs)),
                    "research_checked_at": local_prov.get("checked_at") or region_profile.get("last_verified"),
                })
                entity["freshness"] = {"checked_at": local_prov.get("checked_at") or region_profile.get("last_verified")}
                entity["migration"]["regional_content_status"] = (
                    "migrated_existing_region_profile"
                    if region_source_refs else "migrated_region_profile_requires_source_normalization"
                )
                entity["coverage_role"] = "regional_profile" if region_source_refs else "structural"

            if locality_profile:
                entity["primary_location"] = locality_profile.get("primary_location")
                entity["relations"] = {
                    "source_region_names": locality_profile.get("regions") or [],
                    "source_object_names": locality_profile.get("object_names") or [],
                }
                profile = locality_profile.get("profile") or {}
                if profile.get("summary"):
                    entity["description"]["narrow"] = profile.get("summary")
                for field in ("history", "culture", "geography", "geology", "ethnography", "myths_beliefs", "climate", "transport", "languages", "nature", "marine", "health", "safety", "architecture", "relief", "hydrology", "coast"):
                    if profile.get(field) not in (None, "", [], {}):
                        entity[field] = profile.get(field)
                profile_prov = profile.get("provenance") or {}
                locality_source_refs = list(dict.fromkeys(
                    (profile_prov.get("source_refs") or []) + collect_source_refs(profile)
                ))
                if profile_prov:
                    entity["provenance"]["locality_profile"] = profile_prov
                    if profile_prov.get("checked_at"):
                        entity["freshness"] = {"checked_at": profile_prov.get("checked_at")}
                existing_research_refs = entity["provenance"].get("research_source_refs") or []
                entity["provenance"]["research_source_refs"] = list(dict.fromkeys(
                    existing_research_refs + locality_source_refs
                ))
                entity["provenance"]["source_refs"] = list(dict.fromkeys(
                    (entity["provenance"].get("structural_source_refs") or [])
                    + entity["provenance"]["research_source_refs"]
                ))
                entity["migration"]["local_reference_status"] = (
                    "migrated_existing_locality_profile"
                    if locality_source_refs else "migrated_locality_profile_requires_source_normalization"
                )
                if (profile or locality_profile.get("primary_location")) and locality_source_refs:
                    entity["coverage_role"] = "locality_profile"
                elif profile or locality_profile.get("primary_location"):
                    entity["coverage_role"] = "structural"

            if entity.get("coverage_role") == "locality_profile" and not entity.get("primary_location"):
                entity["primary_location_status"] = node.get("primary_location_status") or {
                    "status": "unresolved",
                    "reason": "No reliable locality coordinate is stored in the canonical research layer; parent or object coordinates must not be substituted.",
                }
            entity.setdefault("provenance", {})
            entity["provenance"]["source_refs"] = list(dict.fromkeys(
                (entity["provenance"].get("source_refs") or []) + collect_source_refs(entity)
            ))
            geo_entities[geo_id] = entity
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
        "park_authority": "park_authority",
        "museum": "museum",
        "archaeological_service": "archaeological_service",
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
            source_path = release / "sources" / f"{source_id}.json"
            if source_id in canonical_source_ids:
                existing = load(source_path)
                if existing.get("url") != row.get("url"):
                    raise RuntimeError(f"{code}: duplicate canonical source ID with different URL: {source_id}")
                existing["used_for"] = list(dict.fromkeys((existing.get("used_for") or []) + (row.get("used_for") or [])))
                existing["legacy_ids"] = list(dict.fromkeys((existing.get("legacy_ids") or []) + [f"country:{code.lower()}:{short_id}"]))
                for key, value in {
                    "title": row.get("title"),
                    "publisher": row.get("publisher"),
                    "language": row.get("language"),
                    "published_at": row.get("published_at"),
                    "accessed_at": row.get("accessed"),
                    "notes": row.get("notes"),
                }.items():
                    if existing.get(key) in (None, "", []) and value not in (None, "", []):
                        existing[key] = value
                dump(source_path, existing)
            else:
                dump(source_path, {
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

    for code, doc in sorted(formal_hierarchy.items()):
        meta = doc.get("meta") or {}
        source_id = meta.get("canonical_source_id")
        if not source_id:
            raise RuntimeError(f"{code}: formal hierarchy missing meta.canonical_source_id")
        if source_id in canonical_source_ids:
            raise RuntimeError(f"{code}: duplicate formal hierarchy canonical source ID {source_id}")
        dump(release / "sources" / f"{source_id}.json", {
            "id": source_id,
            "type": "project_material",
            "title": f"Formal geography hierarchy — {meta.get('country_slug') or code.lower()}",
            "publisher": "Expedition South East",
            "url": None,
            "language": "ru",
            "published_at": None,
            "accessed_at": meta.get("checked_at"),
            "authority": "high",
            "used_for": [
                "canonical geo identity",
                "parentage and geo_path",
                "formal administrative and physical-geography node normalization",
            ],
            "notes": "Project research source compiled from the official and specialist references embedded in the country hierarchy document.",
            "references": doc.get("sources") or [],
            "referenced_by": [],
            "legacy_ids": [f"hierarchy:{code.lower()}"],
        })
        canonical_source_ids.add(source_id)

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
        rebuild_review = ((source_object or {}).get("qa") or {}).get("rebuild_v2") or {}

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
            "gallery_min_5": len(set(media_ids)) >= 5,
            "editorial_rebuild": code != "KH" or rebuild_review.get("status") == "passed",
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
                "water": (
                    {
                        **json.loads(json.dumps(logistics.get("water_structured"), ensure_ascii=False)),
                        "source_refs": list(dict.fromkeys((logistics.get("water_structured") or {}).get("source_refs", []) + source_refs)),
                    }
                    if isinstance(logistics.get("water_structured"), dict)
                    else {
                        "summary": logistics.get("water"),
                        "quality": "unknown",
                        "last_reliable_source": None,
                        "distance_m": None,
                        "natural_sources": [],
                        "source_refs": source_refs,
                    }
                ),
                "supplies": json.loads(json.dumps(logistics.get("supplies"), ensure_ascii=False)) if isinstance(logistics.get("supplies"), dict) else None,
                "overnight": (
                    {
                        **json.loads(json.dumps(logistics.get("overnight"), ensure_ascii=False)),
                        "source_refs": list(dict.fromkeys((logistics.get("overnight") or {}).get("source_refs", []) + source_refs)),
                    }
                    if isinstance(logistics.get("overnight"), dict)
                    else {
                        "status": "unclear",
                        "summary": logistics.get("overnight_and_camping"),
                        "source_refs": source_refs,
                    }
                ),
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

    # Country food/festival images are canonical media too. Source rows keep
    # the research metadata; generated country profiles reference media IDs.
    for code in sorted(published_codes):
        country_source = sources_by_code[code][1]
        travel = country_source.get("travel") or {}
        feature_rows = list(((travel.get("food") or {}).get("items") or [])) + list(travel.get("festivals") or [])
        for feature in feature_rows:
            if not isinstance(feature, dict):
                continue
            image = feature.get("image")
            if not isinstance(image, dict):
                continue
            media_id = media_id_for(code, image)
            existing = media_registry.get(media_id)
            if existing is None:
                media_registry[media_id] = {
                    "id": media_id,
                    "kind": "image",
                    "country_id": f"geo_{code.lower()}",
                    "url": image.get("url") or image.get("static_url"),
                    "source_page": image.get("source_page"),
                    "provider": image.get("provider"),
                    "license": image.get("license"),
                    "artist": image.get("artist"),
                    "checked_at": image.get("last_checked") or image.get("checked_at"),
                    "source_refs": [],
                    "referenced_by": [f"geo_{code.lower()}"],
                }
            elif f"geo_{code.lower()}" not in (existing.get("referenced_by") or []):
                existing.setdefault("referenced_by", []).append(f"geo_{code.lower()}")
            if media_id not in canonical_media_ids_by_country[code]:
                canonical_media_ids_by_country[code].append(media_id)

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
                "name": ((entity.get("names") or {}).get("ru") or (entity.get("names") or {}).get("primary")),
                "parent_id": entity.get("parent_id"),
                "status": ((entity.get("migration") or {}).get("status") or "active"),
                "coordinates": (
                    {
                        "lat": (entity.get("primary_location") or {}).get("lat"),
                        "lon": (entity.get("primary_location") or {}).get("lon"),
                    }
                    if (entity.get("primary_location") or {}).get("lat") is not None and (entity.get("primary_location") or {}).get("lon") is not None
                    else None
                ),
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

        food = travel.get("food") or {}

        def country_feature_row(row):
            if not isinstance(row, dict):
                return row
            out = {key: value for key, value in row.items() if key not in {"image", "source_ids"}}
            image = row.get("image")
            if isinstance(image, dict):
                out["media_id"] = media_id_for(code, image)
            out["source_refs"] = refs_from_ids(row.get("source_ids"))
            return out

        rich_food_items = food.get("items") or []
        street_food_profile = (
            [country_feature_row(row) for row in rich_food_items]
            if rich_food_items
            else food.get("street_food")
        )
        festival_profile = [country_feature_row(row) for row in (travel.get("festivals") or [])]

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
            "cuisine": food.get("budget_food_summary"),
            "street_food": street_food_profile,
            "food_market": {
                "typical_simple_meal_usd_range": food.get("typical_simple_meal_usd_range"),
                "typical_simple_meal_local_range": food.get("typical_simple_meal_local_range"),
                "price_currency": food.get("price_currency"),
                "price_note": food.get("price_note"),
                "checked_at": food.get("checked_at") or checked_at,
                "source_refs": refs_from_ids(food.get("source_ids")),
            },
            "festivals": festival_profile,
            "nature": (
                {
                    **((source.get("nature") or {}).get("country_macro") or {}),
                    "flora": (source.get("nature") or {}).get("flora"),
                    "fauna": (source.get("nature") or {}).get("fauna"),
                    "dangerous_animals": (source.get("nature") or {}).get("dangerous_animals"),
                    "poisonous_plants": (source.get("nature") or {}).get("poisonous_plants"),
                }
                if code == "MY"
                else source.get("nature")
            ),
            "natural_risks": ((source.get("safety") or {}).get("country_macro") if code == "MY" else (source.get("safety") or {}).get("common_traveler_risks")),
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
        criminal_refs = refs_from_ids(travel.get("criminal_law_source_ids")) or refs_for("criminal_law", "drug_law", "national_symbols")
        currency_refs = refs_from_ids((travel.get("currency") or {}).get("source_ids")) or refs_for("currency", "exchange_rate")
        safety_refs = refs_from_ids((source.get("safety") or {}).get("source_ids")) or refs_for("safety")
        permit_refs = refs_from_ids((travel.get("tourist_permits") or {}).get("source_ids")) or refs_for("permit", "permits")
        dump(release / "countries" / code.lower() / "travel-rules.json", {
            "country_id": f"geo_{code.lower()}",
            "visa": wrap_dynamic(travel.get("visa_for_russian_passport"), checked_at, visa_refs),
            "borders": wrap_dynamic(travel.get("land_borders"), checked_at, border_refs),
            "airports": wrap_dynamic(travel.get("airports"), checked_at, airport_refs),
            "international_air_links": wrap_dynamic(travel.get("international_air_links"), checked_at, air_link_refs),
            "transport_rules": wrap_dynamic(travel.get("transport_rules"), checked_at, transport_refs),
            "camping": wrap_dynamic(travel.get("camping_rules"), checked_at, camping_refs),
            "drones": wrap_dynamic(travel.get("drone_rules"), checked_at, drone_refs, "No sufficiently authoritative country-wide drone rule was normalized in this pass; object/site-specific restrictions remain authoritative." if not drone_refs else None),
            "laws_and_prohibitions": wrap_dynamic(travel.get("laws_and_prohibitions"), checked_at, law_refs),
            "criminal_liability": wrap_dynamic(travel.get("criminal_liability"), checked_at, criminal_refs, "Traveller-facing criminal-law summary; not an exhaustive legal code." if travel.get("criminal_liability") else "Country criminal-law layer not yet normalized."),
            "permits": wrap_dynamic(travel.get("tourist_permits"), checked_at, permit_refs),
            "currency": wrap_dynamic(travel.get("currency"), checked_at, currency_refs),
            "safety_snapshot": wrap_dynamic(((source.get("safety") or {}).get("country_macro") if code == "MY" else source.get("safety")), checked_at, safety_refs),
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

        # Country-layer QA is separate from object-card QA. A country must not look
        # "passed" merely because its attraction cards happen to pass.
        profile_doc = load(release / "countries" / code.lower() / "profile.json")
        climate_doc = load(release / "countries" / code.lower() / "climate.json")
        rules_doc = load(release / "countries" / code.lower() / "travel-rules.json")
        required_profile_fields = [
            "history", "geography", "religions", "languages", "ethnography",
            "economy", "culture", "cuisine", "street_food", "natural_risks",
        ]
        profile_missing = [
            key for key in required_profile_fields
            if profile_doc.get(key) in (None, "", [], {})
        ]
        nature_payload = profile_doc.get("nature") or {}
        nature_missing = [
            key for key in ("dangerous_animals", "poisonous_plants")
            if nature_payload.get(key) in (None, "", [], {})
        ]
        stable_source_fields = [
            "history", "geography", "religions", "languages", "ethnography",
            "economy", "political_system", "culture",
        ]
        field_source_refs = profile_doc.get("field_source_refs") or {}
        profile_source_gaps = [
            key for key in stable_source_fields
            if profile_doc.get(key) not in (None, "", [], {})
            and not (field_source_refs.get(key) or [])
        ]
        dynamic_missing_value = []
        dynamic_missing_sources = []
        dynamic_missing_checked_at = []
        for key, wrapper in rules_doc.items():
            if key == "country_id":
                continue
            if not isinstance(wrapper, dict) or "value" not in wrapper:
                dynamic_missing_value.append(key)
                continue
            if wrapper.get("value") in (None, "", [], {}):
                dynamic_missing_value.append(key)
            elif not (wrapper.get("source_refs") or []):
                dynamic_missing_sources.append(key)
            if not wrapper.get("checked_at"):
                dynamic_missing_checked_at.append(key)

        country_checks = {
            "profile_required_fields": not profile_missing,
            "profile_nature_risks": not nature_missing,
            "profile_fact_sources": not profile_source_gaps,
            "climate_data": climate_doc.get("data") not in (None, "", [], {}),
            "climate_sources": bool(climate_doc.get("source_refs")),
            "climate_checked_at": bool(climate_doc.get("checked_at")),
            "travel_rules_values": not dynamic_missing_value,
            "travel_rules_sources": not dynamic_missing_sources,
            "travel_rules_checked_at": not dynamic_missing_checked_at,
            "formal_geography": True,
        }
        country_layer_missing = {
            "profile_fields": profile_missing,
            "nature_fields": nature_missing,
            "profile_fact_sources": profile_source_gaps,
            "travel_rules_values": dynamic_missing_value,
            "travel_rules_sources": dynamic_missing_sources,
            "travel_rules_checked_at": dynamic_missing_checked_at,
        }
        country_layer_missing = {k: v for k, v in country_layer_missing.items() if v}

        country_payload = {
            "country": code.lower(),
            "country_layer": {
                "status": "passed" if all(country_checks.values()) else "incomplete",
                "checks": country_checks,
                "missing": country_layer_missing,
                "hierarchy_nodes": len((formal_hierarchy.get(code) or {}).get("nodes") or []),
                "checked_at": ((sources_by_code[code][1].get("meta") or {}).get("last_updated")),
            },
            "objects_total": len(objects),
            "objects_passed": passed,
            "objects_incomplete": len(objects) - passed,
            "object_missing": dict(sorted(missing.items())),
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
        "next_work_rule": "country layer -> regional geography -> country QA -> next country; object-card work is blocked until all country/regional layers are complete",
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
