"""OJS v1.0 — Master JewelryProduct model.

The root model that composes all 21 domains into a single jewelry record.
Sub-vertical modules are CONDITIONALLY REQUIRED based on `product_type`
discriminator:

  - product_type == "pearl" → `pearls` REQUIRED
  - product_type == "watch" → `watch` REQUIRED
  - product_type == "smart_wearable" → `smart` REQUIRED
  - product_type == "body" → `body` REQUIRED
  - product_type == "estate" → `estate` REQUIRED

Validation enforces these activation rules. Other modules are optional
but recommended per the OJS field tier system (~18 REQUIRED, ~55
RECOMMENDED, ~80 CONDITIONAL, ~138 OPTIONAL).
"""
from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator

from ._common import OJSBaseModel, ProductType, AuditMetadata
from .ai_commerce import AICommerceModule
from .artisan import ArtisanModule
from .body import BodyModule
from .care import CareModule
from .certification import CertificationModule
from .commerce import CommerceModule
from .estate import EstateModule
from .identity import IdentityModule
from .legal import LegalModule
from .media import MediaModule
from .metals import MetalsModule
from .pearls import PearlsModule
from .relationships import RelationshipsModule
from .religious import ReligiousModule
from .reviews import ReviewsModule
from .setting import SettingModule
from .sizing import SizingModule
from .smart import SmartModule
from .stones import StonesModule
from .style import StyleModule
from .watch import WatchModule


class JewelryProduct(OJSBaseModel):
    """The root OJS v1.0 product record.

    Required modules: identity, commerce, media, audit.
    Sub-vertical modules activated by product_type discriminator.
    Other modules are optional but recommended per data tier.

    JSON-LD friendly: when serialized with `@context` reference, this
    becomes valid JSON-LD Schema.org Product with ojs: extensions.
    """

    # --- DISCRIMINATOR ---
    product_type: ProductType = Field(
        description="Top-level product type. Activates sub-vertical modules."
    )

    # --- AUDIT (always required) ---
    audit: AuditMetadata = Field(description="Provenance/audit metadata for the record")

    # --- REQUIRED MODULES ---
    identity: IdentityModule = Field(description="Product identity (REQUIRED)")
    commerce: CommerceModule = Field(description="Pricing/availability (REQUIRED)")
    media: MediaModule = Field(description="Visual assets (REQUIRED — at least 1 image)")

    # --- COMMON OPTIONAL MODULES ---
    metals: Optional[MetalsModule] = Field(
        default=None,
        description="Metal composition. Required for metal-bearing products.",
    )
    stones: Optional[StonesModule] = Field(
        default=None, description="Stone(s) in the piece"
    )
    setting: Optional[SettingModule] = Field(
        default=None, description="How stones are set (skip if no stones)"
    )
    sizing: Optional[SizingModule] = Field(default=None, description="Physical dimensions")
    style: Optional[StyleModule] = Field(default=None, description="Aesthetic/design tags")
    certification: Optional[CertificationModule] = Field(
        default=None, description="Gemological certifications"
    )
    sustainability: Optional[SustainabilityModule] = Field(
        default=None, description="Ethical sourcing claims"
    )
    care: Optional[CareModule] = Field(default=None, description="Cleaning/storage instructions")
    relationships: Optional[RelationshipsModule] = Field(
        default=None, description="Variants and related products"
    )
    reviews: Optional[ReviewsModule] = Field(default=None, description="Aggregate review data")
    legal: Optional[LegalModule] = Field(default=None, description="Compliance metadata")
    ai_commerce: Optional[AICommerceModule] = Field(
        default=None,
        description="AI agent ranking metadata (strongly recommended)",
    )

    # --- SUB-VERTICAL MODULES (conditional) ---
    pearls: Optional[PearlsModule] = Field(
        default=None, description="REQUIRED if product_type='pearl'"
    )
    watch: Optional[WatchModule] = Field(
        default=None, description="REQUIRED if product_type='watch'"
    )
    smart: Optional[SmartModule] = Field(
        default=None, description="REQUIRED if product_type='smart_wearable'"
    )
    body: Optional[BodyModule] = Field(
        default=None, description="REQUIRED if product_type='body'"
    )
    estate: Optional[EstateModule] = Field(
        default=None, description="REQUIRED if product_type='estate'"
    )
    artisan: Optional[ArtisanModule] = Field(
        default=None, description="Optional — for handmade/artist-attributed pieces"
    )
    religious: Optional[ReligiousModule] = Field(
        default=None, description="Optional — for ceremonial/faith pieces"
    )

    # --- DISCRIMINATOR VALIDATION ---
    @model_validator(mode="after")
    def _validate_subvertical_activation(self) -> "JewelryProduct":
        """Enforce that sub-vertical modules are present when product_type requires them."""
        rules = {
            ProductType.PEARL: ("pearls", self.pearls),
            ProductType.WATCH: ("watch", self.watch),
            ProductType.SMART_WEARABLE: ("smart", self.smart),
            ProductType.BODY: ("body", self.body),
            ProductType.ESTATE: ("estate", self.estate),
        }
        pt = self.product_type
        # ProductType may have been coerced to str by use_enum_values=True
        pt_value = pt.value if hasattr(pt, "value") else pt
        for required_type, (module_name, module_value) in rules.items():
            if pt_value == required_type.value and module_value is None:
                raise ValueError(
                    f"product_type='{pt_value}' requires the '{module_name}' module to be populated"
                )
        return self


# Late import to avoid circular reference
from .sustainability import SustainabilityModule  # noqa: E402

JewelryProduct.model_rebuild()
