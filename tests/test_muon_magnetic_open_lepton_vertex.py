"""Literal action/normalization checks; hypothetical fields are CONTROL_ONLY."""
import numpy as np
import pytest
from bhsm.interface.muon_magnetic_open_lepton_vertex import (
    canonical_open_field_vertices,charged_dirac_injection,
    matched_symbol_magnetic_spin_reduction,reached_magnetic_open_vertex,
    magnetic_open_fields_at_node,
)
from bhsm.interface.muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian


def test_charged_injection_matches_actual_general_H_mass_and_charge():
    H=np.array([.3+.4j,-.7+.1j]) # CONTROL_ONLY general H algebra.
    a=charged_dirac_injection(H);J=a['charged'];K=a['neutral']
    rep=retained_higgs_spin_charge_representation()
    m=rep['family_yukawa'][1,1]*np.linalg.norm(H)
    mass=fixed_y_higgs_hamiltonian(H[None])[0]
    np.testing.assert_allclose(J.conj().T@mass@J,m*rep['gamma_Dirac'][0],atol=2e-18)
    np.testing.assert_allclose(K.conj().T@mass@J,0,atol=2e-18)
    assert a['current_Gram_defect']<1e-15 and a['charge_defect']<1e-15
    assert not a['interacting_LSZ_selected']


def test_scalar_vertices_retain_real_linear_reverse_LR_placement():
    v=canonical_open_field_vertices(2.,.7)
    h=np.array([.4,-.3,.6,.2]) # CONTROL_ONLY complex scalar direction.
    expected=fixed_y_higgs_hamiltonian((h[:2]+1j*h[2:])[None])[0]
    np.testing.assert_allclose(np.einsum('a,aij->ij',h,v['scalar']),expected,atol=1e-20)
    assert np.max(abs(v['scalar']-v['scalar'].conj().swapaxes(-1,-2)))==0
    assert not np.any(v['gauge'][1])
    assert not v['HS_auxiliary_identified_with_intrinsic_H']


def test_covariant_uniform_B_minimal_spin_normalization_and_sign():
    # CONTROL_ONLY free matched pole, conventional A=B cross X/2.
    rep=retained_higgs_spin_charge_representation();gamma=rep['gamma_Dirac']
    alpha=np.array([gamma[0]@g for g in gamma[1:]])
    from bhsm.interface.muon_matched_mechanical_source import epsilon
    e,m=.3,.11
    gradient=.5*e*np.einsum('ijk,iuv->kjuv',epsilon(),alpha)*(-1)
    r=matched_symbol_magnetic_spin_reduction(np.zeros((3,4,4)),gradient,
        matched_mass_action=m,electric_charge=e)
    np.testing.assert_allclose(r['relative_to_minimal_Dirac_spin_coefficient'],np.eye(3),atol=3e-15)
    assert not r['quantum_self_energy_or_native_Pauli_completed']


def test_full_actual_point_vertex_equals_same_action_raw_derivative():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs,magnetic_reached_first_fields
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_basis_values,real_scalar_basis_transform,real_scalar_basis_labels
    from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
    inputs=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    t=inputs['source']['times'][2];fields=magnetic_reached_first_fields(inputs,t)
    angular=retained_full_q_angular_space(ROOT);rep=inputs['representation']
    result=reached_magnetic_open_vertex(fields,rep,angular,electric_charge=inputs['electric_charge'])
    labels=real_scalar_basis_labels(3);odd=[i for i,l in enumerate(labels) if l[0] in (1,3)]
    value=(scalar_basis_values(np.eye(2,dtype=complex)[None],3)@real_scalar_basis_transform(3))[0,odd].real
    a=np.einsum('h,Afch->fcA',value,fields['first_wall_gauge'])
    h=np.einsum('h,Ach->cA',value,fields['first_H'])
    raw=fields['raw_fields'];direction=np.zeros((268,8))
    direction[100:180]=np.linalg.lstsq(rep['wall_trace_map'].reshape(20,80),a.reshape(20,8),rcond=None)[0]
    direction[-8:-4]=h
    exact=np.einsum('rA,ruv->Auv',direction,result['operator']['H_can_raw_first_jet'])
    np.testing.assert_allclose(result['canonical_point_vertices'],exact,rtol=2e-12,atol=3e-24)
    # CONTROL_ONLY resolvable variation checks the literal owner rather
    # than attempting subtraction of its actual tiny solved H response.
    d=np.zeros(268);d[[101,117,173,-8,-5]]=[.2,-.07,.09,.1,-.08]
    control_a=np.einsum('fcj,j->fc',rep['wall_trace_map'],d[100:180])
    control=np.einsum('fcuv,fc->uv',result['open_field_vertices']['gauge'],control_a)
    control+=np.einsum('cuv,c->uv',result['open_field_vertices']['scalar'],d[-8:-4])
    step=2e-5
    fd=(primal_trace_enriched_lepton_operator(raw+step*d,rep)['H_can']-primal_trace_enriched_lepton_operator(raw-step*d,rep)['H_can'])/(2*step)
    np.testing.assert_allclose(fd,control,rtol=2e-8,atol=4e-12)
    assert np.linalg.norm(exact)>0
    assert np.linalg.norm(result['neutral_background_leakage'])>0
    assert fields['profile']==1
    assert not result['native_loop_P_A_ghost_HS_contracted']


def test_hermitian_and_missing_mass_guards():
    v=np.zeros((3,4,4),complex);d=np.zeros((3,3,4,4),complex)
    with pytest.raises(ValueError):matched_symbol_magnetic_spin_reduction(v,d,matched_mass_action=0,electric_charge=.3)
    v[0,0,1]=1j
    with pytest.raises(ValueError,match='Hermitian'):matched_symbol_magnetic_spin_reduction(v,d,matched_mass_action=.1,electric_charge=.3)


def test_saved_birth_trace_rounding_preserved_and_real_mismatch_rejected():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    inputs=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    t=inputs['times'][-1];fields=magnetic_open_fields_at_node(inputs,t)
    np.testing.assert_array_equal(fields['first_wall_gauge'].reshape(8,400).T,inputs['contacts']['source_trace'][-1])
    assert fields['source_value_reconstruction_discrepancy']>0
    assert not fields['saved_source_values_replaced']
    inputs['contacts']['source_trace'][-1,0,0]+=1e-7
    with pytest.raises(ValueError,match='beyond spline'):magnetic_open_fields_at_node(inputs,t)
