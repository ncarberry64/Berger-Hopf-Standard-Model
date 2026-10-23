import numpy as np
import pytest
from flint import ctx
from bhsm.interface.muon_mean_legendre_certificate import (
    certify_frozen_legendre_application, prescribed_wall_mean_restriction,
)


def test_indefinite_source_application_and_arithmetic_bound():
    D = np.array([[2., 1., 0.], [1., -1., 0.], [0., 0., 1e-10]])
    B = np.array([[1., 3.], [-2., 4.], [1., -1.]])
    precision = ctx.prec
    result = certify_frozen_legendre_application(D, B)
    exact = -np.linalg.solve(D, B)
    assert np.linalg.norm(result['response']-exact) <= result['certificate']['response_error_Frobenius_upper']
    assert result['certificate']['matrix_invertibility_certified']
    assert result['certificate']['numerical_sign_counts'] == {'positive': 2, 'negative': 1, 'zero': 0}
    assert ctx.prec == precision


def test_singular_and_asymmetric_blocks_are_not_regularized():
    with pytest.raises(ArithmeticError):
        certify_frozen_legendre_application(np.diag([1., 0.]), np.ones((2, 1)))
    with pytest.raises(ValueError):
        certify_frozen_legendre_application(np.array([[1., 1.], [0., 1.]]), np.ones((2, 1)))


def test_domain_restriction_keeps_all_internal_fields_and_wall_reaction_labels():
    labels = [dict(field=f, wall_lift=r == 2) for r in range(3)
              for f in ('A_tau', 'A_rho', 'A_1', 'A_2', 'A_3') for a in range(4)]
    dynamic = np.array([i for i, l in enumerate(labels) if l['field'] != 'A_tau'])
    algebraic = np.array([i for i, l in enumerate(labels) if l['field'] == 'A_tau'])
    r = prescribed_wall_mean_restriction(dict(x_count=90, v_count=90, y_count=36,
        raw_gauge_labels=labels, dynamic_gauge_indices=dynamic, At_indices=algebraic))
    assert len(r['x_indices']) == 74 and len(r['y_indices']) == 32
    assert set(range(38)) <= set(r['x_indices'])
    assert set(range(86, 90)) <= set(r['x_indices'])
    assert set(range(24)) <= set(r['y_indices'])
    assert r['full_to_restricted_lift'].shape == (216, 180)
    assert np.array_equal(r['full_to_restricted_lift'].T@r['full_to_restricted_lift'], np.eye(180))
    assert not r['wall_reaction_rows_discarded']
