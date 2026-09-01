import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CAUSAL_VECTOR_RADIUS_RECONNAISSANCE.json"
)


def test_causal_vector_radius_reconnaissance_is_structural_not_promoted():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    summary = payload["summary"]
    assert payload["structural_validation_passed"] is True
    assert payload["validation_passed"] is False
    assert payload["identity"]["triangular_dependency"] == (
        "STRICTLY_LOWER_CAUSAL_IN_NODE_INDEX"
    )
    assert summary["nodes"] == 48
    assert summary["seams"] == 47
    assert summary["maximum_nonlinear_delta_radius"] < 1.4e-8
    assert summary["maximum_total_radius"] < 3.5e-6
    assert payload["claim_boundary"]["between_seam_retained_action_curvature"] == (
        "OPEN_INTERVAL_AUTHORITY"
    )
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
