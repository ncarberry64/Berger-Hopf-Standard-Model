"""Create a clean source archive and an additive Git patch for this paper.

This creates only local deliverables. It does not contact GitHub, commit to
an existing repository, change a branch, or use repository credentials.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {"__pycache__", ".git", "matplotlib_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".aux", ".fls", ".fdb_latexmk", ".out", ".blg"}


def included(path):
    rel = path.relative_to(ROOT)
    if not path.is_file() or any(x in EXCLUDED_PARTS for x in rel.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES or path.name.endswith(".synctex.gz"):
        return False
    if rel.parts[0] == "manuscript" and path.suffix == ".log":
        return False
    if str(rel) == "provenance/RELEASE_MANIFEST.json":
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in ROOT.rglob("*") if included(p))
    manifest = {"schema": "BHSM-ANGULAR-RELEASE-FILES-V1",
                "exclusion": "manifest excludes its own hash",
                "files": [{"path": str(p.relative_to(ROOT)),
                           "bytes": p.stat().st_size,
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in files]}
    mp = ROOT / "provenance/RELEASE_MANIFEST.json"
    mp.write_text(json.dumps(manifest, indent=2) + "\n")
    files.append(mp)
    prefix = "bhsm_angular_lensing_20261021"
    archive = out / "BHSM_Angular_Lensing_Reproducibility.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            z.write(p, Path(prefix) / p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for item in manifest["files"]:
            data = z.read(str(Path(prefix) / item["path"]))
            assert hashlib.sha256(data).hexdigest() == item["sha256"]
    pdf = out / "BHSM_Angular_Lensing_Manuscript.pdf"
    shutil.copyfile(ROOT / "manuscript/main.pdf", pdf)
    patch = out / "BHSM_Angular_Lensing_New_Paper.patch"
    with tempfile.TemporaryDirectory(prefix="bhsm-angular-git-export-") as temp:
        staging = Path(temp)
        destination = staging / "papers" / prefix
        for p in files:
            target = destination / p.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
        subprocess.run(["git", "init", "-q", str(staging)], check=True)
        subprocess.run(["git", "-C", str(staging), "add", "papers"], check=True)
        diff = subprocess.run(["git", "-C", str(staging), "diff", "--cached",
                               "--binary", "--full-index", "--no-ext-diff"],
                              capture_output=True, check=True).stdout
        patch.write_bytes(diff)
        # A separate empty repository checks that the patch is additive/applicable.
        with tempfile.TemporaryDirectory(prefix="bhsm-angular-patch-check-") as check:
            subprocess.run(["git", "init", "-q", check], check=True)
            subprocess.run(["git", "-C", check, "apply", "--check", str(patch)], check=True)
    print(json.dumps({"release_files": len(files),
                      "archive_crc_and_hashes_verified": True,
                      "additive_patch_check_passed": True,
                      "outputs": [{"path": str(p), "bytes": p.stat().st_size,
                                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                  for p in [pdf, archive, patch]]}, indent=2))


if __name__ == "__main__":
    main()
