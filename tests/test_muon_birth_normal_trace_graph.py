"""Actual graph images and independent nonlinear action chain checks."""
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_birth_normal_trace_graph import (
    affine_connection_profile_two_jet, compose_action_two_jet,
    normal_trace_graph_action_two_jet, normal_trace_graph_action_value,
)
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint


ROOT = Path(__file__).resolve().parents[1]
INPUT = 'artifacts/muon_parent_gauge_geometry_correction_20261010/paired_attachment_endpoint_run_1'


def actual_pair(points=6):
    p = load_attached_endpoint(INPUT, side='incoming', repository=ROOT, radial_points=points, cap_points=48)
    c = load_attached_endpoint(INPUT, side='outgoing', repository=ROOT, radial_points=points, cap_points=48)
    return np.array([p['raw'], c['raw']]), p['representation'], p['receipt']['action_parameters']


def test_general_nonlinear_pullback_keeps_off_shell_contact_and_mixed_terms():
    x = np.array([.4, -.7])
    f = np.array([x[0]*x[1], np.exp(x[0]), x[1]**2])
    J = np.array([[x[1], x[0]], [np.exp(x[0]), 0.], [0., 2*x[1]]])
    D2 = np.zeros((3, 2, 2)); D2[0, 0, 1] = D2[0, 1, 0] = 1
    D2[1, 0, 0] = np.exp(x[0]); D2[2, 1, 1] = 2
    K = np.array([[2., .3, -.2], [.3, -1., .1], [-.2, .1, 4.]])
    load = np.array([.8, -.2, .5]); g = K@f+load
    a = compose_action_two_jet(.5*f@K@f+load@f, g, K, J, D2)
    def literal(z):
        q = np.array([z[0]*z[1], np.exp(z[0]), z[1]**2])
        return .5*q@K@q+load@q
    step = 2e-4
    for v in (np.array([1., 0.]), np.array([0., 1.]), np.array([1., -2.])):
        second = (literal(x+step*v)-2*literal(x)+literal(x-step*v))/step**2
        assert second == pytest.approx(v@a['hessian']@v, rel=3e-7, abs=1e-7)
    assert np.linalg.norm(a['hessian']-J.T@K@J) > 1.


def test_actual_profile_jets_include_both_geometry_blocks_and_embedding_once():
    raw, rep, _ = actual_pair()
    profile = affine_connection_profile_two_jet(raw, rep['rho'])
    direction = np.zeros(200); direction[[98, 198]] = 1
    step = 1e-6; plus = raw.copy(); minus = raw.copy()
    plus[:, 98] += step; minus[:, 98] -= step
    fp = affine_connection_profile_two_jet(plus, rep['rho'])
    fm = affine_connection_profile_two_jet(minus, rep['rho'])
    first = np.einsum('rki,i->rk', profile['first'], direction)
    second = np.einsum('rkij,i,j->rk', profile['second'], direction, direction)
    # The two near-pole derivative values subtract before this finite
    # difference, giving a visible binary64 cancellation floor (~1e-9).
    np.testing.assert_allclose((fp['value']-fm['value'])/(2*step), first, rtol=2e-8, atol=3e-9)
    np.testing.assert_allclose((fp['first']-fm['first'])@direction/(2*step), second, rtol=2e-8, atol=3e-8)
    assert np.linalg.norm(first[:, 0]) > .001
    assert profile['material_advection_count'] == 1
    # Incoming and child differ independently: no fixed-q/source-zero guard.
    assert np.linalg.norm(profile['first'][:, :, :37]) > 0
    assert np.linalg.norm(profile['first'][:, :, 100:137]) > 0


def test_actual_graph_action_normal_second_matches_literal_scalar_action():
    raw, rep, parameters = actual_pair()
    a = normal_trace_graph_action_two_jet(raw, raw, rep, **parameters)
    assert not a['source_image_projected']
    assert not a['full_stationary_birth_or_physical_formation_selected']
    assert np.max(abs(a['profile_increment'])) == 0
    np.testing.assert_allclose(a['raw_hessian'], a['raw_hessian'].T, rtol=0, atol=2e-9)
    assert a['normal_mixed'].shape == (2, 536)
    # Both material proper-normal values move together.  Matter/gauge and
    # every geometric coefficient remain the same unknowns in this chart.
    direction = a['normal_trial_directions'][:, 0].reshape(2, 268)
    base = normal_trace_graph_action_value(raw, raw, rep, **parameters)
    assert base == pytest.approx(a['value'], rel=2e-14, abs=2e-13)
    defects = []
    for step in (5e-5, 2.5e-5):
        p = normal_trace_graph_action_value(raw+step*direction, raw, rep, **parameters)
        m = normal_trace_graph_action_value(raw-step*direction, raw, rep, **parameters)
        first = (p-m)/(2*step); second = (p-2*base+m)/step**2
        assert first == pytest.approx(a['normal_first'][0], rel=2e-6, abs=2e-7)
        defects.append(abs(second-a['normal_second'][0, 0]))
    assert defects[1] < max(.4*defects[0], 2e-5)
    assert defects[1] < 2e-4
    # A joint direction reaches incoming q, child non-Abelian gauge and H,
    # testing the nonlinear source-geometry cross/contact rather than only
    # an isolated normal block.  No physical field values are changed.
    mixed = direction.copy(); mixed[0, 0] = .03
    mixed[1, 100+8] = .1; mixed[1, 261] = .02
    expected_first = a['raw_gradient']@mixed.reshape(-1)
    expected_second = mixed.reshape(-1)@a['raw_hessian']@mixed.reshape(-1)
    step = 2.5e-5
    p = normal_trace_graph_action_value(raw+step*mixed, raw, rep, **parameters)
    m = normal_trace_graph_action_value(raw-step*mixed, raw, rep, **parameters)
    assert (p-m)/(2*step) == pytest.approx(expected_first, rel=2e-6, abs=3e-6)
    assert (p-2*base+m)/step**2 == pytest.approx(expected_second, rel=2e-7, abs=3e-4)
