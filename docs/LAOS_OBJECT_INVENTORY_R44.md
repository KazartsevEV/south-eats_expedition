# Laos object inventory — r44

Date: 2026-10-02

## Scope

Inventory-first expansion before object-by-object QA.

- Baseline Laos objects: 70
- Added preliminary objects: 71
- New total: 141
- Existing objects removed: 0
- Canonical object IDs added: obj_la_0071 … obj_la_0141
- Formal geo nodes: 57
- New formal geo node: geo_la_0080 / Sainyabuli Province
- Release candidate: 2026-10-02-r44
- Promoted latest remains: 2026-10-02-r43

## Dedupe policy

Do not delete an existing object without a proven duplicate or error. Keep a broad landscape/city/park card and a distinct physical component when both are useful expedition entities. Collapse aliases and two names for one visitable complex into one card.

Suppressed overlaps in this pass:

- Tad Hua Khon Waterfall: already covered by `la:tad-se-noi-tad-hua-khon-waterfall`.
- Muang Sing Morning Market: already covered by `la:muang-sing-market-and-tai-lue-cultural-landscape`.
- Ban Komaen ancient tea plantation: already covered by the broad Phongsaly old town and ancient tea highlands card.
- Blue Lagoon 1: kept together with Tham Pou Kham Cave as one visitable complex.

## Coverage added

The expansion adds missing protected areas plus province-level archaeology, caves, waterfalls, museums, religious sites, living craft/ethnographic settlements, islands and wildlife sites. All new cards are deliberately preliminary: unresolved GPS, elevation, access, water, overnight, prices, hours, drone rules and traveler reports remain null/unknown until object QA.

## Structural invariants checked before PR

- 141 unique Laos source-object slugs.
- 141 unique formal-hierarchy object references.
- No source object missing from the Laos formal hierarchy.
- No hierarchy object reference missing from source.
- Every Laos object has a persistent registry ID.
- No duplicate canonical object ID.
- Every object name has a `TYPE_BY_NAME` primary-class mapping.
- Formal geo canonical IDs are unique.
- r44 is not promoted through `latest.json`; r43 remains latest until validation passes.

## Next phase

After r44 passes repository CI, run QA one object at a time using the project order:

object → research → normalization → GPS/elevation → sources → access → water/overnight → traveler reports → visual recon → QA.

Prioritize the 71 new preliminary cards first, then revisit broad/composite legacy cards where decomposition created new component entities.
