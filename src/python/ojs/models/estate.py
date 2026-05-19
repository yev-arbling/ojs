"""OJS v1.0 — Estate domain (sub-vertical discriminator).

Activated when product_type == "estate" OR condition is vintage/antique.
Estate / vintage / antique jewelry requires authentication beyond standard.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class HallmarkType(str, Enum):
    """Common hallmark types."""

    MAKER_MARK = "maker_mark"  # workshop/maker identifier
    ASSAY_OFFICE = "assay_office"  # UK assay office (London, Birmingham, Sheffield, Edinburgh)
    FINENESS_MARK = "fineness_mark"  # 750, 925, etc.
    DATE_LETTER = "date_letter"  # UK year code
    DUTY_MARK = "duty_mark"  # historic tax mark
    STANDARD_MARK = "standard_mark"  # country-specific (e.g. French head)
    IMPORT_MARK = "import_mark"
    OTHER = "other"


class Hallmark(OJSBaseModel):
    """A single hallmark stamped on the piece."""

    hallmark_type: HallmarkType
    mark_text: Annotated[str, Field(max_length=50)] = Field(
        description="Text/symbol of the mark (e.g. 'LION PASSANT', '750', 'M' date letter)"
    )
    location_on_piece: Optional[Annotated[str, Field(max_length=100)]] = Field(
        default=None, description="Where on piece (e.g. 'inner shank', 'clasp underside')"
    )
    interpretation: Optional[Annotated[str, Field(max_length=500)]] = Field(
        default=None, description="What it tells us (e.g. 'Sterling silver, London 1925')"
    )
    photo_url: Optional[str] = None


class ProvenanceEntry(OJSBaseModel):
    """A single chain-of-ownership entry."""

    year_from: Optional[Annotated[int, Field(ge=1000, le=2100)]] = None
    year_to: Optional[Annotated[int, Field(ge=1000, le=2100)]] = None
    owner: Annotated[str, Field(max_length=200)] = Field(
        description="Person, family, institution, or auction house"
    )
    description: Optional[Annotated[str, Field(max_length=1000)]] = Field(
        default=None, description="Notes on ownership period"
    )
    documentation_url: Optional[str] = Field(
        default=None, description="Auction record, certificate, photograph URL"
    )


class RestorationRecord(OJSBaseModel):
    """A documented repair/restoration event."""

    restored_date: Optional[date] = Field(
        default=None, description="When the restoration was performed"
    )
    restorer: Optional[Annotated[str, Field(max_length=200)]] = None
    description: Annotated[str, Field(max_length=1000)] = Field(
        description="What was done (e.g. 'replaced 2 prongs', 'restrung pearls')"
    )
    parts_replaced: Optional[list[Annotated[str, Field(max_length=100)]]] = None


class EstateModule(OJSBaseModel):
    """Estate / vintage / antique authentication.

    Pieces classified as vintage (20+ years) or antique (100+ years)
    need provenance documentation to command premium pricing.
    """

    period_verified: Optional[bool] = Field(
        default=None,
        description="Period attribution verified by qualified appraiser/specialist",
    )
    period_appraiser: Optional[Annotated[str, Field(max_length=200)]] = None
    hallmarks: list[Hallmark] = Field(default_factory=list, description="Stamped hallmarks")
    provenance: list[ProvenanceEntry] = Field(
        default_factory=list, description="Chain of ownership"
    )
    restoration_history: list[RestorationRecord] = Field(
        default_factory=list, description="Documented restorations"
    )
    original_box_papers: Optional[bool] = Field(
        default=None, description="Original box, papers, receipts retained"
    )
    age_estimate_year_from: Optional[Annotated[int, Field(ge=1000, le=2100)]] = None
    age_estimate_year_to: Optional[Annotated[int, Field(ge=1000, le=2100)]] = None
    appraisal_value: Optional[Annotated[str, Field(max_length=200)]] = Field(
        default=None, description="Formal appraisal value (text to preserve currency notation)"
    )
    appraisal_date: Optional[date] = None
    appraisal_url: Optional[str] = None
