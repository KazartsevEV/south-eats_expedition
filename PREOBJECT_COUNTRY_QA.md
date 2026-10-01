# PRE-OBJECT / UPPER-LEVEL COUNTRY QA

## Цель этапа

Довести **верхний уровень всех 11 стран Юго-Восточной Азии** до единого стандарта до начала следующего прохода по карточкам объектов.

**Филиппины (PH) — единственный принятый эталон.**

Остальные 10 стран проходят повторный приёмочный цикл строго по очереди. Ранее сделанные country/geo PR сохраняются и переиспользуются, но сами по себе не считаются финальной приёмкой страны.

## Жёсткая граница этапа

На этом этапе **НЕ ТРОГАТЬ КАРТОЧКИ ОБЪЕКТОВ**.

Заморожены:
- `data/source/<country>.json -> objects` и любые объектные payload, если изменение не требуется исключительно для исправления доказанного broken reference;
- канонические `objects/**`;
- object narrative;
- object logistics;
- water/overnight у объектов;
- traveler reports объектов;
- visual_recon объектов;
- object media;
- object routes;
- object-level lodging/POI migration;
- reclassification объектов.

Не создавать новые достопримечательности, не удалять существующие, не переписывать карточки и не расширять их содержимое.

Если верхнеуровневая валидация ломается из-за объектной ссылки, допускается только минимальный reference-integrity fix без содержательной переработки карточки.

## Очередь

1. BN — Brunei
2. KH — Cambodia
3. LA — Laos
4. ID — Indonesia
5. MY — Malaysia
6. MM — Myanmar
7. SG — Singapore
8. TH — Thailand
9. TL — Timor-Leste
10. VN — Vietnam

PH — Philippines: reference / accepted.

Не перескакивать вперёд. Следующая страна начинается только после полного зелёного gate текущей.

## Что именно считается верхним уровнем

### 1. Country profile

Проверить и нормализовать:
- история;
- география и положение;
- рельеф;
- религии;
- языки;
- этнография;
- экономика;
- культура;
- кухня и street food;
- природные риски;
- опасные животные;
- ядовитые растения;
- общая транспортная связность;
- аэропорты и международное сообщение;
- сухопутные/морские границы;
- валюта и устойчивые справочные сведения.

Не дублировать один и тот же факт одновременно в profile, hierarchy metadata и derived views.

### 2. Climate

Структурировать:
- климатические зоны;
- месяцы;
- температура воздуха;
- температура воды там, где релевантно;
- осадки;
- муссоны;
- тайфуны/циклоны;
- сезонная доступность регионов;
- значимые региональные различия.

### 3. Travel rules

Проверить актуальные изменчивые поля:
- визы для граждан РФ;
- срок безвизового/визового пребывания;
- продление;
- visa run / border run;
- наземные погранпереходы;
- ограничения въезда;
- правила управления автомобилем/мопедом;
- camping rules верхнего уровня;
- drone rules верхнего уровня;
- permits;
- необычные правовые ограничения, реально значимые путешественнику.

У каждого изменчивого факта обязательны:
- `source_refs`;
- `checked_at`.

Не переносить старую формулировку как текущую без проверки.

### 4. Geo hierarchy

Проверять сверху вниз:

`country -> region/state/province -> district -> island/archipelago/protected/geographic area -> city/town/village/settlement`

Требования:
- стабильные ID;
- правильный parent;
- правильный geo kind;
- отсутствие attraction semantics в geo;
- отсутствие дублей;
- сохранение всех валидных существующих узлов.

### 5. Regional profiles

Для каждого включённого регионального/административного узла требуется:
- narrow/description;
- geography;
- climate;
- transport;
- provenance.source_refs;
- provenance.research_source_refs, где применимо;
- provenance.checked_at;
- freshness.checked_at.

Дополнительные разделы только при наличии материала:
- history;
- culture;
- geology;
- hydrology;
- nature;
- ethnography;
- religion;
- architecture;
- myths_beliefs;
- marine.

Не заполнять регион шаблонным текстом уровня страны.

### 6. Locality profiles

Для используемых city/town/village/settlement:
- narrow/summary;
- primary_location или явно документированное отсутствие координаты;
- geography;
- climate;
- transport;
- source_refs;
- checked_at/freshness.

Координата поселения — только центр/якорь поселения. Она никогда не заменяет GPS достопримечательности, входа, пирса, трейлхеда, вершины или водопада.

### 7. Geometry

Система координат: **WGS84 / EPSG:4326**.

Допустимо:
- sourced administrative boundary;
- sourced physical/protected-area boundary;
- упрощённая навигационная геометрия с явной provenance;
- approximate expedition mask только с `accuracy=approximate` и `coverage_basis`.

Запрещено:
- копировать polygon родителя в ребёнка ради закрытия QA gap;
- выдавать approximate mask за административную границу;
- заявлять cadastral/survey precision;
- подменять отсутствующую геометрию выдуманной.

Отсутствующая геометрия лучше ложной.

## Источники

Приоритет:
1. материалы проекта;
2. государственные и официальные источники;
3. национальные статистические/географические службы;
4. park authorities / local authorities;
5. UNESCO / музеи / археологические службы;
6. университеты и научные публикации;
7. OSM и авторитетные картографические источники;
8. качественные вторичные источники только там, где первичного нет.

Для актуальных правовых и транспортных правил приоритет всегда у текущего официального источника.

## Язык

Пользовательский текст — нормальный русский язык.

Не допускать англо-русской каши. Английские/местные формы оставлять только для:
- официальных названий;
- собственных имён;
- локальных терминов;
- транспортных систем;
- юридических терминов, если русский эквивалент искажает смысл.

## Порядок работы по стране

1. Audit текущего source/canonical/generated состояния.
2. Сверка со стандартом PH.
3. Country profile.
4. Climate.
5. Travel rules.
6. Geo hierarchy.
7. Regional profiles.
8. Locality profiles.
9. Geometry.
10. Source refs / freshness.
11. Build normalized CDN.
12. Build canonical CDN.
13. Build recursive hierarchy.
14. Validate country/regional layer.
15. Validate source/generated CDN.
16. Validate canonical contract.
17. Validate recursive hierarchy.
18. Build + validate derived maps.
19. Strict locality/geo validation.
20. Post-merge publish/read-model check.
21. Только после этого статус страны = complete и переход к следующей.

## Обязательный validation gate

После каждого country-changing batch:

```text
build CDN
-> build canonical CDN
-> build hierarchy
-> validate country layer
-> validate CDN
-> validate canonical
-> validate hierarchy
-> build/validate maps
-> validate locality --strict --strict-geo
```

Не переводить release/latest/current на новый набор данных, пока структурная валидация не прошла.

## Definition of Done — страна на этом этапе

Страна считается завершённой, только если:
- profile соответствует контракту;
- climate соответствует контракту;
- travel rules актуальны и имеют source_refs/checked_at;
- hierarchy непротиворечива;
- regional profiles заполнены по роли;
- locality profiles заполнены по роли;
- координаты поселений имеют правильную семантику;
- geometry честная и имеет provenance;
- нет доказанных дублей;
- валидные старые сущности не потеряны;
- производные search/views/maps получены только build-процессом;
- полный validation gate зелёный;
- после merge опубликованный read-model проверен;
- карточки объектов не изменялись содержательно.

## Текущий статус

- PH — reference / accepted.
- BN — complete (upper-level gate + post-merge publish green).
- KH — complete (upper-level acceptance recorded; full gate required on this PR).
- LA — complete (upper-level acceptance recorded; full gate required on this PR).
- ID — complete (upper-level acceptance recorded; full gate required on this PR).
- MY — complete (upper-level acceptance recorded; full gate required on this PR).
- MM — complete (upper-level acceptance recorded; full gate required on this PR).
- SG — active.
- TH — queued.
- TL — queued.
- VN — queued.

Ранее выполненные верхнеуровневые изменения в этих странах переиспользуются как заготовка, но каждая из десяти стран должна пройти новый полный приёмочный цикл по этому ТЗ.
