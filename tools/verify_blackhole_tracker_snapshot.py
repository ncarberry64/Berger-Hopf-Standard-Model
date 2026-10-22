"""Verify the byte-exact formal tracker snapshot without a workspace checkout."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/blackhole_tracker"


def verify() -> dict:
    manifest = json.loads((PRODUCT / "FORMAL_PROVENANCE.json").read_text(encoding="utf-8"))
    if manifest["canonical_repository"] != "https://github.com/ncarberry64/Berger-Hopf-Standard-Model":
        raise ValueError("The formal source repository differs")
    paths = set()
    for entry in manifest["source_files"]:
        path = PRODUCT / entry["path"]
        if not path.resolve().is_relative_to(PRODUCT.resolve()) or entry["path"] in paths:
            raise ValueError("Unsafe or duplicated source path")
        paths.add(entry["path"])
        data = path.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("Formal tracker source changed: " + entry["path"])
    if not (PRODUCT / "REVIEWER.md").is_file():
        raise ValueError("Formal reviewer instructions are missing")
    return {"passed": True, "files": len(paths),
            "workspace_source_commit": manifest["workspace_source_commit"],
            "canonical_path": manifest["canonical_path"],
            "scope": "Source byte integrity, not physical validation"}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
