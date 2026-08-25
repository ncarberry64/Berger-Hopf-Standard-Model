import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_BIRTH_LIMIT_CONJUGATED_TANGENT_REMAINDER.json"
)


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_birth_limit_conjugated_tangent_remainder_certified():
    payload = _payload()
    assert payload["validation_passed"] is True
    assert "CERTIFIED" in payload["status"]
    assert payload["moving_cubic"]["ball_value_lower"] > 0.0
    assert payload["selected_line"]["normal_plane_rotation_upper"] < 1.0
    assert payload["conjugated_growth"]["total_birth_limit_tangent_growth_upper"] >= 1.0
    assert payload["conjugated_growth"]["total_birth_limit_full_ball_growth_upper"] >= 1.0
    assert (
        payload["physical_tube"]["current_combined_action_radius_upper"]
        < payload["physical_tube"]["certified_matrix_center_ball_radius"]
    )


def test_finite_s_correction_and_gate_status_are_not_overclaimed():
    payload = _payload()
    assert payload["adjudication"]["finite_s_correction_sG"].startswith("OPEN")
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
