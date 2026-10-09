"""OJS v1.0 — Commerce domain.

Pricing, availability, fulfillment. The single most platform-critical domain —
every distribution channel (Schema.org Offer, GMC, ACP, UCP) requires this.

REQUIRED: at least one Offer with price + currency + availability + url
RECOMMENDED: return_policy_url (ACP requires this)
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import CountryCode, Money, OJSBaseModel


class Availability(str, Enum):
    """Product availability state. Aligned with Schema.org ItemAvailability
    and GMC/ACP availability enums."""

    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"
    BACKORDER = "backorder"
    DISCONTINUED = "discontinued"
    LIMITED_AVAILABILITY = "limited_availability"
    MADE_TO_ORDER = "made_to_order"
    UNKNOWN = "unknown"


class Condition(str, Enum):
    """Product condition (used by Schema.org, GMC, ACP)."""

    NEW = "new"
    REFURBISHED = "refurbished"
    USED = "used"
    ESTATE = "estate"  # synonym for used/pre-owned in jewelry trade
    VINTAGE = "vintage"  # 20+ years old
    ANTIQUE = "antique"  # 100+ years old
    PRE_OWNED = "pre_owned"         # authenticated/verified used; TheRealReal, Vestiaire
    NEW_WITH_TAGS = "new_with_tags"  # unworn, original tags present


class PaymentMethod(str, Enum):
    """Accepted payment methods. Influences BNPL/financing signals."""

    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    AFFIRM = "affirm"  # BNPL
    KLARNA = "klarna"  # BNPL
    AFTERPAY = "afterpay"  # BNPL
    SHOP_PAY = "shop_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    OTHER = "other"


class Offer(OJSBaseModel):
    """A single commercial offer for the piece.

    Maps to Schema.org Offer. Multi-region pricing or multi-channel
    offers use multiple Offer entries.
    """

    price: Money = Field(description="Price including currency")
    sale_price: Optional[Money] = Field(
        default=None, description="Sale price if currently on sale"
    )
    sale_starts: Optional[datetime] = Field(default=None, description="Sale start (ISO 8601)")
    sale_ends: Optional[datetime] = Field(default=None, description="Sale end (ISO 8601)")
    availability: Availability = Field(description="Stock state")
    availability_date: Optional[date] = Field(
        default=None,
        description="ISO 8601 date when item becomes available (required if preorder)",
    )
    url: str = Field(description="Product detail page URL (HTTPS preferred)")
    condition: Condition = Field(
        default=Condition.NEW, description="New / used / vintage / antique"
    )
    inventory_count: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, description="Units in stock if quantifiable"
    )
    target_countries: list[CountryCode] = Field(
        min_length=1,
        description="ISO 3166-1 alpha-2 countries where offer is valid (ACP required field)",
    )
    seller_name: Annotated[str, Field(max_length=70)] = Field(
        description="Seller name (ACP required, ≤70 chars)"
    )
    seller_url: str = Field(description="Seller website URL (ACP required)")
    return_policy_url: Optional[str] = Field(
        default=None,
        description="Return policy URL (ACP required for eligible_checkout)",
    )
    seller_privacy_policy_url: Optional[str] = Field(default=None)
    seller_tos_url: Optional[str] = Field(default=None)
    accepted_payments: list[PaymentMethod] = Field(
        default_factory=list, description="Accepted payment methods"
    )
    bnpl_available: Optional[bool] = Field(
        default=None,
        description="Whether BNPL (Affirm/Klarna/Afterpay) is offered — strong AI ranking signal",
    )
    free_shipping: Optional[bool] = Field(default=None)
    free_shipping_threshold: Optional[Money] = Field(default=None)
    handling_time_days: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, description="Days from order to ship"
    )
    free_engraving: Optional[bool] = Field(default=None)
    lifetime_warranty: Optional[bool] = Field(default=None)
    warranty_description: Optional[Annotated[str, Field(max_length=500)]] = None
    warranty_years: Optional[Annotated[float, Field(ge=0)]] = Field(
        default=None,
        description="Manufacturer warranty in years. Complements lifetime_warranty (boolean). "
        "E.g. 2.0 for a 2-year warranty.",
    )
    return_policy_days: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None,
        description="Return window in days. Structured complement to return_policy_url. "
        "GMC and AI agents require numeric value for comparison.",
    )


class CommerceModule(OJSBaseModel):
    """All commercial offers for the piece. REQUIRED.

    Most products have one offer (one retailer); marketplace pieces
    may have many. Use first offer for short-form syndication.
    """

    offers: list[Offer] = Field(min_length=1, description="One or more commercial offers")
    primary_offer_index: int = Field(
        default=0, ge=0, description="Index of canonical offer for short-form syndication"
    )
