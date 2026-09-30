# SEA pre-object geo-QA rollout

Updated: 2026-10-01

## Purpose

Bring every Southeast Asia country already present in the repository to the same canonical pre-object geography standard before any further object-card migration or object-card redesign.

Philippines is the reference implementation. Existing country, regional, locality, source and object data must be preserved. Existing nodes may be removed only when a duplicate or factual/schema error is proven.

Object cards remain frozen until the complete country queue below has passed this phase.

## Canonical ownership

Facts must have one canonical owner.

- Country-wide facts: `data/source/<country>.json` country layer.
- Administrative/physical hierarchy and stable geo IDs: `data/hierarchy/countries/<country>.json`.
- Researched regional/locality content: canonical source layer; hierarchy may hold canonical regional profiles where that is already the country pattern, but the same narrative must not be duplicated across both layers.
- Boundary geometry: `data/geo/nodes/<geo_id>.geojson`.
- Generated CDN, search, views, QA and maps are derived output and are never hand-edited.

## Required role contracts

### regional_profile

A node treated as a researched region/province/state/district/physical expedition area must resolve in the canonical CDN to:

- `description.narrow`;
- `geography`;
- `climate`;
- `transport`;
- `provenance.source_refs`;
- `provenance.research_source_refs`;
- `provenance.checked_at`;
- `freshness.checked_at`.

Additional sections are included only when source-supported: history, culture, geology, hydrology, nature, ethnography, religion, architecture, myths_beliefs, marine, hazards/health where the country model supports them.

### locality_profile

Every included city/town/village/settlement used as a route or logistics node must resolve to:

- `description.narrow`;
- `primary_location`, or an explicit sourced reason it is unavailable;
- `geography`;
- `climate`;
- `transport`;
- `provenance.source_refs`;
- `provenance.research_source_refs`;
- `provenance.checked_at`;
- `freshness.checked_at`.

Settlement coordinates are map/logistics anchors only. They must never substitute for attraction entrances, trailheads, piers, summits, viewpoints or other object coordinates.

### geometry

Published geometry uses WGS84 / EPSG:4326.

- Administrative boundaries: `simplified_sourced_boundary` when provenance is sufficient.
- Physical/expedition composites: `approximate` unless an independent legal/physical boundary exists.
- Current administrative identity and codes must be separated from older boundary-vintage codes where boundaries come from an older dataset.
- Never clone a parent boundary into a composite expedition node merely to avoid `null`.
- Never claim cadastral/survey precision for simplified navigation masks.
- If no defensible geometry exists, keep geometry absent and explain the QA state rather than inventing a polygon.

## Source priority

Use, in order:

1. project materials already collected;
2. government / official statistical / administrative sources;
3. park authorities, museums, archaeology/heritage bodies, UNESCO;
4. academic/university sources;
5. authoritative map/OSM-type sources for geometry/anchors;
6. independent traveler reports;
7. forums, Reddit, blogs, YouTube, Google Maps and local social sources only for appropriate traveler-report or practical context.

Do not invent GPS, elevations, route distances, prices, schedules, contacts, permits, camping legality, legends or historical facts.

## Per-country execution order

For each country, work top-down and do not skip levels:

1. Audit source layer, hierarchy, generated QA and current CDN output.
2. Preserve IDs and existing nodes; repair hierarchy/parentage only when verified.
3. Fill top administrative/regional profiles.
4. Fill included child administrative and physical-area profiles.
5. Fill city/town/village/settlement locality profiles and settlement GPS anchors.
6. Add sourced administrative geometry and defensible physical/expedition masks.
7. Separate current administrative changes from geometry source vintage.
8. Run full role-contract audit for regional/locality coverage.
9. Build normalized CDN.
10. Build canonical CDN.
11. Build recursive hierarchy.
12. Validate country/regional layer.
13. Validate source and generated CDN.
14. Validate canonical CDN contract.
15. Validate recursive hierarchy.
16. Build and validate derived maps.
17. Merge only after green CI.
18. Run post-merge audit and verify published read-model.
19. Mark country `geo_profile_qa_complete_before_object_cards`.
20. Move to the next country.

## Global exit criteria

The pre-object phase is complete only when every country in the queue below satisfies all of the following:

- country layer valid;
- all required hierarchy nodes resolve to the correct coverage role;
- all included administrative/regional nodes have complete sourced regional profiles;
- all included settlement nodes have complete sourced locality profiles;
- geometry exists where defensible, with explicit approximation where appropriate;
- remaining geometry nulls are intentional and documented;
- source refs and checked_at/freshness are intact;
- generated search/views/maps match canonical data;
- full build/validate/hierarchy/derived-map CI is green;
- object-card payloads were not modified during this phase.

## Country queue

PH is the reference implementation and is already complete.

1. **BN — Brunei** — verify-only; pre-object geo QA already complete.
2. **KH — Cambodia** — verify-only; pre-object geo QA already complete.
3. **LA — Laos** — active work.
4. **ID — Indonesia** — queued after Laos.
5. **MY — Malaysia** — queued.
6. **MM — Myanmar** — queued.
7. **SG — Singapore** — queued.
8. **TH — Thailand** — queued.
9. **TL — Timor-Leste** — queued.
10. **VN — Vietnam** — queued.

## Current inventory snapshot

| Country | Geo nodes | Existing profile-bearing hierarchy nodes | Geometry nodes | Current state |
|---|---:|---:|---:|---|
| BN | 11 | 5 | 7 | complete / verify-only |
| KH | 18 | 8 | 14 | complete / verify-only |
| LA | 25 | 0 | 0 | active |
| ID | 14 | 0 | 0 | queued |
| MY | 32 | 0 | 0 | queued |
| MM | 27 | 0 | 0 | queued |
| SG | 22 | 0 | 0 | queued |
| TH | 58 | 0 | 0 | queued |
| TL | 35 | 0 | 0 | queued |
| VN | 75 | 0 | 0 | queued |
| PH | 68 | 34 hierarchy profiles + 17 canonical locality profiles | 63 | reference complete |

The inventory count is diagnostic only. A country is not complete because the raw count is high; completion is determined by the role contract and green validation.
