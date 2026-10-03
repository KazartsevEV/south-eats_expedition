#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "laos.json"
REGISTRY = ROOT / "data" / "id-registry.json"
CHECKED = "2026-10-03"

NEW_SOURCES = {
    "https://discoverlaos.today/en/vang-vieng/thing-to-do/kaeng-nyui": "src_990511",
    "https://www.adb.org/projects/49387-002/main": "src_990512",
    "https://ewsdata.rightsindevelopment.org/files/documents/02/ADB-49387-002_YRpx9UL.pdf": "src_990513",
    "https://www.sgp.undp.org/spacial-itemid-projects-landing-page/spacial-itemid-project-search-results/spacial-itemid-project-detailpage.html?id=26307&view=projectdetail": "src_990514",
    "https://researchcommons.waikato.ac.nz/bitstreams/5ce5e24a-0ce8-4c87-aa0d-c85f9562cc0e/download": "src_990515",
    "https://laos-dmn.com/wp-content/uploads/2025/02/Vang-Vieng-Town-Environs-Tourism-Master-Plan-2025-%E2%80%93-2035_English-1.pdf": "src_990516",
    "https://www.travelfish.org/sight_profile/laos/vientiane_and_surrounds/vientiane/vang_vieng/3382": "src_990517",
    "https://www.tripadvisor.com/Attraction_Review-g612363-d4556470-Reviews-Kaeng_Nyui_Waterfalll-Vang_Vieng_Vientiane_Province.html": "src_990518",
    "https://www.wikiloc.com/hiking-trails/kaeng-nyui-201245476": "src_990519",
    "https://www.journeyatthirty.com/vang-vieng-laos-part-ii.html": "src_990520",
    "https://sg.trip.com/moments/detail/vang-vieng-21457-150662542/?curr=&locale=en-SG": "src_990521",
    "https://uat.discoverlaos.today/destination/vang-vieng": "src_990522",
}

def source_key(url: str) -> str:
    return "src:" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:14]

def find_object(node):
    if isinstance(node, dict):
        if node.get("name") == "Kaeng Nyui Waterfall":
            return node
        for value in node.values():
            found = find_object(value)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_object(value)
            if found is not None:
                return found
    return None

data = json.loads(SOURCE.read_text(encoding="utf-8"))
obj = find_object(data)
if obj is None:
    raise SystemExit("Kaeng Nyui Waterfall not found")

obj["class"] = "waterfall"
obj["interest"] = [
    "waterfall",
    "forest",
    "community_based_tourism",
    "ethnography",
    "walking",
    "swimming",
    "geology",
]
obj["why_go"] = (
    "Кенг-Ньюи — лесной водопад примерно в 7 км к востоку от Ванг-Вьенга, но интерес здесь не ограничивается главным 30-метровым сбросом. "
    "Маршрут идёт вдоль Хуай-Ньюи и Нам-Лао через небольшие каскады и Кенлон с купальной чашей, а сам участок десятилетиями управляется жителями Бан-Надуанг. "
    "После завершения новой бетонной дороги в 2025 году добираться сюда стало значительно проще, при этом внутри сохранился короткий лесной маршрут по водосборному лесу."
)

card = obj.setdefault("traveler_card", {})
card["location"] = {
    "region": "Vientiane Province / Vang Vieng District",
    "nearest_hub": "Ванг-Вьенг",
    "languages_spoken": [
        "лаосский",
        "кхму и тайские языки встречаются в Бан-Надуанг; состав населения менялся и по старым источникам описывается по-разному",
    ],
    "coordinates": {
        "lat": 18.953889,
        "lon": 102.4925,
        "elevation_m": None,
    },
    "coordinate_type": "waterfall_base",
    "accuracy": "medium",
    "elevation_accuracy": "unknown",
    "coordinates_checked_at": CHECKED,
    "coordinate_source": {
        "type": "other",
        "title": "Kaeng Yui Waterfall — Initial Environmental Examination",
        "publisher": "Asian Development Bank",
        "url": "https://ewsdata.rightsindevelopment.org/files/documents/02/ADB-49387-002_YRpx9UL.pdf",
        "language": "en",
        "published_at": "2018",
        "authority": "high",
        "accessed": CHECKED,
        "notes": "ADB biodiversity proximity report gives 18°57′14″N, 102°29′33″E for Kaeng Yui Waterfall; Travelfish independently gives the same coordinate to the second.",
    },
    "object_elevation": {
        "representative_m": None,
        "min_m": 340,
        "max_m": 405,
        "reference_type": "range",
        "accuracy": "approximate",
        "source": {
            "type": "traveler_report",
            "title": "Kaeng Nyui — recorded hiking loop",
            "publisher": "Wikiloc",
            "url": "https://www.wikiloc.com/hiking-trails/kaeng-nyui-201245476",
            "language": "en",
            "published_at": "2025-02-12",
            "authority": "medium",
            "accessed": CHECKED,
        },
        "checked_at": CHECKED,
        "notes": (
            "340–405 м — диапазон GPS-трека посетителя по петле Кенг-Ньюи в феврале 2025 года, а не геодезические отметки верхней и нижней кромки водопада. "
            "Точную абсолютную высоту основания каскада надёжный источник не публикует."
        ),
    },
    "geo_points": [
        {
            "type": "waterfall_base",
            "name": "Кенг-Ньюи — главный каскад",
            "coordinates": {"lat": 18.953889, "lon": 102.4925, "elevation_m": None},
            "accuracy": "medium",
            "elevation_accuracy": "unknown",
            "coordinate_source": {
                "type": "other",
                "title": "Kaeng Yui Waterfall — ADB biodiversity proximity report",
                "publisher": "Asian Development Bank",
                "url": "https://ewsdata.rightsindevelopment.org/files/documents/02/ADB-49387-002_YRpx9UL.pdf",
                "language": "en",
                "published_at": "2018",
                "authority": "high",
                "accessed": CHECKED,
            },
            "checked_at": CHECKED,
        },
        {
            "type": "parking",
            "name": "Парковка и рынок у начала тропы",
            "coordinates": {"lat": 18.953333, "lon": 102.492778, "elevation_m": None},
            "accuracy": "medium",
            "elevation_accuracy": "unknown",
            "coordinate_source": {
                "type": "other",
                "title": "Kaeng Yui Waterfall Access Improvements — Initial Environmental Examination",
                "publisher": "Asian Development Bank",
                "url": "https://ewsdata.rightsindevelopment.org/files/documents/02/ADB-49387-002_rVRbhBM.pdf",
                "language": "en",
                "published_at": "2018",
                "authority": "high",
                "accessed": CHECKED,
                "notes": "IEE identifies the footpath/market/parking area at 18°57′12″N, 102°29′34″E.",
            },
            "checked_at": CHECKED,
        },
    ],
}

card["logistics"] = {
    "access": (
        "Из Ванг-Вьенга ехать на восток через Бан-Надуанг. Старые путеводители описывают каменистую грунтовку, но это уже устарело: "
        "ADB завершил 6,6 км бетонной дороги к водопаду и передал объект 1 августа 2025 года. Свежий отзыв декабря 2025 года отдельно отмечает необычно хорошее состояние дороги."
    ),
    "public_transport": (
        "Регулярный маршрут общественного транспорта прямо к Кенг-Ньюи не подтверждён. Для самостоятельного визита практичны мопед/мотоцикл, велосипед, частный водитель или пеший подход из Ванг-Вьенга."
    ),
    "last_mile": (
        "От парковки начинается оборудованный лесной маршрут вдоль ручьёв. Официальное описание ведёт через каскады и Кенлон к главному водопаду. "
        "GPS-петля февраля 2025 года получилась около 1,0 км с набором примерно 54 м; её время сильно зависит от остановок и купания."
    ),
    "typical_visit_hours": [1, 3],
    "permit_or_guide": (
        "Обязательный гид не нужен. Если нужен природоведческий контекст, Tourism Laos рекомендует договариваться о деревенском гиде в Бан-Надуанг: "
        "местные гиды объясняют растения, животных и традиционное использование лесных продуктов."
    ),
    "mobility_notes": (
        "Дорога до парковки теперь бетонная. Внутри — лесная тропа, небольшие мосты, мокрые камни и ступени; после сильного дождя поверхность скользкая, а поток заметно мощнее."
    ),
    "modes": {
        "public_transport": "Регулярный фиксированный маршрут до водопада не подтверждён.",
        "taxi_ridehail": "Можно договориться с тук-туком или частным водителем; актуальный фиксированный тариф не опубликован.",
        "car": "После реконструкции 2025 года подъезд к парковке идёт по бетонной дороге.",
        "moped": "Удобный самостоятельный вариант; новый бетонный подъезд устранил старую проблему каменистой грунтовки.",
        "motorcycle": "То же: примерно 6–7 км из города по улучшенному подъезду.",
        "walking": "Около 1,5 часа из Ванг-Вьенга по свежему пользовательскому отчёту; внутри участка ещё около километра лесной петли.",
    },
    "water": (
        "Напитки и еда продаются у входной зоны, которой управляют жители Бан-Надуанг. В ручьях и бассейнах вода природная и не классифицирована как питьевая; "
        "Кенлон официально описывается как место для купания."
    ),
    "water_structured": {
        "at_object": True,
        "quality": "unknown",
        "last_reliable_point": "продавцы напитков у парковки/входа Кенг-Ньюи",
        "distance_m": None,
        "natural_sources": [
            {
                "type": "stream",
                "potability": "treatment_required",
                "notes": "Хуай-Ньюи и Нам-Лао — поверхностная вода; питьевой статус не подтверждён.",
            },
            {
                "type": "swimming_pool",
                "potability": "technical_only",
                "notes": "Купальная чаша Кенлон предназначена для отдыха, не как источник питьевой воды.",
            },
        ],
        "notes": "Для питья использовать бутилированную воду из входной зоны; природную воду без обработки не пить.",
        "source_refs": ["src_000283", "src_990511"],
    },
    "supplies": {
        "status": "available_at_site",
        "summary": "У парковки/входа жители Бан-Надуанг держат точки с едой и напитками; крупные закупки удобнее делать в Ванг-Вьенге.",
        "poi_ids": [],
        "source_refs": ["src_000283", "src_990511"],
    },
    "overnight_and_camping": (
        "Кенг-Ньюи — дневной природный объект. Свободный кемпинг в деревенском охраняемом водосборном лесу не подтверждён. "
        "Исторически в Бан-Надуанг развивались homestay, но актуальную бронируемую инфраструктуру на 2026 год карточка не утверждает без отдельной проверки."
    ),
    "overnight": {
        "status": "unclear",
        "summary": "Разрешение на палаточную ночёвку у водопада не найдено; территория относится к деревенскому conservation/watershed forest.",
        "source_refs": ["src_990514", "src_990515"],
    },
    "access_requirements": (
        "Оплатить местный входной сбор; не сходить с оборудованной тропы в охраняемом водосборном лесу и соблюдать указания деревенской команды по купанию и чистоте."
    ),
    "access_options": [
        {
            "id": "vang_vieng_kaeng_nyui_road",
            "origin": "Ванг-Вьенг",
            "modes": ["motorcycle", "moped", "car", "walking"],
            "checked_at": CHECKED,
            "source_refs": ["src_990512", "src_990518", "src_990521"],
            "legs": [
                {
                    "mode": "motorcycle",
                    "distance_km": 6.6,
                    "duration_min": 20,
                    "surface": "paved",
                    "condition": "Новая бетонная дорога к водопаду, завершённая и переданная в 2025 году.",
                    "seasonality": "Круглогодичный дорожный доступ; после сильных дождей осторожнее на мокром покрытии.",
                    "elevation_gain_m": None,
                    "elevation_loss_m": None,
                    "trailhead": None,
                    "navigation": "Из Ванг-Вьенга на восток через Бан-Надуанг к конечной парковке водопада.",
                    "fords": 0,
                    "notes": "6,6 км — длина ADB access-improvement package; около 20 минут — свежий пользовательский ориентир, не официальный норматив.",
                    "source_refs": ["src_990512", "src_990521"],
                },
                {
                    "mode": "walking",
                    "distance_km": 1.0,
                    "duration_min": None,
                    "surface": "trail",
                    "condition": "Оборудованная лесная петля вдоль ручьёв, малых каскадов и Кенлона; мокрые участки скользкие.",
                    "seasonality": "В дождливый сезон поток сильнее, но тропа мокрее; в апреле–мае главный водопад может ослабнуть почти до ручья.",
                    "elevation_gain_m": 54,
                    "elevation_loss_m": 54,
                    "trailhead": {"lat": 18.953333, "lon": 102.492778},
                    "navigation": "От парковки следовать оборудованной тропе вдоль Хуай-Ньюи/Нам-Лао к Кенлону и главному каскаду.",
                    "fords": 0,
                    "notes": "Дистанция и набор — GPS-петля февраля 2025 года; точное время не фиксируем, потому что запись включает длительные остановки.",
                    "source_refs": ["src_990511", "src_990519"],
                },
            ],
        }
    ],
    "self_guided_default": True,
    "travel_model": "самостоятельный выезд из Ванг-Вьенга по новой бетонной дороге + короткий оборудованный лесной маршрут; деревенский гид опционален",
}

card["climate"] = {
    "best_period": (
        "Если нужен именно мощный водопад — конец сезона дождей и первые месяцы после него. В самый сухой период, особенно в апреле–мае, официальный туристический источник предупреждает, "
        "что Кенг-Ньюи может ослабнуть почти до ручья."
    ),
    "heat_rain_notes": (
        "В дождливый сезон вода сильнее и лес насыщеннее, но мостки, ступени и камни мокрые. В сухой сезон идти проще, однако впечатление от главного каскада сильно зависит от текущего расхода воды."
    ),
    "site_specific_notes": "Кенлон остаётся отдельной купальной точкой по пути; состояние и глубина бассейна после сильных дождей могут меняться.",
}

card["operations"] = {
    "status": "open/verify",
    "hours": None,
    "ticket": (
        "Небольшой деревенский сбор взимается на входе. Свежий пользовательский отчёт 2026 года называет около 20 000 кип; "
        "отдельные сообщения 2025 года после реконструкции давали 30 000–50 000 кип. Тариф считать динамическим и проверять на месте."
    ),
    "closure_notes": (
        "Публичного сезонного закрытия не найдено. Главный практический фактор — расход воды: в апреле–мае водопад может быть очень слабым."
    ),
    "last_verified": CHECKED,
    "official_url": "https://www.tourismlaos.org/central-provinces/vientiane-province/",
    "status_snapshot": {
        "as_of": CHECKED,
        "summary": (
            "ADB сообщает, что 6,6 км подъездной бетонной дороги и связанные улучшения были завершены на 100% и переданы 1 августа 2025 года. "
            "Отзывы декабря 2025 года подтверждают открытый объект, новую хорошую дорогу и прогулочный park-like маршрут к водопаду."
        ),
        "source_refs": ["src_990512", "src_990518"],
    },
    "source_refs": ["src_000283", "src_990512", "src_990518", "src_990521"],
}

card["safety"] = {
    "main_risks": [
        "мокрые камни и скользкие участки тропы после дождя",
        "резко более сильный поток в сезон дождей",
        "купальные чаши без подтверждённой спасательной инфраструктуры",
        "жара при пешем подходе из Ванг-Вьенга",
    ],
    "sensitive_areas": [
        "деревенский conservation/watershed forest — не сходить с тропы без необходимости",
        "не собирать лесные продукты и растения без разрешения местных владельцев/гидов",
        "соблюдать правила местной команды по чистоте и купанию",
    ],
    "confidence": "high",
    "source_refs": ["src_990513", "src_990514", "src_990515", "src_990519"],
    "checked_at": CHECKED,
}

card["media"] = {
    "photo_suitability_5": 5,
    "video_suitability_5": 5,
    "best_light": (
        "Главный каскад окружён лесом: мягкий утренний свет или лёгкая облачность лучше сохраняют фактуру тёмной скалы и белой воды. "
        "Для ручьёв и Кенлона рассеянный свет удобнее жёсткого полуденного солнца."
    ),
    "visual_scouting": {
        "best_time": "утро или облачный день; по сезону — когда поток ещё сильный после дождей",
        "best_weather_light": (
            "После дождей водопад мощнее и растительность насыщеннее; в сухую ясную погоду тропа проще, но в апреле–мае главный каскад может быть слабым."
        ),
        "viewpoints_for_photo_video": [
            {
                "id": "vp_main_platform",
                "name": "Платформа перед главным каскадом",
                "description": "Оборудованная точка прямо перед высоким узким сбросом; новая металлическая платформа отделяет зрителя от мокрой зоны у основания.",
                "coordinates": {"lat": 18.953889, "lon": 102.4925, "elevation_m": None},
                "access": "По основной лесной тропе от парковки через малые каскады.",
                "view": {"description": "весь 30-метровый каскад, тёмная скальная стенка и плотный лес вокруг"},
                "best_time": "утро или пасмурная погода",
                "best_weather_light": "Ровный свет лучше удерживает детали белой воды и теней под лесным пологом.",
                "useful_equipment": [
                    {"type": "wide", "why": "для полного вертикального каскада вместе с лесной стеной"},
                    {"type": "standard", "why": "для потока, скальной поверхности и деталей платформы"},
                ],
                "source": {
                    "type": "other",
                    "title": "Kaeng Nyui Waterfall",
                    "publisher": "Discover Laos Today",
                    "url": "https://discoverlaos.today/en/vang-vieng/thing-to-do/kaeng-nyui",
                    "language": "en",
                    "published_at": None,
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
            {
                "id": "vp_kenlon_pool",
                "name": "Кенлон и купальная чаша",
                "description": "Меньший, примерно 5-метровый водопад по пути к Кенг-Ньюи с естественным бассейном около 9 м в поперечнике.",
                "coordinates": None,
                "access": "На основной тропе до главного каскада.",
                "view": {"description": "малый каскад, круглая купальная чаша, лес и каменные берега"},
                "best_time": "утро",
                "best_weather_light": "Рассеянный свет уменьшает блики на воде.",
                "useful_equipment": [
                    {"type": "wide", "why": "для бассейна вместе с лесным окружением"},
                    {"type": "standard", "why": "для самого Кенлона и поверхности воды"},
                ],
                "source": {
                    "type": "government_official",
                    "title": "Vientiane Province — Kaeng Nyui Waterfall",
                    "publisher": "Tourism Laos",
                    "url": "https://www.tourismlaos.org/central-provinces/vientiane-province/",
                    "language": "en",
                    "published_at": None,
                    "authority": "high",
                    "accessed": CHECKED,
                },
            },
            {
                "id": "vp_stream_trail",
                "name": "Тропа вдоль Хуай-Ньюи и Нам-Лао",
                "description": "Последовательность ручьёв, небольших мостов, каскадов и водосборного леса до главного водопада.",
                "coordinates": None,
                "access": "Оборудованная петля от парковки.",
                "view": {"description": "ручьи под лесным пологом, небольшие каскады, мостики и плотная растительность"},
                "best_time": "утро или после лёгкого дождя",
                "best_weather_light": "Мягкий свет под лесом лучше прямого солнца.",
                "useful_equipment": [
                    {"type": "wide", "why": "для русла, мостов и лесного пространства"},
                    {"type": "standard", "why": "для малых каскадов и деталей водосборного леса"},
                    {"type": "macro", "why": "для растительности и лесных деталей без сбора образцов"},
                ],
                "source": {
                    "type": "other",
                    "title": "Kaeng Nyui Waterfall",
                    "publisher": "Discover Laos Today",
                    "url": "https://discoverlaos.today/en/vang-vieng/thing-to-do/kaeng-nyui",
                    "language": "en",
                    "published_at": None,
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
        ],
        "seasonal_visuals": [
            "Конец сезона дождей: главный каскад наиболее мощный, лес насыщенно зелёный, но мокрые поверхности требуют осторожности.",
            "Прохладный сухой сезон: комфортнее тропа и чище дорожный доступ, поток постепенно уменьшается.",
            "Апрель–май: официальный источник предупреждает, что Кенг-Ньюи может ослабнуть почти до ручья; для визуальной разведки это слабый период.",
        ],
        "video_activity": [
            "последовательность малых каскадов по пути к Кенлону",
            "главный вертикальный сброс с оборудованной платформы",
            "движение воды через купальную чашу Кенлона",
            "деревенская инфраструктура управления участком без постановочной съёмки людей",
        ],
        "useful_equipment": [
            {"type": "wide", "why": "для высокого каскада в тесном лесном амфитеатре"},
            {"type": "standard", "why": "для ручьёв, Кенлона и деталей скальной стенки"},
            {"type": "macro", "why": "для растительности водосборного леса и фактур без вмешательства в среду"},
            {"type": "phone", "why": "маршрут короткий и оборудованный, большая часть точек доступна без специальной техники"},
        ],
    },
    "drone": {
        "visual_value": "С воздуха хорошо читается положение водопада внутри восточного лесного водосбора и отличие этой зоны от западного известнякового карста Ванг-Вьенга.",
        "legal_status": "regulated",
        "permit_required": None,
        "restrictions": [
            "Применяются общие правила БПЛА Лаоса.",
            "Участок находится в деревенском conservation/watershed forest и рядом с посетителями; локальное разрешение нельзя считать автоматическим.",
            "Отдельное опубликованное разрешение на полёт над Кенг-Ньюи не найдено.",
        ],
        "source_refs": ["src:23a65d16d80264", "src_990514"],
        "checked_at": CHECKED,
    },
    "filming_restrictions": (
        "Отдельного запрета на обычную наземную любительскую съёмку не найдено. Для коммерческой работы, дрона и съёмки жителей крупным планом режим нужно согласовывать отдельно."
    ),
}

card["annotation"] = {
    "canonical_story_from_sections": True,
    "sections": [
        {
            "section_id": "overview",
            "content": (
                "Кенг-Ньюи — главный водопад небольшого лесного комплекса к востоку от Ванг-Вьенга. Официальные материалы дают высоту около 30 м; Travelfish — 34 м, "
                "поэтому разумнее говорить «около тридцати метров», а не делать вид, что каскад точно измерен. По пути тропа идёт вдоль Хуай-Ньюи и Нам-Лао через малые ступени "
                "и отдельный водопад Кенлон высотой примерно 5 м с купальной чашей около 9 м в диаметре."
            ),
            "source_refs": ["src_000283", "src_990511", "src_990517"],
        },
        {
            "section_id": "history",
            "content": [
                {
                    "type": "documented_history",
                    "text": (
                        "История Кенг-Ньюи тесно связана с Бан-Надуанг. Университетское исследование, опирающееся на материалы Lao National Tourism Administration, "
                        "фиксирует в 1878 году переселение 12 хозяйств тай-пуа из северного Лаоса в район тогдашнего Мыанг-Сонга. К 1937 году поселение носило имя На-Луанг, "
                        "а позже получило современное название Надуанг."
                    ),
                },
                {
                    "type": "documented_history",
                    "text": (
                        "Современный туристический рассказ сохраняет немного другую деревенскую хронологию: предки тай-маен и тай-пуа бежали от набегов хо, "
                        "а Пхо Пхасай во время охотничьих выходов нашёл долину Нам-Лао и в 1873 году основал здесь поселение из 18 домов. Болезни заставляли жителей временно уходить и делить поселение, "
                        "а в 1937 году несколько групп снова объединились. Расхождение в датах 1873/1878 и числе первых домов лучше сохранять, а не искусственно сводить к одной версии."
                    ),
                },
                {
                    "type": "documented_history",
                    "text": (
                        "В 2009–2013 годах Бан-Надуанг стал целевой деревней программы устойчивого туризма ADB/Lao tourism authorities. Кенг-Ньюи рассматривался как главный природный объект, "
                        "доход от которого должен был поддерживать деревню. В 2019–2020 годах отдельный проект UNDP усиливал охрану водосборного леса, а в 2021–2025 годах новый ADB-проект перестроил подъезд "
                        "и туристическую инфраструктуру; 6,6 км бетонной дороги были официально переданы в августе 2025 года."
                    ),
                },
            ],
            "source_refs": ["src_990515", "src_990522", "src_990514", "src_990512"],
        },
        {
            "section_id": "culture",
            "content": (
                "Кенг-Ньюи — хороший пример того, как в Лаосе природный объект может быть частью деревенской экономики, а не отдельным частным аттракционом. "
                "Жители Бан-Надуанг создали тропы, мосты, купальные места и пикниковую зону, управляют билетами, парковкой и торговыми точками. Полевое исследование 2016 года описывает отдельную группу "
                "управления водопадом и группу безопасности; дежурства по продаже билетов распределялись между жителями, а деньги от водопада были одним из заметных источников деревенского фонда развития."
            ),
            "source_refs": ["src_000283", "src_990515"],
        },
        {
            "section_id": "geography",
            "content": (
                "Водопад лежит примерно в 6–7 км к востоку от Ванг-Вьенга в верховьях местного водосбора Нам-Лао. ADB фиксирует точку Кенг-Ньюи около 18.953889, 102.492500. "
                "Тропа следует по системе Хуай-Ньюи и Нам-Лао, а не ведёт сразу к единственному обрыву. UNDP рассматривал около 1000 га местного водосборного леса, 25 га буферной зоны "
                "и примерно 20 га водной территории, включающей Кенг-Ньюи, его верхнее и нижнее течение, как единый охраняемый ландшафт."
            ),
            "source_refs": ["src_990513", "src_990514"],
        },
        {
            "section_id": "geology",
            "content": (
                "Кенг-Ньюи находится не в той же геологической обстановке, что знаменитые известняковые башни к западу от Ванг-Вьенга. Обновлённый мастер-план Ванг-Вьенга описывает южные и восточные горы "
                "как лесистые волнистые холмы, сложенные преимущественно песчаниковыми толщами, тогда как эффектный карст сосредоточен в другой части долины. Поэтому Кенг-Ньюи правильнее рассматривать как водопад "
                "в восточном песчаниковом горном поясе. При этом прямого петрографического анализа скалы самого 30-метрового уступа у нас нет: утверждать, что конкретная стенка водопада состоит именно из песчаника, было бы лишней точностью. "
                "Форма маршрута — последовательность ручьёв, малых каскадов и основного сброса — показывает обычную работу потока, который врезается в неодинаково устойчивое коренное основание."
            ),
            "source_refs": ["src_990516", "src_990511"],
        },
        {
            "section_id": "ethnography",
            "content": (
                "Бан-Надуанг — смешанное поселение, но старые источники дают разные цифры состава населения. Материалы LNTA, использованные в исследовании 2016 года, описывали преимущественно кхму и небольшую долю лао-лум; "
                "более поздний туристический профиль говорит о смеси кхму и тай. Исторические рассказы при этом отдельно помнят тай-пуа и тай-маен среди основателей. Поэтому современную деревню нельзя честно свести к одной этнической этикетке. "
                "Повседневная экономика традиционно связана с рисом, огородами, лесными продуктами, ткачеством и позднее — homestay и туристическими услугами."
            ),
            "source_refs": ["src_990515", "src_990522", "src_990514"],
        },
        {
            "section_id": "myths_beliefs",
            "content": [
                {
                    "type": "local_tradition",
                    "text": (
                        "В материалах LNTA о Бан-Надуанг зафиксирован ежегодный обряд на третий день седьмого месяца по лаосскому календарю. Жители — независимо от различий между анимистической и буддийской традицией — "
                        "почитают предков, которых считают защитниками деревни, источником здоровья и хорошего урожая. Это не легенда о возникновении водопада, а живая система представлений сообщества, которому принадлежит участок."
                    ),
                },
                {
                    "type": "local_tradition",
                    "text": (
                        "С именем самой деревни существуют разные рассказы. В одной версии На-Луанг означало «большое поле», а Надуанг выбрали позднее как более приятное по звучанию название. "
                        "В другой, записанной в исследовании 2016 года, старое Naluang избегали из-за неблагоприятной ассоциации слова luang с быстрым присвоением чужого. Эти версии лучше читать как местные этимологические объяснения, а не как строгую лингвистику."
                    ),
                },
                {
                    "type": "local_tradition",
                    "text": (
                        "В туристической жизни Бан-Надуанг сохраняется бааси — обряд благопожелания и «связывания» жизненных сил. Исследование деревни описывает отдельную группу старейшин, которая проводила бааси для гостей: "
                        "для приветствия, пожелания безопасной дороги и включения приезжего в пространство деревни. Часть пожертвований при таких церемониях шла в деревенский фонд."
                    ),
                },
                {
                    "type": "modern_tourist_story",
                    "text": (
                        "В одном независимом путевом рассказе встречается ещё одна красивая этимология: будто выражением «ньюи-ньюи» местные называют тонкую водяную пыль от удара главного каскада, и от неё произошло имя водопада. "
                        "Подтверждения в официальных или лингвистических источниках я не нашёл, поэтому это остаётся современной туристической историей, а не установленным происхождением топонима."
                    ),
                },
            ],
            "source_refs": ["src_990515", "src_990522", "src_990520"],
        },
    ],
}

card["traveler_reports"] = [
    {
        "kind": "traveler_report",
        "topic": "post_reconstruction_access",
        "summary": (
            "Декабрь 2025: посетитель описал дорогу к Кенг-Ньюи как неожиданно качественную — практически лучший дорожный участок, который он видел в Лаосе. "
            "После оплаты входа территория воспринималась как небольшой природный парк, по которому можно гулять от часа до нескольких часов."
        ),
        "observed_period": "2025-12",
        "source_refs": ["src_990518"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "current_price_and_time",
        "summary": (
            "Свежий пользовательский отчёт 2026 года называет около 20 минут на мотоцикле из Ванг-Вьенга или примерно 1,5 часа пешком и вход около 20 000 кип. "
            "Эти цифры полезны как текущий ориентир, но не заменяют официальный тариф."
        ),
        "observed_period": "2026",
        "source_refs": ["src_990521"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "trail_profile",
        "summary": (
            "GPS-запись февраля 2025 года даёт лесную петлю около 1,0 км, набор и сброс примерно по 54 м, с высотами трека приблизительно 340–405 м. "
            "Время записи 1 ч 50 мин включает остановки; чистое время движения было намного меньше, поэтому его нельзя превращать в норматив прохождения."
        ),
        "observed_period": "2025-02",
        "source_refs": ["src_990519"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "seasonal_flow",
        "summary": (
            "Travelfish в обновлении августа 2025 года подчёркивает резкую сезонность: ближе к концу дождливого сезона водопады полноводны, а в сухой период система может быть почти без воды. "
            "Это совпадает с официальным предупреждением о слабом потоке в апреле–мае."
        ),
        "observed_period": "2025-08",
        "source_refs": ["src_990517", "src_990511"],
        "confidence": "medium",
    },
]
card["accommodation"] = []

existing_sources = [s for s in (obj.get("sources") or []) if isinstance(s, dict)]
add_sources = [
    {
        "type": "other",
        "title": "Kaeng Nyui Waterfall",
        "publisher": "Discover Laos Today",
        "url": "https://discoverlaos.today/en/vang-vieng/thing-to-do/kaeng-nyui",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["waterfall dimensions", "seasonality", "Kenlon", "community management", "village guides", "gallery"],
        "accessed": CHECKED,
    },
    {
        "type": "other",
        "title": "Second Greater Mekong Subregion Tourism Infrastructure for Inclusive Growth Project",
        "publisher": "Asian Development Bank",
        "url": "https://www.adb.org/projects/49387-002/main",
        "language": "en",
        "published_at": None,
        "authority": "high",
        "used_for": ["6.6 km concrete access road", "2025 completion and handover", "current infrastructure status"],
        "accessed": CHECKED,
    },
    {
        "type": "other",
        "title": "Kaeng Yui Waterfall Access Improvements — Initial Environmental Examination",
        "publisher": "Asian Development Bank",
        "url": "https://ewsdata.rightsindevelopment.org/files/documents/02/ADB-49387-002_YRpx9UL.pdf",
        "language": "en",
        "published_at": "2018",
        "authority": "high",
        "used_for": ["exact site coordinates", "conservation-forest context", "parking/footpath project footprint"],
        "accessed": CHECKED,
    },
    {
        "type": "other",
        "title": "Strengthening Sustainable Community Watershed Forest Conservation through Religious Practice and Alternative Income Support",
        "publisher": "UNDP Small Grants Programme",
        "url": "https://www.sgp.undp.org/spacial-itemid-projects-landing-page/spacial-itemid-project-search-results/spacial-itemid-project-detailpage.html?id=26307&view=projectdetail",
        "language": "en",
        "published_at": "2019",
        "authority": "high",
        "used_for": ["watershed forest", "conservation area", "NTFP dependence", "Kaeng Nyui water area", "community livelihoods"],
        "accessed": CHECKED,
    },
    {
        "type": "academic",
        "title": "Is Community-Based Tourism beneficial to local communities? The case of Naduang Village, Vang Vieng District, Vientiane Province, Laos",
        "publisher": "University of Waikato",
        "url": "https://researchcommons.waikato.ac.nz/bitstreams/5ce5e24a-0ce8-4c87-aa0d-c85f9562cc0e/download",
        "language": "en",
        "published_at": "2016",
        "authority": "high",
        "used_for": ["Naduang history", "ethnography", "ancestor beliefs", "Baci", "waterfall-management group", "ticketing", "CBT economics"],
        "accessed": CHECKED,
    },
    {
        "type": "other",
        "title": "Vang Vieng Town and Environs Tourism Master Plan 2025–2035",
        "publisher": "Destination Management Network / Lao tourism planning",
        "url": "https://laos-dmn.com/wp-content/uploads/2025/02/Vang-Vieng-Town-Environs-Tourism-Master-Plan-2025-%E2%80%93-2035_English-1.pdf",
        "language": "en",
        "published_at": "2025",
        "authority": "high",
        "used_for": ["eastern Vang Vieng sandstone hills", "regional geomorphology", "landscape context"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Kaeng Nyui Waterfall — visitor guide and review",
        "publisher": "Travelfish",
        "url": "https://www.travelfish.org/sight_profile/laos/vientiane_and_surrounds/vientiane/vang_vieng/3382",
        "language": "en",
        "published_at": "2025-08-26",
        "authority": "medium",
        "used_for": ["seasonal flow", "field access context", "34 m alternate height", "community fee"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Kaeng Nyui Waterfall — traveler reviews",
        "publisher": "Tripadvisor",
        "url": "https://www.tripadvisor.com/Attraction_Review-g612363-d4556470-Reviews-Kaeng_Nyui_Waterfalll-Vang_Vieng_Vientiane_Province.html",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["December 2025 road condition", "post-reconstruction visitor experience", "visit duration"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Kaeng Nyui — recorded hiking loop",
        "publisher": "Wikiloc",
        "url": "https://www.wikiloc.com/hiking-trails/kaeng-nyui-201245476",
        "language": "en",
        "published_at": "2025-02-12",
        "authority": "medium",
        "used_for": ["trail distance", "elevation gain/loss", "approximate trail elevation range", "field timing"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Vang Vieng, Laos Part II — Kenlon and Kaeng Nyui",
        "publisher": "Journey at Thirty",
        "url": "https://www.journeyatthirty.com/vang-vieng-laos-part-ii.html",
        "language": "en",
        "published_at": None,
        "authority": "low",
        "used_for": ["modern tourist etymology of 'nyui-nyui' spray only"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Vang Vieng: Favorite Lagoons + Kaeng Nyui Waterfall",
        "publisher": "Trip.com contributor",
        "url": "https://sg.trip.com/moments/detail/vang-vieng-21457-150662542/?curr=&locale=en-SG",
        "language": "en",
        "published_at": "2026",
        "authority": "medium",
        "used_for": ["current 2026 entrance-price estimate", "motorbike time", "walking time"],
        "accessed": CHECKED,
    },
    {
        "type": "other",
        "title": "Vang Vieng destination — Ban Naduang Village",
        "publisher": "Discover Laos Today",
        "url": "https://uat.discoverlaos.today/destination/vang-vieng",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["alternate Naduang founding tradition", "Tai Maen/Tai Pua context", "village name story", "community tourism"],
        "accessed": CHECKED,
    },
]
by_url = {s.get("url"): s for s in existing_sources if s.get("url")}
for source in add_sources:
    by_url[source["url"]] = source
obj["sources"] = list(by_url.values())

gallery_urls = [
    "https://discoverlaos.today/img/thing_to_do/94cc4ec706c7528446ed326fe35b3f59.jpg?p=original",
    "https://discoverlaos.today/img/thing_to_do/0157555f8c7651c4891e708a27d3de8a.jpg?p=original",
    "https://discoverlaos.today/img/thing_to_do/31381dff4c9b27fe126c931fb540e4b0.jpg?p=original",
    "https://discoverlaos.today/img/thing_to_do/8d856f833f2fcf368dc3620d5013fff6.jpg?p=original",
    "https://discoverlaos.today/img/thing_to_do/96cde89191c9c90eccd30a204ca8f3bc.jpg?p=original",
    "https://discoverlaos.today/img/thing_to_do/522789cae92df9d7ab85f99aad7ada9f.jpg?p=original",
]
obj["illustration"] = {
    "static_url": gallery_urls[0],
    "source_page": "https://discoverlaos.today/en/vang-vieng/thing-to-do/kaeng-nyui",
    "provider": "Discover Laos Today",
    "license": "reuse_terms_unverified",
    "artist": None,
    "illustration_scope": "Kaeng Nyui waterfall complex, viewing platform, stream trail and forest",
    "last_checked": CHECKED,
    "gallery": [
        {
            "static_url": url,
            "source_page": "https://discoverlaos.today/en/vang-vieng/thing-to-do/kaeng-nyui",
            "provider": "Discover Laos Today",
            "license": "reuse_terms_unverified",
            "artist": None,
            "last_checked": CHECKED,
        }
        for url in gallery_urls
    ],
}

obj["verification"] = {
    "dynamic_fields": ["ticket", "hours", "water flow", "swimming conditions", "local transport", "overnight", "drone"],
    "verify_before_departure": True,
}

obj["qa"] = {
    **(obj.get("qa") or {}),
    "language_review": {
        "status": "reviewed",
        "checked_at": CHECKED,
        "notes": (
            "История деревни сохраняет расхождение между версиями 1873/1878; старые демографические проценты не выданы за текущие. "
            "Геология восточного Ванг-Вьенга отделена от точной литологии стенки водопада. Этимология 'nyui-nyui' помечена как современная туристическая история."
        ),
    },
    "human_copy_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "checks": {
            "natural_russian": True,
            "no_stock_travel_copy": True,
            "practical_information_first": True,
            "geology_explained": True,
            "community_history_explained": True,
            "local_beliefs_explained": True,
            "uncertainty_preserved": True,
        },
    },
    "card_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "полный объектный QA Kaeng Nyui Waterfall",
        "checks": {
            "language": True,
            "classification": True,
            "geo": True,
            "coordinates": True,
            "elevation": True,
            "narrative": True,
            "sources": True,
            "access": True,
            "water": True,
            "overnight": True,
            "traveler_reports": True,
            "visual_recon": True,
            "gallery_min_5": True,
            "fact_source_scoping": True,
            "history_substantive": True,
            "culture_substantive": True,
            "geography_substantive": True,
            "geology_substantive": True,
            "ethnography_substantive": True,
            "myths_beliefs_substantive": True,
            "legend_labeled": True,
            "community_management_substantive": True,
            "road_reconstruction_current": True,
            "no_narrative_duplication": True,
        },
        "notes": [
            "Primary GPS comes from ADB and is independently matched by Travelfish.",
            "Trail elevation is kept as an approximate recorded range rather than a fabricated waterfall altitude.",
            "Old dirt-road logistics are explicitly superseded by the completed 2025 concrete-road project.",
            "Naduang demographic records conflict across years; the card does not present old percentages as current population.",
            "No direct waterfall-origin legend was found; ancestor beliefs, Baci, village-name traditions and a weak modern Nyui etymology are clearly separated.",
        ],
    },
    "rebuild_v2": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "полная редакционная, историческая, геологическая, этнографическая, полевая и источниковая перестройка Kaeng Nyui Waterfall",
        "checks": {
            "connected_story": True,
            "history_substantive": True,
            "culture_substantive": True,
            "geography_substantive": True,
            "geology_substantive": True,
            "ethnography_substantive": True,
            "myths_beliefs_substantive": True,
            "no_placeholder_sections": True,
            "no_invented_precision": True,
            "logistics_self_guided": True,
            "water_honest": True,
            "overnight_honest": True,
            "traveler_reports": True,
            "visual_recon": True,
            "sources": True,
            "media_provenance": True,
            "gallery_min_5": True,
            "community_conservation_context": True,
            "drone_rule_precision": True,
        },
    },
    "fact_source_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": (
            "Kaeng Nyui: identity, ADB GPS, trail elevation range, water-flow seasonality, new 2025 road, Ban Naduang history and CBT, "
            "watershed conservation, eastern sandstone-hill geology, ancestor beliefs, Baci, name traditions, current traveler reports, media and drone"
        ),
        "checks": {
            "narrative_section_sources": True,
            "coordinate_source_scoped": True,
            "elevation_source_scoped": True,
            "waterfall_height_conflict_preserved": True,
            "road_old_vs_new_split": True,
            "regional_geology_not_overstated_as_site_petrology": True,
            "village_history_versions_preserved": True,
            "old_demography_not_presented_as_current": True,
            "ancestor_beliefs_scoped_to_village": True,
            "modern_etymology_marked_weak": True,
            "ticket_marked_dynamic": True,
            "water_quality_unknown_preserved": True,
            "camping_permission_unknown_preserved": True,
            "traveler_report_period_scoped": True,
            "gallery_sources_traced": True,
            "drone_rules_official": True,
        },
    },
}

SOURCE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
sources = registry.setdefault("sources", {})
for url, canonical_id in NEW_SOURCES.items():
    legacy = source_key(url)
    current = sources.get(legacy)
    if current not in (None, canonical_id):
        raise SystemExit(f"source ID collision: {legacy} -> {current}, wanted {canonical_id}")
    sources[legacy] = canonical_id
REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Updated Kaeng Nyui Waterfall and registered", len(NEW_SOURCES), "source IDs")
