"""Generate versioned codelist JSON files from Pydantic enums.

Codelists are the canonical published lists of allowed values for each
controlled vocabulary in OJS. They are versioned independently so they
can evolve without breaking the core schema.

Outputs to spec/v1/codelists/ (or a provided out_dir).
One file per enum — every str,Enum subclass in ojs.models is exported.
"""
from __future__ import annotations

import json
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Type

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

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


def _codelist(enum_cls: Type[Enum]) -> dict:
    name = enum_cls.__name__
    filename = _enum_to_filename(name)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{OJS_NS}{filename}.json",
        "title": f"OJS codelist: {filename}",
        "description": _DESCRIPTIONS.get(name, f"OJS v1 controlled vocabulary: {name}"),
        "version": "1.0.0",
        "values": [
            {"code": e.value, "label": e.name.replace("_", " ").title()}
            for e in enum_cls
        ],
    }


def _collect_enums() -> list[Type[Enum]]:
    seen: set[str] = set()
    result = []
    for attr_name in dir(_models):
        obj = getattr(_models, attr_name)
        try:
            if (
                isinstance(obj, type)
                and issubclass(obj, Enum)
                and issubclass(obj, str)
                and obj is not Enum
                and obj.__name__ not in seen
            ):
                seen.add(obj.__name__)
                result.append(obj)
        except TypeError:
            pass
    return sorted(result, key=lambda c: c.__name__)


def main(out_dir: Path | None = None) -> None:
    if out_dir is None:
        out_dir = Path(__file__).resolve().parents[3] / "spec" / "v1" / "codelists"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    enums = _collect_enums()
    written = []
    for enum_cls in enums:
        data = _codelist(enum_cls)
        filename = _enum_to_filename(enum_cls.__name__) + ".json"
        path = out_dir / filename
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        written.append(filename)

    print(f"Wrote {len(written)} codelist files to {out_dir}:")
    for f in sorted(written):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
