# Pearls

> **Tier**: Tier 2 (sub-vertical, conditionally required) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/pearls.py`

## Overview

CIBJO 7-factor pearl grading: type, luster, surface, shape, color, overtone, size. Plus nacre quality, matching grade, treatments. Pearls follow a fundamentally different grading system from gemstones — there is no "carat × cut × clarity × color" 4Cs framework. Instead, the CIBJO Pearl Blue Book defines seven independent quality factors, plus pearl species type (the single most economically important attribute).

For pieces with pearls, populate BOTH `stones` (with `species=pearl`) AND `pearls`. The duplication is intentional: search agents querying "pearl necklace" hit the `stones` index, while agents querying "Akoya AAA luster" hit the `pearls` index.

## When to populate

**Activated when `product_type == "pearl"`** (discriminator-enforced as required) OR any stone has `species == "pearl"` (strongly recommended).

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `pearl_type` | PearlType | ✅ | Akoya/South Sea/Tahitian/Freshwater/… |
| `luster` | PearlLuster | ✅ | excellent/very_good/good/fair/poor |
| `surface_quality` | PearlSurface | ✅ | clean/lightly/moderately/heavily blemished |
| `shape` | PearlShape | ✅ | CIBJO 7-shape classification |
| `body_color` | PearlBodyColor | ✅ | Primary body color |
| `overtone` | PearlOvertone | ⚪ | Secondary translucent color |
| `nacre_quality` | NacreQuality | 🟡 | thick/acceptable/thin/unknown |
| `nacre_thickness_mm` | float >0 | ⚪ | Measured if known |
| `size_mm` | float >0 | ✅ | Diameter (longest axis for non-round) |
| `size_range_mm` | string ≤20 | ⚪ | Strand range like "7.0-7.5" |
| `pearl_count` | int ≥1 | ✅ (default 1) | Number of pearls in piece |
| `matching_grade` | PearlMatchingGrade | ⚪ | For strands |
| `drilling` | string ≤50 | ⚪ | fully_drilled/half_drilled/undrilled |
| `treatments` | list[string ≤50] | ⚪ | bleached/dyed/irradiated/pinking |

### `pearl_type` (PearlType enum)

The single most price-relevant attribute. Common values:

| Type | Species | Origin | Size range | Typical price |
|---|---|---|---|---|
| `akoya` | *Pinctada fucata* | Japan/China | 2–10 mm | $$ – $$$ |
| `south_sea` | *Pinctada maxima* | Australia/Indonesia/Philippines | 8–20 mm | $$$$ |
| `tahitian` | *Pinctada margaritifera* | French Polynesia | 8–18 mm | $$$ – $$$$ |
| `freshwater` | *Hyriopsis cumingi* | China | 4–14 mm | $ – $$ |
| `sea_of_cortez` | *Pteria sterna* | Mexico | rare | $$$$$ |
| `keshi` | by-product | various | small | $$ |
| `mabe` | half-pearl on shell | various | 10–17 mm | $$ |
| `imitation` | man-made (glass/plastic) | n/a | any | $ |

**`imitation`** MUST be used for man-made/synthetic pearls per FTC 16 CFR §23.26 — non-disclosure is illegal.

### `luster` (PearlLuster enum)

The most subjective but most consequential quality factor. CIBJO categories: `excellent` (AAA — mirror-like, sharp reflections), `very_good`, `good` (AA — bright with some softness), `fair` (A — softer), `poor` (dull/milky).

The "AAA/AA/A" trade shorthand maps roughly to excellent/good/fair — but it's not standardized; CIBJO terms are unambiguous.

### `surface_quality` (PearlSurface enum)

`clean` (AAA equivalent — no visible blemishes), `lightly_blemished` (AA), `moderately_blemished` (A), `heavily_blemished`.

### `shape` (PearlShape enum)

CIBJO 7-shape classification: `round` (most valued; deviation <2% of diameter), `near_round` (2–5%), `oval`, `button`, `drop`, `semi_baroque`, `baroque` (irregular), `circle` (with concentric rings), `keshi`, `other`.

### `body_color` + `overtone`

Body color is the primary hue; overtone is the secondary translucent overlay. White Akoya with a **rose** overtone commands a 20–40% premium over plain white. Tahitian with **peacock** overtone (green + rose + bronze) is the most prized.

### `nacre_quality` / `nacre_thickness_mm`

Nacre is the iridescent calcium-carbonate layer over the nucleus. Thick nacre (>0.5 mm) is durable; thin nacre (<0.35 mm) may show the nucleus and degrade with wear. GIA recommends measuring nacre thickness directly when possible; many Akoya certifications report it explicitly.

### `treatments`

Free-text list (not an enum because pearl treatments are heterogeneous): `bleached`, `dyed`, `irradiated`, `pinking` (light irradiation to enhance pink overtone), `waxed`, `coated`. FTC 16 CFR §23.22 disclosure required.

## Validation rules

- `pearl_type` is required; **`imitation` must NOT be left unset** for man-made pearls (FTC).
- `size_mm` is required.
- If `pearl_count > 1`, `matching_grade` is strongly recommended.
- If `pearl_type == "imitation"`, `nacre_quality` should be `unknown` (or omitted).
- Tahitian pearls (`pearl_type == "tahitian"`) are naturally dark — `body_color == "white"` is implausible and warrants review.

## Lessons learned & gotchas

- **"South Sea" is geographic, not species-specific.** Strictly, `pearl_type == "south_sea"` means *Pinctada maxima* from the South Pacific region. Some retailers mislabel large Filipino freshwater as South Sea — this is FTC-actionable.
- **AAA/AA/A grades are unstandardized.** Use the CIBJO `excellent`/`good`/`fair` mapping consistently. If a supplier provides AAA, mark `luster=excellent`, `surface_quality=clean`.
- **Keshi pearls** are all-nacre (no nucleus) by-products. They command premium for their luster and unique shapes. Don't conflate with treated baroque.
- **Mabe** are half-pearls fused to shell — used in earrings and rings, never strands. Setting structure (`setting.styles[].setting_type=bezel`) is implied.
- **CIBJO vs. GIA**: GIA's Pearl Description System uses slightly different terms ("Excellent / Very Good / Good / Fair" — same 4-tier idea, slightly different labels). OJS aligns with CIBJO terminology; the GIA mapping is documented in transformer code.
- **Size ranges** for strands: report the range in `size_range_mm` (e.g. `"7.0-7.5"`) and the midpoint in `size_mm`. AI agents query both.

## References

- [CIBJO Pearl Blue Book (2020)](https://www.cibjo.org/blue-books/pearl-book/)
- [GIA Pearl Description System](https://www.gia.edu/pearl-description-system)
- [FTC 16 CFR §23.26 — Pearls and cultured pearls](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23)
- [ISO 18323:2015 — Consumer confidence in the diamond industry](https://www.iso.org/standard/62113.html) (analogous disclosure principles)
