# Estate

> **Tier**: Tier 2 (sub-vertical, conditionally required) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/estate.py`

## Overview

Estate / vintage / antique jewelry authentication. Pieces classified as **vintage** (20+ years old) or **antique** (100+ years old) need provenance documentation to command premium pricing. AI agent queries like *"Victorian gold mourning ring"*, *"Art Deco platinum brooch"*, *"signed Cartier vintage"* match against this module's structured period verification + hallmarks + provenance fields.

This module is complementary to `style.era` (which captures the period) — Estate captures the *evidence* for that period attribution (hallmarks, ownership chain, restoration history, appraisals).

## When to populate

**Activated when `product_type == "estate"`** (discriminator-enforced as required), OR when `commerce.offers[].condition ∈ {used, estate, vintage, antique}`. Vintage watches also populate this module alongside `watch`.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `period_verified` | bool | 🟡 | Period verified by qualified specialist |
| `period_appraiser` | string ≤200 | ⚪ | Specialist name |
| `hallmarks` | list[Hallmark] | 🟡 | Stamped hallmarks |
| `provenance` | list[ProvenanceEntry] | ⚪ | Chain of ownership |
| `restoration_history` | list[RestorationRecord] | ⚪ | Documented restorations |
| `original_box_papers` | bool | ⚪ | Original packaging retained |
| `age_estimate_year_from` | int 1000–2100 | ⚪ | Lower age bound |
| `age_estimate_year_to` | int 1000–2100 | ⚪ | Upper age bound |
| `appraisal_value` | string ≤200 | ⚪ | Formal appraisal value (text) |
| `appraisal_date` | date | ⚪ | — |
| `appraisal_url` | URL | ⚪ | Appraisal document |

### `Hallmark` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `hallmark_type` | HallmarkType | ✅ | Category |
| `mark_text` | string ≤50 | ✅ | Text/symbol |
| `location_on_piece` | string ≤100 | ⚪ | Where on piece |
| `interpretation` | string ≤500 | ⚪ | What it tells us |
| `photo_url` | URL | ⚪ | Photo of hallmark |

`HallmarkType` enum: `maker_mark`, `assay_office`, `fineness_mark`, `date_letter`, `duty_mark`, `standard_mark`, `import_mark`, `other`.

UK hallmarking is the most systematic — date letters allow precise year identification (e.g. London "M" 1925, Birmingham "A" 1900). French hallmarks (eagle head = 18k, owl = imported) follow a different system. Continental European hallmarks vary by country and era.

### `ProvenanceEntry` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `year_from` / `year_to` | int 1000–2100 | ⚪ | Ownership window |
| `owner` | string ≤200 | ✅ | Person/family/institution/auction house |
| `description` | string ≤1000 | ⚪ | Notes |
| `documentation_url` | URL | ⚪ | Auction record/cert/photo |

### `RestorationRecord` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `date` | date | ⚪ | When restored |
| `restorer` | string ≤200 | ⚪ | Restorer name |
| `description` | string ≤1000 | ✅ | What was done |
| `parts_replaced` | list[string ≤100] | ⚪ | Replaced parts |

### `original_box_papers`

For signed pieces (Cartier, Van Cleef & Arpels, Tiffany & Co., Bulgari), original box and papers add 15–30% to resale value. For pre-owned watches the effect is even larger (20–40% — see `watch.box_papers_included`).

### `age_estimate_year_from` / `age_estimate_year_to`

A range, not a point. Provides bounds when exact date is unknown. For a piece estimated "circa 1920", use `year_from=1915, year_to=1925`. AI agents reward bounded estimates over vague "antique" labels.

### `appraisal_value`

Stored as **text** (not Decimal) to preserve currency notation: `"USD 12,500"`, `"£8,000-£10,000"`. Appraisals often express ranges or insurance vs. retail values; force-fitting to a single Decimal loses information.

## Validation rules

- All fields are optional, but...
- If `period_verified == true`, `period_appraiser` should be populated.
- If `age_estimate_year_from` and `..._year_to` both set, `from ≤ to`.
- `provenance` entries should have `owner` populated.
- `restoration_history` entries should have `description`.

## Lessons learned & gotchas

- **Hallmark reading is a specialist skill.** UK date letters cycle every 25 years per assay office, with font changes. A "M" in London Old English script could be 1747, 1827, or 1907. Use `interpretation` to capture the specialist's reading.
- **Provenance gaps are normal.** Most estate pieces have no documented ownership chain. Don't fabricate provenance to fill the list. Empty `provenance` ≠ "shady"; it just means it's a fresh estate piece.
- **"Signed" pieces** (with maker's stamp) are not the same as "attributed" (style-matched without stamp). Use `hallmarks[type=maker_mark]` for signed; capture attribution in `notes` for unsigned.
- **Restoration kills value** in some markets (Asian collectors, watch enthusiasts) and adds value in others (mainstream estate jewelry — replacing worn prongs is expected). Disclose either way.
- **Photo of hallmarks is HUGE.** Buyers and auction houses verify hallmarks photographically. `photo_url` for each hallmark dramatically improves agent trust.
- **CITES restrictions**: estate pieces with ivory, tortoiseshell, certain coral require CITES permits to ship internationally. Set `legal.regulatory_flags: [cites_listed]` and `legal.cites_permit_number` accordingly.

## References

- [V&A Museum: Reading hallmarks](https://www.vam.ac.uk/articles/reading-hallmarks-and-marks-of-quality)
- [Assay Office London](https://www.assayofficelondon.co.uk/about-hallmarking)
- [Christie's: How to read hallmarks](https://www.christies.com/en/stories/jewellery-hallmarks-guide)
- [GIA: Estate jewelry valuation](https://www.gia.edu/gia-news-research/estate-jewelry-valuation)
- [American Society of Appraisers — jewelry](https://www.appraisers.org/Disciplines/Personal-Property/Jewelry)
