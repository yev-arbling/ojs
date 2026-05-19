# Legal

> **Tier**: Tier 2 (required for cross-border / regulated pieces) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/legal.py`

## Overview

Legal and regulatory compliance metadata: HS customs codes, age restrictions, FTC disclosures, conflict-minerals flags, REACH/RoHS/CPSIA compliance, CITES permits. Required for any piece shipping cross-border (HS code + country of origin), regulated content (lead/cadmium in children's jewelry, CPSIA), or controlled materials (CITES for coral, ivory, certain woods).

## When to populate

- **Required** for cross-border commerce: `hs_code` + `country_of_origin`
- **Required** for children's jewelry sold in the US: `cpsia_compliant` flag
- **Required** for any piece with mined diamond / 3TG metals (under SEC Form SD if publicly listed)
- **Required** for treated or lab-grown stones (FTC disclosure flags)
- **Required** for CITES-controlled materials (coral, antique ivory)
- **Optional** elsewhere

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `hs_code` | HSCodePrefix | 🟡 | HS 2022 code (jewelry: 7113, watches: 9101/9102) |
| `hs_code_full` | string (6–10 digits) | ⚪ | Country-specific extensions |
| `country_of_origin` | ISO 3166-1 alpha-2 | 🟡 | Origin country |
| `age_restriction_minimum` | int 0–21 | ⚪ | Minimum buyer age |
| `regulatory_flags` | list[RegulatoryFlag] | ⚪ | Compliance claims |
| `ftc_lab_grown_disclosure` | bool | ⚪ | FTC 16 CFR §23.24 |
| `ftc_treatment_disclosure` | bool | ⚪ | FTC 16 CFR §23.22 |
| `cites_permit_number` | string ≤50 | ⚪ | For restricted materials |

### `hs_code` (HSCodePrefix enum)

HS 2022 codes for jewelry — provided as enum for common headings:

| Code | Description |
|---|---|
| `7101` | Pearls, natural or cultured |
| `710110` | Natural pearls |
| `710121` | Cultured pearls, unworked |
| `710122` | Cultured pearls, worked |
| `710231` | Diamonds, unsorted, non-industrial |
| `710239` | Diamonds, non-industrial, otherwise |
| `710310` | Other precious stones, unworked |
| `710391` | Rubies, sapphires, emeralds — cut |
| `710399` | Other precious/semi-precious stones — cut |
| `711311` | Jewelry of silver |
| `711319` | Jewelry of gold/platinum |
| `711320` | Jewelry of base metal clad with precious metal |
| `7114` | Goldsmiths' / silversmiths' wares (not jewelry) |
| `7115` | Other articles of precious metal |
| `711610` | Articles of natural/cultured pearls |
| `711620` | Articles of precious/semi-precious stones |
| `7117` | Imitation jewellery |
| `711719` | Imitation jewellery of base metal |
| `711790` | Imitation jewellery, other |
| `9101` | Wrist-watches with precious-metal case |
| `9102` | Wrist-watches, other |

### `hs_code_full`

Full HS code (6–10 digits) including country-specific extensions. E.g. US HTS code `7113.19.5085` for "Jewelry of gold/platinum, other". 10-digit US HTS codes can vary by destination country tariff schedule.

### `country_of_origin`

ISO 3166-1 alpha-2 code (e.g. `"IT"`, `"FR"`, `"TH"`, `"IN"`). Required for cross-border shipments; customs use this for duty calculation. Often differs from `commerce.offers[].seller_url` country — country of MANUFACTURE, not selling.

### `regulatory_flags` (list[RegulatoryFlag])

| Value | Description |
|---|---|
| `prop_65_warning` | California Prop 65 (chemical exposure warning) |
| `nickel_directive_compliant` | EU 94/27/EC |
| `cpsia_compliant` | US Consumer Product Safety (children's jewelry) |
| `reach_compliant` | EU REACH |
| `rohs_compliant` | For smart wearables |
| `fcc_certified` | For smart wearables |
| `ce_marked` | EU conformity |
| `kimberley_verified` | Rough diamonds origin |
| `cites_listed` | Endangered species materials |

### `ftc_lab_grown_disclosure` / `ftc_treatment_disclosure`

Booleans confirming disclosures are made per FTC 16 CFR Part 23:
- §23.24: synthetic / lab-grown stone disclosure
- §23.22: treatment disclosure (heat, oiling, irradiation, etc.)

Setting these to `true` doesn't make the disclosure — that happens in `stones.stones[].origin_type` and `stones.stones[].treatments`. The booleans assert "yes, we made the required disclosure in our marketing copy and listings."

### `cites_permit_number`

CITES = Convention on International Trade in Endangered Species. Permit required for international shipment of:
- Black coral, red coral (some species)
- Antique ivory (pre-CITES exemptions complex)
- Tortoiseshell (pre-1947 exempt in some jurisdictions)
- Crocodile/alligator leather straps
- Certain wood inlays (rosewood, ebony — species-specific)

Permit number format varies by issuing country; store as text.

## Validation rules

- For cross-border commerce: `hs_code` and `country_of_origin` should be set (warning, not blocked).
- If `age_restriction_minimum < 13`, `cpsia_compliant` in regulatory_flags is strongly recommended (US).
- If `cites_listed` in regulatory_flags, `cites_permit_number` is required.

## Lessons learned & gotchas

- **HS codes are political.** A piece of jewelry with both precious metal and a non-precious-stone could be 7113 or 7117 depending on customs interpretation. When in doubt, consult a licensed customs broker.
- **Watch HS codes split by case material.** 9101 = precious-metal case; 9102 = other (steel, ceramic, titanium). A Rolex Submariner steel is 9102; a Rolex DateJust gold is 9101.
- **Prop 65 is broad.** California Prop 65 warns about ~900 chemicals. Many alloys (lead-bearing solder, certain pigments) trigger warnings. Cheap base-metal jewelry frequently needs the warning.
- **CPSIA limits**: lead ≤90 ppm in surface coatings, ≤100 ppm in substrates for children's jewelry. Testing certificates needed for ages <12. Fine jewelry typically passes; fashion jewelry often fails.
- **CITES gotchas**: antique-ivory pieces require pre-Convention provenance to ship internationally. Documentation must be from before March 3, 1947 in the US (Endangered Species Act 4(d) rule). Recent dating analysis on ivory may be required.
- **REACH chromium VI in plating**: EU REACH restricts hexavalent chromium plating. Some vintage pieces violate; can't be re-imported into EU without remediation.
- **Country of origin vs assembled-in**: complex pieces with stones from one country and metal from another have a "substantial transformation" rule. Usually the country where final assembly happens determines `country_of_origin`. Edge cases warrant customs broker consultation.

## References

- [HS 2022 — World Customs Organization](https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition.aspx)
- [FTC Jewelry Guides 16 CFR Part 23](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23)
- [CITES Convention](https://cites.org/)
- [US Customs Harmonized Tariff Schedule](https://hts.usitc.gov/)
- [California Prop 65 list](https://oehha.ca.gov/proposition-65)
- [CPSIA — Consumer Product Safety Improvement Act](https://www.cpsc.gov/cpsia)
- [EU REACH regulation](https://echa.europa.eu/regulations/reach/)
