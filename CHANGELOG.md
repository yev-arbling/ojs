# Changelog

All notable changes to OJS are documented here. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-17

Initial public release.

### Added

- **Core schema** — 21 domains, ~290 fields total across REQUIRED / RECOMMENDED / CONDITIONAL / OPTIONAL tiers.
- **Sub-vertical discriminator pattern** — `product_type` activates 5 specialized modules: `pearls`, `watch`, `smart`, `body`, `estate`.
- **JSON Schema (Draft 2020-12)** — strict mode, 108 model definitions, auto-generated from Pydantic v2 source.
- **JSON-LD context** — Schema.org-compatible vocabulary mapping with `ojs:` namespace for jewelry-specific extensions.
- **Codelists** (8 files) — versioned controlled vocabularies: metals, gems, treatments, hallmarks, eras, settings, pearls, styles.
- **Pydantic v2 reference implementation** — `src/python/ojs/models/` — canonical source of truth.
- **7 platform transformers** — `src/python/ojs/transformers/`:
  - `schema_org` — JSON-LD Product
  - `gmc` — Google Merchant Center feed
  - `acp` — OpenAI Agentic Commerce Protocol (2026-04-17 spec)
  - `ucp` — Google Universal Commerce Protocol
  - `perplexity` — Perplexity Merchant feed (GMC CSV)
  - `shopify` — Shopify Product + metafields (round-trip via `ojs.full`)
  - `mcp` — Model Context Protocol resources
- **23 domain reference docs** — `docs/domains/` — FHIR-grade per-field documentation.
- **5 examples** — engagement ring, pearl necklace, vintage watch, smart ring, body piercing.
- **21-test pytest suite** — model validation, discriminator enforcement, transformer export, Shopify round-trip integrity.

### Authoritative reference data corrections

These corrections were made based on Stage 2 research (Prompt 4):

- **AGS Laboratories** marked as legacy-only — the lab closed end-2022 and merged into GIA. The `GradingLab.AGS` enum value retained for legacy reports but flagged.
- **ASTM F1295** correctly defined as **Ti-6Al-7Nb titanium alloy**, NOT pure niobium. Pure niobium is **ASTM B392-18**. Both enum values present in `BiocompatibilityStandard`.
- **FTC vermeil rule** correctly cited as **16 CFR §23.5** (not §23.4 — common documentation error).
- **UN/CEFACT micron unit code** uses **"4H"** for micrometers (some sources incorrectly cite "UNT").
- **ACP file-upload spec** dated **2026-04-17** with `is_eligible_search` / `is_eligible_checkout` flat boolean fields.

### Architecture

- **Strict mode** Pydantic config (`extra="forbid"`) — unknown fields raise validation errors. Use the `x_*` prefix convention for extensions.
- **Discriminator enforcement** via `model_validator(mode="after")` — `product_type=pearl` without `pearls` module raises a clear ValidationError.
- **Multilingual support** — `title_localized`, `description_localized`, etc., keyed by ISO 639-1.
- **Confidence scoring** — `ai_commerce.confidence_scores` dict keyed by dotted field paths. Dual thresholds: ≥0.80 auto-publish, 0.50–0.80 review, <0.50 drop.

### Licensing

- Dual-licensed: **CC0 1.0** for vocabulary/schema/codelists (LICENSE-CC0); **Apache 2.0** for the reference implementation (LICENSE-APACHE).
- DCO sign-off for contributions (no CLA).

### Governance

- 5-seat steering committee (3 external seats — Arbling does not hold majority).
- Quarterly minor release cadence target.
- 6-month migration window for breaking (major) changes.

### Known limitations and future work

- **`from_*` transformers (reverse direction) are LOSSY** for everything except Shopify (which round-trips via the canonical `ojs.full` json metafield). Pull data via OJS-aware exporters where possible.
- **No `from_acp` validator** — ACP's category_attributes dict is unstructured; reverse parse requires platform-specific heuristics deferred to consumers.
- **GMC reverse parser** decodes top-level fields but leaves `product_detail` triples as raw — full reverse decoding deferred to v1.1.
- **Sustainability claims are not audit-chain-verified** — fields are descriptive; consumers should verify against W3C Verifiable Supply Chain CG outputs once available.

[1.0.0]: https://github.com/openjewelryschema/ojs/releases/tag/v1.0.0
