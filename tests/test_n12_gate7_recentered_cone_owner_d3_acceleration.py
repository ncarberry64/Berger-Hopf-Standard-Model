import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_RECENTERED_CONE_OWNER_D3_ACCELERATION_AUDIT.json"
)


def test_recentered_cone_owner_d3_acceleration_is_retained_crosschecked():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert len(payload["rows"]) == 101
    assert payload["validation"][
        "all_101_owner_projection_directions_replayed"
    ] is True
    assert payload["claim_boundary"][
        "owner_cell_JAX_D3_acceleration"
    ] == "RETAINED_CROSSCHECKED"
    assert payload["claim_boundary"][
        "recentered_cone_selected_projector_graph"
    ] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
