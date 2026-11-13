"""Same-action kinetic trial checks retain every saddle reaction."""
from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.muon_birth_normal_constrained_action import (
    constrained_velocity_trial, joint_normal_kinetic_application,
)


def test_singular_velocity_form_has_an_exact_constraint_reaction_not_a_shift():
    # C controls the zero kinetic direction.  The direct saddle is invertible
    # even though an inverse-A or positive-minimum implementation would fail.
    A = np.diag([2., -3., 0.]); C = np.array([[0., 0., 1.]])
    B = np.array([[1., 0., 0.], [0., 1., 0.]])
    r = constrained_velocity_trial(A, C, B, velocity_cotangent=np.array([.4, .7, 9.]))
    np.testing.assert_allclose(r['kinetic_response'], np.diag([2., -3.]), atol=2e-15)
    np.testing.assert_allclose(r['trial_momentum'], [.4, .7], atol=2e-15)
    np.testing.assert_allclose(r['constraint_annihilation'], 0., atol=1e-15)
    np.testing.assert_allclose(r['kinetic_reaction_identity'], 0., atol=2e-15)
    assert r['regularizing_shift'] == 0 and r['spectral_directions_removed'] == 0


def test_kinetic_dual_matches_independent_constrained_stationarity():
    A = np.array([[2., .4, -.3], [.4, -1.2, .8], [-.3, .8, 3.]])
    C = np.array([[.2, -.7, 1.]])
    B = np.array([[1., .1, 0.]])
    r = constrained_velocity_trial(A, C, B)
    v = r['velocity_lift'][:, 0]
    # A null variation of both trace and constraint must do no work against
    # A v.  This independently tests the indefinite stationary application.
    z = np.cross(B[0], C[0]); z /= np.linalg.norm(z)
    assert z@A@v == pytest.approx(0., abs=2e-15)
    for s in (-.2, .3):
        change = .5*(v+s*z)@A@(v+s*z)-.5*v@A@v
        assert change == pytest.approx(.5*s*s*(z@A@z), abs=3e-16)


def test_actual_joint_graph_keeps_both_Gauss_sectors_and_normal_constraints():
    root = Path(__file__).resolve().parents[1]
    base = root/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    receipt = json.loads((base/'paired_attachment_endpoint_run_1/result.json').read_text())
    with np.load(base/'normal_trace_graph_canonical_run_1/application.npz', allow_pickle=False) as a:
        r = joint_normal_kinetic_application(a['raw_pair'], a['raw_gradient'], a['raw_hessian'],
            receipt['gauge_labels'], surface_gradient_per_gamma=a['surface_gradient_per_gamma'],
            surface_hessian_per_gamma=a['surface_hessian_per_gamma'])
    assert r['saddle'].shape == (298, 298)
    assert r['constraint_velocity'].shape == (80, 212)
    assert r['surface_saddle_coefficient_per_gamma'].shape == r['saddle'].shape
    np.testing.assert_allclose(r['trial_trace']@r['velocity_lift'], np.eye(6), atol=1e-11)
    np.testing.assert_allclose(r['constraint_annihilation'], 0., atol=1e-10)
    np.testing.assert_allclose(r['solve_residual'], 0., atol=1e-10)
    np.testing.assert_allclose(r['kinetic_reaction_identity'], 0., atol=1e-9)
    assert r['common_normal_kinetic'] == pytest.approx(6.99270985005, rel=2e-10)
    assert np.linalg.norm(r['velocity_lift'][:, 4:]) > 100
    assert not r['full_temporal_junction_or_formation_operator']
    assert r['all_multiplier_and_Gauss_reactions_retained']
