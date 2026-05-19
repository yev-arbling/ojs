"""OJS v1.0 — Platform transformers (bidirectional).

7 platform mappers between the canonical OJS model and external formats:

  schema_org → JSON-LD Product (W3C, all AI agents that parse PDP HTML)
  gmc        → Google Merchant Center feed row (Shopping, AI Overviews)
  acp        → Agentic Commerce Protocol 2026-04-17 (ChatGPT, Operator)
  ucp        → Google Universal Commerce Protocol (AI Mode buy button)
  perplexity → Perplexity Merchant feed (GMC-compatible CSV via SFTP/S3)
  shopify    → Shopify Product + metafields (canonical ojs.full + scalars)
  mcp        → Model Context Protocol resources & tool definitions

Each module exposes flat functions:
  to_<platform>(product: JewelryProduct) -> dict
  from_<platform>(data: dict) -> dict  (partial OJS dict)

The OJS canonical model is source of truth. Transformers are LOSSY in
both directions because no single platform supports all 280 OJS fields.
"""
from .acp import to_acp, from_acp
from .gmc import to_gmc, from_gmc
from .mcp import to_mcp_search_result, to_mcp_resource, to_mcp_tool_definitions
from .perplexity import to_perplexity, to_perplexity_csv_row, from_perplexity
from .schema_org import to_schema_org, from_schema_org
from .shopify import to_shopify_product, to_shopify_metafields, from_shopify
from .ucp import to_ucp, from_ucp

__all__ = [
    "to_schema_org", "from_schema_org",
    "to_gmc", "from_gmc",
    "to_acp", "from_acp",
    "to_ucp", "from_ucp",
    "to_perplexity", "to_perplexity_csv_row", "from_perplexity",
    "to_shopify_product", "to_shopify_metafields", "from_shopify",
    "to_mcp_search_result", "to_mcp_resource", "to_mcp_tool_definitions",
]
