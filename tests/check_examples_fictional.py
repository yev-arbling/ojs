"""Release 1.0.3: every contributed example's prices and ring size differ from the 1.0.2 release's values.

The contributed examples (examples/contrib/) were modelled on real catalogue shapes. From 1.0.3 their values are
fictional: no offer keeps its 1.0.2 price and no ring keeps its 1.0.2 size, so no example mirrors one real product.
tests/fixtures/contrib-values-1.0.2.json holds the 1.0.2 values. Validation against the schema stays the job of
validate_examples.py and the Node validator. Exit 0 when every value moved, 1 otherwise.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OLD = json.loads((ROOT / "tests" / "fixtures" / "contrib-values-1.0.2.json").read_text(encoding="utf-8"))


def values(doc):
    sizing = doc.get("sizing") or {}
    return {
        "prices": [offer["price"]["amount"] for offer in (doc.get("commerce") or {}).get("offers", [])],
        "ring_size_us_ca": (sizing.get("ring_size") or {}).get("us_ca"),
    }


def main():
    files = sorted((ROOT / "examples" / "contrib").glob("*.json"))
    failures = []
    if sorted(path.name for path in files) != sorted(OLD):
        failures.append("examples/contrib/ is not the 1.0.2 set of files")
    for path in files:
        old = OLD.get(path.name)
        if old is None:
            continue
        now = values(json.loads(path.read_text(encoding="utf-8")))
        if len(now["prices"]) != len(old["prices"]):
            failures.append(f"{path.name}: {len(now['prices'])} offers, 1.0.2 had {len(old['prices'])}")
        kept = [a for a, b in zip(now["prices"], old["prices"]) if float(a) == float(b)]
        if kept:
            failures.append(f"{path.name}: price(s) {kept} equal the 1.0.2 values")
        if old["ring_size_us_ca"] is not None and now["ring_size_us_ca"] == old["ring_size_us_ca"]:
            failures.append(f"{path.name}: ring size {now['ring_size_us_ca']} equals the 1.0.2 value")
    for line in failures:
        print("FAIL", line)
    print(f"{len(files)} contributed examples; {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
