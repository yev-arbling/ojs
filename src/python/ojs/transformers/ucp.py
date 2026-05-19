"""OJS v1.0 — Google UCP (Universal Commerce Protocol) transformer (bidirectional).

UCP launched at NRF 2026 (Jan 11, 2026), 20+ retailers. UCP is a
checkout/discovery protocol layered on existing GMC feeds — NOT a
separate feed format. The product data UCP exchanges is retrieved from
the merchant's GMC feed. UCP-specific addition:

  - `native_commerce`: true → triggers "Buy" button on AI Mode results
  - `.well-known/ucp` profile published by merchant

OUTPUT: GMC dict + UCP-specific flags. Caller publishes via existing
GMC pipeline; UCP discovery is via the /.well-known/ucp endpoint.
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct
from .gmc import to_gmc, from_gmc


def to_ucp(product: JewelryProduct) -> dict:
    """OJS → UCP-compatible product entry.

    UCP = GMC + native_commerce flag + return policy + checkout URL.
    """
    out = to_gmc(product)
    offer = product.commerce.offers[product.commerce.primary_offer_index]
    # UCP-specific
    out["native_commerce"] = bool(offer.return_policy_url and offer.seller_url)
    if offer.return_policy_url:
        out["return_policy_url"] = offer.return_policy_url
    out["seller_url"] = offer.seller_url
    out["seller_name"] = offer.seller_name
    return out


def from_ucp(data: dict) -> dict:
    """UCP → partial OJS dict. Currently identical to GMC reverse."""
    return from_gmc(data)
