"""Replay the retained signed mixed-curvature identity for final Y."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_exact_signed_mixed_field_curvature as retained  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
GREEN = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.npz"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_MIXED_FIELD_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")
retained.GREEN = GREEN
retained.RESULT = RESULT
retained.DATA = DATA


def main() -> None:
    payload = retained.build_payload()
    payload["artifact"] = "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_MIXED_FIELD_CURVATURE"
    if payload["validation_passed"]:
        payload["status"] = "FINAL_EXACT_AFFINE_SIGNED_MIXED_FIELD_CURVATURE_DERIVED"
    payload["inputs"][retained._relative(Path(__file__).resolve())] = retained._sha256(
        Path(__file__).resolve()
    )
    retained_script = Path(retained.__file__).resolve()
    payload["inputs"][retained._relative(retained_script)] = retained._sha256(
        retained_script
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": payload["validation_passed"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
