"""Actual enriched source checks and exact charged-coordinate algebra."""
import json
import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_birth_trace_enriched_phase import enriched_representation_from_values
from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from bhsm.interface.muon_trace_enriched_charged_current_response import (
    enriched_charged_current_action_source,enriched_central_profiles,
    enriched_midpoint_source_rows,charged_kernel_coordinates,
)
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


@pytest.fixture(scope='module')
def actual():
    base=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    folder=base/'paired_field_endpoint_enriched_run_1'
    receipt=json.loads((folder/'result.json').read_bytes())
    with np.load(folder/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
    rep=enriched_representation_from_values(receipt,arrays)
    with np.load(base/'enriched_phase_outgoing_1steps_run_1/application.npz',allow_pickle=False) as a:raw=a['stage_midpoint_raw'][0].copy()
    return raw,rep,enriched_charged_current_action_source(raw,rep)


@pytest.mark.parametrize('index',[0,74,98,100,140,160,260])
def test_same_actual_coordinate_time_action_source(actual,index):
    raw,rep,source=actual;h=2e-6;p=raw.copy();m=raw.copy();p[index]+=h;m[index]-=h
    plus=primal_trace_enriched_lepton_operator(p,rep);minus=primal_trace_enriched_lepton_operator(m,rep)
    derivative=(-plus['N']*plus['H_can']+minus['N']*minus['H_can'])/(2*h)
    expected=np.einsum('aij,ji->a',source['current_matrices'],derivative).real
    np.testing.assert_allclose(source['raw_source'][index],expected,atol=2e-9,rtol=5e-6)


def test_two_analytic_profiles_survive_nonpolynomial_enrichment(actual):
    _,rep,_=actual;p=enriched_central_profiles(rep)
    np.testing.assert_array_equal(p['theta_coefficients'][2],0)
    np.testing.assert_array_equal(p['radial_derivative_coefficients'][2],0)
    rho=np.array([.18,.54,1.07,1.44]);h=1e-6
    B,_=trace_enriched_radial_basis(rep,rho)
    P,_=trace_enriched_radial_basis(rep,rho+h);M,_=trace_enriched_radial_basis(rep,rho-h)
    np.testing.assert_allclose((P@p['theta_coefficients']-M@p['theta_coefficients'])/(2*h),
        B@p['radial_derivative_coefficients'],atol=3e-10,rtol=1e-9)
    assert p['profile_reconstruction_absolute_error']<2e-12


def test_all358_midpoint_rows_have_literal_source_signs_CONTROL_ONLY():
    B=np.arange(252*2,dtype=float).reshape(252,2);h=-.25;r=enriched_midpoint_source_rows(B,h)
    assert r.shape==(358,2)
    np.testing.assert_array_equal(r[:106],0)
    np.testing.assert_array_equal(r[106:212],.25*B[:106])
    np.testing.assert_array_equal(r[212:318],B[106:212])
    np.testing.assert_array_equal(r[318:],B[212:])
    with pytest.raises(ValueError):enriched_midpoint_source_rows(B+1j,1.)
    with pytest.raises(ValueError):enriched_midpoint_source_rows(B,0.)


def test_charged_recombination_is_bilinear_not_adjoint_guess_CONTROL_ONLY():
    K=np.arange(64,dtype=float).reshape(8,8);a=charged_kernel_coordinates(K)
    P=np.vstack((np.eye(4),1j*np.eye(4)))/np.sqrt(2)
    np.testing.assert_allclose(a['Jminus_Jplus'],P.conj().T@K@P,atol=2e-14,rtol=0)
    np.testing.assert_allclose(a['Jplus_Jplus'],P.T@K@P,atol=2e-14,rtol=0)
    eta=np.diag([1,-1,-1,-1]);c=a['metric_tensor_coefficient_real']+1j*a['metric_tensor_coefficient_imag']
    np.testing.assert_allclose(a['metric_tensor_remainder']+c*eta,a['Jminus_Jplus'],atol=0,rtol=0)
    assert abs(np.sum(eta*a['metric_tensor_remainder']))<1e-14
    assert not a['physical_lorentz_current_or_LSZ_projection_selected']
    assert a['physical_c_F'] is None


def test_local_metric_tensor_condition_and_anisotropic_counterexample_CONTROL_ONLY():
    eta=np.diag([1.,-1.,-1.,-1.]);K=np.zeros((8,8));K[:4,:4]=3*eta;K[4:,4:]=3*eta
    good=charged_kernel_coordinates(K)
    assert good['metric_tensor_coefficient_real']==3
    assert good['metric_tensor_remainder_norm']==0
    assert good['equal_charge_kernel_norm']==0
    K[1,1]+=.5;bad=charged_kernel_coordinates(K)
    assert bad['metric_tensor_remainder_norm']>0
    assert bad['equal_charge_kernel_norm']>0


def test_enriched_actual_allfamily_current_and_scoped_zero_rows(actual):
    raw,rep,a=actual;b=enriched_charged_current_action_source(raw,rep,family=2)
    np.testing.assert_array_equal(a['raw_source'],b['raw_source'])
    np.testing.assert_array_equal(a['raw_source'][180:],0)
    assert np.linalg.norm(raw[100:180])>0
    assert a['master_source'].shape==(252,8)
    assert not a['physical_external_state_selected']
    assert not a['constant_angular_Haar_volume_reapplied']
