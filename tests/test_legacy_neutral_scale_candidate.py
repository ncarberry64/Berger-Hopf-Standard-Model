from __future__ import annotations

from bhsm.interface.neutrino_scale import (
    build_legacy_curvature_scale_report,
    build_legacy_neutral_scale_candidate,
)


def test_legacy_candidate_requires_radius_and_physical_curvature() -> None:
    candidate = build_legacy_neutral_scale_candidate()
    assert candidate.mass_functional_available is True
    assert candidate.propagation_radius_available is False
    assert candidate.neutral_curvature_mapping_available is True
    assert candidate.physical_curvature_units_available is False
    assert candidate.dimensionful_mass_possible is False
    assert candidate.dimensionful_mass_eV is None
    assert candidate.dimensionful_mass_GeV is None
    assert candidate.candidate_status == "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS"


def test_report_uses_no_empirical_or_reference_theorem_inputs() -> None:
    report = build_legacy_curvature_scale_report()
    result = report.result
    assert report.legacy_particle_tables_used_as_derivation_inputs is False
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.electron_neutrino_limit_used_as_derivation_input is False
    assert result.w_mass_used_as_theorem_input is False
    assert report.frozen_predictions_changed is False

