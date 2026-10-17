import numpy as np
import pytest
from bhsm.interface.muon_local_charge_matching_response import local_charge_matching_identity,source_form_charge_restriction


def test_local_action_charge_cancellation_keeps_both_current_factors():
    r=local_charge_matching_identity()
    assert r['exact_scalar_residual']=='0'
    # d/dz of the fully matched exchange is exactly zero; the displayed
    # derivative expression is simplified by Sympy's rational arithmetic.
    import sympy as s
    assert s.simplify(s.sympify(r['exact_deltaZ_derivative']))==0
    assert not r['anisotropic_or_momentum_dependent_terms_canceled']


def test_complex_nonproportional_response_survives_charge_restriction():
    K=np.array([[3.,.2],[.2,2.]])
    R=.03*K+np.array([[.01j,.04],[-.04,.02j]])
    r=source_form_charge_restriction(K,R)
    np.testing.assert_allclose(r['proportional_source_restriction']+r['surviving_nonproportional_complex_source_form'],R)
    np.testing.assert_allclose(r['charge_matched_scaled_inverse'],np.linalg.inv(K),atol=2e-16)
    assert r['restriction_residual_norm']>.05
    assert not r['subtraction_applied']
    assert not r['physical_locality_or_momentum_domain_inferred_from_finite_form']


def test_local_matching_rejects_missing_source_or_singular_kinetic_domain():
    with pytest.raises(ValueError,match='required'):source_form_charge_restriction(np.eye(3),None)
    with pytest.raises(np.linalg.LinAlgError):source_form_charge_restriction(np.diag([1.,0.]),np.eye(2)*.001)
