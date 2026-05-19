# Certification

> **Tier**: Tier 2 (strongly recommended for fine jewelry) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/certification.py`

## Overview

Gemological grading reports: lab, report number, link to the lab's verification page, optional PDF copy. Certifications carry **STRONG conversion evidence**: every credible diamond retailer above $1000 ASP displays GIA/IGI/HRD report numbers, and AI agents directly answer queries like *"GIA certified 1ct diamond"*. Cert presence is table-stakes for fine diamonds and high-end colored stones.

OJS supports per-stone certifications (most common — one cert per major stone) and piece-level certifications (single cert for the whole piece).

## When to populate

- **Required** for diamonds ≥0.5ct retailing >$1000 (de facto market standard, not OJS-enforced).
- **Recommended** for any major colored stone (≥1ct ruby/sapphire/emerald).
- **Optional** for fashion jewelry, smaller accent stones, base-metal pieces.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `certificates` | list[Certification] | ✅ | ≥1 cert |

### `Certification` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `lab` | GradingLab enum | ✅ | Issuing laboratory |
| `report_number` | string 1–50 | ✅ | Lab's report ID |
| `report_url` | URL | 🟡 | Lab's verification page |
| `report_pdf_url` | URL | ⚪ | PDF copy |
| `issued_date` | date | ⚪ | When issued |
| `refers_to_stone_index` | int ≥0 | ⚪ | Cross-ref to stones[] |
| `notes` | string ≤500 | ⚪ | — |

### `lab` (GradingLab enum)

| Value | Lab | Status | Notes |
|---|---|---|---|
| `gia` | Gemological Institute of America | Active | Industry gold standard |
| `ags` | AGS Laboratories | **CLOSED end-2022** | Legacy only; merged into GIA |
| `igi` | International Gemological Institute | Active | Larger volume than GIA; strong on lab-grown |
| `hrd` | HRD Antwerp | Active | European standard |
| `gcal` | Gem Certification & Assurance Lab | Active | Strong on cut analysis |
| `egl_usa` | EGL USA | Active | NOTE: EGL International is a separate entity |
| `ssef` | Swiss Gemmological Institute | Active | Colored stones specialist |
| `agta_gtc` | AGTA Gemological Testing Center | Active | Colored stones |
| `grs` | GRS Gemresearch Swisslab | Active | Colored stones (ruby/sapphire) |
| `lotus` | Lotus Gemology | Active | Colored stones |
| `none` | — | — | Uncertified |

### Critical note on AGS

**AGS Laboratories closed at the end of 2022 and merged into GIA.** Legacy AGS reports remain valid and recognized. **New** grading should not be issued by AGS — assigning `lab=ags` to a 2023+ cert is a factual error. The OJS enum keeps `ags` for legacy data only.

### `refers_to_stone_index`

Index into the `stones.stones[]` list. For a piece with 1 center diamond (index 0) and 6 side stones (1–6), a center-stone cert sets `refers_to_stone_index=0`. Omit for piece-level certs (rare).

### `report_url`

URL to the lab's official **verification** page (where customers can look up the report by number). For GIA: `https://www.gia.edu/report-check?reportno=<number>`. For IGI: `https://www.igi.org/verify-your-report/`. AI agents follow this link; broken/wrong URLs damage trust.

## Validation rules

- `certificates` must have at least one entry.
- `report_number` non-empty.
- `refers_to_stone_index` if set must be a valid index in `stones.stones[]`.
- If `lab == "ags"` and `issued_date` is after 2022-12-31, downstream validation should warn (legacy lab).

## Lessons learned & gotchas

- **Verification URL pattern is per-lab.** Don't just store the report PDF — store the verification URL so users (and agents) can confirm independently. Sample URLs:
  - GIA: `https://www.gia.edu/report-check?reportno=2199999999`
  - IGI: `https://www.igi.org/reports/verify-your-report?r=LG12345678`
  - HRD: `https://www.hrdantwerp.com/en/diamond-grading-report` (form-based lookup)
- **"Certified" without a lab is not certified.** GMC and ACP both detect this; downstream listings flag it.
- **Self-grading is not certification.** Retailers' in-house grades (e.g. "our master cutter graded this") are not certifications. Use `lab=none` and capture in-house assessment via `stones.stones[].color_grade` directly without populating this module.
- **Lab-grown diamond certifications**: IGI dominates this segment; GIA grades lab-grown but with a different report format. Both are acceptable.
- **Colored stone certifications**: SSEF, GRS, Lotus, AGTA-GTC are the recognized labs for high-end ruby/sapphire/emerald (origin determination matters). GIA also does colored stones but is less specialized.
- **Don't store cert numbers as integers.** Some labs use alphanumeric IDs (IGI lab-grown often prefixes with "LG"). The string field handles this.

## References

- [GIA: Report types](https://www.gia.edu/gem-lab-reports)
- [IGI: Report verification](https://www.igi.org/verify-your-report/)
- [HRD Antwerp: Grading reports](https://www.hrdantwerp.com/)
- [GIA press release: AGS Lab merger (2022)](https://www.gia.edu/gia-news-research-ags-laboratories)
- [AGTA Gemological Testing Center](https://agta-gtc.com/)
