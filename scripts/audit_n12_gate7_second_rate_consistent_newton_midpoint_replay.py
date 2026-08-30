"""Replay exact midpoints after the second rate-consistent Newton step."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_n12_gate7_first_hs_tangent_newton_midpoint_replay as replay  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY.json"


def main() -> None:
    replay.PARENT = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY.json"
    replay.ENDPOINT = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
    replay.THEORY = ROOT / "theory" / "n12_gate7_rate_consistent_newton_midpoint_replay.md"
    replay.RESULT = RESULT
    replay.DATA = RESULT.with_suffix(".npz")
    replay.THIS_SCRIPT = Path(__file__).resolve()
    replay.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY"
    payload["status"] = (
        "SECOND_RATE_CONSISTENT_NEWTON_STEP_REDUCES_NONLINEAR_HERMITE_SIMPSON_RESIDUAL"
        if payload["validation_passed"] else
        "SECOND_RATE_CONSISTENT_NEWTON_STEP_DOES_NOT_REDUCE_NONLINEAR_RESIDUAL"
    )
    payload["mesh"].pop("endpoint_tangent_dimension", None)
    payload["mesh"]["endpoint_map"] = "SECOND_CONSTRAINT_PROJECTED_ONE_JET_DESCRIPTOR_RATE_RECENTER"
    payload["validation"][
        "second_rate_consistent_step_reduces_nonlinear_Hermite_Simpson_residual"
    ] = payload["validation"].pop(
        "intrinsic_tangent_step_reduces_nonlinear_Hermite_Simpson_residual"
    )
    payload["adjudication"] = {
        "first_rate_consistent_center": "PARENT",
        "second_rate_consistent_Newton_step": (
            "ACCEPTED_FOR_NEXT_ITERATION" if payload["validation_passed"]
            else "REJECTED_BY_EXACT_NONLINEAR_REPLAY"
        ),
    }
    payload["exact_next_dependency"] = (
        "IF_REDUCED,_REBUILD_THE_CURRENT_CENTER_JACOBIANS_AND_ITERATE;_"
        "OTHERWISE_DIFFERENTIATE_THE_COMPLETE_PROJECTED_RECENTERED_RESIDUAL_MAP"
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
