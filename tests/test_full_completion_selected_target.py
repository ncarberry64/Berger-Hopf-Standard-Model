from __future__ import annotations

from fractions import Fraction

from bhsm.interface.full_completion import (
    boundary_jacobian_normalization,
    build_boundary_measure_closure,
    collar_jacobian_from_principal_curvatures,
    same_scale_boundary_transport,
)


def test_collar_jacobian_and_boundary_normalization_are_exact() -> None:
    kappas = (Fraction(2), Fraction(-1))
    assert collar_jacobian_from_principal_curvatures(Fraction(1, 4), kappas) == Fraction(9, 8)
    assert boundary_jacobian_normalization(kappas) == 1


def test_identity_transport_does_not_infer_cross_scale_running() -> None:
    assert same_scale_boundary_transport("mu_BH_boundary", "mu_BH_boundary") == 1
    assert same_scale_boundary_transport("mu_BH_boundary", "M_Z") is None


def test_selected_closure_is_partial_and_unit_safe() -> None:
    result = build_boundary_measure_closure()
    assert result.closure_result == "PARTIAL_CLOSURE_BOUNDARY_MEASURE_SHAPE_AND_IDENTITY_TRANSPORT"
    assert result.collar_shape_derived_conditionally is True
    assert result.boundary_value_exact is True
    assert result.same_scale_transport_exact is True
    assert result.physical_measure_normalization_available is False
    assert result.cross_scale_transport_available is False
    assert result.physical_units_available is False
    assert result.empirical_inputs_used is False
    assert result.official_prediction_logic_changed is False
    assert result.frozen_predictions_changed is False
