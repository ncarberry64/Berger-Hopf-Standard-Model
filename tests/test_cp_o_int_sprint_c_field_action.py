from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_sprint_c_report import build_cp_o_int_field_action_report

ROOT = Path(__file__).resolve().parents[1]


def test_field_action_candidate_advances_localization_not_closure():
    result = build_cp_o_int_field_action_report(repository=ROOT)
    assert result.candidate_status == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert result.status_before == "OPEN_MISSING_INTERACTION_ATTACHMENT"
    assert result.status_after == "OPEN_MISSING_ACTION_SOURCE"
    assert result.deepest_valid_stage_before.startswith("Stage 2")
    assert result.deepest_valid_stage_after.startswith("Stage 8")
    assert result.first_failed_required_stage.startswith("Stage 9")
    assert result.promoted is False
    assert result.action_level_closure_achieved is False


def test_field_representation_is_explicitly_symbolic_and_incomplete():
    field = build_cp_o_int_field_action_report(repository=ROOT).field_factor
    assert field["status"] == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert field["is_placeholder"] is True
    assert field["chirality_defined"] is False
    assert field["family_indices_defined"] is False
    assert "physical field representation" in field["missing_object"]
