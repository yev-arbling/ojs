"""OJS v1.0 — Metals domain.

Precious metal composition: type, purity (fineness), color, finish, plating.
Maps to: Schema.org material, GMC material + product_detail triples,
        ACP material, Shopify metafield ojs.metal (json) + metaobject_reference.

REFERENCES:
  - ISO 9202:2019 — Jewellery — Fineness of precious metal alloys
  - FTC 16 CFR §23.5 (precious metals) — US disclosure rules
  - UK Hallmarking Act 1973 — required hallmarks
  - ASTM B392-18 — Standard Specification for Niobium and Niobium Alloys

REQUIRED if metal-bearing: primary_metal (type + purity)
RECOMMENDED: color, finish, additional_metals (for two-tone pieces)
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class MetalType(str, Enum):
    """Base metal types per ISO 9202:2019.

    Codes correspond to common jewelry trade conventions. For non-precious
    or surgical metals (steel, titanium), use the appropriate enum.
    """

    GOLD = "gold"
    SILVER = "silver"
    PLATINUM = "platinum"
    PALLADIUM = "palladium"
    RHODIUM = "rhodium"
    TITANIUM = "titanium"  # ASTM F136 / F1295 (Ti-6Al-7Nb) for body jewelry
    NIOBIUM = "niobium"  # ASTM B392-18 unalloyed niobium
    STEEL = "steel"  # Stainless 304/316L for fashion/body jewelry
    TUNGSTEN = "tungsten"
    BRASS = "brass"
    BRONZE = "bronze"
    COPPER = "copper"
    OTHER = "other"


class MetalColor(str, Enum):
    """Visible metal color. Note: 'rose'/'yellow'/'white' refer to gold variants."""

    YELLOW = "yellow"
    WHITE = "white"
    ROSE = "rose"
    GREEN = "green"  # green gold (Au+Ag alloy)
    BLACK = "black"  # rhodium-plated or oxidized
    NATURAL = "natural"  # silver, platinum default
    TWO_TONE = "two_tone"  # mixed in same piece
    TRI_COLOR = "tri_color"


class MetalFinish(str, Enum):
    """Surface finish."""

    POLISHED = "polished"
    MATTE = "matte"
    BRUSHED = "brushed"
    SATIN = "satin"
    HAMMERED = "hammered"
    SANDBLASTED = "sandblasted"
    OXIDIZED = "oxidized"
    MILGRAIN = "milgrain"
    ENGRAVED = "engraved"
    FLORENTINE = "florentine"


class PlatingType(str, Enum):
    """Surface plating applied over a base metal."""

    NONE = "none"
    GOLD_PLATED = "gold_plated"  # generic gold plating
    GOLD_FILLED = "gold_filled"  # mechanically bonded, thicker layer
    GOLD_VERMEIL = "vermeil"  # ≥10k gold over sterling, ≥2.5 µm per FTC 16 CFR §23.5
    RHODIUM_PLATED = "rhodium_plated"  # common over white gold or silver
    SILVER_PLATED = "silver_plated"
    PLATINUM_PLATED = "platinum_plated"
    BLACK_RHODIUM = "black_rhodium"
    ROSE_GOLD_PLATED = "rose_gold_plated"


class MetalComposition(OJSBaseModel):
    """A single metal component of the piece.

    For multi-metal pieces (two-tone rings, etc.), include one
    MetalComposition per distinct metal. Mark `primary=True` on the
    dominant one (used for short-form syndication like Schema.org material).
    """

    type: MetalType = Field(description="Base metal type")
    purity_fineness: Optional[Annotated[int, Field(ge=1, le=999)]] = Field(
        default=None,
        description=(
            "Parts per 1000 (fineness). Examples: gold 24k=999, 18k=750, 14k=585, "
            "10k=417; silver sterling=925, Britannia=958; platinum=950."
        ),
    )
    purity_karat: Optional[Annotated[float, Field(ge=0, le=24)]] = Field(
        default=None,
        description="Karat for gold only (10/14/18/22/24). Auto-derivable from fineness.",
    )
    color: Optional[MetalColor] = Field(default=None, description="Visible color")
    finish: Optional[MetalFinish] = Field(default=None, description="Surface finish")
    plating: Optional[PlatingType] = Field(default=None, description="Plating type if any")
    plating_thickness_microns: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None,
        description="Plating thickness in µm (UN/CEFACT code '4H'). Vermeil requires ≥2.5 µm.",
    )
    weight_grams: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Weight of this metal component in grams"
    )
    primary: bool = Field(
        default=False,
        description="Whether this is the primary/dominant metal (one per product)",
    )
    hallmark: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Stamped hallmark (e.g. '750', 'PT950', 'STERLING')",
    )


class MetalsModule(OJSBaseModel):
    """All metal information for a jewelry piece.

    REQUIRED for metal-bearing products. Skip for pure-pearl or pure-gem
    items where metal is incidental (e.g. pearl on silk cord).
    """

    compositions: list[MetalComposition] = Field(
        min_length=1,
        description="One per distinct metal. Mark one with primary=True.",
    )
    total_metal_weight_grams: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None,
        description="Sum of metal weight across all compositions",
    )
    nickel_free: Optional[bool] = Field(
        default=None,
        description="Compliant with EU Nickel Directive 94/27/EC for prolonged skin contact",
    )
    hypoallergenic_certified: Optional[bool] = Field(
        default=None,
        description="Manufacturer claims hypoallergenic; verify with ASTM F2999 / EN 1811",
    )
    conflict_free: Optional[bool] = Field(
        default=None,
        description="Compliant with OECD conflict-free sourcing for gold",
    )
    recycled_content_percent: Optional[Annotated[float, Field(ge=0, le=100)]] = Field(
        default=None,
        description="Percent recycled metal content (0-100). Audit chain required for claim.",
    )
