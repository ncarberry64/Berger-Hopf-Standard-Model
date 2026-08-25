import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"


def test_cancelled_field_lohner_step() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["segment"]["total_certified_segments"] == 1215
    assert payload["segment"]["stored_step_action_norm"] > 0.0
    assert payload["segment"]["endpoint_tube_radius_upper"] < payload["domain"]["selected_domain_radius"]
    assert payload["segment"]["joint_domain_use_upper"] < payload["domain"]["selected_domain_radius"]
    assert payload["second_variation"][
        "s_times_cancelled_correction_second_variation_upper"
    ] < payload["second_variation"]["birth_limit_second_variation_upper"]
    assert payload["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
