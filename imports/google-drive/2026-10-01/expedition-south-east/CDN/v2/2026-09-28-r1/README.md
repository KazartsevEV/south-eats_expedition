# Expedition South East — CDN v2

Release: `2026-09-28-r1`  
Schema: `2.0.0`

This directory is the CDN-ready read model. Original country JSON files remain the editorial/source model.

## Layout

- `manifest.json` — release contract, hashes, cache classes.
- `home.json` — homepage payload.
- `countries.json` — country index.
- `taxonomy.json` — global facets.
- `search/objects.json` — client-side search corpus.
- `countries/<cc>/country.json` — country narrative + entry/transport; no object blobs.
- `countries/<cc>/regions.json` — regions/localities.
- `countries/<cc>/objects.json` — lightweight cards for lists/maps/filters.
- `countries/<cc>/objects/<slug>.json` — lazy-loaded object detail.
- `schema/*.schema.json` — contract schemas.
- `qa.json` — release gate.

## Rules

1. A release is immutable. New data => new `release_id`.
2. Lists never download full country monoliths.
3. Object detail is lazy-loaded.
4. Search/taxonomy are independent global payloads.
5. Every image reference carries provenance/license when known.
6. Dynamic fields keep dated verification/source metadata.
7. Source country JSON remains editorial truth; CDN files are generated derivatives.
