from __future__ import annotations

import json
import math

import numpy as np
import sympy as sp

from bhsm.interface.aether_norman_incidence_reconnection_v15_21 import (
    FULL_BHSM_COMPLETE,
    attachment_state_argument_audit,
    completion_payload,
    eta_fixed_momentum_quartic,
    eta_second_sigma_inertia_tensor,
    formation_peak_momentum_drive,
    homoclinic_formation_phase_space,
    instantaneous_sigma_activation_window,
    materialize,
    round_separation_incidence_audit,
)


def test_eta_second_sigma_tensor_and_scalar_reduction() -> None:
    inertia = np.asarray([[3.0]])
    tensor = eta_second_sigma_inertia_tensor(inertia, 0.7)
    assert np.allclose(tensor, [[4.2]])
    result = eta_fixed_momentum_quartic([1.1], inertia, 0.7)
    assert math.isclose(result["G_inertia"], 2.0 * 1.1**2 * 0.7**2 / 3.0)
    assert result["nonnegative"]


def test_second_sigma_tensor_matches_finite_difference() -> None:
    inertia = np.asarray([[2.0, 0.2], [0.2, 1.3]])
    g = 0.6
    eps = 1.0e-4
    plus = (1.0 + g * eps**2) * inertia
    zero = inertia
    minus = (1.0 + g * eps**2) * inertia
    finite_difference = (plus - 2.0 * zero + minus) / eps**2
    assert np.allclose(finite_difference, eta_second_sigma_inertia_tensor(inertia, g))


def test_homoclinic_hamiltonian_conserved_but_pq_not_conserved() -> None:
    center = homoclinic_formation_phase_space(
        0.0, supercriticality=0.5, critical_radius=1.7
    )
    flank = homoclinic_formation_phase_space(
        0.8, supercriticality=0.5, critical_radius=1.7
    )
    assert abs(center["Hamiltonian"]) < 1.0e-12
    assert abs(flank["Hamiltonian"]) < 1.0e-12
    assert abs(flank["Hamilton_equation_residual"]) < 1.0e-12
    assert center["p_q"] == 0.0
    assert abs(center["p_q_dot"]) > 0.0
    assert center["p_q_conserved"] is False


def test_homoclinic_solution_and_zero_energy_symbolically() -> None:
    tau, m, ac = sp.symbols("tau m a_c", positive=True, real=True)
    amplitude = sp.sqrt(sp.Rational(90, 23) * m)
    omega = sp.sqrt(sp.Rational(5, 6) * m / ac**2)
    q = amplitude * sp.sech(omega * tau)
    residual = sp.diff(q, tau, 2) - 5 * m * q / (6 * ac**2) + 23 * q**3 / (
        54 * ac**2
    )
    inertia = sp.Rational(3, 2) * ac**2
    potential = -sp.Rational(5, 8) * m * q**2 + sp.Rational(23, 144) * q**4
    energy = sp.Rational(1, 2) * inertia * sp.diff(q, tau) ** 2 + potential
    assert sp.simplify(sp.trigsimp(residual.rewrite(sp.exp))) == 0
    assert sp.simplify(sp.trigsimp(energy.rewrite(sp.exp))) == 0


def test_peak_momentum_drive_matches_exact_flank() -> None:
    m = 0.8
    radius = 2.3
    peak = formation_peak_momentum_drive(m)
    omega = math.sqrt(5.0 * m / (6.0 * radius**2))
    tau = peak["absolute_omega_tau_at_maximum"] / omega
    state = homoclinic_formation_phase_space(
        tau, supercriticality=m, critical_radius=radius
    )
    assert math.isclose(
        state["p_q"] ** 2 / state["M_q"],
        peak["max_p_q_squared_over_M_q"],
        rel_tol=1.0e-12,
    )


def test_instantaneous_sigma_branch_is_two_lobed_not_centered() -> None:
    active = instantaneous_sigma_activation_window(
        supercriticality=1.0,
        critical_radius=2.0,
        coupling_g=2.0,
        static_curvature=1.0,
    )
    assert active["active"]
    assert active["positive_time_interval"][0] > 0.0
    assert active["positive_time_interval"][1] > active["positive_time_interval"][0]
    assert active["negative_time_interval"][1] < 0.0
    assert active["active_at_concentration_peak_tau_zero"] is False
    assert active["active_asymptotically"] is False


def test_attachment_lineage_has_no_q_sigma_d_state_arguments() -> None:
    audit = attachment_state_argument_audit()
    assert audit["scalar_incidence_function_arguments"] == []
    assert audit["tensor_incidence_function_arguments"] == []
    assert audit["D2_sigma_attachment_map_evaluable"] is False
    assert audit["D_q_attachment_state_map_evaluable"] is False
    assert audit["D_d_attachment_state_map_evaluable"] is False


def test_round_separation_is_first_order_null_but_second_shape_nonzero() -> None:
    audit = round_separation_incidence_audit(1.4)
    assert audit["xi_plus_first_compatibility_column_norm"] == 0.0
    assert audit["xi_minus_first_compatibility_column_norm"] == 0.0
    assert audit["first_order_round_G_qd"] == 0.0
    assert audit["second_shape_nonzero"]
    assert audit["second_shape_is_a_first_order_canonical_tangent"] is False
    assert audit["canonical_p_d_available"] is False


def test_completion_fails_closed_at_one_exact_object() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["v15_10_sigma_nonuniqueness_resolved"] is False
    assert payload["q_to_d_canonical_transfer_derived"] is False
    assert len(payload["Hindsight_20_20"]["OPEN"]) == 1


def test_materialization_is_deterministic(tmp_path) -> None:
    path = materialize(tmp_path)
    first = path.read_bytes()
    second_path = materialize(tmp_path)
    second = second_path.read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
