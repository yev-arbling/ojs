# Audit

> **Tier**: Tier 1 (REQUIRED) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/_common.py` (AuditMetadata)

## Overview

Provenance and audit metadata for the OJS record itself. Tracks who created the record, when, where (source system), and when a human last validated it end-to-end. **Required on every `JewelryProduct`** — without audit fields, round-trip integrity, compliance, and debugging are all compromised.

Audit is intentionally minimal — its purpose is to capture WHERE the OJS record came from and HOW it has been validated, not to duplicate the operational metadata that downstream systems (Shopify, GMC) already maintain.

## When to populate

Always. `audit` is a required module on every product.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `ojs_version` | SemVer string | ✅ (default `1.0.0`) | OJS spec version |
| `created_at` | datetime (ISO 8601) | ✅ | Record creation |
| `updated_at` | datetime (ISO 8601) | ⚪ | Last update |
| `source_system` | SourceSystem enum | ✅ | Where record was created |
| `source_record_id` | string ≤200 | ⚪ | Source system's native ID |
| `last_validated_by_human` | datetime (ISO 8601) | ⚪ | Last human review |

### `ojs_version`

SemVer string for the OJS spec version this record conforms to. Default `"1.0.0"`. Used by consumers to apply version-specific deserializers and feature flags. Format: `^\d+\.\d+\.\d+$`.

### `created_at` / `updated_at`

ISO 8601 datetime with timezone (use `Z` for UTC). Don't use naive datetimes — different consumers interpret naive datetimes inconsistently. Python `datetime.now(timezone.utc).isoformat()` is the recommended pattern.

### `source_system` (SourceSystem enum)

| Value | Description |
|---|---|
| `manual` | Human-entered (CMS form) |
| `shopify` | Imported from Shopify Admin |
| `arbling_pipeline` | Arbling enrichment pipeline |
| `pim_akeneo` | Akeneo PIM |
| `pim_salsify` | Salsify PXM |
| `pim_syndigo` | Syndigo |
| `gmc_import` | Reverse-engineered from a GMC feed |
| `acp_import` | Reverse-engineered from an ACP entry |
| `other` | — |

### `source_record_id`

The native ID in the source system. For Shopify, this is the Shopify product ID (e.g. `"gid://shopify/Product/123"`). For Akeneo, the Akeneo identifier. Lets downstream pipelines round-trip changes without re-keying.

### `last_validated_by_human`

When a human last reviewed the entire record end-to-end (not just a single field). Different from `ai_commerce.confidence_scores[].validated_at` which is per-field. This is a record-level checkpoint.

## Validation rules

- `created_at` required.
- `source_system` required.
- `ojs_version` must match `^\d+\.\d+\.\d+$`.

## Lessons learned & gotchas

- **Use timezone-aware datetimes.** `datetime.utcnow()` is deprecated in Python 3.12+ in favor of `datetime.now(timezone.utc)`. Pydantic v2 accepts both but the latter is canonical.
- **`source_record_id` is the round-trip key.** When syncing from Shopify back to OJS, this is how you match a Shopify product to its OJS record without ambiguity. SKU is not enough — SKUs can collide across stores.
- **Don't conflate `updated_at` with field-level update times.** Field-level timestamps live in `ai_commerce.confidence_scores[].validated_at`. Record-level `updated_at` is the last time ANY part of the record changed.
- **`last_validated_by_human`** is the compliance audit field. For regulated jewelry (children's, body, conflict-minerals), regulators may ask "when did a human last verify this?". Track it.
- **Don't fake `source_system=manual`** for AI-generated records. Use `arbling_pipeline` (or your equivalent) and let `last_validated_by_human` flag whether a human reviewed.
- **Version migration**: when upgrading to OJS v1.1, do NOT bump `ojs_version` in-place. Run an explicit migration that updates the version, re-validates, and writes a fresh `updated_at`.

## References

- [Pydantic v2 datetime handling](https://docs.pydantic.dev/latest/api/standard_library_types/#datetime-types)
- [ISO 8601 datetime format](https://en.wikipedia.org/wiki/ISO_8601)
- [SemVer 2.0.0](https://semver.org/)
