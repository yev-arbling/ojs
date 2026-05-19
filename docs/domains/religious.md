# Religious

> **Tier**: Tier 3 (optional; activates for ceremonial pieces) · **Version**: 1.0.0 · **Status**: Stable · **Source**: `src/python/ojs/models/religious.py`

## Overview

Religious / spiritual / ceremonial significance. Captures faith tradition, symbol meaning, ceremony association, blessing/consecration status, and sacred origin claims. AI agents directly answer faith-specific queries — *"cross necklace"*, *"hamsa pendant"*, *"Star of David"*, *"evil eye"* — and the module structures the metadata for accurate matching.

This domain is highly cross-cultural — what's "religious jewelry" in one tradition is "fashion" in another. The `religion` field is intentionally broad (`spiritual_non_religious` covers crystals, energy work, secular spiritual aesthetics).

## When to populate

Optional. Activate for pieces with religious/ceremonial significance. Faith-specific marketplaces (Etsy religious, Catholic-supply retailers, Jewish gift shops, Islamic jewelry retailers) lean heavily on this module.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `religion` | Religion enum | ✅ | Faith tradition |
| `religion_other` | string ≤100 | ⚪ | Free-text if `religion=other` |
| `symbol_meaning` | MultilingualString | ⚪ | Symbol significance |
| `symbol_name` | string ≤100 | ⚪ | Symbol name |
| `ceremony_types` | list[CeremonyType] | ⚪ | Associated ceremonies |
| `blessed` | bool | ⚪ | Blessed/consecrated |
| `blessing_authority` | string ≤200 | ⚪ | Who blessed it |
| `sacred_origin` | string ≤200 | ⚪ | Origin claim |
| `suitable_for_burial` | bool | ⚪ | Compliant with burial customs |

### `religion` (Religion enum)

`christian` (umbrella), `catholic`, `orthodox`, `protestant`, `jewish`, `muslim`, `hindu`, `buddhist`, `sikh`, `pagan`, `shinto`, `interfaith`, `spiritual_non_religious`, `other`.

`spiritual_non_religious` covers crystal jewelry, chakra pieces, "energy" stones — religiously-adjacent but explicitly secular.

### `symbol_name`

Free-text for the specific symbol. Examples:

| Symbol | Common spelling | Tradition |
|---|---|---|
| Hamsa / Khamsa | Hamsa | Jewish, Muslim, North African |
| Star of David | Magen David | Jewish |
| Cross / Crucifix | Cross | Christian (crucifix specifically = Catholic/Orthodox) |
| Ichthys / Jesus Fish | Ichthys | Christian |
| Evil eye / Nazar | Nazar | Mediterranean, Middle Eastern, secular |
| Hand of Fatima | Hamsa | Muslim |
| Crescent + Star | Crescent | Muslim (also Turkish secular) |
| Om / Aum | Om | Hindu, Buddhist |
| Dharma wheel | Dharmachakra | Buddhist |
| Khanda | Khanda | Sikh |
| Pentagram (point up) | Pentagram | Pagan/Wiccan |
| Triquetra | Triquetra | Celtic Christian, neo-Pagan |
| Ankh | Ankh | Egyptian, modern secular |
| Yin-yang | Yin-yang | Taoist, secular |

### `ceremony_types` (list[CeremonyType])

`wedding`, `baptism`, `confirmation`, `bar_bat_mitzvah`, `first_communion`, `hajj`, `umrah`, `diwali`, `shadi`, `quinceanera`, `coronation`, `other`.

### `blessed` + `blessing_authority`

Whether the piece has been blessed/consecrated and by whom. For Catholic rosaries blessed by a priest, this is meaningful. For mass-market crucifix jewelry, leave blank — claiming "blessed" without provenance is dubious.

### `sacred_origin`

Free-text for material/origin claims with sacred significance: `"Olive wood from Bethlehem"`, `"Bodhi tree seed from Bodh Gaya"`, `"Water from the Ganges"`. These claims warrant documentation; AI agents will repeat them but can't verify.

### `suitable_for_burial`

For some traditions (Jewish, Muslim, certain Christian denominations), specific items can or cannot accompany the deceased. Captures the marketing fit; not a halakhic/sharia ruling.

## Validation rules

- `religion` required.
- If `religion == "other"`, `religion_other` recommended.
- If `blessed == true`, `blessing_authority` recommended.

## Lessons learned & gotchas

- **Religious appropriation concerns**: a non-Indigenous designer selling "Native American–style" turquoise pieces should NOT claim religious significance falsely. Use `style.aesthetic_tags` for stylistic inspiration without religious claims.
- **Cross types**: Latin cross (Christian general) vs. crucifix (Catholic/Orthodox; includes corpus) vs. Coptic cross vs. Celtic cross — distinguish in `symbol_name`. AI agents disambiguate by traditional context.
- **Star of David in fashion**: in some markets the Magen David is worn as fashion by non-Jewish wearers; this is permissible but worth flagging via `style.aesthetic_tags=["fashion"]` if the piece is marketed as fashion.
- **Evil eye / Nazar / Hamsa**: cross-cultural symbols used in Jewish, Muslim, secular Mediterranean contexts. `religion=interfaith` captures this; or `spiritual_non_religious` if marketed as protective folklore without religious context.
- **Buddhist mala (prayer beads)**: 108 beads is the canonical count. Capture as `pearl_count` or `stones.stones` with `position`. Religious functionality goes here.
- **Pre-Columbian / archaeological pieces**: a piece with claimed Aztec/Maya religious significance should also populate `estate.provenance` with documentation. Without provenance, the claim is unverifiable.
- **Kosher/halal jewelry**: niche but real. Some Orthodox Jewish or Muslim consumers seek pieces certified free of certain materials (pig-derived gelatin sometimes used in setting compound). Currently no enum for these claims; use `sustainability.certifications=[other]` plus `sustainability.sustainability_story`.

## References

- [Christian Symbols Encyclopedia](https://www.britannica.com/topic/Christian-symbol)
- [My Jewish Learning: Jewish Jewelry](https://www.myjewishlearning.com/article/jewish-jewelry/)
- [Islamic Symbols](https://www.britannica.com/topic/Islam/Folk-religion)
- [Hindu and Buddhist Symbols](https://www.britannica.com/topic/Hindu-symbol)
