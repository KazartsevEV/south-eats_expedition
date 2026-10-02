# Laos structural split — r46 candidate

Date: 2026-10-02

## Purpose

Resolve the five `composite_needs_split` identities found by r45 before further object-by-object enrichment.

Rule: a retired composite ID is never reused for one child. The old identity remains reserved in `data/id-registry.json -> retired_objects` and maps one-to-many through `data/migrations/laos-r46-composite-splits.json`.

## Inventory result

- r45 active Laos objects: 141
- proven composites retired: 5
- replacement children created: 12
- r46 active Laos objects: **148**
- active normalized title duplicates: 0
- active `composite_needs_split`: 0
- active `duplicate_of`: 0
- active `unresolved`: 0
- identity distribution: **139 distinct + 5 alias_merged + 4 same_visitable_complex**
- explicit parent-child links: **32**

## One-to-many migrations

| Retired ID | Retired composite | Replacement IDs |
|---|---|---|
| obj_la_0010 | Nong Khiaw and Muang Ngoi | obj_la_0142 Nong Khiaw; obj_la_0143 Muang Ngoi |
| obj_la_0014 | Vientiane sacred architecture | obj_la_0144 Pha That Luang; obj_la_0145 Wat Sisaket; obj_la_0146 Hor Phra Keo Museum; obj_la_0147 Wat Si Muang |
| obj_la_0016 | Phongsaly old town and ancient tea highlands | obj_la_0148 Phongsaly Old Town; obj_la_0149 Ban Komaen 400-Year-Old Tea Plantation |
| obj_la_0017 | Muang Sing market and Tai Lue cultural landscape | obj_la_0150 Muang Sing Morning Market; obj_la_0151 Muang Sing Tai Lue Cultural Landscape |
| obj_la_0031 | Nong Fa / Dong Ampham landscape | obj_la_0152 Nong Fa Lake; obj_la_0153 Dong Ampham National Protected Area |

## No-false-precision decisions

- Pha That Luang retains the old card's sourced monument coordinate, but its type is normalized to `center`; the old unsupported `temple_entrance` precision is not carried forward.
- Wat Sisaket, Hor Phra Keo Museum and Wat Si Muang receive `null` primary coordinates until each has a separately verified object GPS.
- Muang Sing Morning Market does **not** inherit the Muang Sing town-center coordinate.
- Muang Sing Tai Lue Cultural Landscape does **not** use the town coordinate as the center of the extended landscape.
- Ban Komaen does **not** inherit Phongsaly Town coordinates.
- Nong Fa Lake retains its lake coordinate/elevation.
- Dong Ampham NPA receives `null` primary GPS/elevation; the Nong Fa lake coordinate is not reused as a park center or entrance.

## Parent-child corrections

- obj_la_0150 Muang Sing Morning Market → obj_la_0151 Muang Sing Tai Lue Cultural Landscape.
- obj_la_0152 Nong Fa Lake → obj_la_0153 Dong Ampham National Protected Area.
- Phongsaly Ethnic Museum is retargeted from retired obj_la_0016 → obj_la_0148 Phongsaly Old Town.
- Poum Pouk Stupa is retargeted from retired obj_la_0017 → obj_la_0151.
- Phou Fa Mountain and Stupa loses the invalid parent link to retired obj_la_0016; it remains a separate nearby object.

## Provenance

Each replacement child carries:

- `qa.identity_review.split_from_object_ids`
- canonical `relations.split_from_ids`
- an immutable retired-ID reservation in the registry
- one-to-many mapping in `data/migrations/laos-r46-composite-splits.json`

The canonical validator checks all four layers for r46.

## Release policy

r46 is a candidate. `latest` remains r44 until build CDN, canonical validation, derived-map validation and hierarchy validation are all green.
