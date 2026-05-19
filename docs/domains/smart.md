# Smart

> **Tier**: Tier 2 (sub-vertical, conditionally required) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/smart.py`

## Overview

Smart wearable specifications: smart rings (Oura, Ultrahuman, RingConn), smart bracelets, smart-watch features that go beyond traditional `watch` module fields. Per Google Product Taxonomy, smart watches sit under Jewelry > Watches (ID 201) — NOT Electronics. An Apple Watch / Samsung Galaxy Watch populates BOTH the `watch` module (case, crystal, strap) AND this module (heart rate, GPS, app).

Smart wearables are a fast-evolving category: subscription models, FDA medical clearance, data export portability are increasingly important purchase considerations.

## When to populate

**Activated when `product_type == "smart_wearable"`** (discriminator-enforced as required). Use this product_type for **non-wrist** smart wearables (smart rings, smart pendants). Smart wrist watches use `product_type=watch` and populate both modules.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `features` | list[SmartFeature] | ✅ | ≥1 feature |
| `operating_system` | string ≤50 | ⚪ | OS name + version |
| `app_required` | bool | ⚪ | Companion app needed |
| `app_ios_compatible` | bool | ⚪ | — |
| `app_android_compatible` | bool | ⚪ | — |
| `minimum_ios_version` | string ≤20 | ⚪ | — |
| `minimum_android_version` | string ≤20 | ⚪ | — |
| `battery_life_hours` | float >0 | ⚪ | Typical use hours |
| `battery_life_days` | float >0 | ⚪ | Preferred unit for rings |
| `charging_method` | string ≤50 | ⚪ | magnetic_puck/usb_c/wireless_qi |
| `charge_time_minutes` | int >0 | ⚪ | — |
| `connectivity` | list[Connectivity] | ⚪ | Wireless standards |
| `sensor_count` | int ≥0 | ⚪ | — |
| `sensors` | list[string ≤50] | ⚪ | Sensor names |
| `waterproof_rating` | WaterProofRating | ⚪ | IP/ATM rating |
| `fda_cleared` | bool | ⚪ | FDA medical clearance |
| `fda_clearance_numbers` | list[string ≤50] | ⚪ | 510(k) numbers |
| `ce_certified` | bool | ⚪ | — |
| `subscription_required` | bool | ⚪ | **Strong purchase consideration** |
| `subscription_monthly_usd` | float ≥0 | ⚪ | Monthly subscription |
| `data_export_supported` | bool | ⚪ | — |
| `data_export_formats` | list[string ≤20] | ⚪ | csv/json/hl7-fhir |
| `weight_grams` | float >0 | ⚪ | **Important for rings** |

### `features` (list[SmartFeature])

`heart_rate`, `hrv` (heart rate variability), `spo2` (blood oxygen), `ecg`, `sleep_tracking`, `activity_tracking`, `gps`, `nfc_payment`, `cellular_lte`, `blood_pressure`, `skin_temperature`, `body_battery` (Garmin term), `stress_tracking`, `menstrual_cycle`, `fall_detection`, `crash_detection`, `emergency_sos`, `smart_notifications`, `voice_assistant`, `camera`, `speaker`, `microphone`, `other`.

### `operating_system`

Common values: `"watchOS 11"`, `"Wear OS 4"`, `"Oura OS"`, `"Garmin OS"`, `"Fitbit OS"`, `"Tizen 8.0"` (Samsung older).

### `subscription_required`

Critical purchase consideration. Oura ring requires a $5.99/mo subscription for full features post-2021; this is a frequent AI-agent query (*"Do I need a subscription?"*). Set the boolean + monthly USD price for clarity.

### `connectivity` (list[Connectivity])

`bluetooth_le`, `bluetooth_classic`, `wifi`, `nfc`, `uwb` (Ultra-Wideband — Apple U1/U2), `lte_cat_m1`, `lte_cat_nb1`, `gps`, `glonass`, `galileo`.

### `waterproof_rating` (WaterProofRating enum)

For electronics, IP / ATM ratings:

| Value | Description |
|---|---|
| `ipx4` | Splash |
| `ipx7` | Submersion 1m for 30 min |
| `ipx8` | Submersion >1m (mfr-specified) |
| `ip67` | Dust-tight + IPX7 |
| `ip68` | Dust-tight + IPX8 |
| `3atm` | 30m static (splash only) |
| `5atm` | 50m static (swim OK) |
| `10atm` | 100m |

Strict mapping: 3 ATM ≠ "can wear swimming". 5 ATM is the consumer threshold for swim-safe use.

### `fda_cleared` + `fda_clearance_numbers`

For medical features (ECG, blood pressure, SpO₂, fall detection), FDA 510(k) clearance is the US regulatory marker. Apple Watch Series 4+ has multiple clearances; Oura has none (lifestyle device, not medical). The boolean + list captures this for queries like *"FDA-approved smart ring"* (answer: there isn't one as of 2026-05).

### `data_export_supported` + `data_export_formats`

Increasingly relevant: users want to own their health data. CSV / JSON / HL7-FHIR are common export formats. Oura supports JSON via API; Apple HealthKit exports XML/JSON.

### `weight_grams`

**Critical for smart rings.** Oura Gen3 is 4–6g depending on size; RingConn is 3–5g; Ultrahuman is 2.4–3.6g. Weight perceptibility is a known purchase concern.

## Validation rules

- `features` must have at least one entry.
- `app_required == true` should pair with `app_ios_compatible` and/or `app_android_compatible`.
- `subscription_monthly_usd` requires `subscription_required == true`.
- If `fda_cleared == true`, `fda_clearance_numbers` should be non-empty.

## Lessons learned & gotchas

- **Smart watch ↔ traditional watch dichotomy is collapsing.** Apple Watch is both a watch and a computer. Use `product_type=watch` for wrist-worn smart watches; populate both `watch.movement_type=smart` AND the `smart` module.
- **Battery life under "typical use"** is heterogeneous. Apple Watch Series 9 claims 18 hours; with always-on display + intensive workout tracking, real-world is 8–12 hours. Don't inflate claims.
- **FDA clearance ≠ FDA approval.** 510(k) clearance is "substantially equivalent to a predicate device"; it's the bar most wearables clear. Full FDA approval is for new device classes. AI agents conflate them — store the actual regulatory marker.
- **Subscription lock-in is a sticking point.** Oura's monthly fee for the data the ring already collects irritates users; many AI agent comparisons surface this as a negative. Honestly disclose; don't hide.
- **GDPR / HIPAA**: smart wearables collecting health data fall under HIPAA in the US (in clinical contexts) and GDPR special-category data in the EU. Disclose in privacy policy URL via `commerce.offers[].seller_privacy_policy_url`.
- **Sensor naming inconsistency**: "PPG sensor" (photoplethysmography) vs "optical heart rate sensor" vs "green LED heart rate" — all describe the same hardware. Use the canonical term in `sensors` (`"PPG"`) for cross-product consistency.

## References

- [Apple Watch — Health features](https://www.apple.com/watch/health/)
- [Oura Ring — Sensors and tracking](https://ouraring.com/blog/sensors-and-tracking/)
- [FDA 510(k) Premarket Notification](https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/premarket-notification-510k)
- [IEC 60529 — Ingress Protection ratings](https://www.iec.ch/ip-ratings)
