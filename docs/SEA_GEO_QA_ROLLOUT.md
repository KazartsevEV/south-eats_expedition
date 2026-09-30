# SEA country geo-QA rollout

Updated: 2026-10-01

## Reference state

Philippines is the reference implementation for the pre-object phase.

Exit criteria before object-card work:
- canonical country layer remains valid;
- formal hierarchy is verified and uses stable IDs;
- every administrative/regional node required by the project has a sourced `regional_profile`;
- every included city/town/village settlement has a sourced `locality_profile` with a settlement coordinate that is not reused as an attraction coordinate;
- geometry is added for administrative/physical nodes only where a sourced or honestly approximate boundary can be defended;
- composite expedition areas never inherit a parent polygon merely to avoid a null;
- `source_refs`, `checked_at` and freshness are preserved;
- search/views/maps are generated from canonical data, never edited by hand;
- build CDN -> validate country/CDN -> validate canonical -> validate hierarchy -> validate derived maps must all pass;
- object cards remain frozen until all countries in this queue have passed the pre-object geo layer.

## Canonical role contract

### regional_profile
Required:
- description/narrow;
- geography;
- climate;
- transport;
- provenance.source_refs;
- provenance.research_source_refs;
- provenance.checked_at;
- freshness.checked_at.

Additional sections are added only when supported: history, culture, geology, hydrology, nature, ethnography, religion, architecture, myths_beliefs, marine.

### locality_profile
Required:
- description/narrow;
- primary_location or an explicit sourced reason why it is unavailable;
- geography;
- climate;
- transport;
- provenance.source_refs;
- provenance.research_source_refs;
- provenance.checked_at;
- freshness.checked_at.

Settlement coordinates are map/logistics anchors only. They must not substitute for attraction entrances, trailheads, piers, summits or other object coordinates.

### geometry
- WGS84 / EPSG:4326 for published geometry;
- administrative boundary: `simplified_sourced_boundary` when provenance is sufficient;
- expedition/physical composite: `approximate` unless an independent legal/physical boundary exists;
- no parent-boundary cloning for a composite node;
- no cadastral/survey precision claims for simplified navigation masks.

## Country order

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

PH — Philippines: reference geo layer complete before object cards.

## Per-country work order

For each country, without skipping levels:

1. Audit country source, hierarchy and generated QA.
2. Normalize/repair hierarchy and stable IDs; never delete existing nodes except a proven duplicate/error.
3. Fill top administrative/regional profiles.
4. Fill included child administrative or physical regional profiles.
5. Fill settlement/locality profiles and settlement GPS anchors.
6. Add sourced geometry and honest approximate expedition masks.
7. Verify current administrative changes separately from boundary-data vintage.
8. Build canonical CDN.
9. Validate country/source/CDN.
10. Validate canonical contract.
11. Validate recursive hierarchy.
12. Build and validate derived maps.
13. Merge only after green CI.
14. Run post-merge audit and publish.
15. Mark the country pre-object geo layer complete; move to the next country.

## Queue status

| # | Country | Status |
|---|---|---|
| 1 | BN Brunei | complete |
| 2 | KH Cambodia | complete |
| 3 | LA Laos | regional/locality content complete; geometry subchunk pending |
| 4 | ID Indonesia | active |
| 5 | MY Malaysia | queued |
| 6 | MM Myanmar | queued |
| 7 | SG Singapore | queued |
| 8 | TH Thailand | queued |
| 9 | TL Timor-Leste | queued |
| 10 | VN Vietnam | queued |
| — | PH Philippines | reference complete |


## Live execution notes — 2026-10-01

- BN and KH are already at the pre-object geo-complete marker and are verify-only.
- PH remains the reference implementation and is not part of the remaining queue.
- LA regional ownership and real locality profiles have passed full CI and are merged; sourced administrative/physical geometry remains the open Laos subchunk.
- ID regional ownership is the active country; legacy composite route hubs must remain for compatibility while real settlement nodes receive separate stable IDs.
- MY → MM → SG → TH → TL → VN follow strictly after ID, one country at a time.
- A country is not marked complete merely because regional prose exists. It must pass role QA, geometry QA, canonical build, recursive hierarchy validation and derived-map validation.
- Object-card migration/rewrite stays frozen globally until all ten countries are complete or explicitly marked verify-only.
