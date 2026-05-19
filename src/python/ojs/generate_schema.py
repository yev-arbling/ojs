"""Generate JSON Schema (Draft 2020-12) from Pydantic v2 models.

Run from repo root:
    python -m ojs.generate_schema

Outputs spec/v1/ojs-strict.json — the canonical machine-readable schema.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make `from ojs.models import ...` resolve when run as a script
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ojs.models import JewelryProduct, OJS_VERSION, OJS_NAMESPACE  # noqa: E402


def build_schema() -> dict:
    schema = JewelryProduct.model_json_schema()
    # Inject root-level $id, $schema, title, version
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{OJS_NAMESPACE}ojs-strict.json",
        "title": "Open Jewelry Schema (OJS) v1.0 — Strict",
        "description": (
            "Canonical machine-readable schema for the Open Jewelry Schema. "
            "Generated from Pydantic v2 models. Strict mode (extra fields forbidden)."
        ),
        "$comment": (
            f"OJS version {OJS_VERSION}. License: CC0 1.0 (vocabulary), "
            f"Apache 2.0 (reference implementation)."
        ),
        "version": OJS_VERSION,
        **schema,
    }
    return schema


def main() -> None:
    schema = build_schema()
    out_path = Path(__file__).resolve().parents[3] / "spec" / "v1" / "ojs-strict.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path}")
    print(f"  Definitions: {len(schema.get('$defs', {}))}")
    print(f"  Top-level required: {schema.get('required', [])}")


if __name__ == "__main__":
    main()
