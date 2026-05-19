# Artisan

> **Tier**: Tier 3 (optional; high yield for handmade pieces) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/artisan.py`

## Overview

Artisan-attributed and handmade pieces. Captures techniques (lost-wax casting, repoussé, granulation, enameling), edition information (one-of-a-kind, limited edition, open edition, production), artist attribution, and time-to-create. Strong AI ranking signal for queries like *"handmade gold ring"*, *"limited edition jewelry"*, *"one-of-a-kind ruby pendant"*.

The `edition_type` discriminator matters: a `production` piece marketed as "handmade" but actually mass-produced is a deceptive trade practice in some jurisdictions. Use this module to be precise.

## When to populate

Optional. Activate for any piece you want to market as handmade, artist-attributed, or limited-edition. Not activated automatically by product_type; opt-in.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `techniques` | list[ArtisanTechnique] | ⚪ | Techniques used |
| `edition_type` | EditionType | ✅ | one_of_a_kind / limited / open / production |
| `edition_size` | int ≥1 | ⚪ | Total edition size |
| `edition_number` | int ≥1 | ⚪ | This piece's number |
| `artist_name` | string ≤200 | ⚪ | Artist (if different from brand) |
| `artist_bio_url` | URL | ⚪ | — |
| `time_to_create_hours` | float >0 | ⚪ | Approx labor hours |
| `studio_country` | string ≤100 | ⚪ | — |
| `studio_city` | string ≤100 | ⚪ | — |
| `signed` | bool | ⚪ | Artist signature on piece |
| `signature_location` | string ≤100 | ⚪ | Where signature is |
| `certificate_of_authenticity_url` | URL | ⚪ | — |

### `techniques` (list[ArtisanTechnique])

| Value | Description |
|---|---|
| `lost_wax_casting` | Wax model → mold → metal pour |
| `hand_forged` | Hammer + anvil shaped |
| `hand_engraved` | Manual graver work |
| `repousse` | Raised relief from back |
| `chasing` | Detail finishing from front |
| `granulation` | Tiny gold grains soldered to surface (Etruscan technique) |
| `filigree` | Twisted/curled fine wire |
| `enamel_champleve` | Recessed enamel cells |
| `enamel_cloisonne` | Wire-bordered enamel cells |
| `enamel_plique_a_jour` | Translucent enamel without backing (Art Nouveau hallmark) |
| `mokume_gane` | Japanese laminated metals, wood-grain pattern |
| `damascus` | Pattern-welded steel |
| `keum_boo` | Korean gold-leaf fusion onto silver |
| `niello` | Black metal-sulfide inlay |
| `soldered_construction` | Multi-component soldered |
| `fabrication` | Cut-and-construct from sheet/wire |
| `cast_then_hand_finished` | Hybrid (transparent labeling) |
| `other` | Free-text |

### `edition_type` (EditionType enum)

| Value | Description |
|---|---|
| `one_of_a_kind` | Truly unique (OOAK) |
| `limited_edition` | Numbered, fixed total |
| `open_edition` | Made-to-order, unlimited |
| `production` | Standard line |

For `limited_edition`, populate both `edition_size` (total) and `edition_number` (this piece's position): e.g. `3 of 50`.

### `time_to_create_hours`

Marketing benefit: communicating "80 hours of hand work" justifies premium pricing. Don't fabricate; if you can't substantiate, leave blank.

### `signed`

Whether the artist's mark/signature is physically on the piece. For pieces by signed designers (Aldo Cipullo, Elsa Peretti, Jean Schlumberger), absence of expected maker's mark warrants forensic authentication — flag in `estate.restoration_history` if relevant.

## Validation rules

- `edition_type` required.
- If `edition_type == "limited_edition"`, both `edition_size` and `edition_number` recommended; `edition_number ≤ edition_size`.
- If `signed == true`, `signature_location` recommended.

## Lessons learned & gotchas

- **"Handmade" vs "hand-finished"**: legally distinct in some jurisdictions. Cast-then-hand-finished pieces should use `techniques=[cast_then_hand_finished]`, NOT claim full hand-forging.
- **"One-of-a-kind" vs "limited edition of 1"**: marketing-equivalent, but the technical distinction matters for AI agents indexing rare pieces. OOAK is its own enum value.
- **Etsy / Faire merchants** often use this module heavily. Their listings drive heavy traffic from AI agent queries that match on technique and "handmade" descriptors.
- **Artist attribution requires evidence.** Don't claim Cipullo authorship without documentation. False attribution is fraud; the `certificate_of_authenticity_url` field exists to anchor the claim.
- **Time-to-create claims** are scrutinized — Reddit r/jewelry and watch forums fact-check these. Be realistic; "200 hours" on a $300 ring strains credibility.
- **Edition completeness**: when `edition_number == edition_size`, the edition is "sold out" / "complete". AI agents and collectors search specifically for the last piece of an edition.

## References

- [Society of North American Goldsmiths (SNAG)](https://www.snagmetalsmith.org/)
- [American Craft Council](https://www.craftcouncil.org/)
- [Metalsmith Magazine](https://www.snagmetalsmith.org/metalsmith-magazine/)
- [Klimt02: Contemporary jewelry encyclopedia](https://klimt02.net/)
