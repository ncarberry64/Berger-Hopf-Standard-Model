"""Exact area-law checks and retained E1+ reconstruction checks.

Synthetic coefficient inputs below are CONTROL_ONLY algebra fixtures.
The retained-state checks consume existing data without action/root replay.
"""
import json
import math
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from bhsm.interface.muon_birth_candidate_geometry_action import (
    RESET_RECEIPT,
    STATE_SOURCE,
    candidate_surface_normal_form,
    evaluate_retained_candidate_geometry,
    supplied_surface_stiffness,
    wall_geometry_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]


def _retained_state():
    receipt = json.loads((ROOT/RESET_RECEIPT).read_text())
    return np.array([float.fromhex(x) for x in
                     receipt['retained_state_values']['Phi_mu_plus_geometry']['binary64_hex']])


def test_retained_endpoint_indices_are_not_shifted_by_one():
    state = _retained_state()
    result = wall_geometry_snapshot(state[:37], state[37:74], state[74:])
    # Independent frozen E1+ values, not another call to the reconstruction.
    assert result['endpoint_profiles']['u'] == pytest.approx(0.002369009513617654, abs=1e-17)
    assert result['endpoint_profiles']['w'] == pytest.approx(-0.03676475809223184, abs=1e-17)
    assert result['endpoint_profiles']['v'] == pytest.approx(0.006621109282019484, abs=1e-17)
    assert result['endpoint_profiles']['log_N'] == pytest.approx(-0.355740766388884, abs=1e-16)
    assert result['shift']['beta_chi'] == pytest.approx(2.1083831285076995, rel=1e-15)
    assert result['coordinate_time_log_rates']['C'] == pytest.approx(5.298749758682122, rel=1e-15)


def test_retained_geometry_normal_uses_actual_raw_metric():
    state = _retained_state()
    result = wall_geometry_snapshot(state[:37], state[37:74], state[74:])
    assert 1/result['C'] == pytest.approx(0.5213519106704843, rel=2e-15)
    assert 1/result['N'] == pytest.approx(1.4272375123687948, rel=2e-15)
    assert result['unit_normal_trace_per_amplitude'] == [0.0, -1/result['C'], 1/result['C']]
    assert result['fixed_chart_state_levelset_derivative'] == 0
    assert result['fixed_eta_wall_levelset_derivative_per_amplitude'] > 0


def test_separate_cosine_indices_and_window_second_derivative_control_only():
    q = np.zeros(7)
    # N=2: u1,u2 | w0,w1 | v0,v1, distinct endpoint signs.
    q[1:] = [1/100, 2/100, 3/100, 4/100, 5/100, 6/100]
    v = np.zeros(7)
    m = np.array([7/100, 8/100, 9/100, 10/100])
    result = wall_geometry_snapshot(q, v, m, order=2)
    assert result['endpoint_profiles']['u'] == pytest.approx(1/100)
    assert result['endpoint_profiles']['w'] == pytest.approx(-1/100)
    assert result['endpoint_profiles']['v'] == pytest.approx(-1/100)
    assert result['endpoint_profiles']['log_N'] == pytest.approx(1/100)
    assert result['shift']['beta_chi'] == pytest.approx(4/100)
    assert result['chi_second_log']['C'] == pytest.approx(-40/100)
    # Direct scalar derivatives of the exact profile, independent of output.
    chi = sp.symbols('chi', real=True)
    u = sp.cos(4*chi)/100 + sp.cos(8*chi)/50
    w = sp.sin(2*chi)**2*(sp.Rational(3,100)+sp.cos(4*chi)/25)
    c2 = sp.diff(u+w, chi, 2).subs(chi, sp.pi/4)
    assert result['chi_second_log']['C'] == pytest.approx(float(c2))


@pytest.mark.parametrize('stratum', ['M8', 'M5'])
def test_surface_second_variation_from_graph_determinant_control_only(stratum):
    # CONTROL_ONLY exact graph law: independently differentiate the area,
    # including nonzero first curvature, temporal C motion and shift.
    s, a, adot, C, N, cdot, beta, rho, gamma, l1, l2, grad2 = sp.symbols(
        's a adot C N cdot beta rho gamma l1 l2 grad2', real=True)
    graph_density = rho*sp.exp(l1*s*a/C + l2*s*s*a*a/(2*C*C))
    graph_slope_square = s*s*(grad2-(adot-(cdot-beta)*a)**2/N**2)
    area_action = -gamma*graph_density*sp.sqrt(1+graph_slope_square)
    first = sp.diff(area_action, s).subs(s, 0)
    second = sp.diff(area_action, s, 2).subs(s, 0)
    expected_first = -gamma*rho*l1*a/C
    expected_second = gamma*rho*((adot-(cdot-beta)*a)**2/N**2
                                 -grad2-(l2+l1*l1)*a*a/C**2)
    assert sp.simplify(first-expected_first) == 0
    assert sp.simplify(second-expected_second) == 0
    control = wall_geometry_snapshot(np.zeros(7), np.zeros(7), np.zeros(4), order=2)
    form = candidate_surface_normal_form(control, stratum=stratum)
    assert form['second_normal_form']['normal_time_connection'] == 0
    assert form['second_normal_form']['V_graph'] == pytest.approx(-12/RADIUS0**2)
    assert form['surface_inertia_density_per_gamma'] > 0


def test_moving_fiber_measure_prevents_false_quotient_zero():
    packet = evaluate_retained_candidate_geometry()
    g = packet['geometry']
    ambient, quotient = (packet['separate_surface_contributions'][name] for name in ('M8','M5'))
    assert ambient['mean_curvature'] == 0
    assert abs(quotient['mean_curvature']) > 1e-3
    assert ambient['coordinate_time_area_density_per_unit_angular_measure'] == pytest.approx(
        quotient['coordinate_time_area_density_per_unit_angular_measure']*g['fiber_radius']**3,
        rel=3e-15)
    quotient_l1 = quotient['mean_curvature']*g['C']
    fiber_l1 = 3*g['chi_first_log']['fiber']
    assert quotient_l1+fiber_l1 == pytest.approx(0, abs=1e-15)
    qratio2 = quotient['second_normal_form']['V_graph']*g['C']**2
    fiber_l2 = 3*g['chi_second_log']['fiber']
    aratio2 = ambient['second_normal_form']['V_graph']*g['C']**2
    assert qratio2+(fiber_l2+fiber_l1**2)+2*quotient_l1*fiber_l1 == pytest.approx(aratio2, abs=2e-13)
    assert packet['moving_fiber_pullback']['sum_across_strata_performed'] is False


def test_shift_connection_is_retained_in_area_inertia():
    packet = evaluate_retained_candidate_geometry()
    g = packet['geometry']
    assert g['Hc'] == pytest.approx(
        (g['coordinate_time_log_rates']['C']-g['shift']['beta_chi'])/g['N'])
    assert abs(g['Hc']-g['coordinate_time_log_rates']['C']/g['N']) > 1
    for surface in packet['separate_surface_contributions'].values():
        assert surface['second_normal_form']['normal_time_connection'] == g['Hc']
        # The evaluated coefficients do not select psi or normalize full I.
        assert surface['normal_amplitude_selected'] is False
        assert surface['full_inertia_normalization'] is None


def test_retained_receipt_matches_original_and_is_not_stationary_promotion():
    packet = evaluate_retained_candidate_geometry()
    with np.load(ROOT/STATE_SOURCE, allow_pickle=False) as data:
        original = data['state'][:98]
    assert np.array_equal(_retained_state().view(np.uint64), original.view(np.uint64))
    assert packet['source']['branch'] == 24
    assert packet['retained_geometric_base_residual']['multiplier_constraints']['l2_norm'] == pytest.approx(
        3.624453649115574e-15, rel=1e-15)
    assert packet['retained_geometric_base_residual']['full_classical_L_eta'] is None
    assert packet['retained_geometric_base_residual']['full_classical_stationarity_established'] is False
    assert all(value is None for value in packet['physical_source'].values())
    assert packet['execution']['old_action_producer_calls'] == 0


def test_nonminimal_wall_hessian_retains_mean_curvature_squared():
    packet = evaluate_retained_candidate_geometry()
    form = packet['separate_surface_contributions']['M5']
    q = form['second_normal_form']
    assert q['mean_curvature_squared'] > 0
    assert q['V_graph'] == pytest.approx(
        q['normal_area_measure_log_contact']+q['mean_curvature_squared'], abs=3e-15)


def test_nonlinear_levelset_path_retains_first_variation_contact_control_only():
    s, a, chi_second, C, rho, gamma, l1, l2 = sp.symbols(
        's a chi_second C rho gamma l1 l2', real=True)
    coordinate_motion = s*a/C + s*s*chi_second/2
    action = -gamma*rho*sp.exp(l1*coordinate_motion+l2*coordinate_motion**2/2)
    second = sp.diff(action,s,2).subs(s,0)
    affine = -gamma*rho*(l2+l1*l1)*a*a/C**2
    assert sp.simplify(second-affine+gamma*rho*l1*chi_second) == 0
    packet = evaluate_retained_candidate_geometry()
    assert packet['separate_surface_contributions']['M8'][
        'second_action_embedding_path_contact_per_gamma_per_chi_second'] == 0
    assert packet['separate_surface_contributions']['M5'][
        'second_action_embedding_path_contact_per_gamma_per_chi_second'] != 0


def test_supplied_stiffness_is_existing_dimensional_owner_law_control_only():
    assert supplied_surface_stiffness(2, 3, stratum='M8') == pytest.approx(2/3**7)
    assert supplied_surface_stiffness(2, 3, stratum='M5') == pytest.approx(2/3**4)
    with pytest.raises(ValueError):
        supplied_surface_stiffness(2, 3, stratum='M4')


@pytest.mark.parametrize('bad_order', [0, -1, 1.5, True])
def test_invalid_order_is_rejected(bad_order):
    with pytest.raises(ValueError, match='positive integer'):
        wall_geometry_snapshot(np.zeros(7), np.zeros(7), np.zeros(4), order=bad_order)


def test_invalid_state_and_missing_stratum_are_rejected():
    with pytest.raises(ValueError, match='q must'):
        wall_geometry_snapshot([0]*6, [0]*7, [0]*4, order=2)
    with pytest.raises(ValueError, match='velocity must'):
        wall_geometry_snapshot([0]*7, [math.nan]*7, [0]*4, order=2)
    g = wall_geometry_snapshot([0]*7, [0]*7, [0]*4, order=2)
    with pytest.raises(ValueError, match='only the supplied'):
        candidate_surface_normal_form(g, stratum='M4')


def test_result_mutations_are_detached():
    first = evaluate_retained_candidate_geometry()
    first['geometry']['C'] = -1
    first['retained_geometric_base_residual']['multiplier_constraints']['values'][0] = 99
    second = evaluate_retained_candidate_geometry()
    assert second['geometry']['C'] > 0
    assert second['retained_geometric_base_residual']['multiplier_constraints']['values'][0] != 99
