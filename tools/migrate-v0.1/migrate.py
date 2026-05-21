"""Migrate v0.1 .jsonld examples → v1.0.1 JSON for examples/contrib/.

Usage:
    python tools/migrate-v0.1/migrate.py

Run from repo root. Reads from the v0.1-final source directory, writes to
examples/contrib/, and validates each output against the Pydantic model.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from ojs.models import JewelryProduct  # noqa: E402

SOURCE_DIR = Path(
    r"C:\Users\yevma\Downloads\Arbling-Brain\raw\tools\open-jewelry-schema\v0.1-final\examples"
)
OUTPUT_DIR = REPO_ROOT / "examples" / "contrib"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CREATED_AT = "2026-05-21T00:00:00Z"

# ── Field mapping helpers ────────────────────────────────────────────────────

AVAILABILITY_MAP = {
    "https://schema.org/InStock": "in_stock",
    "https://schema.org/OutOfStock": "out_of_stock",
    "https://schema.org/BackOrder": "backorder",
    "https://schema.org/Discontinued": "discontinued",
    "https://schema.org/PreOrder": "preorder",
    "https://schema.org/LimitedAvailability": "limited_availability",
    "https://schema.org/MadeToOrder": "made_to_order",
    "in_stock": "in_stock",
    "out_of_stock": "out_of_stock",
    "backorder": "backorder",
    "discontinued": "discontinued",
}

STONE_CUT_MAP = {
    "round_brilliant": "round_brilliant",
    "round": "round_brilliant",
    "princess": "princess",
    "cushion": "cushion",
    "emerald_cut": "emerald_cut",
    "emerald": "emerald_cut",
    "oval": "oval",
    "pear": "pear",
    "marquise": "marquise",
    "radiant": "radiant",
    "asscher": "asscher",
    "heart": "heart",
    "baguette": "baguette",
    "tapered_baguette": "baguette",  # closest valid enum
    "trillion": "trillion",
    "rose_cut": "rose_cut",
    "old_european": "old_european",
    "old_mine": "old_mine",
    "cabochon": "cabochon",
    "briolette": "briolette",
    "fancy": "fancy",
}

MOTIF_MAP = {
    "floral": "floral",
    "leaf": "leaf",
    "animal": "animal",
    "butterfly": "butterfly",
    "bird": "bird",
    "snake": "snake",
    "heart": "heart",
    "star": "star",
    "moon": "moon",
    "sun": "sun",
    "celestial": "celestial",
    "cross": "cross",
    "knot": "knot",
    "infinity": "infinity",
    "bow": "bow",
    "geometric": "geometric",
    "scroll": "scroll",
    "filigree": "filigree",
    "milgrain": "milgrain",
    # "nature" is not a valid Motif value — mapped below
}

ERA_MAP = {
    "georgian": "georgian",
    "early_victorian": "early_victorian",
    "mid_victorian": "mid_victorian",
    "late_victorian": "late_victorian",
    "edwardian": "edwardian",
    "art_nouveau": "art_nouveau",
    "art_deco": "art_deco",
    "retro": "retro",
    "mid_century": "mid_century",
    "modernist": "modernist",
    "contemporary": "contemporary",
    "unknown": "unknown",
    # "minimalist" is a design style, not a historical era
}

DESIGN_STYLE_MAP = {
    "minimalist": "minimalist",
    "maximalist": "maximalist",
    "classic": "classic",
    "vintage_inspired": "vintage_inspired",
    "boho": "boho",
    "gothic": "gothic",
    "industrial": "industrial",
    "nature_inspired": "nature_inspired",
    "geometric": "geometric",
    "abstract": "abstract",
    "romantic": "romantic",
    "unisex": "unisex",
    "feminine": "feminine",
    "masculine": "masculine",
}

METAL_TYPE_MAP = {
    "gold": "gold",
    "silver": "silver",
    "platinum": "platinum",
    "palladium": "palladium",
    "titanium": "titanium",
    "niobium": "niobium",
    "steel": "steel",
    "tungsten": "tungsten",
    "brass": "brass",
    "bronze": "bronze",
    "copper": "copper",
}

METAL_COLOR_MAP = {
    "yellow": "yellow",
    "white": "white",
    "rose": "rose",
    "green": "green",
    "black": "black",
    "natural": "natural",
    "two_tone": "two_tone",
    "tri_color": "tri_color",
}

STONE_SPECIES_MAP = {
    "diamond": "diamond",
    "ruby": "ruby",
    "sapphire": "sapphire",
    "emerald": "emerald",
    "aquamarine": "aquamarine",
    "morganite": "morganite",
    "amethyst": "amethyst",
    "citrine": "citrine",
    "smoky_quartz": "smoky_quartz",
    "rose_quartz": "rose_quartz",
    "tanzanite": "tanzanite",
    "topaz": "topaz",
    "tourmaline": "tourmaline",
    "garnet": "garnet",
    "peridot": "peridot",
    "spinel": "spinel",
    "zircon": "zircon",
    "moissanite": "moissanite",
    "pearl": "pearl",
    "amber": "amber",
    "coral": "coral",
    "jet": "jet",
    "opal": "opal",
    "turquoise": "turquoise",
    "lapis_lazuli": "lapis_lazuli",
    "malachite": "malachite",
    "onyx": "onyx",
    "agate": "agate",
    "jade_jadeite": "jade_jadeite",
    "jade_nephrite": "jade_nephrite",
}

STONE_ORIGIN_MAP = {
    "natural": "natural",
    "lab_grown": "lab_grown",
    "simulant": "simulant",
    "simulated": "simulant",
    "synthetic": "lab_grown",
    "unknown": "unknown",
}

SETTING_TYPE_MAP = {
    "prong": "prong",
    "bezel": "bezel",
    "half_bezel": "half_bezel",
    "tension": "tension",
    "channel": "channel",
    "pave": "pave",
    "pavé": "pave",
    "micro_pave": "micro_pave",
    "bar": "bar",
    "flush": "flush",
    "gypsy": "gypsy",
    "invisible": "invisible",
    "cluster": "cluster",
    "halo": "halo",
    "burnish": "burnish",
    "illusion": "illusion",
    "suspension": "suspension",
}


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60]


def parse_purity(purity_str: str, metal_type: str) -> dict:
    """Convert v0.1 purity string to v1.0 purity fields."""
    if not purity_str:
        return {}
    purity_str = str(purity_str).strip().lower()
    # Karat: "10k", "14k", "18k", "22k", "24k"
    m = re.match(r"^(\d+)k$", purity_str)
    if m:
        return {"purity_karat": float(m.group(1))}
    # Fineness: "925", "950", "999", "750", "585", "417"
    if re.match(r"^\d{3}$", purity_str):
        return {"purity_fineness": int(purity_str)}
    return {}


def extract_seller_info(offer_url: str) -> tuple[str, str]:
    """Infer seller_name and seller_url from offer URL."""
    # All v0.1 examples are mejuri.com
    if "mejuri.com" in offer_url:
        return "Mejuri", "https://mejuri.com"
    # Generic fallback: extract domain
    m = re.match(r"(https?://[^/]+)", offer_url)
    if m:
        base_url = m.group(1)
        domain = re.sub(r"https?://", "", base_url)
        seller_name = domain.replace("www.", "").split(".")[0].title()
        return seller_name, base_url
    return "Unknown Seller", "https://example.com"


def migrate_metal(metal: dict) -> dict | None:
    """Convert v0.1 metal object → v1.0 metals module."""
    if not metal:
        return None
    metal_type_raw = metal.get("type", "")
    metal_type = METAL_TYPE_MAP.get(metal_type_raw.lower(), None)
    if not metal_type:
        return None  # unknown metal type — skip

    comp = {"type": metal_type, "primary": True}

    purity_fields = parse_purity(metal.get("purity", ""), metal_type)
    comp.update(purity_fields)

    color_raw = metal.get("color", "")
    if color_raw and color_raw.lower() in METAL_COLOR_MAP:
        comp["color"] = METAL_COLOR_MAP[color_raw.lower()]

    finish_raw = metal.get("finish", "")
    valid_finishes = {"polished", "matte", "brushed", "satin", "hammered", "sandblasted", "oxidized", "milgrain", "engraved", "florentine"}
    if finish_raw and finish_raw.lower() in valid_finishes:
        comp["finish"] = finish_raw.lower()

    # v0.1 "construction" = "vermeil" maps to plating
    construction = metal.get("construction", "")
    if construction:
        plating_map = {
            "vermeil": "vermeil",
            "gold_plated": "gold_plated",
            "gold_filled": "gold_filled",
            "rhodium_plated": "rhodium_plated",
        }
        if construction.lower() in plating_map:
            comp["plating"] = plating_map[construction.lower()]

    return {"compositions": [comp]}


def migrate_stones(stones_raw) -> dict | None:
    """Convert v0.1 stones array → v1.0 stones module."""
    if not stones_raw:
        return None
    if isinstance(stones_raw, dict):
        stones_raw = [stones_raw]
    if not isinstance(stones_raw, list) or len(stones_raw) == 0:
        return None

    migrated = []
    for s in stones_raw:
        type_raw = s.get("type", "").lower()
        species = STONE_SPECIES_MAP.get(type_raw)
        if not species:
            # Log and skip unknown species
            print(f"  [WARN] Unknown stone species '{type_raw}' — skipping stone")
            continue

        origin_raw = s.get("origin", "natural").lower()
        origin_type = STONE_ORIGIN_MAP.get(origin_raw, "unknown")

        stone = {
            "species": species,
            "origin_type": origin_type,
        }

        # Cut
        cut_raw = s.get("cut", "")
        if cut_raw:
            mapped_cut = STONE_CUT_MAP.get(cut_raw.lower())
            if mapped_cut:
                stone["cut"] = mapped_cut
            else:
                stone["cut"] = "other"

        # Carat
        if "carat" in s and s["carat"] is not None:
            stone["carat"] = float(s["carat"])

        # Position: first stone is "center" if is_primary
        if s.get("is_primary"):
            stone["position"] = "center"

        # Color grade (if present)
        if "color_grade" in s:
            stone["color_description"] = str(s["color_grade"])

        # Clarity (if present)
        # Map string clarity grades to DiamondClarityGrade if diamond
        clarity_map = {"FL": "FL", "IF": "IF", "VVS1": "VVS1", "VVS2": "VVS2",
                       "VS1": "VS1", "VS2": "VS2", "SI1": "SI1", "SI2": "SI2",
                       "I1": "I1", "I2": "I2", "I3": "I3"}
        if "clarity" in s and species == "diamond":
            clarity = str(s["clarity"]).upper()
            if clarity in clarity_map:
                stone["clarity_grade"] = clarity_map[clarity]

        migrated.append(stone)

    if not migrated:
        return None

    return {"stones": migrated, "center_stone_index": 0}


def migrate_setting(setting: dict) -> dict | None:
    """Convert v0.1 setting object → v1.0 setting module."""
    if not setting:
        return None
    type_raw = setting.get("type", "").lower()
    setting_type = SETTING_TYPE_MAP.get(type_raw)
    if not setting_type:
        return None
    style = {
        "style_id": "main",
        "setting_type": setting_type,
    }
    if "prong_count" in setting:
        style["prong_count"] = int(setting["prong_count"])
    return {"styles": [style]}


def migrate_sizing(sizing: dict, product_type: str) -> dict | None:
    """Convert v0.1 sizing → v1.0 sizing module."""
    if not sizing:
        return None
    result = {}

    if "ring_size_us" in sizing and sizing["ring_size_us"] is not None:
        result["ring_size"] = {"us_ca": float(sizing["ring_size_us"])}

    resizable = sizing.get("resizable")
    if resizable is not None:
        result["ring_resizable"] = bool(resizable)

    length = sizing.get("length_mm") or sizing.get("length")
    if length is not None:
        result["length_mm"] = float(length)

    if not result:
        return None
    return result


def migrate_style(style: dict) -> dict | None:
    """Convert v0.1 style object → v1.0 style module."""
    if not style:
        return None
    result: dict = {
        "design_styles": [],
        "motifs": [],
        "aesthetic_tags": [],
    }

    # Era
    era_raw = style.get("era", "")
    if era_raw:
        if era_raw.lower() in ERA_MAP:
            result["era"] = ERA_MAP[era_raw.lower()]
        elif era_raw.lower() in DESIGN_STYLE_MAP:
            # e.g. "minimalist" is a design style, not an era
            result["design_styles"].append(DESIGN_STYLE_MAP[era_raw.lower()])

    # Motif (singular in v0.1, list in v1.0)
    motif_raw = style.get("motif", "")
    if motif_raw:
        mapped = MOTIF_MAP.get(motif_raw.lower())
        if mapped:
            result["motifs"].append(mapped)
        # "nature" and other unknown motifs: add to aesthetic_tags
        elif motif_raw.lower() not in ("nature",):
            # Try to map to a valid design style
            if motif_raw.lower() in DESIGN_STYLE_MAP:
                result["design_styles"].append(DESIGN_STYLE_MAP[motif_raw.lower()])
            else:
                result["aesthetic_tags"].append(motif_raw.lower())
        # "nature" motif: add as aesthetic_tag since it's not a valid Motif enum
        else:
            result["aesthetic_tags"].append("nature-inspired")

    # Occasions → aesthetic_tags
    occasions = style.get("occasions", [])
    if isinstance(occasions, str):
        occasions = [occasions]
    for occ in occasions:
        if occ and occ not in result["aesthetic_tags"]:
            result["aesthetic_tags"].append(occ)

    # Color story → aesthetic_tags (prefix with "color:")
    color_story = style.get("color_story", [])
    if isinstance(color_story, str):
        color_story = [color_story]
    for c in color_story:
        tag = f"color:{c}"
        if tag not in result["aesthetic_tags"]:
            result["aesthetic_tags"].append(tag)

    # Finish style → aesthetic_tags
    finish_style = style.get("finish_style", "")
    if finish_style:
        result["aesthetic_tags"].append(finish_style)

    # Remove empty lists to keep JSON clean (but keep the keys)
    return result


def migrate_offers(offers_raw, root_url: str, product_type: str) -> list:
    """Convert v0.1 offers (object or array) → v1.0 Offer list."""
    if offers_raw is None:
        return []
    if isinstance(offers_raw, dict):
        offers_raw = [offers_raw]
    if not isinstance(offers_raw, list):
        return []

    result = []
    for o in offers_raw:
        price_val = o.get("price")
        price_currency = o.get("priceCurrency", "USD")
        availability_raw = o.get("availability", "https://schema.org/InStock")
        offer_url = o.get("url", root_url)

        if price_val is None:
            continue

        availability = AVAILABILITY_MAP.get(availability_raw, "in_stock")

        seller_name, seller_url = extract_seller_info(offer_url)

        offer = {
            "price": {
                "amount": f"{float(price_val):.2f}",
                "currency": price_currency.upper(),
            },
            "availability": availability,
            "url": offer_url,
            "condition": "new",
            "target_countries": ["US"],
            "seller_name": seller_name,
            "seller_url": seller_url,
        }

        result.append(offer)

    return result


def migrate_file(source_path: Path) -> dict | None:
    """Migrate a single v0.1 .jsonld file to v1.0 structure."""
    raw = source_path.read_text(encoding="utf-8")
    data = json.loads(raw)

    # Drop JSON-LD specific keys
    jewelry_type = data.get("jewelry_type") or data.get("@type", "").lower()
    if jewelry_type == "product":
        jewelry_type = "other"

    name = data.get("name", "")
    description = data.get("description", "").strip()
    brand_raw = data.get("brand", "")
    sku_raw = data.get("sku", "")
    image_primary = data.get("image", "")
    images_extra = data.get("_images", [])
    root_url = data.get("url", "")

    # product_type
    product_type_map = {
        "ring": "ring", "earring": "earring", "necklace": "necklace",
        "bracelet": "bracelet", "pendant": "pendant", "brooch": "brooch",
        "anklet": "anklet", "watch": "watch", "pearl": "pearl",
        "smart_wearable": "smart_wearable", "body": "body", "estate": "estate",
        "jewelry_set": "jewelry_set", "other": "other",
    }
    product_type = product_type_map.get(jewelry_type.lower(), "other")

    # SKU: generate if missing
    if not sku_raw:
        sku_raw = f"OJS-CONTRIB-{slugify(name)}"

    # identity
    identity = {
        "sku": str(sku_raw)[:100],
        "title": name[:150],
        "description": description[:5000],
        "brand": {
            "name": (brand_raw if isinstance(brand_raw, str) else str(brand_raw))[:70]
        },
    }
    if root_url:
        # Also store collection if present
        collection = data.get("collection")
        if collection:
            identity["collection"] = str(collection)[:100]

    # media
    images = []
    if image_primary:
        images.append({"url": image_primary, "role": "primary", "is_primary": True})
    if isinstance(images_extra, list):
        for img_url in images_extra:
            if img_url and img_url != image_primary:
                images.append({"url": img_url, "role": "additional", "is_primary": False})
    if not images:
        print(f"  [ERROR] No images found in {source_path.name}")
        return None

    media = {"images": images}

    # commerce
    offers = migrate_offers(data.get("offers"), root_url, product_type)
    if not offers:
        # If no offers, create a stub pointing to root_url
        if root_url:
            seller_name, seller_url = extract_seller_info(root_url)
            offers = [{
                "price": {"amount": "0.00", "currency": "USD"},
                "availability": "out_of_stock",
                "url": root_url,
                "condition": "new",
                "target_countries": ["US"],
                "seller_name": seller_name,
                "seller_url": seller_url,
            }]
        else:
            print(f"  [ERROR] No offers and no URL in {source_path.name}")
            return None

    commerce = {"offers": offers, "primary_offer_index": 0}

    # audit
    audit = {
        "ojs_version": "1.0.1",
        "created_at": CREATED_AT,
        "source_system": "other",
    }

    # Assemble base record
    record: dict = {
        "product_type": product_type,
        "audit": audit,
        "identity": identity,
        "commerce": commerce,
        "media": media,
    }

    # metals
    metal_raw = data.get("metal")
    metals = migrate_metal(metal_raw) if metal_raw else None
    if metals:
        record["metals"] = metals

    # stones
    stones_raw = data.get("stones")
    stones = migrate_stones(stones_raw) if stones_raw else None
    if stones:
        record["stones"] = stones

    # setting
    setting_raw = data.get("setting")
    setting = migrate_setting(setting_raw) if setting_raw else None
    if setting:
        record["setting"] = setting

    # sizing
    sizing_raw = data.get("sizing")
    sizing = migrate_sizing(sizing_raw, product_type) if sizing_raw else None
    if sizing:
        record["sizing"] = sizing

    # style
    style_raw = data.get("style")
    style = migrate_style(style_raw) if style_raw else None
    if style:
        record["style"] = style

    return record


def main() -> int:
    source_files = sorted(SOURCE_DIR.glob("*.jsonld"))
    if not source_files:
        print(f"ERROR: No .jsonld files found in {SOURCE_DIR}")
        return 1

    saved = 0
    skipped = 0
    errors = []

    for src in source_files:
        stem = src.stem
        out_path = OUTPUT_DIR / f"{stem}.json"
        print(f"\nMigrating: {src.name}")

        try:
            record = migrate_file(src)
        except Exception as e:
            msg = f"MIGRATION ERROR: {e}"
            print(f"  [ERROR] {msg}")
            errors.append((src.name, msg))
            skipped += 1
            continue

        if record is None:
            msg = "Migration returned None (see errors above)"
            print(f"  [SKIP] {msg}")
            errors.append((src.name, msg))
            skipped += 1
            continue

        # Validate against Pydantic model
        text = json.dumps(record, ensure_ascii=False, indent=2)
        try:
            product = JewelryProduct.model_validate_json(text)
            out_path.write_text(text, encoding="utf-8")
            print(f"  OK saved -> {out_path.relative_to(REPO_ROOT)} (product_type={product.product_type}, sku={product.identity.sku})")
            saved += 1
        except Exception as e:
            msg = f"Pydantic validation failed: {e}"
            print(f"  [SKIP] {msg}")
            errors.append((src.name, msg))
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Migration complete: {saved} saved, {skipped} skipped")
    if errors:
        print(f"\nSkipped files ({len(errors)}):")
        for name, msg in errors:
            print(f"  FAIL {name}: {msg[:200]}")

    return 0 if skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
