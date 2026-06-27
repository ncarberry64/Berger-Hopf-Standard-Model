from __future__ import annotations

from bhsm.interface.minimal_action import close_minimal_action


def test_cp_o_int_stops_at_action_source() -> None:
    result = close_minimal_action("cp_o_int")
    assert result.status_before == "OPEN_MISSING_ACTION_SOURCE"
    assert result.status_after == "OPEN_MISSING_ACTION_SOURCE"
    assert result.promoted is False
    assert result.remaining_missing_object == (
        "action-derived CP O_int source with normalized coupling, measure, variation, and production rule"
    )
    assert result.action_source_term.action_derived is False
    assert result.production_rule.production_eligible is False
    assert result.production_rule.callable_available is False


def test_cp_result_uses_phase_artifacts_not_reference_inputs() -> None:
    result = close_minimal_action("cp_o_int")
    assert "artifacts/BHSM_cp_o_int_field_action_report_v0_6.json" in result.artifact_sources_used
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.pdg_values_used_as_theorem_inputs is False
    assert result.w_calibration_used_as_theorem_input is False
    assert result.runtime_gates_changed is False


def test_complete_explicit_axiom_is_conditional_not_established() -> None:
    definitions = {
        "field_representation": "author CP field representation",
        "lorentz_structure": "author Lorentz scalar",
        "gauge_representation": "author gauge singlet",
        "coupling_normalization": "author normalized coupling",
        "operator_mass_dimension": "4",
        "coupling_mass_dimension": "0",
        "action_source": "author local action density",
        "measure": "d4x",
        "locality": "local",
        "variation": "delta S / delta O_int",
        "production_rule": "author production rule",
    }
    payload = {"axioms": [{
        "axiom_key": "CP_TEST_AXIOM",
        "enabled": True,
        "complete_definition": True,
        "affected_theorems": ["cp_o_int"],
        "maximum_status": "CONDITIONAL_ACTION_THEOREM",
        "definitions": definitions,
    }]}
    result = close_minimal_action("cp_o_int", axioms=payload)
    assert result.status_after == "CONDITIONAL_ACTION_THEOREM"
    assert result.promoted is True
    assert all(result.proof_gates.values())
    assert result.remaining_missing_object is None
