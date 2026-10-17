"""Exact on-shell identity and actual18-component charged-current sources."""
import json
import numpy as np
import pytest
import sympy as s
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_birth_trace_enriched_phase import enriched_representation_from_values
from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from bhsm.interface.muon_charged_current_cell_amputation import (
    variational_cayley_amputation,amputated_charged_current_action_source,
)


def test_exact_variational_identity_and_action_sign_CONTROL_ONLY():
    # Exact independent complex Hermitian algebra, not a physical state.
    z=s.symbols('z',real=True);h=s.Rational(-2,7)
    K=s.Matrix([[1,z+s.I],[z-s.I,3]])
    I=s.eye(2);U=(I+s.I*h*K/2).inv()*(I-s.I*h*K/2)
    V=(I+U)/2
    assert s.simplify(U.conjugate().T*U-I)==s.zeros(2)
    left=s.I*U.conjugate().T*s.diff(U,z)
    right=h*V.conjugate().T*s.diff(K,z)*V
    assert s.simplify(left-right)==s.zeros(2)
    assert s.simplify(-left/h+V.conjugate().T*s.diff(K,z)*V)==s.zeros(2)


def test_entire_finite_hermitian_tangent_identity_CONTROL_ONLY():
    K=np.array([[1,1j],[-1j,2]],complex)
    D=np.array([np.eye(2),[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    a=variational_cayley_amputation(K,D,-.13)
    assert a['unit_current_propagator_defect']<1e-14
    assert a['exact_identity_evaluation_defect']<1e-14
    assert not a['selected_external_spinor_or_CAR_state']
    assert not a['physical_LSZ_residue_or_pole_selected']
    for j in range(4):
        epsilon=1e-6
        p=variational_cayley_amputation(K+epsilon*D[j],D,-.13)['propagator']
        m=variational_cayley_amputation(K-epsilon*D[j],D,-.13)['propagator']
        np.testing.assert_allclose((p-m)/(2*epsilon),a['propagator_first_jet'][j],atol=2e-10,rtol=2e-9)
    with pytest.raises(ValueError,match='Hermitian'):variational_cayley_amputation(K+np.array([[0,1],[0,0]]),D,.1)
    with pytest.raises(ValueError):variational_cayley_amputation(K,D,0.)


@pytest.fixture(scope='module')
def actual():
    b=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010';endpoint=b/'paired_field_endpoint_enriched_run_1'
    receipt=json.loads((endpoint/'result.json').read_bytes())
    with np.load(endpoint/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
    rep=enriched_representation_from_values(receipt,arrays)
    with np.load(b/'enriched_phase_outgoing_1steps_run_1/application.npz',allow_pickle=False) as a:raw=a['stage_midpoint_raw'][0].copy()
    h=1e-5
    return raw,rep,h,amputated_charged_current_action_source(raw,rep,h)


@pytest.mark.parametrize('index',[0,37,74,98,100,140,160,260,261])
def test_actual_amputated_source_matches_derivative_of_the_same_propagator(actual,index):
    raw,rep,h,a=actual;epsilon=2e-6;p=raw.copy();m=raw.copy();p[index]+=epsilon;m[index]-=epsilon
    up=amputated_charged_current_action_source(p,rep,h)['amputation']['propagator']
    um=amputated_charged_current_action_source(m,rep,h)['amputation']['propagator']
    # The on-shell source equals -i U†D_rU/h. Differentiate U directly,
    # rather than finite-differencing the implemented source expression.
    derivative=(up-um)/(2*epsilon)
    operator=-1j*a['amputation']['propagator'].conj().T@derivative/h
    expected=np.einsum('aij,ji->a',a['current_matrices'],operator).real
    np.testing.assert_allclose(a['raw_source'][index],expected,atol=2e-9,rtol=5e-6)


def test_fixed_Y_H_source_is_reached_without_fitting_Y_or_selecting_a_spinor(actual):
    raw,rep,h,a=actual;e=amputated_charged_current_action_source(raw,rep,h,family=2)
    assert a['reached_fixed_Y_H_source_norm']>1e-13
    assert np.linalg.norm(a['raw_source']-e['raw_source'])>1e-13
    np.testing.assert_array_equal(a['raw_source'][180:260],0)
    np.testing.assert_array_equal(a['raw_source'][264:],0)
    assert a['master_source'].shape==(252,8)
    assert a['amputation']['unit_current_propagator_defect']<1e-14
    assert a['amputation']['exact_identity_evaluation_defect']<1e-17
    assert not a['physical_LSZ_pole_or_local_Fermi_coefficient_assigned']


def test_coordinate_N_variation_is_counted_once(actual):
    raw,rep,_,a=actual
    op=primal_trace_enriched_lepton_operator(raw,rep)
    V=2*np.pi**2
    expected=op['N']*op['H_can_raw_first_jet']+op['proper_time_Haar_measure_first_jet'][:,None,None]*op['H_can']/V
    np.testing.assert_allclose(a['canonical_coordinate_time_operator_first_jet'],expected,atol=2e-16,rtol=4e-16)
    assert not a['constant_angular_Haar_volume_reapplied']
