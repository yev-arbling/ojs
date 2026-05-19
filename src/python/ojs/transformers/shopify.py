"""OJS v1.0 — Shopify transformer (bidirectional).

Highest-fidelity downstream target. Two complementary outputs:

  to_shopify_product(): The Shopify Product object structure (handle,
    title, vendor, product_type, tags, variants, options, images).

  to_shopify_metafields(): A list of metafield objects to attach to the
    product or its variants. STRATEGY:
      1. Store full canonical OJS as `ojs.full` (type=json)
      2. Mirror critical scalar fields as typed metafields for Catalog
         Mapping and Shopify's native filtering
      3. Round-trip preservation via the canonical json metafield

Shopify constraints:
  - Max 3 option axes per product (size/color/material common)
  - Max 2048 variants per product
  - Metafield types used: single_line_text_field, multi_line_text_field,
    number_integer, number_decimal, boolean, date, date_time, json,
    color, weight, dimension, money, rating, file_reference, list.*
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct, ProductType

_SHOPIFY_PRODUCT_TYPE = {
    ProductType.RING: "Rings",
    ProductType.EARRING: "Earrings",
    ProductType.NECKLACE: "Necklaces",
    ProductType.BRACELET: "Bracelets",
    ProductType.PENDANT: "Pendants",
    ProductType.BROOCH: "Brooches",
    ProductType.ANKLET: "Anklets",
    ProductType.WATCH: "Watches",
    ProductType.PEARL: "Pearl Jewelry",
    ProductType.SMART_WEARABLE: "Smart Wearables",
    ProductType.BODY: "Body Jewelry",
    ProductType.ESTATE: "Estate Jewelry",
    ProductType.JEWELRY_SET: "Jewelry Sets",
    ProductType.OTHER: "Jewelry",
}


def to_shopify_product(product: JewelryProduct) -> dict:
    """OJS → Shopify Product object dict."""
    p = product
    offer = p.commerce.offers[p.commerce.primary_offer_index]
    pt_value = p.product_type.value if hasattr(p.product_type, 'value') else p.product_type

    out: dict[str, Any] = {
        "title": p.identity.title,
        "body_html": _html_description(p),
        "vendor": p.identity.brand.name,
        "product_type": _SHOPIFY_PRODUCT_TYPE.get(p.product_type, "Jewelry"),
        "handle": p.identity.handle,
        "status": "active" if offer.availability == "in_stock" else "draft",
        "tags": _build_tags(p),
        "images": [{"src": img.url, "alt": img.alt_text} for img in p.media.images],
    }

    # Variants and options
    if p.relationships and p.relationships.variant_axes:
        out["options"] = [
            {"name": a.name.replace("_", " ").title(), "position": i + 1}
            for i, a in enumerate(p.relationships.variant_axes[:3])
        ]
        # Build single variant from this product (caller merges across SKUs)
        variant: dict[str, Any] = {
            "sku": p.identity.sku,
            "price": str(offer.price.amount),
            "inventory_management": "shopify",
            "inventory_policy": "deny" if offer.availability != "in_stock" else "continue",
        }
        for i, a in enumerate(p.relationships.variant_axes[:3], start=1):
            variant[f"option{i}"] = a.value
        if offer.sale_price:
            variant["compare_at_price"] = str(offer.price.amount)
            variant["price"] = str(offer.sale_price.amount)
        if p.sizing and p.sizing.total_weight_grams:
            variant["weight"] = p.sizing.total_weight_grams
            variant["weight_unit"] = "g"
        out["variants"] = [variant]
    else:
        # Single variant, no options
        v: dict[str, Any] = {
            "sku": p.identity.sku,
            "price": str(offer.price.amount),
            "inventory_management": "shopify",
        }
        if p.sizing and p.sizing.total_weight_grams:
            v["weight"] = p.sizing.total_weight_grams
            v["weight_unit"] = "g"
        out["variants"] = [v]

    return out


def to_shopify_metafields(product: JewelryProduct) -> list[dict]:
    """OJS → list of Shopify metafields to attach to the product.

    The single most important metafield is `ojs.full` (type=json), which
    is the canonical round-trip source-of-truth. The typed scalar
    mirrors below are for Catalog Mapping (sending to Google Shopping)
    and native Shopify Search filtering.
    """
    p = product

    # 1. Canonical OJS JSON metafield — round-trip preservation
    canonical_json = p.model_dump(mode="json", exclude_none=True)
    metafields: list[dict] = [
        {
            "namespace": "ojs",
            "key": "full",
            "type": "json",
            "value": canonical_json,
            "description": "OJS v1.0 canonical jewelry record (source of truth)",
        },
        {
            "namespace": "ojs",
            "key": "version",
            "type": "single_line_text_field",
            "value": p.audit.ojs_version,
        },
        {
            "namespace": "ojs",
            "key": "product_type",
            "type": "single_line_text_field",
            "value": p.product_type if isinstance(p.product_type, str) else p.product_type.value,
        },
    ]

    # 2. Typed scalar mirrors for native Shopify filtering
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        if primary.purity_fineness:
            metafields.append({
                "namespace": "jewelry",
                "key": "metal_fineness",
                "type": "number_integer",
                "value": primary.purity_fineness,
            })
        if primary.color:
            metafields.append({
                "namespace": "jewelry",
                "key": "metal_color",
                "type": "single_line_text_field",
                "value": str(primary.color),
            })
        if primary.type:
            metafields.append({
                "namespace": "jewelry",
                "key": "metal_type",
                "type": "single_line_text_field",
                "value": str(primary.type),
            })

    if p.stones and p.stones.stones:
        center = p.stones.stones[0]
        if center.carat:
            metafields.append({
                "namespace": "jewelry",
                "key": "center_stone_carat",
                "type": "number_decimal",
                "value": center.carat,
            })
        metafields.append({
            "namespace": "jewelry",
            "key": "center_stone_species",
            "type": "single_line_text_field",
            "value": str(center.species),
        })
        if center.cut:
            metafields.append({
                "namespace": "jewelry",
                "key": "center_stone_cut",
                "type": "single_line_text_field",
                "value": str(center.cut),
            })
        if center.color_grade:
            metafields.append({
                "namespace": "jewelry",
                "key": "diamond_color_grade",
                "type": "single_line_text_field",
                "value": str(center.color_grade),
            })
        if center.clarity_grade:
            metafields.append({
                "namespace": "jewelry",
                "key": "diamond_clarity_grade",
                "type": "single_line_text_field",
                "value": str(center.clarity_grade),
            })
        if p.stones.total_carat_weight:
            metafields.append({
                "namespace": "jewelry",
                "key": "total_carat_weight",
                "type": "number_decimal",
                "value": p.stones.total_carat_weight,
            })

    if p.sizing and p.sizing.ring_size:
        if p.sizing.ring_size.iso_mm:
            metafields.append({
                "namespace": "jewelry",
                "key": "ring_size_iso_mm",
                "type": "number_decimal",
                "value": p.sizing.ring_size.iso_mm,
            })

    if p.certification and p.certification.certificates:
        c0 = p.certification.certificates[0]
        metafields.append({
            "namespace": "jewelry",
            "key": "certification_lab",
            "type": "single_line_text_field",
            "value": str(c0.lab),
        })
        metafields.append({
            "namespace": "jewelry",
            "key": "certification_number",
            "type": "single_line_text_field",
            "value": c0.report_number,
        })

    if p.watch:
        metafields.append({
            "namespace": "jewelry",
            "key": "watch_movement",
            "type": "single_line_text_field",
            "value": str(p.watch.movement_type),
        })
        if p.watch.caliber:
            metafields.append({
                "namespace": "jewelry",
                "key": "watch_caliber",
                "type": "single_line_text_field",
                "value": p.watch.caliber,
            })

    if p.media.glb_url:
        metafields.append({
            "namespace": "jewelry",
            "key": "model_3d_glb_url",
            "type": "url",
            "value": p.media.glb_url,
        })

    if p.ai_commerce and p.ai_commerce.semantic_description:
        metafields.append({
            "namespace": "ojs",
            "key": "semantic_description",
            "type": "multi_line_text_field",
            "value": p.ai_commerce.semantic_description,
        })

    return metafields


def _html_description(p: JewelryProduct) -> str:
    """Build a Shopify body_html from OJS description + key specs."""
    parts = [f"<p>{p.identity.description}</p>"]
    if p.stones and p.stones.stones:
        center = p.stones.stones[0]
        spec_bits = []
        if center.carat: spec_bits.append(f"<li>Carat: {center.carat}</li>")
        if center.cut: spec_bits.append(f"<li>Cut: {str(center.cut).replace('_', ' ').title()}</li>")
        if center.color_grade: spec_bits.append(f"<li>Color: {center.color_grade}</li>")
        if center.clarity_grade: spec_bits.append(f"<li>Clarity: {center.clarity_grade}</li>")
        if spec_bits:
            parts.append("<h3>Specifications</h3><ul>" + "".join(spec_bits) + "</ul>")
    if p.certification and p.certification.certificates:
        c = p.certification.certificates[0]
        parts.append(f"<p>Certified by {str(c.lab).upper()}, report #{c.report_number}.</p>")
    return "\n".join(parts)


def _build_tags(p: JewelryProduct) -> str:
    """Build a Shopify tag string (comma-separated) for SEO + filtering."""
    tags: list[str] = []
    pt_value = p.product_type if isinstance(p.product_type, str) else p.product_type.value
    tags.append(pt_value)
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        tags.append(str(primary.type))
        if primary.color: tags.append(str(primary.color))
    if p.stones and p.stones.stones:
        for s in p.stones.stones[:3]:
            tags.append(str(s.species))
    if p.style:
        if p.style.era: tags.append(str(p.style.era))
        for ds in p.style.design_styles[:3]:
            tags.append(str(ds))
    if p.ai_commerce:
        for occ in p.ai_commerce.occasion_tags[:5]:
            tags.append(str(occ))
    return ",".join(t.replace("_", " ") for t in tags)


def from_shopify(product_dict: dict, metafields: list[dict] | None = None) -> dict:
    """Reverse: Shopify Product + metafields → partial OJS-compatible dict.

    Prefers the `ojs.full` json metafield if present (round-trip).
    Falls back to reconstructing from typed metafields + product fields.
    """
    if metafields:
        for mf in metafields:
            if mf.get("namespace") == "ojs" and mf.get("key") == "full":
                # Round-trip: full OJS is stored — just return it
                return mf["value"] if isinstance(mf["value"], dict) else {}

    # Fallback reconstruction (lossy)
    out: dict[str, Any] = {}
    ident: dict[str, Any] = {}
    if "title" in product_dict: ident["title"] = product_dict["title"]
    if "vendor" in product_dict: ident["brand"] = {"name": product_dict["vendor"]}
    if product_dict.get("variants"):
        ident["sku"] = product_dict["variants"][0].get("sku")
    if ident: out["identity"] = ident
    out["_shopify_metafields"] = metafields or []
    return out
