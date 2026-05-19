# Commerce

> **Tier**: Tier 1 (REQUIRED) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/commerce.py`

## Overview

Pricing, availability, fulfillment. The single most platform-critical domain — every distribution channel demands price, currency, availability, and a URL. ACP additionally requires `return_policy_url` for checkout eligibility.

Multi-offer pieces (same SKU sold by multiple sellers, or with regional pricing variations) use multiple `Offer` entries. The `primary_offer_index` (default 0) is the canonical offer used for short-form syndication.

## When to populate

Always. `commerce` is a required module on every `JewelryProduct`, with at least one `Offer`.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `offers` | list[Offer] | ✅ | ≥1 commercial offer |
| `primary_offer_index` | int ≥0 | ⚪ | Canonical offer (default 0) |

### `Offer` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `price` | Money | ✅ | Price + currency |
| `sale_price` | Money | ⚪ | Sale price |
| `sale_starts` / `sale_ends` | datetime | ⚪ | Sale window |
| `availability` | Availability enum | ✅ | Stock state |
| `availability_date` | date | ⚪ | When preorder ships |
| `url` | URL | ✅ | Product page URL |
| `condition` | Condition enum | ⚪ (default `new`) | New/used/vintage/antique |
| `inventory_count` | int ≥0 | ⚪ | Units in stock |
| `target_countries` | list[CountryCode] | ✅ | ISO 3166-1 alpha-2, ≥1 |
| `seller_name` | string ≤70 | ✅ | Seller name |
| `seller_url` | URL | ✅ | Seller website |
| `return_policy_url` | URL | 🟡 | Required for ACP eligible_checkout |
| `seller_privacy_policy_url` | URL | ⚪ | — |
| `seller_tos_url` | URL | ⚪ | — |
| `accepted_payments` | list[PaymentMethod] | ⚪ | Visa/Affirm/Klarna/… |
| `bnpl_available` | bool | ⚪ | **Strong AI ranking signal** |
| `free_shipping` | bool | ⚪ | — |
| `free_shipping_threshold` | Money | ⚪ | Min order for free shipping |
| `handling_time_days` | int ≥0 | ⚪ | Days from order to ship |
| `free_engraving` | bool | ⚪ | — |
| `lifetime_warranty` | bool | ⚪ | — |
| `warranty_description` | string ≤500 | ⚪ | — |

### `price` (Money)

`amount` is a `Decimal` (stored as string for JSON round-trip without float drift); `currency` is ISO 4217 (e.g. `"USD"`, `"EUR"`).

### `availability` (Availability enum)

`in_stock`, `out_of_stock`, `preorder`, `backorder`, `discontinued`, `limited_availability`, `made_to_order`, `unknown`.

Maps to:
- Schema.org `https://schema.org/InStock` etc.
- GMC `availability` (in_stock / out_of_stock / preorder / backorder)
- ACP `availability`

### `condition` (Condition enum)

`new`, `refurbished`, `used`, `estate`, `vintage`, `antique`. `estate`, `vintage`, `antique` are jewelry-trade-specific conditions; downstream platforms collapse them to `used`.

### `target_countries`

ISO 3166-1 alpha-2 list (e.g. `["US", "CA", "GB"]`). **ACP-required** — ACP rejects offers without a target_countries list. A piece that ships globally should still list specific countries; never use a wildcard.

### `return_policy_url`

URL to the return policy page. **ACP requires this for `is_eligible_checkout=true`** in 2026. Without it, ChatGPT will list the product but won't trigger the checkout flow.

### `bnpl_available`

Whether BNPL (Affirm, Klarna, Afterpay, Shop Pay Installments) is offered. **Strong AI ranking signal**: BNPL availability lifts conversion 20–35% per multiple BNPL provider studies, and several AI agents weight it in product comparisons.

### `accepted_payments` (list[PaymentMethod])

`visa`, `mastercard`, `amex`, `paypal`, `apple_pay`, `google_pay`, `affirm`, `klarna`, `afterpay`, `shop_pay`, `bank_transfer`, `crypto`, `other`.

## Validation rules

- `offers` must have at least one entry.
- Each Offer must have `price`, `availability`, `url`, `target_countries` (≥1), `seller_name`, `seller_url`.
- For ACP eligibility: `return_policy_url` must be set, and `availability == "in_stock"`.
- If `sale_price` is set, `price` should be the original (compare-at) price.
- `sale_starts < sale_ends` if both present.

## Lessons learned & gotchas

- **Don't store prices as floats.** Decimals via string round-trip (`{"amount": "8500.00", ...}`). Float drift breaks tax/total reconciliation.
- **"Free shipping" without `target_countries` is meaningless.** A retailer offering "free shipping" only in the US must list `target_countries=["US"]`.
- **`condition=vintage` and `condition=estate`**: trade-equivalent. Use `estate` when the piece comes via consignment/auction; `vintage` when the retailer claims period (20+ years old). Both collapse to `UsedCondition` in Schema.org.
- **Multi-currency**: don't try to express EUR + USD in a single Offer. Create two Offers, one per currency, with appropriate `target_countries`.
- **Made-to-order vs preorder**: `made_to_order` is "I will craft this for you"; `preorder` is "I will have this in stock". Both delay shipping, but the AI agent messaging differs.
- **ACP `is_eligible_checkout` depends on this module**: missing `return_policy_url` is the #1 reason an ACP product fails eligibility.

## References

- [Schema.org/Offer](https://schema.org/Offer)
- [OpenAI ACP file-upload spec 2026-04-17](https://developers.openai.com/commerce/specs/file-upload/products)
- [GMC required attributes (Apparel & Accessories)](https://support.google.com/merchants/answer/6324468)
- [ISO 4217 currency codes](https://www.iso.org/iso-4217-currency-codes.html)
- [Affirm/Klarna BNPL conversion lift case studies](https://www.affirm.com/business/case-studies)
