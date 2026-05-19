# Relationships

> **Tier**: Tier 2 (required for variants) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/relationships.py`

## Overview

Product relationships: variants (same product, different size/color/metal), sets (matching earrings + necklace), pairs, accessories (chain for pendant), substitutes. The relationships module bridges OJS SKUs to:

- **Schema.org** `ProductGroup` + `hasVariant` / `isVariantOf`
- **GMC** `item_group_id`
- **ACP** `group_id` + `variant_dict` + `Custom_variant1/2/3` + `relationship_type` enum
- **Shopify** Product → Variants (up to 3 option axes, 2048 variants total)

Shopify's 3-axis cap is the binding constraint: model your variant taxonomy around 3 axes max for clean Shopify mapping.

## When to populate

Required when the product has variants (any axis: size, color, metal, stone size). Optional but useful for related-product recommendations (cross-sell, upsell, complete-the-set).

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `item_group_id` | string ≤100 | 🟡 | Group ID across variants |
| `variant_axes` | list[VariantAxis] (≤3) | ⚪ | Variation dimensions |
| `is_master_variant` | bool | ⚪ | This SKU is canonical |
| `related_products` | list[ProductRelation] | ⚪ | Cross-references |

### `VariantAxis` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string ≤50 | ✅ | Axis name |
| `value` | string ≤100 | ✅ | This SKU's value on the axis |

Common jewelry variant axes:
- `metal_color` (yellow_gold / white_gold / rose_gold)
- `metal_type` (gold / silver / platinum)
- `ring_size` (US 5–9 in ½ steps)
- `chain_length` (16in / 18in / 20in / 24in)
- `stone_carat` (0.5ct / 1.0ct / 1.5ct / 2.0ct)
- `stone_cut` (round / princess / cushion)

### `ProductRelation` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `related_sku` | ItemID | ✅ | SKU of related product |
| `relationship_type` | RelationshipType | ✅ | Type |
| `description` | string ≤500 | ⚪ | — |

### `relationship_type` (RelationshipType enum)

Matches ACP's `relationship_type` enum:

| Value | Description |
|---|---|
| `variant` | Same product, different axis |
| `is_variant_of` | This is variant of related_sku |
| `part_of_set` | E.g. earrings of matching set |
| `pairs_with` | Often bought together |
| `substitute` | Equivalent alternative |
| `replaces` | This SKU supersedes related_sku |
| `successor_of` | Same item, newer version |
| `different_brand` | Same model, different brand |
| `accessory` | Chain for pendant, box, polishing cloth |
| `required_part` | Pendant requires chain (sold separately) |

## Validation rules

- `variant_axes` is capped at 3 entries (Shopify constraint).
- If `variant_axes` is non-empty, `item_group_id` must be set.
- `related_sku` should be a valid SKU in the catalog (not enforced; caller responsibility).
- Bidirectional relationships should be expressed on both ends (if A `pairs_with` B, B should `pairs_with` A).

## Lessons learned & gotchas

- **Shopify caps variants at 2048 per product.** Multi-stone customizable rings (10 metal × 8 size × 30 stone options = 2400) exceed this. Split into multiple products by metal, with size/stone as the 2 axes within each.
- **ACP `Custom_variant1/2/3`** map order matters for ChatGPT filtering UI. The recommended order for jewelry is:
  1. `Custom_variant1 = metal_color`
  2. `Custom_variant2 = ring_size` (or chain_length for non-rings)
  3. `Custom_variant3 = stone_carat` (or stone_cut)
- **GMC `item_group_id`** must be the SAME value across all variants for them to group in Shopping. Use a stable group ID (e.g. the master SKU without size/color suffix).
- **Master variant flag**: Shopify implicitly treats the first variant as master; OJS makes it explicit. Set exactly one variant per product to `is_master_variant=true` for clarity.
- **Sets**: a matching earrings + necklace + bracelet "wedding set" has each item as a separate SKU with `relationship_type=part_of_set` cross-references. Don't model the set itself as a separate SKU unless it's sold as a bundle.
- **"Pairs with" should be curated, not algorithmic.** AI agents follow these links. Bad recommendations damage trust; "engagement ring → coffee mug" because of historical co-purchase is not useful.

## References

- [Schema.org ProductGroup](https://schema.org/ProductGroup)
- [GMC `item_group_id` documentation](https://support.google.com/merchants/answer/6324507)
- [OpenAI ACP `relationship_type` enum](https://developers.openai.com/commerce/specs/file-upload/products)
- [Shopify product/variant model](https://shopify.dev/docs/api/admin-rest/products/product)
