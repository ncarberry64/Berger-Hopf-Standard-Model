import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESPONSE = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_LOHNER_RESPONSE_BALL_1215.json"
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_LOHNER_STEP_1216.json"


def test_lohner_step_1216() -> None:
    response = json.loads(RESPONSE.read_text(encoding="utf-8"))
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert response["validation_passed"] is True
    assert payload["validation_passed"] is True
    assert payload["segment"]["prior_certified_segments"] == 1215
    assert payload["segment"]["total_certified_segments"] == 1216
    assert payload["segment"]["stored_step_action_norm"] > 0.0
    assert payload["segment"]["joint_domain_use_upper"] < payload["domain"]["selected_domain_radius"]
    assert payload["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
