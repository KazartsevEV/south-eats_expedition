# Media and country culture UI standard

## Image interaction contract

This is a project-wide rule for every current and future country, object, gallery and culture card.

1. A click on a photograph opens the image itself in the site lightbox.
2. The lightbox must support zooming and closing without navigating away from the expedition site.
3. `media.url` is the image-media URL (direct file, CDN mirror, or a file redirect such as Wikimedia `Special:FilePath`). It must never be a Wikipedia/Wikimedia description page.
4. `media.source_page` is attribution/provenance only. It may appear as a separate “Источник” link, but it is never the click target of the photograph.
5. A media entity keeps `provider`, `license`, `artist`, and `checked_at` when known.
6. If a local full-resolution mirror is introduced later, the lightbox target changes to that mirror while `source_page` remains the provenance link. The semantic contract does not change.

## Country food cards

For a country with researched food data, `profile.street_food[]` should use rich rows rather than bare dish names.

Required rich-row fields:
- `name`
- `description` — short, factual description of what the dish is
- `where_common` — where it is actually common/easy to find; country-wide claims need evidence
- `format` — market / street stall / roadside vendor / local cafe / restaurant, so restaurant pricing is not mislabeled as street food
- `price_usd_range` — approximate price for the stated format, not a generic restaurant average
- `price_context` — what market/menu snapshot the range represents
- `checked_at`
- `source_refs`
- `media_id`

Prices are snapshots. Delivery fees, temporary discounts and tourist-zone restaurant prices must not be silently mixed into a “typical street-food price”. When delivery/menu platforms are used as evidence, the card states that this is a menu snapshot and walk-up prices may differ.

## Country festival cards

For a country with researched festival data, `profile.festivals[]` should use rich rows.

Required rich-row fields:
- `name`
- `description` — what is actually observed or done
- `where_common` — where a traveler can realistically observe it; distinguish nationwide observance from one ceremonial venue
- `checked_at`
- `source_refs`
- `media_id`

Recommended when relevant:
- `access_cost` — whether ordinary observation is free, ticketed, or venue-dependent

Use `dates_YYYY` for year-specific dates and `status_YYYY` for current cancellations, relocations or other material changes. A recurring traditional description and a current-year operational status are separate facts.

## UI

Country food and festival blocks are visual card grids. Photography is part of the card, not a decorative external link. Clicking the photograph opens the image lightbox; the source-page link is shown separately with attribution.
