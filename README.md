# Expedition South East CDN

Public, versioned CDN read model for the **Expedition South East** expedition knowledge base.

## Current architecture

Schema `2.3.0` is built top-down and traversed recursively:

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
