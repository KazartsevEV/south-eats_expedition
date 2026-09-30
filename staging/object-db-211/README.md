# Object DB consolidation staging

This branch is a non-live migration workspace. It restores the project Drive object inventory to 211 objects without changing release pointers, opening a PR, or merging to main.

## Inventory

- Existing canonical objects in main: 113 (BN, KH, ID, LA, MY, MM).
- Restored source objects: 98 (PH, SG, TH, TL, VN).
- Project object inventory after source recovery: 211.

## Staging contract

Each staged object follows the approved canonical top-level structure: id, kind, slug, status, names, summary, classification, geo, narrative, visit, traveler_reports, visual_recon, media, relations, freshness, qa.

No GPS, elevation, water, overnight, permits, prices or routes were invented. Missing fields remain null/unknown and are explicitly failed in qa.checks. Source registries are staged separately per country and must be deduplicated/remapped to the global source registry before live migration.

## Next migration work

1. Reconcile staged source refs with data/id-registry.json.
2. Assign/lock permanent IDs for PH/SG/TH/TL/VN objects.
3. Migrate and validate geo refs and coordinates.
4. Split infrastructure/lodging/routes/media into canonical entities where project data supports them.
5. Run build CDN, validate CDN and hierarchy validation on this branch only.
6. Do not promote latest/current or merge to main without explicit command.
