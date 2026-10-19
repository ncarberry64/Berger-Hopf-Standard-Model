"""Actual interacting-domain application; numerator scope stays explicit."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_formed_event_domain_application import (
    endpoint_seam_numerator,event_frame_incidence,endpoint_checks,
)

ROOT=Path(__file__).resolve().parents[1]


def data(side,label):
    with np.load(ROOT/('artifacts/muon_retained_response_20261018/inputs/'+side+'_history.npz')) as z:
        return z[label+'_raw_fields'].copy(),z[label+'_raw_coordinate_time_derivative'].copy()


@pytest.fixture(scope='module')
def endpoints():
    return tuple(endpoint_seam_numerator(*data(side,label)) for side,label in (
        ('incoming','hi'),('outgoing','lo')))


def test_actual_higgs_domain_has_nonzero_complement_and_original_rows(endpoints):
    for a in endpoints:
        checks=endpoint_checks(a)
        for key in ('original_weak_rows','isotropy_rows','nilpotence_rows',
            'selected_trace_image_rows','geometric_green_rows'):
            assert checks[key]['value_max']<2e-10
            assert checks[key]['coordinate_time_max']<2e-10
        assert checks['image_norm']>.02
        assert checks['image_time_norm']>1e-4
        assert checks['adapted_retained_complement_norm']>.02
        assert checks['free_hard_graph_defect_norm']>.01
        assert a['normal_mode_values_assigned'] is False
        for channel in checks['channel_coefficients'].values():
            assert channel['original_weak_value_max']<2e-10
            assert channel['original_weak_time_max']<2e-10
            assert channel['selected_trace_value_max']<2e-10
            assert channel['selected_trace_time_max']<2e-10
            assert channel['domain_complement_forcing_norm']>.01
        assert checks['forcing_numerical_rank']==12
        assert checks['middle_charged_forcing_numerical_rank']==4
        for row in checks['independent_channel_nilpotence'].values():
            assert row['value_max']<2e-10
            assert row['coordinate_time_max']<2e-10


def test_time_derivative_uses_actual_original_fields_and_geometry(endpoints):
    a=endpoints[1];x=a['raw268'];d=a['raw_coordinate_time_derivative268'];h=2e-6
    p=endpoint_seam_numerator(x+h*d,d)
    m=endpoint_seam_numerator(x-h*d,d)
    for key in ('Nhat','Bhat','Ehat','image','complement_image','domain_complement_image'):
        difference=(p[key][0]-m[key][0])/(2*h)
        assert np.max(abs(difference-a[key][1]))<2e-8


def test_two_temporal_boosts_intertwine_actual_interacting_eta_graph(endpoints):
    a=event_frame_incidence(*endpoints)
    for key in ('geometric_intertwining_rows','selected_numerator_intertwining_rows',
        'interacting_seam_intertwining_rows'):
        assert np.max(abs(a[key][0]))<2e-10
    assert np.linalg.norm(a['plus_boost'][0]-np.eye(384))>.5
    assert np.linalg.norm(a['plus_boost'][0]-a['minus_boost'][0])>1.
    assert abs(a['Cauchy_density_ratio']-1)<2e-14
    assert a['simultaneous_curvature_H_stabilizer_rank']==4
    assert np.min(a['spatial_SU2_curvature_singular_values'])>1.
    # Algebraic frame covariance does not equate the two actual histories.
    assert abs(endpoints[0]['velocity_time']-endpoints[1]['velocity_time'])>.01
    assert np.max(abs(a['selected_numerator_intertwining_rows'][1]))<2e-10
    assert 'u_R_in/u_R_out' in a['normalized_right_trace_rule']


def test_invalid_missing_original_fields_fail_closed():
    with pytest.raises(ValueError):endpoint_seam_numerator(np.zeros(267),np.zeros(268))
