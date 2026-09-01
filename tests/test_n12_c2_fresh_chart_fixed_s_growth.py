import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
)


def test_fresh_chart_fixed_s_growth_is_certified():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    radius = payload["radius_derivation"]
    assert payload["validation_passed"] is True
    assert radius["selected_growth_chart_radius"] > radius["incoming_endpoint_tube_upper"]
    assert radius["selected_growth_chart_radius"] < radius["fresh_eigenline_chart_radius"]
    assert payload["moving_cubic"]["ball_value_lower"] > 0.0
    assert payload["fresh_line_bounds"]["eigenline_gap_lower"] > 0.0
    assert payload["birth_limit_generator"]["full_action_ball_operator_norm_upper"] > 0.0
    assert payload["current_Gate7_semantic_owner"].startswith("G7_08")
    assert payload["FULL_BHSM_COMPLETE"] is False
