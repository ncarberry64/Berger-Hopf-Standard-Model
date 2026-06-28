from __future__ import annotations

import pytest

from bhsm.interface.neutrino_action import build_neutral_action_spectral_closure


def test_default_action_closure_produces_no_dimensionful_mass() -> None:
    result = build_neutral_action_spectral_closure()
    assert result.status == "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE"
    assert result.dimensionful_mass_status == "DIMENSIONFUL_MASS_NOT_AVAILABLE"
    assert result.dimensionful_mass_available is False
    assert result.inverse_length_gap_per_m is None
    assert result.mass_kg is None
    assert result.mass_eV is None
    assert result.mass_GeV is None


def test_dimensionful_path_requires_both_explicit_unit_inputs() -> None:
    length_only = build_neutral_action_spectral_closure(stiffness_length_m=2.0)
    curvature_only = build_neutral_action_spectral_closure(curvature_per_m2=3.0)
    complete = build_neutral_action_spectral_closure(stiffness_length_m=2.0, curvature_per_m2=3.0)
    assert length_only.dimensionful_mass_available is False
    assert curvature_only.dimensionful_mass_available is False
    assert complete.status == "DIMENSIONFUL_MASS_AVAILABLE"
    assert complete.inverse_length_gap_per_m == pytest.approx(6.0)
    assert complete.mass_eV is not None

