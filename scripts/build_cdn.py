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

SCHEMA_VERSION = "2.1.0"
RELEASE_ID = "2026-09-28-r4"
PUBLISH = [
    ("brunei.json", "BN", "brunei"),
    ("cambodia.json", "KH", "cambodia"),
    ("laos.json", "LA", "laos"),
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
}


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def compact_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return value


def gallery_from(obj):
    ill = obj.get("illustration") or {}
    gallery = []
    if isinstance(ill.get("gallery"), list):
        for row in ill["gallery"]:
            if isinstance(row, dict) and row.get("static_url"):
                gallery.append(row)
    if ill.get("static_url"):
        candidate = {
            "url": ill.get("static_url"),
            "source_page": ill.get("source_page"),
            "provider": ill.get("provider"),
            "license": ill.get("license"),
            "artist": ill.get("artist"),
            "last_checked": ill.get("last_checked"),
        }
        if not any(x.get("url") == candidate["url"] for x in gallery):
            gallery.insert(0, candidate)
    return gallery


def story_from(obj):
    ann = ((obj.get("traveler_card") or {}).get("annotation") or {})
    narrative = ann.get("narrative") if isinstance(ann, dict) else None
    return {
        "narrative": compact_text(narrative) or compact_text(obj.get("why_go")),
        "culture_ethnography": compact_text(ann.get("culture_ethnography")) if isinstance(ann, dict) else None,
        "geography_geology": compact_text(ann.get("geography_geology")) if isinstance(ann, dict) else None,
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
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    release = PUBLIC / RELEASE_ID
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

    for filename, code, country_slug in PUBLISH:
        src_path = SRC / filename
        if not src_path.exists() or src_path.stat().st_size < 10000:
            raise RuntimeError(f"source missing or too small: {src_path}")
        source = load(src_path)
        if (source.get("meta") or {}).get("data_model_version") != "1.5":
            raise RuntimeError(f"{filename}: publish requires source model 1.5")

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
            route = obj.get("route_meta") or {}
            gallery = gallery_from(obj)
            story = story_from(obj)

            tags = list(dict.fromkeys((obj.get("tags") or []) + (obj.get("interest") or [])))
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
                    "narrow": compact_text(obj.get("narrow")),
                    "object_type": object_type,
                    "object_type_label_ru": TYPE_LABELS[object_type],
                    "prominence": obj.get("class"),
                    "interests": obj.get("interest") or [],
                    "tags": tags,
                },
                "location": location,
                "story": story,
                "visit": {
                    "logistics": card.get("logistics"),
                    "climate": card.get("climate"),
                    "operations": card.get("operations"),
                    "safety": card.get("safety"),
                    "accommodation": card.get("accommodation"),
                    "traveler_reports": card.get("traveler_reports"),
                },
                "route": route,
                "media": {
                    "gallery": gallery,
                    "gallery_status": "carousel_ready" if len(gallery) >= 2 else "single_image_source",
                    "photo_video": card.get("media"),
                },
                "provenance": {
                    "sources": obj.get("sources") or [],
                    "verification": obj.get("verification"),
                    "source_country_file": filename,
                },
            }
            dump(cdir / "objects" / f"{slug}.json", detail)

            card_row = {
                "id": object_id,
                "slug": slug,
                "name": name,
                "narrow": compact_text(obj.get("narrow")),
                "object_type": object_type,
                "object_type_label_ru": TYPE_LABELS[object_type],
                "prominence": obj.get("class"),
                "region": location.get("region"),
                "nearest_hub": location.get("nearest_hub"),
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
            for i in obj.get("interest") or []:
                interest_counts[str(i)] += 1
            prominence_counts[str(obj.get("class") or "unknown")] += 1

            keywords = list(dict.fromkeys(
                re.findall(
                    r"[\w\-]+",
                    " ".join(
                        str(x)
                        for x in [
                            name,
                            obj.get("narrow") or "",
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
                "narrow": compact_text(obj.get("narrow")),
                "object_type": object_type,
                "prominence": obj.get("class"),
                "region": location.get("region"),
                "nearest_hub": location.get("nearest_hub"),
                "tags": tags,
                "keywords": keywords,
                "detail_path": card_row["detail_path"],
            })
            qa_objects.append({
                "id": object_id,
                "story": bool(story.get("narrative")),
                "narrow": bool(card_row.get("narrow")),
                "logistics": bool(card.get("logistics")),
                "water": bool((card.get("logistics") or {}).get("water") or route.get("water")),
                "overnight": bool((card.get("logistics") or {}).get("overnight_and_camping") or route.get("overnight_and_camping")),
                "accommodation": bool(card.get("accommodation")),
                "traveler_reports": bool(card.get("traveler_reports")),
                "sources": bool(obj.get("sources")),
                "route_meta": bool(route),
                "hero": bool(gallery),
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
                "name": name,
                "slug": slugify(name),
                "languages_spoken": region.get("languages_spoken") or [],
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
        },
        "countries": countries,
    })

    required = ["story", "narrow", "logistics", "water", "overnight", "accommodation", "traveler_reports", "sources", "route_meta", "hero"]
    coverage = {k: sum(1 for x in qa_objects if x[k]) for k in required}
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
            for k in required
            if any(not x[k] for x in qa_objects)
        },
        "notes": [
            "Source model remains editorial/research; CDN is a normalized read model.",
            "why_go is not emitted separately: one canonical story lives at story.narrative.",
            "Object type is curated independently of broad search tags.",
            "Single-image objects remain valid but are marked single_image_source for later gallery enrichment.",
        ],
    }
    dump(release / "qa.json", qa)

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
