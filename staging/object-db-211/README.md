# Full object-layer rebuild staging

This branch is a non-live workspace for rebuilding the complete expedition object-card layer before an eventual atomic replacement in `main`.

> **Inventory correction:** the directory name `object-db-211` is historical. A branch audit found additional researched objects that had never reached `main`. The authoritative target is now **248 unique object cards**.

## Confirmed inventory

- BN: 18
- KH: 19
- ID: 21
- LA: 31
- MY: 46
- MM: 15
- PH: 19
- SG: 18
- TH: 21
- TL: 17
- VN: 23
- **Total: 248**

The original 211-object inventory was incomplete:
- Laos: 19 → **31** after recovering 12 researched cards from `draft/laos-canonical-r41`.
- Malaysia: 21 → **46 unique** after reconciling the 40-object `draft/malaysia-cdn-after-laos` line with six additional unique objects from `draft/malaysia-canonical-r40`.

All branches containing `laos` and `malaysia` in their names were checked. No Laos branch exceeded 31. Malaysia had a 40-object line and a different 37-object line; their union after entity-level deduplication is 46.

## Target

`248 source objects → 248 rebuilt canonical cards → factual QA → ref reconciliation → build/validate/hierarchy → atomic replacement of the complete objects layer`.

Existing cards in `main` are source material only, not the target schema.

## Required card contract

`id → kind → slug → status → names → summary → classification → geo → narrative → visit → traveler_reports → visual_recon → media → relations → freshness → qa`

Facts belonging to geo, lodging, POI, routes, media or sources must ultimately live in their canonical entities and be referenced by ID.

## Current rebuild status

- BN: 18/18 structurally rebuilt.
- KH: 19/19 structurally rebuilt; factual QA: 0 passed, 19 incomplete (overnight evidence, traveler-report provenance).
- ID: 21/21 structurally rebuilt; factual QA: 0 passed, 21 incomplete (overnight/traveler provenance; 15 visual-recon gaps; 1 elevation gap).
- MM: 15/15 structurally rebuilt; factual QA: 0 passed, 15 incomplete (elevation/overnight/traveler/visual gaps; 10 water; 2 access).
- PH: 19/19 structurally rebuilt; factual gaps retained for geo/GPS/elevation/access/water/overnight/traveler/visual evidence.
- LA: 31/31 structurally rebuilt; 26 passed factual QA, 5 remain incomplete for real missing evidence.
- MY: 46/46 structurally rebuilt; factual QA remains intentionally incomplete where evidence for elevation/visual recon is absent.
- Other countries: inventory preserved; full contract rebuild still pending.

## Safety rules

1. Do not remove an object unless a duplicate/error is proven.
2. Preserve permanent object IDs; slugs may change.
3. Do not invent GPS, elevation, distance, price, schedule, contact, camping legality, permits, legends, history or GPX.
4. Missing values stay `null` / `unknown` and are reflected in QA.
5. Reconcile source/geo/lodging/media/route refs before import.
6. Run build CDN → validate CDN → validate hierarchy on this branch.
7. Do not create a PR, merge to `main`, or promote `latest/current` until the replacement layer is structurally valid.
