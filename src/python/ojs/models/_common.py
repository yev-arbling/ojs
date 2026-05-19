"""OJS v1.0 — Common types, enums, and validators shared across all domains.

This module is the foundation of the Open Jewelry Schema. Every domain
imports from here. Single source of truth for:
  - Primitive types (URLs, ISO codes, dates)
  - Money / Currency
  - Multilingual strings
  - Measurement primitives (Dimension, Weight)
  - Confidence scoring
  - Audit metadata
  - Source provenance
"""
from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
)

# --- Constants ----------------------------------------------------------

OJS_VERSION = "1.0.0"
OJS_NAMESPACE = "https://schema.openjewelryschema.org/v1/"

# ISO 4217 currency code (3 uppercase letters)
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]

# ISO 3166-1 alpha-2 country code (2 uppercase letters)
CountryCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]

# ISO 639-1 language code (2 lowercase letters)
LanguageCode = Annotated[str, StringConstraints(pattern=r"^[a-z]{2}$")]

# GTIN: 8, 12, 13, or 14 digits
GTIN = Annotated[str, StringConstraints(pattern=r"^\d{8}$|^\d{12}$|^\d{13}$|^\d{14}$")]

# Stable item identifier (ACP item_id, max 100 chars)
ItemID = Annotated[str, StringConstraints(min_length=1, max_length=100)]

# --- Base config --------------------------------------------------------


class OJSBaseModel(BaseModel):
    """Base model with shared config. All OJS models inherit from this."""

    model_config = ConfigDict(
        extra="forbid",  # strict — unknown fields raise; use x_* for extensions
        str_strip_whitespace=True,
        use_enum_values=True,
        populate_by_name=True,
    )


# --- Confidence scoring -------------------------------------------------


class ConfidenceSource(str, Enum):
    """Where a value came from. Higher confidence sources outrank lower."""

    MANUAL = "manual"  # Human-entered by retailer (1.0)
    CERTIFICATE = "certificate"  # Imported from GIA/IGI/etc PDF (0.99)
    REGEX_TEXT = "regex_text"  # Pattern-matched from description (0.85-0.95)
    CV_IMAGE = "cv_image"  # Computer vision from product photo (0.60-0.96)
    LLM_INFERRED = "llm_inferred"  # LLM inferred from context (0.50-0.85)
    DEFAULT = "default"  # Schema default fallback (0.20)


Confidence = Annotated[float, Field(ge=0.0, le=1.0)]


class ConfidenceScore(OJSBaseModel):
    """Confidence metadata for a field value.

    Surfaced in the Arbling enrichment pipeline so retailers can see
    which fields are reliable vs. need review.
    """

    value: Confidence = Field(description="0.0-1.0 confidence score")
    source: ConfidenceSource = Field(description="How the value was derived")
    validated_at: Optional[datetime] = Field(
        default=None, description="When a human last confirmed this value"
    )


# --- Multilingual ------------------------------------------------------


class MultilingualString(OJSBaseModel):
    """Text in multiple languages, keyed by ISO 639-1 code.

    Use for product titles, descriptions, care instructions, etc.
    Always include at least one language; 'en' recommended as fallback.
    """

    en: Optional[str] = None
    es: Optional[str] = None
    fr: Optional[str] = None
    de: Optional[str] = None
    it: Optional[str] = None
    ja: Optional[str] = None
    zh: Optional[str] = None
    ru: Optional[str] = None
    ar: Optional[str] = None
    pt: Optional[str] = None
    ko: Optional[str] = None
    # Catch-all for other languages
    other: Optional[dict[LanguageCode, str]] = None

    def primary(self) -> Optional[str]:
        """Return the first non-empty value, preferring English."""
        return self.en or self.es or self.fr or self.de or self.zh

    @field_validator("other", mode="before")
    @classmethod
    def validate_other_keys(cls, v):
        if v is None:
            return v
        for k in v:
            if not re.fullmatch(r"[a-z]{2}", k):
                raise ValueError(
                    f"Language key '{k}' must be ISO 639-1 (2 lowercase letters)"
                )
        return v


# --- Money / Price ----------------------------------------------------


class Money(OJSBaseModel):
    """A monetary amount with currency.

    `amount` is stored as Decimal-compatible string to avoid float drift.
    Always pair with `currency` (ISO 4217). Schema.org maps this to
    PriceSpecification; GMC splits into `price` + `currency`.
    """

    amount: Decimal = Field(ge=0, description="Amount, non-negative")
    currency: CurrencyCode = Field(description="ISO 4217 currency code (e.g. 'USD')")

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


# --- Measurements -----------------------------------------------------


class DimensionUnit(str, Enum):
    """Length units. UN/CEFACT codes in parentheses for reference."""

    MILLIMETER = "mm"  # MMT
    CENTIMETER = "cm"  # CMT
    METER = "m"  # MTR
    INCH = "in"  # INH
    FOOT = "ft"  # FOT


class WeightUnit(str, Enum):
    """Weight units. UN/CEFACT codes in parentheses for reference."""

    CARAT = "ct"  # CTM — for gemstones
    GRAM = "g"  # GRM
    KILOGRAM = "kg"  # KGM
    OUNCE = "oz"  # ONZ
    POUND = "lb"  # LBR
    GRAIN = "gr"  # GRN — used for pearls historically
    PENNYWEIGHT = "dwt"  # DWT — used in precious metals trade


class Dimension(OJSBaseModel):
    """A length measurement with unit."""

    value: float = Field(gt=0, description="Numeric value, positive")
    unit: DimensionUnit = Field(description="Unit of measurement")


class Weight(OJSBaseModel):
    """A weight measurement with unit. Use carat (ct) for gemstones."""

    value: float = Field(gt=0, description="Numeric value, positive")
    unit: WeightUnit = Field(description="Unit of measurement")


# --- Audit / provenance -----------------------------------------------


class SourceSystem(str, Enum):
    """Where the OJS record was created or last updated."""

    MANUAL = "manual"
    SHOPIFY = "shopify"
    ARBLING_PIPELINE = "arbling_pipeline"
    PIM_AKENEO = "pim_akeneo"
    PIM_SALSIFY = "pim_salsify"
    PIM_SYNDIGO = "pim_syndigo"
    GMC_IMPORT = "gmc_import"
    ACP_IMPORT = "acp_import"
    OTHER = "other"


class AuditMetadata(OJSBaseModel):
    """Provenance metadata for the OJS record itself.

    REQUIRED on every JewelryProduct. Tracks who/when/where the data
    came from for compliance and round-trip integrity.
    """

    ojs_version: str = Field(
        default=OJS_VERSION,
        pattern=r"^\d+\.\d+\.\d+$",
        description="SemVer of the OJS spec this record conforms to",
    )
    created_at: datetime = Field(description="ISO 8601 timestamp of record creation")
    updated_at: Optional[datetime] = Field(
        default=None, description="ISO 8601 timestamp of last update"
    )
    source_system: SourceSystem = Field(description="Where this record was created")
    source_record_id: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Source system's native record ID for round-trip",
    )
    last_validated_by_human: Optional[datetime] = Field(
        default=None,
        description="When a human last reviewed this record end-to-end",
    )


# --- Product type discriminator ---------------------------------------


class ProductType(str, Enum):
    """Top-level discriminator. Activates sub-vertical modules.

    See domain docs for which fields become required per type:
      - pearl → pearls module
      - watch → watch module
      - smart_wearable → smart module
      - body → body module
      - estate → estate module
    """

    RING = "ring"
    EARRING = "earring"
    NECKLACE = "necklace"
    BRACELET = "bracelet"
    PENDANT = "pendant"
    BROOCH = "brooch"
    ANKLET = "anklet"
    WATCH = "watch"
    PEARL = "pearl"
    SMART_WEARABLE = "smart_wearable"
    BODY = "body"
    ESTATE = "estate"
    JEWELRY_SET = "jewelry_set"
    OTHER = "other"
