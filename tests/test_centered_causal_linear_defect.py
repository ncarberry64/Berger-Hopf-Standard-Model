from fractions import Fraction
import math

import numpy as np
import pytest
from flint import arb, arb_mat, ctx, fmpq

from bhsm.interface.centered_causal_linear_defect import (
    bound_causal_linear_defect, centered_step, projected_row_bounds,
)


def scalar_bound(maps, left, right, **kwargs):
    def value(v):
        return arb(fmpq(v.numerator, v.denominator)) if isinstance(v, Fraction) else v
    return bound_causal_linear_defect(
        np.array(maps, dtype=float).reshape(-1, 1, 1),
        [[[value(v)]] for v in left], [[[value(v)]] for v in right],
        np.ones((len(maps)+1, 1)), kwargs.pop('map_gain', 0), **kwargs)


def exact_scalar_rows(maps, left, right):
    row = []
    rows = []
    for i, p in enumerate(maps):
        row = [Fraction(p)*v for v in row]
        if i:
            row[-1] += Fraction(left[i])
        row.append(Fraction(right[i]))
        rows.append(row[:])
    return rows


def test_signed_chain_encloses_exact_fraction_operator_and_omits_initial_input():
    maps = [0, Fraction(1, 2), -2, Fraction(3, 4)]
    left = [10**30, -1, Fraction(1, 8), -3]
    right = [2, Fraction(1, 4), -1, Fraction(1, 2)]
    result = scalar_bound(maps, left, right)
    expected = max(sum(map(abs, row)) for row in exact_scalar_rows(maps, left, right))
    upper = result['frozen_inverse_linear_defect_bounds_upper'][0][0]
    assert Fraction(upper) >= expected
    assert upper < float(expected)*(1+1e-12)
    assert not result['physical_Z1_recertified'] and not result['FULL_BHSM_COMPLETE']
    assert result['fixed_initial_endpoint_omitted']


def test_local_interval_uncertainty_is_transported_after_its_own_map():
    result = scalar_bound([1000, 2, -3], [0, 0, 0], [arb(1, .125), 0, 0])
    upper = result['frozen_inverse_linear_defect_bounds_upper'][0][0]
    assert upper >= 6*1.125
    assert upper < 6.751
    assert result['error_transport']['maximum_node_error_norm_upper'] >= .75


def test_nonunit_projection_identity():
    bounds = projected_row_bounds(arb_mat([[1, 2], [3, 4]]), [[0, 3]], [2, 0])
    expected = [[12, math.sqrt(20)], [math.sqrt(468), math.sqrt(70)]]
    for actual, wanted in zip(np.ravel(bounds), np.ravel(expected)):
        assert actual >= wanted
        assert actual <= wanted*(1+1e-12)


def test_noncommuting_chain_bounds_exact_vectors_with_nonunit_axes():
    maps = np.array([[[0, 0], [0, 0]], [[1, 2], [-1, 0]], [[0, -1], [2, 1]]])
    left = [np.eye(2)*999, np.array([[1, -2], [0, 1]]), np.array([[2, 0], [1, 1]])]
    right = [np.array([[1, 2], [3, 4]]), np.eye(2), np.array([[0, 1], [-2, 0]])]
    axes = np.array([[99, 99], [2, 0], [0, .5], [1, 1]])
    result = bound_causal_linear_defect(maps, left, right, axes, 0)
    bounds = np.array(result['frozen_inverse_linear_defect_bounds_upper'])
    rng = np.random.default_rng(19)
    # All operands below are dyadic; these small integer operations are exact.
    for _ in range(20):
        inputs = rng.integers(-4, 5, size=(4, 2)).astype(float)
        inputs[0] = 0
        ell = np.sum(axes*inputs, axis=1)
        transverse = inputs-axes*ell[:, None]
        radii = [max(abs(ell)), max(np.linalg.norm(transverse, axis=1))]
        v = np.zeros(2)
        for i in range(3):
            v = maps[i]@v+left[i]@inputs[i]+right[i]@inputs[i+1]
            observed = [abs(axes[i+1]@v), np.linalg.norm(v-axes[i+1]*(axes[i+1]@v))]
            assert np.all(observed <= bounds@radii)


def test_frozen_map_perturbation_covers_changed_recurrence():
    result = scalar_bound([0, .5, .5], [0, 0, 0], [1, 1, 1], map_gain=.1)
    # ||G deltaP|| <= .075 < .1 in the scalar block-sup norm.
    rows = exact_scalar_rows([0, Fraction(11, 20), Fraction(9, 20)], [0]*3, [1]*3)
    actual = max(sum(map(abs, row)) for row in rows)
    assert Fraction(result['frozen_inverse_linear_defect_bounds_upper'][0][0]) >= actual


def test_subnormal_scale_is_rounded_up_not_dropped():
    tiny = arb(2)**-1100
    bounds = projected_row_bounds(arb_mat([[tiny]]), [[1]], [1])
    assert bounds[0][0] == np.nextafter(0., 1.)
    assert arb(bounds[0][0]) > tiny


def test_center_reset_reports_fresh_radius_and_retains_cancellation():
    previous = arb_mat([[2]])
    center, error = centered_step(arb_mat([[.5]]), previous, arb_mat([[-1]]),
                                 arb_mat([[arb(1, .125)]]))
    assert center[0, 0].is_zero()
    assert all(value.rad().is_zero() for value in center.entries())
    assert error >= .25


@pytest.mark.parametrize('kwargs', [{'precision': 63}, {'precision': True},
    {'map_gain': 1}, {'map_gain': -1}, {'block_size': 0}])
def test_invalid_parameters_fail_and_restore_precision(kwargs):
    previous = ctx.prec
    with pytest.raises(ValueError):
        scalar_bound([0], [0], [1], **kwargs)
    assert ctx.prec == previous


def test_callback_cannot_change_precision():
    previous = ctx.prec
    def change_precision(*_):
        ctx.prec = 64
    with pytest.raises(RuntimeError, match='precision'):
        scalar_bound([0], [0], [1], progress=change_precision)
    assert ctx.prec == previous


def test_nonfinite_or_missing_local_blocks_fail():
    with pytest.raises(ValueError):
        scalar_bound([0], [0], [arb('nan')])
    with pytest.raises(ValueError):
        bound_causal_linear_defect(np.zeros((2, 1, 1)), [[[0]]], [[[1]]], np.ones((3, 1)), 0)
