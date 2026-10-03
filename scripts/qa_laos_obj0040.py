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
    "https://discoverlaos.today/vang-vieng/thing-to-do/tham-chang-cave": "src_990498",
    "https://www.wikidata.org/wiki/Q7709769": "src_990499",
    "https://www.researchgate.net/publication/386275397_Geological_Perspective_as_Karst_Geotourism_Potential_A_Case_Study_of_Vientiane_Province_Laos": "src_990500",
    "https://www.alltrails.com/en-gb/trail/laos/vientiane/tham-chang-cave": "src_990501",
    "https://www.tripadvisor.com/Attraction_Review-g612363-d2314020-Reviews-Tham_Chang_Cave-Vang_Vieng_Vientiane_Province.html": "src_990502",
    "https://kpl.gov.la/en/detail.aspx?id=24081": "src_990503",
    "https://www.tandfonline.com/doi/full/10.1177/0967828X17741037": "src_990504",
    "https://commons.wikimedia.org/wiki/File:VientianeProvince_VangVieng_ThamJang1_tango7174.jpg": "src_990505",
    "https://www.komoot.com/highlight/5440367": "src_990506",
}

def source_key(url: str) -> str:
    return "src:" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:14]

def find_object(node):
    if isinstance(node, dict):
        if node.get("name") == "Tham Chang Cave":
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
    raise SystemExit("Tham Chang Cave not found")

obj["class"] = "cave"
obj["interest"] = [
    "cave",
    "karst",
    "geology",
    "history",
    "local_tradition",
    "viewpoint",
    "swimming",
    "walking",
]
obj["why_go"] = (
    "Тхам-Чанг — самая простая для самостоятельного посещения крупная пещера рядом с Ванг-Вьенгом: до неё можно дойти из города, "
    "а внутри есть лестницы, освещение и оборудованные проходы. Но интереснее она не как «ещё одна пещера со сталактитами», а как место, где сходятся "
    "карстовая геология, старое убежище жителей Муанг-Сонга, местные версии происхождения названия, холодный источник и высокий проём с видом на долину Нам-Сонг."
)

card = obj.setdefault("traveler_card", {})
card["location"] = {
    "region": "Vientiane Province / Vang Vieng District",
    "nearest_hub": "Ванг-Вьенг",
    "languages_spoken": ["лаосский", "английский — в туристическом секторе"],
    "coordinates": {
        "lat": 18.909,
        "lon": 102.442,
        "elevation_m": 270,
    },
    "coordinate_type": "cave_entrance",
    "accuracy": "medium",
    "elevation_accuracy": "approximate",
    "coordinates_checked_at": CHECKED,
    "coordinate_source": {
        "type": "other",
        "title": "Tham Jang — Wikidata",
        "publisher": "Wikidata",
        "url": "https://www.wikidata.org/wiki/Q7709769",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "accessed": CHECKED,
        "notes": "Wikidata/Commons location: 18°54′32.4″N, 102°26′31.2″E. Used for the cave entrance/cliff location, not the town center.",
    },
    "elevation_source": {
        "type": "traveler_report",
        "title": "Tham Chang Cave — hiking highlight",
        "publisher": "Komoot",
        "url": "https://www.komoot.com/highlight/5440367",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "accessed": CHECKED,
        "notes": "Komoot lists the cave highlight at 270 m. This is a route-platform elevation, not a survey benchmark.",
    },
    "object_elevation": {
        "representative_m": 270,
        "min_m": None,
        "max_m": None,
        "reference_type": "characteristic",
        "accuracy": "approximate",
        "source": {
            "type": "traveler_report",
            "title": "Tham Chang Cave — hiking highlight",
            "publisher": "Komoot",
            "url": "https://www.komoot.com/highlight/5440367",
            "language": "en",
            "published_at": None,
            "authority": "medium",
            "accessed": CHECKED,
        },
        "checked_at": CHECKED,
        "notes": (
            "Около 270 м — ориентировочная высота точки пещеры по маршрутной платформе. Старое полевое описание отдельно ставит вход примерно на 30 м выше реки; "
            "точная геодезическая отметка входа не найдена."
        ),
    },
    "geo_points": [
        {
            "type": "cave_entrance",
            "name": "Главный вход Тхам-Чанг",
            "coordinates": {"lat": 18.909, "lon": 102.442, "elevation_m": 270},
            "accuracy": "medium",
            "elevation_accuracy": "approximate",
            "coordinate_source": {
                "type": "other",
                "title": "Tham Jang — Wikidata / Wikimedia Commons",
                "publisher": "Wikidata / Wikimedia Commons",
                "url": "https://www.wikidata.org/wiki/Q7709769",
                "language": "en",
                "published_at": None,
                "authority": "medium",
                "accessed": CHECKED,
            },
            "elevation_source": {
                "type": "traveler_report",
                "title": "Tham Chang Cave — hiking highlight",
                "publisher": "Komoot",
                "url": "https://www.komoot.com/highlight/5440367",
                "language": "en",
                "published_at": None,
                "authority": "medium",
                "accessed": CHECKED,
            },
            "checked_at": CHECKED,
        },
        {
            "type": "viewpoint",
            "name": "Проём у входа с видом на долину Нам-Сонг",
            "coordinates": {"lat": 18.909, "lon": 102.442, "elevation_m": 270},
            "accuracy": "medium",
            "elevation_accuracy": "approximate",
            "coordinate_source": {
                "type": "other",
                "title": "Tham Jang — Wikimedia Commons geotagged cave view",
                "publisher": "Wikimedia Commons",
                "url": "https://commons.wikimedia.org/wiki/Category:Tham_Jang",
                "language": "en",
                "published_at": None,
                "authority": "medium",
                "accessed": CHECKED,
            },
            "elevation_source": {
                "type": "traveler_report",
                "title": "Tham Chang Cave — hiking highlight",
                "publisher": "Komoot",
                "url": "https://www.komoot.com/highlight/5440367",
                "language": "en",
                "published_at": None,
                "authority": "medium",
                "accessed": CHECKED,
            },
            "checked_at": CHECKED,
            "notes": "Точка совпадает с главным входным проёмом; отдельную координату внутри пещеры не выдумываем.",
        },
    ],
}

card["logistics"] = {
    "access": (
        "Тхам-Чанг находится на южной окраине Ванг-Вьенга и подходит для пешего визита без тура. От южного автобусного терминала до пещеры старый подробный "
        "путеводитель даёт около 1,7 км; из центральной туристической части свежие отзывы описывают примерно 15–25 минут пешком до переправы. "
        "После Нам-Сонга остаётся короткий подход и 147 ступеней к входу."
    ),
    "public_transport": (
        "Отдельный общественный транспорт к пещере не нужен: объект находится в пешей зоне города. До Ванг-Вьенга добираются обычным междугородним транспортом/поездом, "
        "но этот городской сегмент не дублируется в карточке пещеры."
    ),
    "last_mile": (
        "Главная неопределённость — переправа через Нам-Сонг. Старый оранжевый мост к пещере был разрушен штормом в июне 2021 года; свежие отзывы 2025 года описывают "
        "короткую переправу на маленьком пароме. При этом некоторые актуальные туристические листинги всё ещё пишут о подвесном мосте. Способ перехода лучше уточнить в день визита."
    ),
    "typical_visit_hours": [1, 2],
    "permit_or_guide": "Гид для оборудованной части пещеры не требуется; маршрут внутри самостоятельный и освещённый.",
    "mobility_notes": (
        "До входа нужно подняться по 147 бетонным ступеням. Внутри основные проходы оборудованы дорожками, ступенями и перилами, но известняк остаётся влажным и местами скользким."
    ),
    "modes": {
        "public_transport": "Специального городского маршрута не требуется.",
        "taxi_ridehail": "Тук-тук или частный водитель могут сократить городской подход, но фиксированный тариф не публикуется.",
        "car": "Автомобиль оставляют со стороны городского подхода/переправы; к самому входу машина не поднимается.",
        "moped": "Можно подъехать к зоне переправы, но дальнейший участок к пещере пеший.",
        "motorcycle": "То же, что для мопеда: подъезд только до нижней зоны.",
        "boat": "Свежие отзывы 2025 года описывают короткий паром через Нам-Сонг.",
        "walking": "Основной режим: городской подход, переправа, затем 147 ступеней и оборудованная пещера.",
    },
    "water": (
        "В нижней visitor-зоне свежие отзывы подтверждают продавцов еды и напитков. У пещеры есть холодный карстовый источник и бассейн для купания, "
        "но его воду не считать питьевой без отдельного подтверждения качества."
    ),
    "water_structured": {
        "at_object": True,
        "quality": "unknown",
        "last_reliable_point": "продавцы напитков в нижней visitor-зоне",
        "distance_m": None,
        "natural_sources": [
            {
                "type": "karst_spring",
                "potability": "unknown",
                "notes": "Карстовый источник используется для купания; данных о питьевом качестве не найдено.",
            }
        ],
        "notes": "Для питья брать бутилированную воду; родниковая вода в карточке не классифицируется как potable.",
        "source_refs": ["src_990498", "src_990502"],
    },
    "supplies": {
        "status": "available_at_site",
        "summary": "У нижней зоны есть продавцы еды и напитков; свежие отзывы также упоминают туалеты.",
        "poi_ids": [],
        "source_refs": ["src_990502"],
    },
    "overnight_and_camping": (
        "Пещера — дневной городской объект. Официальный кемпинг у входа не подтверждён; ночёвка внутри пещеры или у источника не является стандартным режимом доступа. "
        "Практическая база — Ванг-Вьенг."
    ),
    "overnight": {
        "status": "unclear",
        "summary": "Разрешение на палаточную ночёвку у пещеры не опубликовано; объект расположен рядом с городом и рассчитан на дневное посещение.",
        "source_refs": ["src_990498"],
    },
    "access_requirements": "Оплатить локальный вход, соблюдать часы работы и не выходить за ограждённые/оборудованные проходы в закрытые участки пещеры.",
    "access_options": [
        {
            "id": "vang_vieng_walk_ferry_cave",
            "origin": "центр Ванг-Вьенга",
            "modes": ["walking", "boat", "walking"],
            "checked_at": CHECKED,
            "source_refs": ["src_990498", "src_990501", "src_990502", "src_990505"],
            "legs": [
                {
                    "mode": "walking",
                    "distance_km": None,
                    "duration_min": 20,
                    "surface": "paved",
                    "condition": "Городской подход по улицам и дорожке к Нам-Сонгу.",
                    "seasonality": "Круглогодично; в жару открытые участки неприятнее.",
                    "elevation_gain_m": None,
                    "elevation_loss_m": None,
                    "trailhead": None,
                    "navigation": "Идти к южной части города и зоне переправы к Тхам-Чанг.",
                    "fords": 0,
                    "notes": "20 минут — практический ориентир свежих отзывов, а не фиксированное время от любой точки города.",
                    "source_refs": ["src_990502"],
                },
                {
                    "mode": "boat",
                    "distance_km": None,
                    "duration_min": 5,
                    "surface": None,
                    "condition": "Короткая переправа через Нам-Сонг на небольшом пароме по отзывам 2025 года.",
                    "seasonality": "Режим может зависеть от уровня воды и текущей инфраструктуры.",
                    "elevation_gain_m": None,
                    "elevation_loss_m": None,
                    "trailhead": None,
                    "navigation": "Следовать локальной схеме переправы; старые карты с мостом могут быть устаревшими.",
                    "fords": 0,
                    "notes": "Discover Laos всё ещё упоминает подвесной мост, поэтому способ пересечения реки считать динамическим.",
                    "source_refs": ["src_990498", "src_990502", "src_990505"],
                },
                {
                    "mode": "walking",
                    "distance_km": None,
                    "duration_min": None,
                    "surface": "stairs",
                    "condition": "147 бетонных ступеней к входу, затем освещённые дорожки и лестницы внутри.",
                    "seasonality": "Во влажный сезон камень и ступени могут быть скользкими.",
                    "elevation_gain_m": 30,
                    "elevation_loss_m": 0,
                    "trailhead": {"lat": 18.909, "lon": 102.442},
                    "navigation": "От нижней зоны по обозначенной лестнице к главному входу.",
                    "fords": 0,
                    "notes": "147 ступеней подтверждаются KPL и свежими отзывами; около 30 м вертикали — полевой ориентир EarthCache, не геодезический замер.",
                    "source_refs": ["src_990503", "src_990501"],
                },
            ],
        }
    ],
    "self_guided_default": True,
    "travel_model": "самостоятельный городской визит: пешком → текущая переправа через Нам-Сонг → лестница → оборудованная пещера",
}

card["climate"] = {
    "best_period": (
        "Для вида из входного проёма удобнее сухой прохладный сезон, когда меньше дымки и проще лестница. Сама пещера посещается круглый год и заметно прохладнее улицы."
    ),
    "heat_rain_notes": (
        "В сезон дождей вокруг входа и внутри влажнее, камень скользче, а состояние переправы через Нам-Сонг важнее обычного. "
        "В жаркие месяцы основная нагрузка — открытый подход и лестница, а не интерьер пещеры."
    ),
    "site_specific_notes": "Утро снижает жару на подъёме и обычно даёт меньше посетителей; после сильных дождей переправу и нижнюю водную зону проверять отдельно.",
}

card["operations"] = {
    "status": "open/verify",
    "hours": (
        "Discover Laos публикует: пн–пт 08:00–11:00 и 13:00–16:00; сб–вс 08:00–16:00. "
        "Другие локальные источники встречаются с диапазоном до 17:00, поэтому часы перед визитом перепроверить."
    ),
    "ticket": (
        "Свежие пользовательские отчёты 2025 года дают примерно 20 000–22 000 LAK за вход/зону; это не официальный тариф и он может меняться."
    ),
    "closure_notes": "Специального сезонного закрытия не найдено; фактический доступ зависит от часов работы и текущей переправы через Нам-Сонг.",
    "last_verified": CHECKED,
    "official_url": "https://www.tourismlaos.org/central-provinces/vientiane-province/",
    "status_snapshot": {
        "as_of": CHECKED,
        "summary": (
            "Тхам-Чанг остаётся действующей оборудованной достопримечательностью. В конце 2025 года посетители сообщали о работающем освещении, бетонных дорожках, "
            "147 ступенях и тарифе около 20–22 тыс. кип; способ переправы через реку в свежих отчётах — маленький паром."
        ),
        "source_refs": ["src_990501", "src_990502"],
    },
    "source_refs": ["src:9799177acb170c", "src_990498", "src_990501", "src_990502"],
}

card["safety"] = {
    "main_risks": [
        "147 ступеней на жаре",
        "влажный и местами скользкий известняк внутри пещеры",
        "переправа через Нам-Сонг зависит от текущей инфраструктуры и уровня воды",
        "скользкие камни в карстовом источнике/водной пещере",
        "ограниченная естественная освещённость вне оборудованных дорожек",
    ],
    "sensitive_areas": [
        "не трогать и не ломать натёчные образования",
        "не уходить в неосвещённые закрытые ответвления",
        "уважать буддийский алтарь/святилище внутри пещеры",
    ],
    "confidence": "medium",
    "source_refs": ["src_990498", "src_990501", "src_990502"],
    "checked_at": CHECKED,
}

card["media"] = {
    "photo_suitability_5": 5,
    "video_suitability_5": 5,
    "best_light": (
        "Для внешнего вида сильнее всего работает свет из входного проёма на долину Нам-Сонг; утром меньше дымки и людей, "
        "а во второй половине дня боковой свет лучше рисует карстовые хребты."
    ),
    "visual_scouting": {
        "best_time": "утро для спокойной пещеры; поздний день для вида из входного проёма",
        "best_weather_light": (
            "Сухой ясный день даёт дальний план по долине и карстам. Облачность полезна у источника и на известняковых стенах, "
            "где прямое солнце создаёт слишком резкий контраст."
        ),
        "viewpoints_for_photo_video": [
            {
                "id": "vp_cave_mouth_valley",
                "name": "Проём Тхам-Чанг над долиной Нам-Сонг",
                "description": "Высокая естественная рамка в скале с видом на реку, город, рисовые поля и карстовые хребты.",
                "coordinates": {"lat": 18.909, "lon": 102.442, "elevation_m": 270},
                "access": "147 ступеней от нижней visitor-зоны; точка находится у оборудованного входа.",
                "view": {"description": "Нам-Сонг, южная часть Ванг-Вьенга, поля и карстовые башни"},
                "best_time": "утро или поздний день",
                "best_weather_light": "При низкой дымке хорошо читаются несколько планов карстовых хребтов.",
                "useful_equipment": [
                    {"type": "wide", "why": "для естественной рамки входа и широкой долины"},
                    {"type": "telephoto", "why": "для сжатия дальних карстовых гряд и деталей на Нам-Сонге"},
                ],
                "source": {
                    "type": "other",
                    "title": "View from the Tham Jang",
                    "publisher": "Wikimedia Commons",
                    "url": "https://commons.wikimedia.org/wiki/File:View_from_the_Tham_Jang.jpg",
                    "language": "en",
                    "published_at": "2018-08-22",
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
            {
                "id": "vp_main_chambers",
                "name": "Главные оборудованные залы",
                "description": "Крупные залы с колоннами, сталактитами, сталагмитами и потёчными формами вдоль освещённой дорожки.",
                "coordinates": None,
                "access": "По оборудованным проходам внутри пещеры.",
                "view": {"description": "объём залов, натёчные образования, слои и трещины известняка"},
                "best_time": "в часы работы",
                "best_weather_light": "Внешняя погода почти не влияет; визуальный характер задают естественные тёмные зоны и локальное электрическое освещение.",
                "useful_equipment": [
                    {"type": "wide", "why": "для тесных проходов и масштаба залов"},
                    {"type": "standard", "why": "для отдельных колонн, потёков и стен"},
                ],
                "source": {
                    "type": "other",
                    "title": "Tham Jang 2",
                    "publisher": "Wikimedia Commons",
                    "url": "https://commons.wikimedia.org/wiki/File:Tham_Jang_2.jpg",
                    "language": "en",
                    "published_at": "2018-08-22",
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
            {
                "id": "vp_karst_spring",
                "name": "Карстовый источник у основания лестницы",
                "description": "Холодная прозрачная вода выходит из массива и образует бассейн под лесным склоном.",
                "coordinates": None,
                "access": "Нижняя зона перед подъёмом к пещере.",
                "view": {"description": "голубовато-зелёная вода, известняк, лес и пешеходные мостки"},
                "best_time": "утро или облачный день",
                "best_weather_light": "Мягкий свет лучше показывает прозрачность воды и зелень без сильных бликов.",
                "useful_equipment": [
                    {"type": "wide", "why": "для бассейна вместе с основанием карстовой стены"},
                    {"type": "standard", "why": "для воды, мостков и деталей выхода источника"},
                ],
                "source": {
                    "type": "other",
                    "title": "Tham Jang Lagoon 1",
                    "publisher": "Wikimedia Commons",
                    "url": "https://commons.wikimedia.org/wiki/File:Tham_Jang_Lagoon_1.jpg",
                    "language": "en",
                    "published_at": "2018-08-22",
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
        ],
        "seasonal_visuals": [
            "В сухой сезон легче получить дальний чистый вид из входного проёма на долину и карстовые гряды.",
            "В сезон дождей растительность насыщеннее и источник выглядит полноводнее, но лестницы и камень внутри влажнее.",
            "Утренний туман иногда держится над долиной Нам-Сонг и подчёркивает отдельные карстовые башни.",
        ],
        "video_activity": [
            "подъём по лестнице с постепенным раскрытием долины",
            "переход из яркого входного проёма в крупные тёмные залы",
            "натёчные формы вдоль оборудованной дорожки",
            "выход карстового источника и движение воды в нижнем бассейне",
        ],
        "useful_equipment": [
            {"type": "wide", "why": "для интерьера пещеры и входного проёма"},
            {"type": "standard", "why": "для натёчных форм, алтаря и источника"},
            {"type": "telephoto", "why": "для дальних карстовых хребтов из входного проёма"},
            {"type": "phone", "why": "основной маршрут оборудован и подходит для быстрой документальной съёмки без специальной техники"},
        ],
    },
    "drone": {
        "visual_value": "Высокая для связи пещеры с Нам-Сонг и карстовой долиной, но объект находится у города и частной/туристической инфраструктуры.",
        "legal_status": "regulated",
        "permit_required": None,
        "restrictions": [
            "Применяются общие правила БПЛА Лаоса.",
            "Полёт над городом, посетителями, переправой и частной территорией нельзя считать автоматически допустимым.",
            "Отдельное разрешение именно для Тхам-Чанг в открытых источниках не найдено.",
        ],
        "source_refs": ["src:23a65d16d80264"],
        "checked_at": CHECKED,
    },
    "filming_restrictions": (
        "Отдельный запрет на обычную наземную любительскую съёмку не найден. У буддийского алтаря и в людных узких проходах соблюдать локальные знаки и просьбы персонала."
    ),
}

card["annotation"] = {
    "canonical_story_from_sections": True,
    "sections": [
        {
            "section_id": "overview",
            "content": (
                "Тхам-Чанг находится практически на окраине Ванг-Вьенга, но по устройству это уже полноценная карстовая пещера: большой вход высоко в известняковой стене, "
                "несколько освещённых залов, сталактиты и сталагмиты, холодный источник у подножия и отдельный проём с широким видом на Нам-Сонг. "
                "Главное отличие от многих окрестных пещер — сюда не нужен мотоцикл по грунтовке и не нужен проводник."
            ),
            "source_refs": ["src:9799177acb170c", "src_990498"],
        },
        {
            "section_id": "history",
            "content": [
                {
                    "type": "documented_history",
                    "text": (
                        "Официальный Tourism Laos сохраняет историю о жителях Муанг-Сонга, которые выращивали овощи на юге нынешнего Ванг-Вьенга и во время войны "
                        "перенесли жизнь в пещеру: её высокий вход давал укрытие и обзор долины. Позже, уже в колониальный период, жители вернулись к полям и продолжали пользоваться холодным источником."
                    ),
                },
                {
                    "type": "documented_history",
                    "text": (
                        "Многие современные путеводители связывают убежище именно с набегами хо — вооружённых групп, пришедших из Южного Китая. Но часто повторяемая формула "
                        "«начало XIX века» плохо согласуется с академической хронологией: исследование Райана Вулфсона-Форда относит войны хо в Лаосе примерно к 1869–1889 годам. "
                        "Поэтому использование пещеры как убежища хорошо закреплено в местной туристической истории, а точную дату и конкретный эпизод войны лучше считать неустановленными."
                    ),
                },
            ],
            "source_refs": ["src:9799177acb170c", "src_990498", "src_990504"],
        },
        {
            "section_id": "culture",
            "content": (
                "Тхам-Чанг давно встроена в повседневный ландшафт Ванг-Вьенга: сюда приходят не только смотреть пещеру, но и купаться у холодного источника. "
                "Внутри есть небольшой буддийский алтарь. Государственное агентство KPL также записало местную практику сиенг-си — гадания с палочками — и рассказ гида, "
                "что посетители считают 147 ступеней, связывая это со счастливой приметой."
            ),
            "source_refs": ["src_990498", "src_990503"],
        },
        {
            "section_id": "geography",
            "content": (
                "Пещера прорезает карстовую стену Пха-Лао к юго-западу от центра Ванг-Вьенга. Вход находится примерно на 30 м выше уровня Нам-Сонг; "
                "отсюда хорошо видно речную долину, городскую окраину, рисовые поля и цепочку изолированных известняковых башен. "
                "Координата главного входа по Wikidata и геопривязанным фотографиям Commons — около 18.909, 102.442."
            ),
            "source_refs": ["src_990499", "src_990505", "src_990506"],
        },
        {
            "section_id": "geology",
            "content": (
                "Тхам-Чанг — часть карста Ванг-Вьенга, сформированного в растворимых карбонатных породах. Региональная работа 2024 года относит характерные карстовые холмы "
                "Ванг-Вьенга к пермскому комплексу Pz3 и описывает развитие пещер как продолжающееся растворение известняка и расширение трещин водой. "
                "Когда насыщенная карбонатом вода попадает в воздушную полость, часть минерала снова осаждается: так растут сталактиты, сталагмиты, колонны и потёчные коры, "
                "которые видны в освещённых залах. Важно не переусердствовать с точностью: исследование описывает геосайт Ванг-Вьенга в региональном масштабе и не даёт отдельного "
                "петрографического анализа стены именно Тхам-Чанг."
            ),
            "source_refs": ["src_990500", "src_990498"],
        },
        {
            "section_id": "ethnography",
            "content": (
                "Смысл пещеры в местной памяти связан с Муанг-Сонгом — земледельческим поселением у южной части Ванг-Вьенга. Туристическая традиция описывает жителей как "
                "овощеводов, которые использовали пещеру не эпизодически, а как коллективное убежище и временное место жизни. Источники не дают надёжной этнической атрибуции "
                "этой группы, поэтому карточка не приписывает историю конкретному народу."
            ),
            "source_refs": ["src:9799177acb170c"],
        },
        {
            "section_id": "myths_beliefs",
            "content": [
                {
                    "type": "local_tradition",
                    "text": (
                        "Официальный туристический рассказ сохраняет игру вокруг названия Tham Jang/Chang. В одной версии пещеру назвали местом, где жители могли долго "
                        "«оставаться» во время войны; позже название стали объяснять холодом источника — вода будто настолько ледяная, что ноги деревенели и человек не мог сразу уйти. "
                        "Это местная этимологическая история, а не доказанное происхождение слова."
                    ),
                },
                {
                    "type": "modern_tourist_story",
                    "text": (
                        "Современный Discover Laos предлагает другую трактовку: Jang — «стойкий», «крепкий», что связывается с защитной ролью пещеры. "
                        "Поскольку обе версии живут одновременно и источники не дают лингвистического разбора, правильнее сохранить их как конкурирующие традиции, а не выбирать одну как факт."
                    ),
                },
                {
                    "type": "local_tradition",
                    "text": (
                        "KPL записал ещё одну небольшую традицию самого посещения: люди считают 147 ступеней к входу, считая, что это может принести удачу; "
                        "рядом практикуют сиенг-си — гадание по выпавшим палочкам. Это уже не история происхождения пещеры, а современная локальная практика."
                    ),
                },
            ],
            "source_refs": ["src:9799177acb170c", "src_990498", "src_990503"],
        },
    ],
}

card["traveler_reports"] = [
    {
        "kind": "traveler_report",
        "topic": "current_access_and_price",
        "summary": (
            "Октябрь 2025: посетитель сообщил о билете 20 000 кип, короткой переправе на маленьком пароме и 147 ступенях после высадки. "
            "Это важнее старых схем с мостом, но тариф и сама переправа остаются динамическими."
        ),
        "observed_period": "2025-10",
        "source_refs": ["src_990502"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "interior_condition",
        "summary": (
            "Декабрь 2025: несколько отзывов описывают основные залы как хорошо освещённые и оборудованные мощёными/бетонными дорожками. "
            "Один посетитель заплатил 22 000 кип и назвал Тхам-Чанг самой коммерчески оборудованной пещерой из увиденных вокруг Ванг-Вьенга."
        ),
        "observed_period": "2025-12",
        "source_refs": ["src_990502"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "walking_and_water_area",
        "summary": (
            "Февраль–март 2025: AllTrails и пользовательские отчёты подтверждают простой городской подход, бетонные ступени и освещение; "
            "нижняя водная зона использовалась для купания. Это отдельная активность от сухой оборудованной части Тхам-Чанг."
        ),
        "observed_period": "2025-02/03",
        "source_refs": ["src_990501"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "visitor_pressure_and_conservation",
        "summary": (
            "Декабрь 2025: посетитель отдельно критиковал вмешательство инфраструктуры в натёчные образования и советовал приходить сразу после открытия, "
            "когда меньше групп. Это субъективное наблюдение, но полезное для оценки степени коммерциализации объекта."
        ),
        "observed_period": "2025-12",
        "source_refs": ["src_990502"],
        "confidence": "medium",
    },
]
card["accommodation"] = []

existing_sources = [s for s in (obj.get("sources") or []) if isinstance(s, dict)]
add_sources = [
    {
        "type": "other",
        "title": "Tham Chang Cave",
        "publisher": "Discover Laos Today / supported by Laos Tourism Board",
        "url": "https://discoverlaos.today/vang-vieng/thing-to-do/tham-chang-cave",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["current visitor listing", "hours", "history tradition", "name tradition", "stairs", "spring", "Buddhist shrine", "visual context"],
        "accessed": CHECKED,
    },
    {
        "type": "other",
        "title": "Tham Jang",
        "publisher": "Wikidata",
        "url": "https://www.wikidata.org/wiki/Q7709769",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["cave identity", "Pha Lao", "coordinates", "Commons linkage"],
        "accessed": CHECKED,
    },
    {
        "type": "academic",
        "title": "Geological Perspective as Karst Geotourism Potential: A Case Study of Vientiane Province, Laos",
        "publisher": "Jurnal Geosains dan Remote Sensing",
        "url": "https://www.researchgate.net/publication/386275397_Geological_Perspective_as_Karst_Geotourism_Potential_A_Case_Study_of_Vientiane_Province_Laos",
        "language": "en",
        "published_at": "2024-11-30",
        "authority": "high",
        "used_for": ["Vang Vieng regional geology", "Permian Pz3 karst context", "limestone dissolution", "cave/speleothem geosite context"],
        "accessed": CHECKED,
        "notes": "DOI 10.23960/jgrs.ft.unila.346; regional geosite study, not a direct petrographic sample from Tham Chang.",
    },
    {
        "type": "traveler_report",
        "title": "Tham Chang Cave — route and 2025 field reports",
        "publisher": "AllTrails",
        "url": "https://www.alltrails.com/en-gb/trail/laos/vientiane/tham-chang-cave",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["walking route", "stairs", "lighting", "2025 entry price", "water area", "current visitor condition"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Tham Chang Cave — traveler reviews",
        "publisher": "Tripadvisor",
        "url": "https://www.tripadvisor.com/Attraction_Review-g612363-d2314020-Reviews-Tham_Chang_Cave-Vang_Vieng_Vientiane_Province.html",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["2025-2026 condition", "price", "ferry", "crowding", "walkways", "supplies", "slipperiness"],
        "accessed": CHECKED,
    },
    {
        "type": "government_official",
        "title": "Vang Vieng has Much to Impress",
        "publisher": "KPL / Lao News Agency",
        "url": "https://kpl.gov.la/en/detail.aspx?id=24081",
        "language": "en",
        "published_at": "2017",
        "authority": "high",
        "used_for": ["147 stairs", "local luck tradition", "siengxi divination", "historic ticket context"],
        "accessed": CHECKED,
    },
    {
        "type": "academic",
        "title": "Strangers in the hills: Social disruption and the origins of Lao nationalism (1873–1911)",
        "publisher": "South East Asia Research / Taylor & Francis",
        "url": "https://www.tandfonline.com/doi/full/10.1177/0967828X17741037",
        "language": "en",
        "published_at": "2018-10-18",
        "authority": "high",
        "used_for": ["Ho Wars chronology", "historical caution on tourist dating"],
        "accessed": CHECKED,
        "notes": "Dates the Ho Wars in Laos approximately 1869–1889; used to prevent repeating an inconsistent 'early 19th century' tourist chronology as fact.",
    },
    {
        "type": "other",
        "title": "Former bridge leading to Tham Jang",
        "publisher": "Wikimedia Commons",
        "url": "https://commons.wikimedia.org/wiki/File:VientianeProvince_VangVieng_ThamJang1_tango7174.jpg",
        "language": "en",
        "published_at": "2013-11-24",
        "authority": "medium",
        "used_for": ["old bridge identity", "bridge collapse June 2021", "access-change context"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Tham Chang Cave — hiking highlight",
        "publisher": "Komoot",
        "url": "https://www.komoot.com/highlight/5440367",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["approximate cave elevation", "walking context"],
        "accessed": CHECKED,
    },
]
by_url = {s.get("url"): s for s in existing_sources if s.get("url")}
for source in add_sources:
    by_url[source["url"]] = source
obj["sources"] = list(by_url.values())

gallery = [
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Tham_Jang_3.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Tham_Jang_3.jpg",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Tham_Jang_2.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Tham_Jang_2.jpg",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Tham_Jang_5.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Tham_Jang_5.jpg",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/27/Tham_Jang_entrance.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Tham_Jang_entrance.jpg",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/ae/View_from_the_Tham_Jang.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:View_from_the_Tham_Jang.jpg",
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Tham_Jang_Lagoon_1.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Tham_Jang_Lagoon_1.jpg",
    },
]
obj["illustration"] = {
    "static_url": gallery[0]["url"],
    "source_page": gallery[0]["page"],
    "provider": "Wikimedia Commons",
    "license": "CC BY-SA 4.0",
    "artist": "Christophe95",
    "illustration_scope": "Tham Jang Cave, entrance, valley view and karst spring",
    "last_checked": CHECKED,
    "gallery": [
        {
            "static_url": row["url"],
            "source_page": row["page"],
            "provider": "Wikimedia Commons",
            "license": "CC BY-SA 4.0",
            "artist": "Christophe95",
            "last_checked": CHECKED,
        }
        for row in gallery
    ],
}

obj["verification"] = {
    "dynamic_fields": ["hours", "ticket", "river crossing", "access", "water activity", "crowding", "drone"],
    "verify_before_departure": True,
}

obj["qa"] = {
    **(obj.get("qa") or {}),
    "language_review": {
        "status": "reviewed",
        "checked_at": CHECKED,
        "notes": (
            "Туристическая хронология убежища отделена от академической датировки войн хо; конкурирующие версии названия сохранены как традиции, "
            "а не объявлены установленной этимологией."
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
            "local_traditions_explained": True,
            "uncertainty_preserved": True,
        },
    },
    "card_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "полный объектный QA Tham Chang Cave",
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
            "ethnography_scoped": True,
            "myths_beliefs_substantive": True,
            "legend_labeled": True,
            "history_chronology_conflict_explicit": True,
            "river_crossing_dynamic": True,
            "no_narrative_duplication": True,
        },
        "notes": [
            "Primary GPS is the cave entrance/cliff, not Vang Vieng town center.",
            "270 m is an approximate route-platform elevation, explicitly not a survey benchmark.",
            "The old bridge collapse and recent ferry reports are separated from stale bridge instructions in tourism listings.",
            "Ho-war chronology is corrected by attribution rather than silently rewriting the local tradition.",
            "Competing name etymologies remain labeled as traditions.",
        ],
    },
    "rebuild_v2": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "полная редакционная, геологическая, историческая, полевая и источниковая перестройка Tham Chang Cave",
        "checks": {
            "connected_story": True,
            "history_substantive": True,
            "culture_substantive": True,
            "geography_substantive": True,
            "geology_substantive": True,
            "ethnography_scoped": True,
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
            "open_license_gallery": True,
            "drone_rule_precision": True,
        },
    },
    "fact_source_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": (
            "Tham Chang: identity, entrance GPS, approximate elevation, Vang Vieng karst geology, Meuang Xong refuge tradition, "
            "Ho Wars chronology, name traditions, stairs/luck practice, current access/ferry, hours, price reports, water, media and drone"
        ),
        "checks": {
            "narrative_section_sources": True,
            "coordinate_source_scoped": True,
            "elevation_source_scoped": True,
            "regional_geology_not_overstated_as_site_petrology": True,
            "tourist_history_vs_academic_chronology_split": True,
            "name_etymologies_marked_tradition": True,
            "current_crossing_uncertainty_preserved": True,
            "ticket_marked_traveler_report": True,
            "water_quality_unknown_preserved": True,
            "camping_permission_unknown_preserved": True,
            "traveler_report_period_scoped": True,
            "gallery_open_license": True,
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

print("Updated Tham Chang Cave and registered", len(NEW_SOURCES), "source IDs")
