from __future__ import annotations

from bhsm.interface.neutrino_scale import (
    build_neutral_radius_curvature_closure,
    compute_dimensionful_neutrino_mass_candidate,
)


def test_current_candidate_emits_no_kg_ev_or_gev() -> None:
    result = compute_dimensionful_neutrino_mass_candidate(build_neutral_radius_curvature_closure())
    assert result.status == "DIMENSIONFUL_MASS_NOT_AVAILABLE"
    assert result.dimensionful_mass_available is False
    assert result.dimensionful_mass_kg is None
    assert result.dimensionful_mass_eV is None
    assert result.dimensionful_mass_GeV is None


def test_numeric_radius_and_curvature_do_not_bypass_dimension_gate() -> None:
    result = compute_dimensionful_neutrino_mass_candidate(
        build_neutral_radius_curvature_closure(),
        radius_m=1.0,
        curvature_per_m2=1.0,
    )
    assert result.dimensionful_mass_available is False
    assert result.formula_output_dimension == "mass_per_length"
    assert "kg/m, not kg" in result.remaining_missing_object

