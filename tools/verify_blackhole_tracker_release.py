"""Verify a complete tracker source ZIP against its manifest and source tree."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "papers/bhsm_blackhole_tracker_20261021/provenance/RELEASE_MANIFEST.json"
PRODUCT = "products/blackhole_tracker/"
PAPERS = ("bhsm_blackhole_tracker_20261021", "bhsm_angular_lensing_20261021",
          "bhsm_state_rotation_20261021")


def safe_path(name: str) -> None:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise ValueError("Unsafe archive path: " + name)
    if path.as_posix() != name:
        raise ValueError("Noncanonical archive path: " + name)


def verify(archive: Path, source_root: Path = ROOT) -> dict:
    """Read only; every archive member must be owned by the release manifest."""
    source_root = source_root.resolve(strict=True)
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate source ZIP members")
        for name in names:
            safe_path(name)
        manifest_bytes = bundle.read(MANIFEST)
        manifest = json.loads(manifest_bytes)
        if manifest.get("formal_reviewer_repository") != "https://github.com/ncarberry64/Berger-Hopf-Standard-Model":
            raise ValueError("Wrong formal reviewer repository")
        if manifest.get("product_path") != PRODUCT.rstrip("/") or manifest.get("manifest_excludes_its_own_hash") is not True:
            raise ValueError("Unsupported source ZIP manifest contract")
        entries = manifest.get("files")
        if not isinstance(entries, list) or not entries:
            raise ValueError("Empty source ZIP manifest")
        records = {}
        for entry in entries:
            name = entry["path"]
            safe_path(name)
            if name in records or name == MANIFEST:
                raise ValueError("Duplicate or self-referential manifest entry")
            records[name] = entry
        if set(names) != set(records) | {MANIFEST}:
            raise ValueError("Source ZIP membership differs from its manifest")
        runtime = {PRODUCT + name for name in ("pyproject.toml", "bhtracker/__init__.py",
                   "bhtracker/forward.py", "bhtracker/inference.py",
                   "bhtracker/theory/BHSM_INTERPRETATION_MANIFEST.json")}
        required = {"LICENSE.md", "ACADEMIC_USE.md", PRODUCT + "FORMAL_PROVENANCE.json", PRODUCT + "REVIEWER.md",
                    "tools/verify_blackhole_tracker_snapshot.py",
                    "tools/smoke_blackhole_tracker_wheel.py", "tools/verify_blackhole_tracker_release.py"}
        required.update(runtime)
        required.update("papers/" + paper + "/manuscript/main.tex" for paper in PAPERS)
        required.add("papers/bhsm_blackhole_tracker_20261021/manuscript/main.pdf")
        if not required.issubset(records):
            raise ValueError("Source ZIP omits a required product, paper or helper")
        for name, entry in records.items():
            data = bundle.read(name)
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Source ZIP byte mismatch: " + name)
            source = source_root / name
            if not source.resolve().is_relative_to(source_root) or source.read_bytes() != data:
                raise ValueError("Source ZIP differs from source tree: " + name)
        if (source_root / MANIFEST).read_bytes() != manifest_bytes:
            raise ValueError("Source ZIP manifest differs from source tree")
        formal = json.loads(bundle.read(PRODUCT + "FORMAL_PROVENANCE.json"))
        if formal.get("canonical_repository") != manifest["formal_reviewer_repository"]:
            raise ValueError("Inner formal repository differs")
        if formal.get("schema_version") != 1 or formal.get("canonical_path") != PRODUCT.rstrip("/"):
            raise ValueError("Unsupported inner formal manifest contract")
        if not re.fullmatch(r"[0-9a-f]{40}", formal.get("workspace_source_commit", "")):
            raise ValueError("Inner source revision is not immutable")
        upstream = formal.get("source_files")
        if not isinstance(upstream, list) or not upstream:
            raise ValueError("Empty inner source manifest")
        seen = set()
        for entry in upstream:
            safe_path(entry["path"])
            name = PRODUCT + entry["path"]
            if name in seen:
                raise ValueError("Duplicate inner source manifest entry")
            seen.add(name)
            if name not in records:
                raise ValueError("An upstream source file is missing from ZIP")
            data = bundle.read(name)
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Inner formal source byte mismatch: " + name)
        if not runtime.issubset(seen):
            raise ValueError("Inner source manifest omits required runtime entries")
    return {"passed": True, "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "members": len(names), "upstream_files": len(upstream),
            "workspace_source_commit": formal["workspace_source_commit"],
            "scope": "Full archive/source-tree byte integrity; no physical or statistical revalidation"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--source-root", default=ROOT, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive.resolve(strict=True), args.source_root), indent=2))
