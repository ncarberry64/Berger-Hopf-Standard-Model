from __future__ import annotations

from bhsm.interface.neutrino_propagation import build_neutrino_propagation_report


def test_neutrino_propagation_theorem_builds_offline() -> None:
    report = build_neutrino_propagation_report()
    closure = report.closure
    assert closure.status_before == "CONDITIONAL_PROPAGATION_THEOREM"
    assert closure.status_after == "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE"
    assert closure.promoted is True
    assert closure.internet_required is False
    assert closure.external_hep_tools_required is False
    assert closure.neutral_kernel.status == "ESTABLISHED_ARTIFACT_BACKED"
    assert report.field.interpretation.startswith("physical neutral boundary-local field")


def test_neutrino_theorem_uses_no_empirical_or_calibration_inputs() -> None:
    closure = build_neutrino_propagation_report().closure
    assert closure.empirical_derivation_inputs_used is False
    assert closure.reference_values_used_as_theorem_inputs is False
    assert closure.electron_neutrino_upper_limit_used_as_derivation_input is False
    assert closure.w_mass_used_as_theorem_input is False
    assert closure.frozen_predictions_changed is False
    assert closure.production_physics_model_logic_changed is False
