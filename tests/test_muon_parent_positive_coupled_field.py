"""Independent literal-action controls and actual corrected-profile binding."""
import numpy as np
import pytest
from bhsm.interface.muon_parent_positive_coupled_field import (
    corrected_positive_parent_reference, coupled_wall_maps,
    intrinsic_gauge_higgs_boundary_blocks, full18_coupled_current_contraction,
)


@pytest.fixture(scope='module')
def actual():
    from pathlib import Path
    from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    b=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing')
    with np.load(ROOT/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1/application.npz') as a:
        saved={k:a[k].copy() for k in a.files}
    return b,saved,retained_full_q_angular_space(ROOT)


def test_corrected_wall_binding_keeps_full_profile_rate_and_radial_image(actual):
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    from bhsm.interface.muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator
    b,s,a=actual;raw=s['stage_independent_raw'][0];t=s['stage_coordinate_time'][0]
    rep=dict(b['representation']);rep['rho']=np.array([WALL]);rep['radial_quadrature']=np.ones(1)
    rep['gauge_basis']=np.moveaxis(rep['wall_trace_map'],-1,0)[None,:,None]
    rep['gauge_radial_basis']=np.moveaxis(rep['wall_radial_derivative_map'],-1,0)[None,:,None]
    r=corrected_positive_parent_reference(raw,rep,coordinate_time=t,initial_pair=s['initial_pair'],reference_pair=s['reference_pair'])
    op=inherited_intrinsic_lepton_operator(raw,t,s['initial_pair'],s['reference_pair'],b['representation'])
    np.testing.assert_allclose(r['background_values'][0],op['total_wall_connection'],rtol=0,atol=8e-16)
    np.testing.assert_allclose(r['background_time_derivatives'][0,2:],op['total_wall_spatial_connection_coordinate_rate'],rtol=0,atol=8e-16)
    np.testing.assert_allclose(r['inherited_profile_value_time_radial'][0],s['stage_wall_profile'][0],rtol=0,atol=5e-16)
    assert np.linalg.norm(r['inherited_profile_value_time_radial'])>1e-9
    assert r['exact_normal_geometry_applied'] and r['material_connection_embedding_count']==1
    assert r['extra_connection_Ar_advection_count']==0
    with pytest.raises(ValueError,match='both initial and reference'):
        corrected_positive_parent_reference(raw,rep,coordinate_time=t,initial_pair=s['initial_pair'])


def test_full_intrinsic_mass_and_cross_hessian_matches_independent_literal_action(actual):
    from bhsm.interface.muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
    from bhsm.interface.muon_parent_positive_brst_ghost import smooth_ghost_temporal_values
    b,s,angular=actual;E=angular['derivative_matrices'];Y=angular['basis_values'];hw=angular['Haar_weights']
    rng=np.random.default_rng(815) # CONTROL_ONLY trial/action coefficients, no state selection.
    A=rng.normal(size=(5,4))*.15;H=rng.normal(size=4);Hdot=rng.normal(size=4)*.2
    wt,ws,wv=2.,.7,1.3;lam=.31;nu=1.1;L=1.
    wall=coupled_wall_maps(A,E,length=L)
    r=intrinsic_gauge_higgs_boundary_blocks((wt,ws,wv),H,Hdot,A,E,wall['wall_time_profile_value_maps'],length=L,lambda_H=lam,nu_squared_action=nu)
    gauge=rng.normal(size=1120)*.03;scalar=rng.normal(size=(4,20))*.04
    T=higgs_u2_real_representation()['real_generators'];Omega=np.einsum('fc,cij->fij',A,T)
    nodes,w=np.polynomial.legendre.leggauss(7)
    times=np.concatenate(((nodes+1)/4,(nodes+3)/4));weights=np.tile(w/4,2)
    ghost=smooth_ghost_temporal_values(times,L)
    def value(eps,delta):
        out=0.
        for time,tg,weight in zip(times,ghost,weights):
            tent=2*min(time,1-time);rate=2 if time<.5 else -2
            functions=np.array([tent,rate,tg[0,0],tg[0,1],tg[1,0],tg[1,1]])
            ag=(np.einsum('t,tij,j->i',functions,wall['wall_time_profile_value_maps'],gauge)).reshape(5,4,20)
            av=A[None]+eps*np.einsum('qh,fch->qfc',Y,ag)
            om=np.einsum('qfc,cij->qfij',av,T)
            h=H[None]+delta*tent*(Y@scalar.T)
            ordinary=Hdot[None]+delta*rate*(Y@scalar.T)
            dt=ordinary+np.einsum('qij,qj->qi',om[:,0],h)
            ds=[]
            for i in range(3):
                ds.append(delta*tent*(Y@(scalar@E[i].T).T)+np.einsum('qij,qj->qi',om[:,2+i],h))
            ds=np.array(ds)
            integrand=wt*np.sum(dt**2,axis=1)+ws*np.sum(ds**2,axis=(0,2))+wv*lam*(np.sum(h**2,axis=1)-nu)**2
            out+=weight*(hw@integrand)/(2*np.pi**2)
        return out
    h=.015
    # Separate polarized derivatives avoid a total Hessian test that could
    # conceal a missing mixed placement or a wrong factor of two.
    mixed=(value(h,h)-value(h,-h)-value(-h,h)+value(-h,-h))/(4*h*h)
    expected=gauge@r['boundary_gauge_Higgs_mixed_Hessian']@scalar.ravel()
    assert mixed==pytest.approx(expected,rel=3e-8,abs=3e-10)
    def second(f):
        zero=f(0);return (16*(f(h)+f(-h)-2*zero)-(f(2*h)+f(-2*h)-2*zero))/(12*h*h)
    assert second(lambda e:value(e,0))==pytest.approx(gauge@r['boundary_gauge_mass_Hessian']@gauge,rel=3e-8,abs=3e-10)
    assert second(lambda d:value(0,d))==pytest.approx(scalar.ravel()@r['intrinsic_Higgs_Hessian']@scalar.ravel(),rel=3e-8,abs=3e-10)


def test_actual_background_Hdot_cannot_be_dropped_from_cross_rows(actual):
    b,s,a=actual;E=a['derivative_matrices'];A=np.zeros((5,4));H=np.array([.4,.9,.2,-.1]);hd=np.array([.3,-.2,.6,.7])
    W=coupled_wall_maps(A,E,length=.5)['wall_time_profile_value_maps']
    opts=dict(length=.5,lambda_H=.2,nu_squared_action=4.)
    r=intrinsic_gauge_higgs_boundary_blocks((2.,3.,4.),H,hd,A,E,W,**opts)
    zero=intrinsic_gauge_higgs_boundary_blocks((2.,3.,4.),H,np.zeros(4),A,E,W,**opts)
    np.testing.assert_array_equal(r['intrinsic_Higgs_Hessian'],zero['intrinsic_Higgs_Hessian'])
    np.testing.assert_array_equal(r['boundary_gauge_mass_Hessian'],zero['boundary_gauge_mass_Hessian'])
    assert np.linalg.norm(r['boundary_gauge_Higgs_mixed_Hessian']-zero['boundary_gauge_Higgs_mixed_Hessian'])>.01
    np.testing.assert_array_equal(r['actual_H_covariant_time_derivative'],hd)


def test_full18_open_contraction_retains_both_gauge_H_cross_placements():
    # CONTROL_ONLY algebra fixture: two noncommuting vertices and one
    # offdiagonal field covariance distinguish a joint inverse from sector sums.
    v=np.zeros((5,4,18,18),complex);s=np.zeros((4,18,18),complex)
    v[0,0,:2,:2]=[[1,1j],[-1j,0]];s[0,:2,:2]=[[0,2],[3,1]]
    G=np.zeros((480,480));G[0,400]=.7;G[400,0]=.7
    got=full18_coupled_current_contraction(G,v,s)
    A=v[0,0];B=s[0]
    np.testing.assert_array_equal(got,.7*(A.conj().T@B+B.conj().T@A))
    assert np.linalg.norm(got)>1
    assert np.linalg.norm(full18_coupled_current_contraction(np.diag(np.diag(G)),v,s))==0
    with pytest.raises(ValueError):full18_coupled_current_contraction(G[:400,:400],v,s)


def test_one_joint_inverse_differs_from_sum_of_sector_inverses():
    # Independent exact CONTROL_ONLY Schur check; no model inverse or state.
    import sympy as sp
    K=sp.Matrix([[3,1],[1,2]]);G=K.inv();separate=sp.diag(sp.Rational(1,3),sp.Rational(1,2))
    assert G!=separate and G[0,1]==-sp.Rational(1,5)
    C=K-sp.diag(3,2)
    assert G-separate==-separate*C*G
