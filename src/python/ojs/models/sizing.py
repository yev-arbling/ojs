"""OJS v1.0 — Sizing domain.

Physical dimensions: ring sizes (ISO 8653 + regional conversions),
chain/bracelet length, earring drop, brooch dimensions.

REFERENCES:
  - ISO 8653:2016 — Jewellery — Ring sizes — Definition, measurement and designation
  - ISO 9202:2019 — Jewellery — Fineness of precious metal alloys
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class SizeSystem(str, Enum):
    """Ring size designation systems."""

    ISO = "iso"  # ISO 8653:2016 — inner circumference in mm
    US_CA = "us_ca"  # USA/Canada numeric (e.g. 6, 6.5, 7)
    UK_AU = "uk_au"  # UK/Australia/Ireland alphabetic (e.g. M, N)
    EU = "eu"  # France/Spain (inner circumference in mm, ~equal to ISO)
    DE = "de"  # Germany (inner circumference in mm, fractional)
    JP_CN = "jp_cn"  # Japan/China numeric (e.g. 13)
    IT = "it"  # Italy (Italian numeric)
    BR = "br"  # Brazil
    OTHER = "other"


class JewelryClosure(str, Enum):
    """For necklaces, bracelets, earrings — closure mechanism."""

    LOBSTER_CLAW = "lobster_claw"
    SPRING_RING = "spring_ring"
    BOX_CLASP = "box_clasp"
    TOGGLE = "toggle"
    MAGNETIC = "magnetic"
    SCREW = "screw"
    HOOK = "hook"
    BARREL = "barrel"
    SLIDE = "slide"
    PUSH_BACK = "push_back"  # earrings
    LEVER_BACK = "lever_back"  # earrings
    OMEGA_BACK = "omega_back"  # earrings
    SCREW_BACK = "screw_back"  # earrings
    FRENCH_WIRE = "french_wire"  # earrings
    CLIP_ON = "clip_on"  # non-pierced earrings
    OTHER = "other"


class RingSize(OJSBaseModel):
    """A ring size measurement in multiple equivalent systems.

    ISO inner circumference is canonical; other systems derived.
    Example: US 7 ≈ ISO 54 ≈ UK N ≈ EU 54.
    """

    iso_mm: Optional[Annotated[float, Field(gt=0, le=100)]] = Field(
        default=None,
        description="ISO 8653 inner circumference in mm (canonical)",
    )
    us_ca: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="US/Canada numeric size (e.g. 7.0)"
    )
    uk_au: Optional[Annotated[str, Field(max_length=5)]] = Field(
        default=None, description="UK/Australia alphabetic size (e.g. 'N', 'N1/2')"
    )
    eu: Optional[Annotated[float, Field(gt=0)]] = Field(default=None)
    de: Optional[Annotated[float, Field(gt=0)]] = Field(default=None)
    jp_cn: Optional[Annotated[int, Field(gt=0)]] = Field(default=None)
    it: Optional[Annotated[int, Field(gt=0)]] = Field(default=None)
    inner_diameter_mm: Optional[Annotated[float, Field(gt=0, le=30)]] = Field(
        default=None, description="Inner diameter (alternative to circumference)"
    )


class SizingModule(OJSBaseModel):
    """Physical dimensions of the piece. Fields used depend on product_type."""

    # Ring sizing
    ring_size: Optional[RingSize] = Field(
        default=None, description="Ring size (rings only)"
    )
    ring_width_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Band width across finger (mm)"
    )
    ring_resizable: Optional[bool] = Field(
        default=None, description="Whether ring can be resized professionally"
    )

    # Chain/strand length (necklaces, bracelets, anklets)
    length_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Total length in mm"
    )
    adjustable_to_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None,
        description="If adjustable, maximum length reached (mm)",
    )
    chain_width_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Chain/strand thickness (mm)"
    )

    # Pendant / drop
    drop_length_mm: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Length below clasp/post (mm) for pendants/earrings"
    )
    pendant_width_mm: Optional[Annotated[float, Field(gt=0)]] = None
    pendant_height_mm: Optional[Annotated[float, Field(gt=0)]] = None

    # Earring
    earring_drop_mm: Optional[Annotated[float, Field(gt=0)]] = None
    earring_width_mm: Optional[Annotated[float, Field(gt=0)]] = None

    # Brooch / pin
    brooch_width_mm: Optional[Annotated[float, Field(gt=0)]] = None
    brooch_height_mm: Optional[Annotated[float, Field(gt=0)]] = None

    # Closure (most non-ring items)
    closure: Optional[JewelryClosure] = Field(default=None, description="Closure mechanism")

    # Total weight
    total_weight_grams: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Total weight of the finished piece (g)"
    )
