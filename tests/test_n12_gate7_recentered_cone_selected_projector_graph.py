import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_RECENTERED_CONE_SELECTED_PROJECTOR_GRAPH.json"
)


def test_recentered_cone_selected_projector_graph_is_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["mesh"]["projection_dimension"] == 101
    assert payload["summary"][
        "maximum_selected_projector_motion_upper"
    ] < 1.0
    assert payload["claim_boundary"][
        "recentered_cone_selected_projector_graph"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "recentered_cone_bordered_response"
    ] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
