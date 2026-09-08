from fractions import Fraction as F

import numpy as np
import pytest
from flint import ctx

from bhsm.interface.current_green_midpoint_coordinate_error import bound_coordinate_pullback_error


def _exact_pullback(q, x):
    # An independent exact-rational contraction, including every signed leg.
    return [[[sum(F(float(x[i, k])) * F(float(q[o, i, j])) * F(float(x[j, l]))
                  for i in range(x.shape[0]) for j in range(x.shape[0]))
              for l in range(x.shape[1])] for k in range(x.shape[1])]
            for o in range(q.shape[0])]


@pytest.mark.parametrize("seed", range(6))
def test_encloses_exact_rational_full_signed_and_mapped_error(seed):
    rng = np.random.default_rng(seed)
    q = rng.integers(-9, 10, (3, 4, 4)).astype(float) / 8
    q = q + q.transpose(0, 2, 1)
    approximate = rng.integers(-7, 8, (4, 3)).astype(float) / 8
    perturbation = rng.integers(-3, 4, (4, 3)).astype(float) / 128
    exact_coordinates = approximate + perturbation
    epsilon = float(max(sum(abs(F(float(v))) for v in row) for row in perturbation))
    output = np.array([[1., -2., .25], [0., .5, -1.]])
    result = bound_coordinate_pullback_error(q[:, :2, :2], q[:, 2:, :2],
                                             q[:, 2:, 2:], approximate, epsilon, output)
    exact = _exact_pullback(q, exact_coordinates)
    center = _exact_pullback(q, approximate)
    error_squared = sum(sum(F(float(output[p, o])) * (exact[o][i][j] - center[o][i][j])
                            for o in range(3)) ** 2
                        for p in range(2) for i in range(3) for j in range(3))
    assert 0 < error_squared <= F(result["pullback_coordinate_error_frobenius_upper"]) ** 2
    assert result["physical_Hessian_rounding_enclosed"] is False
    assert result["pullback_assembly_rounding_enclosed"] is False


def test_quadratic_error_term_survives_zero_approximate_coordinates():
    result = bound_coordinate_pullback_error(np.ones((1, 1, 1)), np.zeros((1, 1, 1)),
                                             np.ones((1, 1, 1)), np.zeros((2, 1)), .25)
    # X=(1/4,1/4): exact pullback error is 1/8; linear-only bound would be zero.
    assert result["pullback_coordinate_error_frobenius_upper"] >= .125


def test_both_cross_legs_count_even_when_diagonal_blocks_vanish():
    result = bound_coordinate_pullback_error(np.zeros((1, 1, 1)), np.ones((1, 1, 1)),
                                             np.zeros((1, 1, 1)), np.zeros((2, 1)), .5)
    assert F(result["full_stored_tensor_frobenius_upper"]) ** 2 >= 2
    assert result["pullback_coordinate_error_frobenius_upper"] >= .5


@pytest.mark.parametrize("zero", ["error", "tensor", "map"])
def test_structural_zero_remains_exact(zero):
    q = np.zeros((1, 1, 1)) if zero == "tensor" else np.ones((1, 1, 1))
    result = bound_coordinate_pullback_error(q, q, q, np.ones((2, 2)),
                                             0. if zero == "error" else 1.,
                                             np.zeros((1, 1)) if zero == "map" else None)
    assert result["pullback_coordinate_error_frobenius_upper"] == 0.


def test_subnormal_bound_rounds_outward_instead_of_to_zero():
    tiny = np.nextafter(0., 1.)
    q = np.ones((1, 1, 1))
    result = bound_coordinate_pullback_error(q, q, q, np.zeros((2, 1)), tiny)
    assert result["pullback_coordinate_error_frobenius_upper"] == tiny


def test_large_norm_uses_ball_arithmetic_and_restores_precision():
    previous = ctx.prec
    q = np.full((1, 1, 1), 1e200)
    # Binary64 squaring overflows; the norm and final answer remain representable.
    result = bound_coordinate_pullback_error(q, q, q, np.zeros((2, 1)), 1e-100)
    assert 4 <= result["pullback_coordinate_error_frobenius_upper"] < 4.000000000001
    assert ctx.prec == previous


def test_unrepresentable_bound_fails_and_restores_precision():
    previous = ctx.prec
    q = np.full((1, 1, 1), 1e308)
    with pytest.raises(RuntimeError, match="not finite"):
        bound_coordinate_pullback_error(q, q, q, np.ones((2, 1)), 1.)
    assert ctx.prec == previous


@pytest.mark.parametrize("key,value", [
    ("retained_retained", np.ones((1, 1, 1), complex)),
    ("retained_retained", np.full((1, 1, 1), np.nan)),
    ("retained_retained", np.empty((0, 1, 1))),
    ("complement_retained", np.zeros((1, 2, 1))),
    ("complement_complement", np.zeros((1, 0, 0))),
    ("approximate_coordinates", np.zeros((2, 0))),
    ("coordinate_error_infinity_upper", -1.),
    ("coordinate_error_infinity_upper", np.inf),
    ("coordinate_error_infinity_upper", [1.]),
    ("coordinate_error_infinity_upper", "1"),
    ("output_map", np.ones((1, 2))),
])
def test_invalid_inputs_fail_closed(key, value):
    args = dict(retained_retained=np.ones((1, 1, 1)),
                complement_retained=np.ones((1, 1, 1)),
                complement_complement=np.ones((1, 1, 1)),
                approximate_coordinates=np.ones((2, 1)),
                coordinate_error_infinity_upper=1.)
    args[key] = value
    previous = ctx.prec
    with pytest.raises(ValueError):
        bound_coordinate_pullback_error(**args)
    assert ctx.prec == previous
