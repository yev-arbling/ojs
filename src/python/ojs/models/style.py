"""OJS v1.0 — Style domain.

Aesthetic and design classification: era, design style, motif, aesthetic tags.
Used heavily for AI agent query matching ('vintage art deco', 'modern minimalist').
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class Era(str, Enum):
    """Historical periods. Estate/antique jewelry critical for AI search.

    Boundaries are conventional, not absolute. Confidence often <0.80
    from CV — recommend human validation.
    """

    GEORGIAN = "georgian"  # 1714-1837
    EARLY_VICTORIAN = "early_victorian"  # 1837-1860
    MID_VICTORIAN = "mid_victorian"  # 1860-1885
    LATE_VICTORIAN = "late_victorian"  # 1885-1901
    EDWARDIAN = "edwardian"  # 1901-1915
    ART_NOUVEAU = "art_nouveau"  # 1890-1910
    ART_DECO = "art_deco"  # 1920-1935
    RETRO = "retro"  # 1935-1950
    MID_CENTURY = "mid_century"  # 1950-1970
    MODERNIST = "modernist"  # 1960-1980
    CONTEMPORARY = "contemporary"  # 1980-present
    UNKNOWN = "unknown"


class DesignStyle(str, Enum):
    """Design style tags. Multi-valued in StyleModule."""

    MINIMALIST = "minimalist"
    MAXIMALIST = "maximalist"
    CLASSIC = "classic"
    VINTAGE_INSPIRED = "vintage_inspired"
    BOHO = "boho"
    GOTHIC = "gothic"
    INDUSTRIAL = "industrial"
    NATURE_INSPIRED = "nature_inspired"
    GEOMETRIC = "geometric"
    ABSTRACT = "abstract"
    FIGURATIVE = "figurative"
    ETHNIC = "ethnic"
    TRIBAL = "tribal"
    ROMANTIC = "romantic"
    EDGY = "edgy"
    UNISEX = "unisex"
    FEMININE = "feminine"
    MASCULINE = "masculine"
    OTHER = "other"


class Motif(str, Enum):
    """Recurring decorative motifs (multi-valued)."""

    FLORAL = "floral"
    LEAF = "leaf"
    ANIMAL = "animal"
    BUTTERFLY = "butterfly"
    BIRD = "bird"
    SNAKE = "snake"
    HEART = "heart"
    STAR = "star"
    MOON = "moon"
    SUN = "sun"
    CELESTIAL = "celestial"
    CROSS = "cross"
    KNOT = "knot"
    INFINITY = "infinity"
    BOW = "bow"
    GEOMETRIC = "geometric"
    SCROLL = "scroll"
    FILIGREE = "filigree"
    MILGRAIN = "milgrain"
    OTHER = "other"


class StyleModule(OJSBaseModel):
    """Aesthetic and design tags. Multi-valued by design — pieces can
    have multiple styles and motifs."""

    era: Optional[Era] = Field(default=None, description="Historical period")
    design_styles: list[DesignStyle] = Field(
        default_factory=list, description="Design style tags (multi-valued)"
    )
    motifs: list[Motif] = Field(default_factory=list, description="Decorative motifs")
    aesthetic_tags: list[Annotated[str, Field(max_length=50)]] = Field(
        default_factory=list,
        max_length=20,
        description="Free-text aesthetic descriptors for AI search (e.g. 'cottagecore', 'old-money')",
    )
