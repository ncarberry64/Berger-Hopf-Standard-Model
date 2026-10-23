"""Graded accounting and actual fixed-Y overlap contraction identities."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_attached_native_source_pair import combine_executed_fermion_pair
from bhsm.interface.muon_attached_source_mean_load import load_attached_reached_mean_inputs
from bhsm.interface.muon_current_source_motion_mean_load import enriched_reached_first_fields
from bhsm.interface.muon_primal_cell_reached_source_heat import actual_reached_cell_vertices
from bhsm.interface.muon_native_mean_core_heat_target import _unit_lepton_mass6
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation

ROOT=Path(__file__).resolve().parents[1]


def test_statistics_applied_once_to_both_orders_and_mean_without_conjugation():
    # Accounting control only; these are not supplied physical source values.
    a=np.arange(64).reshape(8,8).astype(complex);a[0,1]+=2j
    direct=dict(source_square_contact=-a,ordered_two_insertion=2*a,opposite_order_two_insertion=2*a.T)
    mean=3*a
    r=combine_executed_fermion_pair(direct,mean)
    np.testing.assert_array_equal(r['ungraded_source_pair'],4*a+2*a.T)
    np.testing.assert_array_equal(r['graded_source_pair'],2*a+a.T)
    assert r['fermion_statistics_factor']==.5
    assert not r['charge_conjugate_doubling_applied']


def test_missing_nonfinite_or_incomplete_pair_is_not_a_zero():
    direct={k:np.zeros((8,8)) for k in ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion')}
    for mean in (np.zeros((7,8)),np.full((8,8),np.nan)):
        with pytest.raises(ValueError):combine_executed_fermion_pair(direct,mean)


@pytest.fixture(scope='module')
def vertices():
    i=load_attached_reached_mean_inputs('artifacts/muon_attached_reached_action_20261011/incoming_run_1',repository=ROOT)
    f=enriched_reached_first_fields(i,i['times'][len(i['times'])//2])
    return actual_reached_cell_vertices(f,i['representation'])


def test_actual_first_local_mass_contact_has_owned_spin_multiplicity(vertices):
    H=vertices['complex_H_response']
    X=np.array([_unit_lepton_mass6(h) for h in H.reshape(160,2)]).reshape(8,20,6,6)
    gram=np.einsum('Ahij,Bhij->AB',X.conj(),X)
    direct=gram+gram.T
    expected=8*np.einsum('Aha,Bha->AB',H.conj(),H).real
    assert np.linalg.norm(expected)>0
    # Off-diagonal contractions cancel twelve or more orders below the
    # diagonal.  Compare this independent identity at the full pairing norm.
    assert np.linalg.norm(direct-expected)<=2e-15*np.linalg.norm(expected)


def test_Y_independent_operator_is_identical_in_actual_middle_and_light_copies(vertices):
    op=vertices['operator'];W=op['W'].copy();W[:12,12:]=0;W[12:,:12]=0
    ids1=np.array([2,3,8,9,14,15]);ids2=np.array([4,5,10,11,16,17])
    np.testing.assert_array_equal(W[np.ix_(ids1,ids1)],W[np.ix_(ids2,ids2)])
    np.testing.assert_array_equal(op['Omega_tau'][np.ix_(ids1,ids1)],op['Omega_tau'][np.ix_(ids2,ids2)])
    # The Yukawa difference is retained, rather than extending this identity
    # to the mass-dependent full heat or external Pauli kinematics.
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real
    assert Y[1]**2!=Y[2]**2
