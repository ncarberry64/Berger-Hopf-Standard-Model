"""Actual finite form and independent CONTROL_ONLY action/domain checks."""
import numpy as np
import pytest
from bhsm.interface.muon_parent_positive_gauge_form import (
    one_form_temporal_moments,one_form_cell_row,positive_curvature_contact_matrix,
    positive_parent_gauge_application,stored_inverse_neumann_majorant,
)


@pytest.fixture(scope='module')
def actual():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    f=magnetic_open_fields_at_node(b,b['source']['times'][2]);angular=retained_full_q_angular_space(ROOT)
    r=positive_parent_gauge_application(f['raw_fields'],b['representation'],angular,length=b['receipt']['chronological_response_span'])
    return b,f,angular,r


def test_exact_tent_and_h2_polynomial_cross_moments():
    import sympy as s
    u=s.symbols('u');g=u**2*(1-u)**2;h=(2*u-1)*g
    left=[2*u,2,g,s.diff(g,u),h,s.diff(h,u)]
    right=[2*(1-u),-2,g,s.diff(g,u),h,s.diff(h,u)]
    exact=np.array([[float(s.integrate(a*b,(u,0,s.Rational(1,2)))+
        s.integrate(c*d,(u,s.Rational(1,2),1))) for b,d in zip(left,right)] for a,c in zip(left,right)])
    np.testing.assert_array_equal(one_form_temporal_moments(1.),exact)
    assert exact[0,3]==0 and exact[0,5]!=0 # odd ghost detects temporal tent divergence.
    with pytest.raises(ValueError):one_form_temporal_moments(0)


def test_literal_contact_pairing_is_symmetric_and_keeps_time_radial_terms():
    from bhsm.interface.muon_parent_maxwell_full_weak import _bracket,_second_curvatures
    from bhsm.interface.muon_parent_maxwell_corrected_retarded import constant_angular_curvatures
    rng=np.random.default_rng(773) # CONTROL_ONLY finite action vectors, not a state.
    A,At,Ar=rng.normal(size=(3,5,4));a,b=rng.normal(size=(2,5,4));dens=np.array([2.,3.,4.,5.,.17])
    F=constant_angular_curvatures(A,At,Ar);c=_second_curvatures(a,b);e,r,d,k,beta=dens
    expected=k*F['Ftr']@c[0]+e*np.sum((F['Ft']-beta*F['Fr'])*(c[1]-beta*c[2]))+r*np.sum(F['Fr']*c[2])+d*np.sum(F['B']*c[3])
    C=positive_curvature_contact_matrix(F,dens,1)
    np.testing.assert_allclose(C,C.T,atol=1e-15)
    assert a.ravel()@C@b.ravel()==pytest.approx(expected,rel=2e-15)
    assert np.linalg.norm(C[:8,8:])>0 and np.linalg.norm(C[:4,4:8])>0


def test_augmented_row_matches_literal_polynomial_action_with_full_gradient_jets(actual):
    from bhsm.interface.muon_parent_positive_brst_ghost import smooth_ghost_temporal_values,covariant_ghost_gradient_images
    from bhsm.interface.muon_parent_maxwell_full_weak import _bracket
    from bhsm.interface.muon_matched_mechanical_source import epsilon
    b,f,angular,r=actual;j=len(r['rho'])//2
    A,At,Ar=[r[key][j] for key in ('background_values','background_time_derivatives','background_radial_derivatives')]
    E=angular['derivative_matrices'];rad=r['radial_profile_value_rate_second'][j]
    dens=r['positive_two_form_densities'][j];metric=r['positive_metric_coefficients'][j];eps=epsilon()
    # CONTROL_ONLY trial coefficient and interval exercise the entire1120
    # domain without importing a physical source/quantum state.
    rng=np.random.default_rng(491);z=rng.normal(size=1120)*.03
    K,G,C=one_form_cell_row(A,At,Ar,E,rad,metric,dens,one_form_temporal_moments(1.))
    nodes,w=np.polynomial.legendre.leggauss(7);times=np.concatenate(((nodes+1)/4,(nodes+3)/4));weights=np.tile(w/4,2)
    ts=smooth_ghost_temporal_values(times,1.);values=angular['basis_values'];hw=angular['Haar_weights'];e,rr,d,k,beta=dens
    action=lambda val,tau,rho,ang:.5*np.sum(hw*(k*np.sum((tau[:,1]-rho[:,0]+_bracket(val[:,0],val[:,1]))**2,axis=1)+
        e*np.sum((tau[:,2:]-ang[:,:,0]+_bracket(val[:,0,None],val[:,2:])-beta*(rho[:,2:]-ang[:,:,1]+_bracket(val[:,1,None],val[:,2:])))**2,axis=(1,2))+
        rr*np.sum((rho[:,2:]-ang[:,:,1]+_bracket(val[:,1,None],val[:,2:]))**2,axis=(1,2))+
        d*np.sum((2*val[:,2:]+np.einsum('ijk,pjkc->pic',eps,ang[:,:,2:])+
            .5*np.einsum('ijk,pjkc->pic',eps,_bracket(val[:,2:,None],val[:,None,2:])))**2,axis=(1,2))))
    def total(h):
        out=0.
        for t,tv,ww in zip(times,ts,weights):
            tent=2*min(t,1-t);rate=2 if t<.5 else -2
            field=z[:800].reshape(2,5,4,20)
            v=tent*np.einsum('r,rfch->fch',rad[:,0],field)
            vt=rate*np.einsum('r,rfch->fch',rad[:,0],field)
            vr=tent*np.einsum('r,rfch->fch',rad[:,1],field)
            va=np.einsum('phk,fck->pfch',E,v)
            g=covariant_ghost_gradient_images(A,At,Ar,E,tv,rad)
            v+=np.reshape(g['value']@z[800:],(5,4,20));vt+=np.reshape(g['time']@z[800:],(5,4,20));vr+=np.reshape(g['radial']@z[800:],(5,4,20));va+=np.reshape(g['angular']@z[800:],(3,5,4,20))
            pv=A[None]+h*np.einsum('ph,fch->pfc',values,v)
            pt=At[None]+h*np.einsum('ph,fch->pfc',values,vt)
            pr=Ar[None]+h*np.einsum('ph,fch->pfc',values,vr)
            pa=h*np.einsum('qh,ifch->qifc',values,va)
            out+=ww*action(pv,pt,pr,pa)
        return out
    step=.03;zero=total(0);second=(16*(total(step)+total(-step)-2*zero)-(total(2*step)+total(-2*step)-2*zero))/(12*step**2)
    assert z@K@z==pytest.approx(second,rel=3e-8,abs=2e-9)
    assert abs(z@C@z)>1e-4 # contact cannot be silently dropped.
    assert z@G@z>0


def test_actual_ghost_images_and_lorenz_fix_use_same_domain(actual):
    b,f,a,r=actual
    G=r['one_form_Gram'];D=r['ghost_gradient_coordinate_injection'];F=r['weak_Lorenz_map']
    assert G.shape==(1120,1120) and D.shape==(1120,320)
    np.testing.assert_array_equal(D[:800],np.zeros((800,320)))
    np.testing.assert_allclose(D.T@G@D,r['ghost_FP_Hessian'],rtol=2e-14,atol=1e-8)
    np.testing.assert_allclose(r['ghost_Gram']@F,r['weak_gradient_pairing'],rtol=2e-12,atol=1e-9)
    assert r['ghost_image_FP_relative_error']<3e-15
    assert np.linalg.norm(r['one_form_curvature_contact'])>1000
    assert r['finite_gauge_fixed_form_positive']
    assert r['gauge_fixed_eigenvalues'][0]>2
    assert r['normalized_inverse_residual']<2e-4
    assert r['stored_normalized_inverse_majorant']['defect_infinity_upper']<1
    assert not r['intrinsic_Higgs_gauge_boundary_mass_and_mixed_rows_included']
    assert not r['physical_Wick_relative_BRST_quotient_or_LSZ_completed']


def test_boundary_product_complement_is_retained_and_wall_trace_is_full(actual):
    b,f,a,r=actual;L=b['receipt']['chronological_response_span']
    assert r['vertex_time_projection'][0]==pytest.approx(.75)
    assert r['source_product_complement_Gram'][0,0]==pytest.approx(L/80,rel=2e-15)
    assert not r['temporal_product_image_complete_in_single_tent']
    maps=r['wall_time_profile_value_maps'].reshape(6,5,80,1120)
    assert np.linalg.norm(maps[0,0])>0 and np.linalg.norm(maps[0,1])>0
    # Interior ghosts vanish at wall but retain a radial derivative there.
    assert np.linalg.norm(maps[2,1, :,800:880])>0
    assert r['projected_wall_one_form_Green'].shape==(400,400)
    assert np.linalg.norm(r['projected_wall_one_form_Green'])>0


def test_exact_stored_neumann_majorant_is_not_upstream_or_zero_filled():
    import sympy as s
    A=np.array([[2.,1.],[1.,3.]]);M=np.array([[.59,-.19],[-.19,.39]])
    exact=np.array(s.Matrix(A).inv(),float);r=stored_inverse_neumann_majorant(A,M)
    assert np.linalg.norm(exact-M,np.inf)<=r['exact_stored_inverse_difference_infinity_upper']
    assert np.linalg.norm(exact,np.inf)<=r['exact_stored_inverse_infinity_upper']
    assert not r['operator_or_Gram_production_error_included']
    failed=stored_inverse_neumann_majorant(A,2*np.eye(2))
    assert failed['exact_stored_inverse_infinity_upper'] is None
    with pytest.raises(ValueError):stored_inverse_neumann_majorant(A,np.array([[np.nan,0],[0,1]]))
