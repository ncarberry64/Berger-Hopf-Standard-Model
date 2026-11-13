"""Literal source forcing at an imperfect held value field."""
import numpy as np
import pytest
from bhsm.interface.muon_d5_event_consumed_source_refinement import (
    original_source_forcing,source_forcing_gauss_update,
)
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule


def test_original_forcing_retains_radial_value_defect_instead_of_substitution():
    rng=np.random.default_rng(620);n,d,k=3,4,7
    R=np.broadcast_to(np.eye(d),(n,d,d)).copy()*1.3
    T=rng.normal(size=R.shape)*.2;K=rng.normal(size=R.shape)*.3
    Rx=rng.normal(size=R.shape)*.1;Tx=rng.normal(size=R.shape)*.1;Kx=rng.normal(size=R.shape)*.1
    V=rng.normal(size=(n,d,k));Vt=V*.17
    consistent=-np.linalg.solve(R,T@Vt+K@V)
    defect=rng.normal(size=V.shape)*.04;Vr=consistent+defect
    force,difference=original_source_forcing(R,T,K,Rx,Tx,Kx,V,Vr,Vt)
    np.testing.assert_allclose(R@force+Rx@Vr+Tx@Vt+Kx@V,0,atol=4e-16)
    np.testing.assert_allclose(difference,-np.linalg.solve(R,Rx@defect),atol=7e-17)
    assert np.max(abs(difference))>.001
    _,zero=original_source_forcing(R,T,K,Rx,Tx,Kx,V,consistent,Vt)
    np.testing.assert_allclose(zero,0,atol=1e-16)


def test_general_source_gauss_uses_explicit_nonnull_cached_initializer():
    rng=np.random.default_rng(13);q,d,k=3,4,6
    _,_,_,A=_collocation_rule(q);h=-.03
    G=rng.normal(size=(q,d,d))*.2;F=rng.normal(size=(q,d,k))*.3
    initial=rng.normal(size=(d,k));guess=rng.normal(size=F.shape)
    slopes,report=source_forcing_gauss_update(G,F,initial,h,A,guess)
    stages=initial[None]+h*np.einsum('ij,jdk->idk',A,slopes)
    np.testing.assert_allclose(slopes,np.einsum('qij,qjk->qik',G,stages)+F,atol=5e-16)
    assert report['initializer_stage_residual_max']>1
    assert report['corrected_stage_residual_max']<2e-15
    assert report['initializer_correction_norm']>1
    assert report['value_equations_resolved'] is False
    with pytest.raises(ValueError):source_forcing_gauss_update(G,F,initial[:,:-1],h,A,guess)
