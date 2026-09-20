"""Analytic checks of common parameters and rigorous nonlinear remainders."""
import pytest
from flint import arb, ctx
from bhsm.interface.shared_action_taylor import TaylorDomain


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 128
    yield
    ctx.prec = old


def test_signed_affine_terms_cancel_before_hull():
    domain = TaylorDomain([(0, 2, 'euclidean')], 2)
    x = domain.affine(3, [1, -2])
    y = domain.affine(4, [-1, 2])
    assert (x + y).support() == 7
    assert (x + y).r.is_zero()


def test_product_remainder_encloses_exact_polynomial_on_ball():
    d = TaylorDomain([(0, 2, 'euclidean')], 2)
    a, b = d.affine(2, [1, 2]), d.affine(3, [-2, 1])
    result = a * b
    assert result.c == 6
    assert result.a[0, 0] == -1 and result.a[0, 1] == 8
    for x, y in [('0.6', '0.8'), ('-0.6', '0.8'), ('0', '0')]:
        x, y = arb(x), arb(y)
        exact = (2+x+2*y)*(3-2*x+y)
        predicted = result.c+result.a[0, 0]*x+result.a[0, 1]*y+arb(0, result.r)
        assert predicted.contains(exact)


@pytest.mark.parametrize('name', ['exp', 'log', 'reciprocal'])
def test_unary_remainder_includes_input_remainder(name):
    d = TaylorDomain([(0, 1, 'interval')], 1)
    x = d.affine(2, [arb('0.1')], arb('0.01'))
    result = getattr(x, name)()
    for theta in [-1, 0, 1]:
        for remainder in ['-0.01', '0.01']:
            exact = arb(2)+arb('0.1')*theta+arb(remainder)
            expected = 1/exact if name == 'reciprocal' else getattr(exact, name)()
            predicted = result.c+result.a[0, 0]*theta+arb(0, result.r)
            assert predicted.contains(expected)


def test_domain_and_singular_denominator_fail_closed():
    d, other = [TaylorDomain([(0, 1, 'interval')], 1) for _ in range(2)]
    with pytest.raises(ValueError, match='identity'):
        d.affine(1)+other.affine(1)
    with pytest.raises(ArithmeticError, match='zero'):
        d.affine(1, [2]).reciprocal()
    with pytest.raises(ArithmeticError, match='positive'):
        d.affine(1, [2]).log()


def test_coefficient_uncertainty_cannot_cancel_as_exact():
    d = TaylorDomain([(0, 1, 'interval')], 1)
    a, b = [d.affine(0, [arb(1, '0.1')]) for _ in range(2)]
    assert (a-b).support() >= arb('0.2')


def test_retained_action_adapter_includes_global_inertia_and_boundary():
    import importlib.util
    from pathlib import Path
    import sys
    import numpy as np
    from bhsm.interface.shared_action_taylor import scalar_taylor_action
    path = Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
    name = '_gate7_taylor_parent_test'
    spec = importlib.util.spec_from_file_location(name, path)
    parent = importlib.util.module_from_spec(spec)
    sys.modules[name] = parent
    spec.loader.exec_module(parent)
    d = TaylorDomain([(0, 1, 'interval')], 1)
    state = [d.affine(0, [arb('0.00001') if i == 0 else arb(0)]) for i in range(98)]
    left = np.array([arb(i == 37) for i in range(98)], dtype=object)
    right = np.array([arb(i == 38) for i in range(98)], dtype=object)
    maps = [parent._dense_mapping(parent._integrand([arb(0)]*98, node, 0).maps)
            for node in range(parent.POINTS)]
    original = parent._a, parent.Mixed, parent._local_variables
    with scalar_taylor_action(parent):
        enclosed = parent._contracted_action(np.array(state, dtype=object), [left, right], maps)
    assert (parent._a, parent.Mixed, parent._local_variables) == original
    for theta in [-1, 0, 1]:
        point = np.array([x.c+x.a[0, 0]*theta for x in state], dtype=object)
        exact = parent._contracted_action(point, [left, right], maps)
        bound = enclosed.c+enclosed.a[0, 0]*theta+arb(0, enclosed.r)
        assert bound.contains(exact)
    with pytest.raises(RuntimeError):
        with scalar_taylor_action(parent):
            raise RuntimeError('restore even after failure')
    assert (parent._a, parent.Mixed, parent._local_variables) == original
