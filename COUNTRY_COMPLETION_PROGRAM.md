# Southeast Asia country completion program

## Goal

Bring all 11 Southeast Asian countries in the existing Expedition South East repository to one production standard.

Philippines (PH) is the reference country already accepted for this program. The remaining ten countries are completed strictly one by one. Existing research, objects, IDs, sources, geography and useful metadata must be preserved. A record may be deleted only when a duplicate or factual error is proven.

This program does not restart the project and does not replace the current CDN architecture.

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

Reference: PH — Philippines.

Do not skip ahead. Do not mark a country complete because it is merely present in a published reference release.

## Source-of-truth rule

Canonical layers:
- geo;
- countries / country source;
- objects;
- infrastructure;
- routes;
- media;
- sources;
- taxonomy.

Derived layers:
- search;
- views;
- object cards/read models;
- region/class/tag pages;
- aggregates.

A fact is stored in one canonical place. Derived files are rebuilt and never hand-edited.

## Country execution order

For each country:

1. Audit the current canonical source and generated CDN.
2. Preserve all existing valid entities, IDs, relationships and sources.
3. Resolve country profile and dynamic travel rules.
4. Resolve geography top-down:
   - country;
   - region/state/province/district;
   - island/archipelago/protected/geographic areas;
   - city/town/village/settlement;
   - WGS84 geometry and point semantics.
5. Work object classes one by one.
6. For every object:
   - normalize identity/class/tags;
   - verify geo links;
   - verify primary GPS point and coordinate_type;
   - verify elevation and provenance;
   - rebuild narrative in natural Russian;
   - verify independent-travel logistics;
   - verify water and supplies;
   - verify overnight/camping status;
   - link lodging/POI/routes instead of duplicating them;
   - add sourced traveler reports;
   - normalize visual reconnaissance;
   - verify media and sources;
   - run object QA.
7. Complete infrastructure:
   - lodging;
   - water;
   - shops/markets/food;
   - fuel;
   - parking;
   - ranger/visitor centers;
   - piers/stops/stations;
   - trailheads;
   - medical/ATM/repair/moped rental where relevant.
8. Complete standalone routes and waypoints where the source material supports them.
9. Complete source entities and fact-level refs.
10. Run class QA.
11. Run country QA.
12. Build and validate the CDN.
13. Only after the full gate is green may the country be marked complete and the queue advance.

## Country profile standard

Country data must cover, when supported:
- history;
- geography and relief;
- religions;
- languages;
- ethnography;
- economy;
- culture;
- cuisine and street food;
- climate by month/zone;
- natural hazards;
- dangerous animals;
- poisonous plants;
- visas and visa-run conditions;
- border crossings;
- transport rules;
- camping;
- drones;
- restrictions and permits.

Fast-changing fields require source refs and checked_at.

## Object standard

Each attraction has a stable ID and one primary class plus tags.

Required semantic blocks:
- names;
- summary.narrow;
- classification;
- geo;
- narrative.sections;
- visit;
- traveler_reports;
- visual_recon;
- media;
- relations;
- freshness;
- qa.

Narrative sections are added only when material exists:
- overview;
- history;
- culture;
- geography;
- geology;
- ethnography;
- myths_beliefs.

Distinguish documented history, local tradition, legend and modern tourist story.

## Geodata contract

WGS84 / EPSG:4326.

For each physical object use a meaningful operational point, not a convenient substitute:
- center;
- entrance;
- trailhead;
- summit;
- viewpoint;
- pier;
- parking;
- cave_entrance;
- waterfall_base;
- archaeological_core;
- temple_entrance.

Do not substitute town coordinates for an attraction. Do not use a park centroid as an entrance. Unknown is null/unknown; approximate coordinates must be explicitly marked approximate.

Each non-null elevation must describe the correct entity/point and have provenance.

## Logistics contract

Access is multimodal and structured.

Each access option records origin, modes and legs. A leg records, where supported:
- mode;
- distance_km;
- duration_min;
- road surface/condition/seasonality;
- walking distance;
- elevation gain/loss;
- trailhead GPS;
- trail condition/navigation;
- fords/crossings.

Public transport, taxi/ride-hailing, moped/motorcycle, boats and walking are evaluated separately.

Package tours are not the default. A guide/operator is recorded only when mandatory, permit-linked, access-enabling or objectively useful for difficult logistics.

Long approaches, stairs, multiday travel and lack of mass-tourism infrastructure are not negative criteria.

## Water, supplies and overnight

Water must identify:
- water at the object;
- last reliable water/shop point;
- distance;
- natural sources;
- quality: potable / filter_required / treatment_required / technical_only / unknown.

Overnight status must use:
- official;
- allowed;
- permission_required;
- tolerated_in_practice;
- prohibited;
- unclear.

Never assert legality without a source.

## Traveler reports

Traveler reports are evidence, not filler. Use them for road/trail condition, bad map data, closed gates, water, return transport, real prices, parking, insects/leeches, dogs, tides/currents, closures and lodging condition.

Every report needs provenance or must remain explicitly unverified; an empty source_refs array must not qualify as passed QA.

## Visual reconnaissance

This is location intelligence, not a photography tutorial.

Store:
- viewpoints;
- seasonal_visuals;
- video_activity;
- drone.

A useful viewpoint records, when supportable:
- GPS;
- access;
- what is visible;
- useful time/season;
- useful equipment category and why;
- source refs.

Allowed equipment categories:
ultra_wide, wide, standard, telephoto, long_telephoto, macro, action_camera, underwater_camera, drone, phone.

Do not write ISO, shutter speed, aperture, shot lists, camera moves, staging or scripts.

Drone is structured:
- legal_status;
- permit_required;
- restrictions;
- source_refs;
- checked_at.

## Editorial standard

User-facing prose is natural Russian. Avoid English-Russian hybrid prose except proper names, official terms and unavoidable local terminology.

Remove generic filler. Every sentence must add a fact, explain the place, constrain logistics or help field planning.

## Definition of Done — object

An object is complete only when QA truthfully covers:
- language;
- classification;
- geo;
- coordinates;
- elevation;
- narrative;
- sources;
- access;
- water;
- overnight;
- traveler_reports;
- visual_recon.

A legacy qa.status=passed does not count if the underlying fields fail the current contract.

## Definition of Done — country

A country is complete only when:
- country profile and dynamic rules meet the current contract;
- hierarchy/geo/localities are coherent;
- all retained object cards have been reviewed against the current object contract;
- infrastructure refs resolve;
- route/media/source refs resolve;
- no proven canonical duplicates remain;
- no valid unique object has been lost;
- Russian editorial QA passes;
- build normalized CDN passes;
- build canonical CDN passes;
- recursive hierarchy build passes;
- country/regional validation passes;
- source/generated CDN validation passes;
- canonical contract passes;
- recursive hierarchy validation passes;
- derived map validation passes;
- strict locality/geo validation passes;
- post-merge publication/read-model is verified.

## Mandatory validation gate

After each country-changing batch run the repository pipeline equivalent:

1. build normalized CDN;
2. build canonical CDN layer;
3. build recursive hierarchy;
4. validate country/regional layer;
5. validate source and generated CDN;
6. validate canonical contract;
7. validate recursive hierarchy;
8. build and validate derived maps;
9. validate strict locality/geo contract.

Do not advance the queue while the current country has unresolved structural failures.

## Current execution state

- PH — reference / accepted.
- BN — active country.
- KH — queued.
- LA — queued.
- ID — queued.
- MY — queued.
- MM — queued.
- SG — queued.
- TH — queued.
- TL — queued.
- VN — queued.

BN must be re-audited against this full contract even if older metadata says object cards or QA were previously complete.
