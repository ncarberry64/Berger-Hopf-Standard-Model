"""Independent retained-rate binding and only affected array checks."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pytest
from bhsm.interface.muon_parent_source_contact import retained_source_cut_rate,cut_metric_dirac_actions
from bhsm.interface.aether_forward_boundary_radius import proper_time_log_radius_rate

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference'
OLD=ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_metric_dirac_actions.npz'


def test_rate_binding_against_actual_retained_producer_and_certificate():
    rate=retained_source_cut_rate(ROOT)
    for name in ('prefix_state','prefix_certificate'):
        ref=rate[name]
        assert hashlib.sha256((ROOT/ref['repository_path']).read_bytes()).hexdigest()==ref['sha256']
    with np.load(ROOT/rate['prefix_state']['repository_path']) as p:y=p[rate['state_key']]
    H=proper_time_log_radius_rate(12,y[:37],y[37:74],y[74:])
    cert=json.loads((ROOT/rate['prefix_certificate']['repository_path']).read_text())
    assert H==rate['value']==0.08877816767234145
    assert rate['interval']==cert['domain']['D_tau_log_R4_interval']
    assert rate['interval'][0]<=H<=rate['interval'][1]
    assert H!=rate['excluded_affine_logR_slope']
    with np.load(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz') as p:
        assert p['boundary_H'][0]==0
    # Future production cannot silently fall back to the stale cache.
    with pytest.raises(TypeError):cut_metric_dirac_actions(None,None,None)


def test_additive_repair_and_unaffected_body_are_preserved():
    rate=retained_source_cut_rate(ROOT)
    with np.load(OLD) as old,np.load(ART/'parent_source_rate_corrected.npz') as new,np.load(ART/'source_rate_old_new_delta.npz') as d:
        changed={'source_kernel_time_log_derivative'}
        for n in (1,3):
            key=f'D5_on_same_source_image_b_coefficient_n{n}'
            tau=f'D5_on_same_source_image_b_tau_coefficient_n{n}'
            change=-rate['value']/2*old[tau]
            np.testing.assert_array_equal(d[f'C_b_delta_n{n}'],change)
            np.testing.assert_array_equal(new[key],old[key]+change)
            changed.add(key)
        np.testing.assert_array_equal(new['source_kernel_time_log_derivative'],old['source_kernel_time_log_derivative']-rate['value']/2)
        for key in old.files:
            if key not in changed:np.testing.assert_array_equal(new[key],old[key])


def test_inherited_H_error_is_separate_and_encloses_fixed_input_variations():
    result=json.loads((ART/'result.json').read_text())
    rate=result['source_rate']
    assert 'unresolved' in result['interpolation_body_error']
    with np.load(ART/'parent_source_rate_corrected.npz') as p:
        for n in (1,3):
            tau=p[f'D5_on_same_source_image_b_tau_coefficient_n{n}']
            bound=result['inherited_H_uncertainty'][str(n)]['H_only_bound_upper_float']
            for endpoint in rate['interval']:
                perturbation=(float(endpoint)-rate['value'])/2*tau
                assert np.linalg.norm(perturbation)<=bound
