from itertools import product
import numpy as np
import pytest
from flint import arb, arb_mat, ctx, fmpq
from bhsm.interface.direct_physical_residual import local_residual_source, bound_causal_residual
from bhsm.interface.physical_hs_value import physical_midpoint


def test_nonlinear_actual_midpoint_enters_residual_without_linearization():
    previous = ctx.prec
    ctx.prec = 512
    try:
        z0, z1, h = [arb(1)], [arb(2)], arb(fmpq(1, 4))
        f0, f1 = [arb(1)], [arb(4)]
        midpoint = physical_midpoint(z0, z1, f0, f1, h)
        fm = [midpoint[0]**2]
        result = local_residual_source([[2.]], [[3.]], z0, z1, f0, fm, f1, h)
        exact = -fmpq(3, 2)*(1-fmpq(1, 24)*(5+4*fmpq(45, 32)**2))
        assert result[0].contains(arb(exact))
        old_midpoint_result = local_residual_source([[2.]], [[3.]], z0, z1, f0, [arb(fmpq(9, 4))], f1, h)
        assert not result[0].overlaps(old_midpoint_result[0])
    finally:
        ctx.prec = previous


def test_signed_propagation_keeps_cancellation():
    result = bound_causal_residual(np.ones((2, 1, 1)), [[arb(3)], [arb(-3)]], np.ones((3, 1)), 0.)
    assert result['signed_center_rows'][1]['longitudinal_upper'] < 1e-100
    assert result['frozen_inverse_residual_bounds_upper'][0] >= 3
    assert result['physical_Y_recertified'] is False


def test_all_source_uncertainty_corners_fit_projected_bounds():
    maps = np.array([[[1., .25], [0., 1.]], [[.5, -.25], [1., .5]]])
    axes = np.array([[2., 0.], [2., 0.], [2., 0.]])
    sources = [[arb(1, .125), arb(-1, .125)], [arb(-1, .125), arb(2, .125)]]
    result = bound_causal_residual(maps, sources, axes, 0.)
    for signs in product((-1, 1), repeat=4):
        z = np.zeros(2)
        for i in range(2):
            center = np.array([1., -1.]) if i == 0 else np.array([-1., 2.])
            z = maps[i]@z+center+.125*np.array(signs[2*i:2*i+2])
            longitudinal = axes[i+1]@z
            transverse = z-axes[i+1]*longitudinal
            assert abs(longitudinal) <= result['frozen_inverse_residual_bounds_upper'][0]
            assert np.linalg.norm(transverse) <= result['frozen_inverse_residual_bounds_upper'][1]
    assert result['fixed_axis_projection_norms_upper'][1] >= 3


def test_frozen_map_error_includes_cross_term():
    plain = bound_causal_residual(np.ones((1, 1, 1)), [[arb(1, .125)]], np.ones((2, 1)), 0.)
    lifted = bound_causal_residual(np.ones((1, 1, 1)), [[arb(1, .125)]], np.ones((2, 1)), .25)
    assert lifted['frozen_inverse_residual_bounds_upper'][0] >= 1.125/.75
    assert lifted['frozen_inverse_residual_bounds_upper'][0] > plain['frozen_inverse_residual_bounds_upper'][0]


def test_invalid_or_missing_sources_and_singular_inverse_fail():
    with pytest.raises(ValueError):
        bound_causal_residual(np.ones((2, 1, 1)), [[arb(1)]], np.ones((3, 1)), 0.)
    with pytest.raises(ValueError):
        bound_causal_residual(np.ones((1, 1, 1)), [[arb('nan')]], np.ones((2, 1)), 0.)
    with pytest.raises((ZeroDivisionError, ValueError, ArithmeticError)):
        local_residual_source([[0.]], [[1.]], [0], [1], [1], [1], [1], 1)
