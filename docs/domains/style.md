# Style

> **Tier**: Tier 3 (recommended; high AI-ranking yield) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/style.py`

## Overview

Aesthetic and design classification: era (Georgian → Contemporary), design style tags (minimalist, boho, art_deco-inspired), motifs (floral, celestial, geometric), and free-text aesthetic descriptors. Style fields drive AI agent match for queries like *"art deco engagement ring"*, *"modern minimalist gold bracelet"*, *"vintage-inspired solitaire"*.

Era is particularly valuable for estate/vintage commerce. Style descriptors are multi-valued by design — a piece can be "vintage-inspired", "romantic", and "feminine" simultaneously.

## When to populate

Recommended for all pieces. Especially valuable for fashion-forward, estate, designer, or aesthetic-keyed products. Less impactful for utility pieces (basic stud earrings, classic eternity bands).

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `era` | Era enum | ⚪ | Historical period |
| `design_styles` | list[DesignStyle] | ⚪ | Multi-valued |
| `motifs` | list[Motif] | ⚪ | Multi-valued |
| `aesthetic_tags` | list[string ≤50] | ⚪ | Free-text descriptors, ≤20 items |

### `era` (Era enum)

| Value | Range | Characteristic |
|---|---|---|
| `georgian` | 1714–1837 | Hand-fabricated, closed-back settings, foiled stones |
| `early_victorian` | 1837–1860 | Romantic, naturalistic motifs |
| `mid_victorian` | 1860–1885 | Mourning jewelry, heavy gold |
| `late_victorian` | 1885–1901 | Aesthetic, delicate, diamond-heavy |
| `edwardian` | 1901–1915 | Platinum, lace-like, garland style |
| `art_nouveau` | 1890–1910 | Organic curves, female forms, plique-à-jour enamel |
| `art_deco` | 1920–1935 | Geometric, bold color contrasts, Calibré-cut |
| `retro` | 1935–1950 | Bold, large-scale, rose/yellow gold |
| `mid_century` | 1950–1970 | Diamonds, platinum, marriage emphasis |
| `modernist` | 1960–1980 | Abstract, sculptural, studio jewelers |
| `contemporary` | 1980–present | Anything current |
| `unknown` | — | Period unclear |

- **Confidence target (Arbling)**: 0.71 (CV weakest here — hard to distinguish Edwardian from Art Deco from photos alone; human validation recommended).

### `design_styles` (list[DesignStyle])

`minimalist`, `maximalist`, `classic`, `vintage_inspired`, `boho`, `gothic`, `industrial`, `nature_inspired`, `geometric`, `abstract`, `figurative`, `ethnic`, `tribal`, `romantic`, `edgy`, `unisex`, `feminine`, `masculine`, `other`.

Multi-valued — a piece can be both `minimalist` and `modernist`. AI agents reward more tags (within reason).

### `motifs` (list[Motif])

`floral`, `leaf`, `animal`, `butterfly`, `bird`, `snake`, `heart`, `star`, `moon`, `sun`, `celestial`, `cross`, `knot`, `infinity`, `bow`, `geometric`, `scroll`, `filigree`, `milgrain`, `other`.

### `aesthetic_tags` (free-text list)

Up to 20 free-text descriptors for emerging or niche aesthetics not captured by the enums:

- `"cottagecore"`, `"y2k"`, `"old-money"`, `"dark academia"`, `"clean girl"`, `"quiet luxury"`, `"grandmillennial"`

These tags evolve faster than the enum can — AI agents reward currency.

## Validation rules

- `aesthetic_tags` cap at 20 entries.
- All other fields are optional.

## Lessons learned & gotchas

- **"Art Deco" vs "Art Deco-inspired"**: a piece made in 1925 is `era=art_deco`. A 2024 piece styled after Art Deco is `era=contemporary, design_styles=[vintage_inspired], aesthetic_tags=["art deco style"]`. Don't conflate.
- **Era ranges are conventional, not absolute**. Some appraisers extend Art Deco to 1939; OJS uses 1920–1935 as the strict CIBJO-aligned range.
- **CV confidence on era is low** (~0.71 in Arbling's pipeline). Recommend human validation before publishing era-keyed claims for premium estate pieces — incorrect era attribution depresses the appraisal value.
- **`design_styles=[unisex]`** vs `audience_tags=[unisex]` (in ai_commerce) are related but not redundant: design_styles describes the *piece*, audience_tags describes the *target buyer*. A "feminine"-styled piece can still target a "gift_for_him" audience.
- **Don't stuff `aesthetic_tags`** with synonyms (avoid `["vintage", "old", "antique", "retro"]` all on one piece — pick 1–2 most specific).

## References

- [V&A Museum: Jewellery periods](https://www.vam.ac.uk/articles/jewellery-through-history)
- [Christie's: Antique jewelry periods](https://www.christies.com/en/stories/the-evolution-of-jewellery-design)
- [The Adventurine: vintage style guide](https://theadventurine.com/)
