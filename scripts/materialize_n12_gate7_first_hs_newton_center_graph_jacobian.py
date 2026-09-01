"""Rebuild endpoint graph Jacobians on the first Hermite--Simpson Newton center."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import materialize_n12_gate7_signed_green_current_center_graph_jacobian as graph  # noqa: E402

BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_CENTER_GRAPH_JACOBIAN.json"


def main() -> None:
    graph.CENTER = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE.json"
    graph.CENTER_DATA = graph.CENTER.with_suffix(".npz")
    graph.PRIOR = BASE / "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN.json"
    graph.THEORY = ROOT / "theory" / "n12_gate7_first_hs_newton_center_graph_jacobian.md"
    graph.RESULT = RESULT
    graph.DATA = RESULT.with_suffix(".npz")
    graph.THIS_SCRIPT = Path(__file__).resolve()
    graph.main()
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["artifact"] = "BHSM_N12_GATE7_FIRST_HS_NEWTON_CENTER_GRAPH_JACOBIAN"
    payload["status"] = "FIRST_HS_NEWTON_CENTER_371_ENDPOINT_JACOBIANS_MATERIALIZED"
    payload["exact_next_dependency"] = "ASSEMBLE_THE_SECOND_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR"
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
