"""Current geometric normalization and full response source-image checks."""
import numpy as np
import pytest

from bhsm.interface.muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
from bhsm.interface.muon_native_current_component_heat import (
    current_geometric_photon_component,current_component_dual_response,
    component_response_fermion_image,current_component_response_heat_core,
    current_component_source_history,
)
from bhsm.interface.muon_native_product_factor_graph import finite_eight_q_cutoff_heat_application
from bhsm.interface.muon_parent_maxwell_full_weak import full_maxwell_gauge_hessian_matrix
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_parent_gauge_geometry_correction import finite_common_iterate_at_time,MAXWELL_TO_CAP
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


def test_actual_current_b_normalization_retains_moving_geometry_two_jets():
    response=retained_corrected_scalar_photon_response();a=current_geometric_photon_component(response,0.)
    assert a['source_frame_identity_residual']<5e-16
    assert a['current_source_Gram_residual']<2e-12
    np.testing.assert_allclose(a['T_b'],1/np.sqrt(2*np.pi**2*a['R4']),rtol=5e-16)
    R=a['intrinsic_geometry']['R4'];Tb=a['T_b']
    np.testing.assert_allclose(a['T_b_geometric_gradient'],-.5*Tb*R.gradient/R.value,rtol=3e-15,atol=1e-30)
    wanted=Tb*(.75*np.outer(R.gradient,R.gradient)/R.value**2-.5*R.hessian/R.value)
    np.testing.assert_allclose(a['T_b_geometric_hessian'],wanted,rtol=3e-14,atol=1e-28)
    assert np.linalg.norm(a['coefficient_geometric_jacobian'][:,-2:])>0
    assert a['negative_Lorentz_angular_sign_retained']


def test_fresh_full_angular_response_and_heat_image_do_not_compress_to_original_Q():
    response=retained_corrected_scalar_photon_response();component=current_geometric_photon_component(response,0.)
    result=current_component_dual_response(component,multipliers=(1.25,));r=result['records'][0]
    J=result['current']['dual_current_basis'];H=component['K_per_kappa1']+r['zeta_over_kappa1']*component['M_geometric_scalar']*np.eye(240)
    np.testing.assert_allclose(r['basis_response'],np.linalg.solve(H,J),rtol=1e-11,atol=1e-13)
    assert result['independent_frame'].shape[1]>8
    assert r['outside_original_Q8_relative_norm']>1e-4
    image=component_response_fermion_image(component,r)
    assert image['unit_radius_b_source_image'].shape==(8,20,18,18)
    assert image['Hermiticity_coefficient_residual']<1e-10
    assert not result['actual_physical_current_covector_selected']
    core=current_component_response_heat_core(response,component,r,time_nodes=np.linspace(-.001,0,5),quadrature_order=3,family_indices=(1,))
    application=finite_eight_q_cutoff_heat_application(core,4.7240808471919143e-8)
    row=application['families']['1']
    assert np.isfinite(row['integrated_paired_heat_mixed']).all()
    assert np.linalg.norm(row['integrated_source_square_contact'])>0
    assert np.linalg.norm(row['integrated_ordered_two_insertion'])>0
    np.testing.assert_allclose(row['integrated_paired_heat_mixed'],row['integrated_source_square_contact']+row['integrated_ordered_two_insertion']+row['integrated_opposite_order_two_insertion'],rtol=1e-14,atol=1e-24)
    assert not core['genuine_coupled_source_geometry_H_gauge_response_included']


def test_reached_current_core_rejects_extrapolation_and_missing_directions():
    response=retained_corrected_scalar_photon_response()
    with pytest.raises(ValueError,match='extrapolate'):current_geometric_photon_component(response,.001)
    component=current_geometric_photon_component(response,0.)
    with pytest.raises(ValueError,match='required'):component_response_fermion_image(component,dict(basis_response=None))


def test_moving_source_history_derivative_uses_same_wall_and_geometry():
    response=retained_corrected_scalar_photon_response();component=current_geometric_photon_component(response,0.)
    r=current_component_dual_response(component,multipliers=(1.25,))['records'][0]
    t=-.00042;h=1e-8
    hist=current_component_source_history(response,component,r,np.array([t-h,t,t+h]))
    difference=(hist['full400_source_Q'][2]-hist['full400_source_Q'][0])/(2*h)
    np.testing.assert_allclose(hist['full400_source_Qdot'][1],difference,rtol=3e-7,atol=1e-8)
    assert hist['full400_source_Q'].shape==(3,400,8)
    assert hist['source_normal_hessian'].shape==(3,400,8,2,2)
    assert np.count_nonzero(hist['full400_source_Q'][:,:160])==0
    assert not hist['source_profile_included']


def test_angular_component_sign_and_contact_equal_literal_owned_full_weak_row():
    response=retained_corrected_scalar_photon_response();component=current_geometric_photon_component(response,0.)
    d=finite_common_iterate_at_time(0.,response['coefficients'],response['representation'],response['reference'],rho=np.array([WALL]))
    geo=geometric_connection_coefficient_jets(12,d['q'],d['qdot'],d['m'],np.array([WALL]),source_value=d['normal'],source_rate=d['normal_rate'])
    angular=component['angular'];q=component['source_inclusion'].reshape(3,4,20,8);Tb=component['T_b']
    value=Tb*np.einsum('ichA,ph->Apic',q,angular['basis_values'])
    derivative=Tb*np.einsum('ichA,pdh->Apdic',q,angular['basis_derivative_values'])
    count=len(angular['Haar_weights']);gauge=np.zeros((1,count,5,4));ga=np.zeros((1,count,3,5,4))
    test=np.zeros((1,8,count,5,4));test[0,:,:,2:]=value
    ea=np.zeros((1,8,count,3,5,4));ea[0,:,:,:,2:]=derivative
    result=full_maxwell_gauge_hessian_matrix(geo,np.ones(1),angular['Haar_weights'],gauge=gauge,gauge_tau=gauge,gauge_rho=gauge,gauge_angular=ga,
        tests=test,tests_tau=np.zeros_like(test),tests_rho=np.zeros_like(test),tests_angular=ea)
    S=component['source_inclusion'];expected=S.T@component['K_per_kappa1']@S
    np.testing.assert_allclose(expected,MAXWELL_TO_CAP*result['matrix'],rtol=2e-12,atol=1e-12)
    assert np.linalg.norm(result['curvature_contact_matrix'])>0
