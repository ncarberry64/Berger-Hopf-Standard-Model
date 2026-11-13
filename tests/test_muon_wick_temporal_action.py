"""Original temporal action, Gauss and canonical source continuation checks."""
import numpy as np
from bhsm.interface.muon_wick_temporal_action import (
    wick_temporal_forms, quadratic_action_rows, analytic_gauss_reduction,
    compare_temporal_action_continuation,
)


def fixture():
    M = np.diag([0., 3., 5., 7.])
    B = np.array([[0., .13, -.17, .23], [0., .4, -.3, .6],
        [0., -.7, .2, -.1], [0., .9, .5, -.8]])
    K = np.array([[2., .3, -.5, .7], [.3, -11., .8, -.9],
        [-.5, .8, -13., 1.1], [.7, -.9, 1.1, -17.]])
    x = np.arange(12).reshape(4, 3).astype(complex)/17.; v = np.arange(12, 24).reshape(4, 3)/29.
    reduced = analytic_gauss_reduction((M, B, K), 1)
    x[0] = (reduced['At_value_map']@x[1:]+reduced['At_velocity_map']@v[1:])[0]
    return (M, B, K), x, v


def test_all_action_canonical_source_and_original_gauss_rows_continue():
    forms, x, v = fixture()
    a = compare_temporal_action_continuation(forms, x, v, 1)
    assert max(a['continuation_residuals'].values()) < 1e-13
    assert np.max(abs(a['original_Lorentz_Gauss_rows'])) < 1e-14
    assert np.max(abs(a['continued_original_Gauss_rows'])) < 1e-14
    assert not a['terminal_Dirichlet_domain_imposed']
    assert not a['native_heat_or_normalized_soft_Pauli_completed']


def test_euclidean_source_coordinates_differentiate_before_any_inverse():
    forms, x, v = fixture(); w = wick_temporal_forms(forms, 1)
    r = w['coordinate_rotation']; xe, ve = r[:, None]*x, -1j*r[:, None]*v
    rows = quadratic_action_rows(w['forms'], xe, ve)
    direction = np.array([[.2], [-.7], [.5], [.3]])
    h = 1e-5
    plus = quadratic_action_rows(w['forms'], xe+h*direction, ve)['action_pairing']
    minus = quadratic_action_rows(w['forms'], xe-h*direction, ve)['action_pairing']
    expected = direction.T@rows['value_row']+rows['value_row'].T@direction
    np.testing.assert_allclose((plus-minus)/(2*h), expected/2, atol=2e-9)


def test_original_gauss_row_is_used_in_the_reduced_action_with_cross_source():
    forms, x, v = fixture(); a = analytic_gauss_reduction(forms, 1)
    full = quadratic_action_rows(forms, x, v)
    reduced = quadratic_action_rows(tuple(a[k] for k in ('M', 'B', 'K')), x[1:], v[1:])
    np.testing.assert_allclose(full['action_pairing'], reduced['action_pairing'], atol=2e-14)
    np.testing.assert_allclose(full['momentum'][1:], reduced['momentum'], atol=2e-14)
    assert np.linalg.norm(a['At_velocity_map']) > 0
