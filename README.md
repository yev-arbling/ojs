# Open Jewelry Schema (OJS) v1.0

> A free, vendor-neutral data schema for jewelry commerce, designed for the AI agent era.

[![License: CC0 1.0](https://img.shields.io/badge/License%20(vocabulary)-CC0%201.0-lightgrey.svg)](LICENSE-CC0)
[![License: Apache 2.0](https://img.shields.io/badge/License%20(code)-Apache%202.0-blue.svg)](LICENSE-APACHE)
[![Status: 1.0.0](https://img.shields.io/badge/status-1.0.0-green.svg)](#)

OJS is a structured data schema for jewelry that captures the attributes existing standards (Schema.org, GS1, GMC) miss: stone provenance, treatments, ring sizes in eight regional systems, watch movements, CIBJO 7-factor pearl grading, body-jewelry biocompatibility, hallmarks, AR placement metadata, and agent-ranking signals.

**Designed to be consumed by AI shopping agents** (ChatGPT/ACP, Perplexity, Google AI Mode/UCP, Microsoft Copilot, MCP-based agents), AS WELL AS traditional commerce platforms (Shopify, Schema.org, Google Merchant Center).

## What's in the box

- **JSON Schema (Draft 2020-12)** — `spec/v1/ojs-strict.json` — 108 model definitions
- **JSON-LD context** — `spec/v1/context.jsonld` — for Schema.org compatibility
- **Codelists** — `spec/v1/codelists/` — versioned controlled vocabularies (metals, gems, treatments, hallmarks, eras, settings, pearls, styles)
- **Pydantic v2 reference implementation** — `src/python/ojs/` — single source of truth, validates input and generates JSON Schema
- **7 platform transformers** — `src/python/ojs/transformers/` — bidirectional mappers to:
  - Schema.org JSON-LD
  - Google Merchant Center
  - OpenAI ACP (Agentic Commerce Protocol) 2026-04-17
  - Google UCP (Universal Commerce Protocol)
  - Perplexity Merchant feed
  - Shopify (Product + metafields)
  - Model Context Protocol (MCP) resources
- **21 domain reference docs** — `docs/domains/` — FHIR-grade per-field documentation
- **Examples** — `examples/` — realistic sample products per sub-vertical
- **Test suite** — `tests/` — 21 tests covering models, discriminators, transformers, round-trip

## Quickstart

```bash
pip install pydantic>=2.5
git clone https://github.com/openjewelryschema/ojs.git
cd ojs
export PYTHONPATH=src/python
```

```python
from ojs.models import JewelryProduct, ProductType

product = JewelryProduct.model_validate(open("examples/engagement-ring.json").read())
print(product.identity.title, product.commerce.offers[0].price)
```

Export to any platform:

```python
from ojs.transformers import to_schema_org, to_gmc, to_acp, to_shopify_metafields

schema_org_jsonld = to_schema_org(product)   # → JSON-LD <script>
gmc_feed_row     = to_gmc(product)            # → GMC feed row
acp_entry        = to_acp(product)            # → ACP file-upload JSONL entry
shopify_mfs      = to_shopify_metafields(product)  # → Shopify metafield list
```

## Architecture

OJS is a **hybrid modular core + sub-vertical discriminators** pattern (FHIR-inspired):

- **4 always-required modules**: `identity`, `commerce`, `media`, `audit`
- **5 sub-vertical discriminator modules**: `pearls`, `watch`, `smart`, `body`, `estate` — required when `product_type` matches
- **12 recommended optional modules**: `metals`, `stones`, `setting`, `sizing`, `style`, `certification`, `sustainability`, `care`, `relationships`, `reviews`, `legal`, `artisan`, `religious`
- **1 cross-cutting module**: `ai_commerce` — agent ranking metadata

See [docs/domains/README.md](docs/domains/README.md) for the full domain index.

## Tier system

| Tier | Field count | Status |
|---|---|---|
| REQUIRED | ~18 | Must populate on every product |
| RECOMMENDED | ~55 | Strongly recommended for AI agent ranking |
| CONDITIONAL | ~80 | Required when relevant sub-vertical is active |
| OPTIONAL | ~138 | Specialized / niche fields |
| **TOTAL** | **~290** | |

## Sub-vertical discriminator activation

| `product_type` | Required sub-vertical |
|---|---|
| `pearl` | `pearls` |
| `watch` | `watch` |
| `smart_wearable` | `smart` |
| `body` | `body` |
| `estate` | `estate` |
| (other types) | — |

## Validation example

```python
from ojs.models import JewelryProduct, ProductType

# Will raise ValidationError: pearl requires pearls module
JewelryProduct(product_type=ProductType.PEARL, audit=..., identity=..., ...)
```

## License

**Dual-licensed** (FHIR / GS1 pattern):

- **Vocabulary, schema, and codelists** — [CC0 1.0 Universal (public domain)](LICENSE-CC0). You may use the schema and field names without restriction in any commercial or open-source product.
- **This reference implementation (Python code)** — [Apache 2.0](LICENSE-APACHE). Standard patent grant; bring your own copyright notices when redistributing.

## Governance

See [GOVERNANCE.md](GOVERNANCE.md). OJS is governed by a steering committee with named external members beyond the originating maintainer.

## Contributing

Pull requests welcome. We use **DCO (Developer Certificate of Origin)** sign-off, not a CLA. See [GOVERNANCE.md](GOVERNANCE.md).

## Versioning

OJS follows [SemVer](https://semver.org/):

- **Major** (`2.0`): breaking schema changes (renamed/removed fields, enum value removals).
- **Minor** (`1.1`): backwards-compatible additions (new optional fields, new enum values).
- **Patch** (`1.0.1`): documentation, codelist additions, bug fixes in reference implementation.

Codelists version independently of the schema.

## References

This schema synthesizes:

- Schema.org Product + JewelryStore vocabulary
- GS1 Global Product Classification (segment 67 — Jewellery)
- GIA 4Cs (diamonds) and Pearl Description System
- CIBJO Blue Books (Diamond, Coloured Stone, Pearl)
- ISO 8653 (ring sizes), 9202 (fineness), 22810 (watch water resistance)
- ASTM F138/F136/F1295/B392-18 (body jewelry biocompatibility)
- FTC 16 CFR Part 23 (US jewelry disclosure)
- HS 2022 customs codes (chapters 71, 91)
- OpenAI ACP 2026-04-17, Google UCP 2026-01-11
- Anthropic MCP (Model Context Protocol)
