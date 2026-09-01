import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FAST_CANCELLED_DELTA_IDENTITY_AUDIT.json"
)


def test_combined_direction_replays_split_cancelled_delta() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["summary"]["maximum_Delta_absolute_residual"] < 1.0e-21
    assert all(row["selected_branch"] == 24 for row in payload["rows"])
    assert max(row["field_action_residual_2_norm"] for row in payload["rows"]) < 1.0e-12
    assert max(row["b_psi_residual"] for row in payload["rows"]) < 1.0e-12


def test_combined_direction_is_only_an_algebraic_acceleration() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    validation = payload["validation"]
    assert validation["linearity_of_Dlambda_used_before_floating_point_evaluation"] is True
    assert validation["retained_action_and_inverse_free_selected_complement_unchanged"] is True
    assert validation["no_action_equation_stop_selector_scale_gate_or_chord_changed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
