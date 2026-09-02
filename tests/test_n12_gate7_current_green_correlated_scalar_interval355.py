import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355.json"


def test_correlated_scalar_removes_interval355_nonfinite_box_result():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["interval"] == 355
    bounds = payload["operand_norm_bounds"]
    assert bounds["midpoint_intrinsic_curvature"]["upper"] < 0.012207
    assert bounds["midpoint_incidence_curvature"]["upper"] < 3.474e-7
    assert bounds["local_HS_second_residual"]["upper"] < 0.003052
    assert payload["claim_boundary"]["CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355_FINITE"]
    assert not payload["claim_boundary"]["CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED"]


def test_axis_error_is_preserved_for_later_mixed_transverse_bound():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    errors = payload["central_axis_neighborhood_error_upper"]
    assert 0.0 < errors["left_node_355"] < 1.0e-6
    assert 0.0 < errors["right_node_356"] < 2.0e-6
    assert payload["validation"][
        "axis_neighborhood_error_deferred_to_mixed_transverse_remainder"
    ]
    assert not payload["claim_boundary"][
        "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED"
    ]
