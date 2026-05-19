# Care

> **Tier**: Tier 3 (recommended; medium AI yield) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/care.py`

## Overview

Care, cleaning, storage, and activity-safety instructions. **Medium AI ranking impact**: agents directly answer queries like *"Is this waterproof?"*, *"Can I shower with this?"*, *"Is this hypoallergenic?"*. Structured care data lets an agent answer authoritatively; absence forces the agent to either say "I don't know" or hedge — both depress conversion.

Care recommendations are jewelry-specific: opals and pearls are damaged by ultrasonic cleaners; emeralds dissolve in acetone; kunzite fades in direct sunlight. Capture the "avoid" list explicitly — buyers want safety information, not generic advice.

## When to populate

Recommended for all pieces. Especially valuable for pieces with delicate stones (pearls, opals, emeralds), vintage pieces, or smart wearables with specific care requirements.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `cleaning_methods` | list[CleaningMethod] | ⚪ | Recommended cleaning approaches |
| `activity_safety` | list[ActivitySafety] | ⚪ | Safe + avoid-list activities |
| `storage` | list[StorageRecommendation] | ⚪ | Storage recommendations |
| `professional_inspection_recommended_months` | int 1–120 | ⚪ | Inspection cadence |
| `care_instructions_text` | string ≤2000 | ⚪ | Free-text English |
| `care_instructions_localized` | MultilingualString | ⚪ | Translations |

### `cleaning_methods` (list[CleaningMethod])

| Value | Description |
|---|---|
| `mild_soap_water` | Most pieces |
| `jewelry_cleaner` | Commercial cleaner |
| `ultrasonic_safe` | Diamonds, sapphires, rubies (untreated) |
| `ultrasonic_avoid` | **Opal, pearl, emerald, tanzanite, kunzite** |
| `steam_safe` | Diamonds (untreated) |
| `steam_avoid` | Most colored stones, treated stones |
| `polishing_cloth_only` | Silver, vintage pieces |
| `professional_only` | Antique, delicate, heirloom |
| `avoid_water` | Pearl strands (silk cord), vintage pieces with cement |

### `activity_safety` (list[ActivitySafety])

| Value | Description |
|---|---|
| `shower_safe` | Can be worn in shower |
| `swimming_safe` | Pool-chlorine safe |
| `ocean_safe` | Salt-water safe |
| `exercise_safe` | Won't catch/snag |
| `sleep_safe` | Won't catch on bedding |
| `avoid_perfume` | Pearls, opals, soft metals |
| `avoid_lotion` | Same |
| `avoid_household_chemicals` | Bleach, ammonia |
| `avoid_direct_sun` | **Kunzite, amethyst, topaz** (fading) |

### `storage` (list[StorageRecommendation])

| Value | Description |
|---|---|
| `soft_pouch` | Individual fabric pouch |
| `jewelry_box_divided` | Compartmented box (avoid scratches) |
| `airtight_bag` | Silver (slow tarnish) |
| `dry_environment` | All |
| `avoid_humidity` | Pearls, vintage, leather straps |
| `lay_flat` | Pearl strings (prevent string stretch) |

### `professional_inspection_recommended_months`

Months between recommended professional inspections (1–120). Suggested defaults:
- Prong settings: 6–12 months (prong wear common)
- Pavé / micro-pavé: 6 months
- Pearls (knotted strands): 12–24 months (restring)
- Watches (mechanical): 36–60 months (full service)
- Estate / vintage: 12 months

### `care_instructions_text`

Free-text English ≤2000 chars. Used by AI agents for direct quotation in answers. Be concrete, not aspirational.

## Validation rules

- All fields are optional.
- `professional_inspection_recommended_months` must be in 1–120 range if set.
- Logical pairs warn if violated: `swimming_safe=true` with `ultrasonic_avoid=true` is suspicious (probably a fashion piece with delicate components).

## Lessons learned & gotchas

- **Stone-specific avoidance lists are crucial.** Don't write "avoid harsh chemicals" — name them. Opal damaged by water, emerald damaged by acetone, kunzite faded by UV — these are the queries.
- **"Hypoallergenic" is not a care field** — it's a material property. Capture via `metals.hypoallergenic_certified` and `metals.nickel_free`.
- **Smart wearables have unique care needs** — water-resistance ratings, battery storage, app-driven firmware. Use the `smart` module fields, supplement with `care` for general practices.
- **Pearl strings need yearly restringing.** Set `professional_inspection_recommended_months=12` for knotted pearl strands.
- **Plated pieces wear**: vermeil and gold-plated pieces last 1–3 years with daily wear. Reflect this in `care_instructions_text` to set buyer expectations and avoid returns.
- **AI agents quote freely from this field.** Inaccuracies (e.g. claiming a glued piece is shower-safe) become customer-service problems. Be conservative.

## References

- [GIA: Jewelry care guide](https://www.gia.edu/jewelry-care)
- [American Gem Society: Gemstone care](https://www.americangemsociety.org/category/gemstone-care/)
- [Cultured Pearl Association: Pearl care](https://culturedpearlassociation.org/pearl-care/)
- [Watch and Jewelry Care: industry best practices](https://www.jewelers.org/page/Care)
