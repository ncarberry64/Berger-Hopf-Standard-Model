"""Actual saved-field finite-cell applications, not physical Pauli tests."""
import json
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from bhsm.interface.muon_primal_cell_native_heat import actual_cell_heat_polynomial,actual_cell_even_y_target,actual_cell_eight_q_heat_core,actual_cell_eight_q_cutoff_application
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def actual():
    p=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/enriched_phase_incoming_1steps_run_1'
    md=json.loads((p/'result.json').read_text());rep=correction_representation(radial_points=48,cap_points=48,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    with np.load(p/'application.npz',allow_pickle=False) as a:
        raw=a['stage_midpoint_raw'][0].copy();rep['wall_trace_map']=a['wall_trace_map'].copy()
    rep['gauge_labels']=md['gauge_labels']
    return raw,rep,abs(md['span'])


def test_actual_positive_tent_pencil_matches_independent_covariant_form_quadrature(actual):
    raw,rep,L=actual;p=actual_cell_heat_polynomial(raw,rep,length=L);op=p['operator'];ids=np.array([0,1,6,7,12,13])
    x,w=np.polynomial.legendre.leggauss(12);x=(x+1)/2;w=w*L/2
    B=(op['W']+op['Omega_tau'])[np.ix_(ids,ids)];K=np.zeros((6,6),complex);M=0.
    for u,wt in zip(x,w):
        b=2*u if u<=.5 else 2*(1-u);bd=2/L if u<.5 else -2/L
        A=bd/op['N']*np.eye(6)+b*B
        K+=wt*op['proper_time_Haar_measure']*(A.conj().T@A);M+=wt*op['proper_time_Haar_measure']*b*b
    # Split Gauss quadrature at the tent kink for its exact polynomial form.
    K*=0;M=0.
    for lo,hi in ((0.,.5),(.5,1.)):
        for gx,gw in zip(*np.polynomial.legendre.leggauss(4)):
            u=lo+(gx+1)*(hi-lo)/2;wt=gw*(hi-lo)*L/2;b=2*u if u<.5 else 2*(1-u);bd=2/L if u<.5 else -2/L
            A=bd/op['N']*np.eye(6)+b*B;K+=wt*op['proper_time_Haar_measure']*A.conj().T@A;M+=wt*op['proper_time_Haar_measure']*b*b
    Y=np.diag(__import__('bhsm.interface.muon_native_dirac_hamiltonian',fromlist=['lepton_current_hilbert_representation']).lepton_current_hilbert_representation()['family_Y']).real[0]
    np.testing.assert_allclose(K/M,p['P0']+Y*p['P1']+Y*Y*p['P2'],rtol=4e-16,atol=8e-5)
    assert np.linalg.eigvalsh(K/M)[0]>0
    assert p['normalized_Gram_contact_included']


@pytest.mark.parametrize('index',[37,98,99,160,260,263])
def test_actual_cell_polynomial_first_jets_match_primal_field_finite_differences(actual,index):
    raw,rep,L=actual;p=actual_cell_heat_polynomial(raw,rep,length=L);step=1e-5;d=np.eye(268)[index]
    plus=actual_cell_heat_polynomial(raw+step*d,rep,length=L);minus=actual_cell_heat_polynomial(raw-step*d,rep,length=L)
    for base,jet in (('zero_Y_spatial_square','zero_Y_spatial_square_raw_first_jet'),('P1','P1_raw_first_jet'),('P2','P2_raw_first_jet')):
        fd=(plus[base]-minus[base])/(2*step)
        # Isolate the spatial square so the huge temporal diagonal cannot erase a small derivative.
        scale=max(1.,np.linalg.norm(p[jet][index]));assert np.linalg.norm(fd-p[jet][index])/scale<3e-5


def test_even_y_raw_target_matches_direct_coefficient_derivative_without_family_subtraction(actual):
    raw,rep,L=actual;p=actual_cell_heat_polynomial(raw,rep,length=L);c=1/min(np.linalg.eigvalsh(p['P0']))
    target=actual_cell_even_y_target(p,c);step=1e-5;d=np.eye(268)[261]
    plus=actual_cell_even_y_target(actual_cell_heat_polynomial(raw+step*d,rep,length=L),c)
    minus=actual_cell_even_y_target(actual_cell_heat_polynomial(raw-step*d,rep,length=L),c)
    fd=(plus['paired_middle_minus_light_Y2_value']-minus['paired_middle_minus_light_Y2_value'])/(2*step)
    assert fd==pytest.approx(target['paired_middle_minus_light_raw_cotangent'][261],rel=5e-7,abs=2e-24)
    assert target['exact_sign_parity_retained']
    assert target['physical_cutoff_or_completed_Pauli_selected'] is False


def test_actual_source_heat_retains_complete_complement_and_both_orders(actual):
    raw,rep,L=actual;core=actual_cell_eight_q_heat_core(raw,rep,length=L,repository=ROOT)
    c=1/min(core['families']['1']['n0_eigenvalues']);out=actual_cell_eight_q_cutoff_application(core,c)
    for family in core['families'].values():
        assert family['intermediate_shells']['1']['all_intermediate_mode_count']==24
        assert family['intermediate_shells']['3']['all_intermediate_mode_count']==96
    for value in out['families'].values():
        np.testing.assert_array_equal(value['opposite_order_two_insertion'],value['ordered_two_insertion'].T)
        np.testing.assert_allclose(value['available_fixed_field_source_pair'],value['source_square_contact']+value['ordered_two_insertion']+value['opposite_order_two_insertion'],atol=1e-30)
    assert out['paired_middle_minus_light'] is None


def test_unknown_cell_or_cutoff_cannot_be_assigned_a_unit_value(actual):
    raw,rep,L=actual
    with pytest.raises(ValueError,match='explicit real'):actual_cell_heat_polynomial(raw,rep,length=None)
    with pytest.raises(ValueError,match='positive finite'):actual_cell_even_y_target(actual_cell_heat_polynomial(raw,rep,length=L),0.)
