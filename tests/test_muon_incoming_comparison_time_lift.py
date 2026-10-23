import numpy as np
from bhsm.interface.muon_incoming_comparison_time_lift import (
    execute_stationary_time_lift,sector_projector_source,execute_electron_comparison,
)


def actual_shaped_control():
    # Explicit finite comparison test data; not adopted physical values.
    t=np.zeros(22);t[:2]=[.9,1.2];t[2:6]=[.03,-.01,.02,.04]
    t[6:18]=np.c_[np.diag([-.8,-1.1,-.9]),[.02,.03,-.01]].ravel()
    t[18:22]=[.1,.7,.05,-.03]
    return t


def test_historical_stationary_rows_determine_only_constant_compensator_class():
    a=execute_stationary_time_lift(actual_shaped_control())
    assert a['represented_time_gauge_lift_rank']==4
    np.testing.assert_array_equal(a['original_symmetry_rows'],0)
    assert a['singular_values'][-1]>.01
    # H alone has a stabilizer; the actual independent spatial connections
    # are needed even in the constant class. Nonconstant compensators
    # require the separate curvature-integrability test in the v2 owner.
    t=actual_shaped_control();t[2:18]=0
    import pytest
    with pytest.raises(ValueError):execute_stationary_time_lift(t)


def test_sylvester_source_matches_original_boundary_projector_variation():
    rng=np.random.default_rng(33);Z=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6))
    h=(Z+Z.conj().T)/2+np.diag([-4,-3,-2,2,3,4])
    X=rng.normal(size=(2,6,6))+1j*rng.normal(size=(2,6,6));X=(X+X.conj().swapaxes(-1,-2))/2
    a=sector_projector_source(h,X)
    for key in ('original_projector_source_rows','original_idempotent_source_rows'):
        np.testing.assert_allclose(a[key],0,atol=9e-15)
    e=1e-5
    for i,x in enumerate(X):
        p=sector_projector_source(h+e*x,X)['positive'];m=sector_projector_source(h-e*x,X)['positive']
        np.testing.assert_allclose(a['positive_source'][i],(p-m)/(2*e),atol=2e-10,rtol=3e-8)


def test_full_electron_family_reduces_but_charged_four_is_only_tested():
    t=actual_shaped_control();g=np.eye(22)
    a=execute_electron_comparison(t,g)
    np.testing.assert_allclose(a['original_causal_coefficient_rows'],0,atol=8e-16)
    np.testing.assert_array_equal(a['electron_family_reducing_rows'],0)
    np.testing.assert_array_equal(a['electron_family_source_reducing_rows'],0)
    np.testing.assert_allclose(a['complete_constant_Haar_Cauchy_Gram_rows'],0,atol=3e-16)
    assert np.linalg.norm(a['electron_charged_to_neutral_rows'])>.1
    assert a['original_current_pair_operator_blocks'].shape==(24,6,6)
    direction=np.linspace(-.13,.21,22);e=1e-5
    plus=execute_electron_comparison(t+e*direction,g)['original_current_pair_operator_blocks']
    minus=execute_electron_comparison(t-e*direction,g)['original_current_pair_operator_blocks']
    source=np.einsum('j,jvab->vab',direction,a['original_current_pair_operator_source'])
    np.testing.assert_allclose(source,(plus-minus)/(2*e),atol=3e-10,rtol=3e-7)
