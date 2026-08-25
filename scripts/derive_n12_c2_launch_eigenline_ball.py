"""Build the canonical small action ball for the outgoing C2 launch.

The working tree may contain unrelated edits to shared certificate machinery.
This driver therefore executes the committed canonical source blob when that
machinery is dirty, while a clean exported archive imports the same file
directly.  No worktree file is overwritten.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BASE = ROOT / "artifacts" / "flagship_integration"
RADIUS = "1e-12"
CHECKPOINT = BASE / "BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz"
THIRD = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
ACTION = BASE / "BHSM_N12_C2_LAUNCH_ACTION_MAJORANTS.json"
MIXED = BASE / "BHSM_N12_C2_LAUNCH_EVENT_EIGENLINE_MIXED_MAJORANTS.json"
RESULT = BASE / "BHSM_N12_C2_LAUNCH_EVENT_EIGENLINE_BALL.json"

CANONICAL = {
    "derive_n12_action_ball_majorants": (
        SCRIPTS / "derive_n12_action_ball_majorants.py",
        "78877CF5ED04CBD7A88AB7BF9E50C6D2DE88E1FC50679349FFA3BCC2ABB1592C",
    ),
    "derive_n12_ordered_event_mixed_majorants": (
        SCRIPTS / "derive_n12_ordered_event_mixed_majorants.py",
        "EE720755D5D11CA8E09DEDF827901DBADB0CDFB138C001D709D5D5C69035B2CF",
    ),
    "certify_n12_ordered_event_eigenline_ball": (
        SCRIPTS / "certify_n12_ordered_event_eigenline_ball.py",
        "95A876AB7A4C7E541B8EE4AAD8ACF69BF706D9968369957FB27F2FE124C7A605",
    ),
}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload.replace(b"\r\n", b"\n")).hexdigest().upper()


def _canonical_source(path: Path, expected: str) -> bytes:
    payload = path.read_bytes()
    if _sha256(payload) == expected:
        return payload
    relative = path.relative_to(ROOT).as_posix()
    try:
        payload = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"], cwd=ROOT
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(
            f"canonical source {relative} is dirty and no Git blob is available"
        ) from error
    if _sha256(payload) != expected:
        raise RuntimeError(f"canonical source hash mismatch for {relative}")
    return payload


def _load(name: str) -> types.ModuleType:
    path, expected = CANONICAL[name]
    source = _canonical_source(path, expected)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    sys.modules[name] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(SCRIPTS))
    os.environ.update({
        "BHSM_N12_CERTIFICATE_BALL": RADIUS,
        "BHSM_N12_CHECKPOINT": str(CHECKPOINT.relative_to(ROOT)),
        "BHSM_N12_THIRD_VARIATION_RESULT": str(THIRD.relative_to(ROOT)),
        "BHSM_N12_ACTION_MAJORANT_RESULT": str(ACTION.relative_to(ROOT)),
        "BHSM_N12_ORDERED_MIXED_MAJORANT_RESULT": str(MIXED.relative_to(ROOT)),
        "BHSM_N12_ORDERED_EIGENLINE_BALL_RESULT": str(RESULT.relative_to(ROOT)),
        "BHSM_N12_EIGENLINE_SIDE": "event",
    })
    action_module = _load("derive_n12_action_ball_majorants")
    action_module.main()
    mixed_module = _load("derive_n12_ordered_event_mixed_majorants")
    mixed_module.main()
    eigenline_module = _load("certify_n12_ordered_event_eigenline_ball")
    eigenline_module.main()


if __name__ == "__main__":
    main()
