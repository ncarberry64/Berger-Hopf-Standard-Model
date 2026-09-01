import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_LOHNER_GROWTH_1215.json"


def test_lohner_growth_1215() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    radius = payload["radius_derivation"]
    assert payload["validation_passed"] is True
    assert radius["selected_growth_chart_radius"] > radius["incoming_endpoint_tube_upper"]
    assert payload["moving_cubic"]["ball_value_lower"] > 0.0
    assert payload["birth_limit_generator"]["D2F0_action_operator_upper"] > 0.0
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
