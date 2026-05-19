"""OJS v1.0 — Model Context Protocol (MCP) transformer.

Emits MCP-compatible tool responses for a jewelry catalog MCP server.
Pattern follows Shopify's Storefront MCP and Catalog MCP servers.

Tools an OJS-backed MCP server typically exposes:

  - search_catalog(query, filters, limit) → list of search results
  - lookup_catalog(sku) → single full product
  - get_product(sku) → ui:// resource card (lightweight, render-friendly)

This module provides the projection functions; the actual MCP server
wraps them in an MCP SDK (e.g. @modelcontextprotocol/sdk).
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct


def to_mcp_search_result(product: JewelryProduct) -> dict:
    """OJS → MCP search-result entry (lightweight summary)."""
    p = product
    offer = p.commerce.offers[p.commerce.primary_offer_index]
    primary_img = next((i.url for i in p.media.images if i.is_primary), p.media.images[0].url)

    metal_str = ""
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        karat = {999: "24k", 916: "22k", 750: "18k", 585: "14k", 417: "10k"}.get(primary.purity_fineness, "")
        parts = []
        if primary.color: parts.append(str(primary.color))
        if karat: parts.append(karat)
        parts.append(str(primary.type))
        metal_str = " ".join(parts).replace("_", " ")

    stone_str = ""
    if p.stones and p.stones.stones:
        s = p.stones.stones[0]
        bits = []
        if s.carat: bits.append(f"{s.carat}ct")
        bits.append(str(s.species))
        if s.cut: bits.append(str(s.cut).replace("_", " "))
        stone_str = " ".join(bits)

    return {
        "sku": p.identity.sku,
        "title": p.identity.title,
        "brand": p.identity.brand.name,
        "price": str(offer.price.amount),
        "currency": offer.price.currency,
        "availability": offer.availability if isinstance(offer.availability, str) else offer.availability.value,
        "url": offer.url,
        "image_url": primary_img,
        "summary": _build_summary(p, metal_str, stone_str),
        "facets": _build_facets(p),
    }


def to_mcp_resource(product: JewelryProduct) -> dict:
    """OJS → MCP ui:// resource card (full product detail for in-chat rendering).

    Returns a structured payload that MCP clients (ChatGPT, Claude
    Desktop) can render in-conversation. Contains the canonical OJS
    JSON plus a rendered human-friendly summary.
    """
    p = product
    offer = p.commerce.offers[p.commerce.primary_offer_index]
    primary_img = next((i.url for i in p.media.images if i.is_primary), p.media.images[0].url)

    # Build a render-friendly "card" structure
    return {
        "type": "resource",
        "uri": f"ojs://product/{p.identity.sku}",
        "mimeType": "application/json",
        "name": p.identity.title,
        "description": p.identity.description,
        "annotations": {
            "audience": ["user", "assistant"],
        },
        "card": {
            "title": p.identity.title,
            "brand": p.identity.brand.name,
            "image_url": primary_img,
            "additional_images": [i.url for i in p.media.images if not i.is_primary][:5],
            "price": str(offer.price.amount),
            "currency": offer.price.currency,
            "url": offer.url,
            "rating": p.reviews.aggregate.rating_value if p.reviews and p.reviews.aggregate else None,
            "review_count": p.reviews.aggregate.review_count if p.reviews and p.reviews.aggregate else None,
            "specs": _build_specs(p),
        },
        "data": p.model_dump(mode="json", exclude_none=True),
    }


def to_mcp_tool_definitions() -> list[dict]:
    """Return MCP tool definitions (JSON-Schema) for an OJS catalog server.

    These can be returned from an MCP server's `tools/list` endpoint.
    """
    return [
        {
            "name": "search_catalog",
            "description": "Search the jewelry catalog by free text and structured filters.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Free-text query"},
                    "product_type": {"type": "string", "description": "Filter by product_type"},
                    "max_price": {"type": "number"},
                    "metal_type": {"type": "string"},
                    "stone_species": {"type": "string"},
                    "limit": {"type": "integer", "default": 10, "maximum": 50},
                },
                "required": ["query"],
            },
        },
        {
            "name": "lookup_catalog",
            "description": "Look up a single product by its SKU.",
            "inputSchema": {
                "type": "object",
                "properties": {"sku": {"type": "string"}},
                "required": ["sku"],
            },
        },
        {
            "name": "get_product",
            "description": "Get full OJS product detail for in-chat rendering.",
            "inputSchema": {
                "type": "object",
                "properties": {"sku": {"type": "string"}},
                "required": ["sku"],
            },
        },
    ]


def _build_summary(p: JewelryProduct, metal_str: str, stone_str: str) -> str:
    bits = []
    if stone_str: bits.append(stone_str)
    if metal_str: bits.append(metal_str)
    pt_value = p.product_type if isinstance(p.product_type, str) else p.product_type.value
    bits.append(pt_value.replace("_", " "))
    return " ".join(bits).strip()


def _build_facets(p: JewelryProduct) -> dict[str, Any]:
    """Build structured facets for AI agents to filter on."""
    f: dict[str, Any] = {}
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        f["metal_type"] = str(primary.type)
        if primary.color: f["metal_color"] = str(primary.color)
        if primary.purity_fineness: f["metal_fineness"] = primary.purity_fineness
    if p.stones and p.stones.stones:
        s = p.stones.stones[0]
        f["stone_species"] = str(s.species)
        if s.carat: f["stone_carat"] = s.carat
        if s.cut: f["stone_cut"] = str(s.cut)
        if p.stones.total_carat_weight: f["total_carat_weight"] = p.stones.total_carat_weight
    if p.style and p.style.era: f["era"] = str(p.style.era)
    if p.ai_commerce and p.ai_commerce.price_tier:
        f["price_tier"] = str(p.ai_commerce.price_tier)
    return f


def _build_specs(p: JewelryProduct) -> list[dict[str, Any]]:
    """Build human-readable spec bullets for the card."""
    specs: list[dict[str, Any]] = []
    if p.metals and p.metals.compositions:
        primary = next((c for c in p.metals.compositions if c.primary), p.metals.compositions[0])
        if primary.type:
            specs.append({"label": "Metal", "value": str(primary.type).replace("_", " ").title()})
        if primary.purity_fineness:
            karat = {999: "24k", 916: "22k", 750: "18k", 585: "14k", 417: "10k"}.get(primary.purity_fineness)
            specs.append({"label": "Purity", "value": karat or f"{primary.purity_fineness}/1000"})
    if p.stones and p.stones.stones:
        s = p.stones.stones[0]
        specs.append({"label": "Stone", "value": str(s.species).replace("_", " ").title()})
        if s.carat: specs.append({"label": "Carat", "value": f"{s.carat}ct"})
        if s.cut: specs.append({"label": "Cut", "value": str(s.cut).replace("_", " ").title()})
        if s.color_grade: specs.append({"label": "Color", "value": s.color_grade})
        if s.clarity_grade: specs.append({"label": "Clarity", "value": s.clarity_grade})
    if p.sizing and p.sizing.ring_size and p.sizing.ring_size.us_ca:
        specs.append({"label": "Size", "value": f"US {p.sizing.ring_size.us_ca}"})
    if p.certification and p.certification.certificates:
        c = p.certification.certificates[0]
        specs.append({"label": "Certified", "value": f"{str(c.lab).upper()} #{c.report_number}"})
    return specs
