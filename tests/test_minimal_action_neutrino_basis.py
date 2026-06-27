from __future__ import annotations

from bhsm.interface.minimal_action import close_minimal_action
from bhsm.interface.minimal_action.neutrino_basis_closure import (
    propagation_conditioned_neutrino_mass,
)


def test_neutrino_closes_as_conditional_propagation_theorem() -> None:
    result = close_minimal_action("neutrino_basis_scale")
    assert result.status_after == "CONDITIONAL_PROPAGATION_THEOREM"
    assert result.promoted is True
    assert result.remaining_missing_object is None
    assert result.field_representation.status == "CONDITIONAL_PROPAGATION_THEOREM"
    assert result.coupling_normalization.status == "CONDITIONAL_PROPAGATION_THEOREM"
    assert result.target_disposition == "PROPAGATION_CONDITIONED_EFFECTIVE_MASS"
    assert result.numerical_closure_open is True
    assert result.action_source_term.action_derived is False
    assert all(result.proof_gates.values())


def test_neutrino_attempt_uses_no_limits_references_or_calibration() -> None:
    result = close_minimal_action("neutrino_basis_scale")
    assert "R_curv" in result.action_term.expression
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.pdg_values_used_as_theorem_inputs is False
    assert result.w_calibration_used_as_theorem_input is False
    assert result.production_rule.production_eligible is False
    assert result.hep_runtime_readiness_claimed is False


def test_neutrino_effective_mass_is_locked_to_propagation_and_threshold() -> None:
    assert propagation_conditioned_neutrino_mass(3.5, propagating=True, threshold_met=True) == 3.5
    assert propagation_conditioned_neutrino_mass(3.5, propagating=False, threshold_met=True) == 0
    assert propagation_conditioned_neutrino_mass(3.5, propagating=True, threshold_met=False) == 0
