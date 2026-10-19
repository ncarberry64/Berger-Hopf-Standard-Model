import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_d5_raw_event_temporal_ports import (
    temporal_map_source_ports,material_velocity_source_from_spin,normal_rate_clock_ports,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import moving_d5_material_trace_frame


def test_all7_temporal_ports_retain_noncommuting_left_and_right_vertices():
    p=np.array([[.17j,.12],[-.12,-.09j]]);c=np.array([[-.11j,.03j],[.03j,.14j]])
    u=expm(np.array([[.21j,.13],[-.13,-.21j]]));k=.73
    a=temporal_map_source_ports(p,c,k,u)
    np.testing.assert_allclose(a['original_rows'],0,atol=2e-17)
    for ux,utx in zip(a['map_first'],a['temporal_first']):
        e=1e-5;F=lambda v:-c@v+k*v@p
        np.testing.assert_allclose(utx,(F(u+e*ux)-F(u-e*ux))/(2*e),atol=3e-12)


def test_recover_original_velocity_and_clock_rate_ports_without_history_replay():
    p,c=.13,-.27;px,cx=.21,-.11
    a=moving_d5_material_trace_frame(p,px);b=moving_d5_material_trace_frame(c,cx)
    np.testing.assert_allclose(material_velocity_source_from_spin(a['spin_boost128'],a['spin_boost_first128'],p),px,atol=6e-17)
    np.testing.assert_allclose(material_velocity_source_from_spin(b['spin_boost128'],b['spin_boost_first128'],c),cx,atol=6e-17)
    k=np.sqrt(1-c*c)/np.sqrt(1-p*p);v=normal_rate_clock_ports(k,p,c,px,cx)
    e=1e-5
    f=lambda P,C:np.sqrt(1-C*C)/np.sqrt(1-P*P)
    np.testing.assert_allclose(v,[(f(p+e*px,c)-f(p-e*px,c))/(2*e),(f(p,c+e*cx)-f(p,c-e*cx))/(2*e)],atol=8e-12)
