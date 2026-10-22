"""Wrap an exact product-only source ZIP with canonical notices and provenance.

This packages existing source bytes. It never fits data, builds a wheel, changes
a manuscript, or makes a publication. The code revision must already identify
the formal imported product. The output's own hash stays outside its manifest.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def sha(content):
    return hashlib.sha256(content).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--upstream-revision", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{64}", args.source_sha256):
        parser.error("source SHA-256 must be64 lowercase hex digits")
    if not all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in (args.code_revision, args.upstream_revision)):
        parser.error("formal and upstream revisions must be exact40-digit Git commits")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+rc[0-9]+", args.version):
        parser.error("a versioned release-candidate identity is required")
    content = args.source_zip.read_bytes()
    if sha(content) != args.source_sha256:
        raise ValueError("source ZIP differs from its supplied release SHA-256")
    with zipfile.ZipFile(args.source_zip) as source:
        names = source.namelist()
        if len(names) != len(set(names)) or not names:
            raise ValueError("empty or duplicate source archive members")
        if any(not name.startswith("product/") or ".." in PurePosixPath(name).parts or "\\" in name or name.endswith("/") for name in names):
            raise ValueError("only regular product/ source-file members are allowed")
        files = {name: source.read(name) for name in names}
    manifest = {
        "formal_repository": "https://github.com/ncarberry64/Berger-Hopf-Standard-Model",
        "formal_code_commit": args.code_revision, "upstream_snapshot": args.upstream_revision,
        "standalone_layout": "product/", "product_version": args.version,
        "input_source_archive_sha256": args.source_sha256,
        "files": {name: sha(data) for name, data in sorted(files.items())}}
    files["PRODUCT_MANIFEST.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf8")
    for name in ("LICENSE.md", "ACADEMIC_USE.md"):
        files[name] = (ROOT / name).read_bytes()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o644 << 16
            target.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(json.dumps({"file": str(args.output), "bytes": args.output.stat().st_size,
        "sha256": sha(args.output.read_bytes()), "product_source_files": len(manifest["files"]),
        "formal_code_commit": args.code_revision, "version": args.version}))


if __name__ == "__main__":
    main()
