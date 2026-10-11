"""Moving metric chart and canonical birth pullback checks."""
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_birth_finite_geometric_trace_endpoint import (
    moving_geometric_trace_jet, pair_master_chart, temporal_birth_cotangent,
    moving_trace_saddle_data, projected_birth_cotangent, anchored_reference_clock_work,
    moving_endpoint_rows,
)
from bhsm.interface.muon_birth_normal_trace_graph import affine_connection_profile_two_jet
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.aether_full_reset_action_jacobian import (
    _attachment_jacobian_at_order, _attachment_coordinates_at_order, _trace_jacobian_at_order,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'


def actual():
    p = load_attached_endpoint(BASE/'paired_attachment_endpoint_run_1', side='incoming', repository=ROOT)
    with np.load(BASE/'normal_trace_graph_canonical_run_1/application.npz', allow_pickle=False) as a:
        raw = a['raw_pair'].copy(); graph = dict(raw_gradient=a['raw_gradient'], raw_hessian=a['raw_hessian'])
        profile = a['profile_first']; dual = a['profile_local_action_dual']
    with np.load(BASE/'paired_attachment_endpoint_run_1/application.npz', allow_pickle=False) as a:
        parent = dict(raw_gradient=a['updated_gradients'][0], raw_hessian=a['updated_hessians'][0])
        oldg = a['updated_gradients'].copy()
    return raw, p['representation'], graph, parent, profile, dual, oldg


def test_moving_metric_chart_recovers_owned_unmoved_values_and_attachment_B():
    raw, rep, *_ = actual()
    for x in raw:
        t = moving_geometric_trace_jet(x)
        np.testing.assert_allclose(t['value'][:3], _trace_jacobian_at_order(12)@x[:37], atol=3e-16)
        np.testing.assert_allclose(t['attachment_value'], _attachment_coordinates_at_order(12, x[:37]), atol=3e-16)
        np.testing.assert_allclose(t['attachment_first'][:, :37], _attachment_jacobian_at_order(12, x[:37]), atol=2e-15)
        # The normal derivative is retained even at the anchored base.
        assert np.linalg.norm(t['first'][:, 98]) > .1
    x = raw[0].copy(); x[98] = .002
    d = np.zeros(len(x)); d[[0, 4, 98]] = [.1, -.03, 1.]
    t = moving_geometric_trace_jet(x); eps = 2e-6
    p = moving_geometric_trace_jet(x+eps*d); m = moving_geometric_trace_jet(x-eps*d)
    np.testing.assert_allclose((p['value']-m['value'])/(2*eps), t['first']@d[:100], rtol=2e-8, atol=4e-10)
    np.testing.assert_allclose((p['first']-m['first'])@d[:100]/(2*eps),
        np.einsum('aij,i,j->a', t['second'], d[:100], d[:100]), rtol=2e-8, atol=1e-8)


def test_actual_temporal_face_is_oriented_cotangent_pullback_not_action_sum():
    raw, rep, graph, parent, profile, dual, oldg = actual(); chart = pair_master_chart(rep)
    f = temporal_birth_cotangent(graph, parent, chart); n = chart['dynamic_count']
    contact = dual[:, 1]@profile[:, 0]
    np.testing.assert_allclose(graph['raw_gradient'].reshape(2, -1)[:, 37:74].ravel(),
        oldg[:, 37:74].ravel()+contact[np.r_[np.arange(37), 100+np.arange(37)]], atol=8e-15)
    expected = oldg[0, 99]-oldg[1, 99]-contact[98]-contact[198]
    assert f['common_normal_raw_cotangent'] == pytest.approx(expected, abs=3e-15)
    assert expected == pytest.approx(-.8902631047775218, abs=3e-14)
    assert f['action_sum_momentum_not_temporal_jump']
    assert abs(graph['raw_gradient'][99]+graph['raw_gradient'][268+99]-expected) > 10


def test_joint_moved_trace_saddle_projects_full_face_with_constraint_reactions():
    raw, rep, graph, parent, *_ = actual()
    r = projected_birth_cotangent(graph, parent, raw, rep, compute_derivative=False)
    t = moving_trace_saddle_data(raw, rep, r['chart'])
    np.testing.assert_allclose(t['B']@r['base']['velocity_lift'], np.eye(6), atol=1e-11)
    np.testing.assert_allclose(r['base']['constraint_annihilation'], 0, atol=1e-10)
    np.testing.assert_allclose(r['kinetic_adjoint_residual'], 0, atol=1e-10)
    assert r['cotangent'].shape == (3,)
    assert np.linalg.norm(t['DB'][:, :, 37]) > .1
    assert r['base']['regularizing_shift'] == 0


def test_anchored_reference_clock_work_retains_exact_weak_source_derivative():
    raw, rep, graph, *_ = actual(); chart = pair_master_chart(rep)
    # The helper consumes the actual profile first jet, not a coefficient
    # projection; augment the saved action jet by this retained field map.
    base = affine_connection_profile_two_jet(raw, rep['rho'])
    graph.update(profile_increment=np.zeros_like(base['value']), profile_first=base['first'])
    a = anchored_reference_clock_work(raw, raw, rep, graph, chart)
    assert a['value'] == pytest.approx(.8028613141947586, abs=2e-15)
    d = np.zeros(len(chart['lift'][0])); nm = chart['master_count']
    d[[0, 37, nm+37, nm+chart['dynamic_count']+40]] = [.03, 1., 1., .07]
    delta = (chart['lift']@d).reshape(raw.shape); eps = 2e-6
    def work(x):
        p = affine_connection_profile_two_jet(x, rep['rho'])
        g = dict(profile_increment=p['value']-base['value'], profile_first=p['first'])
        return anchored_reference_clock_work(x, raw, rep, g, chart)['value']
    numeric = (work(raw+eps*delta)-work(raw-eps*delta))/(2*eps)
    assert numeric == pytest.approx(a['master_first']@d, rel=3e-8, abs=1e-7)


def test_full_row_directional_jacobian_includes_implicit_trace_and_clock_contacts():
    # This is a derivative check on the same actual field vector with a
    # reduced integration rule, not a physical quadrature closure claim.
    p = load_attached_endpoint(BASE/'paired_attachment_endpoint_run_1', side='incoming',
        repository=ROOT, radial_points=6, cap_points=48)
    with np.load(BASE/'paired_attachment_endpoint_run_1/application.npz', allow_pickle=False) as a:
        raw = a['updated_raw_pair']; weights = a['state_weights']; norm = a['normalization_coordinates']
    rep = p['representation']; rep['endpoint_action_parameters'] = p['receipt']['action_parameters']
    a = moving_endpoint_rows(raw, raw, rep, weights, norm)
    chart = a['chart']; nm = chart['master_count']; n = chart['dynamic_count']
    d = np.zeros(2*nm); d[[0, 37, nm, nm+37, nm+40, nm+n-1]] = [.03, 1., .03, 1., .1, .02]
    delta = (chart['lift']@d).reshape(raw.shape); eps = 2e-6
    plus = moving_endpoint_rows(raw+eps*delta, raw, rep, weights, norm, compute_cotangent_derivative=False)
    minus = moving_endpoint_rows(raw-eps*delta, raw, rep, weights, norm, compute_cotangent_derivative=False)
    numeric = (plus['residual']-minus['residual'])/(2*eps)
    expected = a['jacobian']@d
    np.testing.assert_allclose(numeric[:-3], expected[:-3], rtol=1e-7, atol=2e-6)
    # The last three rows use a centered directional Hessian derivative;
    # binary64 cancellation and saddle conditioning give a visible floor.
    np.testing.assert_allclose(numeric[-3:], expected[-3:], rtol=3e-5, atol=1e-4)
    assert a['jacobian'].shape == (226, 504)
