from __future__ import annotations

from bhsm.interface.minimal_action import close_minimal_action


def test_neutrino_closure_stops_at_physical_basis() -> None:
    result = close_minimal_action("neutrino_basis_scale")
    assert result.status_after == "OPEN_MISSING_PHYSICAL_BASIS"
    assert result.promoted is False
    assert result.remaining_missing_object == (
        "map from the neutral boundary channel basis to physical neutrino states"
    )
    assert result.field_representation.status == "ARTIFACT_BACKED"
    assert result.coupling_normalization.status == "OPEN_MISSING_DIMENSIONAL_SCALE"


def test_neutrino_attempt_uses_no_limits_references_or_calibration() -> None:
    result = close_minimal_action("neutrino_basis_scale")
    assert "K_nu" in result.action_term.expression
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.pdg_values_used_as_theorem_inputs is False
    assert result.w_calibration_used_as_theorem_input is False
    assert result.production_rule.production_eligible is False
