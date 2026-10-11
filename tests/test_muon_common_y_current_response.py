import numpy as np
from bhsm.interface.muon_common_y_current_response import (
    block_bidiagonal, common_y_inverse_action, common_y_rectangular_source_jet,
    polynomial_current_pairing, paired_fixed_y_polynomial, exact_stored_inverse_tail,
    certify_current_pairing)


def test_noncommuting_action_recurrence_and_both_directed_source_terms():
    a = np.array([[3+1j, .4], [.2j, 2-.3j]])
    b = np.array([[.1j, .2], [.3, -.1]])
    r = np.array([np.eye(2), [[.1, .2j], [.3, 0]]], complex)
    d = np.array([[[.2, .1j], [-.2j, 0]], [[0, .05], [.04j, .01]]])
    dr = np.array([[[.1, 0], [.2, .3]], [[0, .1j], [.05, 0]]])
    u = common_y_inverse_action(a, b, r, order=5)['coefficients']
    du = common_y_rectangular_source_jet(a, b, u, d, dr, order=5)['coefficients']
    for y in (.01, -.015):
        sums = lambda c: sum(y**k*x for k, x in enumerate(c))
        actual = np.linalg.solve(a+y*b, sums(r))
        actual_jet = np.linalg.solve(a+y*b, sums(dr)-sums(d)@actual)
        np.testing.assert_allclose(sums(u), actual, rtol=2e-14, atol=2e-16)
        np.testing.assert_allclose(sums(du), actual_jet, rtol=2e-14, atol=2e-16)


def test_pair_keeps_odd_powers_and_literal_left_current():
    u = np.array([np.eye(2), [[0, 2j], [3, 1]], [[1, 0], [0, 2]]])
    left = np.array([[[1j, 2]], [[2, -1j]]])
    c = polynomial_current_pairing(left, u)
    m, e = .03, .005
    expected = (m-e)*c[1] + (m*m-e*e)*c[2]
    np.testing.assert_allclose(paired_fixed_y_polynomial(c, m, e), expected)
    assert np.linalg.norm((m-e)*c[1]) > 0


def test_block_domain_and_stored_tail_bounds_actual_remainder():
    d = np.array([[[3., .1j], [0., 2.]], [[4., 0.], [.1, 3.]]])
    l = np.array([np.eye(2), [[-.2j, .1], [0, -.1]]])
    a = block_bidiagonal(d, l)
    np.testing.assert_array_equal(a[:2, 2:], 0)
    np.testing.assert_array_equal(a[2:, :2], l[1])
    b = np.diag([.1, -.1, .2, .15])
    r = np.eye(4)[:, :2]
    c = common_y_inverse_action(a, b, r[None], order=3)['coefficients']
    cert = exact_stored_inverse_tail(a, b, r, [.03, .005], order=3, computed_coefficients=c)
    actual = np.linalg.solve(a+.03*b, r)
    residual = actual-sum(.03**k*x for k, x in enumerate(c))
    assert np.linalg.norm(residual) <= cert['fixed_family_tails'][0]['response_tail_upper']['upper_binary64']
    left = np.array([[1, .2j, .1, 0], [.2, 0, .1j, .5]])
    pair = paired_fixed_y_polynomial(polynomial_current_pairing(left[None], c), .03, .005)
    current_cert = certify_current_pairing(left, c, pair, [.03, .005], cert)
    actual_pair = left@(actual-np.linalg.solve(a+.005*b, r))
    assert np.linalg.norm(pair-actual_pair) <= current_cert['paired_current_total_stored_arithmetic_and_Y_tail_upper']['upper_binary64']
