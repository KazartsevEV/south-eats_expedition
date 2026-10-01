# Google Drive → canonical reconciliation — 2026-10-02

## Verdict

- All **11 country monoliths** are represented in the current dataset.
- Donor object count: **211**. Canonical object count: **211**.
- Identity coverage: **211/211**. There are no missing attraction records.
- The only name-level mismatch is an intentional editorial rename in Brunei: `Tutong and Tamu markets` → `Pasarneka Tutong / Tamu Tutong`.
- Current QA: **38 complete / 173 incomplete**. Most remaining gaps are research gaps, not migration loss.

## What survived migration

The five rich donor monoliths — BN, KH, ID, LA and MY — contain water, overnight/camping, accommodation and traveler reports for all **98 objects**. Current canonical QA confirms these dimensions survived: those five countries no longer show water/overnight/traveler-report gaps.

The thinner MM, PH, SG, TH, TL and VN monoliths did not contain the missing canonical GPS/elevation/water/overnight/traveler-report/visual-recon facts. Those fields therefore cannot be “restored” from the old country JSON and must be researched.

No numeric latitude/longitude pairs were found in the 11 donor monolith object records. The 38 physically available r1 standalone BN/KH/LA detail files also do not reveal a hidden GPS/elevation layer.

## Historical derived layers

### CDN r1

The r1 manifest contains 73 entries. **55 files are present exactly; 18 Laos standalone object-detail files are physically absent from Drive.** This remains a declared provenance gap. Their original hashes must not be attached to reconstructed/newer content.

### CDN_v2 r3

The surviving r3 manifest describes **153 files / 98 objects** for BN, KH, LA, ID and MY, and QA records **188 image references**. However, its `countries/` directory is empty in the Drive tree. Only metadata files survive there.

Therefore the manifest proves a richer derived read-model existed, but exact r3-only detail payloads — especially any ID/MY helper-gallery URLs — are no longer recoverable from the Drive tree.

### Reference ZIP

`expedition_cdn_v2_reference.zip` is a separate earlier derivative snapshot, not an exact reconstruction of r1 or r3. It preserves usable helper-gallery media for BN/KH/LA and can be used as an explicitly separate donor source.

After deduplicating Wikimedia aliases and obvious resized-image variants, the archive contains **104 underlying media assets that are not present in the current canonical gallery sets**:

| Country | Old-only distinct assets | Current relevance |
| --- | ---: | --- |
| BN | 37 | 4 current gallery QA blockers can be closed |
| KH | 40 | historical alternatives only; KH already passes |
| LA | 27 | 1 current gallery QA blocker can be closed; Tham Piu gains 1 image but remains incomplete |

The five directly recoverable gallery closures are:

1. BN — Pasarneka Tutong / Tamu Tutong
2. BN — Billionth Barrel Monument
3. BN — Malay Technology Museum
4. BN — Tamu Kianggeh
5. LA — Vientiane sacred architecture

If every listed legacy asset still passes URL, license and mirror validation, this recovery would move QA from **38 → 43 passed objects** and `gallery_min_5` missing from **173 → 168**.

## Content unique to surviving standalone detail files

Beyond the country monoliths and reference-media layer, the surviving standalone r1 details add only two meaningful categories:

- **67 gallery-description values** — potentially useful as media metadata when they still refer to the same verified asset.
- **61 media score values** — editorial ranking, not a canonical fact; do not migrate.

Other differences are read-model mechanics: schema/release metadata, generated timestamps, derived IDs and provenance paths.

## Intentionally not migrated

Do not restore legacy `field_planning`, `capture_sequence`, shot lists or similar instructions. The current project contract explicitly forbids photographer-direction content and retains only viewpoint/access/what-is-visible/best-time/useful-equipment information.

Do not copy old search/views/collections/card payloads back into canonical data. They are derived models and must be regenerated.

## Recovery queue before object-by-object QA

1. Recover and validate the five gallery-closing media sets with explicit provenance.
2. Optionally preserve matching historical gallery descriptions in media entities.
3. Keep the 18 r1 Laos files and the missing r3 detail tree recorded as historical provenance gaps; never fake exact reconstruction.
4. Then resume country → class → object QA against the actual current gaps.
