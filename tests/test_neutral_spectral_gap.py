from __future__ import annotations

import pytest

from bhsm.interface.neutrino_spectral import build_neutral_spectral_gap_candidate


def test_symbolic_spectral_gap_produces_no_numeric_mass() -> None:
    result = build_neutral_spectral_gap_candidate()
    assert result.status == "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE"
    assert result.inverse_length_gap_available is False
    assert result.dimensionful_mass_available is False
    assert result.dimensionful_mass_kg is None
    assert result.dimensionful_mass_eV is None
    assert result.dimensionful_mass_GeV is None


def test_physical_mass_unit_path_requires_both_dimensional_inputs() -> None:
    only_length = build_neutral_spectral_gap_candidate(stiffness_length_m=2.0)
    only_curvature = build_neutral_spectral_gap_candidate(curvature_per_m2=3.0)
    complete = build_neutral_spectral_gap_candidate(stiffness_length_m=2.0, curvature_per_m2=3.0)
    assert only_length.dimensionful_mass_available is False
    assert only_curvature.dimensionful_mass_available is False
    assert complete.inverse_length_gap_per_m == pytest.approx(6.0)
    assert complete.dimensionful_mass_kg is not None
    assert complete.dimensionful_mass_eV is not None


def test_zero_propagation_removes_conditional_mass_contribution() -> None:
    result = build_neutral_spectral_gap_candidate(
        stiffness_length_m=2.0,
        curvature_per_m2=3.0,
        propagating=False,
    )
    assert result.inverse_length_gap_per_m == 0.0
    assert result.dimensionful_mass_kg == 0.0
    assert result.zero_propagation_mass_vanishes is True

