"""OJS v1.0 — Relationships domain.

Product relationships: variants, sets, pairs, accessories.
Maps to: Schema.org hasVariant/isVariantOf, GMC item_group_id,
        ACP related_product_id + relationship_type, Shopify product variants.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import ItemID, OJSBaseModel


class RelationshipType(str, Enum):
    """How two products relate (matches ACP relationship_type enum)."""

    VARIANT = "variant"  # same product, different size/color/metal
    IS_VARIANT_OF = "is_variant_of"
    PART_OF_SET = "part_of_set"  # earrings + matching necklace
    PAIRS_WITH = "pairs_with"  # often_bought_with
    SUBSTITUTE = "substitute"
    REPLACES = "replaces"
    SUCCESSOR_OF = "successor_of"
    DIFFERENT_BRAND = "different_brand"
    ACCESSORY = "accessory"  # chain for pendant, box, polishing cloth
    REQUIRED_PART = "required_part"  # chain required for pendant to wear


class ProductRelation(OJSBaseModel):
    """A relationship to another product."""

    related_sku: ItemID = Field(description="SKU of related product")
    relationship_type: RelationshipType = Field(description="Type of relationship")
    description: Optional[Annotated[str, Field(max_length=500)]] = None


class VariantAxis(OJSBaseModel):
    """A dimension of variation (e.g. 'metal_color', 'ring_size', 'stone_size').

    Used to group SKUs into a coherent product family. Shopify exposes
    these as Option 1/2/3 (max 3 axes, 2048 variants total).
    """

    name: Annotated[str, Field(max_length=50)] = Field(
        description="Axis name (e.g. 'metal_color', 'ring_size', 'stone_carat')"
    )
    value: Annotated[str, Field(max_length=100)] = Field(
        description="This SKU's value on this axis (e.g. 'yellow_gold', '7', '1.5ct')"
    )


class RelationshipsModule(OJSBaseModel):
    """Variant grouping and related-product relationships."""

    item_group_id: Optional[Annotated[str, Field(max_length=100)]] = Field(
        default=None,
        description="Stable group ID shared by all variants of this product (GMC item_group_id, ACP group_id, Shopify product ID)",
    )
    variant_axes: list[VariantAxis] = Field(
        default_factory=list,
        max_length=3,
        description="Up to 3 axes (Shopify cap). For ACP, also fills Custom_variant1-3.",
    )
    is_master_variant: bool = Field(
        default=False, description="Whether this SKU is the canonical/master variant"
    )
    related_products: list[ProductRelation] = Field(
        default_factory=list, description="Related products by SKU"
    )
