# Expedition South East CDN

Public, versioned CDN read model for the **Expedition South East** expedition knowledge base.

## Current architecture

The current schema version is declared by each release in `schema/schema-version.json` and is built top-down:

`project → Southeast Asia → country → geography / class family → primary class → object`

The editorial/research source model remains separate. The CDN is the normalized read model used by the frontend and by search/filter clients.

### Canonical upper-level endpoints

- `/cdn/v2/latest.json`
- `/cdn/v2/<release>/project.json`
- `/cdn/v2/<release>/region/southeast-asia.json`
- `/cdn/v2/<release>/navigation/tree.json`
- `/cdn/v2/<release>/geography/tree.json`
- `/cdn/v2/<release>/taxonomy/tree.json`
- `/cdn/v2/<release>/page-layouts.json`
- `/cdn/v2/<release>/hierarchy-status.json`

Country, geography, class and object pages are generated below those roots. All 11 Southeast Asian countries exist in the country catalog; countries not yet migrated from the research source remain explicit placeholders rather than invented content.

## Taxonomy rule

Every object has exactly one primary class. Higher-level families are navigation only. Broad legacy classes such as `natural_landscape`, `river_or_wetland`, `island_or_coast` and `living_settlement` are marked transitional and are split only after object-level evidence supports a more precise class.

## Recursive workflow

Work proceeds in this order:

1. project shell and page layout;
2. Southeast Asia regional layer;
3. country catalog;
4. geography contract and class families;
5. country page;
6. geographic branch / primary-class branch;
7. object cards;
8. QA at each parent before descending to its children.

Sparse objects are retained. Missing lower-level data is recorded as a gap, not filled by guesswork.

## CI workflow

Every relevant push to `main`:

1. rebuilds the normalized CDN;
2. augments it with the recursive hierarchy and page models;
3. validates JSON, release integrity and manifest hashes;
4. validates the project → region → country → geography/class → object graph;
5. commits generated CDN files back to `main` only when validation passes.


## Geodata contract

Object geodata uses WGS84 / EPSG:4326. A physical object may expose a primary operational point and additional points such as entrance, trailhead, summit, viewpoint, pier, parking, cave entrance or waterfall base.

- latitude/longitude are decimal degrees;
- elevation is metres above mean sea level and remains `null` when not verified;
- `accuracy` records whether a point is high-confidence, medium, approximate or unknown;
- large parks and route-like places should use a meaningful access point instead of an unexplained geometric centre;
- human-readable decimal and DMS strings are generated from canonical numeric coordinates;
- search indexes carry the same primary coordinates as object detail pages;
- missing geodata is exposed in QA gaps and is never replaced by invented zero values.

The generated contract is published at `/cdn/v2/<release>/schema/geodata-contract.json`.

## Canonical migration and derived layers

The release keeps the researched source records and their stable registry IDs. Canonical roots are `geo`,
`countries`, `objects`, `infrastructure`, `routes`, `media`, `sources`, and `taxonomy`. Search, views, maps,
site HTML, and QA are deterministic read models rebuilt by the scripts; they must not be edited directly.

`manifest.json` is the release entry point. It links the global search and home view, the SEA/country/region
map manifests, and static site entry points. Map coordinates are projected from canonical entities rather
than maintained in a parallel map dataset.

### Migration audit / remaining gaps

- Six researched countries are published; the eleven-country catalog retains explicit placeholders.
- Existing stable object, geography, source, lodging, route, and media IDs are preserved.
- Media metadata is canonical, but most published objects do not yet meet the five-image gallery rule.
- Local 960×640 WebP previews are not fabricated. Missing binaries remain a QA gap until a suitable,
  rights-compatible representative image has been selected and encoded.
- GeoJSON boundary/linear geometries, infrastructure coverage, and route coverage remain incremental.

## Visual reconnaissance

The visual block is location intelligence, not a photography tutorial: where a useful view is obtained, when the light/season makes it work, what is visible there and which equipment category is useful because of the geometry or distance. Camera settings, shot lists, composition lessons and video scripts are outside the data model.
