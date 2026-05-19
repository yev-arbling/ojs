"""OJS v1.0 — Agentic Commerce Protocol (ACP) transformer (bidirectional).

OpenAI ACP file-upload spec, 2026-04-17. Reference:
developers.openai.com/commerce/specs/file-upload/products

Key ACP fields:
  - item_id (≤100 chars, stable identifier)
  - is_eligible_search / is_eligible_checkout (flat booleans)
  - group_id + variant_dict for variant groups
  - Custom_variant1, Custom_variant2, Custom_variant3 for axes
  - q_and_a for customer questions
  - relationship_type for related products

For jewelry, the typical Custom_variant assignment is:
  Custom_variant1 = Metal_Color
  Custom_variant2 = Stone_Cut OR Stone_Carat
  Custom_variant3 = Ring_Size OR Chain_Length

Output is a list of dicts (one per variant) — caller serializes to the
ACP file-upload format (JSON Lines).
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct

_AVAIL_ACP = {
    "in_stock": "in_stock",
    "out_of_stock": "out_of_stock",
    "preorder": "preorder",
    "backorder": "backorder",
    "discontinued": "out_of_stock",
    "limited_availability": "in_stock",
    "made_to_order": "preorder",
}
_COND_ACP = {
    "new": "new", "refurbished": "refurbished", "used": "used",
    "estate": "used", "vintage": "used", "antique": "used",
}


def to_acp(product: JewelryProduct) -> dict:
    """Render OJS as an ACP product entry dict.

    Returns a single dict. For multi-variant products, the caller
    invokes this on each variant and uploads as JSON Lines (one entry per line).
    """
    p = product
    offer = p.commerce.offers[p.commerce.primary_offer_index]

    # Eligibility — auto-set based on data completeness
    has_return_policy = bool(offer.return_policy_url)
    has_seller_url = bool(offer.seller_url)
    is_in_stock = offer.availability == "in_stock"
    is_eligible_checkout = has_return_policy and has_seller_url and is_in_stock
    is_eligible_search = bool(p.identity.title and p.identity.description and p.media.images)

    out: dict[str, Any] = {
        "item_id": p.identity.sku[:100],
        "is_eligible_search": is_eligible_search,
        "is_eligible_checkout": is_eligible_checkout,
        "title": p.identity.title[:150],
        "description": p.identity.description[:5000],
        "link": offer.url,
        "image_link": next((i.url for i in p.media.images if i.is_primary), p.media.images[0].url),
        "additional_image_link": [i.url for i in p.media.images if not i.is_primary][:9],
        "price": str(offer.price.amount),
        "currency": offer.price.currency,
        "availability": _AVAIL_ACP.get(offer.availability, "in_stock"),
        "condition": _COND_ACP.get(offer.condition, "new"),
        "brand": p.identity.brand.name[:70],
        "seller_name": offer.seller_name[:70],
        "seller_url": offer.seller_url,
        "target_countries": offer.target_countries,
    }

    if p.identity.gtin: out["gtin"] = p.identity.gtin
    if p.identity.mpn: out["mpn"] = p.identity.mpn
    if offer.return_policy_url: out["return_policy_url"] = offer.return_policy_url
    if offer.sale_price:
        out["sale_price"] = str(offer.sale_price.amount)
    if p.media.videos:
        out["video_url"] = p.media.videos[0].url
    if p.media.glb_url:
        out["model_3d_url"] = p.media.glb_url

    # Variant grouping
    if p.relationships:
        if p.relationships.item_group_id:
            out["group_id"] = p.relationships.item_group_id
        # variant_dict {axis: value} pairs
        if p.relationships.variant_axes:
            out["variant_dict"] = {a.name: a.value for a in p.relationships.variant_axes}
        # Standard Custom_variant1-3 mapping for jewelry
        for i, axis in enumerate(p.relationships.variant_axes[:3], start=1):
            out[f"Custom_variant{i}_name"] = axis.name
            out[f"Custom_variant{i}_value"] = axis.value

    # Material short form
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        karat = {999: "24k", 916: "22k", 750: "18k", 585: "14k", 417: "10k"}.get(primary.purity_fineness, "")
        parts = []
        if primary.color: parts.append(str(primary.color))
        if karat: parts.append(karat)
        parts.append(str(primary.type))
        out["material"] = " ".join(parts).replace("_", " ")
        if primary.color:
            out["color"] = str(primary.color).replace("_", " ")

    # Reviews → ACP product-level stars
    if p.reviews and p.reviews.aggregate:
        out["star_rating"] = round(p.reviews.aggregate.rating_value, 1)
        out["review_count"] = p.reviews.aggregate.review_count

    # Q&A
    if p.reviews and p.reviews.qa_questions:
        out["q_and_a"] = [
            {"question": q, "answer": a}
            for q, a in zip(p.reviews.qa_questions, p.reviews.qa_answers)
        ]

    # Related products
    if p.relationships and p.relationships.related_products:
        out["related_products"] = [
            {"related_item_id": r.related_sku, "relationship_type": r.relationship_type}
            for r in p.relationships.related_products
        ]

    # ACP doesn't have a dedicated jewelry-attribute slot. Stuff key
    # AI-rankable fields into a "category_attributes" map for ChatGPT
    # to consume.
    cat_attrs: dict[str, Any] = {}
    if p.stones and p.stones.stones:
        s = p.stones.stones[0]
        cat_attrs["stone_species"] = s.species
        cat_attrs["stone_origin"] = s.origin_type
        if s.carat: cat_attrs["stone_carat"] = s.carat
        if s.cut: cat_attrs["stone_cut"] = s.cut
        if s.color_grade: cat_attrs["stone_color_grade"] = s.color_grade
        if s.clarity_grade: cat_attrs["stone_clarity_grade"] = s.clarity_grade
        if p.stones.total_carat_weight:
            cat_attrs["total_carat_weight"] = p.stones.total_carat_weight

    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        if primary.purity_fineness:
            cat_attrs["metal_fineness"] = primary.purity_fineness
        if primary.plating and primary.plating != "none":
            cat_attrs["metal_plating"] = primary.plating

    if p.pearls:
        cat_attrs["pearl_type"] = p.pearls.pearl_type
        cat_attrs["pearl_luster"] = p.pearls.luster
        cat_attrs["pearl_size_mm"] = p.pearls.size_mm

    if p.watch:
        cat_attrs["watch_movement"] = p.watch.movement_type
        if p.watch.caliber: cat_attrs["watch_caliber"] = p.watch.caliber
        if p.watch.case_diameter_mm: cat_attrs["watch_case_diameter_mm"] = p.watch.case_diameter_mm

    if p.certification and p.certification.certificates:
        c0 = p.certification.certificates[0]
        cat_attrs["cert_lab"] = c0.lab
        cat_attrs["cert_number"] = c0.report_number

    if p.style and p.style.era:
        cat_attrs["era"] = p.style.era

    if p.ai_commerce:
        if p.ai_commerce.semantic_description:
            cat_attrs["semantic_description"] = p.ai_commerce.semantic_description
        if p.ai_commerce.occasion_tags:
            cat_attrs["occasions"] = [str(o) for o in p.ai_commerce.occasion_tags]

    if cat_attrs:
        out["category_attributes"] = cat_attrs

    return out


def from_acp(data: dict) -> dict:
    """Reverse: parse ACP entry into partial OJS-compatible dict."""
    out: dict[str, Any] = {}
    ident: dict[str, Any] = {}
    if "item_id" in data: ident["sku"] = data["item_id"]
    if "title" in data: ident["title"] = data["title"]
    if "description" in data: ident["description"] = data["description"]
    if "brand" in data: ident["brand"] = {"name": data["brand"]}
    if "gtin" in data: ident["gtin"] = data["gtin"]
    if "mpn" in data: ident["mpn"] = data["mpn"]
    if ident: out["identity"] = ident

    # Recover category_attributes
    if "category_attributes" in data:
        out["_acp_category_attributes"] = data["category_attributes"]
    if "variant_dict" in data:
        out["_acp_variant_dict"] = data["variant_dict"]
    return out
