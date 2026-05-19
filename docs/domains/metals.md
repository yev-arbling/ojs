# Metals

> **Tier**: Tier 1 (REQUIRED if metal-bearing) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/metals.py`

## Overview

Precious metal composition: base metal type, fineness (parts-per-1000), color, finish, plating. The metals module supports **multi-metal pieces** (two-tone rings, tri-color gold) via the `compositions` list with a `primary=true` flag on the dominant metal. Fineness is the canonical purity representation; karat is derivable for gold but stored separately for convenience.

This is one of OJS's highest-yield enrichment domains: Arbling's CV pipeline reliably extracts `metal_color` at ~0.96 confidence from product photos. Metal disclosure is also legally required in most jurisdictions (FTC 16 CFR §23.5 in the US, UK Hallmarking Act 1973 in the UK).

## When to populate

Required for any piece containing precious metal. Skip for pure-pearl on silk cord, pure-gemstone-on-string, or fabric pieces where metal is incidental.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `compositions` | list[MetalComposition] | ✅ | One per distinct metal; ≥1 |
| `total_metal_weight_grams` | float >0 | ⚪ | Sum across compositions |
| `nickel_free` | bool | ⚪ | EU 94/27/EC compliant |
| `hypoallergenic_certified` | bool | ⚪ | ASTM F2999 / EN 1811 |
| `conflict_free` | bool | ⚪ | OECD due diligence |
| `recycled_content_percent` | 0–100 | ⚪ | Recycled content % |

### `MetalComposition` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | MetalType enum | ✅ | gold/silver/platinum/… |
| `purity_fineness` | int 1–999 | 🟡 | Parts per 1000 |
| `purity_karat` | float 0–24 | ⚪ | Karat (gold only) |
| `color` | MetalColor | ⚪ | yellow/white/rose/… |
| `finish` | MetalFinish | ⚪ | polished/matte/… |
| `plating` | PlatingType | ⚪ | Plating type |
| `plating_thickness_microns` | float >0 | ⚪ | µm (UN/CEFACT `4H`) |
| `weight_grams` | float >0 | ⚪ | Per-composition weight |
| `primary` | bool | ⚪ | Dominant metal flag (exactly one) |
| `hallmark` | string ≤50 | ⚪ | Stamped hallmark |

### `type` (MetalType enum)

Base metal types: `gold`, `silver`, `platinum`, `palladium`, `rhodium`, `titanium`, `niobium`, `steel`, `tungsten`, `brass`, `bronze`, `copper`, `other`.

- **Confidence target (Arbling)**: 0.98 (CV + cert reliable).
- **Mappings**: Schema.org `material` (composed) · GMC `material` (slash-separated 3 metals) · ACP `material` · Shopify `jewelry.metal_type` metafield.

### `purity_fineness`

Parts per 1000 — the canonical purity representation. Examples:

| Metal | Common fineness values |
|---|---|
| Gold | 999 (24k), 916 (22k), 750 (18k), 585 (14k), 417 (10k), 375 (9k) |
| Silver | 999 (fine), 958 (Britannia), 925 (sterling), 900 (coin) |
| Platinum | 999, 950 (standard), 900, 850 |
| Palladium | 999, 950, 500 |

- **Validation**: 1–999 integer.
- **Confidence target**: 0.97 (regex from hallmark text) or 1.0 (cert).
- **Mappings**: GMC `product_detail[Metal/Fineness]` · ACP `category_attributes.metal_fineness` · Shopify `jewelry.metal_fineness` (number_integer).

### `color` (MetalColor enum)

`yellow`, `white`, `rose`, `green`, `black`, `natural`, `two_tone`, `tri_color`. `green` refers to green gold (Au+Ag alloy). `natural` is the default for silver/platinum.

- **Confidence target (Arbling)**: 0.96 (CV very reliable on metal color).

### `plating` (PlatingType enum)

`none`, `gold_plated`, `gold_filled`, `vermeil`, `rhodium_plated`, `silver_plated`, `platinum_plated`, `black_rhodium`, `rose_gold_plated`.

**Vermeil** (`vermeil`) requires ≥10k gold over sterling silver with **plating thickness ≥2.5 µm** per FTC 16 CFR §23.5. Set `plating_thickness_microns` accordingly to substantiate the claim.

**Gold-filled** is mechanically bonded with a thicker layer (typically ≥5% by weight in the US). Don't confuse with `gold_plated` — these are legally distinct claims.

### `nickel_free`

EU Nickel Directive 94/27/EC compliance — required for pieces in prolonged skin contact in the EU. White gold and base-metal jewelry frequently contain nickel; rhodium plating masks but doesn't eliminate nickel exposure as the plating wears.

### `recycled_content_percent`

0–100. **Audit chain required** for the claim to be defensible. Suggest pairing with `sustainability.certifications` (SCS-Recycled or equivalent) when published.

## Validation rules

- `compositions` must have at least one entry.
- Exactly one composition should have `primary=true` (warning, not blocked, if zero or multiple — but downstream transformers pick the first).
- If `plating == "vermeil"`, `plating_thickness_microns ≥ 2.5` is expected (warning if missing).
- `purity_karat` and `purity_fineness` should be consistent (`karat ≈ fineness × 24 / 1000` ± 1).
- `recycled_content_percent` claim requires `sustainability.certifications` to be non-empty for audit defensibility.

## Lessons learned & gotchas

- **Catalogs commonly list "Niobium" without ASTM spec.** ASTM F1295 is **Ti-6Al-7Nb alloy**, NOT pure niobium — pure unalloyed niobium is ASTM B392-18. For body jewelry use `BiocompatibilityStandard.ASTM_B392_18` if it's pure niobium, `ASTM_F1295` only for the Ti-Al-Nb alloy.
- **Fineness 583 vs 585**: 14k gold can be stamped either way (583⅓ rounded). OJS canonicalizes to `585`.
- **"Gold" without fineness is a red flag.** GMC may reject as misleading; require `purity_fineness ≥ 375` for gold pieces.
- **Two-tone pieces**: the second composition needs its own MetalComposition entry, NOT a `color="two_tone"` on a single composition. The `two_tone` enum value is for short-form descriptors only.

## References

- [ISO 9202:2019 — Fineness of precious metal alloys](https://www.iso.org/standard/76925.html)
- [FTC 16 CFR §23.5 — Precious metals](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23)
- [UK Hallmarking Act 1973](https://www.legislation.gov.uk/ukpga/1973/43)
- [EU Nickel Directive 94/27/EC](https://eur-lex.europa.eu/eli/dir/1994/27/oj)
- [ASTM B392-18 — Niobium and Niobium Alloys](https://www.astm.org/b0392-18.html)
- [UN/CEFACT Recommendation 20 (units of measure)](https://unece.org/trade/uncefact/cl-recommendations)
