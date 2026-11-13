"""Independent changing-point and complete paired gauge/H image checks."""
import numpy as np
import pytest
from bhsm.interface.muon_parent_positive_coupled_temporal import (
    one_form_point_row,paired_scalar_orbit_maps,intrinsic_coupled_point_form,
)


@pytest.fixture(scope='module')
def angular():
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    return retained_full_q_angular_space(ROOT)


def test_point_form_retains_nonzero_tent_value_rate_cross(angular):
    from bhsm.interface.muon_parent_positive_gauge_form import one_form_cell_row,one_form_temporal_moments
    from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values
    rng=np.random.default_rng(677) # CONTROL_ONLY finite point action.
    A,At,Ar=rng.normal(size=(3,5,4))*.1
    rad=ghost_radial_values([.81])[0];E=angular['derivative_matrices']
    metric=np.array([2.,3.,4.,5.,.19,.7]);dens=np.array([2.,3.,4.,1.5,.19]);t=np.array([.7,1.2,0.,0.,0.,0.])
    r=one_form_point_row(A,At,Ar,E,rad,metric,dens,t)
    plus=one_form_point_row(A,At,Ar,E,rad,metric,dens,np.array([.7,-1.2,0.,0.,0.,0.]))
    assert np.linalg.norm(r['Hessian']-plus['Hessian'])>1
    # A preintegrated constant tent cannot capture this pointwise cross.
    # The integrated Gauss rule reproduces its cancellation only when the
    # reference coefficients actually are constant.
    nodes,w=np.polynomial.legendre.leggauss(6);K=np.zeros((1120,1120));G=K.copy()
    for u,ww in zip(np.r_[(nodes+1)/4,(nodes+3)/4],np.tile(w/4,2)):
        tv=np.array([2*min(u,1-u),2 if u<.5 else -2,0.,0.,0.,0.])
        v=one_form_point_row(A,At,Ar,E,rad,metric,dens,tv);K+=ww*v['Hessian'];G+=ww*v['Gram']
    old=one_form_cell_row(A,At,Ar,E,rad,metric,dens,one_form_temporal_moments(1.))
    np.testing.assert_allclose(K[:800,:800],old[0][:800,:800],rtol=5e-14,atol=2e-11)
    np.testing.assert_allclose(G[:800,:800],old[1][:800,:800],rtol=5e-14,atol=2e-11)


def test_paired_scalar_orbit_has_true_rate_and_covariant_derivative(angular):
    from bhsm.interface.muon_parent_positive_coupled_field import coupled_wall_maps
    from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    from bhsm.interface.muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
    rng=np.random.default_rng(466) # CONTROL_ONLY gauge/H first germ.
    A=rng.normal(size=(5,4))*.2;H=rng.normal(size=4);Hd=rng.normal(size=4)*.3
    E=angular['derivative_matrices'];t=np.array([.8,-.4,.13,.29,-.07,.31]);rad=ghost_radial_values([WALL])[0]
    maps=coupled_wall_maps(A,E,length=1.)['wall_time_profile_value_maps'];W=np.zeros((400,1200));W[:,:1120]=np.einsum('t,tij->ij',t,maps)
    hs=paired_scalar_orbit_maps(H,Hd,t,rad)
    r=intrinsic_coupled_point_form([2.,3.,4.],H,Hd,A,E,W,hs['value'],hs['time'],lambda_H=.2,nu_squared_action=4.)
    T=higgs_u2_real_representation()['real_generators']
    expected=[]
    for base in (r['covariant_H_time'],*r['covariant_H_spatial']):
        U=np.einsum('cij,j->ci',T,base);x=np.zeros((80,320))
        for i in range(2):
            for j in range(2):x[:,160*i+80*j:160*i+80*(j+1)]=-rad[j,0]*t[2+2*i]*np.kron(U.T,np.eye(20))
        expected.append(x)
    np.testing.assert_allclose(r['scalar_covariant_first_images'][:,:,800:1120],expected,rtol=5e-14,atol=3e-16)
    without_rate=paired_scalar_orbit_maps(H,np.zeros(4),t,rad)
    assert np.linalg.norm(hs['time']-without_rate['time'])>.01
    assert np.linalg.norm(hs['value'][:,800:1120])>0


def test_literal_joint_point_Hessian_keeps_ghost_scalar_and_offshell_contacts(angular):
    from bhsm.interface.muon_parent_positive_coupled_field import coupled_wall_maps
    from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    from bhsm.interface.muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
    rng=np.random.default_rng(989) # CONTROL_ONLY supplied tangent, no physical state.
    A=rng.normal(size=(5,4))*.1;H=rng.normal(size=4);Hd=rng.normal(size=4)*.4
    E=angular['derivative_matrices'];Y=angular['basis_values'];hw=angular['Haar_weights']
    t=np.array([.8,-.4,.13,.29,-.07,.31]);rad=ghost_radial_values([WALL])[0]
    maps=coupled_wall_maps(A,E,length=1.)['wall_time_profile_value_maps'];W=np.zeros((400,1200));W[:,:1120]=np.einsum('t,tij->ij',t,maps)
    hs=paired_scalar_orbit_maps(H,Hd,t,rad);weights=np.array([2.,3.,4.]);lam=.23;nu=1.4
    r=intrinsic_coupled_point_form(weights,H,Hd,A,E,W,hs['value'],hs['time'],lambda_H=lam,nu_squared_action=nu)
    z=rng.normal(size=1200)*.04;ag=(W@z).reshape(5,4,20);h=(hs['value']@z).reshape(4,20);ht=(hs['time']@z).reshape(4,20)
    T=higgs_u2_real_representation()['real_generators']
    def value(e):
        a=A[None]+e*np.einsum('ph,fch->pfc',Y,ag);o=np.einsum('pfc,cij->pfij',a,T)
        hv=H[None]+e*(Y@h.T);dt=Hd[None]+e*(Y@ht.T)+np.einsum('pij,pj->pi',o[:,0],hv)
        ds=np.array([e*(Y@(h@E[i].T).T)+np.einsum('pij,pj->pi',o[:,2+i],hv) for i in range(3)])
        return (hw@(weights[0]*np.sum(dt**2,axis=1)+weights[1]*np.sum(ds**2,axis=(0,2))+weights[2]*lam*(np.sum(hv**2,axis=1)-nu)**2))/(2*np.pi**2)
    eps=.02;zero=value(0);second=(16*(value(eps)+value(-eps)-2*zero)-(value(2*eps)+value(-2*eps)-2*zero))/(12*eps**2)
    assert z@r['Hessian']@z==pytest.approx(second,rel=3e-8,abs=3e-10)
    assert np.linalg.norm(r['Gram'][800:1120,1120:])>0 # actual shared scalar image, not block-diagonal omission.


def test_invalid_complete_point_operands_fail_closed(angular):
    E=angular['derivative_matrices'];W=np.zeros((400,1200));h=np.zeros((80,1200))
    with pytest.raises(ValueError):intrinsic_coupled_point_form([1.,1.,1.],np.ones(4),np.zeros(4),np.zeros((5,4)),E,W,h,h,lambda_H=.2,nu_squared_action=-1.)
    with pytest.raises(ValueError):paired_scalar_orbit_maps(np.ones(4),np.zeros(4),np.zeros(5),np.zeros((2,3)))
