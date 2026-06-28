from __future__ import annotations

from bhsm.interface.neutrino_spectral import audit_legacy_gravitational_mass_formula_dimensions


def test_legacy_expression_is_mass_per_length_not_mass() -> None:
    result = audit_legacy_gravitational_mass_formula_dimensions()
    assert result.status == "DIMENSIONALLY_GATED_LEGACY_FUNCTIONAL"
    assert result.curvature_dimension == "length^-2"
    assert result.radius_squared_curvature_dimension == "dimensionless"
    assert result.formula_output_dimension == "mass_per_length"
    assert result.physical_mass_dimension_passed is False
    assert result.numeric_particle_mass_output_allowed is False
    assert result.legacy_gravitational_formula_used_as_mass_formula is False

