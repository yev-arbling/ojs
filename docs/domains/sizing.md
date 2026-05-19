# Sizing

> **Tier**: Tier 2 (recommended; required for rings) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/sizing.py`

## Overview

Physical dimensions of the piece. The fields you populate depend on the product type:

- **Rings**: `ring_size` (multi-system), `ring_width_mm`, `ring_resizable`
- **Necklaces / bracelets / anklets**: `length_mm`, `adjustable_to_mm`, `chain_width_mm`, `closure`
- **Pendants**: `pendant_width_mm`, `pendant_height_mm`, `drop_length_mm`
- **Earrings**: `earring_drop_mm`, `earring_width_mm`, `closure` (push_back / lever_back / etc.)
- **Brooches**: `brooch_width_mm`, `brooch_height_mm`
- **All**: `total_weight_grams`

Ring sizing follows ISO 8653:2016 (inner circumference in mm) with conversion tables to US, UK, EU, DE, JP/CN, IT, BR systems. Storing the ISO value plus one or two regional values is sufficient for cross-locale shopping.

## When to populate

Required for rings (size is critical for purchase decision). Recommended for all other physical pieces.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `ring_size` | RingSize object | 🟡 | Rings only |
| `ring_width_mm` | float >0 | ⚪ | Band width across finger |
| `ring_resizable` | bool | ⚪ | Can be professionally resized |
| `length_mm` | float >0 | 🟡 | Total length (chains/strands) |
| `adjustable_to_mm` | float >0 | ⚪ | Maximum adjustable length |
| `chain_width_mm` | float >0 | ⚪ | Chain/strand thickness |
| `drop_length_mm` | float >0 | ⚪ | Below clasp/post (pendants/earrings) |
| `pendant_width_mm` / `pendant_height_mm` | float >0 | ⚪ | Pendant dimensions |
| `earring_drop_mm` / `earring_width_mm` | float >0 | ⚪ | Earring dimensions |
| `brooch_width_mm` / `brooch_height_mm` | float >0 | ⚪ | Brooch dimensions |
| `closure` | JewelryClosure enum | ⚪ | Closure mechanism |
| `total_weight_grams` | float >0 | 🟡 | Whole-piece weight |

### `RingSize` object

| Field | Type | Description |
|---|---|---|
| `iso_mm` | float 0–100 | **Canonical**: ISO 8653 inner circumference (mm) |
| `us_ca` | float | US/Canada numeric (4 to 13 typical) |
| `uk_au` | string ≤5 | UK/AU alphabetic (e.g. "M", "N½") |
| `eu` | float | EU (≈ ISO) |
| `de` | float | Germany (fractional inner circumference) |
| `jp_cn` | int | Japan/China numeric |
| `it` | int | Italy |
| `inner_diameter_mm` | float | Diameter alternative |

**Storage convention**: always populate `iso_mm` as canonical; populate `us_ca` for North American markets; populate one additional regional system for primary target markets. Downstream transformers (Shopify, Schema.org) prefer `us_ca` for display.

Ring size conversion table (selected):

| ISO (mm) | US/CA | UK/AU | EU | JP/CN |
|---|---|---|---|---|
| 47.8 | 4 | H½ | 47 | 7 |
| 49.3 | 5 | J½ | 49 | 9 |
| 50.6 | 5½ | K½ | 50 | 10 |
| 51.9 | 6 | L½ | 51 | 12 |
| 53.1 | 6½ | M½ | 53 | 13 |
| 54.4 | 7 | N½ | 54 | 14 |
| 55.7 | 7½ | O½ | 55 | 15 |
| 57.0 | 8 | P½ | 57 | 16 |
| 58.3 | 8½ | Q½ | 58 | 17 |
| 59.5 | 9 | R½ | 59 | 18 |

### `closure` (JewelryClosure enum)

For necklaces/bracelets: `lobster_claw`, `spring_ring`, `box_clasp`, `toggle`, `magnetic`, `screw`, `hook`, `barrel`, `slide`.

For earrings: `push_back`, `lever_back`, `omega_back`, `screw_back`, `french_wire`, `clip_on`.

## Validation rules

- `RingSize.iso_mm` should be in range 40–80 mm for realistic ring sizes.
- If `adjustable_to_mm` is set, it must be > `length_mm`.
- `closure` is required for any necklace/bracelet/anklet (not enforced; warning).

## Lessons learned & gotchas

- **US ring sizes increase in ½ steps but ISO is continuous.** A US 7 is 54.4 mm; US 7¼ is 54.8 mm; US 7½ is 55.7 mm. Don't assume linearity below ½-size precision.
- **UK alphabetic sizes skip "I"** to avoid confusion with "1". Sequence: G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z.
- **Pearl strand "lengths" have conventional names:**
  - Choker: 14–16 in (35–40 cm)
  - Princess: 17–19 in (43–48 cm)
  - Matinee: 20–24 in (50–60 cm)
  - Opera: 28–35 in (70–90 cm)
  - Rope: 36+ in (90+ cm)
  Capture these as free-text in `style.aesthetic_tags` if needed; OJS stores numeric length canonically.
- **Watch sizing** is handled in `watch.case_diameter_mm`, not here. The `sizing` module is for non-watch dimensions.
- **Body jewelry sizing** is handled in `body.gauge` + `body.bar_length_mm`, not here.

## References

- [ISO 8653:2016 — Ring sizes](https://www.iso.org/standard/63776.html)
- [Wikipedia: Ring size conversion table](https://en.wikipedia.org/wiki/Ring_size)
- [Jewelers of America: Ring sizing guide](https://www.jewelers.org/page/RingSize)
