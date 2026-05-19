"""OJS v1.0 — Identity domain.

Product identification: SKU, GTIN, MPN, brand, model, title, description.
Maps to: Schema.org Product (sku, gtin, brand, name, description),
        GMC (id, gtin, mpn, brand, title, description),
        ACP (item_id, gtin, mpn, brand, title, description),
        Shopify (product.handle, product.title, product.vendor).

REQUIRED FIELDS: sku, title, brand, description
RECOMMENDED: gtin, mpn, model
"""
from __future__ import annotations

from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from ._common import GTIN, ItemID, MultilingualString, OJSBaseModel


class Brand(OJSBaseModel):
    """Brand / manufacturer identity.

    Maps to: Schema.org Brand, GMC `brand`, ACP `brand`, Shopify `vendor`.
    """

    name: Annotated[str, StringConstraints(min_length=1, max_length=70)] = Field(
        description="Brand name (≤70 chars per ACP and GMC limits)"
    )
    legal_name: Optional[Annotated[str, StringConstraints(max_length=200)]] = Field(
        default=None,
        description="Full legal entity name if different from brand name",
    )
    website: Optional[str] = Field(
        default=None, description="Brand official website URL"
    )
    logo_url: Optional[str] = Field(default=None, description="Brand logo URL")
    gln: Optional[Annotated[str, StringConstraints(pattern=r"^\d{13}$")]] = Field(
        default=None,
        description="GS1 Global Location Number (13 digits) — links to GS1 registry",
    )


class IdentityModule(OJSBaseModel):
    """Product identity. REQUIRED on every JewelryProduct.

    The minimum viable fields for cross-platform syndication. Every
    downstream platform (Schema.org, GMC, ACP, UCP, Shopify, MCP)
    requires title + brand + a stable identifier.
    """

    sku: ItemID = Field(
        description="Stable SKU. Maps to: Schema.org sku, GMC id, ACP item_id, Shopify variant.sku"
    )
    title: Annotated[str, StringConstraints(min_length=1, max_length=150)] = Field(
        description="Product title (≤150 chars per ACP; ≤150 GMC recommended). Avoid all-caps."
    )
    title_localized: Optional[MultilingualString] = Field(
        default=None,
        description="Title in additional languages. Use for multi-locale catalogs.",
    )
    description: Annotated[str, StringConstraints(min_length=1, max_length=5000)] = Field(
        description="Plain-text product description (≤5000 chars per ACP)"
    )
    description_localized: Optional[MultilingualString] = Field(
        default=None,
        description="Description in additional languages",
    )
    brand: Brand = Field(description="Brand / manufacturer")
    gtin: Optional[GTIN] = Field(
        default=None,
        description="GTIN-8/12/13/14. Strongly recommended — major AI ranking signal.",
    )
    mpn: Optional[Annotated[str, StringConstraints(max_length=70)]] = Field(
        default=None,
        description="Manufacturer Part Number (≤70 chars per ACP)",
    )
    model: Optional[Annotated[str, StringConstraints(max_length=100)]] = Field(
        default=None,
        description="Model name (e.g. 'Submariner Date 126610LN' for Rolex)",
    )
    collection: Optional[Annotated[str, StringConstraints(max_length=100)]] = Field(
        default=None,
        description="Collection or line name (e.g. 'Love', 'Tank', 'Trinity')",
    )
    designer: Optional[Annotated[str, StringConstraints(max_length=100)]] = Field(
        default=None,
        description="Designer name if distinct from brand (e.g. 'Aldo Cipullo' for Cartier Love)",
    )
    handle: Optional[Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+$", max_length=100)]] = Field(
        default=None,
        description="URL-safe slug. Shopify-style handle (lowercase, hyphens). Auto-generated if absent.",
    )
