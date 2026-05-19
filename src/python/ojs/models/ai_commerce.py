"""OJS v1.0 — AI Commerce module (cross-cutting).

AI agent-specific metadata: semantic descriptions, query keywords,
occasion/audience tags, confidence scores. Cross-cutting because every
field in the product can have an associated confidence score, and the
discovery hooks (semantic_description, query_keywords) describe the
product as a whole.

KEY DESIGN DECISIONS:
  - Dual confidence thresholds: ≥0.80 auto-publish, 0.50-0.80 needs review,
    <0.50 do not publish.
  - Semantic description targets AI agents, NOT humans. Different content
    from the human-facing `description` in IdentityModule.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import ConfidenceScore, MultilingualString, OJSBaseModel


class Occasion(str, Enum):
    """Common gift/purchase occasions (multi-valued)."""

    ENGAGEMENT = "engagement"
    WEDDING = "wedding"
    ANNIVERSARY = "anniversary"
    BIRTHDAY = "birthday"
    VALENTINES = "valentines"
    MOTHERS_DAY = "mothers_day"
    FATHERS_DAY = "fathers_day"
    CHRISTMAS = "christmas"
    HANUKKAH = "hanukkah"
    GRADUATION = "graduation"
    PROM = "prom"
    QUINCEANERA = "quinceanera"
    PUSH_PRESENT = "push_present"  # for new mothers
    PROMOTION = "promotion"  # career milestone
    SELF_PURCHASE = "self_purchase"
    EVERYDAY = "everyday"
    EVENING = "evening"
    FORMAL = "formal"
    CASUAL = "casual"
    BRIDAL_PARTY = "bridal_party"  # bridesmaid/groomsman gifts
    OTHER = "other"


class Audience(str, Enum):
    """Target audience tags (multi-valued)."""

    WOMEN = "women"
    MEN = "men"
    UNISEX = "unisex"
    GENDER_NEUTRAL = "gender_neutral"
    CHILDREN = "children"
    TEENS = "teens"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    GIFT_FOR_HER = "gift_for_her"
    GIFT_FOR_HIM = "gift_for_him"
    GIFT_FOR_PARENT = "gift_for_parent"
    GIFT_FOR_PARTNER = "gift_for_partner"
    GIFT_FOR_FRIEND = "gift_for_friend"
    BRIDE = "bride"
    GROOM = "groom"
    GRADUATE = "graduate"


class PriceTier(str, Enum):
    """Coarse price tier for AI agent matching ('affordable luxury', 'fine')."""

    BUDGET = "budget"  # <$100
    AFFORDABLE = "affordable"  # $100-500
    MID_MARKET = "mid_market"  # $500-2000
    AFFORDABLE_LUXURY = "affordable_luxury"  # $2000-10000
    LUXURY = "luxury"  # $10000-50000
    ULTRA_LUXURY = "ultra_luxury"  # $50000+


class AICommerceModule(OJSBaseModel):
    """AI agent ranking metadata.

    Designed to be consumed by ChatGPT (ACP), Perplexity, Google AI Mode,
    Microsoft Copilot, and MCP-based agents. Provides explicit discovery
    hooks the platforms reward (vs. relying on agents to parse free text).
    """

    semantic_description: Annotated[str, Field(min_length=20, max_length=2000)] = Field(
        description=(
            "Description written FOR AI AGENTS, not humans. Should be dense, "
            "factual, attribute-loaded. E.g.: 'Vintage art deco style platinum "
            "solitaire engagement ring with old european cut diamond center "
            "stone, milgrain detail, suitable for engagement and anniversary.'"
        )
    )
    semantic_description_localized: Optional[MultilingualString] = None

    query_keywords: list[Annotated[str, Field(max_length=80)]] = Field(
        default_factory=list,
        max_length=30,
        description=(
            "Phrases real shoppers type ('art deco engagement ring', "
            "'vintage diamond ring under $5000'). Used for query matching."
        ),
    )
    occasion_tags: list[Occasion] = Field(
        default_factory=list, description="Gift/purchase occasions this piece suits"
    )
    audience_tags: list[Audience] = Field(
        default_factory=list, description="Target audiences"
    )
    style_descriptors: list[Annotated[str, Field(max_length=50)]] = Field(
        default_factory=list,
        description="Aesthetic descriptors ('vintage', 'romantic', 'minimalist')",
    )
    price_tier: Optional[PriceTier] = Field(default=None, description="Coarse price tier")

    # Field-level confidence scores. Keys = dotted path into the product
    # (e.g. 'metals.compositions.0.purity_fineness', 'style.era').
    confidence_scores: dict[str, ConfidenceScore] = Field(
        default_factory=dict,
        description="Per-field confidence metadata for enrichment pipeline review",
    )

    # Overall enrichment quality
    overall_quality_score: Optional[Annotated[float, Field(ge=0, le=1)]] = Field(
        default=None, description="Aggregate quality score across all fields (0-1)"
    )
    enrichment_completeness_percent: Optional[Annotated[float, Field(ge=0, le=100)]] = Field(
        default=None, description="% of OJS fields populated (0-100)"
    )
    last_enriched_at: Optional[Annotated[str, Field(pattern=r".+")]] = Field(
        default=None, description="ISO 8601 timestamp of last enrichment run"
    )
