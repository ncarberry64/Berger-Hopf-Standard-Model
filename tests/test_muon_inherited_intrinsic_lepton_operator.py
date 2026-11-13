from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator


@pytest.fixture(scope='module')
def actual_inputs():
    root=Path(__file__).resolve().parents[1]
    base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing',repository=root)
    with np.load(root/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1/application.npz') as a:
        return dict(raw=a['stage_independent_raw'][0],time=float(a['stage_coordinate_time'][0]),
            initial=a['initial_pair'],reference=a['reference_pair'],rep=base['representation'],
            expected_wall=a['stage_wall_gauge'][0],expected_rate=a['stage_wall_gauge_rate'][0])


def apply(data,raw=None):
    return inherited_intrinsic_lepton_operator(data['raw'] if raw is None else raw,data['time'],
        data['initial'],data['reference'],data['rep'])


def test_owned_exact_wall_geometry_and_unprojected_image_match_solved_stage(actual_inputs):
    a=apply(actual_inputs)
    np.testing.assert_allclose(a['wall_independent_plus_inherited_image'],actual_inputs['expected_wall'],rtol=0,atol=3e-16)
    np.testing.assert_allclose(a['wall_independent_plus_inherited_image_coordinate_rate'],actual_inputs['expected_rate'],rtol=0,atol=3e-16)
    assert abs(a['mechanical_lambda_owner_difference'])<3e-16
    assert a['mechanical_lambda_owner_first_jet_difference']<3e-15
    np.testing.assert_allclose(a['W'],a['W'].conj().T,rtol=0,atol=3e-15)
    assert np.linalg.norm(a['W_profile_contact'])>0
    assert a['mechanical_connection_count']==1
    assert a['geometry']['R4']['value']>0
    assert a['geometry']['induced_lapse']['value']>0


def test_complete_nonlinear_child_first_jet_matches_literal_action_direction(actual_inputs):
    raw=actual_inputs['raw'];a=apply(actual_inputs);u=np.zeros(len(raw))
    u[[0,13,37,86,98]]=[.31,-.23,.07,.13,.19];u[-8]=.17
    eps=1e-5;p=apply(actual_inputs,raw+eps*u);m=apply(actual_inputs,raw-eps*u)
    for key,jet in (('W','W_raw_first_jet'),('H_can','H_can_raw_first_jet'),('Omega_tau','Omega_tau_raw_first_jet')):
        literal=(p[key]-m[key])/(2*eps)
        expected=np.einsum('j,juv->uv',u,a[jet])
        np.testing.assert_allclose(literal,expected,rtol=3e-8,atol=2e-9)
    for name in a['geometry']:
        literal=(p['geometry'][name]['value']-m['geometry'][name]['value'])/(2*eps)
        expected=a['geometry'][name]['raw_first_jet']@u
        np.testing.assert_allclose(literal,expected,rtol=3e-8,atol=2e-9)


def test_child_mechanical_motion_is_cancelled_once_by_the_owned_affine_image(actual_inputs):
    raw=actual_inputs['raw'];u=np.zeros(len(raw));u[[1,14,98]]=[.7,-.2,.3]
    p=apply(actual_inputs,raw+2e-5*u);m=apply(actual_inputs,raw-2e-5*u)
    # At fixed parent/reference chart the full child connection inherits
    # their lambda; changing child geometry moves mechanical and affine
    # terms with opposite derivatives.  This does not freeze the metric.
    np.testing.assert_allclose(p['total_wall_connection'],m['total_wall_connection'],rtol=0,atol=2e-15)
    assert p['geometry']['R4']['value']!=m['geometry']['R4']['value']
    assert p['algebraic_At_coordinate_rate_not_claimed']
