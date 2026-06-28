from __future__ import annotations

from bhsm.interface.minimal_action import close_minimal_action
from bhsm.interface.minimal_action.x_ch_closure import apply_x_ch_boundary_response


def test_x_ch_closes_conditionally_as_boundary_response() -> None:
    result = close_minimal_action("X_ch")
    assert result.status_after == "CONDITIONAL_ACTION_THEOREM"
    assert result.promoted is True
    assert result.remaining_missing_object is None
    assert result.field_representation.symbol == "X_ch"
    assert result.field_representation.status == "CONDITIONAL_ACTION_THEOREM"
    assert result.production_rule.production_eligible is False
    assert result.action_source_term.action_derived is False
    assert result.target_disposition == "BOUNDARY_RESPONSE_OPERATOR"
    assert all(result.proof_gates.values())


def test_x_ch_source_matrix_is_not_used_as_field_theorem() -> None:
    result = close_minimal_action("X_ch")
    assert "X_ch(P_ch Psi_boundary)" in result.action_term.expression
    assert "artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json" in result.artifact_sources_used
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.w_calibration_used_as_theorem_input is False
    assert result.author_ontology_used is True
    assert result.hep_runtime_readiness_claimed is False


def test_x_ch_callable_preserves_the_boundary_response_chain() -> None:
    response = apply_x_ch_boundary_response("Psi_boundary")
    assert response == {
        "boundary_field": "Psi_boundary",
        "projected_field": "P_ch(Psi_boundary)",
        "response": "X_ch(P_ch(Psi_boundary))",
        "attachment": "charged-current response",
    }
