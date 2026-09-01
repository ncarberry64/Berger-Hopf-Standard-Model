"""Rebuild endpoint Jacobians on the first repaired rate-consistent center."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_signed_green_current_center_graph_jacobian as graph  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_CENTER_GRAPH_JACOBIAN.json"


def main() -> None:
    graph.CENTER = BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.json"
    graph.CENTER_DATA = graph.CENTER.with_suffix(".npz")
    graph.PRIOR = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_CENTER_GRAPH_JACOBIAN.json"
    graph.THEORY = ROOT / "theory" / "n12_gate7_rate_consistent_newton_endpoint_candidate.md"
    graph.RESULT = RESULT
    graph.DATA = RESULT.with_suffix(".npz")
    graph.THIS_SCRIPT = Path(__file__).resolve()
    graph.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_CENTER_GRAPH_JACOBIAN"
    payload["status"] = "SECOND_RATE_CONSISTENT_CENTER_371_ENDPOINT_JACOBIANS_MATERIALIZED"
    payload["exact_next_dependency"] = "REBUILD_THE_370_RATE_CONSISTENT_MIDPOINT_JACOBIANS"
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
