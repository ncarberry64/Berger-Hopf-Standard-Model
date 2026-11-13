"""Exact temporal domain, actual covariant images and off-shell Ward tests."""
import numpy as np
import pytest
from bhsm.interface.muon_parent_positive_brst_ghost import (
    smooth_ghost_temporal_values,ghost_temporal_moments,ghost_radial_values,
    covariant_ghost_gradient_images,positive_parent_ghost_application,
)


@pytest.fixture(scope='module')
def actual():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    f=magnetic_open_fields_at_node(b,b['source']['times'][2]);a=retained_full_q_angular_space(ROOT)
    r=positive_parent_ghost_application(f['raw_fields'],b['representation'],a,
        length=b['receipt']['chronological_response_span'],first_gauge=f['first_gauge'],
        first_gauge_rate=f['first_gauge_rate'],first_gauge_radial=f['first_gauge_radial'])
    return b,f,a,r


def test_smooth_ghost_has_exact_moments_and_h2_endpoint_compatibility():
    import sympy as s
    u=s.symbols('u');g=[u**2*(1-u)**2,(2*u-1)*u**2*(1-u)**2]
    m=ghost_temporal_moments(1.)
    for key,orders in [('value_value',(0,0)),('rate_value',(1,0)),('value_rate',(0,1)),('rate_rate',(1,1))]:
        exact=np.array([[float(s.integrate(s.diff(a,u,orders[0])*s.diff(b,u,orders[1]),(u,0,1))) for b in g] for a in g])
        np.testing.assert_array_equal(m[key],exact)
    ends=smooth_ghost_temporal_values([0.,1.],1.)
    np.testing.assert_array_equal(ends[:,:,:2],np.zeros((2,2,2)))
    assert np.linalg.norm(ends[:,:,2])>0 # derivatives are retained, not zero-filled.
    with pytest.raises(ValueError):smooth_ghost_temporal_values([1.1],1.)


def test_radial_gradient_second_jet_agrees_with_same_profile_derivative():
    from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis,WALL
    rho=WALL*np.array([.14,.52,.88]);h=1e-5
    analytic=ghost_radial_values(rho)
    fd=(regular_radial_basis(rho+h,1)[1]-regular_radial_basis(rho-h,1)[1])/(2*h)
    np.testing.assert_allclose(analytic[:,:,2],fd,rtol=2e-9,atol=3e-9)
    assert np.isfinite(ghost_radial_values([WALL])).all()


def test_actual_positive_form_matches_independent_gradient_quadrature(actual):
    b,f,a,r=actual
    from bhsm.interface.muon_parent_positive_brst_ghost import _ghost_form_row
    j=len(r['rho'])//2;A,At,Ar=[r[k][j] for k in ('background_values','background_time_derivatives','background_radial_derivatives')]
    metric=r['positive_metric_coefficients'][j];mu,gt,gr,gs,beta,R=metric
    rng=np.random.default_rng(713) # CONTROL_ONLY test coordinate, not a state.
    z=rng.normal(size=320);z/=np.linalg.norm(z)
    K,G=_ghost_form_row(A,a['derivative_matrices'],r['ghost_radial_basis_value_rate_second'][j],metric,ghost_temporal_moments(b['receipt']['chronological_response_span']))
    value=gram=0.
    for t,w in zip(r['ghost_temporal_basis_value_rate_second'],r['ghost_temporal_weights']):
        images=covariant_ghost_gradient_images(A,At,Ar,a['derivative_matrices'],t,r['ghost_radial_basis_value_rate_second'][j])
        v=images['value']@z;eta=images['eta']@z
        value+=w*(gt*np.sum((v[0]-beta*v[1])**2)+gr*np.sum(v[1]**2)+gs*np.sum(v[2:]**2))
        gram+=w*mu*np.sum(eta**2)
    assert value==pytest.approx(z@K@z,rel=4e-15)
    assert gram==pytest.approx(z@G@z,rel=4e-15)


def test_actual_offshell_euler_contact_cannot_be_removed_from_ward_or_quotient(actual):
    b,f,a,r=actual
    H,EC,W=[r[k] for k in ('source_gauge_hessian_against_all_ghost_gradients','source_gauge_Euler_contact','source_offshell_Ward_residual')]
    assert H.shape==(8,320)
    assert np.linalg.norm(H)>3e-4 and np.linalg.norm(EC)>3e-4
    assert np.linalg.norm(W)<1e-17
    np.testing.assert_allclose(H+EC,W,atol=1e-19,rtol=0)
    assert r['covariant_curvature_image_relative_error']<3e-14
    assert r['ghost_eigenvalues'][0]>1e11
    assert r['inverse_residual']<2e-12
    assert r['fixed_boson_direct_open_lepton_ghost_vertex']==0
    assert not r['full_one_form_gauge_fixed_inverse_completed']
    assert not r['physical_Wick_relative_BRST_quotient_or_LSZ_completed']
    assert r['physical_a_mu'] is None
