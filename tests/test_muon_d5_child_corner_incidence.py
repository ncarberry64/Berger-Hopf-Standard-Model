"""Birth normal-domain incidence, not a full child boundary solve."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_d5_child_corner_incidence import birth_corner_incidence


def test_actual_child_corner_requires_a_goursat_wedge():
    p = Path(__file__).resolve().parents[1]/'artifacts/muon_formed_event_domain_application_20261019/run_2/formed_event_domain_application.npz'
    with np.load(p) as z:
        a, r = birth_corner_incidence(z['outgoing_raw268'],
            z['outgoing_raw_coordinate_time_derivative268'])
    assert abs(r['outward_time_component']-.1687758438749448) < 1e-13
    assert r['outward_material_radial_component'] > 1
    assert not r['child_birth_ray_enters_future_domain']
    assert r['original_implicit_birth_curve_max'] < 1e-14
    assert a['normal_birth_curve_first'] > 0
    assert not r['physical_event_reset_or_Goursat_data_assigned']


def test_unassigned_corner_fields_are_not_zero_filled():
    with pytest.raises(ValueError):
        birth_corner_incidence(np.zeros(267), np.zeros(268))
