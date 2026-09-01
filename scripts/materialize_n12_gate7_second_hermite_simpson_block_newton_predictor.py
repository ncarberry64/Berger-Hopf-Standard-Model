"""Solve the second Hermite--Simpson block Newton predictor."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_hermite_simpson_block_newton_predictor as predictor  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"


def main() -> None:
    predictor.SOURCE = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
    predictor.ENDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_CENTER_GRAPH_JACOBIAN.json"
    predictor.MIDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_MIDPOINT_GRAPH_JACOBIAN.json"
    predictor.THEORY = ROOT / "theory" / "n12_gate7_second_hermite_simpson_block_newton_predictor.md"
    predictor.RESULT = RESULT
    predictor.DATA = RESULT.with_suffix(".npz")
    predictor.THIS_SCRIPT = Path(__file__).resolve()
    predictor.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR"
    payload["mesh"]["Newton_iteration"] = 2
    payload["exact_next_dependency"] = "APPLY_AND_CONSTRAINT_PROJECT_THE_SECOND_BLOCK_NEWTON_CORRECTION"
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
