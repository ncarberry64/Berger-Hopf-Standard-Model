from __future__ import annotations

from fractions import Fraction

from bhsm.interface.completion.full_dirac_a4_trace_v14_50 import (
    a4_global_scale_weight,
    berger_cylinder_integrated_shape,
    berger_cylinder_weyl_density,
    berger_shape_derivative,
    canonical_sm_generation_trace,
    completion_payload,
    curvature_response_r2_shift_polynomial,
    ray_preserving_curvature_response_values,
)


def test_canonical_sm_trace() -> None:
    trace = canonical_sm_generation_trace()
    assert trace.hypercharge == Fraction(10, 3)
    assert trace.su2 == 2
    assert trace.su3 == 2
    assert trace.normalized_to_su2() == (Fraction(5, 3), 1, 1)


def test_generation_and_particle_doubling_do_not_change_ratios() -> None:
    trace = canonical_sm_generation_trace()
    factor = 6
    assert (
        factor * trace.hypercharge / (factor * trace.su2),
        1,
        factor * trace.su3 / (factor * trace.su2),
    ) == (Fraction(5, 3), 1, 1)


def test_curvature_response_shift_polynomial() -> None:
    xi = Fraction(2, 9)
    assert curvature_response_r2_shift_polynomial(xi) == 30 * xi * (6 * xi - 1)


def test_only_zero_and_conformal_special_value_preserve_ray() -> None:
    roots = ray_preserving_curvature_response_values()
    assert roots == (Fraction(0), Fraction(1, 6))
    for xi in roots:
        assert curvature_response_r2_shift_polynomial(xi) == 0
    assert curvature_response_r2_shift_polynomial(Fraction(1, 4)) != 0


def test_round_berger_cylinder_is_weyl_flat() -> None:
    assert berger_cylinder_weyl_density(Fraction(1)) == 0
    assert berger_cylinder_weyl_density(Fraction(6, 5)) > 0


def test_berger_shape_stationarity_points() -> None:
    assert berger_shape_derivative(Fraction(1)) == 0
    assert berger_shape_derivative(Fraction(1, 1) / 5 ** Fraction(1, 2)) == 0


def test_integrated_shape_nonnegative() -> None:
    for a in (Fraction(1, 4), Fraction(1, 2), Fraction(1), Fraction(5, 4)):
        assert berger_cylinder_integrated_shape(a) >= 0


def test_a4_is_globally_scale_invariant() -> None:
    assert a4_global_scale_weight() == 0


def test_payload_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["completion"]["BHSM_complete"] is False
    assert payload["completion"]["full_phi_response_owned"] is False
    assert payload["completion"]["canonical_trace_matches_historical_1_2_7"] is False
    assert payload["completion"]["absolute_scale_closed"] is False
