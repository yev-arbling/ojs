"""OJS v1.0 — Pydantic v2 models.

Single source of truth for the Open Jewelry Schema. Generates:
  - JSON Schema Draft 2020-12 (strict)
  - JSON-LD context (separate file)
  - Platform-specific transformers (Schema.org, GMC, ACP, UCP, Perplexity, Shopify, MCP)

Usage:
    from ojs.models import JewelryProduct, ProductType
    product = JewelryProduct(product_type=ProductType.RING, ...)
    json_str = product.model_dump_json(indent=2)
"""
from ._common import (
    OJS_VERSION,
    OJS_NAMESPACE,
    OJSBaseModel,
    ProductType,
    AuditMetadata,
    SourceSystem,
    ConfidenceScore,
    ConfidenceSource,
    MultilingualString,
    Money,
    Dimension,
    Weight,
    DimensionUnit,
    WeightUnit,
)
from .ai_commerce import AICommerceModule, Occasion, Audience, PriceTier
from .artisan import ArtisanModule, ArtisanTechnique, EditionType
from .body import (
    BodyModule,
    PiercingLocation,
    BiocompatibilityStandard,
    ThreadingType,
    GaugeMeasurement,
)
from .care import CareModule, CleaningMethod, ActivitySafety, StorageRecommendation
from .certification import CertificationModule, Certification
from .commerce import (
    CommerceModule,
    Offer,
    Availability,
    Condition,
    PaymentMethod,
)
from .estate import EstateModule, Hallmark, ProvenanceEntry, RestorationRecord
from .identity import IdentityModule, Brand, ProductSubtype
from .jewelry_product import JewelryProduct
from .legal import LegalModule, HSCodePrefix, RegulatoryFlag
from .media import MediaModule, ImageAsset, VideoAsset, ARMetadata, ImageRole, PlacementAnchor
from .metals import (
    MetalsModule,
    MetalComposition,
    MetalType,
    MetalColor,
    MetalFinish,
    PlatingType,
)
from .pearls import (
    PearlsModule,
    PearlType,
    PearlLuster,
    PearlSurface,
    PearlShape,
    PearlBodyColor,
    PearlOvertone,
    NacreQuality,
    PearlMatchingGrade,
)
from .relationships import RelationshipsModule, ProductRelation, RelationshipType, VariantAxis
from .religious import ReligiousModule, Religion, CeremonyType
from .reviews import ReviewsModule, AggregateRating, Review
from .setting import SettingModule, SettingStyle, SettingType
from .sizing import SizingModule, RingSize, SizeSystem, JewelryClosure, EarringPostType
from .smart import SmartModule, SmartFeature, Connectivity, WaterProofRating
from .stones import (
    StonesModule,
    Stone,
    GemstoneSpecies,
    StoneOrigin,
    StoneCut,
    GradingLab,
    DiamondColorGrade,
    DiamondClarityGrade,
    ColoredStoneClarityGrade,
    CutGrade,
    FluorescenceIntensity,
    TreatmentType,
)
from .style import StyleModule, Era, DesignStyle, Motif, ChainStyle
from .sustainability import (
    SustainabilityModule,
    SustainabilityCertification,
    OriginClaim,
    CarbonClaim,
)
from .watch import (
    WatchModule,
    MovementType,
    WatchComplication,
    CrystalType,
    StrapType,
    CaseShape,
    WaterResistanceRating,
)

__all__ = [
    "OJS_VERSION",
    "OJS_NAMESPACE",
    "OJSBaseModel",
    "JewelryProduct",
    "ProductType",
    # Core building blocks
    "AuditMetadata",
    "SourceSystem",
    "ConfidenceScore",
    "ConfidenceSource",
    "MultilingualString",
    "Money",
    "Dimension",
    "Weight",
    "DimensionUnit",
    "WeightUnit",
    # 21 modules
    "IdentityModule",
    "Brand",
    "ProductSubtype",
    "MetalsModule",
    "MetalComposition",
    "StonesModule",
    "Stone",
    "ColoredStoneClarityGrade",
    "PearlsModule",
    "SettingModule",
    "SettingStyle",
    "SizingModule",
    "RingSize",
    "EarringPostType",
    "StyleModule",
    "ChainStyle",
    "CommerceModule",
    "Offer",
    "CertificationModule",
    "Certification",
    "SustainabilityModule",
    "CareModule",
    "WatchModule",
    "BodyModule",
    "EstateModule",
    "ArtisanModule",
    "ReligiousModule",
    "SmartModule",
    "RelationshipsModule",
    "ReviewsModule",
    "AggregateRating",
    "MediaModule",
    "ImageAsset",
    "VideoAsset",
    "ARMetadata",
    "LegalModule",
    "AICommerceModule",
]
