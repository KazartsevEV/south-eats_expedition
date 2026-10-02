# Laos structural split — r46 candidate

Date: 2026-10-02

## Purpose

Resolve the five `composite_needs_split` identities found by the r45 identity audit.

The old persistent IDs are retired from the active Laos inventory and are **not reassigned**. Their migration mapping is stored in `travel.object_migrations`.

## Retired composite IDs → replacements

- `obj_la_0010` Nong Khiaw and Muang Ngoi
  - `obj_la_0142` Nong Khiaw
  - `obj_la_0143` Muang Ngoi
- `obj_la_0014` Vientiane sacred architecture
  - `obj_la_0144` Pha That Luang
  - `obj_la_0145` Wat Sisaket
  - `obj_la_0146` Ho Phra Keo
  - `obj_la_0147` Wat Si Muang
- `obj_la_0016` Phongsaly old town and ancient tea highlands
  - `obj_la_0148` Phongsaly Old Town
  - `obj_la_0149` Ban Komaen Ancient Tea Plantation
- `obj_la_0017` Muang Sing market and Tai Lue cultural landscape
  - `obj_la_0150` Muang Sing Morning Market
  - `obj_la_0151` Muang Sing Tai Lue Cultural Landscape
- `obj_la_0031` Nong Fa / Dong Ampham landscape
  - `obj_la_0152` Nong Fa Lake
  - `obj_la_0153` Dong Ampham National Protected Area

## Inventory arithmetic

Before split: 141 active cards.

Retire 5 composite cards and add 12 child identities:

`141 - 5 + 12 = 148` active cards.

Identity statuses after split:

- distinct: 139
- alias_merged: 5
- same_visitable_complex: 4
- composite_needs_split: 0
- duplicate_of: 0
- unresolved: 0

## Data migration policy

Only facts that can be attributed to a specific child are copied into that child.

Examples:
- Nong Khiaw keeps its road access, Pha Daeng and Nong Khiaw pier points.
- Muang Ngoi receives its own settlement center, pier/Phanoi points and the Nong Khiaw→Muang Ngoi boat/overland legs.
- Pha That Luang keeps the old composite coordinate because that coordinate was actually tied to That Luang.
- Wat Sisaket, Ho Phra Keo and Wat Si Muang receive **null coordinates** rather than inheriting That Luang's coordinate.
- Phongsaly Old Town keeps the town coordinate; Ban Komaen remains null until its own GPS is verified.
- Muang Sing Morning Market remains null rather than inheriting the town-center coordinate.
- Nong Fa keeps the lake coordinate/elevation; Dong Ampham NPA remains null rather than inheriting the lake center.

This is intentional: structural correctness takes precedence over filling child cards with guessed or inherited precision.

## Validation gate

r46 is a candidate. The canonical validator now fails Laos when any active card remains:
- `duplicate_of`
- `unresolved`
- `composite_needs_split`

Promotion to `latest` is allowed only after build CDN, canonical validation and hierarchy validation are green.
