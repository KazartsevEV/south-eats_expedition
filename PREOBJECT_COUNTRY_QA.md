# Pre-object country QA program

## Scope

Bring every Southeast Asia country in the canonical dataset to the same pre-object baseline proven on the Philippines before object-card migration resumes.

Object cards remain frozen throughout this program. Do not create, rewrite, delete, reclassify or migrate attraction/object payloads except to fix a proven reference-integrity defect that blocks structural validation.

## Fixed queue

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

PH — Philippines is the reference country and is already complete for this phase.

Do not start the next country until the current country passes the full build/validation pipeline and is merged to main.

## Country procedure

For each country, work top-down:

1. Audit current canonical country, hierarchy, source and generated CDN layers.
2. Preserve every existing valid node, profile, source and relationship.
3. Resolve administrative hierarchy first:
   - current official parentage;
   - stable canonical IDs;
   - correct geo kind;
   - no attraction/place semantic leakage into geography.
4. Complete the regional/provincial profile layer.
5. Complete locality ownership:
   - city/town/village/settlement data live in the canonical locality source layer when the builder already owns those facts there;
   - do not duplicate the same narrative in hierarchy metadata.
6. Add geometry only when defensible:
   - official administrative boundary where applicable;
   - sourced physical/protected-area boundary where appropriate;
   - composite expedition masks only as accuracy=approximate with an explicit coverage_basis;
   - never copy a parent polygon merely to remove a QA gap.
7. QA source references and freshness.
8. Build canonical CDN.
9. Validate country/regional layer.
10. Validate generated CDN.
11. Validate canonical contract.
12. Validate recursive hierarchy.
13. Build and validate derived maps.
14. Merge only after the complete workflow is green.
15. Verify post-merge publish/read-model.
16. Mark the country pre-object layer complete and move to the next country.

## Required regional-profile contract

A canonical regional/provincial profile must provide, directly or through the canonical builder ownership model:

- description.narrow / profile.narrow;
- geography;
- climate;
- transport;
- provenance.source_refs;
- provenance.research_source_refs where the role requires them;
- provenance.checked_at;
- freshness.checked_at.

Add history, culture, geology, nature, ethnography, religion, architecture, hydrology or marine context only where supported by the source material. Do not pad profiles with generic country-level prose.

## Locality contract

For city/town/village/settlement nodes used as geographic or logistics anchors:

- narrow/summary;
- primary_location or explicit documented no-coordinate status;
- geography;
- climate;
- transport;
- source_refs;
- checked_at/freshness.

Settlement coordinates are settlement centers only. They must never stand in for an attraction, cave entrance, trailhead, pier, summit or park entrance.

## Geometry contract

All coordinate geometry uses WGS84 / EPSG:4326 in generated canonical output.

Administrative geometry must retain:
- boundary level;
- source vintage;
- current administrative identity separately from legacy source codes when necessary;
- source_refs;
- checked_at;
- simplified/navigation-only status where applicable.

Approximate composite masks must retain:
- accuracy=approximate;
- geometry_type;
- coverage_basis;
- source_refs;
- checked_at;
- explanatory note.

A missing polygon is preferable to a false polygon.

## Definition of Done per country

A country is complete for this phase only when:

- hierarchy has no unresolved administrative-parentage defects;
- regional/province profiles satisfy the required contract;
- locality profiles satisfy the locality contract;
- geometry gaps are either resolved or explicitly intentional;
- no canonical narrative fact has been duplicated merely for presentation;
- sources and refs resolve;
- build normalized CDN passes;
- build canonical CDN passes;
- recursive hierarchy build passes;
- country/regional validation passes;
- source/generated CDN validation passes;
- canonical contract passes;
- recursive hierarchy validation passes;
- derived-map validation passes;
- post-merge CDN publish is verified;
- country metadata records pre-object completion;
- object cards remain frozen.

## Reference implementation

Philippines (PH), completed 2026-09-30, is the behavioral reference for this program. Reuse its ownership and QA principles, not its country-specific hierarchy or geometry.
