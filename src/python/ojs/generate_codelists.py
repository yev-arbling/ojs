"""Generate versioned codelist JSON files from Pydantic enums.

Codelists are the canonical published lists of allowed values for each
controlled vocabulary in OJS. They are versioned independently so they
can evolve without breaking the core schema.

Outputs in spec/v1/codelists/ (1.1.0: the grouped files below are kept at their paths and `$id`s, and one file
per enum is added beside them, `<kebab-case-enum-name>.json`, for every str Enum the models export):
  - metals.json
  - gems.json
  - treatments.json
  - hallmarks.json
  - eras.json
  - settings.json
  - pearls.json
"""
from __future__ import annotations

import json
import re
import sys
from enum import Enum
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ojs.models import (  # noqa: E402
    DesignStyle, Era, GemstoneSpecies, GradingLab, MetalColor, MetalFinish,
    MetalType, Motif, PearlBodyColor, PearlLuster, PearlOvertone, PearlShape,
    PearlSurface, PearlType, PlatingType, SettingType, StoneCut, StoneOrigin,
    TreatmentType,
)
from ojs.models._common import OJS_VERSION  # noqa: E402
from ojs.models.estate import HallmarkType  # noqa: E402
import ojs.models as _models  # noqa: E402

OJS_NS = "https://schema.openjewelryschema.org/v1/codelist/"

_DESCRIPTIONS: dict[str, str] = {
    "ActivitySafety": "Safe and avoid-list activities for care",
    "ArtisanTechnique": "Traditional and artisan fabrication techniques",
    "Audience": "Target audience tags for AI commerce matching",
    "Availability": "Product availability states (Schema.org / GMC / ACP aligned)",
    "BiocompatibilityStandard": "Material safety standards for body jewelry (ASTM/ISO)",
    "CaseShape": "Watch case shapes",
    "CeremonyType": "Ceremony and ritual occasion types",
    "ChainStyle": "Chain link topology for necklaces and bracelets",
    "CleaningMethod": "Recommended cleaning approaches",
    "ColoredStoneClarityGrade": "GIA clarity grades for colored stones (sapphire, ruby, emerald, etc.)",
    "Condition": "Product condition (Schema.org / GMC / ACP aligned)",
    "ConfidenceSource": "Data provenance sources for enrichment pipeline",
    "Connectivity": "Wireless connectivity standards for smart jewelry",
    "CutGrade": "GIA cut/polish/symmetry grades for round brilliant diamonds",
    "DesignStyle": "Aesthetic design style tags (multi-valued)",
    "DiamondClarityGrade": "GIA FL-I3 clarity scale for diamonds",
    "DiamondColorGrade": "GIA D-Z color scale plus Fancy Color descriptors",
    "EarringPostType": "Earring finding form factors (distinct from closure mechanism)",
    "EditionType": "Edition classification for artisan pieces",
    "Era": "Historical jewelry periods and style aesthetics",
    "FluorescenceIntensity": "GIA fluorescence intensity under longwave UV",
    "GemstoneSpecies": "Major gemstone species per GIA / CIBJO",
    "GradingLab": "Accredited gemological laboratories (AGS legacy-only post-2022)",
    "HSCodePrefix": "Common HS 2022 codes for jewelry customs",
    "ImageRole": "Image role/category for media assets",
    "JewelryClosure": "Closure mechanisms for necklaces, bracelets, earrings",
    "MetalColor": "Visible metal colors",
    "MetalFinish": "Metal surface finishes",
    "MetalType": "Base metal types per ISO 9202",
    "Motif": "Recurring decorative motifs (multi-valued)",
    "MovementType": "Watch movement technology",
    "NacreQuality": "Pearl nacre thickness assessment",
    "Occasion": "Gift and purchase occasions for AI commerce matching",
    "PaymentMethod": "Accepted payment methods",
    "PearlBodyColor": "Pearl body colors per CIBJO",
    "PearlLuster": "Pearl luster quality grades",
    "PearlMatchingGrade": "Pearl strand matching quality",
    "PearlOvertone": "Pearl overtone colors",
    "PearlShape": "CIBJO 7-shape pearl classification",
    "PearlSurface": "Pearl surface cleanliness grades",
    "PearlType": "Pearl origin types per CIBJO",
    "PiercingLocation": "Body piercing anatomical sites",
    "PlacementAnchor": "AR body anchor points for virtual try-on",
    "PlatingType": "Plating types (vermeil requires >=2.5um per FTC 23.5)",
    "PriceTier": "Coarse price tiers for AI commerce matching",
    "ProductSubtype": "Fine-grained product classification within product_type",
    "ProductType": "Top-level product type discriminator",
    "RegulatoryFlag": "Compliance claims (Nickel Directive, RoHS, etc.)",
    "RelationshipType": "Product relationship types (variant, complement, etc.)",
    "Religion": "Religious traditions for ceremonial jewelry",
    "SettingType": "Stone setting types",
    "SizeSystem": "Ring size designation systems (ISO, US/CA, UK/AU, etc.)",
    "SmartFeature": "Smart wearable feature capabilities",
    "SourceSystem": "Data provenance system identifiers",
    "StoneCut": "Gemstone faceting shapes",
    "StoneOrigin": "Stone origin types (natural / lab-grown / simulant)",
    "StorageRecommendation": "Storage and handling recommendations",
    "StrapType": "Watch strap/bracelet material types",
    "ThreadingType": "Body jewelry threading types",
    "TreatmentType": "Stone enhancement treatments (FTC 16 CFR 23.22 disclosure required)",
    "WaterProofRating": "Smart wearable water resistance ratings",
}


def _enum_to_filename(name: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1-\2", s)
    return s.lower()


def _enum_codelist(enum_cls: type[Enum]) -> dict:
    """One enum's own codelist (1.1.0), beside the grouped files."""
    filename = _enum_to_filename(enum_cls.__name__)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{OJS_NS}{filename}.json",
        "title": f"OJS codelist: {filename}",
        "description": _DESCRIPTIONS.get(enum_cls.__name__, f"OJS v1 controlled vocabulary: {enum_cls.__name__}"),
        "version": OJS_VERSION,
        "values": [{"code": e.value, "label": e.name.replace("_", " ").title()} for e in enum_cls],
    }


def _collect_enums() -> list[type[Enum]]:
    """Every str Enum `ojs.models` exports, once, by name."""
    found = {obj.__name__: obj for obj in vars(_models).values()
             if isinstance(obj, type) and issubclass(obj, Enum) and issubclass(obj, str)}
    return [found[name] for name in sorted(found)]


def _codelist(name: str, enum_cls, description: str) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{OJS_NS}{name}.json",
        "title": f"OJS codelist: {name}",
        "description": description,
        "version": OJS_VERSION,
        "values": [
            {"code": e.value, "label": e.name.replace("_", " ").title()}
            for e in enum_cls
        ],
    }


def main(out_dir: Path | None = None) -> None:
    if out_dir is None:
        out_dir = Path(__file__).resolve().parents[3] / "spec" / "v1" / "codelists"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    codelists = {
        "metals": {
            "types": _codelist("metal_types", MetalType, "Base metal types per ISO 9202"),
            "colors": _codelist("metal_colors", MetalColor, "Visible metal colors"),
            "finishes": _codelist("metal_finishes", MetalFinish, "Surface finishes"),
            "platings": _codelist("plating_types", PlatingType, "Plating types (vermeil ≥2.5µm per FTC §23.5)"),
        },
        "gems": {
            "species": _codelist("gemstone_species", GemstoneSpecies, "Recognized gemstone species"),
            "origins": _codelist("stone_origins", StoneOrigin, "Stone origin types (natural/lab-grown/simulant)"),
            "cuts": _codelist("stone_cuts", StoneCut, "Faceting shapes"),
            "grading_labs": _codelist("grading_labs", GradingLab, "Accredited grading laboratories (AGS legacy-only after 2022)"),
        },
        "treatments": _codelist("treatments", TreatmentType, "Stone enhancement treatments (FTC 16 CFR §23.22 disclosure)"),
        "hallmarks": _codelist("hallmark_types", HallmarkType, "Hallmark categories"),
        "eras": _codelist("eras", Era, "Historical periods for vintage/antique pieces"),
        "settings": _codelist("setting_types", SettingType, "Stone setting types"),
        "pearls": {
            "types": _codelist("pearl_types", PearlType, "Pearl origin types per CIBJO"),
            "luster": _codelist("pearl_luster", PearlLuster, "Luster grades"),
            "surface": _codelist("pearl_surface", PearlSurface, "Surface cleanliness grades"),
            "shapes": _codelist("pearl_shapes", PearlShape, "CIBJO 7-shape classification"),
            "body_colors": _codelist("pearl_body_colors", PearlBodyColor, "Body colors"),
            "overtones": _codelist("pearl_overtones", PearlOvertone, "Overtone colors"),
        },
        "styles": {
            "design": _codelist("design_styles", DesignStyle, "Design style tags"),
            "motifs": _codelist("motifs", Motif, "Decorative motifs"),
        },
    }

    # Write each codelist to its own file
    written = []
    for name, content in codelists.items():
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n")
        written.append(path.name)

    print(f"Wrote {len(written)} codelist files to {out_dir}:")
    for f in written:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
