# Expedition South East CDN

Public, versioned CDN read model for the **Expedition South East** travel-research project.

## Current release

- Schema: `2.1.0`
- Release: `2026-09-28-r3`
- Publishable countries: Brunei, Cambodia, Laos, Indonesia, Malaysia
- Objects: 98
- Places/tags: 122
- Object types: 22

The editorial/research source model is intentionally separate. This repository contains the normalized read model used by the frontend/CDN.

## Endpoints after GitHub Pages deployment

- `/cdn/v2/latest.json`
- `/cdn/v2/2026-09-28-r3/manifest.json`
- `/cdn/v2/2026-09-28-r3/home.json`
- `/cdn/v2/2026-09-28-r3/countries.json`
- `/cdn/v2/2026-09-28-r3/object-types.json`
- `/cdn/v2/2026-09-28-r3/places.json`
- `/cdn/v2/2026-09-28-r3/taxonomy.json`
- `/cdn/v2/2026-09-28-r3/search/objects.json`
- `/cdn/v2/2026-09-28-r3/search/places.json`

## Workflow

Every push to `main` that touches the CDN, validator, or workflow:

1. parses every JSON file;
2. verifies release ID/schema consistency;
3. checks manifest byte sizes and SHA-256 hashes;
4. checks global country/object/place counts and duplicate object identifiers;
5. blocks deployment if `qa.json` contains failures;
6. publishes `public/` to GitHub Pages.

The dated release directory is immutable. Future country migrations should create a new release and advance `public/cdn/v2/latest.json`.
