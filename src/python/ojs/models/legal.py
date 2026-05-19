"""OJS v1.0 — Legal / regulatory compliance domain.

Customs codes, age restrictions, FTC disclosures, export controls.

REFERENCES (from Prompt 4 research):
  - HS 2022 codes 7101-7117 (Pearls, precious stones, jewelry)
  - FTC 16 CFR Part 23 — Jewelry Guides (revised 2018, §23.5 not 23.4)
  - EU Nickel Directive 94/27/EC
  - California Prop 65 (CCR Title 27)
  - US Conflict Minerals Rule (Dodd-Frank §1502, SEC Form SD)
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class HSCodePrefix(str, Enum):
    """Common HS 2022 codes for jewelry. Use 6-digit subheadings where known."""

    # 7101 — Pearls
    HS_7101 = "7101"  # Pearls, natural or cultured
    HS_710110 = "710110"  # Natural pearls
    HS_710121 = "710121"  # Cultured pearls, unworked
    HS_710122 = "710122"  # Cultured pearls, worked

    # 7102 — Diamonds
    HS_710231 = "710231"  # Diamonds, unsorted, non-industrial
    HS_710239 = "710239"  # Diamonds, non-industrial, otherwise

    # 7103 — Other precious/semi-precious stones
    HS_710310 = "710310"  # Other precious stones, unworked
    HS_710391 = "710391"  # Rubies, sapphires, emeralds — cut
    HS_710399 = "710399"  # Other precious/semi-precious stones — cut

    # 7113 — Articles of jewellery
    HS_711311 = "711311"  # Of silver, whether or not plated
    HS_711319 = "711319"  # Of other precious metal (gold, platinum)
    HS_711320 = "711320"  # Of base metal clad with precious metal

    # 7114 — Articles of goldsmiths'/silversmiths' wares (not jewelry)
    HS_7114 = "7114"

    # 7115 — Other articles of precious metal
    HS_7115 = "7115"

    # 7116 — Articles of pearls/stones
    HS_711610 = "711610"  # Of natural/cultured pearls
    HS_711620 = "711620"  # Of precious/semi-precious stones

    # 7117 — Imitation jewellery
    HS_7117 = "7117"  # Imitation jewellery
    HS_711719 = "711719"  # Of base metal
    HS_711790 = "711790"  # Other (plastic etc.)

    # 9101/9102 — Watches
    HS_9101 = "9101"  # Wrist-watches with precious-metal case
    HS_9102 = "9102"  # Wrist-watches, other

    OTHER = "other"


class RegulatoryFlag(str, Enum):
    """Regulatory and compliance flags."""

    PROP_65_WARNING = "prop_65_warning"  # CA chemical exposure
    NICKEL_DIRECTIVE_COMPLIANT = "nickel_directive_compliant"  # EU 94/27/EC
    CPSIA_COMPLIANT = "cpsia_compliant"  # US Consumer Product Safety, children's
    REACH_COMPLIANT = "reach_compliant"  # EU REACH
    RoHS_COMPLIANT = "rohs_compliant"  # for smart wearables
    FCC_CERTIFIED = "fcc_certified"  # for smart wearables
    CE_MARKED = "ce_marked"
    KIMBERLEY_VERIFIED = "kimberley_verified"  # rough diamonds origin
    CITES_LISTED = "cites_listed"  # endangered species (coral, etc.)


class LegalModule(OJSBaseModel):
    """Legal / regulatory compliance metadata."""

    hs_code: Optional[HSCodePrefix] = Field(
        default=None, description="HS 2022 code for customs"
    )
    hs_code_full: Optional[Annotated[str, Field(pattern=r"^\d{6,10}$")]] = Field(
        default=None,
        description="Full HS code (6-10 digits) including country sub-classifications",
    )
    country_of_origin: Optional[Annotated[str, Field(pattern=r"^[A-Z]{2}$")]] = Field(
        default=None,
        description="ISO 3166-1 alpha-2 country of origin (required for cross-border)",
    )
    age_restriction_minimum: Optional[Annotated[int, Field(ge=0, le=21)]] = Field(
        default=None,
        description="Minimum age in years (for piercing tools, smart medical wearables)",
    )
    regulatory_flags: list[RegulatoryFlag] = Field(
        default_factory=list, description="Compliance flags claimed"
    )
    ftc_lab_grown_disclosure: Optional[bool] = Field(
        default=None,
        description="Lab-grown disclosed per FTC 16 CFR §23.24 if synthetic stones present",
    )
    ftc_treatment_disclosure: Optional[bool] = Field(
        default=None,
        description="Treatments disclosed per FTC 16 CFR §23.22 if treated stones present",
    )
    cites_permit_number: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="CITES permit number for restricted materials (coral, ivory)",
    )
