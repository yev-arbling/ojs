"""OJS v1.0 — Core test suite.

Run from repo root:
    pytest tests/

Covers:
  - Pydantic model composition & validation
  - Sub-vertical discriminator enforcement
  - JSON Schema generation
  - All 7 transformers (export side)
  - Round-trip integrity for Shopify (via canonical ojs.full metafield)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

from ojs.models import (  # noqa: E402
    AICommerceModule, AggregateRating, Audience, Availability, AuditMetadata,
    Brand, CommerceModule, IdentityModule, ImageAsset, ImageRole,
    JewelryProduct, MediaModule, MetalComposition, MetalsModule, Occasion,
    Offer, PearlsModule, PriceTier, ProductType, ReviewsModule, RingSize,
    SettingModule, SettingStyle, SizingModule, SourceSystem, Stone,
    StonesModule, WatchModule,
)
from ojs.transformers import (  # noqa: E402
    to_acp, to_gmc, to_mcp_resource, to_perplexity, to_schema_org,
    to_shopify_metafields, to_shopify_product, to_ucp,
    from_shopify,
)


# ============================================================
# Fixtures
# ============================================================


def _basic_ring() -> JewelryProduct:
    """Minimal valid ring product."""
    return JewelryProduct(
        product_type=ProductType.RING,
        audit=AuditMetadata(
            created_at=datetime.now(timezone.utc),
            source_system=SourceSystem.MANUAL,
        ),
        identity=IdentityModule(
            sku="TEST-RING-001",
            title="Test Engagement Ring",
            description="Test description for validation purposes",
            brand=Brand(name="Test Brand"),
        ),
        commerce=CommerceModule(offers=[Offer(
            price={"amount": "5000.00", "currency": "USD"},
            availability=Availability.IN_STOCK,
            url="https://example.com/p/1",
            target_countries=["US"],
            seller_name="Test Seller",
            seller_url="https://example.com",
            return_policy_url="https://example.com/returns",
        )]),
        media=MediaModule(images=[
            ImageAsset(url="https://example.com/i.jpg", is_primary=True, role=ImageRole.PRIMARY),
        ]),
    )


def _full_ring() -> JewelryProduct:
    """Fully-loaded ring with metals, stones, setting, reviews, AI commerce."""
    p = _basic_ring()
    p.metals = MetalsModule(compositions=[
        MetalComposition(type="platinum", purity_fineness=950, primary=True),
    ])
    p.stones = StonesModule(
        stones=[Stone(
            species="diamond", origin_type="natural", carat=1.5,
            cut="round_brilliant", color_grade="F", clarity_grade="VS1",
        )],
        total_carat_weight=1.5,
    )
    p.setting = SettingModule(styles=[
        SettingStyle(style_id="c", setting_type="prong", prong_count=6),
    ])
    p.sizing = SizingModule(ring_size=RingSize(iso_mm=54.0, us_ca=7.0))
    p.reviews = ReviewsModule(aggregate=AggregateRating(rating_value=4.7, review_count=128))
    p.ai_commerce = AICommerceModule(
        semantic_description="Test semantic description for AI agents indexing this product.",
        query_keywords=["test engagement ring"],
        occasion_tags=[Occasion.ENGAGEMENT],
        audience_tags=[Audience.WOMEN],
        price_tier=PriceTier.AFFORDABLE_LUXURY,
    )
    return p


# ============================================================
# Model tests
# ============================================================


class TestModels:
    def test_basic_ring_validates(self):
        p = _basic_ring()
        assert p.product_type == "ring"
        assert p.identity.sku == "TEST-RING-001"

    def test_full_ring_validates(self):
        p = _full_ring()
        assert p.metals.compositions[0].purity_fineness == 950
        assert p.stones.stones[0].color_grade == "F"

    def test_missing_required_module_fails(self):
        with pytest.raises(Exception):
            JewelryProduct(
                product_type=ProductType.RING,
                audit=AuditMetadata(
                    created_at=datetime.now(timezone.utc),
                    source_system=SourceSystem.MANUAL,
                ),
                identity=IdentityModule(
                    sku="X", title="X", description="X test",
                    brand=Brand(name="X"),
                ),
                # Missing commerce → should fail
                media=MediaModule(images=[ImageAsset(url="https://x/i.jpg", is_primary=True)]),
            )

    def test_invalid_gtin_rejected(self):
        with pytest.raises(Exception):
            IdentityModule(
                sku="X", title="X", description="X test",
                brand=Brand(name="X"),
                gtin="123",  # Not 8/12/13/14 digits
            )

    def test_negative_price_rejected(self):
        with pytest.raises(Exception):
            Offer(
                price={"amount": "-10", "currency": "USD"},
                availability=Availability.IN_STOCK,
                url="https://x/p", target_countries=["US"],
                seller_name="X", seller_url="https://x",
            )


# ============================================================
# Discriminator tests
# ============================================================


class TestDiscriminators:
    def test_pearl_requires_pearls_module(self):
        with pytest.raises(Exception, match="pearl.*pearls"):
            p = _basic_ring()
            JewelryProduct(
                product_type=ProductType.PEARL,
                audit=p.audit, identity=p.identity,
                commerce=p.commerce, media=p.media,
                # No pearls module → should raise
            )

    def test_pearl_with_pearls_module_succeeds(self):
        p = _basic_ring()
        prod = JewelryProduct(
            product_type=ProductType.PEARL,
            audit=p.audit, identity=p.identity,
            commerce=p.commerce, media=p.media,
            pearls=PearlsModule(
                pearl_type="akoya", luster="excellent",
                surface_quality="clean", shape="round",
                body_color="white", size_mm=8.0,
            ),
        )
        assert prod.pearls.pearl_type == "akoya"

    def test_watch_requires_watch_module(self):
        with pytest.raises(Exception, match="watch.*watch"):
            p = _basic_ring()
            JewelryProduct(
                product_type=ProductType.WATCH,
                audit=p.audit, identity=p.identity,
                commerce=p.commerce, media=p.media,
            )

    def test_watch_with_watch_module_succeeds(self):
        p = _basic_ring()
        prod = JewelryProduct(
            product_type=ProductType.WATCH,
            audit=p.audit, identity=p.identity,
            commerce=p.commerce, media=p.media,
            watch=WatchModule(movement_type="automatic"),
        )
        assert prod.watch.movement_type == "automatic"


# ============================================================
# JSON Schema generation
# ============================================================


class TestJsonSchema:
    def test_schema_generates(self):
        schema = JewelryProduct.model_json_schema()
        assert "$defs" in schema
        assert "properties" in schema
        assert schema["required"] == ["product_type", "audit", "identity", "commerce", "media"]

    def test_schema_has_strict_mode(self):
        schema = JewelryProduct.model_json_schema()
        assert schema.get("additionalProperties") is False

    def test_schema_definitions_count(self):
        schema = JewelryProduct.model_json_schema()
        # Should have ~100+ definitions across all enums and modules
        assert len(schema["$defs"]) >= 100


# ============================================================
# Transformers (export side)
# ============================================================


class TestTransformers:
    def test_schema_org(self):
        p = _full_ring()
        out = to_schema_org(p)
        assert out["@type"] == "Product"
        assert out["sku"] == p.identity.sku
        assert out["name"] == p.identity.title
        assert "additionalProperty" in out

    def test_gmc(self):
        p = _full_ring()
        out = to_gmc(p)
        assert out["id"] == p.identity.sku
        assert "google_product_category" in out
        assert out["google_product_category"].startswith("Apparel & Accessories")
        assert "product_detail" in out

    def test_acp(self):
        p = _full_ring()
        out = to_acp(p)
        assert out["item_id"] == p.identity.sku
        assert "is_eligible_search" in out
        assert "is_eligible_checkout" in out
        assert "target_countries" in out

    def test_ucp(self):
        p = _full_ring()
        out = to_ucp(p)
        assert out["id"] == p.identity.sku
        assert "native_commerce" in out

    def test_perplexity(self):
        p = _full_ring()
        out = to_perplexity(p)
        # Perplexity is GMC-equivalent
        assert out["id"] == p.identity.sku

    def test_shopify_product(self):
        p = _full_ring()
        out = to_shopify_product(p)
        assert out["title"] == p.identity.title
        assert out["vendor"] == p.identity.brand.name
        assert out["product_type"] == "Rings"

    def test_shopify_metafields(self):
        p = _full_ring()
        mfs = to_shopify_metafields(p)
        # Should have ojs.full as round-trip source-of-truth
        ojs_full = [m for m in mfs if m["namespace"] == "ojs" and m["key"] == "full"]
        assert len(ojs_full) == 1
        assert ojs_full[0]["type"] == "json"

    def test_mcp_resource(self):
        p = _full_ring()
        out = to_mcp_resource(p)
        assert "type" in out
        assert "uri" in out
        assert out["uri"].startswith("ojs://product/")
        assert "card" in out
        assert "data" in out


# ============================================================
# Round-trip integrity (Shopify ojs.full preserves all data)
# ============================================================


class TestRoundTrip:
    def test_shopify_round_trip_preserves_canonical(self):
        original = _full_ring()
        # Export to Shopify metafields
        mfs = to_shopify_metafields(original)
        # Mock a Shopify product retrieval and reverse
        mock_product = {"title": original.identity.title, "vendor": original.identity.brand.name}
        recovered_dict = from_shopify(mock_product, mfs)
        # The ojs.full metafield should round-trip the canonical record
        re_validated = JewelryProduct.model_validate(recovered_dict)
        assert re_validated.identity.sku == original.identity.sku
        assert re_validated.stones.stones[0].carat == original.stones.stones[0].carat
        assert re_validated.metals.compositions[0].purity_fineness == 950


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
