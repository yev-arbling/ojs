"""OJS v1.0 — Certification domain.

Gemological grading reports: lab, report number, link, scan/PDF.
Maps to: Schema.org additionalProperty, GMC product_detail under "Certification".

STRONG conversion signal — every credible diamond retailer displays
GIA/IGI report numbers. Cert presence is table-stakes for fine diamonds.
"""
from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel
from .stones import GradingLab


class Certification(OJSBaseModel):
    """A single gemological / authenticity certificate."""

    lab: GradingLab = Field(description="Issuing laboratory")
    report_number: Annotated[str, Field(min_length=1, max_length=50)] = Field(
        description="Lab's report/certificate number"
    )
    report_url: Optional[str] = Field(
        default=None,
        description="URL to lab's official report verification page",
    )
    report_pdf_url: Optional[str] = Field(
        default=None, description="URL to PDF copy of full report"
    )
    issued_date: Optional[date] = Field(default=None, description="Date report was issued")
    refers_to_stone_index: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None,
        description="Index in stones[] this cert refers to (0=center stone). Omit if for whole piece.",
    )
    notes: Optional[Annotated[str, Field(max_length=500)]] = None


class CertificationModule(OJSBaseModel):
    """All certificates associated with the piece.

    Diamonds typically have one cert per stone. Some pieces have a
    single piece-level cert. AGS certs are legacy-only (lab closed 2022).
    """

    certificates: list[Certification] = Field(
        min_length=1, description="One or more certifications"
    )
