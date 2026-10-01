# Expedition South East — CDN v2.1 reference release

Release: `2026-09-28-r3`  
Schema: `2.1.0`

This is the canonical CDN read model for the five publishable countries (Brunei, Cambodia, Laos, Indonesia, Malaysia); Myanmar is held in migration QA until enrichment. Original country JSON remains the research/editorial source model.

## Layout

- `manifest.json` — release contract, hashes and cache classes.
- `home.json` — cover, SEA intro, navigation and featured cards.
- `countries.json` — clickable country cards.
- `object-types.json` + `collections/<type>.json` — real object classes (megaliths, national parks, cities, caves, etc.).
- `places.json` — global region/city-hub tag index.
- `taxonomy.json` — filter facets.
- `search/objects.json` / `search/places.json` — compact client search indexes without duplicated story prose.
- `countries/<cc>/country.json` — country narrative + entry/transport only.
- `countries/<cc>/places.json` — country regions and route hubs.
- `countries/<cc>/collections.json` — country objects grouped by object_type.
- `countries/<cc>/objects.json` — lightweight grid cards.
- `countries/<cc>/objects/<slug>.json` — lazy-loaded object detail.
- `schema/*.schema.json` — data contracts.
- `qa.json` — release gate.

## Semantic rules

1. `prominence` preserves source editorial rank (`major`, `expanded`, `non_touristy`, etc.).
2. `object_type` is the real browse class (`megalithic_site`, `national_park`, `historic_city`, etc.).
3. Story exists once in object detail (`story`). Source `why_go` and `narrow` are not copied into detail.
4. Grid cards contain only a short teaser.
5. Regions and city/route hubs are first-class linkable filter entities.
6. Search indexes contain keywords/facets, not duplicate full narratives.
7. A release is immutable; expansion to the remaining countries creates a new release using the same schema.
