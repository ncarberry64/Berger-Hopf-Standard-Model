import copy
import numpy as np
import pytest
from scipy.linalg import solve
from bhsm.interface.muon_corrected_charged_current_cell import corrected_charged_current_action_source
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_lepton_sample


def test_corrected_child_source_matches_independent_evolution_derivative():
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    step=phase['receipt']['span'];time=step/2
    source=corrected_charged_current_action_source(phase,time,step)
    direction=phase['coordinates']['lift'][:,0]
    def evolved(delta):
        changed=dict(phase,arrays=dict(phase['arrays']))
        changed['arrays'][phase['stage_key']]=phase['arrays'][phase['stage_key']].copy()
        changed['arrays'][phase['stage_key']][0]+=delta*direction
        op=profile_preserving_lepton_sample(changed,time)['operator']
        K=op['N']*op['H_can'];I=np.eye(18)
        return solve(I+1j*step*K/2,I-1j*step*K/2)
    epsilon=1e-4
    derivative=(evolved(epsilon)-evolved(-epsilon))/(2*epsilon)
    literal_action_operator=-1j*source['amputation']['propagator'].conj().T@derivative/step
    expected=np.einsum('aij,ji->a',source['current_matrices'],literal_action_operator)
    np.testing.assert_allclose(direction@source['raw_source'],expected.real,rtol=2e-6,atol=3e-9)
    assert source['inherited_wall_image_count']==1
    assert not source['canonical_angular_volume_reapplied']


def test_actual_source_keeps_both_families_and_rejects_old_clock_direction():
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    time=phase['receipt']['span']/2;step=abs(phase['receipt']['span'])
    middle=corrected_charged_current_action_source(phase,time,step,family=1)
    light=corrected_charged_current_action_source(phase,time,step,family=2)
    assert middle['master_source'].shape==light['master_source'].shape==(252,8)
    assert np.linalg.norm(middle['raw_source'][-8:-4])>0
    assert np.linalg.norm(light['raw_source'][-8:-4])>0
    assert middle['amputation']['unit_current_propagator_defect']<1e-13
    with pytest.raises(ValueError):
        corrected_charged_current_action_source(phase,time,-step)
