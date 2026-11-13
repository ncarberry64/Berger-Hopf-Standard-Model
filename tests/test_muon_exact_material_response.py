"""Exact owned anchors and finite-chart action derivatives, without mode selection."""
from pathlib import Path
import math
import numpy as np
import pytest

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_moving_geometric_action import (
    moving_cap_action_jet, retained_state, response_two_jet,
)
from bhsm.interface.muon_exact_material_response import (
    anchored_join_coefficients, exact_response_at, exact_moving_cap_action_jet,
    exact_geometric_connection_coefficient_jets,
)

ROOT = Path(__file__).resolve().parents[1]


def variable(value, index, dim=2):
    g = np.zeros(dim); g[index] = 1.
    return Jet(value, g, np.zeros((dim, dim)))


def test_implicit_anchors_higher_jets_and_reflection():
    base = anchored_join_coefficients(0.)
    np.testing.assert_allclose(base['derivatives'],
        [[-21/16, 0., -789/308], [-5/16, 0., -6333/308]], rtol=2e-13, atol=2e-13)
    assert base['normalization'] == pytest.approx(math.pi/16, abs=1e-15)
    for delta in (.02, .1):
        plus = anchored_join_coefficients(delta)
        minus = anchored_join_coefficients(-delta)
        np.testing.assert_allclose(minus['coefficients'], -plus['coefficients'], atol=6e-15)
        np.testing.assert_allclose(minus['derivatives'],
            plus['derivatives']*np.array([1., -1., 1.]), atol=2e-12)
        assert np.max(abs(plus['anchor_Taylor_residual'])) < 3e-13
        assert plus['monotone_derivative_lower_bound'] > 0
        # Differentiate the solved finite chart, independently of the
        # implicit Taylor recursion; it must retain its nonzero cubic jet.
        eps = 1e-5
        pp = anchored_join_coefficients(delta+eps)
        pm = anchored_join_coefficients(delta-eps)
        np.testing.assert_allclose((pp['derivatives'][:, 1]-pm['derivatives'][:, 1])/(2*eps),
            plus['derivatives'][:, 2], rtol=2e-7, atol=3e-7)


def test_normalized_sigma_jets_match_retained_tangent_and_exact_moving_traces():
    delta = variable(0., 0); chi = variable(.37, 1); rate = Jet.constant(0., 2)
    new = exact_response_at(chi, delta, rate, anchored_join_coefficients(0.))
    old_f, old_sigma = response_two_jet(chi, delta, Jet.constant(-1/16, 2))
    for a, b in ((new['f'], old_f), (new['sigma'], old_sigma)):
        assert a.value == pytest.approx(b.value, abs=2e-15)
        np.testing.assert_allclose(a.gradient, b.gradient, atol=2e-14)
        np.testing.assert_allclose(a.hessian, b.hessian, atol=2e-13)
    # All anchors remain constant at finite displacement, through their
    # *actual* first/second derivatives rather than a Taylor-only identity.
    delta = variable(.07, 0); rate = variable(.03, 1)
    wall = math.pi/4+delta
    a = exact_response_at(wall, delta, rate, anchored_join_coefficients(delta.value))
    assert a['f'].value == pytest.approx(math.pi/4, abs=3e-15)
    assert a['sigma'].value == pytest.approx(0., abs=3e-15)
    np.testing.assert_allclose(a['f'].gradient, 0., atol=3e-14)
    np.testing.assert_allclose(a['f'].hessian, 0., atol=5e-13)
    np.testing.assert_allclose(a['sigma'].gradient, 0., atol=3e-14)
    np.testing.assert_allclose(a['sigma'].hessian, 0., atol=5e-13)


def test_same_signed_cap_action_matches_recorded_zero_normal_twojet():
    q, v, m = retained_state(ROOT)
    old = moving_cap_action_jet(12, q, v, m, points=48)
    new = exact_moving_cap_action_jet(12, q, v, m, points=48)
    for name in ('total', 'FR_denominator', 'moving_GHY_Hayward', 'surface_per_gamma'):
        a, b = old[name], new[name]
        assert a.value == pytest.approx(b.value, rel=2e-14, abs=2e-13)
        np.testing.assert_allclose(a.gradient, b.gradient, rtol=3e-12, atol=8e-12)
        np.testing.assert_allclose(a.hessian, b.hessian, rtol=3e-12, atol=3e-10)
    assert not new['physical_mode_or_formation_selected']


def test_finite_normal_action_rate_and_geometry_cross_matches_literal_differences():
    q, v, m = retained_state(ROOT)
    # The retained state has a narrow positive eta/timelike response domain;
    # this finite displacement is checked inside it, rather than forcing a
    # large displacement through the domain guard.
    x = np.r_[q, v, m, .001, .00001]
    def evaluate(z, normalization_points=96):
        return exact_moving_cap_action_jet(12, z[:37], z[37:74], z[74:98],
            source_value=z[98], source_rate=z[99], points=48,
            response_points=normalization_points)
    a = evaluate(x)
    for name in ('exact_f_trace', 'exact_sigma_trace'):
        assert abs(a[name].value) < 3e-15
        assert np.max(abs(a[name].gradient)) < 3e-14
        assert np.max(abs(a[name].hessian)) < 5e-13
    direction = np.zeros(100); direction[[0, 1, 39, 74, 98, 99]] = [.01, -.002, .001, .003, 1., .1]
    defects = []
    for step in (4e-6, 2e-6):
        p, n = evaluate(x+step*direction), evaluate(x-step*direction)
        derivative = (p['total'].gradient-n['total'].gradient)/(2*step)
        defects.append(np.max(abs(derivative-a['total'].hessian@direction)))
    assert defects[1] < max(.4*defects[0], 1e-7)
    np.testing.assert_allclose(derivative, a['total'].hessian@direction, rtol=2e-7, atol=3e-6)
    assert (p['total'].value-n['total'].value)/(2*step) == pytest.approx(
        a['total'].gradient@direction, rel=2e-7, abs=3e-7)
    refined = evaluate(x, 128)
    np.testing.assert_allclose(a['total'].hessian, refined['total'].hessian, rtol=2e-11, atol=2e-9)


def test_actual_material_maxwell_densities_match_zero_chart_and_finite_chain():
    from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    q, v, m = retained_state(ROOT)
    rho = np.array([.02, .3, .8, WALL])
    old = geometric_connection_coefficient_jets(12, q, v, m, rho)
    new = exact_geometric_connection_coefficient_jets(12, q, v, m, rho)
    for a, b in zip(old['rows'], new['rows']):
        for key in ('electric', 'electric_radial', 'radial', 'angular', 'shift', 'connection_lambda', 'lambda_tau', 'lambda_rho'):
            # The old 1-4sigma^2 loses relative digits close to the pole;
            # the exact implementation uses equivalent positive 4p(1-p).
            assert a[key].value == pytest.approx(b[key].value, rel=2e-11, abs=3e-12)
            np.testing.assert_allclose(a[key].gradient, b[key].gradient, rtol=2e-11, atol=2e-11)
            np.testing.assert_allclose(a[key].hessian, b[key].hessian, rtol=2e-11, atol=2e-9)
    eps = 2e-6; source = .001
    a = exact_geometric_connection_coefficient_jets(12, q, v, m, rho, source_value=source)
    p = exact_geometric_connection_coefficient_jets(12, q, v, m, rho, source_value=source+eps)
    n = exact_geometric_connection_coefficient_jets(12, q, v, m, rho, source_value=source-eps)
    for a, p, n in zip(a['rows'], p['rows'], n['rows']):
        for key in ('electric', 'electric_radial', 'radial', 'angular', 'lambda_tau'):
            np.testing.assert_allclose((p[key].gradient-n[key].gradient)/(2*eps),
                a[key].hessian[:, 98], rtol=2e-7, atol=8e-6)
