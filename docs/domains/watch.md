# Watch

> **Tier**: Tier 2 (sub-vertical, conditionally required) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/watch.py`

## Overview

Watch-specific specifications: movement, complications, case, crystal, bezel, water resistance, strap. Per Google Product Taxonomy, **watches sit under Jewelry > Watches (ID 201)**, NOT Electronics — even smart watches. This module covers traditional + smart watches' mechanical attributes; for smart features (heart rate, GPS, app), also populate `smart`.

This domain is highly attribute-dense — luxury watch buyers expect detailed disclosure (caliber, jewel count, frequency, power reserve). AI ranking on watch queries (*"Rolex Submariner 41mm"*, *"automatic GMT watch under $5000"*) keys on these fields directly.

## When to populate

**Activated when `product_type == "watch"`** (discriminator-enforced as required).

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `movement_type` | MovementType | ✅ | automatic/manual_wind/quartz/… |
| `caliber` | string ≤50 | 🟡 | e.g. "ETA 2824-2", "Rolex 3235" |
| `cosc_chronometer` | bool | ⚪ | COSC certified |
| `master_chronometer` | bool | ⚪ | METAS Master Chronometer (Omega) |
| `complications` | list[WatchComplication] | ⚪ | Multi-valued |
| `power_reserve_hours` | float >0 | ⚪ | Hours of power reserve |
| `frequency_hz` | float >0 | ⚪ | Beat frequency (4 Hz = 28,800 vph) |
| `jewel_count` | int 0–100 | ⚪ | Movement jewels |
| `case_shape` | CaseShape | ⚪ | round/square/cushion/… |
| `case_diameter_mm` | float >0 | 🟡 | Primary size dimension |
| `case_thickness_mm` | float >0 | ⚪ | Profile thickness |
| `case_lug_to_lug_mm` | float >0 | ⚪ | Lug span |
| `case_lug_width_mm` | float >0 | ⚪ | Strap width |
| `case_material` | string ≤50 | ⚪ | steel/gold/titanium/ceramic |
| `crystal_type` | CrystalType | ⚪ | sapphire/mineral/acrylic/hardlex |
| `crystal_coating_ar` | bool | ⚪ | Anti-reflective coating |
| `bezel_type` | string ≤50 | ⚪ | unidirectional_dive/tachymeter/gmt_24h |
| `rotating_bezel` | bool | ⚪ | — |
| `water_resistance` | WaterResistanceRating | ⚪ | ISO 22810 |
| `shock_resistance_iso_1413` | bool | ⚪ | ISO 1413 compliant |
| `magnetic_resistance_gauss` | int ≥0 | ⚪ | Magnetic resistance |
| `strap_type` | StrapType | ⚪ | leather/metal/rubber/… |
| `strap_material` | string ≤50 | ⚪ | Free-text material |
| `bracelet_type` | string ≤50 | ⚪ | oyster/jubilee/president/milanese |
| `dial_color` | string ≤50 | ⚪ | — |
| `lume_type` | string ≤50 | ⚪ | Super-LumiNova C3, Chromalight |
| `box_papers_included` | bool | ⚪ | **Collector signal** |
| `serviced_date` | string (YYYY-MM-DD) | ⚪ | Last service date |

### `movement_type` (MovementType enum)

`automatic` (self-winding mechanical), `manual_wind` (hand-wound mechanical), `quartz` (battery-powered), `solar_quartz` (Seiko/Citizen Eco-Drive), `kinetic` (Seiko Kinetic), `spring_drive` (Grand Seiko hybrid), `meca_quartz` (mechanical chrono + quartz base), `smart` (use SmartModule too), `other`.

### `caliber`

The specific movement designation. Examples: `"ETA 2824-2"`, `"Rolex 3235"`, `"Omega 8800"`, `"Sellita SW200"`, `"Miyota 9015"`. Strongly recommended for mid-range and luxury watches — collectors search by caliber.

### `cosc_chronometer` / `master_chronometer`

`cosc_chronometer`: Contrôle Officiel Suisse des Chronomètres certified (±4/+6 sec/day standard).

`master_chronometer`: METAS Master Chronometer — Omega's standard above COSC; ±0/+5 sec/day, 15,000 Gauss magnetic resistance. Currently only Omega meets this; the field is here for forward compatibility.

### `complications` (list[WatchComplication])

`chronograph`, `date`, `day_date`, `gmt`, `dual_time`, `moonphase`, `perpetual_calendar`, `annual_calendar`, `equation_of_time`, `tourbillon`, `power_reserve_indicator`, `alarm`, `minute_repeater`, `world_time`, `second_time_zone`, `small_seconds`, `big_date`, `regulateur`, `chime`, `other`.

### `WaterResistanceRating` (object)

| Field | Description |
|---|---|
| `atm` | Atmospheres (1 ATM = 10m static depth) |
| `meters` | Equivalent depth in meters |
| `iso_22810_compliant` | ISO 22810:2010 compliant |
| `iso_6425_divers` | ISO 6425 divers' watch (≥100m + safety features) |

**Real-world wearability** (industry conservative):
- 3 ATM / 30m: splash resistant only
- 5 ATM / 50m: light swimming
- 10 ATM / 100m: swimming, snorkeling
- 20+ ATM / 200m+: diving (with ISO 6425 ideally)

### `box_papers_included`

For pre-owned watches, this is the single largest value differentiator. "Full set" (box, papers, all original accessories) commands 20–40% premium over watch-only. Strong AI ranking signal for collectors.

## Validation rules

- `movement_type` required.
- If `cosc_chronometer == true`, `movement_type` should be `automatic` or `manual_wind` (quartz can't be COSC).
- If `complications` includes `chronograph`, the caliber should be a chronograph-capable movement (warning, not blocked).
- `frequency_hz` typical values: 2.5 (18,000 vph), 3 (21,600 vph), 4 (28,800 vph), 5 (36,000 vph).

## Lessons learned & gotchas

- **Smart watches use BOTH `watch` and `smart` modules.** A Apple Watch is `product_type=watch` (per Google Product Taxonomy) with both modules populated. Don't use `product_type=smart_wearable` for wrist-worn smart watches — reserve that for non-wrist smart wearables (Oura ring, smart bracelets).
- **Apple Watch / Samsung Galaxy Watch**: set `movement_type=smart`. The `caliber` field is replaced functionally by `smart.operating_system`.
- **Quartz "accuracy" is often misstated.** Standard quartz: ±15 sec/month. High-accuracy quartz (Grand Seiko 9F, Bulova Precisionist): ±10 sec/year. Capture in `caliber` not as a generic claim.
- **Diving watch rating**: ISO 6425 is the strict standard (helium escape valve, magnetic resistance, etc.). A 200m watch without ISO 6425 is "water resistant to 200m" — buyer should not dive with it. Both pieces of information matter; the boolean disambiguates.
- **Case material "steel"** is ambiguous — usually 316L stainless. Specify `"316L stainless steel"` or `"904L stainless steel"` (Rolex's harder alloy) for collector accuracy.
- **Vintage watches** also populate `estate` module (provenance, hallmarks if any, restoration history, period verification). Don't drop the estate module just because watch is the primary discriminator.

## References

- [ISO 22810:2010 — Watches with diver functionality](https://www.iso.org/standard/57495.html)
- [ISO 6425:2018 — Diver's watches](https://www.iso.org/standard/72736.html)
- [ISO 1413:2016 — Shock resistance](https://www.iso.org/standard/65091.html)
- [COSC certification](https://www.cosc.swiss/)
- [METAS Master Chronometer](https://www.metas.ch/)
- [Hodinkee Reference: Movement glossary](https://www.hodinkee.com/articles/the-hodinkee-glossary)
