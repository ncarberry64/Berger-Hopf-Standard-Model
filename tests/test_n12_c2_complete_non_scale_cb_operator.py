import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_COMPLETE_NON_SCALE_CB_OPERATOR.json"
)


def test_complete_non_scale_cb_operator() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == "C2_COMPLETE_NON_SCALE_CB_OPERATOR_CERTIFIED"
    assert payload["row_count"] == 97
    assert payload["row_range"] == [1, 97]
    assert payload["common_scale_row_0"]["status"] == "CLOSED_BY_EXACT_COVARIANCE"
    assert payload["operator"]["non_scale_cb_Frobenius_upper"] > 0.0
    assert payload["bootstrap"]["maximum_b_i_radius_needed"] < payload["bootstrap"]["b_i_radius_available"]
    assert payload["bootstrap"]["maximum_c_i_radius_needed"] < payload["bootstrap"]["c_i_radius_available"]
    assert payload["adjudication"]["complete_non_scale_cb_operator"] == "CERTIFIED"
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
