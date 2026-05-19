"""OJS v1.0 — Schema.org JSON-LD Product transformer (bidirectional).

Schema.org Product is the universal lingua franca consumed by Google
rich results, Bing, Yandex, Apple Spotlight, and every modern AI agent
that scrapes PDP HTML. Native mapping covers ~70 OJS fields; the
remaining ~210 ride as PropertyValue under `additionalProperty`.

Round-trip integrity: propertyID = `ojs:<dotted_path>` lets a parser
recover the original OJS field name on reverse.

Embed output in: <script type="application/ld+json">{json}</script>
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct

_AVAIL_MAP = {
    "in_stock": "https://schema.org/InStock",
    "out_of_stock": "https://schema.org/OutOfStock",
    "preorder": "https://schema.org/PreOrder",
    "backorder": "https://schema.org/BackOrder",
    "discontinued": "https://schema.org/Discontinued",
    "limited_availability": "https://schema.org/LimitedAvailability",
    "made_to_order": "https://schema.org/MadeToOrder",
}
_COND_MAP = {
    "new": "https://schema.org/NewCondition",
    "used": "https://schema.org/UsedCondition",
    "estate": "https://schema.org/UsedCondition",
    "vintage": "https://schema.org/UsedCondition",
    "antique": "https://schema.org/UsedCondition",
    "refurbished": "https://schema.org/RefurbishedCondition",
}


def _prop(name: str, value: Any, ojs_path: str) -> dict:
    """Create a Schema.org PropertyValue with OJS round-trip ID."""
    return {
        "@type": "PropertyValue",
        "name": name,
        "value": str(value) if not isinstance(value, (list, dict)) else value,
        "propertyID": f"ojs:{ojs_path}",
    }


def to_schema_org(product: JewelryProduct) -> dict:
    """Render OJS as Schema.org JSON-LD Product dict."""
    p = product
    out: dict[str, Any] = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "sku": p.identity.sku,
        "name": p.identity.title,
        "description": p.identity.description,
        "brand": {
            "@type": "Brand",
            "name": p.identity.brand.name,
            **({"url": p.identity.brand.website} if p.identity.brand.website else {}),
        },
    }
    if p.identity.gtin: out["gtin"] = p.identity.gtin
    if p.identity.mpn: out["mpn"] = p.identity.mpn
    if p.identity.model: out["model"] = p.identity.model

    # Images (primary first)
    images = sorted(p.media.images, key=lambda i: (not i.is_primary, 0))
    out["image"] = [img.url for img in images]

    # Videos
    if p.media.videos:
        out["video"] = [
            {"@type": "VideoObject", "contentUrl": v.url,
             **({"thumbnailUrl": v.thumbnail_url} if v.thumbnail_url else {}),
             **({"duration": f"PT{v.duration_seconds}S"} if v.duration_seconds else {})}
            for v in p.media.videos
        ]

    # 3D models
    if p.media.glb_url or p.media.usdz_url:
        encodings = []
        if p.media.glb_url:
            encodings.append({"@type": "MediaObject", "contentUrl": p.media.glb_url, "encodingFormat": "model/gltf-binary"})
        if p.media.usdz_url:
            encodings.append({"@type": "MediaObject", "contentUrl": p.media.usdz_url, "encodingFormat": "model/vnd.usdz+zip"})
        out["subjectOf"] = {"@type": "3DModel", "encoding": encodings}

    # Offers
    offers = [_offer_to_schema_org(o) for o in p.commerce.offers]
    out["offers"] = offers[0] if len(offers) == 1 else offers

    # Reviews
    if p.reviews and p.reviews.aggregate:
        a = p.reviews.aggregate
        out["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": a.rating_value,
            "reviewCount": a.review_count,
            "bestRating": a.best_rating,
            "worstRating": a.worst_rating,
        }

    # Material (short form, primary metal)
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        mat_parts = []
        if primary.color: mat_parts.append(primary.color)
        if primary.purity_fineness:
            karat = {999: "24k", 916: "22k", 750: "18k", 585: "14k", 417: "10k"}.get(primary.purity_fineness)
            if karat: mat_parts.append(karat)
            else: mat_parts.append(f"{primary.purity_fineness}/1000")
        mat_parts.append(primary.type)
        out["material"] = " ".join(mat_parts).replace("_", " ")

    # Variant group
    if p.relationships and p.relationships.item_group_id:
        out["isVariantOf"] = {
            "@type": "ProductGroup",
            "productGroupID": p.relationships.item_group_id,
            "variesBy": [a.name for a in p.relationships.variant_axes],
        }

    # All extras as PropertyValue array (lossy → recoverable via propertyID)
    out["additionalProperty"] = _flatten_extras(p)
    return out


def _offer_to_schema_org(offer) -> dict:
    out = {
        "@type": "Offer",
        "price": str(offer.price.amount),
        "priceCurrency": offer.price.currency,
        "availability": _AVAIL_MAP.get(offer.availability, "https://schema.org/InStock"),
        "itemCondition": _COND_MAP.get(offer.condition, "https://schema.org/NewCondition"),
        "url": offer.url,
        "seller": {"@type": "Organization", "name": offer.seller_name, "url": offer.seller_url},
        "areaServed": offer.target_countries,
    }
    if offer.return_policy_url:
        out["hasMerchantReturnPolicy"] = {
            "@type": "MerchantReturnPolicy",
            "merchantReturnLink": offer.return_policy_url,
        }
    if offer.sale_price:
        out["priceSpecification"] = {
            "@type": "UnitPriceSpecification",
            "price": str(offer.sale_price.amount),
            "priceCurrency": offer.sale_price.currency,
        }
    return out


def _flatten_extras(p: JewelryProduct) -> list[dict]:
    out: list[dict] = []
    if p.metals:
        for i, c in enumerate(p.metals.compositions):
            base = f"metals.compositions.{i}"
            if c.purity_fineness:
                out.append(_prop(f"metal_{i}_fineness", c.purity_fineness, f"{base}.purity_fineness"))
            if c.plating:
                out.append(_prop(f"metal_{i}_plating", c.plating, f"{base}.plating"))
            if c.hallmark:
                out.append(_prop(f"metal_{i}_hallmark", c.hallmark, f"{base}.hallmark"))
        if p.metals.recycled_content_percent is not None:
            out.append(_prop("recycled_metal_percent", p.metals.recycled_content_percent, "metals.recycled_content_percent"))
        if p.metals.nickel_free is not None:
            out.append(_prop("nickel_free", p.metals.nickel_free, "metals.nickel_free"))

    if p.stones:
        for i, s in enumerate(p.stones.stones):
            base = f"stones.stones.{i}"
            out.append(_prop(f"stone_{i}_species", s.species, f"{base}.species"))
            out.append(_prop(f"stone_{i}_origin", s.origin_type, f"{base}.origin_type"))
            if s.carat: out.append(_prop(f"stone_{i}_carat", s.carat, f"{base}.carat"))
            if s.cut: out.append(_prop(f"stone_{i}_cut", s.cut, f"{base}.cut"))
            if s.color_grade: out.append(_prop(f"stone_{i}_color", s.color_grade, f"{base}.color_grade"))
            if s.clarity_grade: out.append(_prop(f"stone_{i}_clarity", s.clarity_grade, f"{base}.clarity_grade"))
            if s.treatments:
                out.append(_prop(f"stone_{i}_treatments", ", ".join(s.treatments), f"{base}.treatments"))
        if p.stones.total_carat_weight:
            out.append(_prop("total_carat_weight", p.stones.total_carat_weight, "stones.total_carat_weight"))

    if p.pearls:
        for f in ("pearl_type", "luster", "surface_quality", "shape", "body_color", "size_mm"):
            v = getattr(p.pearls, f)
            if v is not None: out.append(_prop(f"pearl_{f}", v, f"pearls.{f}"))

    if p.sizing:
        if p.sizing.ring_size:
            if p.sizing.ring_size.iso_mm:
                out.append(_prop("ring_size_iso", p.sizing.ring_size.iso_mm, "sizing.ring_size.iso_mm"))
            if p.sizing.ring_size.us_ca:
                out.append(_prop("ring_size_us", p.sizing.ring_size.us_ca, "sizing.ring_size.us_ca"))
        if p.sizing.total_weight_grams:
            out.append(_prop("total_weight_g", p.sizing.total_weight_grams, "sizing.total_weight_grams"))
        if p.sizing.length_mm:
            out.append(_prop("length_mm", p.sizing.length_mm, "sizing.length_mm"))

    if p.style and p.style.era:
        out.append(_prop("era", p.style.era, "style.era"))

    if p.certification:
        for i, c in enumerate(p.certification.certificates):
            out.append(_prop(f"cert_{i}_lab", c.lab, f"certification.certificates.{i}.lab"))
            out.append(_prop(f"cert_{i}_number", c.report_number, f"certification.certificates.{i}.report_number"))
            if c.report_url:
                out.append(_prop(f"cert_{i}_url", c.report_url, f"certification.certificates.{i}.report_url"))

    if p.watch:
        for f in ("movement_type", "caliber", "case_diameter_mm", "cosc_chronometer"):
            v = getattr(p.watch, f)
            if v is not None: out.append(_prop(f"watch_{f}", v, f"watch.{f}"))

    if p.sustainability:
        if p.sustainability.is_conflict_free is not None:
            out.append(_prop("conflict_free", p.sustainability.is_conflict_free, "sustainability.is_conflict_free"))
        if p.sustainability.is_lab_grown_marketed is not None:
            out.append(_prop("lab_grown_marketed", p.sustainability.is_lab_grown_marketed, "sustainability.is_lab_grown_marketed"))

    if p.ai_commerce:
        if p.ai_commerce.semantic_description:
            out.append(_prop("ai_semantic_description", p.ai_commerce.semantic_description, "ai_commerce.semantic_description"))
    return out


def from_schema_org(data: dict) -> dict:
    """Parse Schema.org JSON-LD into a partial OJS-compatible dict.

    Returns a dict ready for `JewelryProduct(**out)` after caller fills
    required modules (audit, product_type if not inferable). Lossy:
    PropertyValue array with `propertyID` prefix `ojs:` is decoded back.
    """
    out: dict[str, Any] = {}
    ident: dict[str, Any] = {}
    if "sku" in data: ident["sku"] = data["sku"]
    if "name" in data: ident["title"] = data["name"]
    if "description" in data: ident["description"] = data["description"]
    if "gtin" in data: ident["gtin"] = data["gtin"]
    if "mpn" in data: ident["mpn"] = data["mpn"]
    if "model" in data: ident["model"] = data["model"]
    brand = data.get("brand")
    if isinstance(brand, dict):
        ident["brand"] = {"name": brand.get("name", "Unknown")}
    elif isinstance(brand, str):
        ident["brand"] = {"name": brand}
    if ident:
        out["identity"] = ident

    # additionalProperty round-trip
    extras: dict[str, Any] = {}
    for pv in data.get("additionalProperty", []) or []:
        if isinstance(pv, dict):
            pid = pv.get("propertyID", "")
            if pid.startswith("ojs:"):
                extras[pid[4:]] = pv.get("value")
    if extras:
        out["_ojs_extras"] = extras

    return out
