# Setting

> **Tier**: Tier 3 (recommended if stone-bearing) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/setting.py`

## Overview

How stones are mounted to metal: prong, bezel, pavé, channel, tension, halo. The setting module supports multi-style pieces (engagement ring with prong-set center + pavé side stones) via the `styles` list with `style_id` cross-references from `Stone.setting_style_id`.

Setting type is a strong AI ranking signal for engagement and bridal queries: *"6-prong solitaire"*, *"bezel-set engagement ring"*, *"halo diamond ring"* are all setting-keyed queries.

## When to populate

Recommended for any stone-bearing piece. Not activated when the piece has no stones (pure-metal pieces). For pavé-heavy designs, populate at least one representative setting style — do not enumerate every individual prong.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `styles` | list[SettingStyle] | ✅ | ≥1 setting style |
| `primary_style_id` | string ≤50 | ⚪ | ID of main setting if multiple |

### `SettingStyle` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `style_id` | string ≤50 | ✅ | Local ID for stone cross-ref |
| `setting_type` | SettingType | ✅ | prong/bezel/pavé/… |
| `prong_count` | int 1–12 | ⚪ | For prong/half-bezel only |
| `material` | SettingMaterial | ⚪ | Metal used for setting |
| `head_height_mm` | float >0 | ⚪ | Setting projection above band |
| `gallery_present` | bool | ⚪ | Decorative gallery filigree |
| `notes` | string ≤500 | ⚪ | Free-text |

### `setting_type` (SettingType enum)

| Value | Description |
|---|---|
| `prong` | Most common; 4-prong, 6-prong (Tiffany), 8-prong |
| `bezel` | Encircling metal rim around stone |
| `half_bezel` | Partial bezel — modern, secure |
| `tension` | Stone held by spring tension — minimal visible metal |
| `channel` | Row of stones between two metal walls |
| `pave` | Tiny stones packed close, minimal metal visible |
| `micro_pave` | Pavé with stones <2mm |
| `bar` | Vertical metal bars separating stones |
| `flush` / `gypsy` | Stone sunk flat into metal |
| `invisible` | No visible metal between stones |
| `cluster` | Multiple stones grouped |
| `halo` | Ring of accent stones around a center stone |
| `burnish` | Metal pressed over stone edges |
| `illusion` | Metal extends visual size of stone |
| `suspension` | Drop/pendant style |
| `other` | Free-text via `notes` |

- **Confidence target (Arbling)**: 0.89 (CV reliable on common setting types; weaker on micro_pave vs pave distinction).

### `prong_count`

Number of prongs holding the stone (1–12). Tiffany-style is 6; classic solitaire is 4 or 6; multi-stone settings rarely exceed 8. Only meaningful for `setting_type ∈ {prong, half_bezel}`.

### `style_id` cross-reference

The `style_id` (e.g. `"center"`, `"halo"`, `"side"`) is used by `Stone.setting_style_id` to link stones to their settings:

```python
stones=[
    Stone(species="diamond", carat=1.5, position="center", setting_style_id="center"),
    Stone(species="diamond", carat=0.05, position="halo", setting_style_id="halo"),
],
setting=SettingModule(styles=[
    SettingStyle(style_id="center", setting_type="prong", prong_count=6),
    SettingStyle(style_id="halo", setting_type="pave"),
]),
```

## Validation rules

- `styles` must have at least one entry.
- `prong_count` only valid when `setting_type ∈ {prong, half_bezel}`.
- If `Stone.setting_style_id` is set, it must match a `SettingStyle.style_id` in this module.
- `primary_style_id` if set must match a `style_id`.

## Lessons learned & gotchas

- **"Tiffany setting" is informal.** It commonly means 6-prong solitaire but is occasionally 4-prong. Use `setting_type=prong` + `prong_count=6` for canonical mapping.
- **Pavé vs micro-pavé** is fuzzy. CV models often confuse them. If unsure, use `pave` (broader) and let the description disambiguate.
- **Tension settings** make AI agents nervous — they're durable but appear precarious. Pair with explicit `care.activity_safety` info to reassure buyers.
- **Eternity bands** typically have 20+ identical stones. Don't create 20 SettingStyle entries — one `setting_type=channel` or `setting_type=shared_prong` is enough.
- **Halo settings**: the halo stones use `setting_type=pave` or `setting_type=prong` depending on construction. The "halo" descriptor is more about composition than setting mechanics — capture it via `style.design_styles` if desired.

## References

- [GIA: Engagement Ring Setting Styles](https://www.gia.edu/engagement-ring-settings)
- [De Beers Education: Ring Anatomy](https://www.debeers.com/en-us/the-journey-of-a-diamond/setting-styles)
