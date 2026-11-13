"""Consume the actual changed two-arm geometry without omitting its graph image."""
from pathlib import Path
import numpy as np
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.muon_birth_finite_wall_fields import finite_wall_connection_two_jet

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'


def actual():
    p = load_attached_endpoint(BASE/'paired_attachment_endpoint_run_1', side='incoming', repository=ROOT)
    with np.load(BASE/'finite_moving_trace_run_1/application.npz', allow_pickle=False) as a:
        return a['updated_raw_pair'].copy(), a['reference_raw_pair'].copy(), p['representation']


def test_actual_full_wall_fields_include_time_and_radial_affine_image():
    x, ref, rep = actual()
    a = finite_wall_connection_two_jet(x, ref, rep, second_derivatives=False)
    # Actual numerical temporal matching reproduces the physical connection
    # at the wall while its derivative image remains active.
    np.testing.assert_allclose(a['value'][0, 0], a['value'][1, 0], atol=3e-14)
    assert abs(a['child_affine_profile_increment'][0, 1]) > .08
    assert abs(a['child_affine_profile_increment'][0, 2]) > .001
    # A lone child raw vector would discard these parent-driven derivatives.
    assert np.linalg.norm(a['first'][1, :, 2:, :, :100]) > 1.
    assert not a['bulk_profile_projected']
    assert not a['physical_stationary_state_or_formation_selected']


def test_full_joint_field_second_jets_match_independent_first_jet_differences():
    x, ref, rep = actual()
    a = finite_wall_connection_two_jet(x, ref, rep)
    direction = np.zeros_like(x)
    direction[0, [0, 3, 37, 98, 99]] = [.02, -.001, .03, .1, -.02]
    direction[1, [2, 45, 98, 99, 107]] = [.001, -.01, .1, -.01, .3]
    eps = 2e-6
    p = finite_wall_connection_two_jet(x+eps*direction, ref, rep, second_derivatives=False)
    n = finite_wall_connection_two_jet(x-eps*direction, ref, rep, second_derivatives=False)
    np.testing.assert_allclose((p['value']-n['value'])/(2*eps),
        a['first']@direction.ravel(), rtol=3e-8, atol=2e-9)
    np.testing.assert_allclose((p['first']-n['first'])/(2*eps),
        a['second']@direction.ravel(), rtol=3e-8, atol=2e-8)
