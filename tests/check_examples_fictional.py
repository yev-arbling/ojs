"""One-time check for release 1.0.3: every contributed example's prices and ring size differ from release 1.0.2's.

It reads the 1.0.2 values from the tag itself (`git show v1.0.2:<path>`), so no file in the tree holds them, and it is
removed once the change has landed. Validation against the schema stays the job of validate_examples.py and the Node
validator. Exit 0 when every value moved, 1 otherwise.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAG = "v1.0.2"


def values(doc):
    sizing = doc.get("sizing") or {}
    return {
        "prices": [float(offer["price"]["amount"]) for offer in (doc.get("commerce") or {}).get("offers", [])],
        "ring_size_us_ca": (sizing.get("ring_size") or {}).get("us_ca"),
    }


def at_tag(name):
    out = subprocess.run(["git", "show", f"{TAG}:examples/contrib/{name}"], cwd=ROOT, capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else None


def main():
    files = sorted((ROOT / "examples" / "contrib").glob("*.json"))
    failures = []
    for path in files:
        old_doc = at_tag(path.name)
        if old_doc is None:
            failures.append(f"{path.name}: not found at {TAG}")
            continue
        now, old = values(json.loads(path.read_text(encoding="utf-8"))), values(old_doc)
        if len(now["prices"]) != len(old["prices"]):
            failures.append(f"{path.name}: {len(now['prices'])} offers, {TAG} had {len(old['prices'])}")
        kept = sum(a == b for a, b in zip(now["prices"], old["prices"]))
        if kept:
            failures.append(f"{path.name}: {kept} price(s) equal {TAG}'s")
        if old["ring_size_us_ca"] is not None and now["ring_size_us_ca"] == old["ring_size_us_ca"]:
            failures.append(f"{path.name}: the ring size equals {TAG}'s")
    for line in failures:
        print("FAIL", line)
    print(f"{len(files)} contributed examples; {len(failures)} failure(s)")
    return 1 if failures or not files else 0


if __name__ == "__main__":
    sys.exit(main())
