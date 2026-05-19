# Sustainability

> **Tier**: Tier 3 (recommended; uneven conversion evidence) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/sustainability.py`

## Overview

Provenance, recycled content, conflict-free claims, carbon offsets, audit chain. Sustainability is a **conversion-evidence-weak domain**: published research does NOT support a clear direct sustainability → conversion lift. The strongest measured effects are:

1. **Price-ceiling lift** (e.g. Brilliant Earth sustains a 10–20% premium over commodity-priced peers).
2. **AI agent ranking bias** — some AI agents weight ESG claims in product comparisons.
3. **Regulatory necessity** — EU Green Claims Directive (2024) and FTC Green Guides 16 CFR Part 260 require substantiation; non-compliant claims are enforcement targets.

**Do not oversell** sustainability to retailers as a primary conversion driver. Capture the data structurally for AI ranking benefits and for regulatory defensibility.

## When to populate

Recommended for any piece making a sustainability claim. Required to be auditable if claimed.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `certifications` | list[SustainabilityCertification] | ⚪ | Held certifications |
| `origin_claims` | list[OriginClaim] | ⚪ | Origin/provenance claims |
| `recycled_metal_percent` | 0–100 | ⚪ | Percent recycled (audit required) |
| `is_conflict_free` | bool | ⚪ | OECD due diligence compliance |
| `is_lab_grown_marketed` | bool | ⚪ | Lab-grown alternative marketing |
| `is_traceable` | bool | ⚪ | Full supply-chain traceability |
| `traceability_url` | URL | ⚪ | Dashboard/blockchain URL |
| `carbon` | CarbonClaim object | ⚪ | Carbon footprint |
| `sustainability_story` | string ≤2000 | ⚪ | Free-text narrative |

### `certifications` (list[SustainabilityCertification])

`rjc_cop` (RJC Code of Practices), `rjc_coc` (RJC Chain of Custody), `kimberley_process` (rough diamonds only), `fairmined` (artisanal gold), `fairtrade_gold`, `scs_recycled` (SCS Global Services), `bluesign`, `oeko_tex`, `wgc_conflict_free`, `diamond_foundry_cert`, `bcorp` (company-level), `other`.

### `origin_claims` (list[OriginClaim])

`canadian_diamond`, `botswana_sort`, `australian_diamond`, `recycled_gold`, `fairmined_gold`, `recycled_platinum`, `recycled_silver`, `single_origin`, `blockchain_tracked`, `other`.

**`australian_diamond`**: post-Argyle (closed 2020), this claim is rare but still valid for stock pre-closure.

### `recycled_metal_percent`

0–100. **Audit chain required** for defensibility. Pair with `certifications: [scs_recycled]` to substantiate. Bare claims without certification face regulatory risk in EU markets.

### `is_conflict_free`

OECD Due Diligence Guidance for Responsible Supply Chains of Minerals from Conflict-Affected and High-Risk Areas. For gold and tin/tungsten/tantalum (3TG), this is enforceable under SEC Form SD (US, Dodd-Frank §1502) for publicly listed companies. The Kimberley Process applies separately to rough diamonds.

### `is_lab_grown_marketed`

Whether the piece is marketed as a lab-grown alternative to mined. FTC 16 CFR §23.24 disclosure required for synthetic stones — non-disclosure is deceptive. This boolean is the marketing posture; actual origin lives on `stones.stones[].origin_type`.

### `is_traceable` + `traceability_url`

Blockchain provenance platforms: Tracr (De Beers), Everledger, Sarine Diamond Journey, Provenance. The URL should point to a public dashboard for the specific piece (e.g. `https://tracr.com/diamond/<id>`).

### `CarbonClaim` (object)

| Field | Type | Description |
|---|---|---|
| `is_carbon_neutral_shipping` | bool | — |
| `is_carbon_neutral_product` | bool | — |
| `carbon_kg_co2e` | float ≥0 | Lifecycle CO₂-equivalent emissions |
| `offset_provider` | string ≤100 | Provider name |
| `offset_verification` | string ≤200 | Verifier (Verra, Gold Standard) |

## Validation rules

- All fields are optional, but...
- `recycled_metal_percent` claim without `certifications` or `traceability_url` should warn (greenwashing risk).
- `is_lab_grown_marketed=true` requires consistent `stones.stones[].origin_type=lab_grown` for at least one stone.
- `carbon.carbon_kg_co2e` without `offset_verification` or `offset_provider` should warn.

## Lessons learned & gotchas

- **Conversion evidence is weak.** Don't claim sustainability sells. Published research (e.g. Bain & Company 2022 Luxury Goods Worldwide Market Study) shows luxury buyers profess sustainability concern but rarely act on it at purchase. The real effects are price-ceiling defense and AI ranking, not direct conversion lift.
- **EU Green Claims Directive (effective 2026)** requires substantiation for environmental claims. "Sustainable", "eco-friendly", "carbon-neutral" claims without third-party certification face administrative penalties.
- **Carbon offsets are scrutinized.** Verra and Gold Standard are the two recognized certification bodies; lesser-known providers face credibility issues. Don't store offset claims without naming the verifier.
- **"Conflict-free diamonds" is broader than "Kimberley Process".** Kimberley addresses rough diamonds and government-sanctioned conflicts. OECD due diligence covers a wider scope (artisanal mining ethics, human rights).
- **Recycled gold claims**: gold has been recycled for millennia; "recycled gold" is the default norm, not a premium claim. Don't market this as differentiating without %, audit chain, and certification.
- **Lab-grown is not inherently sustainable.** CVD/HPHT diamond production is energy-intensive; the sustainability claim depends on grid carbon intensity at the production facility. Capture nuance via `sustainability_story` rather than blanket claims.

## References

- [Responsible Jewellery Council (RJC) Code of Practices](https://www.responsiblejewellery.com/standards/cop/)
- [Kimberley Process Certification Scheme](https://www.kimberleyprocess.com/)
- [Fairmined Standard for artisanal gold](https://fairmined.org/)
- [OECD Due Diligence Guidance for Responsible Supply Chains](https://www.oecd.org/corporate/mne/mining.htm)
- [FTC Green Guides 16 CFR Part 260](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-260)
- [EU Green Claims Directive (2024)](https://environment.ec.europa.eu/topics/circular-economy/green-claims_en)
- [W3C Verifiable Supply Chain Community Group (2026-02-03 proposal)](https://www.w3.org/community/groups/)
