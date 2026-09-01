"""Rebuild the graph Jacobian on the second current-linearization center."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import materialize_n12_gate7_signed_green_current_center_graph_jacobian as graph  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN.json"


def main() -> None:
    graph.CENTER = BASE / "BHSM_N12_GATE7_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE.json"
    graph.CENTER_DATA = graph.CENTER.with_suffix(".npz")
    graph.PRIOR = BASE / "BHSM_N12_GATE7_SIGNED_GREEN_CURRENT_CENTER_GRAPH_JACOBIAN.json"
    graph.THEORY = ROOT / "theory" / "n12_gate7_second_current_center_graph_jacobian.md"
    graph.RESULT = RESULT
    graph.DATA = RESULT.with_suffix(".npz")
    graph.THIS_SCRIPT = Path(__file__).resolve()
    graph.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN"
    payload["status"] = "SECOND_CURRENT_CENTER_371_NODE_GRAPH_JACOBIAN_MATERIALIZED"
    payload["adjudication"] = {
        "first_current_center_graph_Jacobian": "SUPERSEDED_FOR_THIRD_NEWTON_PREDICTION",
        "second_current_center_graph_Jacobian": "MATERIALIZED_NUMERICAL_PREDICTOR",
        "retained_directional_and_between_node_interval_replay": "OPEN_AFTER_NEWTON_CONVERGENCE",
    }
    payload["exact_next_dependency"] = (
        "APPLY_A_THIRD_SIGNED_GREEN_NEWTON_STEP_WITH_THIS_GRAPH_AND_THE_"
        "SECOND_CURRENT_CENTER_MACRO_TANGENTS"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
