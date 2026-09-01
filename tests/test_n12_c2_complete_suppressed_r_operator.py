import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_COMPLETE_SUPPRESSED_R_OPERATOR.json"
)


def test_complete_suppressed_r_operator_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == "C2_COMPLETE_SUPPRESSED_R_OPERATOR_CERTIFIED"
    containment = payload["parent_ball_containment"]
    assert containment["containing_radius_upper"] < containment["terminal_parent_action_radius"]
    assert containment["strict_margin_lower"] > 0.0
    assert len(payload["raw_R_second_operator_term_uppers"]) == 11
    assert payload["complete_s_suppressed_R_second_operator_2_norm_upper"] > 0.0
    assert payload["adjudication"]["complete_non_scale_sR_operator"] == "CERTIFIED"
    assert payload["adjudication"]["complete_non_scale_D2Delta_operator"].startswith("OPEN")
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
