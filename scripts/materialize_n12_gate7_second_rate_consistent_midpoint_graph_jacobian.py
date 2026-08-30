"""Rebuild midpoint Jacobians on the first repaired rate-consistent center."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_hermite_simpson_midpoint_graph_jacobian as midpoint  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_MIDPOINT_GRAPH_JACOBIAN.json"


def main() -> None:
    midpoint.SOURCE = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY.json"
    midpoint.ENDPOINT = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
    midpoint.THEORY = ROOT / "theory" / "n12_gate7_rate_consistent_newton_midpoint_replay.md"
    midpoint.RESULT = RESULT
    midpoint.DATA = RESULT.with_suffix(".npz")
    midpoint.THIS_SCRIPT = Path(__file__).resolve()
    midpoint.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_MIDPOINT_GRAPH_JACOBIAN"
    payload["status"] = "SECOND_RATE_CONSISTENT_CENTER_370_MIDPOINT_JACOBIANS_MATERIALIZED"
    payload["exact_next_dependency"] = "ASSEMBLE_THE_SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR"
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
