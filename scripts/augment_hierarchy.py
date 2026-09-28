#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public" / "cdn" / "v2"

TARGET_COUNTRIES = [
    {"code":"BN","slug":"brunei","name_ru":"Бруней","name_en":"Brunei Darussalam","name_local":"Negara Brunei Darussalam","flag":"🇧🇳","subregions":["maritime"],"tags":["borneo","sultanate","rainforest","islamic_culture"]},
    {"code":"KH","slug":"cambodia","name_ru":"Камбоджа","name_en":"Cambodia","name_local":"កម្ពុជា","flag":"🇰🇭","subregions":["mainland"],"tags":["lower_mekong","khmer_culture","archaeology","tonle_sap"]},
    {"code":"ID","slug":"indonesia","name_ru":"Индонезия","name_en":"Indonesia","name_local":"Indonesia","flag":"🇮🇩","subregions":["maritime"],"tags":["archipelago","volcanism","islands","ethnography"]},
    {"code":"LA","slug":"laos","name_ru":"Лаос","name_en":"Lao People's Democratic Republic","name_local":"ລາວ","flag":"🇱🇦","subregions":["mainland"],"tags":["mekong","mountains","karst","buddhist_culture"]},
    {"code":"MY","slug":"malaysia","name_ru":"Малайзия","name_en":"Malaysia","name_local":"Malaysia","flag":"🇲🇾","subregions":["mainland","maritime"],"tags":["malay_peninsula","borneo","rainforest","multicultural"]},
    {"code":"MM","slug":"myanmar","name_ru":"Мьянма","name_en":"Myanmar","name_local":"မြန်မာ","flag":"🇲🇲","subregions":["mainland"],"tags":["irrawaddy","buddhist_culture","archaeology","mountains"]},
    {"code":"PH","slug":"philippines","name_ru":"Филиппины","name_en":"Philippines","name_local":"Pilipinas","flag":"🇵🇭","subregions":["maritime"],"tags":["archipelago","volcanism","reefs","austronesian_cultures"]},
    {"code":"SG","slug":"singapore","name_ru":"Сингапур","name_en":"Singapore","name_local":"Singapore / Singapura / 新加坡 / சிங்கப்பூர்","flag":"🇸🇬","subregions":["maritime"],"tags":["city_state","port","multicultural","urban_history"]},
    {"code":"TH","slug":"thailand","name_ru":"Таиланд","name_en":"Thailand","name_local":"ประเทศไทย","flag":"🇹🇭","subregions":["mainland"],"tags":["mainland","buddhist_culture","mountains","islands"]},
    {"code":"TL","slug":"timor-leste","name_ru":"Тимор-Лешти","name_en":"Timor-Leste","name_local":"Timor-Leste","flag":"🇹🇱","subregions":["maritime"],"tags":["lesser_sunda","mountains","reefs","austronesian_cultures"]},
    {"code":"VN","slug":"vietnam","name_ru":"Вьетнам","name_en":"Vietnam","name_local":"Việt Nam","flag":"🇻🇳","subregions":["mainland"],"tags":["annamite_range","red_river","mekong_delta","karst"]},
]

FAMILIES = [
    {"id":"built_heritage","label_ru":"Поселения и архитектурное наследие","description":"Города, историческая застройка, дворцы, фортификации, индустриальные и иные созданные человеком объекты.","types":["city","historic_city","historic_building","palace","fortification","colonial_architecture","industrial_heritage","monument","abandoned_site"]},
    {"id":"archaeology_memory","label_ru":"Археология, древность и историческая память","description":"Археологические комплексы, мегалиты, музеи и мемориальные места.","types":["archaeological_site","megalithic_site","museum","memorial_site"]},
    {"id":"religion_ethnography","label_ru":"Религия, этнография и живая культура","description":"Священные места, традиционные поселения, культурные ландшафты, рынки и ремесленные центры.","types":["religious_site","living_settlement","traditional_settlement","cultural_landscape","market","craft_center"]},
    {"id":"protected_ecosystems","label_ru":"Охраняемая природа и экосистемы","description":"Национальные парки, резерваты, леса, мангры, места наблюдения за дикой природой и крупные природные ландшафты.","types":["national_park","protected_area","wildlife_site","forest","mangrove","natural_landscape"]},
    {"id":"relief_geology","label_ru":"Рельеф и геология","description":"Горы, вулканы, плато, карст, пещеры и геологические объекты.","types":["mountain","volcano","plateau","karst","cave","geological_site"]},
    {"id":"water_coast_marine","label_ru":"Вода, побережья и морская среда","description":"Реки, озёра, водно-болотные угодья, водопады, острова, пляжи, рифы и дайв-сайты.","types":["river","lake","wetland","waterfall","island","beach","reef","diving_site","river_or_wetland","island_or_coast"]},
]

TRANSITIONAL_TYPES = {
    "natural_landscape":{"status":"transitional_broad_class","target_split":["mountain","plateau","karst","forest","geological_site"],"note_ru":"Слишком широкий исторический класс; объекты мигрируются в более точные классы по фактическому типу."},
    "river_or_wetland":{"status":"transitional_broad_class","target_split":["river","lake","wetland"],"note_ru":"Промежуточный класс старой схемы; должен исчезнуть после покарточной классификации."},
    "island_or_coast":{"status":"transitional_broad_class","target_split":["island","beach","reef","diving_site"],"note_ru":"Промежуточный класс старой схемы; должен быть разделён по реальному типу объекта."},
    "living_settlement":{"status":"transitional_overlap","target_split":["traditional_settlement"],"note_ru":"Старый класс сохраняется до проверки: в новой схеме поселение должно описываться как traditional_settlement, а живая культура — тегами и этнографическим блоком."},
}

PAGE_LAYOUTS = {
    "project":["hero","project_description","southeast_asia_intro","country_grid","taxonomy_families","geography_entry","search_entry"],
    "region":["hero","definition","mainland_and_maritime","natural_zones","climate","historical_layers","languages_religions_ethnicity","cross_border_movement","independent_expedition_context","country_grid"],
    "country":["hero","introduction","history","geography_relief","climate_seasonality","religions_ethnicity_languages","traveler_economy_currency_payments","entry_borders_air","internal_transport","risks_laws_animals_plants","food_festivals","camping_and_mobility","geography_grid","class_grid","object_grid"],
    "geography":["breadcrumb","identity","summary","child_geography","class_counts","object_grid"],
    "class":["breadcrumb","identity","definition","country_distribution","filters","object_grid"],
    "object":["breadcrumb","identity","gallery","story","access","walking","supply","overnight","accommodation","restrictions_cost_season","traveler_reports","visual_scouting","sources_and_verification"],
}

SEA_INTRO = {
    "title":"Что такое Юго-Восточная Азия",
    "definition":"Юго-Восточная Азия лежит между Индийским и Тихим океанами и образует переходную зону между материком Евразии и островным миром Малайского архипелага. Для экспедиционного планирования важнее не политическая рамка сама по себе, а сочетание крупных речных бассейнов, горных дуг, карстовых областей, вулканических островов, экваториальных лесов и густо заселённых дельт.",
    "mainland_and_maritime":"Материковая ЮВА включает прежде всего Мьянму, Таиланд, Лаос, Камбоджу и Вьетнам; Малайзия связывает материковую и островную части региона. Морская ЮВА охватывает Бруней, Индонезию, Филиппины, Сингапур, Тимор-Лешти и островную часть Малайзии. Это различие влияет на логистику: на материке маршруты часто строятся вдоль речных долин и сухопутных границ, на архипелагах — вокруг паромов, малых лодок и внутренних перелётов.",
    "natural_zones":"Регион включает влажные тропические леса, муссонные леса, мангры, известняковый карст, высокогорья, действующие вулканические дуги, коралловые рифы, крупные речные системы и сезонно затапливаемые равнины. Поэтому один и тот же календарный месяц даёт совершенно разные полевые условия на Борнео, в горах северного Индокитая и на островах восточной Индонезии.",
    "climate":"Большая часть региона тропическая, но практическая сезонность определяется не простой парой «сухо/дождливо», а направлением муссонов, высотой, экспозицией склонов и положением относительно моря. Для маршрутов критичны состояние грунтовых дорог, уровень рек, работа лодочных переправ, видимость в горах, прозрачность воды и сезон лесных пожаров или дымки.",
    "historical_layers":"В регионе накладываются древние торговые сети Индийского океана и Южно-Китайского моря, индуистско-буддийские государства, исламские султанаты, китайские торговые диаспоры, местные горные и островные культуры, европейские колониальные системы и постколониальные государства. Поэтому археологический комплекс, портовый квартал, храмовый ландшафт и традиционная деревня часто являются частями одной исторической системы, а не изолированными «достопримечательностями».",
    "languages":"Языковая карта включает австроазиатские, тай-кадайские, сино-тибетские, австронезийские и другие языковые семьи. Национальный язык редко исчерпывает полевую реальность: в удалённых районах название деревни, тропы или реки может существовать в нескольких вариантах, а практическая коммуникация зависит от конкретной этнической территории.",
    "religions":"Буддизм тхеравады определяет значительную часть материкового культурного ландшафта; ислам особенно важен в Малайзии, Брунее и Индонезии; христианство широко представлено на Филиппинах и в Тимор-Лешти. Одновременно сохраняются локальные анимистические культы, культ предков и смешанные ритуальные системы, которые нельзя сводить к официальной религиозной статистике.",
    "ethnicity":"Этническое разнообразие особенно важно вне столиц: горные группы материка, народы Борнео, Папуа, Сулавеси, Малых Зондских островов и северных Филиппин сохраняют собственные языки, архитектуру, земельные практики и ритуалы. В справочнике этнография привязывается к конкретному месту и сообществу, а не добавляется как декоративный общий текст.",
    "movement":"Перемещение между странами сочетает развитые авиахабы с наземными переходами, железными дорогами, автобусами, паромами и локальными лодочными линиями. Для полевой поездки важнее формального наличия дороги её фактическая проходимость, режим границы, возможность вывезти мотоцикл, сезонность парома и наличие обратного транспорта.",
    "independent_travel":"Справочник исходит из автономного маршрута: общественный транспорт, мопед или мотоцикл, лодка, пеший подход, палатка и локальные услуги по необходимости. Длинный переход, многодневность и отсутствие туристической инфраструктуры фиксируются как параметры, а не как причины исключить объект.",
}

def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def refresh_manifest(release: Path, extra_totals: dict):
    manifest_path = release / "manifest.json"
    manifest = load(manifest_path)
    files = []
    for path in sorted(release.rglob("*.json")):
        if path.name == "manifest.json":
            continue
        payload = path.read_bytes()
        files.append({"path":path.relative_to(release).as_posix(),"bytes":len(payload),"sha256":hashlib.sha256(payload).hexdigest()})
    manifest["files"] = files
    manifest.setdefault("totals", {}).update(extra_totals)
    manifest["totals"]["files"] = len(files)
    dump(manifest_path, manifest)

def main():
    latest = load(PUBLIC / "latest.json")
    release = PUBLIC / latest["release_id"]
    countries_data = load(release / "countries.json")["countries"]
    type_rows = load(release / "object-types.json")["object_types"]
    objects = load(release / "search" / "objects.json")["objects"]
    places = load(release / "places.json")["places"]

    published = {row["country_code"]: row for row in countries_data}
    objects_by_id = {row["id"]: row for row in objects}
    objects_by_country = defaultdict(list)
    objects_by_country_type = defaultdict(list)
    for row in objects:
        objects_by_country[row["country_code"]].append(row)
        objects_by_country_type[(row["country_code"], row["object_type"])].append(row)

    places_by_country = defaultdict(list)
    for row in places:
        places_by_country[row["country_code"]].append(row)

    type_by_value = {row["value"]: row for row in type_rows}
    family_by_type = {}
    for family in FAMILIES:
        for t in family["types"]:
            if t in family_by_type:
                raise RuntimeError(f"object type assigned to two families: {t}")
            family_by_type[t] = family["id"]
    unknown_types = sorted(set(type_by_value) - set(family_by_type))
    if unknown_types:
        raise RuntimeError(f"unclassified object types in hierarchy: {unknown_types}")

    country_cards = []
    for meta in TARGET_COUNTRIES:
        src = published.get(meta["code"])
        available = bool(src)
        country_cards.append({
            "id":f"country:{meta['code'].lower()}","country_code":meta["code"],"slug":meta["slug"],
            "name_ru":meta["name_ru"],"name_en":meta["name_en"],"name_local":meta["name_local"],"flag":meta["flag"],
            "subregions":meta["subregions"],"tags":meta["tags"],"available":available,
            "status":"published" if available else "pending_source_migration",
            "summary":src.get("summary") if src else None,"cover":src.get("cover") if src else None,
            "page_path":f"pages/countries/{meta['slug']}.json",
        })

    project = {
        "meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"page_type":"project"},
        "identity":{"title":"Expedition South East","subtitle":"Экспедиционный справочник по Юго-Восточной Азии для самостоятельного полевого путешествия","description":"Единая база мест, маршрутов и практической полевой информации: история, археология, этнография, геология, природа, транспорт, пеший доступ, вода, ночёвка и визуальная разведка без пакетно-туристической оптики."},
        "hero":{"url":"https://upload.wikimedia.org/wikipedia/commons/d/de/Southeast_Asia_location_map.svg","source_page":"https://commons.wikimedia.org/wiki/File:Southeast_Asia_location_map.svg","provider":"Wikimedia Commons","license":"Public domain","artist":"Hariboneagle927","kind":"regional_map"},
        "layout":"project","region_page":"region/southeast-asia.json","countries":country_cards,
        "taxonomy_tree":"taxonomy/tree.json","geography_tree":"geography/tree.json","navigation_tree":"navigation/tree.json","page_layouts":"page-layouts.json",
    }
    dump(release / "project.json", project)
    dump(release / "region" / "southeast-asia.json", {
        "meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"page_type":"region","id":"region:southeast-asia"},
        "identity":{"name_ru":"Юго-Восточная Азия","name_en":"Southeast Asia","slug":"southeast-asia"},"layout":"region","hero":project["hero"],"content":SEA_INTRO,
        "subregions":[{"id":"mainland","label_ru":"Материковая Юго-Восточная Азия","country_codes":["MM","TH","LA","KH","VN","MY"]},{"id":"maritime","label_ru":"Островная и морская Юго-Восточная Азия","country_codes":["BN","ID","MY","PH","SG","TL"]}],
        "countries":country_cards,
    })
    dump(release / "page-layouts.json", {"meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"]},"layouts":PAGE_LAYOUTS})

    taxonomy_families = []
    taxonomy_nodes = 1
    for family in FAMILIES:
        children = []
        for t in family["types"]:
            row = type_by_value.get(t)
            count = row["count"] if row else 0
            label = row["label_ru"] if row else t
            transitional = TRANSITIONAL_TYPES.get(t)
            node = {"id":f"class:{t}","kind":"object_class","value":t,"label_ru":label,"count":count,"page_path":f"pages/classes/{t}.json","collection_path":f"collections/{t}.json" if row else None,"status":transitional["status"] if transitional else "canonical_leaf"}
            if transitional:
                node["migration"] = transitional
            children.append(node); taxonomy_nodes += 1
        taxonomy_families.append({"id":f"family:{family['id']}","kind":"class_family","value":family["id"],"label_ru":family["label_ru"],"description":family["description"],"count":sum(x["count"] for x in children),"children":children})
        taxonomy_nodes += 1

    dump(release / "taxonomy" / "tree.json", {"meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"tree_kind":"object_taxonomy"},"root":{"id":"taxonomy:objects","kind":"taxonomy_root","label_ru":"Классы объектов","rule":"Каждый объект имеет один основной класс; семейства служат только для навигации и не заменяют primary class.","children":taxonomy_families}})

    for family in taxonomy_families:
        for node in family["children"]:
            t=node["value"]; rows=[o for o in objects if o["object_type"]==t]; country_counts=Counter(o["country_code"] for o in rows)
            dump(release / "pages" / "classes" / f"{t}.json", {
                "meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"page_type":"class","id":node["id"]},
                "identity":{"value":t,"label_ru":node["label_ru"],"family_id":family["id"],"status":node["status"]},"layout":"class",
                "definition":family["description"],"migration":node.get("migration"),"count":len(rows),
                "country_distribution":[{"country_code":k,"count":v} for k,v in sorted(country_counts.items())],
                "objects":[{"id":o["id"],"name":o["name"],"country_code":o["country_code"],"region":o.get("region"),"narrow":o.get("narrow"),"detail_path":o["detail_path"]} for o in rows],
            })

    geography_children=[]; geography_nodes=1; place_page_count=0
    for meta in TARGET_COUNTRIES:
        code=meta["code"]; cplaces=sorted(places_by_country.get(code,[]),key=lambda x:(x.get("kind") or "",x.get("name") or "")); child_refs=[]
        for place in cplaces:
            page_path=f"pages/geography/{meta['slug']}/{place['kind']}/{place['slug']}.json"
            child_refs.append({"id":place["id"],"kind":place["kind"],"name":place["name"],"slug":place["slug"],"page_path":page_path,"object_count":len(place.get("object_ids") or [])})
            geography_nodes += 1; place_page_count += 1
            pobj=[objects_by_id[oid] for oid in place.get("object_ids") or [] if oid in objects_by_id]; class_counts=Counter(o["object_type"] for o in pobj)
            dump(release / page_path, {
                "meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"page_type":"geography","id":place["id"]},
                "identity":{"name":place["name"],"kind":place["kind"],"slug":place["slug"],"country_code":code},"layout":"geography",
                "parent":{"id":f"country:{code.lower()}","page_path":f"pages/countries/{meta['slug']}.json"},
                "source_profile":{k:v for k,v in place.items() if k not in {"object_ids","country_code","country_slug"}},
                "parentage_status":"country_parent_confirmed; lower administrative nesting not inferred without source evidence",
                "class_counts":[{"object_type":k,"label_ru":type_by_value.get(k,{}).get("label_ru",k),"count":v} for k,v in sorted(class_counts.items())],
                "objects":[{"id":o["id"],"name":o["name"],"object_type":o["object_type"],"narrow":o.get("narrow"),"detail_path":o["detail_path"]} for o in pobj],
            })
        geography_children.append({"id":f"country:{code.lower()}","kind":"country","name":meta["name_ru"],"slug":meta["slug"],"page_path":f"pages/countries/{meta['slug']}.json","status":"published" if code in published else "pending_source_migration","children":child_refs}); geography_nodes += 1

    dump(release / "geography" / "tree.json", {"meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"tree_kind":"geography","allowed_kinds":["macroregion","country","region","province","state","district","island","city","village","traditional_settlement","geographic_area","city_or_route_hub"]},"root":{"id":"geo:southeast-asia","kind":"macroregion","name":"Юго-Восточная Азия","page_path":"region/southeast-asia.json","children":geography_children}})

    nav_country_children=[]
    for meta in TARGET_COUNTRIES:
        code=meta["code"]; src=published.get(code); cobjects=objects_by_country.get(code,[]); cplaces=sorted(places_by_country.get(code,[]),key=lambda x:(x.get("kind") or "",x.get("name") or "")); present_types=sorted(set(o["object_type"] for o in cobjects))
        class_rows=[]; class_nav=[]
        for t in present_types:
            rows=objects_by_country_type[(code,t)]
            class_rows.append({"object_type":t,"label_ru":type_by_value[t]["label_ru"],"count":len(rows),"global_page_path":f"pages/classes/{t}.json"})
            class_nav.append({"id":f"country-class:{code.lower()}:{t}","kind":"country_class","label_ru":type_by_value[t]["label_ru"],"object_type":t,"children":[{"id":o["id"],"kind":"object","name":o["name"],"path":o["detail_path"]} for o in rows]})
        geography_rows=[{"id":p["id"],"kind":p["kind"],"name":p["name"],"page_path":f"pages/geography/{meta['slug']}/{p['kind']}/{p['slug']}.json","object_count":len(p.get("object_ids") or [])} for p in cplaces]
        dump(release / "pages" / "countries" / f"{meta['slug']}.json", {
            "meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"page_type":"country","id":f"country:{code.lower()}"},
            "identity":{"country_code":code,"slug":meta["slug"],"name_ru":meta["name_ru"],"name_en":meta["name_en"],"name_local":meta["name_local"],"flag":meta["flag"],"subregions":meta["subregions"],"tags":meta["tags"]},
            "layout":"country","status":"published" if src else "pending_source_migration","hero":src.get("cover") if src else None,"summary":src.get("summary") if src else None,"content_ref":src.get("country_path") if src else None,
            "geography":geography_rows,"classes":class_rows,"objects_count":len(cobjects),
            "migration_note":None if src else "Исходный страновой файл ещё не перенесён в Git/CDN; страница существует как узел общей архитектуры без выдуманного содержимого.",
        })
        nav_country_children.append({
            "id":f"country:{code.lower()}","kind":"country","name":meta["name_ru"],"path":f"pages/countries/{meta['slug']}.json","status":"published" if src else "pending_source_migration",
            "children":[
                {"id":f"branch:{code.lower()}:geography","kind":"navigation_branch","label_ru":"География","children":[{"id":p["id"],"kind":p["kind"],"name":p["name"],"path":f"pages/geography/{meta['slug']}/{p['kind']}/{p['slug']}.json","children":[{"id":oid,"kind":"object_ref","path":objects_by_id[oid]["detail_path"]} for oid in p.get("object_ids") or [] if oid in objects_by_id]} for p in cplaces]},
                {"id":f"branch:{code.lower()}:classes","kind":"navigation_branch","label_ru":"Классы объектов","children":class_nav},
            ],
        })

    dump(release / "navigation" / "tree.json", {"meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"],"tree_kind":"site_navigation"},"root":{"id":"project:expedition-south-east","kind":"project","name":"Expedition South East","path":"project.json","children":[{"id":"region:southeast-asia","kind":"region","name":"Юго-Восточная Азия","path":"region/southeast-asia.json","children":nav_country_children}]}})

    dump(release / "hierarchy-status.json", {
        "meta":{"schema_version":latest["schema_version"],"release_id":latest["release_id"]},
        "order":["project","region","country_catalog","taxonomy_families","geography_contract","country_pages","geography_pages","object_classes","object_cards"],
        "levels":{
            "project":{"status":"complete"},"region":{"status":"complete"},
            "country_catalog":{"status":"complete","total":len(TARGET_COUNTRIES),"published":len(published)},
            "taxonomy_families":{"status":"complete","families":len(FAMILIES),"classes":sum(len(f["types"]) for f in FAMILIES)},
            "geography_contract":{"status":"complete","nodes":geography_nodes,"note":"Иерархия ниже уровня страны пока не угадывается: старые route-region/hub узлы сохраняются до доказанной административной нормализации."},
            "country_pages":{"status":"in_progress","published":len(published),"placeholders":len(TARGET_COUNTRIES)-len(published)},
            "geography_pages":{"status":"generated_from_existing_source","count":place_page_count},
            "object_classes":{"status":"formalized_with_transitional_legacy_types"},
            "object_cards":{"status":"lower_branch_migration_in_progress"},
        },
        "next_descent_rule":"После QA уровня переходить только к его детям: страна → география/класс → объект.",
    })
    refresh_manifest(release,{"target_countries":len(TARGET_COUNTRIES),"taxonomy_families":len(FAMILIES),"taxonomy_nodes":taxonomy_nodes,"geography_nodes":geography_nodes,"geography_pages":place_page_count})

if __name__ == "__main__":
    main()
