import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_BORDERED_RESPONSE_SECOND_VARIATION_BALL.json"


def test_bordered_response_second_variation_ball() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["ball"]["relative_second_variation_self_consistency"] < 1.0
    assert payload["ball"]["b_psi_interval"][0] > 0.0
    assert payload["adjudication"]["hard_response_second_variation"].startswith("CERTIFIED")
    assert payload["adjudication"]["full_fixed_s_field_interval"].startswith("OPEN")
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
