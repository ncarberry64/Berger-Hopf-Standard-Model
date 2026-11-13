import numpy as np
import pytest
from bhsm.interface.muon_coupled_field_angular_images import one_form_angular_point,intrinsic_coupled_angular_point
from bhsm.interface.muon_parent_positive_coupled_temporal import one_form_point_row,intrinsic_coupled_point_form
from bhsm.interface.muon_intrinsic_higgs_positive_source import higgs_magnetic_source_image_space
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


def test_entire_retained_odd_point_matches_unchanged_literal_owner():
    rng=np.random.default_rng(72);A=rng.normal(size=(5,4))*.11;At=rng.normal(size=(5,4))*.07;Ar=rng.normal(size=(5,4))*.13
    E=retained_full_q_angular_space()['derivative_matrices'];r=np.array([[.82,.13,0],[.19,.27,0]])
    g=np.array([1.3,1.2,.7,.9,.17,1.1]);d=np.array([1.1,.8,.6,.4,.17]);t=np.array([.43,.7,.03,.08,.04,-.11])
    actual=one_form_angular_point(A,At,Ar,E,r,g,d,t);owned=one_form_point_row(A,At,Ar,E,r,g,d,t)
    for k in ('Hessian','Gram','curvature_contact','ghost_Gram','value_map','curvature_map'):
        np.testing.assert_array_equal(actual[k],owned[k])
    H=np.array([.17,.62,-.11,.07]);Hd=np.array([.1,-.17,.06,.04]);w=np.array([1.2,.9,.7]);lam=.13;nu=4
    a=intrinsic_coupled_angular_point(w,H,Hd,A,E,t,r,lambda_H=lam,nu_squared_action=nu)
    maps=a['maps'];ref=intrinsic_coupled_point_form(w,H,Hd,A,E,maps['gauge'].reshape(400,1200),maps['scalar'],maps['scalar_rate'],lambda_H=lam,nu_squared_action=nu)
    for k in ('Hessian','Gram'):np.testing.assert_array_equal(a[k],ref[k])


def test_even_base_is_entire_gauge_DG_scalar_image_not_Higgs_submatrix():
    from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
    a=scalar_s3_discretization(2);ids=[i for i,l in enumerate(a['real_basis_labels'])if l[0]in(0,2)]
    E=a['real_angular_derivative_matrices'][:,ids][:,:,ids]
    A=np.arange(20).reshape(5,4)/30;At=A/7;Ar=A/9;r=np.array([[.7,.2,0],[.2,-.1,0]]);t=np.array([.6,.3,.04,.06,-.02,.08])
    out=one_form_angular_point(A,At,Ar,E,r,[1,1,1,1,.1,1],[1,1,1,1,.1],t)
    assert out['Hessian'].shape==(560,560)
    np.testing.assert_allclose(out['Hessian'],out['Hessian'].T,atol=2e-14)
    h=intrinsic_coupled_angular_point([1,1,1],[.2,.7,.1,-.1],[.1,-.2,0,.3],A,E,t,r,lambda_H=.13,nu_squared_action=4)
    assert h['Hessian'].shape==(600,600)
    assert np.linalg.norm(h['maps']['scalar'][:,400:560])>0
    assert np.linalg.norm(h['maps']['scalar_rate'][:,400:560])>0
    assert np.linalg.norm(h['Hessian'][:560,560:])>0


def test_complex_or_missing_geometry_and_domains_are_rejected():
    with pytest.raises(ValueError):one_form_angular_point(None,np.zeros((5,4)),np.zeros((5,4)),np.zeros((3,4,4)),np.zeros((2,3)),np.ones(6),np.ones(5),np.ones(6))
    with pytest.raises(ValueError):intrinsic_coupled_angular_point([1,1,1],[0,1,0,0],[0,0,0,0],np.ones((5,4))*1j,np.zeros((3,4,4)),np.ones(6),np.ones((2,3)),lambda_H=.1,nu_squared_action=4)
