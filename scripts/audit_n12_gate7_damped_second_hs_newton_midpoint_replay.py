"""Replay the damped second Hermite--Simpson midpoint residual."""

from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_n12_gate7_second_hermite_simpson_newton_midpoint_replay as replay  # noqa: E402
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_MIDPOINT_REPLAY.json"


def main() -> None:
    replay.PARENT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
    replay.ENDPOINT = BASE / "BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_ENDPOINT_CANDIDATE.json"
    replay.THEORY = ROOT / "theory" / "n12_gate7_damped_second_hs_newton_midpoint_replay.md"
    replay.RESULT = RESULT
    replay.DATA = RESULT.with_suffix(".npz")
    replay.THIS_SCRIPT = Path(__file__).resolve()
    replay.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_MIDPOINT_REPLAY"
    payload["status"] = (
        "DAMPED_SECOND_BLOCK_NEWTON_REDUCES_NONLINEAR_RESIDUAL"
        if payload["validation_passed"] else
        "DAMPED_SECOND_BLOCK_NEWTON_DOES_NOT_REDUCE_NONLINEAR_RESIDUAL"
    )
    payload["exact_next_dependency"] = (
        "IF_REDUCED,_REBUILD_AND_CONTINUE_WITH_RESIDUAL_BASED_GLOBALIZATION;_"
        "OTHERWISE_REJECT_THE_CURRENT_LINE_SEARCH_MODEL"
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
