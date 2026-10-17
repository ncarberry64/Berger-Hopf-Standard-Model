import numpy as np
import pytest

from bhsm.interface.muon_finite_normal_schur import normal_schur_application


def test_indefinite_multiplier_block_keeps_coupled_constraint():
    # Internal x,lambda: lambda forces x'=-2 under the normal variation.
    k=np.array([[3.,1.],[1.,0.]])
    b=np.array([5.,2.]);d=7.
    h=np.block([[k,b[:,None]],[b[None,:],np.array([[d]])]])
    r=normal_schur_application(h,normal_index=2)
    np.testing.assert_allclose(r['internal_response'],[-2.,1.],atol=1e-14)
    assert r['response_z']==pytest.approx(-1.)
    assert r['quadratic_pairing']==pytest.approx(-1.)
    assert r['linear_residual_norm']<1e-14
    assert r['rank']==2 and r['nullity']==0
    assert not r['positive_minimum_assumed']


def test_response_agrees_with_independent_restationary_quadratic():
    k=np.array([[4.,2.,0.],[2.,-3.,1.],[0.,1.,2.]])
    b=np.array([1.,3.,-2.]);d=6.
    h=np.block([[k,b[:,None]],[b[None,:],np.array([[d]])]])
    r=normal_schur_application(h,normal_index=3)
    def reduced_action(s):
        x=np.linalg.solve(k,-s*b)
        y=np.r_[x,s]
        return .5*y@h@y
    step=.002
    curvature=(reduced_action(step)-2*reduced_action(0)+reduced_action(-step))/step**2
    assert r['response_z']==pytest.approx(curvature,rel=2e-14)
    assert abs(r['identity_defect'])<1e-13


def test_internal_coordinate_congruence_preserves_pairing():
    h=np.array([[3.,1.,5.],[1.,0.,2.],[5.,2.,7.]])
    change=np.diag([.02,7.,1.])
    original=normal_schur_application(h,normal_index=2)
    changed=normal_schur_application(change.T@h@change,normal_index=2)
    assert original['response_z']==pytest.approx(changed['response_z'],rel=1e-13,abs=1e-13)
    np.testing.assert_allclose(change[:2,:2]@changed['internal_response'],original['internal_response'],atol=1e-13)


def test_singular_source_exports_obstruction_without_zero_claim():
    h=np.diag([2.,0.,5.]);h[0,2]=h[2,0]=3.;h[1,2]=h[2,1]=1.
    r=normal_schur_application(h,normal_index=2)
    assert r['nullity']==1 and r['retained_range_only']
    np.testing.assert_allclose(r['linear_residual'],[0.,1.])
    assert np.linalg.norm(r['discarded_scaled_source'])>0
    assert r['response_z']==pytest.approx(.5)


def test_asymmetric_nonaction_rows_rejected():
    with pytest.raises(ValueError,match='symmetric'):
        normal_schur_application([[1.,2.],[3.,4.]],normal_index=1)
