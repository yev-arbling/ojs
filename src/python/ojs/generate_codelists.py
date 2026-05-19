"""Generate versioned codelist JSON files from Pydantic enums.

Codelists are the canonical published lists of allowed values for each
controlled vocabulary in OJS. They are versioned independently so they
can evolve without breaking the core schema.

Outputs in spec/v1/codelists/:
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
import sys
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
from ojs.models.estate import HallmarkType  # noqa: E402

OJS_NS = "https://schema.openjewelryschema.org/v1/codelist/"


def _codelist(name: str, enum_cls, description: str) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{OJS_NS}{name}.json",
        "title": f"OJS codelist: {name}",
        "description": description,
        "version": "1.0.0",
        "values": [
            {"code": e.value, "label": e.name.replace("_", " ").title()}
            for e in enum_cls
        ],
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parents[3] / "spec" / "v1" / "codelists"
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
