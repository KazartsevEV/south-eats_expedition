# SEA upper-level country QA rollout

Updated: 2026-10-01

## Reference

PH — Philippines is the only accepted reference implementation for the current pre-object phase.

Object-card work is frozen globally until the ten remaining countries pass upper-level QA.

## Fixed queue

| # | Country | Status |
|---:|---|---|
| — | PH — Philippines | reference / accepted |
| 1 | BN — Brunei | complete |
| 2 | KH — Cambodia | active |
| 3 | LA — Laos | queued |
| 4 | ID — Indonesia | queued |
| 5 | MY — Malaysia | queued |
| 6 | MM — Myanmar | queued |
| 7 | SG — Singapore | queued |
| 8 | TH — Thailand | queued |
| 9 | TL — Timor-Leste | queued |
| 10 | VN — Vietnam | queued |

Previous geo/profile PRs for BN/KH/LA/ID/MY and other countries are retained as prior work, not discarded. Their old `complete` markers do **not** waive the new upper-level acceptance pass.

## Acceptance execution

- BN passed the upper-level acceptance gate and post-merge publish.
- KH is the active acceptance pass.
- PR #189 carries only upper-level QA docs and Brunei country-level source changes; object payloads are frozen.

## Scope

Per country, complete and verify only:

1. country profile;
2. climate;
3. current travel rules;
4. formal geo hierarchy;
5. regional/provincial profiles;
6. locality profiles;
7. locality GPS anchors;
8. administrative/physical geometry;
9. provenance, source refs and freshness;
10. generated upper-level views/search/maps;
11. full structural validation and post-merge publish verification.

## Frozen scope

Do not create, rewrite, delete, reclassify or enrich attraction/object payloads.

Do not work on:
- object narratives;
- object access/logistics;
- water/overnight;
- traveler reports;
- object visual reconnaissance;
- object media;
- routes tied to object completion;
- lodging/POI migration for object cards.

Exception: minimal reference-integrity repair only when a broken object ref blocks the upper-level validation pipeline.

## Exit gate

A country advances to `complete` only after:

- country profile QA passes;
- climate QA passes;
- current travel-rule QA passes;
- hierarchy QA passes;
- regional-profile QA passes;
- locality-profile QA passes;
- geometry QA passes;
- source/freshness QA passes;
- normalized CDN build passes;
- canonical CDN build passes;
- recursive hierarchy build passes;
- country/CDN/canonical/hierarchy validators pass;
- derived maps pass;
- strict locality/geo validation passes;
- merge succeeds;
- published read-model is checked.

Then and only then move to the next country.
