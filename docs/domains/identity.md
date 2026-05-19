# Identity

> **Tier**: Tier 1 (REQUIRED) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/identity.py`

## Overview

Product identifiers and human-facing metadata: SKU, GTIN, MPN, brand, model, title, description. Identity is the **most platform-critical** domain in OJS — every external syndication channel (Schema.org, GMC, ACP, UCP, Shopify, MCP) demands a stable identifier, a title, and a brand. Failing to populate `identity` correctly blocks ingestion into every downstream system.

Identity also carries the **localized variants** of title and description, used by retailers selling in multiple locales. The `handle` field is a URL-safe slug; if absent, downstream transformers derive one from `title`.

## When to populate

Always. `identity` is a required module on every `JewelryProduct`.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `sku` | string (1–100) | ✅ | Stable SKU |
| `title` | string (1–150) | ✅ | Product name |
| `title_localized` | MultilingualString | ⚪ | Translations |
| `description` | string (1–5000) | ✅ | Plain-text description |
| `description_localized` | MultilingualString | ⚪ | Translations |
| `brand` | Brand object | ✅ | Manufacturer/maker |
| `gtin` | string (8/12/13/14 digits) | 🟡 | GS1 GTIN — **major AI ranking signal** |
| `mpn` | string (≤70) | ⚪ | Manufacturer Part Number |
| `model` | string (≤100) | ⚪ | Model name |
| `collection` | string (≤100) | ⚪ | Collection / line name |
| `designer` | string (≤100) | ⚪ | Designer (if not same as brand) |
| `handle` | slug (lowercase + hyphen) | ⚪ | URL-safe identifier |

Legend: ✅ required · 🟡 strongly recommended · ⚪ optional

### `sku`

Stable SKU. Must not change across catalog refreshes; downstream agents (ACP `item_id`, GMC `id`) cache search results and dedupe by this key. If you must rename, use `relationships.related_products` with `relationship_type=replaces` to preserve continuity.

- **Validation**: 1–100 chars, no whitespace constraint but ASCII recommended.
- **Confidence target**: 1.00 (always manual).
- **Mappings**: Schema.org `sku` · GMC `id` · ACP `item_id` · Shopify `variant.sku`.

### `title`

Product name. ≤150 chars per ACP and GMC limits. **Avoid all-caps**; GMC's quality scoring penalizes shouting. Avoid stuffing keywords — semantic match comes from `description` and `ai_commerce.query_keywords`.

- **Validation**: 1–150 chars.
- **Multilingual**: yes (use `title_localized`).
- **Mappings**: Schema.org `name` · GMC `title` · ACP `title` · Shopify `product.title`.

### `description`

Plain-text description ≤5000 chars per ACP. Markdown and HTML are **not** allowed in this field — use Shopify's `body_html` (built by the Shopify transformer) for rich text. AI agents extract attributes by NER from this field, so include facts (carat, fineness, dimensions) even when they exist in structured form elsewhere; it improves retrieval recall.

- **Validation**: 1–5000 chars.
- **Mappings**: Schema.org `description` · GMC `description` · ACP `description` · Shopify `product.body_html` (HTML-wrapped).

### `brand`

Brand object: `name` (required, ≤70 chars), optional `legal_name`, `website`, `logo_url`, `gln` (GS1 13-digit Global Location Number). The 70-char cap exists because ACP and GMC both impose it. Use `legal_name` when the legal entity differs (e.g. `name="Tiffany"`, `legal_name="Tiffany and Company"`).

- **Mappings**: Schema.org `brand` → `Brand` · GMC `brand` (name only) · ACP `brand` (name only) · Shopify `vendor`.

### `gtin`

GTIN-8/12/13/14. **Strongly recommended** — major AI ranking signal. GMC matches GTINs to its product catalog to pull aggregate reviews, price history, and competitive listings; products with GTINs rank measurably higher in Shopping. Fine jewelry rarely has UPCs, but custom GTIN assignment via GS1 is cheap (~$30/yr per company prefix for ≤10 GTINs).

- **Validation**: 8, 12, 13, or 14 digits exactly. Pydantic enforces `^\d{8}$|^\d{12}$|^\d{13}$|^\d{14}$`.
- **Confidence target**: 0.99 if from manufacturer; 0.50 if AI-extracted from packaging photos.

### `mpn`

Manufacturer Part Number — used in combination with `brand` when no GTIN exists. ACP and GMC accept this as a near-equivalent identifier for ranking. Particularly useful for watches (e.g. Rolex `126610LN`).

### `model`

Model name for collectibles (watches, signed pieces). E.g. `"Submariner Date 126610LN"`, `"Tank Française"`. Distinct from `collection` (broader grouping).

### `handle`

Lowercase URL-safe slug. Used by Shopify product URLs (`/products/<handle>`). If you do not provide one, the Shopify transformer slugifies `title`.

## Validation rules

- `sku` must be present and non-empty.
- `title.length ≤ 150` (ACP/GMC requirement).
- `description.length ≤ 5000` (ACP requirement).
- `brand.name.length ≤ 70` (ACP/GMC requirement).
- `gtin` must match `\d{8|12|13|14}` exactly if present.

## Lessons learned & gotchas

- **GMC vs. Shopify SKU semantics differ**. Shopify SKUs are per-variant; GMC `id` is per-offer-instance. The `relationships.item_group_id` field bridges this.
- **Don't change `sku` to "improve" it**. Even cosmetic updates break ACP cached search results for 24–72 hours.
- **GTIN absence is OK for vintage/estate** — GMC won't penalize as long as `mpn` or `brand+title` is present, but new mainline pieces should have GTINs.
- **Localized fields default to `en`**. If only one language is set, downstream platforms fall back to `description` regardless of user locale.

## References

- [Schema.org/Product](https://schema.org/Product)
- [Google Merchant Center attribute spec](https://support.google.com/merchants/answer/7052112)
- [OpenAI ACP file-upload spec 2026-04-17](https://developers.openai.com/commerce/specs/file-upload/products)
- [GS1 GTIN allocation rules](https://www.gs1.org/standards/id-keys/gtin)
- [Shopify Product API](https://shopify.dev/docs/api/admin-rest/products/product)
