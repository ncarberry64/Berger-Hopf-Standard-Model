"""Actual nonlinear action, constraints and finite correction checks."""
import numpy as np
import pytest

from bhsm.interface.muon_birth_candidate_geometry_action import ROOT
from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_parent_retarded_hypercharge import SOURCE
from bhsm.interface.muon_parent_gauge_geometry_correction import (
    compact_temporal_basis,correction_representation,coupled_sector_application,
    finite_newton_correction,ORBIT_VOLUME_SQUARED,MAXWELL_TO_CAP,
    iterate_finite_newton,corrected_Q_hessian_and_Ward,
    finite_action_contacts,finite_common_iterate_at_time,
    prolong_finite_coefficients,
)


@pytest.fixture(scope='module')
def application():
    reference=retained_state(ROOT)
    representation=correction_representation(time_points=3,radial_points=16,radial_order=1,cap_points=16)
    zero=np.zeros(representation['count'])
    return reference,representation,zero,coupled_sector_application(zero,representation,reference)


def test_compact_variations_preserve_past_and_future_reference_traces_without_new_event_terms():
    value,rate=compact_temporal_basis(np.array([-.001,0.]),.001)
    np.testing.assert_array_equal(value,0.)
    np.testing.assert_array_equal(rate,0.)
    rep=correction_representation(radial_order=2)
    assert not rep['physical_branch_duration']
    assert rep['count']==106
    assert {r['field'] for r in rep['gauge_labels']}=={'A_tau','A_rho','A_1','A_2','A_3'}


def test_cap_orbit_and_actual_trace_normalization_are_not_set_to_one():
    with np.load(ROOT/SOURCE,allow_pickle=False) as z:
        basis=z['unit_trace_carrier_basis']
    actual=np.sqrt(8)*basis[:3]
    gram=np.einsum('aij,bij->ab',actual.conj(),actual).real
    np.testing.assert_allclose(gram,8*np.eye(3),atol=4e-14)
    assert MAXWELL_TO_CAP==pytest.approx(1/(8*ORBIT_VOLUME_SQUARED),rel=1e-15)


def test_background_energy_subtraction_retains_full_mixed_block_and_all_multiplier_gauss_rows(application):
    _,rep,_,a=application
    gauge=a['sectors']['independent_Maxwell']
    np.testing.assert_array_equal(gauge['residual'][:62],0.)
    np.testing.assert_array_equal(gauge['hessian'][:62,:62],0.)
    assert np.linalg.norm(gauge['hessian'][62:,:62])>0
    assert a['scalar_unknown_count']==4
    assert np.linalg.norm(a['sectors']['intrinsic_H_kinetic_quartic']['hessian'][-4:,-4:])>0
    assert a['multiplier_rows'].shape==(24,)
    assert a['Gauss_rows'].shape==(rep['radial_order'],2,4)
    assert not a['Gauss_rows_eliminated']
    assert not a['background_Maxwell_added_again']
    assert np.max(abs(a['hessian']-a['hessian'].T))<1e-7


def test_common_residual_and_hessian_are_nonlinear_action_derivatives(application):
    reference,rep,zero,_=application
    direction=np.zeros(rep['count'])
    direction[[0,4,17,28,38,48,61,63,69,75]]=[.002,-.001,.001,.0005,.003,-.002,.0001,.002,-.001,.003]
    direction[-4:]=[.002,-.001,.003,.001]
    state=zero+2e-4*direction
    center=coupled_sector_application(state,rep,reference)
    step=2e-4
    plus=coupled_sector_application(state+step*direction,rep,reference)
    minus=coupled_sector_application(state-step*direction,rep,reference)
    first=(plus['value']-minus['value'])/(2*step)
    assert direction@center['residual']==pytest.approx(first,rel=1e-6,abs=2e-9)
    actual=center['hessian']@direction
    numerical=(plus['residual']-minus['residual'])/(2*step)
    np.testing.assert_allclose(actual,numerical,rtol=2e-6,atol=2e-7)


def test_real_correction_reduces_actual_residual_and_consumes_scalar_surface_loads(application):
    reference,rep,zero,_=application
    result=finite_newton_correction(zero,rep,reference)
    assert result['accepted']
    assert result['scaled_updated_residual']<result['scaled_initial_residual']/4
    assert result['rank']+result['nullity']==rep['count']
    assert np.linalg.norm(result['linearized_residual'])<1e-8
    assert np.linalg.norm(result['scalar_vacuum_coefficient_correction_sensitivity'])>0
    assert np.linalg.norm(result['surface_gamma_correction_sensitivity'])>0
    assert np.linalg.norm(result['scalar_sensitivity_linear_residual'])<1e-8
    assert np.linalg.norm(result['surface_sensitivity_linear_residual'])<1e-8
    assert not result['physical_gauge_fixing_selected']
    assert not result['complete_interacting_correction']


def test_shared_nu_surface_family_is_exact_action_polynomial_at_nonzero_scalar(application):
    reference,rep,zero,_=application
    state=zero.copy();state[-4:]=[.003,-.001,.002,.007]
    base=coupled_sector_application(state,rep,reference)
    nu2=.031;gamma=.017
    member=coupled_sector_application(state,rep,reference,nu_squared_action=nu2,surface_gamma=gamma)
    factors={'intrinsic_H_potential_per_nu2':nu2,
       'H_zero_potential_per_lambda_nu4':rep['scalar_matching']['lambda_H']*nu2**2,
       'surface_per_gamma':gamma}
    for key in ('value','residual','hessian'):
        expected=base[key]+sum(factor*base['sectors'][name][key] for name,factor in factors.items())
        np.testing.assert_allclose(member[key],expected,rtol=3e-14,atol=2e-9)
    assert np.linalg.norm(base['sectors']['intrinsic_H_potential_per_nu2']['residual'][-4:])>0
    assert not member['stationary_E1_claim']


def test_repeated_correction_reaches_finite_tolerance_or_reports_actual_stall(application):
    reference,rep,zero,_=application
    result=iterate_finite_newton(zero,rep,reference,max_iterations=5)
    assert len(result['history'])>=2
    assert result['fixed_scaled_final_residual']<result['fixed_scaled_initial_residual']/1e4
    assert result['status'] in ('FINITE_RESIDUAL_TOLERANCE','DAMPING_STALL','ITERATION_LIMIT')
    assert not result['physical_stationarity']


def test_off_shell_full5_Ward_on_actual_updated_connection_and_saved_Q_sources(application):
    reference,rep,zero,_=application
    initial=corrected_Q_hessian_and_Ward(zero,rep,reference)
    state=zero.copy();state[[62,66,70,75]]=[.004,-.003,.002,.001]
    changed=corrected_Q_hessian_and_Ward(state,rep,reference)
    assert changed['Ward_relative_defect']<2e-13
    assert np.linalg.norm(changed['Euler_commutator'])>0
    assert changed['curvature_contacts_retained']
    assert np.linalg.norm(changed['Ward_curvature_contact'])>0
    assert np.linalg.norm(changed['Q_hessian']-initial['Q_hessian'])>0
    assert not changed['native_heat_evaluated']
    assert not changed['Gauss_columns_eliminated']


def test_independent_wall_lift_consumes_Higgs_current_without_inventing_child_boundary():
    reference=retained_state(ROOT)
    rep=correction_representation(time_points=2,radial_points=12,radial_order=1,cap_points=12,include_wall_lift=True)
    state=np.zeros(rep['count']);state[-4:]=[.001,-.003,.002,.007]
    a=coupled_sector_application(state,rep,reference,nu_squared_action=.031)
    assert a['parent_wall_rows'].shape==(20,)
    assert np.linalg.norm(a['scalar_gauge_block'])>0
    assert 'partial parent action' in a['parent_wall_rows_scope']
    faces=finite_action_contacts(state,rep,reference)
    assert faces['wall_conormal'].shape==(2,20)
    assert [row['orientation'] for row in faces['temporal']]==[-1,1]
    assert not faces['physical_boundary_selected']
    endpoint=finite_common_iterate_at_time(0,state,rep,reference)
    np.testing.assert_array_equal(endpoint['q'],reference[0])
    np.testing.assert_array_equal(endpoint['qdot'],reference[1])
    assert 'not appended' in faces['endpoint_contact_role']


def test_scalar_mean_unknowns_preserve_their_trace_cotangents_and_exact_basis_inclusion(application):
    reference,old,zero,_=application
    new=correction_representation(time_points=2,radial_points=12,radial_order=2,cap_points=12,
                                 include_wall_lift=True,include_scalar_mean=True)
    state=zero.copy();state[70]=.003;state[-4:]=[.001,-.002,.003,.004]
    extended=prolong_finite_coefficients(state,old,new)
    a=finite_common_iterate_at_time(-.00043,state,old,reference,rho=np.array([.3,.7,1.2]))
    b=finite_common_iterate_at_time(-.00043,extended,new,reference,rho=np.array([.3,.7,1.2]))
    for key in ('gauge','gauge_tau','gauge_rho','gauge_angular'):
        np.testing.assert_array_equal(a['fields'][key],b['fields'][key])
    mean=np.array([.02,.03,-.01,.04]);extended[-4:]=mean
    faces=finite_action_contacts(extended,new,reference)
    for row in faces['temporal']:
        np.testing.assert_array_equal(row['H_real_trace'],mean)
    application=coupled_sector_application(extended,new,reference,nu_squared_action=4.)
    assert application['scalar_unknown_count']==8
    assert np.linalg.norm(application['scalar_rows'])>0
    assert np.linalg.norm(application['scalar_gauge_block'])>0
    assert not application['stationary_E1_claim']
