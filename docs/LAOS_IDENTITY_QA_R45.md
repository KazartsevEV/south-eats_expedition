# Laos identity QA — r45 candidate

Date: 2026-10-02

## Scope

Identity review now covers **all 141 Laos object cards**, not only the 129 incomplete cards.

This pass answers a narrower question than content QA: whether two cards represent the same physical/canonical identity, a parent/child relationship, a deliberately merged alias/complex, or an invalid composite that must be split.

No attraction is deleted merely because it overlaps geographically with a park, city, cultural landscape or archipelago.

## Result

All 141 cards carry `qa.identity_review`.

Identity status counts:

- `distinct`: 127
- `alias_merged`: 5
- `same_visitable_complex`: 4
- `composite_needs_split`: 5
- `duplicate_of`: 0
- `unresolved`: 0
- explicit parent-child links: 31

For the **129 incomplete cards** that triggered this audit:

- `distinct`: 117
- `alias_merged`: 4
- `same_visitable_complex`: 4
- `composite_needs_split`: 4
- `duplicate_of`: 0
- `unresolved`: 0
- parent-child links represented among them: 30

Important: `distinct` for preliminary cards means **a separate inventory identity supported by a separate official/project listing and no collision found in the current Laos inventory**. It does not mean full visit QA is complete. Most preliminary cards still lack GPS/access/water/overnight evidence and therefore retain medium identity confidence until field-level QA.

## Proven composites that must be split

1. `obj_la_0010` — **Nong Khiaw and Muang Ngoi**
   - planned children: Nong Khiaw; Muang Ngoi
   - reason: two separate settlements with different access; the official Luang Prabang tourism itinerary treats them as separate stops linked by the Nam Ou corridor.
   - evidence: https://tourismluangprabang.org/recommended-trips/day-trips/misty-mountains-nong-khiaw-to-muang-ngoi/

2. `obj_la_0014` — **Vientiane sacred architecture**
   - planned children: Pha That Luang; Wat Sisaket; Ho Phra Keo; Wat Si Muang
   - reason: state media lists them as independent Vientiane attractions.
   - evidence: https://kpl.gov.la/EN/Detail.aspx?id=106044

3. `obj_la_0016` — **Phongsaly old town and ancient tea highlands**
   - planned children: Phongsaly Old Town; Ban Komaen 400-Year-Old Tea Plantation
   - reason: Ban Komaen is a separate village/tea site roughly 18 km from Phongsaly Town.
   - evidence: https://www.tourismlaos.org/northern-provinces/phongsali-province/
   - evidence: https://kpl.gov.la/en/detail.aspx?id=77262

4. `obj_la_0017` — **Muang Sing market and Tai Lue cultural landscape**
   - planned children: Muang Sing Morning Market; Muang Sing Tai Lue Cultural Landscape
   - reason: Tourism Laos publishes Muang Sing Morning Market as its own tourist destination inside the broader district/cultural landscape.
   - evidence: https://www.tourismlaos.org/northern-provinces/luang-namtha-province/

5. `obj_la_0031` — **Nong Fa / Dong Ampham landscape**
   - planned children: Nong Fa Lake; Dong Ampham National Protected Area
   - reason: a specific crater lake was conflated with the separately registered 200,000 ha Dong Ampham protected area.
   - evidence: https://laoparks.la/parks/

The existing IDs and prose are preserved until a separate structural split creates child IDs and migrates the useful material. These five are therefore not accepted as final one-object/one-card identities.

## Deliberately merged aliases

These are one entity under multiple names and must **not** be split back into duplicate cards:

- `obj_la_0005` — Si Phan Don / 4000 Islands
- `obj_la_0069` — Buddha Park / Xieng Khuan
- `obj_la_0026` — Li Phi / Somphamit Falls
- `obj_la_0127` — Nam Tok Katamtok / Xekatam Waterfall
- `obj_la_0059` — Tad Se Noi / Tad Hua Khon Waterfall

## Same visitable complex, retained as one card

- `obj_la_0115` — Tham Pou Kham Cave / Blue Lagoon 1
- `obj_la_0098` — The Rock Viewpoint / Phou Pha Marn tourism node
- `obj_la_0109` — Phou Fa Mountain and summit stupa
- `obj_la_0122` — Kaysone Phomvihane House and Museum

These have more than one physical/theme component but function as one visitable site. They are not cross-card duplicates.

## Parent-child relationships are not duplicates

Examples now encoded explicitly:

- Luang Prabang → Wat Xieng Thong, Mount Phousi, Royal Palace National Museum, Wat Visounnarath, Wat Manolom.
- Vang Vieng karst → Tham Chang, Kaeng Nyui, Tham Pou Kham / Blue Lagoon 1.
- Bolaven Plateau → Dong Houa Sao, Tad Fane, Tad Yuang, Tad Pha Suam, Tad Champi.
- Dong Houa Sao → Tad Fane, Tad Yuang.
- Phou Khao Khouay → Tad Xai, Tad Leuk.
- Hin Nam No → Xe Bang Fai Cave.
- Phou Hin Poun → Kong Lor Cave, Nam Non Cave, Khoun Kong Leng Lake, The Rock / Phou Pha Marn.
- Xe Pian → Tad Saepha, Tad Samongphak, Tad Saeponglaican.
- Si Phan Don → Khone Phapheng Falls, Li Phi / Somphamit Falls.
- Nam Ha → Pha Yueang Waterfall.

Official Lao Parks material separately supports the protected-area identities and, for Phou Hin Poun, explicitly places Kong Lor, Nam Non and The Rock within the park.

## Release policy

This identity pass is staged as **r45 candidate**. `latest` remains r44.

Do not promote r45 until:

1. build CDN passes;
2. canonical validation confirms identity coverage for all 141 Laos cards;
3. hierarchy validation passes;
4. the five `composite_needs_split` cards have either been structurally split or explicitly remain as blockers for the next structural pass.

No further object-by-object enrichment should be spent on the five composites before their split.
