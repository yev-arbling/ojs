# Integration Guides

Step-by-step guides for adding Open Jewelry Schema v1.0 to your storefront.

## What to choose

| Platform | Guide | Transformer available? |
|---|---|---|
| **Shopify** | [shopify-integration.md](shopify-integration.md) | Yes — `to_shopify_metafields()` in `src/python/ojs/transformers/shopify.py` supports round-trip |
| **WooCommerce** | [woocommerce-integration.md](woocommerce-integration.md) | Partial — use `to_schema_org()` from `src/python/ojs/transformers/schema_org.py` for JSON-LD output |

**Use the Shopify guide if:** you're on Shopify and want either a Liquid-based drop-in snippet, or a Python pipeline that pushes metafields via Admin API.

**Use the WooCommerce guide if:** you're on WooCommerce and want a PHP hook that outputs OJS JSON-LD on product pages.

**Use neither (go to [docs/domains/](../domains/README.md)) if:** you're building an enrichment pipeline, running validation in CI, or generating OJS records programmatically — the domain docs and Python transformer reference are more relevant there.

## Common starting point

Both guides follow the same four steps:

1. **Store data** — populate platform-native fields (Shopify metafields / WooCommerce product meta) with OJS values.
2. **Output JSON-LD** — inject a `<script type="application/ld+json">` tag on product pages using the v1.0 schema.
3. **Batch update** — use the platform's REST API to populate fields for existing products.
4. **Validate** — run `ojs-validate product.json` to check against `spec/v1/ojs-strict.json`.

## See also

- [Node.js CLI validator](../../tools/validate-node/) — `npx @openjewelryschema/validate`
- [Python reference implementation](../../src/python/ojs/) — Pydantic v2 models, 7 platform transformers
- [Domain reference docs](../domains/README.md) — per-field documentation for all 21 domains
