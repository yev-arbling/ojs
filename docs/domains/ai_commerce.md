# AI Commerce

> **Tier**: Tier 3 (cross-cutting; strongly recommended for AI-channel sellers) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/ai_commerce.py`

## Overview

AI agent-specific metadata: semantic descriptions written FOR machines (not humans), query keywords, occasion/audience tags, price tier, confidence scores per field. This module is the **structural difference** between "this product is visible to AI" (table-stakes — Schema.org + GMC) and "this product is CHOSEN BY AI" (OJS's wedge).

The module is **cross-cutting**: it describes the product as a whole, AND it carries per-field confidence metadata for the Arbling enrichment pipeline. Confidence scores are surfaced to retailers so they can prioritize human review.

## Confidence scoring philosophy

Dual thresholds:
- `≥0.80` — auto-publish, no review needed
- `0.50 – 0.80` — needs Ira's confirmation (retailer-side reviewer)
- `<0.50` — do not publish

Confidence sources (`ConfidenceSource` enum from `_common.py`):
- `manual` — human-entered (1.00)
- `certificate` — imported from GIA/IGI PDF (0.99)
- `regex_text` — pattern-matched from description (0.85–0.95)
- `cv_image` — computer vision from product photo (0.60–0.96 depending on field)
- `llm_inferred` — LLM inferred from context (0.50–0.85)
- `default` — schema default fallback (0.20)

Arbling pipeline confidence targets per field (internal):
- `metals.compositions[].color` → 0.96
- `metals.compositions[].type` → 0.98
- `pearls.pearl_type` → 0.92
- `setting.styles[].setting_type` → 0.89
- `style.era` → 0.71 (weakest — recommend human validation)

## When to populate

Strongly recommended. Even partial population (just `semantic_description` and `query_keywords`) substantially improves AI agent ranking.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `semantic_description` | string 20–2000 | ✅ | AI-facing description |
| `semantic_description_localized` | MultilingualString | ⚪ | Translations |
| `query_keywords` | list[string ≤80] (≤30) | ⚪ | Phrases shoppers type |
| `occasion_tags` | list[Occasion] | ⚪ | Purchase occasions |
| `audience_tags` | list[Audience] | ⚪ | Target audiences |
| `style_descriptors` | list[string ≤50] | ⚪ | Aesthetic descriptors |
| `price_tier` | PriceTier | ⚪ | Coarse price tier |
| `confidence_scores` | dict[str, ConfidenceScore] | ⚪ | Per-field confidence |
| `overall_quality_score` | float 0–1 | ⚪ | Aggregate quality |
| `enrichment_completeness_percent` | float 0–100 | ⚪ | % populated |
| `last_enriched_at` | ISO 8601 string | ⚪ | Last run timestamp |

### `semantic_description`

Description written FOR AI AGENTS, not humans. Should be dense, factual, attribute-loaded. Example:

```
"Vintage Art Deco style platinum solitaire engagement ring with
old European cut diamond center stone, milgrain detail, suitable
for engagement and anniversary occasions, GIA certified."
```

vs. the human-facing `identity.description`:

```
"A stunning vintage-inspired platinum engagement ring featuring an
old European cut diamond. Hand-detailed milgrain work showcases
period authenticity. Comes with original GIA report."
```

Difference: semantic description is dense with extractable attributes; human description is emotional/aspirational. **Both serve a purpose.**

### `query_keywords` (list[string ≤80], up to 30)

Phrases real shoppers type. Examples:
- `"art deco engagement ring"`
- `"vintage diamond ring under $5000"`
- `"6-prong platinum solitaire"`
- `"old european cut engagement ring"`

Should overlap with content findable by AI agents through other channels (Google search, reddit, fashion blogs). Avoid keyword stuffing — 5–15 high-quality phrases beat 30 generic ones.

### `occasion_tags` (list[Occasion])

`engagement`, `wedding`, `anniversary`, `birthday`, `valentines`, `mothers_day`, `fathers_day`, `christmas`, `hanukkah`, `graduation`, `prom`, `quinceanera`, `push_present`, `promotion`, `self_purchase`, `everyday`, `evening`, `formal`, `casual`, `bridal_party`, `other`.

### `audience_tags` (list[Audience])

`women`, `men`, `unisex`, `gender_neutral`, `children`, `teens`, `young_adult`, `adult`, `gift_for_her`, `gift_for_him`, `gift_for_parent`, `gift_for_partner`, `gift_for_friend`, `bride`, `groom`, `graduate`.

### `price_tier` (PriceTier enum)

| Value | Range |
|---|---|
| `budget` | <$100 |
| `affordable` | $100–500 |
| `mid_market` | $500–2000 |
| `affordable_luxury` | $2000–10000 |
| `luxury` | $10000–50000 |
| `ultra_luxury` | $50000+ |

Coarse buckets used by AI agents to filter on price intent. Don't auto-derive from `commerce.offers[0].price` — let retailers position deliberately.

### `confidence_scores` (dict)

Keys are **dotted paths** into the product (e.g. `"metals.compositions.0.purity_fineness"`, `"style.era"`); values are `ConfidenceScore` objects.

```python
confidence_scores = {
    "metals.compositions.0.purity_fineness": {
        "value": 0.99,
        "source": "certificate",
        "validated_at": "2026-05-12T10:00:00Z",
    },
    "style.era": {
        "value": 0.71,
        "source": "cv_image",
    },
}
```

Per-field confidence lets the retailer's review UI (Arbling-style) flag low-confidence fields for human attention without re-running the pipeline.

## Validation rules

- `semantic_description` length 20–2000 (longer than human description; less than feed-size cap).
- `query_keywords` capped at 30 entries.
- `confidence_scores` values must be valid `ConfidenceScore` objects.

## Lessons learned & gotchas

- **Don't auto-derive `price_tier` from price.** A $3000 Cartier piece is `affordable_luxury` by price band, but the brand positioning is `luxury`. Let retailers position.
- **Avoid keyword stuffing.** AI agents detect and depress stuffed listings. 5–15 high-quality, distinctive phrases > 30 generic.
- **Confidence scores are for retailers, not consumers.** Don't surface in shopper-facing UI. AI agents that ingest OJS may use them to downrank low-confidence claims.
- **The `era` confidence target (0.71)** is intentionally low — Arbling's pipeline acknowledges era classification is the hardest CV task. Don't fudge to 0.85.
- **Semantic description in English is fine even for multi-locale catalogs.** AI agents handle translation. Localized variants in `semantic_description_localized` are bonus, not required.
- **Occasion/audience overlap**: a piece can target `bride` AND `gift_for_her` — overlap is fine. Adding `gift_for_him` AND `gift_for_her` for the same piece signals truly unisex.
- **`overall_quality_score`** is an aggregate AI agents may use. Don't fabricate; derive from completeness × per-field confidence average.

## References

- [OpenAI ACP file-upload spec 2026-04-17](https://developers.openai.com/commerce/specs/file-upload/products)
- [Perplexity Merchant Program Terms](https://www.perplexity.ai/hub/legal/merchant-program-terms)
- [GMC Product Detail attribute](https://support.google.com/merchants/answer/6324468)
- [Anthropic MCP — Model Context Protocol](https://modelcontextprotocol.io/)
