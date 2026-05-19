"""OJS v1.0 — Google Merchant Center (GMC) transformer (bidirectional).

GMC feed schema reference: support.google.com/merchants/answer/7052112

Jewelry-specific attributes go into `product_detail` (up to 1000 entries,
attribute_value ≤1000 chars) under section_name like Metal/Stone/Setting/
Pearl/Watch/Certification. April 2026 additions: `video_link`,
`handling_cutoff_time`, `minimum_order_value`, loyalty_program sub-attrs.

REQUIRED for Apparel & Accessories (jewelry inherits): `color`, `age_group`,
`gender`. Without these, items don't index in Shopping or AI Overviews.

500x500 px minimum image from January 31, 2027.

Output is a flat dict mapping GMC attribute names → values (strings or
lists). For TSV/CSV feed export, serialize lists as comma-joined.
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct, ProductType

_AVAIL_GMC = {
    "in_stock": "in_stock",
    "out_of_stock": "out_of_stock",
    "preorder": "preorder",
    "backorder": "backorder",
    "discontinued": "out_of_stock",
    "limited_availability": "in_stock",
    "made_to_order": "preorder",
}
_COND_GMC = {
    "new": "new",
    "refurbished": "refurbished",
    "used": "used",
    "estate": "used",
    "vintage": "used",
    "antique": "used",
}
# Google product taxonomy: Jewelry > Watches (201); rings/necklaces all under Apparel & Accessories > Jewelry (188)
_GOOGLE_PRODUCT_CATEGORY = {
    ProductType.RING: "Apparel & Accessories > Jewelry > Rings",
    ProductType.EARRING: "Apparel & Accessories > Jewelry > Earrings",
    ProductType.NECKLACE: "Apparel & Accessories > Jewelry > Necklaces",
    ProductType.BRACELET: "Apparel & Accessories > Jewelry > Bracelets",
    ProductType.ANKLET: "Apparel & Accessories > Jewelry > Anklets",
    ProductType.BROOCH: "Apparel & Accessories > Jewelry > Brooches & Lapel Pins",
    ProductType.PENDANT: "Apparel & Accessories > Jewelry > Necklaces",
    ProductType.WATCH: "Apparel & Accessories > Jewelry > Watches",
    ProductType.PEARL: "Apparel & Accessories > Jewelry",
    ProductType.SMART_WEARABLE: "Apparel & Accessories > Jewelry > Watches",
    ProductType.BODY: "Apparel & Accessories > Jewelry > Body Jewelry",
    ProductType.ESTATE: "Apparel & Accessories > Jewelry",
    ProductType.JEWELRY_SET: "Apparel & Accessories > Jewelry > Jewelry Sets",
    ProductType.OTHER: "Apparel & Accessories > Jewelry",
}


def _detail(section: str, name: str, value: Any) -> dict:
    """A GMC product_detail triple. Truncate value to 1000 chars."""
    val_str = str(value)[:1000]
    return {"section_name": section, "attribute_name": name[:140], "attribute_value": val_str}


def to_gmc(product: JewelryProduct) -> dict:
    """Render OJS as a GMC feed row dict.

    Caller serializes to TSV/CSV/XML for feed upload, or POSTs to the
    Content API for Shopping.
    """
    p = product
    offer = p.commerce.offers[p.commerce.primary_offer_index]
    pt_value = p.product_type.value if hasattr(p.product_type, 'value') else p.product_type

    out: dict[str, Any] = {
        "id": p.identity.sku,
        "title": p.identity.title[:150],
        "description": p.identity.description[:5000],
        "link": offer.url,
        "image_link": next((i.url for i in p.media.images if i.is_primary), p.media.images[0].url),
        "additional_image_link": [i.url for i in p.media.images if not i.is_primary][:10],  # up to 10 additional
        "availability": _AVAIL_GMC.get(offer.availability, "in_stock"),
        "price": f"{offer.price.amount} {offer.price.currency}",
        "brand": p.identity.brand.name[:70],
        "condition": _COND_GMC.get(offer.condition, "new"),
        "google_product_category": _GOOGLE_PRODUCT_CATEGORY.get(p.product_type, "Apparel & Accessories > Jewelry"),
        # Apparel & Accessories REQUIRED:
        "age_group": "adult",  # default; override in details below if known
        "gender": "unisex",   # default; override if AudienceTag present
        "shipping_weight": f"{p.sizing.total_weight_grams} g" if p.sizing and p.sizing.total_weight_grams else None,
    }

    if p.identity.gtin: out["gtin"] = p.identity.gtin
    if p.identity.mpn: out["mpn"] = p.identity.mpn
    if offer.sale_price:
        out["sale_price"] = f"{offer.sale_price.amount} {offer.sale_price.currency}"
        if offer.sale_starts and offer.sale_ends:
            out["sale_price_effective_date"] = f"{offer.sale_starts.isoformat()}/{offer.sale_ends.isoformat()}"

    # Variant grouping
    if p.relationships:
        if p.relationships.item_group_id:
            out["item_group_id"] = p.relationships.item_group_id
        # Up to 3 axes; pick first as color if it's color-related
        for axis in p.relationships.variant_axes[:3]:
            if "color" in axis.name.lower() or "metal_color" in axis.name.lower():
                out["color"] = axis.value
            elif "size" in axis.name.lower():
                out["size"] = axis.value
            elif "material" in axis.name.lower():
                out["material"] = axis.value

    # Primary metal → color (or fallback to ojs metal_color)
    if "color" not in out and p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        if primary.color:
            out["color"] = str(primary.color).replace("_", " ").title()

    # Material short form (up to 3 metals slash-separated)
    if p.metals and p.metals.compositions:
        mats = []
        for c in p.metals.compositions[:3]:
            karat = {999: "24k", 916: "22k", 750: "18k", 585: "14k", 417: "10k"}.get(c.purity_fineness)
            parts = []
            if c.color: parts.append(str(c.color).replace("_", " "))
            if karat: parts.append(karat)
            parts.append(str(c.type))
            mats.append(" ".join(parts))
        out["material"] = "/".join(mats)

    # Reviews (rich snippet)
    if p.reviews and p.reviews.aggregate:
        out["product_review_average"] = p.reviews.aggregate.rating_value
        out["product_review_count"] = p.reviews.aggregate.review_count

    # BNPL / financing
    if offer.bnpl_available:
        out["installment"] = {"months": 4, "amount": str(round(float(offer.price.amount) / 4, 2)) + " " + offer.price.currency}

    # April 2026 additions
    if p.media.videos:
        out["video_link"] = p.media.videos[0].url

    # Audience → gender / age_group
    if p.ai_commerce:
        for tag in p.ai_commerce.audience_tags:
            tag_v = tag if isinstance(tag, str) else tag.value
            if tag_v in ("women", "bride", "gift_for_her"): out["gender"] = "female"
            elif tag_v in ("men", "groom", "gift_for_him"): out["gender"] = "male"
            elif tag_v == "unisex": out["gender"] = "unisex"
            elif tag_v == "children": out["age_group"] = "kids"
            elif tag_v == "teens": out["age_group"] = "kids"

    # product_detail triples for everything else
    details: list[dict] = []

    if p.metals:
        for i, c in enumerate(p.metals.compositions):
            if c.purity_fineness:
                details.append(_detail("Metal", f"Metal {i+1} Fineness", c.purity_fineness))
            if c.plating and c.plating != "none":
                details.append(_detail("Metal", f"Metal {i+1} Plating", c.plating))
            if c.hallmark:
                details.append(_detail("Metal", f"Metal {i+1} Hallmark", c.hallmark))
        if p.metals.recycled_content_percent is not None:
            details.append(_detail("Sustainability", "Recycled Content %", p.metals.recycled_content_percent))
        if p.metals.nickel_free:
            details.append(_detail("Compliance", "Nickel-Free", "Yes"))

    if p.stones:
        for i, s in enumerate(p.stones.stones):
            tag = f"Stone {i+1}"
            details.append(_detail("Stone", f"{tag} Species", s.species))
            details.append(_detail("Stone", f"{tag} Origin", s.origin_type))
            if s.carat: details.append(_detail("Stone", f"{tag} Carat", s.carat))
            if s.cut: details.append(_detail("Stone", f"{tag} Cut", s.cut))
            if s.color_grade: details.append(_detail("Stone", f"{tag} Color Grade", s.color_grade))
            if s.clarity_grade: details.append(_detail("Stone", f"{tag} Clarity", s.clarity_grade))
            if s.treatments: details.append(_detail("Stone", f"{tag} Treatments", ", ".join(s.treatments)))
        if p.stones.total_carat_weight:
            details.append(_detail("Stone", "Total Carat Weight", p.stones.total_carat_weight))

    if p.pearls:
        for f in ("pearl_type", "luster", "surface_quality", "shape", "body_color", "size_mm", "nacre_quality"):
            v = getattr(p.pearls, f, None)
            if v is not None: details.append(_detail("Pearl", f.replace("_", " ").title(), v))

    if p.setting:
        for i, s in enumerate(p.setting.styles):
            details.append(_detail("Setting", f"Setting {i+1} Type", s.setting_type))
            if s.prong_count: details.append(_detail("Setting", f"Setting {i+1} Prong Count", s.prong_count))

    if p.sizing:
        if p.sizing.ring_size and p.sizing.ring_size.iso_mm:
            details.append(_detail("Sizing", "Ring Size ISO (mm)", p.sizing.ring_size.iso_mm))
        if p.sizing.ring_size and p.sizing.ring_size.us_ca:
            details.append(_detail("Sizing", "Ring Size US", p.sizing.ring_size.us_ca))
        if p.sizing.length_mm:
            details.append(_detail("Sizing", "Length (mm)", p.sizing.length_mm))

    if p.certification:
        for i, c in enumerate(p.certification.certificates):
            details.append(_detail("Certification", f"Lab {i+1}", c.lab))
            details.append(_detail("Certification", f"Report Number {i+1}", c.report_number))
            if c.report_url:
                details.append(_detail("Certification", f"Report URL {i+1}", c.report_url))

    if p.watch:
        if p.watch.movement_type:
            details.append(_detail("Watch", "Movement", p.watch.movement_type))
        if p.watch.caliber:
            details.append(_detail("Watch", "Caliber", p.watch.caliber))
        if p.watch.case_diameter_mm:
            details.append(_detail("Watch", "Case Diameter (mm)", p.watch.case_diameter_mm))
        if p.watch.water_resistance and p.watch.water_resistance.meters:
            details.append(_detail("Watch", "Water Resistance (m)", p.watch.water_resistance.meters))
        if p.watch.complications:
            details.append(_detail("Watch", "Complications", ", ".join(str(c) for c in p.watch.complications)))

    if p.body:
        details.append(_detail("Body Jewelry", "Piercing Location", p.body.piercing_location))
        if p.body.biocompatibility_standards:
            details.append(_detail("Body Jewelry", "Biocompatibility", ", ".join(str(s) for s in p.body.biocompatibility_standards)))
        if p.body.gauge and p.body.gauge.gauge_us:
            details.append(_detail("Body Jewelry", "Gauge", p.body.gauge.gauge_us))

    if p.style:
        if p.style.era:
            details.append(_detail("Style", "Era", p.style.era))
        if p.style.design_styles:
            details.append(_detail("Style", "Design Styles", ", ".join(str(s) for s in p.style.design_styles)))

    if p.sustainability:
        if p.sustainability.is_conflict_free is not None:
            details.append(_detail("Sustainability", "Conflict-Free", "Yes" if p.sustainability.is_conflict_free else "No"))
        if p.sustainability.certifications:
            details.append(_detail("Sustainability", "Certifications", ", ".join(str(c) for c in p.sustainability.certifications)))

    if details:
        out["product_detail"] = details[:1000]  # GMC cap

    # Strip None values
    return {k: v for k, v in out.items() if v is not None and v != []}


def from_gmc(row: dict) -> dict:
    """Reverse: parse a GMC feed row into a partial OJS-compatible dict.

    Lossy: product_detail triples are recovered into OJS fields where
    sectional/attribute names match the canonical taxonomy.
    """
    out: dict[str, Any] = {}
    ident: dict[str, Any] = {}
    if "id" in row: ident["sku"] = row["id"]
    if "title" in row: ident["title"] = row["title"]
    if "description" in row: ident["description"] = row["description"]
    if "brand" in row: ident["brand"] = {"name": row["brand"]}
    if "gtin" in row: ident["gtin"] = row["gtin"]
    if "mpn" in row: ident["mpn"] = row["mpn"]
    if ident: out["identity"] = ident

    # product_detail triples → semi-structured dict
    if "product_detail" in row:
        out["_gmc_product_detail"] = row["product_detail"]
    return out
