import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_RECENTERED_CONE_BOUNDARY_CLUSTER_SPECTRUM.json"
)


def test_recentered_cone_boundary_cluster_spectrum_is_scoped():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["domain"]["base_center"].endswith(
        "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
    )
    assert payload["domain"]["center_correction"].endswith(
        "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_"
        "CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
    )
    assert payload["domain"]["nonlinear_radius_authority"].endswith(
        "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
    )
    assert payload["domain"]["nonlinear_halo_action_radius"] == (
        1.243972269022099e-12
    )
    assert payload["mesh"]["projection_dimension"] == 101
    assert payload["summary"][
        "minimum_selected_line_boundary_gap_lower"
    ] > 0.0
    assert payload["claim_boundary"][
        "recentered_cone_selected_line_simplicity"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "recentered_cone_selected_projector_graph"
    ] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
