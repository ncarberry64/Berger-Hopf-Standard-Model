"""Reproduce the frozen pilot using exact own-code kernels in a temporary copy.

The released package supplies the runtime scaffold/dependencies. Four small
historical code files, the exact original protocol and immutable external raw
observations supply the analysis identity. The current checkout is not edited.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve_product_root(explicit=None):
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([BASE.parents[2] / "product", BASE.parents[2] / "products/blackhole_tracker"])
    spec = importlib.util.find_spec("bhtracker")
    if spec and spec.origin:
        candidates.append(Path(spec.origin).resolve().parent.parent)
    for candidate in candidates:
        if (candidate / "bhtracker/__init__.py").is_file():
            return candidate.resolve()
    raise ValueError("No current bhtracker runtime scaffold found. Install the wheel or pass --product-root <directory containing bhtracker>.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--product-root", type=Path)
    parser.add_argument("--verify-only", action="store_true", help="Verify exact kernel/protocol/raw hashes and100-event selection without fitting")
    args = parser.parse_args()
    if not args.verify_only and args.output is None:
        parser.error("full reproduction needs a fresh external --output directory")
    scaffold = resolve_product_root(args.product_root)
    snapshot = BASE / "frozen_v1_sources"
    manifest = json.loads((snapshot / "MANIFEST.json").read_text(encoding="utf8"))
    for record in manifest["files"]:
        name = record["path"]
        if Path(name).name != name or sha(snapshot / name) != record["sha256"]:
            raise ValueError("frozen own-code snapshot mismatch: " + name)
    protocol = json.loads((BASE / "protocol_v1.json").read_text(encoding="utf8"))
    expected_protocol_hash = (BASE / "protocol_v1.sha256").read_text().split()[0]
    if sha(BASE / "protocol_v1.json") != expected_protocol_hash:
        raise ValueError("frozen protocol mismatch")
    for name, expected in protocol["kernel_sha256"].items():
        if sha(snapshot / name) != expected:
            raise ValueError("snapshot does not match frozen protocol kernel: " + name)
    if sha(snapshot / "run_pilot.py") != protocol["driver_sha256"]:
        raise ValueError("snapshot driver does not match frozen protocol")
    workspace = Path(tempfile.mkdtemp(prefix="bhsm-frozen-pilot-")).resolve()
    intended_parent = Path(tempfile.gettempdir()).resolve()
    if workspace.parent != intended_parent or not workspace.name.startswith("bhsm-frozen-pilot-"):
        raise ValueError("unexpected temporary workspace location")
    try:
        package = workspace / "product/bhtracker"
        shutil.copytree(scaffold / "bhtracker", package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        paper = workspace / "papers/bhsm_blackhole_tracker_20261021/real_data_pilot_20261022"
        paper.mkdir(parents=True)
        for name in ("observations.py", "photometry.py", "astrometry.py"):
            (package / name).write_bytes((snapshot / name).read_bytes())
        (paper / "run_pilot.py").write_bytes((snapshot / "run_pilot.py").read_bytes())
        for name in ("protocol_v1.json", "protocol_v1.sha256"):
            (paper / name).write_bytes((BASE / name).read_bytes())
        if args.verify_only:
            program = ("import importlib.util,json,pathlib,sys; "
                "spec=importlib.util.spec_from_file_location('frozen_pilot_driver',sys.argv[1]); "
                "module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module); "
                "p=module.verify_protocol(pathlib.Path(sys.argv[2])); "
                "manifest,catalog,selection,reproduced=module.integrity(pathlib.Path(sys.argv[2])); "
                "print(json.dumps({'status':'FROZEN_KERNEL_PROTOCOL_AND_RAW_SELECTION_VERIFIED_NO_FIT',"
                "'raw_files':len(manifest['files']),'sample_sha256':reproduced['selected_ids_sha256'],"
                "'kernel_sha256':module.kernel_hashes()}))")
            command = [sys.executable, "-c", program, str(paper / "run_pilot.py"), str(args.data_root.resolve())]
        else:
            command = [sys.executable, "-u", str(paper / "run_pilot.py"), "run", "--data-root", str(args.data_root.resolve()),
                       "--output", str(args.output.resolve())]
        completed = subprocess.run(command, cwd=workspace, check=False)
        if completed.returncode:
            raise SystemExit(completed.returncode)
        # Copy only derived own-analysis artifacts when an actual reproduction
        # finished. Full observation/replay inputs already live in --output.
        if not args.verify_only:
            derived = paper / "derived_v1"
            destination = args.output / "reproduced_derived_v1"
            if destination.exists():
                raise ValueError("do not replace an existing reproduction artifact directory")
            shutil.copytree(derived, destination)
            (args.output / "reproduced_derived_v1_manifest.json").write_bytes((paper / "derived_v1_manifest.json").read_bytes())
    finally:
        # The resolved absolute target was created by mkdtemp above and remains
        # constrained to this known temp parent/prefix before recursive cleanup.
        if workspace.parent != intended_parent or not workspace.name.startswith("bhsm-frozen-pilot-"):
            raise ValueError("refusing cleanup outside the verified temporary workspace")
        shutil.rmtree(workspace)


if __name__ == "__main__":
    main()
