"""Independent checks of the owned response and moving material traces."""

import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

from bhsm.interface.muon_moving_material_response import (
    anchored_response_jet,
    anchored_coordinate_advection,
    apply_anchored_trials,
    compatible_normal_trial,
    eulerian_embedding_split,
    identity_material_trial_jet,
    normal_geometry_first,
    orbit_length_pullback_jet,
    proper_length_material_trial,
    reciprocal_weight_jet,
    response_action_first,
    response_constraint_first,
    response_constraint_jet,
    response_constraint_weak_jet,
)


def test_anchored_response_mixed_jet_includes_length_normalization():
    chi = np.linspace(0, np.pi / 2, 801)
    f = chi + 0.035 * np.sin(2 * chi)
    a = np.exp(0.08 * np.cos(2 * chi))
    fx, fy = np.sin(2 * chi), 0.3 * np.sin(6 * chi)
    fxy = 0.2 * np.sin(4 * chi)
    mx, my, mxy = 0.2 * np.cos(2 * chi), 0.1 + 0.15 * np.sin(2 * chi), 0.07 * np.cos(4 * chi)
    result = anchored_response_jet(chi, f, a, f_x=fx, f_y=fy, f_xy=fxy,
                                  length_log_x=mx, length_log_y=my, length_log_xy=mxy)

    def value(x, y):
        profile = f + x * fx + y * fy + x * y * fxy
        length = a * np.exp(x * mx + y * my + x * y * mxy)
        density = np.sin(profile)**2 * np.cos(profile)**2 * length
        cells = 0.5 * (density[1:] + density[:-1]) * np.diff(chi)
        total = np.sum(cells)
        return np.r_[0, np.cumsum(cells)] / total - 0.5

    eps = 2e-4
    numerical_x = (value(eps, 0) - value(-eps, 0)) / (2 * eps)
    numerical_xy = (value(eps, eps) - value(eps, -eps)
                    - value(-eps, eps) + value(-eps, -eps)) / (4 * eps**2)
    np.testing.assert_allclose(result['sigma_x'], numerical_x, atol=3e-8, rtol=0)
    np.testing.assert_allclose(result['sigma_xy'], numerical_xy, atol=8e-8, rtol=0)
    assert abs(result['Z_x']) > 1e-3
    assert abs(result['Z_xy']) > 1e-3
    for key in ('sigma_x', 'sigma_y', 'sigma_xy'):
        np.testing.assert_allclose(result[key][[0, -1]], 0, atol=5e-16)


def test_metric_normal_term_is_required_for_response_tangent():
    chi = np.linspace(0, np.pi / 2, 401)
    a = np.exp(0.2 * np.cos(2 * chi))
    mx = 0.3 * np.sin(2 * chi)
    response = anchored_response_jet(
        chi, chi, a, f_x=np.sin(4 * chi), f_y=0, f_xy=0,
        length_log_x=mx, length_log_y=0, length_log_xy=0)
    i = 157
    applied = response_constraint_first(
        response_normal=[1 / a[i]], response_normal_x=[-mx[i] / a[i]],
        sigma_gradient=[response['coordinate_sigma_gradient'][i]],
        sigma_gradient_x=[response['coordinate_sigma_gradient_x'][i]],
        W=response['W'][i], W_x=response['W_x'][i],
        Z=response['Z'], Z_x=response['Z_x'])
    assert abs(applied['C_sigma']) < 3e-16
    assert abs(applied['C_sigma_x']) < 3e-16
    assert abs(applied['metric_normal_variation']) > 0.1


@pytest.mark.parametrize('spatial_sign', [-1, 1])
def test_normal_covector_and_outward_vector_with_metric_variation(spatial_sign):
    c, dc = 2.3, 0.7
    gi = np.diag([-spatial_sign, spatial_sign / c**2])
    dgi = np.diag([0, -2 * spatial_sign * dc / c**3])
    result = normal_geometry_first(gi, [0, 1], inverse_metric_x=dgi, gradient_x=[0, 0])
    np.testing.assert_allclose(result['conormal'], [0, c])
    np.testing.assert_allclose(result['raised_conormal'], [0, spatial_sign / c])
    np.testing.assert_allclose(result['increasing_normal'], [0, 1 / c])
    np.testing.assert_allclose(result['increasing_normal_x'], [0, -dc / c**2])
    # Independent normalization differentiation at an actually tilted gradient.
    gradient = np.array([0.1, 1.0])
    delta_gradient = np.array([0.03, -0.2])
    tilted = normal_geometry_first(gi, gradient, inverse_metric_x=dgi,
                                   gradient_x=delta_gradient)
    eps = 1e-6

    def direct(s):
        matrix, alpha = gi + s * dgi, gradient + s * delta_gradient
        q = alpha @ matrix @ alpha
        return np.sign(q) * (matrix @ alpha) / np.sqrt(abs(q))

    np.testing.assert_allclose(tilted['increasing_normal_x'],
                               (direct(eps) - direct(-eps)) / (2 * eps),
                               atol=1e-10, rtol=0)


def test_trial_normal_uses_eulerian_response_and_does_not_equal_common_advection():
    response = -0.4
    n = np.array([0, 0.5])
    ds = np.array([0.1, 2.0])
    psi = compatible_normal_trial(response, n @ ds)
    split = eulerian_embedding_split(eulerian_sigma=response,
                                     sigma_gradient=ds, embedding_velocity=psi * n)
    assert psi == pytest.approx(0.4)
    assert split['embedding'] == pytest.approx(0.4)
    assert split['pulled_material_derivative'] == pytest.approx(0)
    fixed_state = eulerian_embedding_split(eulerian_sigma=0, sigma_gradient=ds,
                                          embedding_velocity=psi * n)
    assert fixed_state['pulled_material_derivative'] != 0


def test_response_action_keeps_multiplier_and_both_measure_jets_off_shell():
    x = np.linspace(0, np.pi / 2, 101)
    a, mu = np.exp(0.1 * x), 1 + 0.2 * x
    lam, c = np.cos(x) + 0.4, 0.3 + np.sin(x)
    ax, mux, lx, cx = 0.2 * x, -0.1 * x, np.sin(2 * x), np.cos(2 * x)
    result = response_action_first(x, a, orbit_action_density=mu, multiplier=lam,
                                  C_sigma=c, orbit_action_log_x=mux, length_log_x=ax,
                                  multiplier_x=lx, C_sigma_x=cx)
    eps = 1e-6

    def direct(s):
        density = a * np.exp(s * ax) * mu * np.exp(s * mux) * (lam + s * lx) * (c + s * cx)
        return np.trapezoid(density, x)

    assert result['action_x'] == pytest.approx((direct(eps) - direct(-eps)) / (2 * eps), abs=5e-10)
    on_shell = response_action_first(x, a, orbit_action_density=mu, multiplier=lam,
                                    C_sigma=0, orbit_action_log_x=mux, length_log_x=ax,
                                    multiplier_x=lx, C_sigma_x=cx)
    assert on_shell['action_x'] == pytest.approx(np.trapezoid(a * mu * lam * cx, x))


def test_common_anchored_advection_has_required_measure_jet_and_is_not_relative_trial():
    chi = np.linspace(0, np.pi / 2, 4001)
    velocity = np.sin(2 * chi)
    gauge = anchored_coordinate_advection(
        chi, f_coordinate_gradient=1, length_coordinate_log_gradient=0,
        coordinate_velocity=velocity, coordinate_velocity_gradient=2 * np.cos(2 * chi))
    response = anchored_response_jet(
        chi, chi, 1, f_x=gauge['f_x'], f_y=0, f_xy=0,
        length_log_x=gauge['length_log_x'], length_log_y=0, length_log_xy=0)
    assert abs(response['Z_x']) < 2e-15
    exact_sigma_prime = 4 * np.sin(2 * chi)**2 / np.pi
    np.testing.assert_allclose(response['sigma_x'], -velocity * exact_sigma_prime,
                               atol=2e-7, rtol=0)
    midpoint = len(chi) // 2
    assert abs(response['sigma_x'][midpoint] + 4 / np.pi) < 2e-7
    relative = anchored_response_jet(
        chi, chi, 1, f_x=gauge['f_x'], f_y=0, f_xy=0,
        length_log_x=0, length_log_y=0, length_log_xy=0)
    assert abs(relative['sigma_x'][midpoint] + 4 / np.pi) > 0.4
    assert not gauge['physical_formation_mode_selected']


def test_two_harmonic_trial_normalization_against_independent_continuous_integrals():
    x = np.array([0.0, 0.29, np.pi / 4, 1.1, np.pi / 2])
    trial = identity_material_trial_jet(x, normal_velocity=1, C_star=2.064441085671303)
    a1, a3 = trial['eta_trial_coefficients']
    h = lambda q: a1 * np.sin(2 * q) + a3 * np.sin(6 * q)
    wx = lambda q: 0.5 * np.sin(4 * q) * h(q)
    wxx = lambda q: 2 * np.cos(4 * q) * h(q)**2
    zx = quad(wx, 0, np.pi / 2, epsabs=1e-13)[0]
    zxx = quad(wxx, 0, np.pi / 2, epsabs=1e-13)[0]
    assert zx == pytest.approx(trial['Z_x'], abs=1e-15)
    assert zxx == pytest.approx(trial['Z_xx'], abs=1e-14)
    assert abs(zxx) > 0.01
    for i, point in enumerate(x):
        bx = quad(wx, 0, point, epsabs=1e-13)[0]
        bxx = quad(wxx, 0, point, epsabs=1e-13)[0]
        expected_first = bx / trial['Z']
        expected_second = bxx / trial['Z'] - (trial['sigma'][i] + 0.5) * zxx / trial['Z']
        assert trial['sigma_x'][i] == pytest.approx(expected_first, abs=2e-15)
        assert trial['sigma_xx'][i] == pytest.approx(expected_second, abs=2e-15)


def test_two_material_trace_rows_through_second_order_independently():
    trial = identity_material_trial_jet(np.array([np.pi / 4]), normal_velocity=1.7, C_star=2.4)
    a1, a3 = trial['eta_trial_coefficients']
    k = trial['wall_coordinate_x']
    assert a1 - a3 + k == pytest.approx(0, abs=2e-16)
    assert (8 / np.pi) * (a1 / 3 + a3 / 5) + (4 / np.pi) * k == pytest.approx(0, abs=3e-16)
    # Recompute finite displaced traces from the original W(f), not the jets.
    def traces(s):
        wall = np.pi / 4 + s * k
        f = lambda chi: chi + s * (a1 * np.sin(2 * chi) + a3 * np.sin(6 * chi))
        w = lambda chi: np.sin(f(chi))**2 * np.cos(f(chi))**2
        z = quad(w, 0, np.pi / 2, epsabs=1e-13)[0]
        sigma = quad(w, 0, wall, epsabs=1e-13)[0] / z - 0.5
        return np.array([f(wall) - np.pi / 4, sigma])
    eps = 2e-4
    first = (traces(eps) - traces(-eps)) / (2 * eps)
    second = (traces(eps) + traces(-eps) - 2 * traces(0)) / eps**2
    np.testing.assert_allclose(first, 0, atol=1.8e-7, rtol=0)
    np.testing.assert_allclose(second, 0, atol=2e-8, rtol=0)
    # A single sin(2χ) trial can cancel σ but fails the inherited eta trace.
    single = -1.5 * k
    assert abs(single + k) > 0.1


def test_finite_trial_application_preserves_anchors_and_matches_directional_formula():
    chi = np.linspace(0, np.pi / 2, 501)
    f_trials = np.array([np.sin(2 * chi), np.sin(6 * chi)]).T
    length_trials = np.array([np.cos(2 * chi), 0.2 * np.sin(4 * chi)]).T
    result = apply_anchored_trials(chi, chi, 1, f_trials=f_trials,
                                  length_log_trials=length_trials)
    np.testing.assert_allclose(result['sigma_trials'][[0, -1]], 0, atol=2e-16)
    direction = np.array([0.7, -0.4])
    single = anchored_response_jet(
        chi, chi, 1, f_x=f_trials @ direction, f_y=0, f_xy=0,
        length_log_x=length_trials @ direction, length_log_y=0, length_log_xy=0)
    np.testing.assert_allclose(result['sigma_trials'] @ direction, single['sigma_x'], atol=8e-16)


def test_retained_E1_plus_geometry_is_an_actual_input_for_the_trial_not_a_selected_mode():
    repo = Path(__file__).resolve().parents[1]
    packet = json.loads((repo / 'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json').read_text())
    q = np.array([float.fromhex(x) for x in packet['geometry_field_blocks']['outgoing_C2']['q']['binary64_hex']])
    signs_k = (-1.0) ** np.arange(1, 13)
    signs_j = (-1.0) ** np.arange(12)
    c = (343.0 / 5.0)**(1.0 / 6.0) * np.exp(q[0] + q[1:13] @ signs_k + q[13:25] @ signs_j)
    assert 1 / c == pytest.approx(0.5213519106704843, abs=2e-16)
    result = identity_material_trial_jet(np.array([0, np.pi / 4, np.pi / 2]), normal_velocity=1, C_star=c)
    assert c * result['wall_coordinate_x'] == pytest.approx(1)
    assert result['wall_eta_material_x'] == pytest.approx(0, abs=2e-16)
    assert result['wall_sigma_material_x'] == pytest.approx(0, abs=2e-16)
    assert 'psi_selected' not in result


def test_trial_constraint_rows_and_arbitrary_multiplier_weak_application():
    chi = np.linspace(0, np.pi / 2, 101)
    t = identity_material_trial_jet(chi, normal_velocity=1, C_star=1.918090218)
    constraints = []
    for i in range(len(chi)):
        g = [t['sigma_coordinate_gradient'][i]]
        gx = [t['sigma_coordinate_gradient_x'][i]]
        gxx = [t['sigma_coordinate_gradient_xx'][i]]
        row = response_constraint_jet(
            response_normal_jet=([1], [0], [0], [0]),
            sigma_gradient_jet=(g, gx, gx, gxx),
            weight_jet=(t['W'][i], t['W_x'][i], t['W_x'][i], t['W_xx'][i]),
            normalization_jet=(t['Z'], t['Z_x'], t['Z_x'], t['Z_xx']))
        constraints.append([row[k] for k in ('C_sigma', 'C_sigma_x', 'C_sigma_y', 'C_sigma_xy')])
    constraint_jets = np.array(constraints).T
    np.testing.assert_allclose(constraint_jets, 0, atol=4e-16)
    applied = response_constraint_weak_jet(
        chi, measure_jet=(1 + chi, 0.3 * chi, -0.1, 0.2),
        multiplier_jet=(2 + np.cos(chi), np.sin(chi), 0.5 * chi, 0.7),
        constraint_jet=constraint_jets)
    assert abs(applied['action_xy']) < 2e-15
    assert abs(applied['multiplier_contact_xy']) < 2e-15


def test_weak_constraint_mixed_multiplier_contact_survives_zero_base_constraint():
    chi = np.linspace(0, np.pi / 2, 101)
    m = np.exp(0.1 * chi)
    mx, my, mxy = 0.2 * m, -0.1 * m, 0.08 * m
    l, lx, ly, lxy = 1 + chi, np.sin(chi), np.cos(chi), 0.3 * chi
    c, cx, cy, cxy = np.zeros_like(chi), np.cos(2 * chi), np.sin(2 * chi), 0.4 * chi
    value = response_constraint_weak_jet(
        chi, measure_jet=(m, mx, my, mxy), multiplier_jet=(l, lx, ly, lxy),
        constraint_jet=(c, cx, cy, cxy))
    contact = np.trapezoid(m * (lx * cy + ly * cx), chi)
    assert value['multiplier_contact_xy'] == pytest.approx(contact)
    assert abs(contact) > 0.1

    def action(x, y):
        measure = m + x * mx + y * my + x * y * mxy
        multiplier = l + x * lx + y * ly + x * y * lxy
        constraint = c + x * cx + y * cy + x * y * cxy
        return np.trapezoid(measure * multiplier * constraint, chi)

    eps = 2e-5
    mixed = (action(eps, eps) - action(eps, -eps)
             - action(-eps, eps) + action(-eps, -eps)) / (4 * eps**2)
    assert value['action_xy'] == pytest.approx(mixed, abs=5e-9)


def _actual_E1_C_profile():
    """Literal C=R exp[u+w], with the source owner's different k/j ranges."""
    repo = Path(__file__).resolve().parents[1]
    packet = json.loads((repo / 'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json').read_text())
    q = np.array([float.fromhex(x) for x in packet['geometry_field_blocks']['outgoing_C2']['q']['binary64_hex']])
    radius = (343.0 / 5.0)**(1.0 / 6.0) * np.exp(q[0])

    def profile(x):
        x = np.asarray(x)
        u = np.einsum('k,k...->...', q[1:13], np.cos(4 * np.arange(1, 13).reshape((-1,) + (1,) * x.ndim) * x))
        w = np.sin(2 * x)**2 * np.einsum('j,j...->...', q[13:25], np.cos(4 * np.arange(12).reshape((-1,) + (1,) * x.ndim) * x))
        return radius * np.exp(u + w)

    return profile


def test_actual_E1_proper_response_application_and_profile_refinement():
    profile = _actual_E1_C_profile()
    cstar = float(profile(np.pi / 4))
    results = []
    for points in (2049, 4097, 8193):
        chi = np.linspace(0, np.pi / 2, points)
        result = proper_length_material_trial(chi, profile(chi), C_star=cstar, normal_velocity=1)
        results.append(result)
        assert np.max(np.abs(result['response_constraint_rows'])) < 1e-14
        assert abs(result['wall_eta_material_x']) < 3e-16
        assert abs(result['wall_sigma_material_x']) < 2e-15
        assert abs(result['wall_sigma_material_xx']) < 2e-14
        assert result['wall_sigma_eulerian_x'] == pytest.approx(result['wall_sigma_eulerian_target'], abs=2e-15)
        assert abs(result['response']['Z_xy']) > 0.01
        assert not result['physical_formation_mode_selected']
    a, b, c = [r['eta_trial_coefficients'] for r in results]
    assert np.linalg.norm(b - c) < 0.26 * np.linalg.norm(a - b)
    # The promoted proper-length σ differs from the retained coordinate σ.
    fine = results[-1]
    chi = fine['response']['coordinate']
    coordinate_sigma = -0.5 + 2 * chi / np.pi - np.sin(4 * chi) / (2 * np.pi)
    assert np.max(np.abs(fine['response']['sigma'] - coordinate_sigma)) > 1e-4
    assert fine['chart'].endswith('NOT_RETAINED_COORDINATE_ACTION_REPLACEMENT')


def test_actual_E1_proper_response_trial_against_continuous_owner_integrals():
    profile = _actual_E1_C_profile()
    cstar = float(profile(np.pi / 4))
    chi = np.linspace(0, np.pi / 2, 32769)
    result = proper_length_material_trial(chi, profile(chi), C_star=cstar, normal_velocity=1)
    j1 = quad(lambda x: float(profile(x)) * 0.5 * np.sin(4 * x) * np.sin(2 * x), 0, np.pi / 4, epsabs=1e-13)[0]
    j3 = quad(lambda x: float(profile(x)) * 0.5 * np.sin(4 * x) * np.sin(6 * x), 0, np.pi / 4, epsabs=1e-13)[0]
    z = quad(lambda x: float(profile(x)) * np.sin(x)**2 * np.cos(x)**2, 0, np.pi / 2, epsabs=1e-13)[0]
    assert result['J1'] == pytest.approx(j1, abs=2e-9)
    assert result['J3'] == pytest.approx(j3, abs=2e-9)
    assert result['response']['Z'] == pytest.approx(z, abs=2e-14)
    a1, a3 = result['eta_trial_coefficients']
    k = 1 / cstar

    def finite_traces(s):
        wall = np.pi / 4 + s * k
        f = lambda x: x + s * (a1 * np.sin(2 * x) + a3 * np.sin(6 * x))
        weight = lambda x: float(profile(x)) * np.sin(f(x))**2 * np.cos(f(x))**2
        total = quad(weight, 0, np.pi / 2, epsabs=1e-13)[0]
        return np.array([f(wall) - np.pi / 4, quad(weight, 0, wall, epsabs=1e-13)[0] / total - 0.5])

    eps = 1e-4
    np.testing.assert_allclose((finite_traces(eps) - finite_traces(-eps)) / (2 * eps), 0, atol=2e-8)
    np.testing.assert_allclose((finite_traces(eps) + finite_traces(-eps) - 2 * finite_traces(0)) / eps**2,
                               0, atol=6e-8)


def test_proper_length_pullback_includes_coordinate_jacobian_and_normal_operator():
    chi = np.linspace(0, np.pi / 2, 101)
    c = np.exp(0.1 * np.cos(4 * chi))
    cp = -0.4 * np.sin(4 * chi) * c
    cpp = (-1.6 * np.cos(4 * chi) + 0.16 * np.sin(4 * chi)**2) * c
    velocity, vp = 0.2 * np.sin(4 * chi), 0.8 * np.cos(4 * chi)
    acc, accp = 0.07 * np.sin(2 * chi), 0.14 * np.cos(2 * chi)
    jet = orbit_length_pullback_jet(C=c, C_prime=cp, C_second=cpp,
        coordinate_velocity=velocity, velocity_prime=vp,
        coordinate_acceleration=acc, acceleration_prime=accp)

    def density(s):
        moved = chi + s * velocity + s**2 * acc / 2
        jacobian = 1 + s * vp + s**2 * accp / 2
        return np.exp(0.1 * np.cos(4 * moved)) * jacobian

    eps = 4e-5
    dx = (density(eps) - density(-eps)) / (2 * eps)
    dxx = (density(eps) + density(-eps) - 2 * density(0)) / eps**2
    np.testing.assert_allclose(jet['length_density_x'], dx, atol=3e-9, rtol=0)
    np.testing.assert_allclose(jet['length_density_xx'], dxx, atol=8e-7, rtol=0)
    invxx = (1 / density(eps) + 1 / density(-eps) - 2 / density(0)) / eps**2
    np.testing.assert_allclose(jet['orbit_derivative_coefficient_xx'], invxx, atol=8e-7, rtol=0)
    wall = len(chi) // 2
    assert abs(cp[wall]) < 1e-15
    assert abs(jet['length_density_x'][wall]) > 0.5
    assert abs(jet['orbit_derivative_coefficient_x'][wall]) > 0.5


def test_invalid_or_null_domains_fail_closed():
    with pytest.raises(ValueError, match='null normal'):
        normal_geometry_first(np.diag([-1, 1]), [1, 1], inverse_metric_x=np.zeros((2, 2)), gradient_x=[0, 0])
    with pytest.raises(ValueError, match='nonzero'):
        compatible_normal_trial(1, 0)
    with pytest.raises(ValueError, match='positive C_star'):
        identity_material_trial_jet([0, np.pi / 4], normal_velocity=1, C_star=0)
    with pytest.raises(ValueError, match='positive'):
        anchored_response_jet([0, 1], [0, 0], 1, f_x=0, f_y=0, f_xy=0,
                              length_log_x=0, length_log_y=0, length_log_xy=0)
