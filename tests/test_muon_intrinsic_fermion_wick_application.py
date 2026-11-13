import numpy as np
import pytest
from bhsm.interface.muon_intrinsic_fermion_wick_application import (
    continued_fermion_source_vertices,temporal_contour_gauge_covariance,
    fermion_wick_application,
)
from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from bhsm.interface.muon_changing_coupled_open_current import positive_factor_open_vertices
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase


def test_actual_owned_temporal_vertex_rotation_and_both_fixed_y_placements():
    R,N=.91,.73
    a=continued_fermion_source_vertices(R,N)
    L=canonical_open_field_vertices(R,N);P=positive_factor_open_vertices(R,N)
    np.testing.assert_array_equal(a['gauge'],L['gauge'])
    np.testing.assert_array_equal(a['scalar'],L['scalar'])
    np.testing.assert_array_equal(a['gauge'][0],-1j*P['gauge'][0])
    np.testing.assert_array_equal(a['gauge'][2:],P['gauge'][2:])
    assert np.count_nonzero(a['scalar'][:,:12,12:])>0
    assert np.count_nonzero(a['scalar'][:,12:,:12])>0


def test_tau_dependent_gauge_frame_requires_the_continued_derivative():
    Q=np.diag([1.,-2.,3.]);r=temporal_contour_gauge_covariance(Q,.5)
    np.testing.assert_array_equal(r['Lorentz_Hcan_frame_contact']+r['continued_temporal_derivative_frame_contact'],0)
    assert np.linalg.norm(r['real_time_derivative_reuse_residual'])>1


def test_actual_corrected_phase_operator_time_principals_and_full_raw_jets():
    p=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    r=fermion_wick_application(p,abs(p['receipt']['span'])/2)
    assert r['continued_body'].shape==(18,18)
    assert r['continued_body_raw_first_jet'].shape==(268,18,18)
    assert r['body_Lorentz_contour_identity_residual']<1e-14
    expected=-(1+1j)*r['Omega_L_proper_time']
    np.testing.assert_allclose(r['positive_reference_body_difference'],expected,atol=5e-16)
    assert np.count_nonzero(expected)>0
    assert np.linalg.norm(r['continued_body_tau_first'])>0
    assert np.linalg.norm(r['temporal_principal_tau_first'])>0
    assert not r['canonical_far_faces_changed']
    assert not r['full_finite_contour_or_positive_native_square_identified']


def test_continued_principal_and_body_time_germs_against_actual_cell_differences():
    p=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    u=abs(p['receipt']['span'])/2;h=1e-8
    r=fermion_wick_application(p,u);a=fermion_wick_application(p,u+h);b=fermion_wick_application(p,u-h)
    for key in ('continued_body','temporal_principal','spatial_principal'):
        actual=-1j*(a[key]-b[key])/(2*h)
        np.testing.assert_allclose(r[key+'_tau_first'],actual,rtol=2e-5,atol=1e-7)


def test_missing_or_nonreal_geometry_and_nonhermitian_frame_rejected():
    for x in (None,-1.,1+1j):
        with pytest.raises(ValueError):continued_fermion_source_vertices(x,1.)
    with pytest.raises(ValueError):temporal_contour_gauge_covariance([[0,1],[0,0]],1.)
