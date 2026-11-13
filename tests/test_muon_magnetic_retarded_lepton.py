from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_magnetic_retarded_lepton import reached_lorentz_magnetic_vertices,retarded_magnetic_lepton_application
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def actual():
    i=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    a=retained_full_q_angular_space(ROOT)
    return i,a,reached_lorentz_magnetic_vertices(i)

def test_total_gauge_and_H_lorentz_vertices_are_hermitian(actual):
    _,_,r=actual
    assert r['Hermitian_vertex_defect']<1e-15
    assert np.linalg.norm(r['spatial_vertex'])>0
    assert np.linalg.norm(r['fixed_Y_H_vertex'])>0
    assert np.array_equal(r['magnetic_Hcan_vertex'],r['spatial_vertex']+r['temporal_vertex']+r['fixed_Y_H_vertex'])

def test_actual_retarded_open_source_has_full_images_and_current_unitarity(actual):
    i,a,_=actual;r=retarded_magnetic_lepton_application(i,a)
    assert r['initial_transport_identity_defect']==0
    assert r['unitary_transport_defect']<2e-12
    assert r['magnetic_open_fermion_response']['1'].shape==(5,3,72,18)
    assert r['magnetic_open_fermion_response']['3'].shape==(5,3,288,18)
    assert np.linalg.norm(r['magnetic_open_fermion_response']['1'][-1])>0
    assert not np.any(r['magnetic_open_fermion_response']['1'][0])
    assert not r['quantum_Feynman_photon_or_Keldysh_kernel_evaluated']
    assert not r['external_pole_LSZ_or_normalized_Pauli_completed']

def test_causal_observation_guard(actual):
    i,a,_=actual
    with pytest.raises(ValueError,match='causal'):
        retarded_magnetic_lepton_application(i,a,source_time=5e-6,observation_times=np.array([0.,1e-5]))
