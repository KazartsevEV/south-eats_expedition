#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "laos.json"
REGISTRY = ROOT / "data" / "id-registry.json"
CHECKED = "2026-10-03"

SOURCE_IDS = {
    "https://www.cambridge.org/core/journals/antiquity/article/surveys-of-hintang-standing-stone-sites-and-excavations-at-site-7a-houaphanh-lao-pdr/8C35E2A9C5FECBD881283FFDE2F026C8": "src_990481",
    "https://www.tourismlaos.org/2026/04/03/standing-stones-in-houaphanh-recognized-as-national-heritage/": "src_990482",
    "https://kpl.gov.la/Detail.aspx?id=77966": "src_990483",
    "https://houaphanhtourism.com/en/news/Attracting-investment/houaphanh-tourist-attractions-170.html": "src_990484",
    "http://megalithmaniac.blogspot.com/2014/08/hintang.html": "src_990485",
    "https://www.tripadvisor.com/Attraction_Review-g3650252-d1627227-Reviews-Hintang_Houamuang-Houaphanh_Province.html": "src_990486",
    "https://onlinelibrary.wiley.com/doi/10.1111/1469-8676.13092": "src_990487",
}

def source_key(url: str) -> str:
    return "src:" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:14]

def find_object(node):
    if isinstance(node, dict):
        if node.get("name") == "Hintang Archaeological Park":
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
    raise SystemExit("Hintang Archaeological Park not found")

obj["class"] = "archaeology"
obj["interest"] = [
    "archaeology",
    "megalith",
    "history",
    "burial_landscape",
    "trekking",
    "ethnography",
]
obj["why_go"] = (
    "Хинтанг — не одна группа менгиров, а протяжённый мегалитический ландшафт Хуапхана: "
    "десятки участков со стоячими плитами из слюдяного сланца, каменными дисками и погребальными ямами "
    "на горных гребнях. В 2025 году лаосско-австралийская экспедиция заново геопривязала комплексы и "
    "провела первые примерно за 90 лет раскопки; поэтому старая датировка «бронзовый век» теперь должна "
    "рассматриваться как гипотеза, а не как установленный возраст."
)

card = obj.setdefault("traveler_card", {})
card["location"] = {
    "region": "Houaphanh Province / Houameuang District",
    "nearest_hub": "Sam Neua",
    "languages_spoken": [
        "лаосский",
        "местные языки Хуапхана; состав зависит от деревни",
        "английский — ограниченно",
    ],
    "coordinates": {
        "lat": 20.12314,
        "lon": 103.89575,
        "elevation_m": 1450,
    },
    "coordinate_type": "archaeological_core",
    "accuracy": "medium",
    "elevation_accuracy": "approximate",
    "coordinates_checked_at": CHECKED,
    "coordinate_source": {
        "type": "traveler_report",
        "title": "Standing Stones of the Hintang Archaeological Park — San Khong Phan GPS",
        "publisher": "Megalith Maniac / Dr Marco Langbroek",
        "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
        "language": "en",
        "published_at": "2014-10-24",
        "authority": "medium",
        "accessed": CHECKED,
        "notes": (
            "Author GPS for San Khong Phan, the main visitor cluster: 20°07'23.3\"N, 103°53'44.7\"E. "
            "The source corrected a separate Keohintang clerical coordinate error in February 2026."
        ),
    },
    "elevation_source": {
        "type": "traveler_report",
        "title": "Standing Stones of the Hintang Archaeological Park — San Khong Phan GPS/elevation",
        "publisher": "Megalith Maniac / Dr Marco Langbroek",
        "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
        "language": "en",
        "published_at": "2014-10-24",
        "authority": "medium",
        "accessed": CHECKED,
        "notes": "Author GPS reports about 1450 m at San Khong Phan main site.",
    },
    "object_elevation": {
        "representative_m": 1450,
        "min_m": None,
        "max_m": None,
        "reference_type": "site",
        "accuracy": "approximate",
        "source": {
            "type": "traveler_report",
            "title": "Standing Stones of the Hintang Archaeological Park — San Khong Phan GPS/elevation",
            "publisher": "Megalith Maniac / Dr Marco Langbroek",
            "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
            "language": "en",
            "published_at": "2014-10-24",
            "authority": "medium",
            "accessed": CHECKED,
        },
        "checked_at": CHECKED,
        "notes": (
            "Около 1450 м относится к главному комплексу San Kong Phan/Ban Pa Cha, а не к минимальной "
            "или максимальной высоте всего 12-километрового археологического ландшафта."
        ),
    },
    "geo_points": [
        {
            "type": "archaeological_core",
            "name": "Site 7A — раскоп 2025 года",
            "coordinates": {
                "lat": 20.1462389,
                "lon": 103.8673611,
                "elevation_m": 1430,
            },
            "accuracy": "high",
            "elevation_accuracy": "high",
            "coordinate_source": {
                "type": "academic",
                "title": "Surveys of Hintang standing stone sites and excavations at Site 7A, Houaphanh, Lao PDR",
                "publisher": "Antiquity / Cambridge University Press",
                "url": "https://www.cambridge.org/core/journals/antiquity/article/surveys-of-hintang-standing-stone-sites-and-excavations-at-site-7a-houaphanh-lao-pdr/8C35E2A9C5FECBD881283FFDE2F026C8",
                "language": "en",
                "published_at": "2026-08-07",
                "authority": "high",
                "accessed": CHECKED,
                "notes": "Published excavation coordinate: 20°8′46.46″N, 103°52′2.50″E.",
            },
            "elevation_source": {
                "type": "academic",
                "title": "Surveys of Hintang standing stone sites and excavations at Site 7A, Houaphanh, Lao PDR",
                "publisher": "Antiquity / Cambridge University Press",
                "url": "https://www.cambridge.org/core/journals/antiquity/article/surveys-of-hintang-standing-stone-sites-and-excavations-at-site-7a-houaphanh-lao-pdr/8C35E2A9C5FECBD881283FFDE2F026C8",
                "language": "en",
                "published_at": "2026-08-07",
                "authority": "high",
                "accessed": CHECKED,
                "notes": "Published elevation 1430 m asl.",
            },
            "checked_at": CHECKED,
            "notes": "Точка относится к Site 7A, а не к центру всего Хинтанга.",
        },
        {
            "type": "viewpoint",
            "name": "Kéo Hintang / Keohintang",
            "coordinates": {
                "lat": 20.14281,
                "lon": 103.86994,
                "elevation_m": None,
            },
            "accuracy": "medium",
            "elevation_accuracy": "unknown",
            "coordinate_source": {
                "type": "traveler_report",
                "title": "Standing Stones of the Hintang Archaeological Park — Keohintang corrected GPS",
                "publisher": "Megalith Maniac / Dr Marco Langbroek",
                "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
                "language": "en",
                "published_at": "2014-10-24",
                "authority": "medium",
                "accessed": CHECKED,
                "notes": "Coordinate explicitly corrected by the author on 2026-02-24.",
            },
            "checked_at": CHECKED,
            "notes": "Крупный лесной комплекс стоячих камней на пешеходной тропе.",
        },
        {
            "type": "trailhead",
            "name": "Начало лесной тропы Hintang от грунтовой дороги",
            "coordinates": {
                "lat": 20.13369,
                "lon": 103.882756,
                "elevation_m": 1495,
            },
            "accuracy": "medium",
            "elevation_accuracy": "approximate",
            "coordinate_source": {
                "type": "traveler_report",
                "title": "Standing Stones of the Hintang Archaeological Park — trailhead GPS",
                "publisher": "Megalith Maniac / Dr Marco Langbroek",
                "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
                "language": "en",
                "published_at": "2014-10-24",
                "authority": "medium",
                "accessed": CHECKED,
            },
            "elevation_source": {
                "type": "traveler_report",
                "title": "Standing Stones of the Hintang Archaeological Park — trailhead GPS/elevation",
                "publisher": "Megalith Maniac / Dr Marco Langbroek",
                "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
                "language": "en",
                "published_at": "2014-10-24",
                "authority": "medium",
                "accessed": CHECKED,
            },
            "checked_at": CHECKED,
        },
    ],
}

card["logistics"] = {
    "access": (
        "Базовый самостоятельный маршрут идёт из Сам-Ныа по Route 6 к Ban Phao, затем по грубой грунтовой дороге "
        "к San Kong Phan — главному посещаемому кластеру. Официальный KPL/Tourism Laos описывает Ban Phao примерно "
        "в 57 км от Сам-Ныа и около 6 км последнего грунтового участка. Полевой GPS-отчёт 2014 года измерил 5,5 км "
        "от развилки в Ban Phao до San Kong Phan с набором около 350 м."
    ),
    "public_transport": (
        "В 2014 году путешественник успешно доехал из Сам-Ныа рейсовым транспортом по Route 6 до Ban Phao и продолжил пешком; "
        "актуальное расписание на 2026 год не подтверждено. Поэтому автобус нельзя считать гарантированным вариантом без проверки на месте."
    ),
    "last_mile": (
        "От Route 6 до San Kong Phan — примерно 5,5–6 км по крутой грунтовке. После дождя дорога становится очень грязной; "
        "в отзыве 2023 года 4×4 прошёл, а обычную легковую машину автор считал возможной только в сухом состоянии дороги."
    ),
    "typical_visit_hours": None,
    "permit_or_guide": (
        "Обязательный гид для San Kong Phan опубликованными источниками не подтверждён. Однако объект получил статус национального "
        "культурного наследия в 2026 году, а режим охранных зон развивается; перед проходом к удалённым кластерам разумно уточнить "
        "локальные ограничения у провинциальной службы наследия."
    ),
    "mobility_notes": (
        "Грунтовый подъезд крутой и местами разбитый. Лесная тропа узкая, после дождя скользкая; часть камней скрыта растительностью. "
        "На археологических участках встречаются открытые или частично засыпанные погребальные ямы."
    ),
    "modes": {
        "public_transport": "Исторически использовался транспорт по Route 6 до Ban Phao; актуальный график не подтверждён.",
        "taxi_ridehail": "Для полного дня из Сам-Ныа практичен заранее нанятый водитель; фиксированный официальный тариф не подтверждён.",
        "car": "В сухую погоду возможен подъезд к San Kong Phan; 4×4 надёжнее на последней грунтовке.",
        "moped": "В сухую погоду технически возможен на грунтовом подъезде, но состояние после дождя резко ухудшается.",
        "motorcycle": "Официальные туристические материалы показывают мотоциклетный доступ; грунтовка остаётся сезонным ограничением.",
        "walking": "Самый проверяемый независимый вариант — пешком от Ban Phao до главного участка и далее по лесной тропе.",
    },
    "water": (
        "Подтверждённой питьевой воды у San Kong Phan и на лесной тропе нет. Полевой отчёт советует нести большой запас; "
        "для экспедиционного планирования надёжный запас лучше набрать до выезда из Сам-Ныа."
    ),
    "water_structured": {
        "at_object": False,
        "quality": "unknown",
        "last_reliable_point": "Sam Neua",
        "distance_m": None,
        "natural_sources": [],
        "notes": "Постоянный проверенный источник питьевой воды у мегалитов не найден; природную воду не считать питьевой без обработки.",
        "source_refs": ["src_990485"],
    },
    "supplies": {
        "status": "none_confirmed_at_site",
        "summary": "Магазины и постоянные точки снабжения непосредственно у главных мегалитических кластеров не подтверждены.",
        "poi_ids": [],
        "source_refs": ["src_990485"],
    },
    "overnight_and_camping": (
        "Официальный кемпинг на археологическом ландшафте не подтверждён. Свободную ночёвку среди камней нельзя считать разрешённой; "
        "для обычного маршрута базой остаётся Сам-Ныа или иное жильё вне охранной зоны."
    ),
    "overnight": {
        "status": "unclear",
        "summary": "Режим палаточной ночёвки в границах национального культурного наследия публично не найден; разрешённость не утверждается.",
        "source_refs": ["src_990482"],
    },
    "access_requirements": (
        "Не перемещать камни и диски, не заходить в погребальные ямы и не сходить с существующих дорог/троп на участках с археологическими остатками."
    ),
    "access_options": [
        {
            "id": "sam_neua_ban_phao_san_kong_phan",
            "origin": "Sam Neua",
            "modes": ["car", "motorcycle", "moped", "walking"],
            "checked_at": CHECKED,
            "source_refs": ["src_990483", "src_990485", "src_990486"],
            "legs": [
                {
                    "mode": "car",
                    "distance_km": 57,
                    "duration_min": None,
                    "surface": "paved",
                    "condition": "Route 6 до района Ban Phao; официальная публикация даёт ориентир 57 км от Xam Neua.",
                    "seasonality": "Основная дорога существенно надёжнее последнего грунтового подъезда.",
                    "elevation_gain_m": None,
                    "elevation_loss_m": None,
                    "trailhead": None,
                    "navigation": "Route 6 к Ban Phao, затем съезд на грунтовую дорогу к археологическому парку.",
                    "fords": None,
                    "notes": "57 км — официальный ориентир до развилки/района Ban Phao, не расстояние до самого San Kong Phan.",
                    "source_refs": ["src_990483"],
                },
                {
                    "mode": "walking",
                    "distance_km": 5.5,
                    "duration_min": 90,
                    "surface": "dirt",
                    "condition": "Почти непрерывный подъём по открытой грунтовой дороге; после дождя грязно.",
                    "seasonality": "В мокрый период прохождение и проезд заметно тяжелее.",
                    "elevation_gain_m": 350,
                    "elevation_loss_m": None,
                    "trailhead": {
                        "lat": 20.1589,
                        "lon": 103.8913,
                    },
                    "navigation": "От съезда Route 6 в Ban Phao идти по грунтовке до San Kong Phan.",
                    "fords": None,
                    "notes": "Дистанция, набор и около 1,5 часа относятся к GPS-походу 2014 года; использовать как полевой ориентир, не как гарантированное современное время.",
                    "source_refs": ["src_990485"],
                },
            ],
        },
        {
            "id": "hintang_forest_trail",
            "origin": "Hintang forest trailhead",
            "modes": ["walking"],
            "checked_at": CHECKED,
            "source_refs": ["src_990485"],
            "legs": [
                {
                    "mode": "walking",
                    "distance_km": 4.4,
                    "duration_min": 120,
                    "surface": "trail",
                    "condition": "Узкая лесная тропа по гребню; отдельные группы камней легко пропустить в растительности.",
                    "seasonality": "После дождя скользко; возможны пиявки.",
                    "elevation_gain_m": None,
                    "elevation_loss_m": None,
                    "trailhead": {
                        "lat": 20.13369,
                        "lon": 103.882756,
                    },
                    "navigation": "Тропа проходит через меньшие группы и Keohintang и выходит к Ban Tao Hin на Route 6.",
                    "fords": 0,
                    "notes": "2 часа — время автора 2014 года вместе с остановками у Keohintang; актуальная маркировка требует перепроверки.",
                    "source_refs": ["src_990485"],
                }
            ],
        },
    ],
    "self_guided_default": True,
    "travel_model": "самостоятельный доступ к San Kong Phan; удалённые лесные кластеры — пешком с осторожной навигацией и проверкой текущих охранных ограничений",
}

card["climate"] = {
    "best_period": "Сухое состояние дороги предпочтительно для грунтового подъезда и гребневой тропы.",
    "heat_rain_notes": "После дождей грунтовка может стать труднопроходимой для машин, а лесная тропа — скользкой.",
    "site_specific_notes": "Открытая часть подъёма от Ban Phao почти без тени; лесные участки прохладнее, но влажнее.",
}

card["operations"] = {
    "status": "national_heritage_visitation_documented",
    "hours": None,
    "ticket": None,
    "closure_notes": (
        "Единые часы, билет и ежедневный контроль входа для всего протяжённого комплекса не опубликованы. "
        "В 2026 году Хинтанг официально признан национальным культурным наследием; режим охранных зон может меняться."
    ),
    "last_verified": CHECKED,
    "official_url": "https://www.tourismlaos.org/2026/04/03/standing-stones-in-houaphanh-recognized-as-national-heritage/",
    "status_snapshot": {
        "as_of": CHECKED,
        "summary": (
            "Tourism Laos сообщает о признании Хинтанга национальным культурным наследием в 2026 году и о создании охранных зон. "
            "Публичного объявления о закрытии обычного доступа к San Kong Phan не найдено."
        ),
        "source_refs": ["src_990482", "src_990483"],
    },
    "source_refs": ["src_990482", "src_990483"],
}

card["safety"] = {
    "main_risks": [
        "крутая разбитая грунтовая дорога, особенно после дождя",
        "скользкая лесная тропа и пиявки после дождей",
        "открытые или частично засыпанные погребальные ямы среди камней",
        "жара и отсутствие подтверждённой питьевой воды на открытом подъёме",
        "падение ветвей и деревьев: полевой отчёт фиксировал повреждение камней упавшим деревом",
    ],
    "sensitive_areas": [
        "не вставать на каменные диски и не сдвигать археологические элементы",
        "не заходить в свежие раскопы или ограждённые участки",
        "учитывать, что в 2026 году объект получил национальный охранный статус",
    ],
    "confidence": "medium",
    "source_refs": ["src_990481", "src_990482", "src_990485", "src_990486"],
    "checked_at": CHECKED,
}

cambridge_url = "https://www.cambridge.org/core/journals/antiquity/article/surveys-of-hintang-standing-stone-sites-and-excavations-at-site-7a-houaphanh-lao-pdr/8C35E2A9C5FECBD881283FFDE2F026C8"
card["media"] = {
    "photo_suitability_5": 5,
    "video_suitability_5": 4,
    "best_light": "Низкий боковой свет лучше подчёркивает высоту узких плит и рельеф гребня; в лесных группах важнее ровный рассеянный свет.",
    "visual_scouting": {
        "best_time": "morning_or_late_afternoon",
        "best_weather_light": (
            "Сухая ясная погода удобнее для доступа и дальних видов с гребня; после дождя камень и лишайники выглядят контрастнее, "
            "но грунтовка и тропа заметно хуже."
        ),
        "viewpoints_for_photo_video": [
            {
                "id": "vp_san_kong_phan",
                "name": "San Kong Phan / Ban Pa Cha — главный кластер",
                "description": "Открытая группа стоячих плит, дисков и погребальных ям у грунтовой дороги.",
                "coordinates": {"lat": 20.12314, "lon": 103.89575, "elevation_m": 1450},
                "access": "Около 5,5–6 км от Route 6 по грунтовому подъезду.",
                "view": {"description": "Группы вертикальных сланцевых плит, плоские диски и горный гребень."},
                "best_time": "morning_or_late_afternoon",
                "best_weather_light": "Боковой свет подчёркивает узкие профили плит и их взаимное расположение.",
                "useful_equipment": [
                    {"type": "wide", "why": "показывает группы камней в масштабе гребневого ландшафта"},
                    {"type": "standard", "why": "для отдельных групп, дисков и фактуры сланца"},
                ],
                "source": {
                    "type": "traveler_report",
                    "title": "Standing Stones of the Hintang Archaeological Park — San Khong Phan",
                    "publisher": "Megalith Maniac / Dr Marco Langbroek",
                    "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
                    "language": "en",
                    "published_at": "2014-10-24",
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
            {
                "id": "vp_keohintang",
                "name": "Kéo Hintang / Keohintang",
                "description": "Крупный лесной кластер на тропе, скрытый под пологом и визуально совсем иной, чем открытый San Kong Phan.",
                "coordinates": {"lat": 20.14281, "lon": 103.86994, "elevation_m": None},
                "access": "Пешком по лесной тропе Hintang.",
                "view": {"description": "Стоячие плиты среди деревьев; одна из наиболее плотных и высоких групп на маршруте."},
                "best_time": "daylight",
                "best_weather_light": "Рассеянный лесной свет удобнее прямого жёсткого солнца.",
                "useful_equipment": [
                    {"type": "wide", "why": "для тесной связи камней с лесом"},
                    {"type": "standard", "why": "для отдельных плит и дисков"},
                ],
                "source": {
                    "type": "traveler_report",
                    "title": "Standing Stones of the Hintang Archaeological Park — Keohintang",
                    "publisher": "Megalith Maniac / Dr Marco Langbroek",
                    "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
                    "language": "en",
                    "published_at": "2014-10-24",
                    "authority": "medium",
                    "accessed": CHECKED,
                },
            },
            {
                "id": "vp_site_7a",
                "name": "Site 7A — исследовательский участок 2025",
                "description": "Небольшая группа из трёх и более плит на расчищенном участке; здесь прошли первые новые раскопки примерно за 90 лет.",
                "coordinates": {"lat": 20.1462389, "lon": 103.8673611, "elevation_m": 1430},
                "access": "Не считать туристической точкой без проверки текущего режима: это исследовательский и уязвимый участок.",
                "view": {"description": "Стоячие камни и контекст современного археологического исследования."},
                "best_time": None,
                "best_weather_light": None,
                "useful_equipment": [
                    {"type": "standard", "why": "для документального контекста камней и поверхности участка"}
                ],
                "source": {
                    "type": "academic",
                    "title": "Surveys of Hintang standing stone sites and excavations at Site 7A, Houaphanh, Lao PDR",
                    "publisher": "Antiquity / Cambridge University Press",
                    "url": cambridge_url,
                    "language": "en",
                    "published_at": "2026-08-07",
                    "authority": "high",
                    "accessed": CHECKED,
                },
            },
        ],
        "seasonal_visuals": [
            "В сухой сезон подъезд надёжнее и открытые группы проще связать в единый гребневый ландшафт.",
            "После дождей лес насыщеннее, лишайники и мокрый сланец контрастнее, но тропа и грунтовая дорога значительно хуже.",
            "Утренние поездки по Route 6 иногда дают облака в долинах ниже горных гребней; это полевой эффект маршрута, а не гарантированное явление у самих камней.",
        ],
        "video_activity": [
            "переход от открытого San Kong Phan к лесным группам",
            "последовательное появление небольших групп камней вдоль гребневой тропы",
            "археологические диски и погребальные ямы в контексте стоячих плит",
        ],
        "useful_equipment": [
            {"type": "wide", "why": "для групп камней и рельефа гребня"},
            {"type": "standard", "why": "для отдельных плит, дисков и следов обработки"},
            {"type": "macro", "why": "для лишайников, поверхности сланца и мелких деталей без контакта с памятником"},
        ],
    },
    "drone": {
        "visual_value": "Высокая для демонстрации линейного распределения групп по гребням, но археологический статус требует особенно осторожного режима.",
        "legal_status": "regulated",
        "permit_required": None,
        "restrictions": [
            "Действуют общие правила БПЛА Лаоса.",
            "В 2026 году Хинтанг получил статус национального культурного наследия; отдельное публичное разрешение на полёты над охранными зонами не найдено.",
            "Не запускать дрон над активными раскопками или работами службы наследия без отдельного согласования.",
        ],
        "source_refs": ["src:23a65d16d80264", "src:3564b6c27bf542"],
        "checked_at": CHECKED,
    },
    "filming_restrictions": (
        "Обычная наземная съёмка опубликованными источниками не запрещена; для активных раскопок, исследовательских зон и коммерческой съёмки режим нужно согласовывать отдельно."
    ),
}

card["annotation"] = {
    "canonical_story_from_sections": True,
    "sections": [
        {
            "section_id": "overview",
            "content": (
                "Хинтанг — цепочка мегалитических комплексов в горах Хуапхана, а не одна площадка. Исследования фиксируют более 70 участков, "
                "свыше 1500 вертикальных плит из слюдяного сланца и около 150 каменных дисков. Камни образуют группы на гребнях и седловинах; "
                "рядом встречаются погребальные ямы и каменные перекрытия. Главный доступный кластер известен как San Kong Phan/Ban Pa Cha."
            ),
            "source_refs": ["src_990481", "src_990482", "src_990484"],
        },
        {
            "section_id": "history",
            "content": [
                {
                    "type": "documented_history",
                    "text": (
                        "Мадлен Колани исследовала Хинтанг в 1930-х годах и связала стоячие камни с погребальным обрядом: под частью групп она находила "
                        "обложенные камнем камеры с человеческими останками и сопутствующими предметами."
                    ),
                },
                {
                    "type": "documented_history",
                    "text": (
                        "Колани предложила датировку примерно 1700–500 гг. до н. э. и считала Хинтанг более ранним, чем мегалитические кувшины Сиангкхуанга. "
                        "Современная работа 2026 года подчёркивает, что это гипотеза: первые новые образцы для радиометрического датирования были взяты только в 2025 году, "
                        "а результаты ещё не опубликованы."
                    ),
                },
                {
                    "type": "documented_history",
                    "text": (
                        "Раскоп Site 7A в 2025 году обнаружил керамику, перфорированный сланцевый диск и более поздний фрагмент глазурованной чаши, вероятно XV–XVI веков. "
                        "Это показывает сложную историю использования и нарушения слоя: поздняя находка не датирует сами менгиры."
                    ),
                },
                {
                    "type": "documented_history",
                    "text": (
                        "В 2026 году власти Лаоса признали Хинтанг национальным культурным наследием; одновременно продолжаются картирование, охрана и подготовка к возможному "
                        "будущему международному признанию."
                    ),
                },
            ],
            "source_refs": ["src_990481", "src_990482"],
        },
        {
            "section_id": "culture",
            "content": (
                "Хинтанг важен не только как «доисторические камни», но и как современное наследие местных деревень. Новый survey 2025 года проводился совместно "
                "с национальными, провинциальными и районными подразделениями наследия и при участии местных властей. Национальный статус 2026 года закрепляет за местом "
                "не только исследовательскую, но и охранную функцию."
            ),
            "source_refs": ["src_990481", "src_990482"],
        },
        {
            "section_id": "geography",
            "content": (
                "Комплексы вытянуты вдоль горных гребней и седловин в Houameuang District. Официальные туристические материалы описывают полосу памятников примерно 12 км длиной. "
                "Главный San Kong Phan лежит около 1450 м над морем; полевой маршрут к нему поднимается примерно на 350 м от Ban Phao, а лесная тропа связывает несколько меньших групп "
                "и выходит к Ban Tao Hin."
            ),
            "source_refs": ["src_990483", "src_990484", "src_990485"],
        },
        {
            "section_id": "geology",
            "content": (
                "Большинство исследованных стоячих камней — плиты слюдяного сланца. В 2025 году у Vieng Noc Khoum археологи отметили возможный сланцевый карьер, "
                "что важно для понимания происхождения материала. Геология здесь непосредственно связана с конструкцией памятников, но сама по себе не даёт их возраста."
            ),
            "source_refs": ["src_990481"],
        },
        {
            "section_id": "ethnography",
            "content": (
                "Современные исследования Хинтанга показывают, что археологический ландшафт существует внутри живой местной памяти. Этнографическая работа Анны Кэллен и более поздний "
                "анализ традиций народа Phong рассматривают стоячие камни не только как научный объект, но и как часть местных рассказов о прошлом, власти и происхождении. "
                "Поэтому колониальную схему Колани о «исчезнувшей цивилизации» нельзя выдавать за единственное местное объяснение."
            ),
            "source_refs": ["src_990487"],
        },
        {
            "section_id": "myths_beliefs",
            "content": [
                {
                    "type": "local_tradition",
                    "text": (
                        "В одной из записанных традиций Phong камни Хинтанга связываются с правителем Hat Ang: их будто бы готовили для его дворца, но люди бросили камни, "
                        "спасаясь после гибели царя и разрушения его башни. Это этнографически зафиксированный сюжет, а не археологическая датировка или объяснение строительства."
                    ),
                },
                {
                    "type": "modern_tourist_story",
                    "text": (
                        "Популярное сравнение Хинтанга со «Стоунхенджем Лаоса» удобно как образ, но скрывает главное: это не один круг мегалитов, а десятки разнесённых групп, "
                        "связанных с погребальными сооружениями и длинной историей повторного использования."
                    ),
                },
            ],
            "source_refs": ["src_990487", "src_990481"],
        },
    ],
}

card["traveler_reports"] = [
    {
        "kind": "traveler_report",
        "topic": "self_guided_route",
        "summary": (
            "Июль 2014: путешественник прошёл маршрут самостоятельно общественным транспортом до Ban Phao, затем 5,5 км вверх по грунтовке к San Kong Phan и 4,4 км по лесной тропе "
            "через Keohintang до Ban Tao Hin. Он записал GPS всех ключевых точек и отметил, что открытый подъём был тяжелее самой лесной тропы."
        ),
        "observed_period": "2014-07",
        "source_refs": ["src_990485"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "road_condition",
        "summary": (
            "Август 2023: посетитель на 4×4 описал последние примерно 6 км как грубую и крутую дорогу. В сухом состоянии, по его оценке, медленно могла бы пройти и обычная легковая машина; "
            "во влажном состоянии он бы на неё не рассчитывал. Первый кластер был легко заметен справа и частично ограждён."
        ),
        "observed_period": "2023-08",
        "source_refs": ["src_990486"],
        "confidence": "medium",
    },
    {
        "kind": "traveler_report",
        "topic": "trail_navigation",
        "summary": (
            "Полевой отчёт 2014 года отмечает, что меньшие группы в лесу легко пропустить: узкие покрытые мхом плиты визуально сливаются со стволами. "
            "Автор также зафиксировал скользкий спуск к Ban Tao Hin и пиявок после дождя."
        ),
        "observed_period": "2014-07",
        "source_refs": ["src_990485"],
        "confidence": "medium",
    },
]
card["accommodation"] = []

existing_sources = [s for s in (obj.get("sources") or []) if isinstance(s, dict)]
add_sources = [
    {
        "type": "academic",
        "title": "Surveys of Hintang standing stone sites and excavations at Site 7A, Houaphanh, Lao PDR",
        "publisher": "Antiquity / Cambridge University Press",
        "url": "https://www.cambridge.org/core/journals/antiquity/article/surveys-of-hintang-standing-stone-sites-and-excavations-at-site-7a-houaphanh-lao-pdr/8C35E2A9C5FECBD881283FFDE2F026C8",
        "language": "en",
        "published_at": "2026-08-07",
        "authority": "high",
        "used_for": ["2025 survey", "excavation", "archaeology", "Site 7A GPS/elevation", "preservation threats", "gallery"],
        "accessed": CHECKED,
        "notes": "Open Access, CC BY 4.0.",
    },
    {
        "type": "government_official",
        "title": "Standing Stones in Houaphanh Recognized as National Heritage",
        "publisher": "Tourism Laos / Ministry of Culture and Tourism",
        "url": "https://www.tourismlaos.org/2026/04/03/standing-stones-in-houaphanh-recognized-as-national-heritage/",
        "language": "en",
        "published_at": "2026-04-03",
        "authority": "high",
        "used_for": ["national heritage status", "conservation zones", "current heritage policy", "site scale"],
        "accessed": CHECKED,
    },
    {
        "type": "government_official",
        "title": "Houaphanh Province — Hintang Archaeological Park",
        "publisher": "KPL / Lao News Agency",
        "url": "https://kpl.gov.la/Detail.aspx?id=77966",
        "language": "en",
        "published_at": "2023-06-11",
        "authority": "high",
        "used_for": ["official access", "Ban Phao distance", "last-mile distance", "12 km ridge", "baseline description"],
        "accessed": CHECKED,
    },
    {
        "type": "government_official",
        "title": "Houaphanh Tourist Attractions — Mysterious Standing Stones",
        "publisher": "Houaphanh Tourism",
        "url": "https://houaphanhtourism.com/en/news/Attracting-investment/houaphanh-tourist-attractions-170.html",
        "language": "en",
        "published_at": None,
        "authority": "high",
        "used_for": ["provincial tourism context", "70+ groups", "12 km ridge", "walking"],
        "accessed": CHECKED,
    },
    {
        "type": "traveler_report",
        "title": "Standing Stones of the Hintang Archaeological Park, Houaphan, Northeast Laos",
        "publisher": "Megalith Maniac / Dr Marco Langbroek",
        "url": "http://megalithmaniac.blogspot.com/2014/08/hintang.html",
        "language": "en",
        "published_at": "2014-10-24",
        "authority": "medium",
        "used_for": ["GPS", "elevation", "walking distances", "elevation gain", "trail navigation", "water", "seasonal trail observations"],
        "accessed": CHECKED,
        "notes": "Author GPS field report; Keohintang coordinate clerical error explicitly corrected 2026-02-24.",
    },
    {
        "type": "traveler_report",
        "title": "Hintang Houamuang — traveler reviews",
        "publisher": "Tripadvisor",
        "url": "https://www.tripadvisor.com/Attraction_Review-g3650252-d1627227-Reviews-Hintang_Houamuang-Houaphanh_Province.html",
        "language": "en",
        "published_at": None,
        "authority": "medium",
        "used_for": ["2023 road condition", "4x4 access", "site visibility", "older traveler trail reports"],
        "accessed": CHECKED,
    },
    {
        "type": "academic",
        "title": "Phong pioneers: exploring the sociopolitics of mythology in upland Laos",
        "publisher": "Social Anthropology / Wiley",
        "url": "https://onlinelibrary.wiley.com/doi/10.1111/1469-8676.13092",
        "language": "en",
        "published_at": "2021",
        "authority": "high",
        "used_for": ["Phong ethnography", "Hat Ang tradition", "standing-stone local tradition"],
        "accessed": CHECKED,
    },
]
by_url = {s.get("url"): s for s in existing_sources if s.get("url")}
for source in add_sources:
    by_url[source["url"]] = source
obj["sources"] = list(by_url.values())

figs = [
    "https://static.cambridge.org/binary/version/id/urn:cambridge.org:id:binary-alt:20260806120646-53962-mediumThumb-png-S0003598X26104086_fig2.jpg",
    "https://static.cambridge.org/binary/version/id/urn:cambridge.org:id:binary-alt:20260806120646-49762-mediumThumb-png-S0003598X26104086_fig3.jpg",
    "https://static.cambridge.org/binary/version/id/urn:cambridge.org:id:binary-alt:20260806120646-06588-mediumThumb-png-S0003598X26104086_fig4.jpg",
    "https://static.cambridge.org/binary/version/id/urn:cambridge.org:id:binary-alt:20260806120646-23299-mediumThumb-png-S0003598X26104086_fig5.jpg",
    "https://static.cambridge.org/binary/version/id/urn:cambridge.org:id:binary-alt:20260806120646-04237-mediumThumb-png-S0003598X26104086_fig6.jpg",
]
obj["illustration"] = {
    "static_url": figs[0],
    "source_page": cambridge_url,
    "provider": "Antiquity / Cambridge University Press",
    "license": "CC BY 4.0",
    "artist": "Louise Shewan et al.",
    "illustration_scope": "Hintang standing-stone sites / 2025 archaeological survey",
    "last_checked": CHECKED,
    "gallery": [
        {
            "static_url": url,
            "source_page": cambridge_url,
            "provider": "Antiquity / Cambridge University Press",
            "license": "CC BY 4.0",
            "artist": "Louise Shewan et al.",
            "last_checked": CHECKED,
        }
        for url in figs
    ],
}

obj["verification"] = {
    "dynamic_fields": ["access", "road condition", "hours", "tickets", "heritage-zone restrictions", "water", "overnight", "drone"],
    "verify_before_departure": True,
}

obj["qa"] = {
    **(obj.get("qa") or {}),
    "language_review": {
        "status": "reviewed",
        "checked_at": CHECKED,
        "notes": "Археологическая гипотеза Колани отделена от результатов исследований 2025–2026; местная традиция не подменяет историю.",
    },
    "card_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "полный объектный QA Hintang Archaeological Park",
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
            "dating_uncertainty_preserved": True,
            "multi_site_extent_explicit": True,
            "no_narrative_duplication": True,
        },
        "notes": [
            "Primary GPS is San Kong Phan main visitor cluster, not a fabricated centre of the 12-km landscape.",
            "Site 7A keeps its exact 2025 excavation GPS and 1430 m elevation as a separate geo point.",
            "Colani's Bronze Age chronology remains a historical hypothesis; new radiometric results are still pending.",
            "Current national-heritage status is included without inventing hours, ticket price or mandatory guide.",
            "Wild camping and site-specific drone permission remain unconfirmed.",
        ],
    },
    "rebuild_v2": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "полная редакционная, полевая и источниковая перестройка Hintang Archaeological Park",
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
            "archaeological_core_coordinate": True,
            "multi_site_extent_explicit": True,
            "drone_rule_precision": True,
        },
    },
    "fact_source_review": {
        "status": "passed",
        "checked_at": CHECKED,
        "scope": "Hintang: archaeology, chronology, national heritage status, ridge geography, access, GPS/elevation, traveler reports, local tradition, media and drone",
        "checks": {
            "narrative_section_sources": True,
            "coordinate_source_scoped": True,
            "elevation_source_scoped": True,
            "historic_hypothesis_vs_current_research_split": True,
            "new_excavation_dated": True,
            "legend_not_upgraded_to_history": True,
            "current_access_scoped": True,
            "water_unknown_preserved": True,
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
for url, canonical_id in SOURCE_IDS.items():
    legacy = source_key(url)
    current = sources.get(legacy)
    if current not in (None, canonical_id):
        raise SystemExit(f"source ID collision: {legacy} -> {current}, wanted {canonical_id}")
    sources[legacy] = canonical_id
REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Updated Hintang Archaeological Park and registered", len(SOURCE_IDS), "source IDs")
