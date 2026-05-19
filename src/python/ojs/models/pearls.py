"""OJS v1.0 — Pearls domain (sub-vertical discriminator).

Pearl-specific grading per CIBJO 7-factor system: type, luster, surface,
nacre, shape, color, overtone, size.

Maps to: GMC product_detail triples under section "Pearl",
        Schema.org additionalProperty array,
        Shopify ojs.pearl metaobject_reference.

REFERENCES:
  - CIBJO Pearl Blue Book (2020 edition)
  - GIA Pearl Description System
  - ISO 18323:2015 — Jewellery — Consumer confidence in the diamond industry
    (analogous principles applied to pearls)

ACTIVATED WHEN: product_type == "pearl" OR any stone has species == "pearl"
REQUIRED IF ACTIVE: pearl_type, luster, shape; others recommended
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class PearlType(str, Enum):
    """Pearl origin type (most economically important attribute)."""

    AKOYA = "akoya"  # Pinctada fucata, Japan/China — classic round, 2-10mm
    SOUTH_SEA = "south_sea"  # Pinctada maxima, Australia/Indonesia/Philippines — 8-20mm
    TAHITIAN = "tahitian"  # Pinctada margaritifera, French Polynesia — naturally dark
    FRESHWATER = "freshwater"  # Hyriopsis cumingi, China — wide variety
    SEA_OF_CORTEZ = "sea_of_cortez"  # Pteria sterna, Mexico — rare
    NATURAL = "natural"  # non-cultured (historic/heirloom only)
    KESHI = "keshi"  # by-product, no nucleus, all nacre
    MABE = "mabe"  # half-pearl on shell
    IMITATION = "imitation"  # man-made (glass, plastic) — must be disclosed
    OTHER = "other"


class PearlLuster(str, Enum):
    """CIBJO/GIA luster grades — how surface reflects light."""

    EXCELLENT = "excellent"  # AAA — bright, sharp, mirror-like
    VERY_GOOD = "very_good"
    GOOD = "good"  # AA — bright with some softness
    FAIR = "fair"  # A — softer reflections
    POOR = "poor"  # dull, milky


class PearlSurface(str, Enum):
    """Surface cleanliness — abundance of blemishes."""

    CLEAN = "clean"  # AAA — no visible blemishes
    LIGHTLY_BLEMISHED = "lightly_blemished"  # AA — minor surface characteristics
    MODERATELY_BLEMISHED = "moderately_blemished"  # A — noticeable blemishes
    HEAVILY_BLEMISHED = "heavily_blemished"  # for low grades


class PearlShape(str, Enum):
    """CIBJO 7-shape classification."""

    ROUND = "round"  # most valued, deviation <2% diameter
    NEAR_ROUND = "near_round"  # deviation 2-5%
    OVAL = "oval"
    BUTTON = "button"
    DROP = "drop"  # teardrop
    SEMI_BAROQUE = "semi_baroque"
    BAROQUE = "baroque"  # irregular
    CIRCLE = "circle"  # with concentric rings
    KESHI = "keshi"
    OTHER = "other"


class PearlBodyColor(str, Enum):
    """Primary body color (hue of the pearl itself)."""

    WHITE = "white"
    CREAM = "cream"
    GOLD = "gold"  # South Sea gold
    SILVER = "silver"
    PEACH = "peach"
    PINK = "pink"
    LAVENDER = "lavender"
    BLACK = "black"  # Tahitian
    GREY = "grey"
    GREEN = "green"
    BLUE = "blue"
    AUBERGINE = "aubergine"  # Tahitian
    MULTICOLOR = "multicolor"
    OTHER = "other"


class PearlOvertone(str, Enum):
    """Secondary translucent color overlaid on body color."""

    NONE = "none"
    ROSE = "rose"  # adds value to white pearls
    SILVER = "silver"
    GREEN = "green"
    BLUE = "blue"
    PEACOCK = "peacock"  # Tahitian highly valued
    PINK = "pink"
    AUBERGINE = "aubergine"
    OTHER = "other"


class NacreQuality(str, Enum):
    """Nacre thickness assessment."""

    THICK = "thick"  # >0.5mm typically — durable
    ACCEPTABLE = "acceptable"  # 0.35-0.5mm
    THIN = "thin"  # <0.35mm — may show nucleus
    UNKNOWN = "unknown"


class PearlMatchingGrade(str, Enum):
    """For strands and multi-pearl pieces — how well pearls match."""

    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    SINGLE_PEARL = "single_pearl"  # not applicable


class PearlsModule(OJSBaseModel):
    """CIBJO 7-factor pearl grading.

    Activated when product_type='pearl' or stones contain pearl species.
    Many fields have AAA/AA/A market shorthand mapped to the more
    descriptive CIBJO enum values above.
    """

    pearl_type: PearlType = Field(description="Pearl species/origin type")
    luster: PearlLuster = Field(description="Surface luster grade")
    surface_quality: PearlSurface = Field(description="Surface cleanliness grade")
    shape: PearlShape = Field(description="Shape classification")
    body_color: PearlBodyColor = Field(description="Primary body color")
    overtone: Optional[PearlOvertone] = Field(
        default=None, description="Secondary overtone color"
    )
    nacre_quality: Optional[NacreQuality] = Field(
        default=None, description="Nacre thickness assessment"
    )
    nacre_thickness_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Measured nacre thickness if known (mm)"
    )
    size_mm: Annotated[float, Field(gt=0)] = Field(
        description="Pearl diameter in mm (use longest axis for non-round)"
    )
    size_range_mm: Optional[Annotated[str, Field(max_length=20)]] = Field(
        default=None,
        description="For strands: range like '7.0-7.5' (mm)",
    )
    pearl_count: int = Field(
        default=1, ge=1, description="Number of pearls in the piece (e.g. strand)"
    )
    matching_grade: Optional[PearlMatchingGrade] = Field(
        default=None,
        description="Matching quality across pearls (strands/multi-pearl pieces)",
    )
    drilling: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Drill type (e.g. 'fully_drilled', 'half_drilled', 'undrilled')",
    )
    treatments: list[Annotated[str, Field(max_length=50)]] = Field(
        default_factory=list,
        description="Disclosed treatments (e.g. 'bleached', 'dyed', 'irradiated', 'pinking')",
    )
