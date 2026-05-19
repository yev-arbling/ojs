# Stones

> **Tier**: Tier 1 (REQUIRED if stone-bearing) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/stones.py`

## Overview

Gemstone specifications: species, GIA 4Cs (Color/Clarity/Cut/Carat) for diamonds, treatments, origin. The stones module supports multi-stone pieces (engagement ring with center + halo + side stones) via the `stones` list. Stone 0 is conventionally the center / primary stone — confirmed by `center_stone_index` (default 0).

Stones is the highest-leverage domain for AI agent ranking on diamonds: aspirational queries like *"1.5 carat F VS1 lab-grown diamond engagement ring under $5000"* match purely on stones-module fields plus a price filter.

## When to populate

Required for any stone-bearing product. Pearls populate a parallel `pearls` module (CIBJO 7-factor) and SHOULD also appear here as `species=pearl` — duplication is intentional for query consistency.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `stones` | list[Stone] | ✅ | One entry per stone; ≥1 |
| `total_carat_weight` | float >0 | 🟡 | TCW across all stones |
| `center_stone_index` | int ≥0 | ⚪ | Index of center stone (default 0) |

### `Stone` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `species` | GemstoneSpecies | ✅ | diamond/ruby/sapphire/… |
| `species_other` | string ≤100 | ⚪ | Free-text if `species=other` |
| `origin_type` | StoneOrigin | ✅ | natural/lab_grown/simulant |
| `origin_country` | string ≤100 | ⚪ | Geographic origin |
| `carat` | float >0 | 🟡 | Weight in carats |
| `cut` | StoneCut | ⚪ | Cut/shape |
| `length_mm` / `width_mm` / `depth_mm` | float >0 | ⚪ | Dimensions |
| `color_grade` | DiamondColorGrade | ⚪ | D-Z (diamonds only) |
| `color_description` | string ≤100 | ⚪ | Free-text color |
| `clarity_grade` | DiamondClarityGrade | ⚪ | FL/IF/VVS/VS/SI/I |
| `cut_grade` | CutGrade | ⚪ | Excellent/Very Good/Good/… |
| `polish` / `symmetry` | CutGrade | ⚪ | Sub-grades |
| `fluorescence` | FluorescenceIntensity | ⚪ | None/Faint/Medium/Strong |
| `treatments` | list[TreatmentType] | ⚪ | Enhancements (FTC required) |
| `position` | string ≤50 | ⚪ | center/halo/side_1/shank |
| `setting_style_id` | string ≤50 | ⚪ | Cross-ref to setting.styles |

### `species` (GemstoneSpecies enum)

Precious: `diamond`, `ruby`, `sapphire`, `emerald`. Beryl family: `aquamarine`, `morganite`. Quartz: `amethyst`, `citrine`, `smoky_quartz`, `rose_quartz`. Other: `tanzanite`, `topaz`, `tourmaline`, `garnet`, `peridot`, `spinel`, `zircon`, `moissanite`. Organics: `pearl`, `amber`, `coral`, `jet`. Opaque/phenomenal: `opal`, `turquoise`, `lapis_lazuli`, `malachite`, `onyx`, `agate`, `jade_jadeite`, `jade_nephrite`. Plus `other` with free-text fallback.

- **Confidence target (Arbling)**: 0.92 (CV + NER from description).

### `origin_type` (StoneOrigin enum)

`natural`, `lab_grown`, `simulant`, `unknown`. **Required for FTC 16 CFR §23.24** disclosure of lab-grown vs. mined stones — non-disclosure is a deceptive trade practice in the US. `simulant` covers CZ-as-diamond, synthetic-spinel-as-sapphire, etc.

### `carat`

Weight in carats. 1 ct = 200 mg = 0.2 g. UN/CEFACT code `CTM`. For round brilliant diamonds, dimensions and carat correlate (a 6.5mm round is ~1.0 ct).

### `cut` (StoneCut enum)

`round_brilliant`, `princess`, `cushion`, `emerald_cut`, `oval`, `pear`, `marquise`, `radiant`, `asscher`, `heart`, `baguette`, `trillion`, `rose_cut`, `old_european`, `old_mine`, `cabochon`, `briolette`, `fancy`, `other`.

`old_european` and `old_mine` are antique cuts important for estate/vintage pieces; AI agents reliably match queries like *"old european cut diamond ring"*.

### `color_grade` (DiamondColorGrade enum)

GIA D-Z scale. Colorless: D, E, F. Near-colorless: G, H, I, J. Faint: K, L, M. Very-light: N-R. Light: S-Z. Plus Fancy Color descriptors: `fancy_light`, `fancy`, `fancy_intense`, `fancy_vivid`, `fancy_deep`, `fancy_dark` (for fancy yellows, blues, pinks).

### `clarity_grade` (DiamondClarityGrade enum)

`FL`, `IF`, `VVS1`, `VVS2`, `VS1`, `VS2`, `SI1`, `SI2`, `SI3` (note: SI3 is non-GIA; used by EGL), `I1`, `I2`, `I3`.

### `treatments` (list[TreatmentType])

`none`, `heat`, `irradiation`, `laser_drilling`, `fracture_filling`, `oiling`, `dye`, `coating`, `diffusion`, `bleaching`, `hpht_treatment`, `other`. **Required disclosure** per FTC 16 CFR §23.22. Most rubies and sapphires are heat-treated; emeralds are typically oiled. Non-disclosure of treatments is the most common FTC enforcement target in jewelry.

## Validation rules

- `stones` must have at least one entry.
- If any `stone.species == "diamond"`, `origin_type` is required (FTC disclosure).
- If any stone has `treatments` non-empty, downstream syndication should surface them (Schema.org `additionalProperty`, GMC `product_detail`).
- `total_carat_weight` should equal sum of `stone.carat` ± 0.05 (rounding tolerance).
- `color_grade` and `clarity_grade` are diamond-specific; populating them for non-diamonds is allowed but flagged.

## Lessons learned & gotchas

- **AGS Laboratories closed end-2022.** Old AGS reports remain valid; treat as `GradingLab.AGS` legacy only. New diamond grading should go to GIA or IGI. The reference data fix is critical — using AGS for newly-graded stones is a factual error.
- **"Ideal Cut" is ambiguous.** AGS used "Ideal" with rigorous criteria; GIA uses "Excellent" cut grade. OJS uses GIA `CutGrade.EXCELLENT` as the canonical mapping.
- **Padparadscha sapphires** are pinkish-orange — use `color_description` for free-text "Padparadscha" since the GIA color enum doesn't capture this market term.
- **Multi-stone pavé pieces**: don't enumerate every melee diamond (50+ entries explodes feed size). Use `position="pave"` on a single representative Stone with carat = total pavé weight.
- **Lab-grown ≠ simulant.** Lab-grown diamonds are chemically/physically diamonds (CVD or HPHT origin); simulants (CZ, moissanite) are different materials. Conflating these is an FTC violation.
- **GIA color grade "fancy" needs a `color_description`** — "Fancy Vivid Yellow" carries massive premium over "Fancy Light Yellow"; the enum alone doesn't capture market value.

## References

- [GIA 4Cs of Diamond Quality](https://4cs.gia.edu/)
- [CIBJO Diamond Blue Book](https://www.cibjo.org/blue-books/diamond-book/)
- [FTC Jewelry Guides 16 CFR Part 23](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23)
- [ISO 18323:2015 — Consumer confidence in the diamond industry](https://www.iso.org/standard/62113.html)
- [GIA: AGS Lab merger announcement (2022)](https://www.gia.edu/gia-news-research-ags-laboratories)
