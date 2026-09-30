# Regional and geo reference contract

Status: project contract derived from the normalized regional/locality layers of BN, KH, LA, ID, MY and MM.

## 1. Purpose

Regional geography is a canonical knowledge layer between country-wide facts and attraction cards. It describes provinces, regions, cities, towns, islands and expedition geographic areas only at the spatial level to which a fact actually belongs.

A hierarchy node is not required to contain narrative merely because it exists. Administrative structure and researched reference coverage are separate concerns.

## 2. Coverage roles

Every non-country canonical geo entity uses one of three roles.

### structural

Use when the entity is required for identity, hierarchy, parentage or navigation but no independently sourced local reference has been normalized yet.

Required:
- stable canonical geo ID;
- kind;
- names and slug;
- parent_id and geo_path;
- structural provenance with source_refs and checked_at.

Do not fill descriptive sections from a parent, sibling, attraction card or country profile merely to avoid an empty page.

### regional_profile

Use for a researched province, region, island group or expedition geographic area.

Required research core:
- description.narrow;
- geography;
- climate;
- transport;
- safety when a territorial risk statement can be sourced;
- provenance.research_source_refs;
- provenance.source_refs;
- provenance.checked_at;
- freshness.checked_at.

Add only when territorially relevant and supported:
- relief;
- geology;
- hydrology;
- coast;
- marine;
- nature;
- health;
- history;
- ethnography;
- culture;
- myths_beliefs;
- architecture;
- languages.

Regional facts must not be copied into every locality below the region.

### locality_profile

Use for a researched city, town, village, settlement or practical gateway.

Required research core:
- description.narrow;
- locality-specific geography;
- locality-specific transport;
- primary_location in WGS84 when a reliable locality point exists, otherwise primary_location_status with status=unresolved or not_applicable and a concrete reason;
- provenance.research_source_refs;
- provenance.source_refs;
- provenance.checked_at;
- freshness.checked_at.

Add history, culture, architecture, climate, nature, safety, ethnography and other sections only when they are supported specifically for that locality.

## 3. Coordinates and map binding

All coordinates use WGS84 / EPSG:4326.

For a city/town/village:
- coordinate_type=center;
- coordinate represents the locality, not an attraction;
- accuracy reflects the source;
- source_refs and checked_at are mandatory.

For a composite regional or expedition node:
- primary_location may be a documented reference anchor used for map framing;
- the note must state what the point represents;
- a gateway city, volcano, reef or heritage core must never be presented as the geometric centroid unless it actually is one;
- the anchor is not an attraction entrance, trailhead or access coordinate.

Object coordinates remain in the object layer. A geo anchor must not replace an object GPS point.

## 4. Hierarchy and deduplication

Administrative nodes and expedition geographic_area nodes may coexist when they model different concepts.

Do not duplicate the same researched narrative into both an administrative parent and a composite expedition node. Keep the full reference at the most appropriate spatial entity and use explicit hierarchy/relations for navigation.

Do not invent administrative status for composite route regions. If the researched unit is not an official province/state/district, keep it as geographic_area.

Persistent IDs must not change when names or slugs change.

## 5. Source ownership

Research facts are linked through canonical source_refs.

Dynamic or operational statements require checked_at.

Do not infer local climate, crime, dangerous fauna, disease incidence, access restrictions or cultural practice from a country-wide statement.

A source used only to verify a coordinate does not by itself justify narrative claims.

## 6. User-facing language

Reference text is natural Russian. English/local names are retained only where useful as names or official terminology.

Do not expose implementation language such as canonical, geo node, migration status, source normalization or hierarchy mechanics in the user-facing copy.

## 7. Country pass

A country regional/geo pass proceeds in this order:

1. inspect the formal hierarchy and existing researched regions/localities;
2. preserve all existing IDs and researched facts;
3. map researched profiles to the correct hierarchy nodes;
4. add missing locality profiles where those localities are part of the expedition hierarchy;
5. add reliable locality coordinates and regional reference anchors;
6. keep unresolved coordinates null with an explicit status rather than substituting a parent/object point;
7. build CDN;
8. build canonical layer;
9. build recursive hierarchy;
10. validate country layer;
11. validate CDN;
12. validate canonical contract;
13. validate hierarchy;
14. validate locality ownership and geo coverage in strict mode;
15. build/validate derived map layers;
16. merge only after QA passes;
17. deploy to live and stop for visual/user confirmation before the next country.

## 8. Current rollout order

Reference countries: BN, KH, LA, ID, MY, MM.

Remaining countries are processed one at a time:
PH -> SG -> TH -> TL -> VN.

Do not begin the next country until the current country has passed QA, been merged/deployed to live, and the user has confirmed continuation.
