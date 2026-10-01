# Drive raw → canonical 211 reconciliation — 2026-10-02

## Baseline

- Raw Drive snapshot: **211 objects / 11 countries**.
- Strict canonical release: **211 objects**, schema **2.10.10**, release **2026-09-30-r42**.
- Object identity reconciliation: **211/211** — 210 exact country+name matches + 1 proven rename (`Tutong and Tamu markets` → `Pasarneka Tutong / Tamu Tutong`, legacy ID `bn:tutong-and-tamu-markets`).
- Raw leaf-key inventory: **137 distinct paths**.
- Canonical source registry: **1169 entities**.
- Raw source URL rows checked: **944**; present in canonical: **935**; missing: **9**.

## What is actually missing from strict canonical

The object count is not the problem. The builder has field-level blind spots.

1. **Object-level safety:** 211/211 raw objects have a safety block; strict canonical objects do not emit it.
2. **Typical visit duration:** 211/211 objects have `typical_visit_hours`; strict canonical has no equivalent field.
3. **Last mile:** 185 objects have raw last-mile notes; 126 are not exact duplicates of `access` or `modes`.
4. **Public transport detail:** 163 objects have a dedicated raw note; 123 are not exact duplicates of `access` or `modes`.
5. **Mobility / terrain:** 129 mobility notes and 19 terrain/movement notes are not emitted by strict canonical.
6. **Dynamic object status/security:** 45 objects carry old operational/security snapshot fields that are not emitted. These must be **reverified**, not blindly copied.
7. **Visual recon:** canonical QA has **135** visual-recon gaps; raw has a `best_light` seed for **135/135** of them. 22 of those gaps also have old `shooting_recommendation` data and 135 have `field_planning` data that can only be mined for compliant factual scouting context.
8. **Sources:** only **9** of 944 raw source URL rows are absent from the canonical source registry. They are listed verbatim in the JSON audit and require URL/content review before re-adding.

## What is *not* a loss

- `illustration.*` → canonical `media`.
- `sources[]` → canonical `sources` + refs.
- `accommodation[]` → `infrastructure/lodging`.
- annotation/history/culture/geography/myths → `narrative.sections`.
- climate → `visit.seasonality`.
- region / nearest hub → canonical `geo`.
- `route_meta` is mostly a duplicate compatibility layer. It must not be turned into fake route entities; route entities still require route-level distance, waypoints and sources.

## Deliberately deprecated — do not restore verbatim

The old production-oriented fields are not canonical content: `capture_sequence`, `blog_angle`, `best_formats`, production-complexity/phone-only/audio scores, and project-policy boilerplate. Old `shooting_recommendation` and `field_planning` are **review inputs only**: salvage factual **where / when / weather / access / useful equipment context**, but do not restore shot lists, camera moves or photographer instructions.

## Files

The companion JSON audit contains:
- all 137 non-empty raw leaf paths with classification and counts;
- all 211 raw objects with migration-gap payloads;
- the exact 9 raw source URLs missing from canonical;
- per-object visual-recon seed flags;
- current canonical QA coverage/gap counts.

No canonical data was changed by this audit.
