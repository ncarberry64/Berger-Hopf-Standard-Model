import pytest
from flint import arb, arb_mat, ctx

from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor


def test_shared_input_cancellation_and_euclidean_support():
    ctx.prec = 128
    d = TaylorDomain([(0, 2, 'euclidean')], 2)
    f = InputLinearTaylor(d, arb_mat([[3, 4]]), arb_mat([[2, 0], [0, 2]]))
    assert f.support() >= 7 and f.support() < arb('7.00000001')
    assert (f-f).support().is_zero()
    with pytest.raises(ValueError, match='two input legs'):
        f*f


def test_product_keeps_state_input_cross_terms_and_bounds_quadratic_tail():
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval')], 1)
    f = InputLinearTaylor(d, arb_mat([[3, 4]]), arb_mat([[1, -2]]))
    s = d.affine(2, [3])
    result = f*s
    assert result.c == arb_mat([[6, 8]])
    assert result.a == arb_mat([[11, 8]])
    assert result.r >= 3*arb(5).sqrt()
    for theta in (-1, 0, 1):
        u = arb_mat([[arb('0.6')], [arb('0.8')]])
        restricted = result.at_input(u)
        actual = ((3+theta)*u[0, 0]+(4-2*theta)*u[1, 0])*(2+3*theta)
        error = actual-restricted.c-restricted.a[0, 0]*theta
        assert abs(error).upper() <= restricted.r


def test_remainder_scales_with_input_and_domains_cannot_be_identified():
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval')], 1)
    f = InputLinearTaylor(d, arb_mat([[0, 0]]), arb_mat([[0, 0]]), 2)
    assert f.at_input(arb_mat([[3], [4]])).r == 10
    other = TaylorDomain([(0, 1, 'interval')], 1)
    with pytest.raises(ValueError, match='identity'):
        f*other.affine(1)


def test_implicit_corrections_remain_shared_until_residual_cancellation():
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval')], 1)
    inputs = [(0, 2, 'euclidean'), (2, 3, 'box')]
    y = InputLinearTaylor(d, arb_mat([[3, 4, 100]]), arb_mat([[0, 0, 0]]), input_groups=inputs)
    residual = InputLinearTaylor(d, arb_mat([[0, 0, 100]]), arb_mat([[0, 0, 0]]), input_groups=inputs)
    assert y.support() == 105
    assert (y-residual).support() == 5


def test_state_times_direction_error_cancels_before_any_remainder_hull():
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval')], 1)
    groups = [(0, 1, 'euclidean'), (1, 2, 'box')]
    axis = InputLinearTaylor(d, arb_mat([[2, 1]]), arb_mat([[0, 0]]), input_groups=groups)
    error = InputLinearTaylor(d, arb_mat([[0, 1]]), arb_mat([[0, 0]]), input_groups=groups)
    weight = d.affine(1, [arb(1)/128])
    result = weight*axis-weight*error
    assert result.c[0, 1].is_zero() and result.a[0, 1].is_zero()
    assert result.r.is_zero()
    assert result.support() >= arb(129)/64 and result.support() < arb('2.01562501')


def test_retained_action_adapter_with_shared_state_and_input():
    import importlib.util
    from pathlib import Path
    import sys
    import numpy as np
    from bhsm.interface.input_linear_taylor import input_linear_taylor_action
    ctx.prec = 128
    path = Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
    spec = importlib.util.spec_from_file_location('_input_linear_uniform_parent', path)
    parent = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = parent
    spec.loader.exec_module(parent)
    d = TaylorDomain([(0, 1, 'interval')], 1)
    state = np.array([d.affine(0, [arb('0.00001') if i == 0 else arb(0)]) for i in range(98)], dtype=object)
    point = np.array([arb(0)]*98, dtype=object)
    left = np.array([arb(i == 37) for i in range(98)], dtype=object)
    inputs = np.array([InputLinearTaylor(d, arb_mat([[arb(i == 37), arb(i == 38)]]), arb_mat(1, 2))
                       for i in range(98)], dtype=object)
    maps = [parent._dense_mapping(parent._integrand(point, n, 0).maps) for n in range(parent.POINTS)]
    original = parent._a, parent.Mixed, parent._local_variables
    with input_linear_taylor_action(parent):
        value = parent._contracted_action(state, [left, inputs], maps)
    assert (parent._a, parent.Mixed, parent._local_variables) == original
    for theta in (-1, 1):
        at_state = np.array([v.c+theta*v.a[0,0] for v in state], dtype=object)
        for j in range(2):
            direction = np.array([arb(i == 37+j) for i in range(98)], dtype=object)
            at_input = value.at_input(arb_mat([[arb(j == 0)], [arb(j == 1)]]))
            exact = parent._contracted_action(at_state, [left, direction], maps)
            assert (at_input.c+theta*at_input.a[0,0]+arb(0,at_input.r)).contains(exact)


@pytest.fixture(autouse=True)
def restore_arb_precision():
    previous = ctx.prec
    try:
        yield
    finally:
        ctx.prec = previous
