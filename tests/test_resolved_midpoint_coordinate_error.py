from fractions import Fraction as F

import numpy as np
import pytest
from flint import arb, arb_mat, ctx

from bhsm.interface.resolved_midpoint_coordinate_error import bound_resolved_coordinate_pullback_error as bound
from bhsm.interface.resolved_midpoint_coordinate_error import _operator_norm_upper, _float_upper
from bhsm.interface.resolved_midpoint_coordinate_error import bound_storage_coordinate_cross_error as cross_bound


def exact_error_squared(s, m, x, uu, cu, cc):
    s, m, x = [[[F.from_float(float(v)) for v in row] for row in a] for a in (s, m, x)]
    a, b, c, d = s[0][0], s[0][1], s[1][0], s[1][1]
    determinant = a*d-b*c
    inverse = [[d/determinant, -b/determinant], [-c/determinant, a/determinant]]
    exact = [[sum(inverse[i][k]*m[k][j] for k in range(2))
              for j in range(len(m[0]))] for i in range(2)]
    total = F(0)
    for output in range(len(uu)):
        q = [[F.from_float(float(uu[output, 0, 0])), F.from_float(float(cu[output, 0, 0]))],
             [F.from_float(float(cu[output, 0, 0])), F.from_float(float(cc[output, 0, 0]))]]
        for i in range(len(m[0])):
            for j in range(len(m[0])):
                delta = sum(q[k][l]*(exact[k][i]*exact[l][j]-x[k][i]*x[l][j])
                            for k in range(2) for l in range(2))
                total += delta*delta
    return total


def test_scale_separation_prevents_large_cc_norm_from_multiplying_u_error():
    s = np.diag([1e-7, 1.])
    m = np.array([[1e-7, 2e-7], [1e-12, 2e-12]])
    x = np.linalg.solve(s, m)
    x[0, 0] = np.nextafter(x[0, 0], np.inf)
    uu, cu, cc = np.array([[[1.]]]), np.array([[[1.]]]), np.array([[[1e16]]])
    result = bound(s, m, x, uu, cu, cc)
    upper = result['pullback_coordinate_error_frobenius_upper']
    assert exact_error_squared(s, m, x, uu, cu, cc) <= F.from_float(upper)**2
    assert upper < 1e-12
    assert result['complement_coordinate_error_frobenius_upper'] < 1e-100
    assert not result['physical_Hessian_error_enclosed']


@pytest.mark.parametrize('seed', range(6))
def test_multiple_outputs_and_cross_terms_against_exact_rational_oracle(seed):
    rng = np.random.default_rng(seed)
    s = np.array([[2., .25], [-.5, 3.]])
    m = rng.normal(size=(2, 3))
    x = np.linalg.solve(s, m)
    x += rng.normal(size=x.shape)*1e-5
    uu, cu, cc = [rng.normal(size=(3, 1, 1)) for _ in range(3)]
    result = bound(s, m, x, uu, cu, cc)
    upper = result['pullback_coordinate_error_frobenius_upper']
    assert exact_error_squared(s, m, x, uu, cu, cc) <= F.from_float(upper)**2


def test_exact_solution_has_zero_error_and_restores_precision():
    precision = ctx.prec
    result = bound(np.eye(2), np.eye(2), np.eye(2),
                   np.ones((1, 1, 1)), np.ones((1, 1, 1)), np.ones((1, 1, 1)))
    assert result['pullback_coordinate_error_frobenius_upper'] == 0.
    assert ctx.prec == precision


def test_singular_basis_does_not_supply_a_certificate():
    precision = ctx.prec
    with pytest.raises((ZeroDivisionError, ValueError, RuntimeError)):
        bound(np.ones((2, 2)), np.eye(2), np.eye(2),
              np.ones((1, 1, 1)), np.ones((1, 1, 1)), np.ones((1, 1, 1)))
    assert ctx.prec == precision


@pytest.mark.parametrize('invalid', [float('nan'), float('inf'), 1j])
def test_nonfinite_and_complex_operands_fail(invalid):
    with pytest.raises(ValueError):
        bound(np.array([[1., 0.], [0., invalid]]), np.eye(2), np.eye(2),
              np.ones((1, 1, 1)), np.ones((1, 1, 1)), np.ones((1, 1, 1)))


def test_incompatible_blocks_fail():
    with pytest.raises(ValueError):
        bound(np.eye(2), np.eye(2), np.eye(2),
              np.ones((1, 1, 1)), np.ones((1, 2, 1)), np.ones((1, 1, 1)))


@pytest.mark.parametrize('seed', range(4))
def test_multiple_retained_rows_against_exact_diagonal_solve(seed):
    rng = np.random.default_rng(seed+20)
    s = np.diag([.5, 2., 1.])
    m = rng.normal(size=(3, 4))
    x = np.linalg.solve(s, m) + rng.normal(size=m.shape)*1e-7
    uu = rng.normal(size=(2, 2, 2))
    cu = rng.normal(size=(2, 1, 2))
    cc = rng.normal(size=(2, 1, 1))
    result = bound(s, m, x, uu, cu, cc)
    exact = [[F.from_float(float(m[i, j])) / F.from_float(float(s[i, i]))
              for j in range(4)] for i in range(3)]
    approximate = [[F.from_float(float(v)) for v in row] for row in x]
    total = F(0)
    for o in range(2):
        q = np.block([[uu[o], cu[o].T], [cu[o], cc[o]]])
        for i in range(4):
            for j in range(4):
                error = sum(F.from_float(float(q[k, l])) *
                            (exact[k][i]*exact[l][j]-approximate[k][i]*approximate[l][j])
                            for k in range(3) for l in range(3))
                total += error*error
    assert total <= F.from_float(result['pullback_coordinate_error_frobenius_upper'])**2


def test_signed_gram_retains_orthogonal_row_cancellation():
    value = _float_upper(_operator_norm_upper(arb_mat([[1, 1], [1, -1]]), arb(2)))
    assert F.from_float(value)**2 >= 2
    assert value < 1.5


def test_subnormal_error_is_not_erased():
    tiny = np.nextafter(0., 1.)
    s = np.eye(2)
    m = np.array([[tiny], [0.]])
    x = np.zeros((2, 1))
    uu, cu, cc = np.array([[[1e308]]]), np.zeros((1, 1, 1)), np.zeros((1, 1, 1))
    result = bound(s, m, x, uu, cu, cc)
    upper = result['pullback_coordinate_error_frobenius_upper']
    assert upper > 0
    assert exact_error_squared(s, m, x, uu, cu, cc) <= F.from_float(upper)**2


def test_storage_coordinate_cross_term_matches_exact_rational_expansion():
    upper = cross_bound(2., .25, 3., 1., .5, .25)
    assert F.from_float(upper) >= F(119, 64)
    assert upper < 1.86
    # The tensor and coordinate errors cannot merely be added at A.
    a, e, q, dq = F(2), F(1, 4), F(3), F(1, 2)
    total = (q+dq)*(a+e)**2-q*a*a
    separate = q*((a+e)**2-a*a)+dq*a*a
    assert total-separate == dq*(2*a*e+e*e)
    assert F.from_float(cross_bound(float(a), float(e), 1., 0., float(dq), 0.)) >= total-separate


def test_storage_coordinate_cross_term_vanishes_if_either_error_is_zero():
    assert cross_bound(2., 0., 3., 1., .5, .25) == 0.
    assert cross_bound(2., .25, 3., 1., 0., 0.) == 0.


@pytest.mark.parametrize('bad', [-1., float('nan'), float('inf')])
def test_storage_coordinate_cross_term_rejects_invalid_bounds(bad):
    with pytest.raises(ValueError):
        cross_bound(2., bad, 3., 1., .5, .25)
