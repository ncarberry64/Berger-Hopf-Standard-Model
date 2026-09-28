"""Exact monomial checks and outward remainder checks for the collar model."""
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.longitudinal_quadratic_taylor import (
    LongitudinalQuadraticDomain, LongitudinalQuadratic,
)
from bhsm.interface.shared_action_taylor import TaylorDomain, scalar_taylor_action


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 128
    yield
    ctx.prec = old


def at(model, parameters):
    return model.c+sum((a*v for a, v in zip(model.a.entries(), parameters, strict=True)), arb(0))+model.q*parameters[0]**2+arb(0, model.r)


def test_common_longitudinal_square_is_combined_before_support():
    d = LongitudinalQuadraticDomain([(0, 1, 'interval')], 1)
    x = d.affine(0, [1])
    square = x*x
    assert square.q == 1 and square.r == 0
    assert (square-square).support() == 0
    assert (x**3).q == 0 and (x**3).r == 1


def test_other_group_products_and_input_remainders_remain_enclosed():
    d = LongitudinalQuadraticDomain([(0, 1, 'interval'), (1, 3, 'euclidean')], 3)
    x = LongitudinalQuadratic(d, arb(2), arb_mat([[arb(1)/8, arb(1)/16, arb(0)]]), arb(1)/32, arb(1)/128)
    y = d.affine(3, [arb(-1)/8, arb(0), arb(1)/16], arb(1)/256)
    result = x*y
    for t in (-1, 0, 1):
        p = [arb(t), arb(3)/5, arb(4)/5]
        for sign in (-1, 1):
            xv = x.c+sum((a*v for a, v in zip(x.a.entries(), p)), arb(0))+x.q*p[0]**2+sign*x.r
            yv = y.c+sum((a*v for a, v in zip(y.a.entries(), p)), arb(0))-sign*y.r
            assert at(result, p).contains(xv*yv)


@pytest.mark.parametrize('name', ['reciprocal', 'exp', 'log'])
def test_unary_outward_third_order_remainder(name):
    d = LongitudinalQuadraticDomain([(0, 1, 'interval'), (1, 2, 'box')], 2)
    x = LongitudinalQuadratic(d, arb(2), arb_mat([[arb(1)/16, arb(1)/128]]), arb(1)/256, arb(1)/1024)
    result = getattr(x, name)()
    for t in (-1, 0, 1):
        for u in (-1, 1):
            for sign in (-1, 1):
                exact = x.c+x.a[0, 0]*t+x.a[0, 1]*u+x.q*t*t+sign*x.r
                truth = 1/exact if name == 'reciprocal' else getattr(exact, name)()
                assert at(result, [arb(t), arb(u)]).contains(truth)


def test_incompatible_domains_and_singular_functions_fail():
    d = LongitudinalQuadraticDomain([(0, 1, 'interval')], 1)
    with pytest.raises(ValueError, match='implicitly'):
        d.affine(1)+TaylorDomain([(0, 1, 'interval')], 1).affine(1)
    with pytest.raises(ArithmeticError, match='zero'):
        d.affine(1, [2]).reciprocal()
    with pytest.raises(ArithmeticError, match='positive'):
        d.affine(1, [2]).log()


def test_same_retained_action_adapter_preserves_quadratic_models():
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root/'scripts'))
    import solve_n12_gate7_fiber_constrained_center as owner
    A = owner.action
    d = LongitudinalQuadraticDomain([(0, 1, 'interval')], 1)
    y = [d.affine(0, [arb(1)/1024 if i == 0 else arb(0)]) for i in range(98)]
    left = [arb(i == 37) for i in range(98)]
    right = [arb(i == 38) for i in range(98)]
    maps = [A._dense_mapping(A._integrand([arb(0)]*98, i, 0).maps) for i in range(A.POINTS)]
    with scalar_taylor_action(A):
        result = A._contracted_action(y, [left, right], maps)
    assert isinstance(result, LongitudinalQuadratic)
    for t in (-1, 0, 1):
        point = [v.c+v.a[0, 0]*t for v in y]
        actual = A._contracted_action(point, [left, right], maps)
        assert at(result, [arb(t)]).contains(actual)
