"""Validate every example JSON file against the JewelryProduct model.

Run from repo root:
    python tests/validate_examples.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))

from ojs.models import JewelryProduct  # noqa: E402

EXAMPLES = sorted((ROOT / "examples").glob("*.json"))


def main() -> int:
    errors = 0
    for fp in EXAMPLES:
        try:
            data = json.loads(fp.read_text())
            # strip $schema marker — not part of OJS model
            data.pop("$schema", None)
            product = JewelryProduct.model_validate(data)
            print(f"✓ {fp.name} — product_type={product.product_type} sku={product.identity.sku}")
        except Exception as e:
            errors += 1
            print(f"✗ {fp.name} — {type(e).__name__}: {e}")
    print(f"\n{len(EXAMPLES) - errors}/{len(EXAMPLES)} examples valid")
    return errors


if __name__ == "__main__":
    sys.exit(main())
