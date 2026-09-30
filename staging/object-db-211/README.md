# Object DB full-rebuild staging

This branch is a non-live migration workspace for a **complete rebuild of the 211-object canonical object layer**.

## Target

- Source inventory: 211 unique objects across 11 countries.
- Target inventory: 211 canonical object cards.
- Existing cards in `main` are **source material only**. Their current schema/content is not the target contract.
- Future import strategy: atomically replace the complete canonical `objects/` layer after validation.
- Permanent object IDs are preserved/locked; slugs may change.
- No PR, no merge to `main`, no release-pointer promotion in this branch.

## Required target contract

Every rebuilt card must use:

`id → kind → slug → status → names → summary → classification → geo → narrative → visit → traveler_reports → visual_recon → media → relations → freshness → qa`

Facts belonging to lodging, POI, routes, media, sources or geo must live in their canonical entities and be referenced by ID rather than duplicated into object cards.

## Rules

1. Keep all 211 unique objects unless a duplicate/error is proven.
2. Rebuild **all 211 cards**, including BN/KH/ID/LA/MY/MM; do not copy their current live card shape as-is.
3. Reuse existing verified facts and sources where valid.
4. Do not invent GPS, elevation, distance, price, schedule, contact, camping legality, permits, legends, history or GPX.
5. Missing values stay `null` / `unknown` and must be reflected in QA.
6. Reconcile source/geo/lodging/media/route refs before import.
7. Build CDN → validate CDN → validate hierarchy on this branch only.
8. Only after all structural checks pass can the full object layer be considered safe for replacement in `main`.

## Import model

The intended later operation is not “113 old + 98 new”. It is:

`211 source objects → 211 rebuilt canonical cards → QA/validation → atomic replacement of the complete objects layer`.

