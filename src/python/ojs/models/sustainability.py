"""OJS v1.0 — Sustainability domain.

Provenance, recycled content, ethical sourcing claims.

NOTE on conversion impact: direct sustainability → conversion evidence
is WEAK in published research. The strongest measured effect is
*price-ceiling lift* (Brilliant Earth sustains 10-20% premium) and
*AI agent ranking bias* (some AI agents weight ESG claims). Do not
oversell to retailers as a primary conversion driver.

REFERENCES:
  - RJC Code of Practices (Responsible Jewellery Council)
  - Kimberley Process Certification Scheme (rough diamonds)
  - Fairmined certification (artisanal gold)
  - WGC Code of Conduct (gold)
  - W3C Verifiable Supply Chain CG (luxury goods, proposed 2026-02-03)
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class SustainabilityCertification(str, Enum):
    """Recognized sustainability/ethical sourcing certifications."""

    RJC_CoP = "rjc_cop"  # RJC Code of Practices
    RJC_CoC = "rjc_coc"  # RJC Chain of Custody
    KIMBERLEY_PROCESS = "kimberley_process"  # rough diamonds only
    FAIRMINED = "fairmined"  # artisanal gold
    FAIRTRADE_GOLD = "fairtrade_gold"
    SCS_RECYCLED = "scs_recycled"  # SCS Global Services recycled content
    BLUESIGN = "bluesign"  # rare in jewelry but used for textile straps
    OEKO_TEX = "oeko_tex"  # rare in jewelry
    WGC_CONFLICT_FREE = "wgc_conflict_free"
    DIAMOND_FOUNDRY_CERT = "diamond_foundry_cert"  # lab-grown specific
    BCORP = "bcorp"  # company-level
    OTHER = "other"


class OriginClaim(str, Enum):
    """Geographic/ethical origin claim."""

    CANADIAN_DIAMOND = "canadian_diamond"
    BOTSWANA_SORT = "botswana_sort"  # De Beers / Brilliant Earth program
    AUSTRALIAN_DIAMOND = "australian_diamond"  # post-Argyle closure
    RECYCLED_GOLD = "recycled_gold"
    FAIRMINED_GOLD = "fairmined_gold"
    RECYCLED_PLATINUM = "recycled_platinum"
    RECYCLED_SILVER = "recycled_silver"
    SINGLE_ORIGIN = "single_origin"  # traceable to one mine
    BLOCKCHAIN_TRACKED = "blockchain_tracked"  # Tracr, Everledger, etc.
    OTHER = "other"


class CarbonClaim(OJSBaseModel):
    """Carbon footprint or offset claim."""

    is_carbon_neutral_shipping: Optional[bool] = None
    is_carbon_neutral_product: Optional[bool] = None
    carbon_kg_co2e: Optional[Annotated[float, Field(ge=0)]] = Field(
        default=None, description="Lifecycle CO2-equivalent emissions (kg)"
    )
    offset_provider: Optional[Annotated[str, Field(max_length=100)]] = None
    offset_verification: Optional[Annotated[str, Field(max_length=200)]] = Field(
        default=None, description="Verifier (e.g. 'Verra', 'Gold Standard')"
    )


class SustainabilityModule(OJSBaseModel):
    """Sustainability and ethical sourcing claims.

    Audit chain required for every claim. Unsubstantiated claims may
    trigger greenwashing regulatory action (EU Green Claims Directive,
    FTC Green Guides 16 CFR Part 260).
    """

    certifications: list[SustainabilityCertification] = Field(
        default_factory=list,
        description="Held sustainability/ethical certifications",
    )
    origin_claims: list[OriginClaim] = Field(
        default_factory=list,
        description="Origin/provenance claims",
    )
    recycled_metal_percent: Optional[Annotated[float, Field(ge=0, le=100)]] = Field(
        default=None, description="Percent recycled metal (0-100). Audit required."
    )
    is_conflict_free: Optional[bool] = Field(
        default=None,
        description="Compliant with conflict-free sourcing (OECD due diligence)",
    )
    is_lab_grown_marketed: Optional[bool] = Field(
        default=None,
        description="Marketed as lab-grown alternative to mined (FTC disclosure rule applies)",
    )
    is_traceable: Optional[bool] = Field(
        default=None, description="Full supply-chain traceability available"
    )
    traceability_url: Optional[str] = Field(
        default=None, description="URL to traceability dashboard/blockchain record"
    )
    carbon: Optional[CarbonClaim] = Field(default=None, description="Carbon footprint claims")
    sustainability_story: Optional[Annotated[str, Field(max_length=2000)]] = Field(
        default=None,
        description="Free-text sustainability story for AI agent narrative use",
    )
