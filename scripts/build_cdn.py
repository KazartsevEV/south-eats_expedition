#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
PUBLIC = ROOT / "public" / "cdn" / "v2"

SCHEMA_VERSION = "2.10.9"
RELEASE_ID = "2026-09-29-r39"
SUPPORTED_SOURCE_MODELS = {"1.5", "1.6"}
PUBLISH = [
    ("brunei.json", "BN", "brunei"),
    ("cambodia.json", "KH", "cambodia"),
    ("laos.json", "LA", "laos"),
    ("indonesia.json", "ID", "indonesia"),
    ("malaysia.json", "MY", "malaysia"),
    ("myanmar.json", "MM", "myanmar"),
]

TYPE_LABELS = {
    "religious_site": "Храмы и религиозные объекты",
    "living_settlement": "Живые традиционные поселения",
    "national_park": "Национальные парки",
    "protected_area": "Заповедники и охраняемые территории",
    "museum": "Музеи",
    "memorial_site": "Мемориальные места",
    "industrial_heritage": "Индустриальное наследие",
    "market": "Рынки",
    "megalithic_site": "Мегалиты",
    "archaeological_site": "Археологические объекты",
    "city": "Города",
    "historic_city": "Исторические города и кварталы",
    "historic_building": "Исторические здания и руины",
    "palace": "Дворцы",
    "island_or_coast": "Острова и побережья",
    "cave": "Пещеры",
    "waterfall": "Водопады",
    "river_or_wetland": "Реки, озёра, водно-болотные угодья",
    "wildlife_site": "Наблюдение за дикой природой",
    "natural_landscape": "Природные ландшафты и треккинг",
    "cultural_landscape": "Культурные ландшафты",
    "monument": "Памятники и монументы",
    "mountain": "Горы",
    "volcano": "Вулканы и вулканические комплексы",
    "plateau": "Плато и нагорья",
    "karst": "Карстовые районы",
    "lake": "Озёра",
    "river": "Реки",
    "wetland": "Болота и водно-болотные угодья",
    "mangrove": "Мангровые леса",
    "forest": "Леса и джунгли",
    "island": "Острова и архипелаги",
    "beach": "Пляжи",
    "reef": "Рифы",
    "diving_site": "Места для дайвинга",
    "geological_site": "Геологические объекты",
    "fortification": "Фортификации",
    "colonial_architecture": "Колониальная архитектура",
    "traditional_settlement": "Традиционные поселения",
    "craft_center": "Ремесленные центры",
    "abandoned_site": "Заброшенные объекты",
}

TYPE_BY_NAME = {
    "Omar Ali Saifuddien Mosque": "religious_site",
    "Jame' Asr Hassanil Bolkiah Mosque": "religious_site",
    "Kampong Ayer": "living_settlement",
    "Ulu Temburong National Park": "national_park",
    "Royal Regalia Museum": "museum",
    "Seria oil heritage landscape": "industrial_heritage",
    "Labi interior": "cultural_landscape",
    "Tutong and Tamu markets": "market",
    "Tasek Merimbun Heritage Park": "protected_area",
    "Tasek Lama Park": "natural_landscape",
    "Teraja Longhouse": "living_settlement",
    "Mendaram Besar Longhouse": "living_settlement",
    "Billionth Barrel Monument": "monument",
    "Malay Technology Museum": "museum",
    "Bukit Shahbandar Recreational Park": "natural_landscape",
    "Brunei River Mangrove Safari": "river_or_wetland",
    "Tamu Kianggeh": "market",
    "Berakas Forest Recreational Park": "natural_landscape",

    "Angkor Archaeological Park": "archaeological_site",
    "Royal Palace Phnom Penh": "palace",
    "Tuol Sleng Genocide Museum": "museum",
    "Choeung Ek": "memorial_site",
    "Preah Vihear": "archaeological_site",
    "Koh Ker": "archaeological_site",
    "Sambor Prei Kuk": "archaeological_site",
    "Koh Rong islands": "island_or_coast",
    "Banteay Chhmar": "archaeological_site",
    "Preah Khan Kompong Svay": "archaeological_site",
    "Battambang historic shophouses": "historic_city",
    "Cardamom Mountains community routes": "protected_area",
    "Beng Mealea": "archaeological_site",
    "Phnom Kulen National Park": "national_park",
    "Tonle Sap Biosphere Reserve": "protected_area",
    "Oudong": "religious_site",
    "Angkor Borei and Phnom Da": "archaeological_site",
    "Kratie / Kampi Irrawaddy dolphins": "wildlife_site",
    "Bokor National Park and hill station": "national_park",

    "Luang Prabang": "historic_city",
    "Plain of Jars": "megalithic_site",
    "Vang Vieng karst": "natural_landscape",
    "Wat Phou": "archaeological_site",
    "Si Phan Don / 4000 Islands": "river_or_wetland",
    "Vieng Xai caves": "cave",
    "Kong Lor Cave": "cave",
    "Savannakhet old quarter": "historic_city",
    "Nam Et-Phou Louey area": "protected_area",
    "Nong Khiaw and Muang Ngoi": "natural_landscape",
    "Bolaven Plateau": "natural_landscape",
    "Nam Ha National Protected Area": "protected_area",
    "Tham Piu Cave": "cave",
    "Vientiane sacred architecture": "religious_site",
    "Old Thakhek Town": "historic_city",
    "Phongsaly old town and ancient tea highlands": "cultural_landscape",
    "Muang Sing market and Tai Lue cultural landscape": "cultural_landscape",
    "Kuang Si Falls": "waterfall",
    "Pak Ou Caves": "cave",
    "Hin Nam No National Park": "national_park",
    "Nakai Nam Theun National Park": "national_park",
    "Phou Khao Khouay National Park": "national_park",
    "Xe Pian National Park": "national_park",
    "Tad Fane": "waterfall",
    "Tad Yuang": "waterfall",
    "Khone Phapheng Falls": "waterfall",
    "Li Phi / Somphamit Falls": "waterfall",
    "Tham Pa Fa": "cave",
    "Tham Nang Aen": "cave",
    "Dong Hua Sao National Park": "national_park",
    "Nong Fa / Dong Ampham landscape": "natural_landscape",
}



TYPE_BY_NAME.update({
    "Borobudur": "archaeological_site",
    "Prambanan": "archaeological_site",
    "Yogyakarta": "city",
    "Bali temple landscapes": "cultural_landscape",
    "Komodo National Park": "national_park",
    "Bromo-Tengger-Semeru": "natural_landscape",
    "Ijen": "natural_landscape",
    "Raja Ampat": "island_or_coast",
    "Banda Neira": "historic_city",
    "Lasem": "historic_city",
    "Sawahlunto": "industrial_heritage",
    "Tana Toraja hinterland": "cultural_landscape",
    "Gunung Leuser National Park / Bukit Lawang": "national_park",
    "Tanjung Puting National Park": "national_park",
    "Kelimutu National Park": "national_park",
    "Dieng Plateau": "cultural_landscape",
    "Wakatobi National Park": "national_park",
    "Togean Islands": "island_or_coast",
    "Lake Toba / Samosir Batak cultural landscape": "cultural_landscape",
    "Wae Rebo": "living_settlement",
    "Sumba megalithic villages": "megalithic_site",

    "Kuala Lumpur": "city",
    "George Town": "historic_city",
    "Melaka": "historic_city",
    "Mount Kinabalu": "natural_landscape",
    "Gunung Mulu National Park": "national_park",
    "Langkawi": "island_or_coast",
    "Perhentian islands": "island_or_coast",
    "Taiping": "historic_city",
    "Kuala Kangsar": "historic_city",
    "Belum-Temengor": "protected_area",
    "Bario / Kelabit Highlands": "cultural_landscape",
    "Danum Valley Conservation Area": "protected_area",
    "Kinabatangan River": "river_or_wetland",
    "Niah National Park": "national_park",
    "Kellie's Castle": "historic_building",
    "Kuching old town and waterfront": "historic_city",
    "Lenggong Valley archaeological landscape": "archaeological_site",
    "Sipadan Island": "island_or_coast",
    "Kampung Bavanggazo / Rungus longhouse": "living_settlement",
    "Batu Caves": "cave",
    "Sepilok Orangutan Rehabilitation Centre": "wildlife_site",
})


TYPE_BY_NAME.update({
    "Bagan": "archaeological_site",
    "Shwedagon Pagoda": "religious_site",
    "Inle Lake": "river_or_wetland",
    "Mandalay heritage": "historic_city",
    "Kyaiktiyo / Golden Rock": "religious_site",
    "Mawlamyine colonial core": "historic_city",
    "Pyin Oo Lwin": "historic_city",
    "Dawei old town": "historic_city",
    "Mrauk U": "archaeological_site",
    "Pyu Ancient Cities": "archaeological_site",
    "Hpa-An karst and caves": "natural_landscape",
    "Kakku Pagodas": "archaeological_site",
    "Monywa / Thanboddhay and Bodhi Tataung": "religious_site",
    "Indawgyi Lake": "protected_area",
    "Nat Ma Taung / Mount Victoria": "national_park",
})

# Refine broad legacy buckets into the primary real-world classes used by CDN v2.2.
TYPE_BY_NAME.update({
    "Tasek Merimbun Heritage Park": "lake",
    "Tasek Lama Park": "forest",
    "Bukit Shahbandar Recreational Park": "forest",
    "Brunei River Mangrove Safari": "mangrove",
    "Koh Rong islands": "island",
    "Tonle Sap Biosphere Reserve": "wetland",
    "Vang Vieng karst": "karst",
    "Si Phan Don / 4000 Islands": "island",
    "Nong Khiaw and Muang Ngoi": "karst",
    "Bolaven Plateau": "plateau",
    "Bromo-Tengger-Semeru": "volcano",
    "Ijen": "volcano",
    "Raja Ampat": "island",
    "Dieng Plateau": "plateau",
    "Togean Islands": "island",
    "Lake Toba / Samosir Batak cultural landscape": "lake",
    "Mount Kinabalu": "mountain",
    "Langkawi": "island",
    "Perhentian islands": "island",
    "Kinabatangan River": "river",
    "Sipadan Island": "island",
    "Inle Lake": "lake",
    "Hpa-An karst and caves": "karst",
    "Indawgyi Lake": "lake",
    "Nat Ma Taung / Mount Victoria": "mountain",
})


TYPE_BY_NAME.update({
    "Taman Negara National Park": "national_park",
    "Endau-Rompin National Park (Johor)": "national_park",
    "Gunung Stong State Forest Park": "protected_area",
    "Bako National Park": "national_park",
    "Maliau Basin Conservation Area": "protected_area",
    "Crocker Range Park and Salt Trail": "protected_area",
    "Gomantong Caves": "cave",
    "Sungai Batu Archaeological Site": "archaeological_site",
    "Bujang Valley Archaeological Museum and temple landscape": "archaeological_site",
    "Gua Tambun rock art site": "archaeological_site",
})


TYPE_BY_NAME.update({
    "Fairy Cave and Wind Cave Nature Reserves": "cave",
    "Gunung Gading National Park": "national_park",
    "Tawau Hills Park": "national_park",
    "Batang Ai National Park and Iban longhouse landscape": "cultural_landscape",
    "Gunung Jerai Geoforest Park": "mountain",
    "Tasik Chini Biosphere Reserve": "lake",
    "Gua Tempurung": "cave",
})

TYPE_BY_NAME.update({
    "Tabin Wildlife Reserve": "protected_area",
    "Imbak Canyon Conservation Area": "protected_area",
})

TAG_ALIASES = {
    "unesco": "unesco",
    "living heritage": "living_heritage",
    "living_heritage": "living_heritage",
    "colonial heritage": "colonial_heritage",
    "colonial_heritage": "colonial_heritage",
    "industrial heritage": "industrial_heritage",
    "industrial_heritage": "industrial_heritage",
    "community tourism": "community_tourism",
    "community_tourism": "community_tourism",
    "rural landscape": "rural_landscape",
    "rural_landscape": "rural_landscape",
    "daily life": "daily_life",
    "daily_life": "daily_life",
    "vernacular architecture": "vernacular_architecture",
    "vernacular_architecture": "vernacular_architecture",
    "megalithic heritage": "megalithic",
    "megalithic_heritage": "megalithic",
    "waterfalls": "waterfall",
    "waterfall": "waterfall",
    "caves": "cave",
    "cave": "cave",
    "islands": "island",
    "island": "island",
    "beaches": "beach",
    "beach": "beach",
    "temples": "temple",
    "temple": "temple",
    "lakes": "lake",
    "lake": "lake",
    "highlands": "highland",
    "highland": "highland",
    "mekong": "mekong",
}

def canonical_tag(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    key = re.sub(r"\s+", " ", raw).strip().lower()
    if key in TAG_ALIASES:
        return TAG_ALIASES[key]
    key = key.replace("/", "_").replace("-", "_").replace(" ", "_")
    key = re.sub(r"_+", "_", key).strip("_")
    return TAG_ALIASES.get(key, key)

def canonical_tags(values):
    out = []
    seen = set()
    for value in values or []:
        tag = canonical_tag(value)
        if tag and tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


CYRILLIC_TRANSLIT = str.maketrans({
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"i",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f",
    "х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
})

def slugify(value: str) -> str:
    raw = (value or "").strip()
    text = raw.lower().translate(CYRILLIC_TRANSLIT).replace("&", " and ")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if text:
        return text
    # Stable fallback for scripts not covered by transliteration. Never emit a shared "item" slug.
    return "item-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def compact_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return value



COORDINATE_TYPES = {
    "center", "entrance", "trailhead", "summit", "viewpoint", "pier", "parking",
    "cave_entrance", "waterfall_base", "archaeological_core", "temple_entrance",
}

def _dms_component(value, positive, negative, is_lat):
    direction = positive if value >= 0 else negative
    absolute = abs(float(value))
    degrees = int(absolute)
    minutes_full = (absolute - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60, 1)
    width = 2 if is_lat else 3
    return f"{degrees:0{width}d}°{minutes:02d}′{seconds:04.1f}″{direction}"

def gps_repr(lat, lon):
    return {
        "decimal": f"{float(lat):.6f}, {float(lon):.6f}",
        "dms": f"{_dms_component(lat, 'N', 'S', True)} {_dms_component(lon, 'E', 'W', False)}",
    }

def _normalized_point(raw, fallback_type=None):
    if not isinstance(raw, dict):
        return None
    coords = raw.get("coordinates") if isinstance(raw.get("coordinates"), dict) else raw
    lat = coords.get("lat")
    lon = coords.get("lon")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        return None
    if not isinstance(lon, (int, float)) or isinstance(lon, bool):
        return None
    point_type = raw.get("type") or raw.get("coordinate_type") or fallback_type or "center"
    elevation = coords.get("elevation_m")
    elevation_range = raw.get("elevation_range_m") or coords.get("elevation_range_m")
    normalized_range = None
    if isinstance(elevation_range, dict):
        min_m = elevation_range.get("min")
        max_m = elevation_range.get("max")
        if (
            isinstance(min_m, (int, float)) and not isinstance(min_m, bool)
            and isinstance(max_m, (int, float)) and not isinstance(max_m, bool)
        ):
            normalized_range = {"min": float(min_m), "max": float(max_m)}
    return {
        "name": raw.get("name"),
        "type": point_type,
        "coordinates": {
            "lat": float(lat),
            "lon": float(lon),
            "elevation_m": float(elevation) if isinstance(elevation, (int, float)) and not isinstance(elevation, bool) else None,
            "elevation_range_m": normalized_range,
        },
        "gps": gps_repr(lat, lon),
        "accuracy": raw.get("accuracy") or "unknown",
        "elevation_accuracy": raw.get("elevation_accuracy") or ("unknown" if elevation is None and normalized_range is None else raw.get("accuracy") or "unknown"),
        "source_refs": [raw.get("source_ref")] if raw.get("source_ref") else [],
        "elevation_source_refs": [raw.get("elevation_source_ref")] if raw.get("elevation_source_ref") else [],
        "checked_at": raw.get("coordinates_checked_at") or raw.get("checked_at"),
    }

OBJECT_ELEVATION_REFERENCE_TYPES = {
    "site",
    "summit",
    "highest_point",
    "characteristic",
    "range",
    "water_surface",
    "unknown",
}

def _normalized_object_elevation(raw, source_ref=None):
    if not isinstance(raw, dict):
        return None
    representative = raw.get("representative_m")
    min_m = raw.get("min_m")
    max_m = raw.get("max_m")
    def number_or_none(value):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return None
    representative = number_or_none(representative)
    min_m = number_or_none(min_m)
    max_m = number_or_none(max_m)
    if representative is None and min_m is None and max_m is None:
        return None
    if min_m is not None and max_m is not None and min_m > max_m:
        raise RuntimeError(f"invalid object elevation range: min {min_m} > max {max_m}")
    reference_type = raw.get("reference_type") or "unknown"
    if reference_type not in OBJECT_ELEVATION_REFERENCE_TYPES:
        raise RuntimeError(f"unsupported object elevation reference_type: {reference_type!r}")
    return {
        "representative_m": representative,
        "min_m": min_m,
        "max_m": max_m,
        "reference_type": reference_type,
        "accuracy": raw.get("accuracy") or "unknown",
        "source_refs": [source_ref] if source_ref else [],
        "checked_at": raw.get("checked_at"),
        "notes": raw.get("notes"),
    }

def normalize_geo(location, source_registry=None, object_id=None):
    location = location if isinstance(location, dict) else {}

    def fact_source_ref(holder, source_key, used_for_label):
        if not isinstance(holder, dict) or source_registry is None or object_id is None:
            return None
        source = holder.get(source_key)
        if source_key == "coordinate_source" and not isinstance(source, dict):
            source = holder.get("source")
        if not isinstance(source, dict):
            return None
        source = dict(source)
        used_for = list(source.get("used_for") or [])
        if used_for_label not in used_for:
            used_for.append(used_for_label)
        source["used_for"] = used_for
        return merge_source_entity(source_registry, source, object_id)

    object_elevation_raw = location.get("object_elevation")
    object_elevation_source_ref = fact_source_ref(
        object_elevation_raw,
        "source",
        "object elevation",
    ) if isinstance(object_elevation_raw, dict) else None
    object_elevation = _normalized_object_elevation(
        object_elevation_raw,
        object_elevation_source_ref,
    )

    primary_raw = {
        "coordinates": location.get("coordinates"),
        "coordinate_type": location.get("coordinate_type"),
        "accuracy": location.get("accuracy"),
        "elevation_accuracy": location.get("elevation_accuracy"),
        "elevation_range_m": location.get("elevation_range_m"),
        "source_ref": fact_source_ref(location, "coordinate_source", "coordinates"),
        "elevation_source_ref": fact_source_ref(location, "elevation_source", "elevation"),
        "coordinates_checked_at": location.get("coordinates_checked_at"),
    }
    primary = _normalized_point(primary_raw, "center")
    points = []
    for row in location.get("geo_points") or []:
        if not isinstance(row, dict):
            continue
        normalized_raw = dict(row)
        normalized_raw["source_ref"] = fact_source_ref(row, "coordinate_source", "coordinates")
        normalized_raw["elevation_source_ref"] = fact_source_ref(row, "elevation_source", "elevation")
        point = _normalized_point(normalized_raw)
        if point:
            points.append(point)
    return {
        "crs": "WGS84",
        "epsg": 4326,
        "primary_location": primary,
        "points": points,
        "object_elevation": object_elevation,
    }

def location_context(location):
    location = dict(location or {})
    for key in [
        "coordinates", "coordinate_type", "accuracy", "elevation_accuracy", "elevation_range_m",
        "coordinate_source", "elevation_source", "coordinates_checked_at", "geo_points",
        "object_elevation",
    ]:
        location.pop(key, None)
    return location

def gallery_from(obj):
    ill = obj.get("illustration") or {}
    gallery = []
    seen = set()

    def add_media(row):
        if not isinstance(row, dict):
            return
        url = row.get("url") or row.get("static_url")
        if not url or url in seen:
            return
        seen.add(url)
        gallery.append({
            "url": url,
            "source_page": row.get("source_page"),
            "provider": row.get("provider"),
            "license": row.get("license"),
            "artist": row.get("artist"),
            "last_checked": row.get("last_checked"),
        })

    add_media(ill)
    for row in ill.get("gallery") or []:
        add_media(row)
    return gallery

def story_from(obj):
    ann = ((obj.get("traveler_card") or {}).get("annotation") or {})
    narrative = ann.get("narrative") if isinstance(ann, dict) else None
    return {
        "narrative": compact_text(narrative) or compact_text(obj.get("why_go")),
        "culture_ethnography": compact_text(ann.get("culture_ethnography")) if isinstance(ann, dict) else None,
        "geography_geology": compact_text(ann.get("geography_geology")) if isinstance(ann, dict) else None,
        "myths_legends_beliefs": ann.get("myths_legends_beliefs") if isinstance(ann, dict) else None,
    }


def narrow_from(obj):
    # The source "narrow" field in v1.5 often accumulated story + season + media notes.
    # For CDN, a lead must stay compact and must not duplicate the full narrative.
    return compact_text(obj.get("lead")) or compact_text(obj.get("why_go"))


def merged_logistics(card, route):
    logistics = dict(card.get("logistics") or {})
    if route:
        if not logistics.get("modes") and route.get("transport_modes"):
            logistics["modes"] = route.get("transport_modes")
        for src_key, dst_key in [
            ("walking", "walking"),
            ("water", "water"),
            ("overnight_and_camping", "overnight_and_camping"),
            ("permit_or_guide", "permit_or_guide"),
        ]:
            if not logistics.get(dst_key) and route.get(src_key):
                logistics[dst_key] = route.get(src_key)
        if not logistics.get("terrain_and_movement"):
            logistics["terrain_and_movement"] = ((route.get("expedition_profile") or {}).get("terrain_and_movement"))
    return logistics


def source_id_for(source):
    source = source if isinstance(source, dict) else {}
    identity = source.get("url") or "|".join(str(source.get(k) or "") for k in ("publisher", "title", "accessed"))
    return "src:" + hashlib.sha1(identity.encode("utf-8")).hexdigest()[:14]

def merge_source_entity(registry, source, object_id):
    if not isinstance(source, dict):
        return None
    sid = source_id_for(source)
    entity = registry.get(sid)
    if entity is None:
        entity = {
            "id": sid,
            "type": source.get("type"),
            "title": source.get("title"),
            "publisher": source.get("publisher"),
            "url": source.get("url"),
            "language": source.get("language"),
            "published_at": source.get("published_at"),
            "accessed_at": source.get("accessed") or source.get("accessed_at"),
            "authority": source.get("authority"),
            "used_for": list(source.get("used_for") or []),
            "notes": source.get("notes"),
            "referenced_by": [object_id],
        }
        registry[sid] = entity
    else:
        entity["referenced_by"] = list(dict.fromkeys((entity.get("referenced_by") or []) + [object_id]))
        entity["used_for"] = list(dict.fromkeys((entity.get("used_for") or []) + list(source.get("used_for") or [])))
        for key in ("type","title","publisher","url","language","published_at","accessed_at","authority","notes"):
            if entity.get(key) in (None, "", []):
                value = source.get("accessed") if key == "accessed_at" else source.get(key)
                if value not in (None, "", []):
                    entity[key] = value
    return sid

def visual_recon_from(card, source_registry=None, object_id=None):
    media = card.get("media") or {}
    scout = media.get("visual_scouting") or {}

    # Legacy Malaysia/Indonesia cards used shooting_recommendation + field_planning.
    # Convert that material into the canonical reconnaissance model without carrying
    # photographer instructions, shot lists, focal lengths, or camera settings into CDN.
    legacy_shoot = media.get("shooting_recommendation") or {}
    if not scout and isinstance(legacy_shoot, dict):
        positions = legacy_shoot.get("positions") or []
        scout = {
            "best_time": legacy_shoot.get("time") or media.get("best_light"),
            "best_weather_light": legacy_shoot.get("weather"),
            "viewpoints_for_photo_video": [
                {
                    "id": f"vp_{idx:02d}",
                    "description": value.strip(),
                    "best_time": legacy_shoot.get("time") or media.get("best_light"),
                    "best_weather_light": legacy_shoot.get("weather"),
                    "useful_equipment": [],
                }
                for idx, value in enumerate(positions, start=1)
                if isinstance(value, str) and value.strip()
            ],
            "seasonal_visuals": [],
            "video_activity": [],
            "useful_equipment": [],
        }

    viewpoints = []
    for idx, value in enumerate(scout.get("viewpoints_for_photo_video") or [], start=1):
        if isinstance(value, str) and value.strip():
            viewpoints.append({
                "id": f"vp_{idx:02d}",
                "name": None,
                "description": value.strip(),
                "coordinates": None,
                "gps": None,
                "access": None,
                "view": None,
                "best_time": scout.get("best_time"),
                "best_weather_light": scout.get("best_weather_light"),
                "useful_equipment": [],
                "source_refs": [],
            })
            continue
        if not isinstance(value, dict):
            continue
        row = dict(value)
        coords = row.get("coordinates") or {}
        lat = coords.get("lat") if isinstance(coords, dict) else None
        lon = coords.get("lon") if isinstance(coords, dict) else None
        normalized_coords = None
        gps = None
        if isinstance(lat, (int, float)) and not isinstance(lat, bool) and isinstance(lon, (int, float)) and not isinstance(lon, bool):
            elevation = coords.get("elevation_m")
            normalized_coords = {
                "lat": float(lat),
                "lon": float(lon),
                "elevation_m": float(elevation) if isinstance(elevation, (int, float)) and not isinstance(elevation, bool) else None,
            }
            gps = gps_repr(lat, lon)
        refs = list(row.get("source_refs") or [])
        source = row.get("source")
        if isinstance(source, dict) and source_registry is not None and object_id is not None:
            source = dict(source)
            used_for = list(source.get("used_for") or [])
            if "visual viewpoint" not in used_for:
                used_for.append("visual viewpoint")
            source["used_for"] = used_for
            sid = merge_source_entity(source_registry, source, object_id)
            if sid and sid not in refs:
                refs.append(sid)
        viewpoints.append({
            "id": row.get("id") or f"vp_{idx:02d}",
            "name": row.get("name"),
            "description": row.get("description"),
            "coordinates": normalized_coords,
            "gps": gps,
            "access": row.get("access"),
            "view": row.get("view"),
            "best_time": row.get("best_time") or scout.get("best_time"),
            "best_weather_light": row.get("best_weather_light") or scout.get("best_weather_light"),
            "useful_equipment": row.get("useful_equipment") or [],
            "source_refs": refs,
        })
    drone = media.get("drone")
    if isinstance(drone, dict):
        drone = dict(drone)
        drone_refs = list(drone.get("source_refs") or [])
        drone_source = drone.pop("source", None)
        if isinstance(drone_source, dict) and source_registry is not None and object_id is not None:
            drone_source = dict(drone_source)
            used_for = list(drone_source.get("used_for") or [])
            if "drone rules" not in used_for:
                used_for.append("drone rules")
            drone_source["used_for"] = used_for
            sid = merge_source_entity(source_registry, drone_source, object_id)
            if sid and sid not in drone_refs:
                drone_refs.append(sid)
        drone["source_refs"] = drone_refs

    return {
        "photo_suitability_5": media.get("photo_suitability_5"),
        "video_suitability_5": media.get("video_suitability_5"),
        "best_time": scout.get("best_time"),
        "best_weather_light": scout.get("best_weather_light"),
        "viewpoints": viewpoints,
        "seasonal_visuals": scout.get("seasonal_visuals") or [],
        "video_activity": scout.get("video_activity") or [],
        "useful_equipment": scout.get("useful_equipment") or [],
        "drone": drone,
        "filming_restrictions": media.get("filming_restrictions"),
    }

def country_payload(source, code, slug, object_count, places_count):
    travel = source.get("travel") or {}
    return {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "release_id": RELEASE_ID,
            "country_code": code,
            "country_slug": slug,
            "source_model_version": (source.get("meta") or {}).get("data_model_version"),
            "object_count": object_count,
            "places_count": places_count,
        },
        "overview": source.get("overview"),
        "nature": source.get("nature"),
        "climate": source.get("climate"),
        "safety": source.get("safety"),
        "travel_basics": {
            "festivals": travel.get("festivals"),
            "food": travel.get("food"),
            "laws_and_prohibitions": travel.get("laws_and_prohibitions"),
            "currency": travel.get("currency"),
        },
        "entry_and_transport": {
            "visa_for_russian_passport": travel.get("visa_for_russian_passport"),
            "airports": travel.get("airports"),
            "international_air_links": travel.get("international_air_links"),
            "land_borders": travel.get("land_borders"),
        },
    }


def build():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    release = PUBLIC / RELEASE_ID
    if release.exists():
        shutil.rmtree(release)
    release.mkdir(parents=True, exist_ok=True)

    countries = []
    search_objects = []
    places_global = []
    object_types = defaultdict(list)
    tag_counts = Counter()
    interest_counts = Counter()
    region_counts = Counter()
    prominence_counts = Counter()
    qa_objects = []
    lodging_registry = {}
    source_registry = {}

    for filename, code, country_slug in PUBLISH:
        src_path = SRC / filename
        if not src_path.exists() or src_path.stat().st_size < 10000:
            raise RuntimeError(f"source missing or too small: {src_path}")
        source = load(src_path)
        source_model = (source.get("meta") or {}).get("data_model_version")
        if source_model not in SUPPORTED_SOURCE_MODELS:
            raise RuntimeError(f"{filename}: unsupported source model {source_model!r}; supported={sorted(SUPPORTED_SOURCE_MODELS)}")

        travel = source.get("travel") or {}
        source_objects = travel.get("objects") or []
        source_regions = travel.get("regions") or []
        cdir = release / "countries" / country_slug

        cards = []
        region_to_ids = defaultdict(list)
        hub_to_ids = defaultdict(list)

        for obj in source_objects:
            name = obj.get("name")
            if name not in TYPE_BY_NAME:
                raise RuntimeError(f"untyped object in publish set: {code} / {name}")
            object_type = TYPE_BY_NAME[name]
            slug = slugify(name)
            object_id = f"{code.lower()}:{slug}"
            card = obj.get("traveler_card") or {}
            location = card.get("location") or {}
            geo = normalize_geo(location, source_registry, object_id)
            route = obj.get("route_meta") or {}
            gallery = gallery_from(obj)
            story = story_from(obj)
            narrow = narrow_from(obj)
            interests = canonical_tags(obj.get("interest") or [])
            tags = canonical_tags((obj.get("tags") or []) + interests)
            logistics = merged_logistics(card, route)
            visual_recon = visual_recon_from(card, source_registry, object_id)
            source_refs = []
            for source_row in obj.get("sources") or []:
                sid = merge_source_entity(source_registry, source_row, object_id)
                if sid and sid not in source_refs:
                    source_refs.append(sid)
            lodging_ids = []
            for lodging in card.get("accommodation") or []:
                if not isinstance(lodging, dict) or not lodging.get("name"):
                    continue
                lodging_id = f"lod:{code.lower()}:{slugify(lodging['name'])}"
                lodging_ids.append(lodging_id)
                current = lodging_registry.get(lodging_id)
                entity = {
                    "id": lodging_id,
                    "kind": "lodging",
                    "country_code": code,
                    "country_slug": country_slug,
                    "name": lodging.get("name"),
                    "area": lodging.get("area"),
                    "price_for_two": lodging.get("price_for_two"),
                    "contact": lodging.get("contact"),
                    "social_or_web": lodging.get("social_or_web"),
                    "source": lodging.get("source"),
                    "coordinates": lodging.get("coordinates"),
                    "checked_at": lodging.get("checked_at") or lodging.get("last_checked"),
                    "referenced_by": [object_id],
                }
                if current:
                    refs = list(dict.fromkeys((current.get("referenced_by") or []) + [object_id]))
                    current["referenced_by"] = refs
                    for key, value in entity.items():
                        if key != "referenced_by" and current.get(key) in (None, "", []):
                            current[key] = value
                else:
                    lodging_registry[lodging_id] = entity
            detail = {
                "meta": {
                    "schema_version": SCHEMA_VERSION,
                    "release_id": RELEASE_ID,
                    "object_id": object_id,
                    "slug": slug,
                    "country_code": code,
                    "country_slug": country_slug,
                },
                "identity": {
                    "name": name,
                    "narrow": narrow,
                    "object_type": object_type,
                    "object_type_label_ru": TYPE_LABELS[object_type],
                    "prominence": obj.get("class"),
                    "interests": interests,
                    "tags": tags,
                },
                "location": location_context(location),
                "geo": geo,
                "story": story,
                "visit": {
                    "logistics": logistics,
                    "climate": card.get("climate"),
                    "operations": card.get("operations"),
                    "safety": card.get("safety"),
                    "lodging_ids": lodging_ids,
                    "traveler_reports": card.get("traveler_reports"),
                },
                "visual_recon": visual_recon,
                "media": {
                    "gallery": gallery,
                    "gallery_status": "carousel_ready" if len(gallery) >= 2 else "single_image_source",
                },
                "provenance": {
                    "source_refs": source_refs,
                    "verification": obj.get("verification"),
                    "source_country_file": filename,
                },
            }
            dump(cdir / "objects" / f"{slug}.json", detail)

            card_row = {
                "id": object_id,
                "slug": slug,
                "name": name,
                "narrow": narrow,
                "object_type": object_type,
                "object_type_label_ru": TYPE_LABELS[object_type],
                "prominence": obj.get("class"),
                "region": location.get("region"),
                "nearest_hub": location.get("nearest_hub"),
                "coordinates": ((geo.get("primary_location") or {}).get("coordinates")),
                "coordinate_type": ((geo.get("primary_location") or {}).get("type")),
                "tags": tags,
                "hero": gallery[0] if gallery else None,
                "gallery_count": len(gallery),
                "detail_path": f"countries/{country_slug}/objects/{slug}.json",
            }
            cards.append(card_row)
            object_types[object_type].append({**card_row, "country_code": code, "country_slug": country_slug})
            if location.get("region"):
                region_to_ids[location["region"]].append(object_id)
                region_counts[f"{code}:{location['region']}"] += 1
            if location.get("nearest_hub"):
                hub_to_ids[location["nearest_hub"]].append(object_id)
            for t in tags:
                tag_counts[str(t)] += 1
            for i in interests:
                interest_counts[i] += 1
            prominence_counts[str(obj.get("class") or "unknown")] += 1

            keywords = list(dict.fromkeys(
                re.findall(
                    r"[\w\-]+",
                    " ".join(
                        str(x)
                        for x in [
                            name,
                            narrow or "",
                            object_type,
                            location.get("region") or "",
                            location.get("nearest_hub") or "",
                            " ".join(str(x) for x in tags),
                        ]
                    ).lower(),
                    flags=re.UNICODE,
                )
            ))
            search_objects.append({
                "id": object_id,
                "country_code": code,
                "country_slug": country_slug,
                "name": name,
                "slug": slug,
                "narrow": narrow,
                "object_type": object_type,
                "prominence": obj.get("class"),
                "region": location.get("region"),
                "nearest_hub": location.get("nearest_hub"),
                "coordinates": ((geo.get("primary_location") or {}).get("coordinates")),
                "coordinate_type": ((geo.get("primary_location") or {}).get("type")),
                "tags": tags,
                "keywords": keywords,
                "detail_path": card_row["detail_path"],
            })
            qa_objects.append({
                "id": object_id,
                "country_code": code,
                "object_type": object_type,
                "story": bool(story.get("narrative")),
                "narrow": bool(card_row.get("narrow")),
                "logistics": bool(logistics),
                "water": bool(logistics.get("water")),
                "overnight": bool(logistics.get("overnight_and_camping")),
                "accommodation": bool(lodging_ids),
                "traveler_reports": bool(card.get("traveler_reports")),
                "sources": bool(obj.get("sources")),
                "hero": bool(gallery),
                "gallery_min_2": len(gallery) >= 2,
                "photo_video": bool(card.get("media")),
                "visual_recon": bool(visual_recon.get("best_time") or visual_recon.get("viewpoints")),
                "coordinates": bool(geo.get("primary_location")),
                "elevation": bool(geo.get("object_elevation")),
                "coordinate_type": bool((geo.get("primary_location") or {}).get("type")),
                "dynamic_checked_at": bool((card.get("operations") or {}).get("last_verified")),
            })

        places = []
        for region in source_regions:
            name = region.get("name")
            if not name:
                continue
            pid = f"{code.lower()}:region:{slugify(name)}"
            row = {
                "id": pid,
                "kind": "region",
                "name": region.get("name_ru") or name,
                "canonical_name": name,
                "slug": slugify(name),
                "summary": region.get("summary"),
                "languages_spoken": region.get("languages_spoken") or [],
                "language_notes": region.get("language_notes"),
                "currency": region.get("currency"),
                "climate_summary": region.get("climate_summary"),
                "best_period_general": region.get("best_period_general"),
                "object_ids": region_to_ids.get(name, []),
                "last_verified": region.get("last_verified"),
            }
            places.append(row)
            places_global.append({**row, "country_code": code, "country_slug": country_slug})

        for hub, ids in sorted(hub_to_ids.items()):
            pid = f"{code.lower()}:hub:{slugify(hub)}"
            row = {
                "id": pid,
                "kind": "city_or_route_hub",
                "name": hub,
                "slug": slugify(hub),
                "object_ids": ids,
            }
            places.append(row)
            places_global.append({**row, "country_code": code, "country_slug": country_slug})

        dump(cdir / "objects.json", {
            "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "country_code": code, "count": len(cards)},
            "objects": cards,
        })
        dump(cdir / "places.json", {
            "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "country_code": code, "count": len(places)},
            "places": places,
        })
        by_type = defaultdict(list)
        for card in cards:
            by_type[card["object_type"]].append(card["id"])
        dump(cdir / "collections.json", {
            "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "country_code": code},
            "collections": [
                {
                    "object_type": t,
                    "label_ru": TYPE_LABELS[t],
                    "count": len(ids),
                    "object_ids": ids,
                }
                for t, ids in sorted(by_type.items(), key=lambda x: (-len(x[1]), x[0]))
            ],
        })
        dump(cdir / "country.json", country_payload(source, code, country_slug, len(cards), len(places)))

        hero = next((x["hero"] for x in cards if x.get("hero")), None)
        countries.append({
            "country_code": code,
            "slug": country_slug,
            "country": (source.get("meta") or {}).get("country"),
            "summary": (source.get("overview") or {}).get("summary"),
            "objects_count": len(cards),
            "regions_count": len(source_regions),
            "currency": (travel.get("currency") or {}).get("code"),
            "cover": hero,
            "country_path": f"countries/{country_slug}/country.json",
            "objects_path": f"countries/{country_slug}/objects.json",
            "places_path": f"countries/{country_slug}/places.json",
            "collections_path": f"countries/{country_slug}/collections.json",
        })

    dump(release / "countries.json", {"meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID}, "countries": countries})
    dump(release / "places.json", {"meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "count": len(places_global)}, "places": places_global})

    type_rows = [
        {"value": t, "label_ru": TYPE_LABELS[t], "count": len(rows), "collection_path": f"collections/{t}.json"}
        for t, rows in sorted(object_types.items(), key=lambda x: (-len(x[1]), x[0]))
    ]
    dump(release / "object-types.json", {"meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID}, "object_types": type_rows})
    for t, rows in object_types.items():
        dump(release / "collections" / f"{t}.json", {
            "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "object_type": t, "count": len(rows)},
            "objects": rows,
        })

    dump(release / "taxonomy.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID},
        "object_types": type_rows,
        "prominence": [{"value": k, "count": v} for k, v in prominence_counts.most_common()],
        "interests": [{"value": k, "count": v} for k, v in interest_counts.most_common()],
        "tags": [{"value": k, "count": v} for k, v in tag_counts.most_common()],
        "regions": [{"value": k, "count": v} for k, v in region_counts.most_common()],
    })
    dump(release / "search" / "objects.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "count": len(search_objects), "purpose": "compact client-side search; story prose intentionally excluded"},
        "objects": search_objects,
    })
    dump(release / "search" / "places.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "count": len(places_global)},
        "places": places_global,
    })

    dump(release / "home.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "scope": "canonical reference countries"},
        "project": {
            "title": "Expedition South East",
            "about_southeast_asia": "Юго-Восточная Азия — регион между Индийским и Тихим океанами, включающий материковый Индокитай и островные/архипелажные территории. В проекте он рассматривается как единое экспедиционное пространство из 11 стран.",
            "countries_total_target": 11,
            "countries_in_release": len(countries),
        },
        "navigation": {
            "countries": "countries.json",
            "object_types": "object-types.json",
            "places": "places.json",
            "taxonomy": "taxonomy.json",
            "object_search": "search/objects.json",
            "place_search": "search/places.json",
            "geodata_contract": "schema/geodata-contract.json",
            "lodging": "infrastructure/lodging/index.json",
            "sources": "sources/index.json",
            "country_qa": "qa/countries/index.json",
        },
        "countries": countries,
    })

    blocking_required = ["story", "narrow", "logistics", "sources", "hero"]
    expedition_required = ["water", "overnight", "accommodation", "traveler_reports", "gallery_min_2", "photo_video", "visual_recon", "coordinates", "elevation", "coordinate_type", "dynamic_checked_at"]
    coverage = {k: sum(1 for x in qa_objects if x[k]) for k in blocking_required + expedition_required}
    qa = {
        "schema_version": SCHEMA_VERSION,
        "release_id": RELEASE_ID,
        "countries": len(countries),
        "objects": len(search_objects),
        "places": len(places_global),
        "object_types": len(object_types),
        "coverage": coverage,
        "failures": {
            k: [x["id"] for x in qa_objects if not x[k]]
            for k in blocking_required
            if any(not x[k] for x in qa_objects)
        },
        "gaps": {
            k: [x["id"] for x in qa_objects if not x[k]]
            for k in expedition_required
            if any(not x[k] for x in qa_objects)
        },
        "notes": [
            "Source model remains editorial/research; CDN is the normalized read model.",
            "The CDN emits one compact lead at identity.narrow and one canonical story at story.narrative.",
            "Route metadata is merged into visit.logistics and is not emitted as a duplicate route block.",
            "Tags and interests are canonicalized to lowercase underscore identifiers.",
            "Object type is curated independently of broad search tags.",
            "Incomplete expedition fields remain visible in qa.gaps; sparse objects are not deleted.",
        ],
    }
    dump(release / "qa.json", qa)

    country_qa_rows = []
    country_qa_fields = blocking_required + expedition_required
    for _, code, country_slug in PUBLISH:
        rows = [row for row in qa_objects if row.get("country_code") == code]
        missing = {
            key: [row["id"] for row in rows if not row.get(key)]
            for key in country_qa_fields
            if any(not row.get(key) for row in rows)
        }
        complete = [
            row["id"]
            for row in rows
            if all(row.get(key) for key in country_qa_fields)
        ]
        payload = {
            "meta": {
                "schema_version": SCHEMA_VERSION,
                "release_id": RELEASE_ID,
                "country_code": code,
                "country_slug": country_slug,
            },
            "objects_total": len(rows),
            "objects_complete": len(complete),
            "objects_incomplete": len(rows) - len(complete),
            "coverage": {
                key: sum(1 for row in rows if row.get(key))
                for key in country_qa_fields
            },
            "missing": missing,
            "class_breakdown": [
                {
                    "object_type": object_type,
                    "objects_total": len(class_rows),
                    "objects_complete": sum(
                        1 for row in class_rows
                        if all(row.get(key) for key in country_qa_fields)
                    ),
                    "missing": {
                        key: [row["id"] for row in class_rows if not row.get(key)]
                        for key in country_qa_fields
                        if any(not row.get(key) for row in class_rows)
                    },
                }
                for object_type, class_rows in sorted(
                    (
                        (otype, [row for row in rows if row.get("object_type") == otype])
                        for otype in sorted({row.get("object_type") for row in rows if row.get("object_type")})
                    ),
                    key=lambda item: item[0],
                )
            ],
        }
        path = release / "qa" / "countries" / f"{country_slug}.json"
        dump(path, payload)
        country_qa_rows.append({
            "country_code": code,
            "country_slug": country_slug,
            "objects_total": len(rows),
            "objects_complete": len(complete),
            "objects_incomplete": len(rows) - len(complete),
            "path": path.relative_to(release).as_posix(),
        })
    dump(release / "qa" / "countries" / "index.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "count": len(country_qa_rows)},
        "countries": country_qa_rows,
    })

    source_index = []
    for source_id, entity in sorted(source_registry.items()):
        source_path = release / "sources" / f"{source_id.split(':',1)[1]}.json"
        dump(source_path, entity)
        source_index.append({
            "id": source_id,
            "publisher": entity.get("publisher"),
            "title": entity.get("title"),
            "url": entity.get("url"),
            "detail_path": source_path.relative_to(release).as_posix(),
            "referenced_by_count": len(entity.get("referenced_by") or []),
        })
    dump(release / "sources" / "index.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "count": len(source_index)},
        "sources": source_index,
    })

    lodging_index = []
    for lodging_id, entity in sorted(lodging_registry.items()):
        path = release / "infrastructure" / "lodging" / entity["country_slug"] / f"{slugify(entity['name'])}.json"
        dump(path, entity)
        lodging_index.append({
            "id": lodging_id,
            "country_code": entity["country_code"],
            "name": entity["name"],
            "area": entity.get("area"),
            "detail_path": path.relative_to(release).as_posix(),
            "referenced_by": entity.get("referenced_by") or [],
        })
    dump(release / "infrastructure" / "lodging" / "index.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID, "count": len(lodging_index)},
        "lodging": lodging_index,
    })

    dump(release / "schema" / "geodata-contract.json", {
        "meta": {"schema_version": SCHEMA_VERSION, "release_id": RELEASE_ID},
        "crs": "WGS84",
        "epsg": 4326,
        "primary_coordinate_fields": ["lat", "lon", "elevation_m", "elevation_range_m"],
        "object_elevation_fields": ["representative_m", "min_m", "max_m", "reference_type", "accuracy", "source_refs", "checked_at", "notes"],
        "fact_provenance": {
            "coordinate_sources": "source_refs",
            "point_elevation_sources": "elevation_source_refs",
            "object_elevation_sources": "geo.object_elevation.source_refs"
        },
        "coordinate_types": sorted(COORDINATE_TYPES),
        "accuracy_values": ["high", "medium", "approximate", "unknown"],
        "rules": {
            "lat_range": [-90, 90],
            "lon_range": [-180, 180],
            "elevation_unit": "metres_above_mean_sea_level",
            "point_elevation_rule": "Elevation inside primary_location/geo.points belongs only to that GPS point (entrance, pier, trailhead, viewpoint, etc.) and never satisfies object-level elevation QA by itself.",
            "object_elevation_rule": "geo.object_elevation describes the object itself above mean sea level: summit/highest point for peaks, min/max or characteristic elevation for extensive terrain, water_surface for lakes, and site elevation for point-like cultural objects.",
            "elevation_range_rule": "Use min_m/max_m for mountains, plateaus, parks and other extensive objects when one scalar would create false precision.",
            "unknown_values": "null",
            "no_false_precision": True,
            "large_objects": "Use an operational primary point such as entrance/trailhead/pier and additional geo.points rather than an unexplained geometric centre.",
        },
    })

    manifest_files = []
    for path in sorted(release.rglob("*.json")):
        if path.name == "manifest.json":
            continue
        data = path.read_bytes()
        manifest_files.append({
            "path": path.relative_to(release).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    manifest = {
        "project": "Expedition South East",
        "schema_version": SCHEMA_VERSION,
        "release_id": RELEASE_ID,
        "status": "reference_release",
        "published_countries": [x[1] for x in PUBLISH],
        "target_countries_total": 11,
        "totals": {
            "countries": len(countries),
            "objects": len(search_objects),
            "places": len(places_global),
            "object_types": len(object_types),
            "lodging": len(lodging_registry),
            "sources": len(source_registry),
            "files": len(manifest_files),
        },
        "files": manifest_files,
    }
    dump(release / "manifest.json", manifest)
    dump(PUBLIC / "latest.json", {
        "project": "Expedition South East",
        "schema_version": SCHEMA_VERSION,
        "release_id": RELEASE_ID,
        "release_path": f"{RELEASE_ID}/",
        "manifest": f"{RELEASE_ID}/manifest.json",
        "status": "reference_release",
        "published_countries": [x[1] for x in PUBLISH],
        "target_countries_total": 11,
    })
    print(json.dumps(manifest["totals"], ensure_ascii=False))


if __name__ == "__main__":
    build()
