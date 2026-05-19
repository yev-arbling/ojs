# Body Jewelry

> **Tier**: Tier 2 (sub-vertical, conditionally required) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/body.py`

## Overview

Piercing jewelry has **unique material safety requirements** due to long-term skin/mucosa contact. Material disclosure is critical — wrong-material jewelry causes rejection, infection, and migration. The Association of Professional Piercers (APP) maintains strict standards; OJS captures the technical compliance fields.

For initial (healing) piercings, only ASTM F138/F136/F1295/B392-graded materials plus 14k+/18k+ gold and platinum are considered safe per APP Minimum Standards. Threading type and surface finish matter — externally threaded jewelry damages tissue when inserted through fresh piercings.

## When to populate

**Activated when `product_type == "body"`** (discriminator-enforced as required).

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `piercing_location` | PiercingLocation | ✅ | Intended piercing site |
| `suitable_for_initial_piercing` | bool | 🟡 | Per APP standards |
| `biocompatibility_standards` | list[BiocompatibilityStandard] | 🟡 | Material safety standards |
| `gauge` | GaugeMeasurement | 🟡 | Wire/bar thickness |
| `bar_length_mm` | float >0 | 🟡 | Post length / ring diameter |
| `threading_type` | ThreadingType | ⚪ | internally / externally / threadless |
| `end_size_mm` | float >0 | ⚪ | Decorative end diameter |
| `nickel_free_certified` | bool | ⚪ | EU 94/27/EC |
| `autoclave_safe` | bool | ⚪ | Sterilizable |

### `piercing_location` (PiercingLocation enum)

Ear: `ear_lobe`, `ear_helix`, `ear_tragus`, `ear_daith`, `ear_rook`, `ear_conch`, `ear_industrial`. Nose: `nose_nostril`, `nose_septum`, `nose_bridge`. Face: `eyebrow`, `lip_labret`, `lip_monroe`, `lip_medusa`, `tongue`. Body: `navel`, `nipple`, `surface`, `dermal` (microdermal anchor), `genital`. Plus `other`.

### `biocompatibility_standards` (list[BiocompatibilityStandard])

CRITICAL reference data — many catalogs get these wrong:

| Standard | Material | Notes |
|---|---|---|
| `astm_f138` | 316LVM surgical stainless steel | Implant grade |
| `astm_f136` | Ti-6Al-4V titanium | Implant grade |
| `astm_f1295` | **Ti-6Al-7Nb alloy** | ⚠️ NOT pure niobium |
| `astm_b392_18` | Unalloyed niobium | For pure niobium body jewelry |
| `iso_5832_2` | Unalloyed titanium (CP-Ti) | |
| `iso_5832_3` | Wrought Ti-6Al-4V | |
| `gold_14k_plus` | ≥14k gold | APP-acceptable for initial |
| `gold_18k_plus` | ≥18k gold | Premium choice for sensitive piercings |
| `platinum_950` | Pt 950 | Hypoallergenic, expensive |
| `glass_borosilicate` | Solid borosilicate glass | Inert, no leaching |
| `none_disclosed` | — | Not safe for initial piercings |

**Common confusion**: ASTM F1295 is a **titanium-aluminum-niobium ALLOY** (Ti-6Al-7Nb), not pure niobium. Catalogs frequently list "ASTM F1295 Niobium" when they mean the alloy. For unalloyed niobium body jewelry, use `ASTM_B392_18`.

### `gauge` (GaugeMeasurement object)

Body jewelry gauge is **INVERSE**: lower number = thicker.

| Gauge (US) | mm | Common use |
|---|---|---|
| 20g | 0.8 | Nose nostril, helix (thin) |
| 18g | 1.0 | Nose, ear cartilage |
| 16g | 1.2 | Eyebrow, helix, daith, rook |
| 14g | 1.6 | Tongue, navel, nipple, septum |
| 12g | 2.0 | Stretched lobes |
| 10g | 2.4 | Stretched |
| 8g | 3.2 | Stretched |
| 6g | 4.0 | Stretched |
| 4g | 5.0 | Stretched |
| 2g | 6.5 | Stretched |
| 0g | 8.0 | Stretched |
| 00g | 9.3 | Stretched |

Both `gauge_us` (string like `"14g"`) and `diameter_mm` should be populated when known.

### `bar_length_mm`

For straight barbells: total bar length. For curved barbells (eyebrow): chord length. For circular barbells (CBR): inner diameter. For labrets: post length only (not including disc).

Common labret/barbell lengths: 6 mm, 8 mm, 10 mm, 12 mm, 14 mm, 16 mm.

### `threading_type` (ThreadingType enum)

| Value | Description | Safety for initial |
|---|---|---|
| `internally_threaded` | Threading inside the bar | **Preferred** |
| `externally_threaded` | Threading on the bar | Avoid for fresh piercings |
| `threadless` | Press-fit | OK |
| `hinged` | Hinged segment ring | OK |
| `captive_bead` | Bead held by ring tension | OK |
| `seamless` / `segment` | Continuous rings | OK |
| `push_pin` | Threadless variant | OK |
| `other` | Free-text | — |

Externally threaded jewelry has threads that scrape the piercing channel during insertion — major cause of fresh-piercing damage.

### `nickel_free_certified`

EU Nickel Directive 94/27/EC compliance. **Critical for piercings** — nickel allergy is the most common contact allergy in piercing wearers (~17% of women, ~3% of men in EU populations).

### `autoclave_safe`

Whether the piece can be sterilized in a steam autoclave (134°C, 18 PSI). Required for piercing-studio use; not needed for end-consumer sales.

## Validation rules

- `piercing_location` required.
- If `suitable_for_initial_piercing == true`, `biocompatibility_standards` must include one of: `ASTM_F138`, `ASTM_F136`, `ASTM_F1295`, `ASTM_B392_18`, `GOLD_14K_PLUS`, `GOLD_18K_PLUS`, `PLATINUM_950`, `GLASS_BOROSILICATE`. APP-aligned.
- `gauge` strongly recommended.
- `bar_length_mm ≤ 50` (reality check).

## Lessons learned & gotchas

- **The F1295 confusion is endemic.** Audit your catalog — if anything is labeled "Niobium ASTM F1295", verify whether it's actually the Ti-Al-Nb alloy (most common) or true unalloyed niobium (use B392-18 instead).
- **"Surgical steel" is meaningless** without F138 spec. Generic 316 stainless ≠ implant-grade 316LVM. Catalogs that list "surgical steel" with no ASTM reference should be treated as `none_disclosed`.
- **PTFE / Bioplast threaded jewelry**: flexible polymer, acceptable for healing but not all piercers endorse. Not in the enum; use `none_disclosed` or capture in free-text `materials_described` if extended.
- **Gold-plated body jewelry is NOT safe for initial piercings.** Plating wears in the channel, exposing base metal. The `gold_14k_plus`/`gold_18k_plus` standards require SOLID gold, not plated.
- **Septum jewelry sizing differs from nostril.** Septums use shorter bar lengths (6–8 mm typical) and larger gauges (16g–14g typical) vs. nostrils (8–10 mm, 18–20g).
- **Children's "first piercings"**: piercing studios that pierce minors should disclose use of CPSIA-compliant materials (Consumer Product Safety Improvement Act, US). Add `legal.regulatory_flags: [cpsia_compliant]` for children's lobe piercing sets.

## References

- [Association of Professional Piercers — Minimum Standards](https://safepiercing.org/jewelry/)
- [ASTM F138 — Wrought 18Cr-14Ni-2.5Mo stainless steel](https://www.astm.org/f0138-19.html)
- [ASTM F136 — Wrought Ti-6Al-4V](https://www.astm.org/f0136-13r21e01.html)
- [ASTM F1295 — Wrought Ti-6Al-7Nb](https://www.astm.org/f1295-16.html)
- [ASTM B392-18 — Niobium and Niobium Alloys](https://www.astm.org/b0392-18.html)
- [EU Nickel Directive 94/27/EC](https://eur-lex.europa.eu/eli/dir/1994/27/oj)
