# OJS v1.0 — Domain Reference

The Open Jewelry Schema is composed of **21 domains** organized into three tiers, plus 2 cross-cutting modules (`audit`, `ai_commerce`).

## Tier 1 — REQUIRED on every product

| Domain | Module | Required when | Doc |
|---|---|---|---|
| Identity | `identity` | Always | [identity.md](identity.md) |
| Commerce | `commerce` | Always | [commerce.md](commerce.md) |
| Media | `media` | Always (≥1 image) | [media.md](media.md) |
| Audit | `audit` | Always | [audit.md](audit.md) |

## Tier 2 — REQUIRED conditionally (sub-vertical discriminators)

Activated by `product_type` discriminator:

| Domain | Module | Required when | Doc |
|---|---|---|---|
| Pearls | `pearls` | `product_type == "pearl"` | [pearls.md](pearls.md) |
| Watch | `watch` | `product_type == "watch"` | [watch.md](watch.md) |
| Smart | `smart` | `product_type == "smart_wearable"` | [smart.md](smart.md) |
| Body | `body` | `product_type == "body"` | [body.md](body.md) |
| Estate | `estate` | `product_type == "estate"` | [estate.md](estate.md) |

## Tier 3 — RECOMMENDED (high-value optional)

| Domain | Module | Use for | Doc |
|---|---|---|---|
| Metals | `metals` | Metal-bearing pieces | [metals.md](metals.md) |
| Stones | `stones` | Stone-bearing pieces | [stones.md](stones.md) |
| Setting | `setting` | How stones are mounted | [setting.md](setting.md) |
| Sizing | `sizing` | Physical dimensions | [sizing.md](sizing.md) |
| Style | `style` | Era, design tags, motifs | [style.md](style.md) |
| Certification | `certification` | Lab reports | [certification.md](certification.md) |
| Sustainability | `sustainability` | Ethical sourcing claims | [sustainability.md](sustainability.md) |
| Care | `care` | Cleaning, storage | [care.md](care.md) |
| Relationships | `relationships` | Variants & related products | [relationships.md](relationships.md) |
| Reviews | `reviews` | Aggregate rating | [reviews.md](reviews.md) |
| Legal | `legal` | Cross-border compliance | [legal.md](legal.md) |

## Tier 4 — OPTIONAL specialized

| Domain | Module | Use for | Doc |
|---|---|---|---|
| Artisan | `artisan` | Handmade / edition pieces | [artisan.md](artisan.md) |
| Religious | `religious` | Faith / ceremonial pieces | [religious.md](religious.md) |

## Cross-cutting

| Domain | Module | Purpose | Doc |
|---|---|---|---|
| AI Commerce | `ai_commerce` | AI agent ranking metadata | [ai_commerce.md](ai_commerce.md) |
| Audit | `audit` | Provenance / version | [audit.md](audit.md) |

## Field count distribution

- **REQUIRED**: ~18 fields (across identity, commerce, media, audit, product_type)
- **RECOMMENDED**: ~55 fields
- **CONDITIONAL**: ~80 fields (activated by product_type)
- **OPTIONAL**: ~138 fields
- **TOTAL**: ~290 fields across 21+2 domains

## Sub-vertical activation matrix

| product_type | Required sub-vertical module |
|---|---|
| `ring` / `earring` / `necklace` / `bracelet` / `pendant` / `brooch` / `anklet` / `jewelry_set` / `other` | (none) |
| `pearl` | `pearls` |
| `watch` | `watch` |
| `smart_wearable` | `smart` |
| `body` | `body` |
| `estate` | `estate` |

## Conventions

- All enum values are **snake_case**.
- All multilingual fields key by **ISO 639-1** (2-letter lowercase).
- All country codes are **ISO 3166-1 alpha-2** (2-letter uppercase).
- All currency codes are **ISO 4217** (3-letter uppercase).
- All dimensions in **millimeters** unless otherwise specified.
- All weights in **grams** (metals, total piece) or **carats** (gemstones).
- All datetimes in **ISO 8601 with timezone**.
