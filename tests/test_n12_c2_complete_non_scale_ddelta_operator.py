import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_COMPLETE_NON_SCALE_DDELTA_OPERATOR.json"
)


def test_complete_non_scale_ddelta_operator() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == "C2_COMPLETE_NON_SCALE_DDELTA_COVECTOR_TRANSPORT_CERTIFIED"
    assert payload["transport"]["transported_covector_zero_exclusion_margin_lower"] > 0.0
    assert (
        payload["decomposition"]["complete_non_scale_D2Delta_operator_2_norm_upper"]
        < payload["transport"]["complete_operator_transport_ceiling"]
    )
    assert payload["common_scale_direction"]["numerically_deleted"] is False
    assert payload["adjudication"]["complete_non_scale_D2Delta_operator"] == "CERTIFIED"
    assert payload["adjudication"]["transposed_exact_segment_map_action"] == "OPEN_CURRENT_OWNER"
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
