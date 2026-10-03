#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "laos.json"
CHECKED = "2026-10-03"

def find_object(node, name):
    if isinstance(node, dict):
        if node.get("name") == name:
            return node
        for value in node.values():
            found = find_object(value, name)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_object(value, name)
            if found is not None:
                return found
    return None

def sections(obj):
    rows = (((obj.get("traveler_card") or {}).get("annotation") or {}).get("sections") or [])
    return {x.get("section_id"): x for x in rows if isinstance(x, dict) and x.get("section_id")}

data = json.loads(SOURCE.read_text(encoding="utf-8"))

nam = find_object(data, "Nam Kan Provincial Protected Area")
hin = find_object(data, "Hintang Archaeological Park")
if nam is None or hin is None:
    raise SystemExit("target object missing")

# Nam Kan: replace low-resolution gallery sources with original official media.
nam_gallery = [
    "https://www.gibbonexperience.org/wp-content/uploads/2023/11/THE-GIBBON-EXPERIENCE-TH5.jpg",
    "https://www.gibbonexperience.org/wp-content/uploads/2023/08/YKL2863.jpg",
    "https://www.gibbonexperience.org/wp-content/uploads/2023/08/Express-TH2_02.jpg",
    "https://www.gibbonexperience.org/wp-content/uploads/2019/09/TH-night.jpg",
    "https://www.gibbonexperience.org/wp-content/uploads/2019/09/Zipline-1345.jpg",
]
nam["illustration"] = {
    "static_url": nam_gallery[0],
    "source_page": "https://www.gibbonexperience.org/",
    "provider": "Gibbon Experience",
    "license": "reuse_terms_unverified",
    "artist": None,
    "illustration_scope": "Nam Kan National Protected Area / Gibbon Experience",
    "last_checked": CHECKED,
    "gallery": [
        {
            "static_url": url,
            "source_page": "https://www.gibbonexperience.org/",
            "provider": "Gibbon Experience",
            "license": "reuse_terms_unverified",
            "artist": None,
            "last_checked": CHECKED,
        }
        for url in nam_gallery
    ],
}
nlog = nam["traveler_card"]["logistics"]
if isinstance(nlog.get("water_structured"), dict):
    nlog["water_structured"]["notes"] = (
        "Питьевой считается только вода, которую выдаёт Gibbon Experience. Воду из ручьёв и рек внутри парка без обработки не использовать."
    )
    nlog["water_structured"]["last_reliable_point"] = "организованная инфраструктура Gibbon Experience"
for opt in nlog.get("access_options") or []:
    if opt.get("origin") == "Houay Xay — офис Gibbon Experience":
        opt["origin"] = "Хуайсай — офис Gibbon Experience"

# Hintang: natural Russian place names in user-facing copy.
hsec = sections(hin)
hsec["overview"]["content"] = (
    "Хинтанг — не один «парк с камнями», а цепь отдельных групп, растянутая по горным гребням примерно на 12 км. "
    "Исследователи зафиксировали более 70 участков, свыше 1500 стоячих плит и около 150 каменных дисков. "
    "Самый понятный для самостоятельного посещения участок — Сан-Конг-Пхан (Ban Pa Cha)."
)
hsec["history"]["content"][2]["text"] = (
    "На участке 7A в 2025 году нашли обычную керамику, перфорированный сланцевый диск и более поздний фрагмент глазурованной чаши, вероятно XV–XVI веков. "
    "Поздняя керамика не датирует сами менгиры; она показывает, что место использовали или тревожили спустя много веков."
)
hsec["geography"]["content"] = (
    "Комплексы лежат на высоких гребнях и седловинах района Хуамыанг. Сан-Конг-Пхан находится примерно на 1450 м. "
    "От Бан-Пхао к нему идёт крутая грунтовая дорога с набором около 350 м, а дальше можно продолжить пешком по лесному гребню к Кео-Хинтангу и другим группам."
)
hsec["geology"]["content"] = (
    "Стоячие камни в основном сделаны из слюдяного сланца. У Вьенг-Нок-Кхум археологи отметили возможный древний карьер — важная подсказка к тому, "
    "откуда брали материал. Но состав камня сам по себе не отвечает на главный вопрос: когда именно поставили плиты."
)
hsec["myths_beliefs"]["content"][0]["text"] = (
    "В одной из записанных традиций народа Phong камни связывают с правителем Хат-Ангом. По рассказу, плиты готовили для его дворца, "
    "но работы бросили после гибели правителя и разрушения его башни. Это местное предание, а не объяснение, подтверждённое раскопками."
)

hlog = hin["traveler_card"]["logistics"]
hlog["access"] = (
    "Из Сам-Ныа едут по Route 6 к Бан-Пхао. Оттуда до Сан-Конг-Пхана остаётся примерно 5,5–6 км крутой грунтовой дороги. "
    "В сухую погоду этот участок проезжаем, после дождя быстро становится тяжёлым."
)
hlog["public_transport"] = (
    "Есть старый подтверждённый опыт поездки рейсовым транспортом по Route 6 до Бан-Пхао с дальнейшим пешим подъёмом, "
    "но актуальное расписание на 2026 год не найдено. На него нельзя рассчитывать без проверки в Сам-Ныа."
)
hlog["last_mile"] = (
    "Последние 5,5–6 км идут вверх по грунтовке. Полевой трек 2014 года дал около 350 м набора и примерно 1,5 часа пешком. "
    "После дождя дорога раскисает; 4×4 заметно надёжнее обычной машины."
)
hlog["permit_or_guide"] = (
    "Для Сан-Конг-Пхана обязательный гид в открытых источниках не указан. Но после присвоения национального охранного статуса в 2026 году "
    "правила отдельных зон могут меняться, особенно рядом с исследовательскими участками."
)
hlog["overnight_and_camping"] = (
    "Официальный кемпинг среди мегалитов не найден. Разрешённость свободной ночёвки в охранной зоне не подтверждена; обычная база для поездки — Сам-Ныа."
)
hlog["travel_model"] = (
    "Сан-Конг-Пхан подходит для самостоятельного дневного выезда. Лесные группы требуют больше времени, уверенной навигации и проверки текущих ограничений."
)
if isinstance(hlog.get("water_structured"), dict):
    hlog["water_structured"]["last_reliable_point"] = "Сам-Ныа"
for opt in hlog.get("access_options") or []:
    if opt.get("origin") == "Sam Neua":
        opt["origin"] = "Сам-Ныа"
    elif opt.get("origin") == "Hintang forest trailhead":
        opt["origin"] = "начало лесной тропы Хинтанг"
    for leg in opt.get("legs") or []:
        if isinstance(leg.get("navigation"), str):
            leg["navigation"] = (
                leg["navigation"]
                .replace("Ban Phao", "Бан-Пхао")
                .replace("San Kong Phan", "Сан-Конг-Пхан")
                .replace("Keohintang", "Кео-Хинтанг")
                .replace("Ban Tao Hin", "Бан-Тао-Хин")
            )
hcard = hin["traveler_card"]
hcard["traveler_reports"][0]["summary"] = (
    "В июле 2014 года путешественник доехал общественным транспортом до Бан-Пхао, поднялся 5,5 км пешком к Сан-Конг-Пхану, "
    "а затем прошёл ещё 4,4 км по лесной тропе через Кео-Хинтанг до Бан-Тао-Хина. По его описанию, открытый подъём по грунтовке оказался тяжелее лесной части."
)

SOURCE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Upgraded Nam Kan media and polished Russian place-name rendering")
