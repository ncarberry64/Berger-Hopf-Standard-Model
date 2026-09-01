"""Solve the second rate-consistent ambient Hermite--Simpson block step."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_hermite_simpson_block_newton_predictor as predictor  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR.json"


def main() -> None:
    predictor.SOURCE = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY.json"
    predictor.ENDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_CENTER_GRAPH_JACOBIAN.json"
    predictor.MIDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_MIDPOINT_GRAPH_JACOBIAN.json"
    predictor.THEORY = ROOT / "theory" / "n12_gate7_rate_consistent_block_newton_predictor.md"
    predictor.RESULT = RESULT
    predictor.DATA = RESULT.with_suffix(".npz")
    predictor.THIS_SCRIPT = Path(__file__).resolve()
    predictor.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR"
    payload["status"] = (
        "SECOND_RATE_CONSISTENT_AMBIENT_BLOCK_NEWTON_PREDICTOR_SOLVED"
        if payload["validation_passed"] else "SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR_INVALID"
    )
    payload["exact_next_dependency"] = (
        "APPLY_THE_SECOND_CORRECTION,_PROJECT_AND_RECENTER_EACH_ENDPOINT,_"
        "REEVALUATE_EACH_RATE_AT_ITS_SAME_DESCRIPTOR,_AND_REPLAY_ALL_MIDPOINTS"
    )
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
