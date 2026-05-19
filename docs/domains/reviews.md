# Reviews

> **Tier**: Tier 2 (strongly recommended) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/reviews.py`

## Overview

Aggregate review data + optional individual reviews + Q&A pairs. **STRONG conversion + AI ranking signal** — every primary-source AI commerce spec (ACP, GMC) supports aggregate rating. Schema.org `AggregateRating` is the universal mapping.

**Optimal rating band** per Northwestern Spiegel Research Center 2017 (20M+ product pages with PowerReviews): purchase likelihood peaks at 4.0–4.7 stars; 5.0-star products underperform 4.75–4.99 due to consumer suspicion. **Authentic mid-band ratings outperform perfect ones.** Don't shame retailers for honest <5.0 averages.

## When to populate

Strongly recommended for any product with review history. If you have zero reviews, omit the module — don't fake aggregate data.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `aggregate` | AggregateRating | 🟡 | Summary stats |
| `reviews` | list[Review] (≤20) | ⚪ | Individual reviews |
| `qa_questions` | list[string ≤500] | ⚪ | Customer questions |
| `qa_answers` | list[string ≤2000] | ⚪ | Corresponding answers |

### `AggregateRating` (object)

| Field | Type | Required | Description |
|---|---|---|---|
| `rating_value` | float 0–5 | ✅ | Average rating |
| `review_count` | int ≥0 | ✅ | Number of reviews |
| `best_rating` | float | (default 5.0) | Max rating |
| `worst_rating` | float | (default 1.0) | Min rating |

### `Review` (per-entry fields)

| Field | Type | Required | Description |
|---|---|---|---|
| `rating` | float 0–5 | ✅ | Star rating |
| `author_name` | string ≤100 | ⚪ | Reviewer name |
| `verified_purchase` | bool | ⚪ | Verified buyer |
| `title` | string ≤200 | ⚪ | Review title |
| `body` | string ≤5000 | ⚪ | Review text |
| `review_date` | date | ⚪ | When reviewed |
| `review_url` | URL | ⚪ | Permalink |
| `helpful_votes` | int ≥0 | ⚪ | Helpfulness count |

### `qa_questions` / `qa_answers`

Customer questions and merchant/community answers. **Same-index pairing** between the two lists. Used by ACP's `q_and_a` field — ChatGPT surfaces these in shopping flows.

Example:
```python
qa_questions = ["Is this ring resizable?", "Does it come with the certificate?"]
qa_answers = [
    "Yes, ½ size up or down at no extra cost.",
    "Yes, GIA report #2199999999 included; full report PDF on the product page."
]
```

## Validation rules

- `aggregate.rating_value` must be in `[worst_rating, best_rating]`.
- `aggregate.review_count ≥ 0`.
- `qa_questions` and `qa_answers` lists must be **same length** (paired by index).
- `reviews` cap at 20 entries — for products with hundreds of reviews, send aggregates only and link out via `review_url`.

## Lessons learned & gotchas

- **Don't fabricate reviews.** FTC 16 CFR Part 465 (Final Rule on Fake Reviews, effective October 2024) prohibits fake reviews and review suppression. Penalties up to $51,744 per violation. AI agents are not in a position to detect fakes, but regulators and aggregator platforms (Trustpilot, Bazaarvoice) are.
- **The "4.0–4.7 is optimal" insight is counterintuitive.** When ALL of your products show 5.0, consumers suspect manipulation. A few authentic 3-star reviews on a 4.6-average product look more trustworthy than a 5.0-uniform catalog.
- **Verified purchase flag is gold.** ACP, GMC, and most AI agents weight verified reviews higher. Set explicitly when known.
- **Q&A length matters.** ACP `q_and_a` cap is ~2000 chars per answer. Don't write essays; aim for 1–3 sentences. AI agents will quote these directly to shoppers.
- **Localized reviews**: this module captures English reviews as primary. Multi-locale review data (Yotpo, BV, Trustpilot localized) doesn't fit the simple schema cleanly — consider OJS extension `x_reviews_localized` for v1.1.
- **Aggregate rounding**: don't round `rating_value` to 1 decimal place before storage. Store `4.673` and let display layers round. Aggregate calculations on rounded values compound error.
- **`review_count` includes ratings without text.** A "stars-only" rating still counts. Don't artificially suppress count to inflate average.

## References

- [Schema.org/AggregateRating](https://schema.org/AggregateRating)
- [Northwestern Spiegel Research Center: How Online Reviews Influence Sales (2017)](https://spiegel.medill.northwestern.edu/online-reviews/)
- [FTC 16 CFR Part 465 — Final Rule on Fake Reviews (2024)](https://www.ftc.gov/legal-library/browse/rules/rule-consumer-reviews-testimonials)
- [Google rich result requirements — Reviews](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)
