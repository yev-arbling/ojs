"""Open Jewelry Schema (OJS) v1.0 — Python reference implementation.

OJS is an open-source jewelry data schema for AI-driven commerce.
21 domains covering ~280 fields, dual-published as JSON Schema and JSON-LD.

License: CC0 1.0 (vocabulary) + Apache 2.0 (this implementation).
Repo: https://github.com/openjewelryschema/ojs
Docs: https://schema.openjewelryschema.org/v1/

Quick start:
    from ojs.models import JewelryProduct, ProductType
    from ojs.transformers import to_schema_org, to_gmc, to_acp

    product = JewelryProduct(product_type=ProductType.RING, ...)
    schema_org_jsonld = to_schema_org(product)
    gmc_row = to_gmc(product)
    acp_row = to_acp(product)
"""
from .models import JewelryProduct, ProductType, OJS_VERSION

__version__ = OJS_VERSION
__all__ = ["JewelryProduct", "ProductType", "OJS_VERSION"]
