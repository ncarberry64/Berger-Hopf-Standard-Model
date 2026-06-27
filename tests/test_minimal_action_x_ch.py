from __future__ import annotations

from bhsm.interface.minimal_action import close_minimal_action


def test_x_ch_stops_at_field_representation() -> None:
    result = close_minimal_action("X_ch")
    assert result.status_after == "OPEN_MISSING_FIELD_REPRESENTATION"
    assert result.promoted is False
    assert result.remaining_missing_object == "action-derived X_ch field representation"
    assert result.field_representation.symbol == "X_ch^mu"
    assert result.field_representation.status == "OPEN_MISSING_FIELD_REPRESENTATION"
    assert result.production_rule.production_eligible is False


def test_x_ch_source_matrix_is_not_used_as_field_theorem() -> None:
    result = close_minimal_action("X_ch")
    assert "C_ch_boundary" in result.action_term.expression
    assert "artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json" in result.artifact_sources_used
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.w_calibration_used_as_theorem_input is False
