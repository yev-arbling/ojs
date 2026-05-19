"""OJS v1.0 — Body jewelry domain (sub-vertical discriminator).

Activated when product_type == "body". Piercing jewelry has unique
material safety requirements due to long-term skin/mucosa contact.

CRITICAL REFERENCES (FROM PROMPT 4 RESEARCH):
  - ASTM F138 — Stainless steel for surgical implants
  - ASTM F136 — Ti-6Al-4V titanium alloy for surgical implants
  - ASTM F1295 — Ti-6Al-7Nb ALLOY (NOT pure niobium — common error in catalogs)
  - ASTM B392-18 — Standard Specification for Niobium and Niobium Alloys
    (use for unalloyed niobium body jewelry)
  - APP (Association of Professional Piercers) Minimum Standards
  - ISO 5832 — Implants for surgery — Metallic materials

For initial piercings only ASTM F138/F136/F1295/B392 + 14k+/18k+ gold
and platinum are typically considered safe per APP standards.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class PiercingLocation(str, Enum):
    """Piercing site."""

    EAR_LOBE = "ear_lobe"
    EAR_HELIX = "ear_helix"
    EAR_TRAGUS = "ear_tragus"
    EAR_DAITH = "ear_daith"
    EAR_ROOK = "ear_rook"
    EAR_CONCH = "ear_conch"
    EAR_INDUSTRIAL = "ear_industrial"
    NOSE_NOSTRIL = "nose_nostril"
    NOSE_SEPTUM = "nose_septum"
    NOSE_BRIDGE = "nose_bridge"
    EYEBROW = "eyebrow"
    LIP_LABRET = "lip_labret"
    LIP_MONROE = "lip_monroe"
    LIP_MEDUSA = "lip_medusa"
    TONGUE = "tongue"
    NAVEL = "navel"
    NIPPLE = "nipple"
    SURFACE = "surface"
    DERMAL = "dermal"  # microdermal anchor
    GENITAL = "genital"
    OTHER = "other"


class BiocompatibilityStandard(str, Enum):
    """Material safety standards for body jewelry."""

    ASTM_F138 = "astm_f138"  # 316LVM surgical stainless steel
    ASTM_F136 = "astm_f136"  # Ti-6Al-4V titanium
    ASTM_F1295 = "astm_f1295"  # Ti-6Al-7Nb alloy (NOT pure niobium)
    ASTM_B392_18 = "astm_b392_18"  # unalloyed niobium
    ISO_5832_2 = "iso_5832_2"  # unalloyed titanium
    ISO_5832_3 = "iso_5832_3"  # wrought titanium 6-aluminum 4-vanadium
    GOLD_14K_PLUS = "gold_14k_plus"  # ≥14k yellow/white/rose
    GOLD_18K_PLUS = "gold_18k_plus"
    PLATINUM_950 = "platinum_950"
    GLASS_BOROSILICATE = "glass_borosilicate"  # solid glass, no leaching
    NONE_DISCLOSED = "none_disclosed"


class ThreadingType(str, Enum):
    """How the jewelry attaches together."""

    INTERNALLY_THREADED = "internally_threaded"  # threading inside the bar — preferred for new piercings
    EXTERNALLY_THREADED = "externally_threaded"  # threading on the bar — cheaper but rougher on tissue
    THREADLESS = "threadless"  # press-fit
    HINGED = "hinged"  # hinged segment ring
    CAPTIVE_BEAD = "captive_bead"  # bead held by ring tension
    SEAMLESS = "seamless"
    SEGMENT = "segment"
    PUSH_PIN = "push_pin"
    OTHER = "other"


class GaugeMeasurement(OJSBaseModel):
    """Body jewelry gauge — wire/bar thickness.

    Gauge is INVERSE: lower number = thicker. 20g (0.8mm) is thinnest
    common; 00g (~10mm) is thickest standard for stretched piercings.
    """

    gauge_us: Optional[Annotated[str, Field(max_length=5)]] = Field(
        default=None,
        description="US wire gauge (e.g. '20g', '18g', '16g', '14g', '12g', '10g', '8g', '6g', '4g', '2g', '0g', '00g')",
    )
    diameter_mm: Optional[Annotated[float, Field(gt=0, le=50)]] = Field(
        default=None, description="Bar/wire diameter in mm"
    )


class BodyModule(OJSBaseModel):
    """Body jewelry specifications.

    Required when product_type='body'. Material disclosure is critical
    for first-piercing/healing safety.
    """

    piercing_location: PiercingLocation = Field(description="Intended piercing site")
    suitable_for_initial_piercing: Optional[bool] = Field(
        default=None,
        description="Material/design suitable for fresh piercings per APP standards",
    )
    biocompatibility_standards: list[BiocompatibilityStandard] = Field(
        default_factory=list,
        description="Material safety standards this piece meets (multi-valued)",
    )
    gauge: Optional[GaugeMeasurement] = None
    bar_length_mm: Optional[Annotated[float, Field(gt=0, le=50)]] = Field(
        default=None, description="Bar length / post length / ring inner diameter (mm)"
    )
    threading_type: Optional[ThreadingType] = None
    end_size_mm: Optional[Annotated[float, Field(gt=0, le=30)]] = Field(
        default=None, description="Decorative end (ball, gem, charm) diameter (mm)"
    )
    nickel_free_certified: Optional[bool] = Field(
        default=None,
        description="EU Nickel Directive 94/27/EC compliant — critical for piercings",
    )
    autoclave_safe: Optional[bool] = Field(
        default=None, description="Can be sterilized by steam autoclave"
    )
