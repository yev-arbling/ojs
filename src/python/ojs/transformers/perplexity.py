"""OJS v1.0 — Perplexity Merchant transformer (bidirectional).

Per Perplexity Merchant Program Terms (perplexity.ai/hub/legal/merchant-program-terms):
"Merchant must request access via email from taz@perplexity.ai and may
receive access to the Perplexity API, an SFTP upload link, or by sharing
CSV files via a designated S3 bucket."

Perplexity inherits the Google Shopping CSV feed format verbatim. This
transformer is a thin wrapper around the GMC transformer with TSV
serialization helpers for CSV upload via SFTP/S3.
"""
from __future__ import annotations

from typing import Any

from ..models import JewelryProduct
from .gmc import to_gmc, from_gmc


def to_perplexity(product: JewelryProduct) -> dict:
    """OJS → Perplexity Merchant product entry.

    Identical to GMC format (Perplexity consumes Google Shopping CSV
    verbatim). The Perplexity-specific delivery channel is SFTP/S3, not
    a different schema.
    """
    out = to_gmc(product)
    # Add Perplexity-specific metadata if known
    return out


def to_perplexity_csv_row(product: JewelryProduct) -> dict[str, str]:
    """OJS → flat dict of strings for CSV row writing.

    Comma-joins list values. Drops product_detail (Perplexity ignores).
    """
    src = to_perplexity(product)
    out: dict[str, str] = {}
    for k, v in src.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                continue  # skip list-of-dict fields (product_detail, q_and_a)
            out[k] = ",".join(str(x) for x in v)
        elif isinstance(v, dict):
            continue  # skip nested dicts
        else:
            out[k] = str(v)
    return out


def from_perplexity(data: dict) -> dict:
    """Perplexity → partial OJS dict. Identical to GMC reverse."""
    return from_gmc(data)
