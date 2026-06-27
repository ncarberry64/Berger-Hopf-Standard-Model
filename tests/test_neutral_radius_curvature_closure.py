from __future__ import annotations

from bhsm.interface.neutrino_scale import build_neutral_radius_curvature_closure


def test_coupled_closure_reports_symbolic_but_not_numeric_bridge() -> None:
    result = build_neutral_radius_curvature_closure()
    assert result.status == "DIMENSIONFUL_MASS_NOT_AVAILABLE"
    assert result.symbolic_bridge_available is True
    assert result.numeric_bridge_available is False
    assert result.radius.status == "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE"
    assert result.curvature_map.status == "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE"


def test_legacy_functional_fails_mass_dimension_gate() -> None:
    result = build_neutral_radius_curvature_closure()
    assert result.dimensional_consistency_passed is False
    assert result.legacy_functional_output_dimension == "mass_per_length"
    assert "dimensionally consistent mass normalization" in result.remaining_missing_object

