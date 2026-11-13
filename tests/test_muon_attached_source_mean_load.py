"""Actual full220 consumer binding; no new chosen physical fields."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_attached_source_mean_load import load_attached_reached_mean_inputs
from bhsm.interface.muon_current_source_motion_mean_load import enriched_reached_first_fields
from bhsm.interface.muon_parent_retarded_hypercharge import compact_trace_pulse
from scipy.interpolate import CubicSpline

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def actual():
    return load_attached_reached_mean_inputs(
        'artifacts/muon_attached_reached_action_20261011/incoming_run_1',repository=ROOT)


def test_binding_consumes_actual_full220_scalar_and_Gauss_fields(actual):
    assert actual['consumed_full_attachment']
    assert 'attached_phase_incoming_' in actual['actual_attached_phase_path'].name
    t=actual['times'][len(actual['times'])//2]
    fields=enriched_reached_first_fields(actual,t);i=np.flatnonzero(actual['times']==t)[0]
    np.testing.assert_array_equal(fields['first_H'],actual['phase']['state'][i,320:400].T.reshape(8,4,20))
    np.testing.assert_array_equal(fields['first_H_rate'],actual['velocity']['velocity'][i,320:400].T.reshape(8,4,20))
    assert np.linalg.norm(fields['first_H'])>0
    assert np.linalg.norm(fields['first_gauge'])>0
    assert fields['profile']==fields['profile_rate']==0
    np.testing.assert_array_equal(fields['first_wall_gauge'],0)


def test_attached_binding_rejects_old_enriched_response():
    with pytest.raises(ValueError,match='attached response'):
        load_attached_reached_mean_inputs(
            'artifacts/muon_trace_enriched_reached_action_20261010/incoming_run_1',repository=ROOT)


def test_active_incoming_source_uses_future_clock_and_total_Tb_motion(actual):
    s=actual['source'];T=actual['times'][-1];D=actual['receipt']['source_pulse_duration']
    np.testing.assert_array_equal(s['coordinate_times'],s['times']-T)
    index=4;u=actual['times'][index];p,pt,_=compact_trace_pulse(u,D)
    assert p>0 and pt>0
    Q=CubicSpline(s['times'],s['Q'])(u);Qt=CubicSpline(s['times'],s['Qdot'])(u)
    np.testing.assert_allclose(actual['contacts']['source_trace_rate'][index],pt*Q+p*Qt,rtol=2e-16,atol=1e-12)
    with pytest.raises(ValueError,match='retained response node'):
        enriched_reached_first_fields(actual,u+1e-15)
