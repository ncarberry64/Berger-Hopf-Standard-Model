from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_native_two_time_green import (
 load_executed_magnetic_green_form,retarded_boundary_green_application,
 apply_reached_canonical_source,continue_canonical_green_across_birth)
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def incoming():
    return load_executed_magnetic_green_form('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)

def test_two_time_support_jump_and_gauss_contact(incoming):
    T=incoming['final_time'];s=T/2
    a=retarded_boundary_green_application(incoming,s,np.array([0.,s,T]))
    assert not np.any(a['phase_kernel'][0])
    assert np.array_equal(a['phase_kernel'][1],a['canonical_jump_columns'])
    assert np.linalg.norm(a['instantaneous_Gauss_contact'])>0
    assert a['phase_kernel'].shape==(3,800,3)
    assert not a['quantum_Feynman_or_positive_native_covariance_claimed']
    outgoing=load_executed_magnetic_green_form('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/outgoing_run_1',repository=ROOT)
    b=continue_canonical_green_across_birth(a,outgoing,np.array([0.,T]))
    assert b['canonical_birth_jump_norm']==0
    assert not b['outgoing_velocity_or_Gauss_copied_from_incoming']

def test_two_channel_equation_reproduces_actual_full488_source_solution(incoming):
    T=incoming['final_time'];times=incoming['inputs']['source']['times']
    a=apply_reached_canonical_source(incoming,lambda t:magnetic_turn_on_profile(t,T/4),observation_times=times)
    idx=[int(np.flatnonzero(incoming['inputs']['times']==t)[0]) for t in times]
    saved=incoming['inputs']['phase']['state'][idx,:,:3]
    assert np.linalg.norm(a['phase']-saved)/(1+np.linalg.norm(saved))<3e-10

def test_outgoing_zero_initial_cannot_replace_actual_birth():
    f=load_executed_magnetic_green_form('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/outgoing_run_1',repository=ROOT)
    with pytest.raises(ValueError,match='canonical birth'):
        apply_reached_canonical_source(f,lambda t:(1.,0.,0.))
