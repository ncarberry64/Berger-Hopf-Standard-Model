"""Bind and replay the original invented algebra controls in a fresh location.

This is a deterministic mathematical replay, not a new observational experiment
or a repeat of the original full-source review. No network or product imports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def write_new(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
    return sha(raw)


def prepare(output):
    pins_path = HERE / "ORIGINAL_IMPLEMENTATION_PINS_v1.json"
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    files = []
    for record in pins["files"]:
        name = record["path"]
        if Path(name).name != name:
            raise ValueError("Only the recorded sibling implementation files are admitted")
        source = HERE / name
        raw = source.read_bytes()
        if len(raw) != record["bytes"] or sha(raw) != record["sha256"]:
            raise ValueError("Original implementation differs: " + name)
        files.append({**record, "path": str(source.resolve())})
    dossier = HERE.parents[1] / "docs/BHSM_ENVELOPMENT_CLAIM_AND_FALSIFIERS_V1.md"
    for path in (pins_path, Path(__file__).resolve(), dossier):
        raw = path.read_bytes()
        files.append({"path": str(path.resolve()), "bytes": len(raw), "sha256": sha(raw)})
    # All preflight reads precede creation; refuse an old output without editing it.
    output.mkdir(parents=True, exist_ok=False)
    freeze_path = output / "LOCAL_REPLAY_FREEZE_v1.json"
    freeze_sha = write_new(freeze_path, {
        "schema": "bhsm.claim_dossier.portable_algebra_replay.v1",
        "scope": "Same16 invented controls at new local paths; not new data or independent repetitions.",
        "files": files,
        "original_full_source_review_repeated": False,
        "native_observations_used": False,
    })
    admission_path = output / "LOCAL_REPLAY_DECISION_v1.json"
    admission_sha = write_new(admission_path, {
        "execution_admitted": True,
        "freeze_sha256": freeze_sha,
        "origin": "Explicit invocation of the portable deterministic algebra replay.",
        "scope": "Only the original invented mathematical controls, after exact local byte checks.",
        "physical_acceptance_or_publication_authorized": False,
    })
    command = [sys.executable, "-B", str(HERE / "run_ideal_claim_controls_v1.py"),
               "--output", str(output / "results"), "--freeze", str(freeze_path),
               "--freeze-sha256", freeze_sha, "--admission-file", str(admission_path),
               "--admission-sha256", admission_sha, "--root-execution-admitted"]
    write_new(output / "COMMAND_v1.json", {
        "argv": command,
        "qualification": "The retained driver flag records a local scoped replay decision; it is not an external approval or scientific certificate.",
    })
    return command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    command = prepare(output)
    if args.prepare_only:
        print(json.dumps({"prepared": True, "executed": False, "command_file": str(output / "COMMAND_v1.json")}))
        return 0
    return subprocess.run(command, cwd=HERE, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
