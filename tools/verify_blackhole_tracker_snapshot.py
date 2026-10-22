"""Verify the byte-exact formal tracker snapshot without a workspace checkout."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/blackhole_tracker"


def verify() -> dict:
    manifest = json.loads((PRODUCT / "FORMAL_PROVENANCE.json").read_text(encoding="utf-8"))
    if manifest["canonical_repository"] != "https://github.com/ncarberry64/Berger-Hopf-Standard-Model":
        raise ValueError("The formal source repository differs")
    if manifest.get("schema_version") != 1 or manifest.get("canonical_path") != "products/blackhole_tracker":
        raise ValueError("Unsupported formal source manifest contract")
    if not re.fullmatch(r"[0-9a-f]{40}", manifest.get("workspace_source_commit", "")):
        raise ValueError("The workspace source commit is not immutable")
    entries = manifest.get("source_files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("The formal source manifest contains no files")
    paths = set()
    for entry in entries:
        relative = PurePosixPath(entry["path"])
        if (relative.is_absolute() or ".." in relative.parts or "\\" in entry["path"]
                or ":" in entry["path"] or relative.as_posix() != entry["path"]):
            raise ValueError("Unsafe source path")
        path = PRODUCT / entry["path"]
        if not path.resolve().is_relative_to(PRODUCT.resolve()) or entry["path"] in paths:
            raise ValueError("Unsafe or duplicated source path")
        paths.add(entry["path"])
        data = path.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("Formal tracker source changed: " + entry["path"])
    required = {"pyproject.toml", "bhtracker/__init__.py", "bhtracker/forward.py",
                "bhtracker/inference.py", "bhtracker/theory/BHSM_INTERPRETATION_MANIFEST.json"}
    if not required.issubset(paths):
        raise ValueError("The source manifest omits required runtime files")
    if not (PRODUCT / "REVIEWER.md").is_file():
        raise ValueError("Formal reviewer instructions are missing")
    return {"passed": True, "files": len(paths),
            "canonical_repository": manifest["canonical_repository"],
            "manifest_sha256": hashlib.sha256((PRODUCT / "FORMAL_PROVENANCE.json").read_bytes()).hexdigest(),
            "workspace_source_commit": manifest["workspace_source_commit"],
            "canonical_path": manifest["canonical_path"],
            "scope": "Source byte integrity, not physical validation"}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
