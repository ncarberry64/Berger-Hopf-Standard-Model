from __future__ import annotations

import json
import math

import numpy as np
import pytest

from bhsm.interface.aether_degree_one_join_state_map_v15_23 import (
    FULL_BHSM_COMPLETE,
    completion_payload,
    fixed_radial_domain_closure_audit,
    gravitational_kinetic_hamiltonian,
    gravitational_log_momenta,
    gravitational_velocity_form,
    invert_gravitational_log_momenta,
    materialize,
    round_join_recovery,
    radial_gauge_invariants,
    radial_momentum_constraint,
    shape_trial_rayleigh,
    static_legendre_certificate,
    smooth_join_boundary_domain,
)


def test_round_join_recovers_s7_and_degree_one_eta() -> None:
    for chi in (0.13, 0.41, 0.79, 1.31):
        result = round_join_recovery(2.7, chi)
        assert result["round_recovery"]
        assert result["degree_one_recovery"]
        assert np.isclose(result["R7"], 42.0 / 2.7**2)
        assert np.isclose(result["X_eta"], 7.0 / 2.7**2)


def test_round_join_rejects_collapse_poles_in_coordinate_formula() -> None:
    with pytest.raises(ValueError):
        round_join_recovery(1.0, 0.0)
    with pytest.raises(ValueError):
        round_join_recovery(1.0, math.pi / 2.0)


def test_gravitational_velocity_form_and_fixed_volume_reduction() -> None:
    result = gravitational_velocity_form()
    matrix = np.asarray(result["matrix"])
    assert np.linalg.matrix_rank(matrix) == 3
    assert result["direct_shape_coefficient"] == 6.0
    c_dot, h_dot, u_dot = -1.8, 0.3, -0.4
    value = np.array([c_dot, h_dot, u_dot]) @ matrix @ np.array(
        [c_dot, h_dot, u_dot]
    )
    assert np.isclose(value, 42.0 * h_dot**2 + 6.0 * u_dot**2)


def test_metric_log_legendre_map_inverts_and_hamiltonian_is_quadratic() -> None:
    rates = {"h_c": 0.2, "h_a": -0.1, "h_b": 0.3}
    momenta = gravitational_log_momenta(**rates, kappa1=1.7, volume=2.2)
    inverse = invert_gravitational_log_momenta(**momenta, kappa1=1.7, volume=2.2)
    assert np.isclose(inverse["H_C"], rates["h_c"])
    assert np.isclose(inverse["H_A"], rates["h_a"])
    assert np.isclose(inverse["H_B"], rates["h_b"])
    hamiltonian = gravitational_kinetic_hamiltonian(
        **momenta, kappa1=1.7, volume=2.2
    )
    expected = 0.5 * 1.7 * 2.2 * (
        -6 * rates["h_a"] ** 2
        - 6 * rates["h_b"] ** 2
        - 18 * rates["h_a"] * rates["h_b"]
        - 6 * rates["h_c"] * rates["h_a"]
        - 6 * rates["h_c"] * rates["h_b"]
    )
    assert np.isclose(hamiltonian, expected)


def test_shift_constraint_and_round_gauge_invariants() -> None:
    constraint = radial_momentum_constraint(
        p_c_chi=0.7,
        p_c=0.2,
        p_a=-0.1,
        p_b=0.4,
        p_f=0.3,
        p_sigma=-0.2,
        c_chi=0.5,
        a_chi=-0.6,
        b_chi=0.8,
        f_chi=1.0,
        sigma_chi=-0.9,
    )
    assert np.isclose(constraint, 0.26)
    chi, xi, xi_chi = 0.43, 0.09, -0.04
    before = radial_gauge_invariants(
        chi=chi,
        delta_c=0.2,
        delta_h=-0.4,
        delta_u=0.3,
        delta_f=-0.12,
        delta_f_chi=0.07,
    )
    after = radial_gauge_invariants(
        chi=chi,
        delta_c=0.2 + xi_chi,
        delta_h=-0.4 + xi / np.tan(2 * chi),
        delta_u=0.3 - xi / np.sin(2 * chi),
        delta_f=-0.12 + xi,
        delta_f_chi=0.07 + xi_chi,
    )
    assert before == pytest.approx(after)


def test_static_legendre_degeneracy_is_only_lapse_and_shift() -> None:
    result = static_legendre_certificate(
        volume=2.0, kappa1=1.0, x_eta=1.4, sigma_weight=1.2, zsigma=0.8
    )
    assert result["metric_velocity_Hessian_rank"] == 3
    assert result["eta_velocity_Hessian"] > 0.0
    assert result["sigma_velocity_Hessian"] > 0.0
    assert result["dynamical_field_block_regular"]
    assert result["primary_constraint_variables"] == ["lapse_N", "radial_shift_beta_chi"]


def test_smooth_join_domain_contains_both_collapse_poles() -> None:
    domain = smooth_join_boundary_domain()
    assert "B=0" in domain["chi_0"]
    assert "A=0" in domain["chi_pi_over_2"]
    assert domain["self_adjoint_boundary_form_must_vanish"]


def test_smooth_fixed_radial_trial_integrals_are_exact() -> None:
    result = shape_trial_rayleigh(power=2)
    assert np.isclose(result["norm_integral"], 2.0 / 35.0)
    assert np.isclose(result["gradient_integral"], 16.0 / 105.0)
    assert np.isclose(result["singular_potential_integral"], 4.0 / 15.0)
    assert np.isclose(result["geometric_Rayleigh_value"], -20.0 / 3.0)


def test_v15_9_crossing_does_not_destabilize_smooth_shape_trial() -> None:
    radius = (343.0 / 5.0) ** (1.0 / 6.0)
    result = shape_trial_rayleigh(power=2, radius=radius)
    assert np.isclose(result["omega_squared_diagnostic"], 16.0 / (3.0 * radius**2))
    assert result["omega_squared_diagnostic"] > 0.0
    assert result["constraint_reduced_eigenfrequency"] is False


def test_fixed_radial_operator_fails_smooth_domain_closure() -> None:
    result = fixed_radial_domain_closure_audit(2)
    assert result["input_leading_order"] == "chi^2"
    assert result["operator_leading_order"] == "chi^0"
    assert result["operator_leading_coefficient"] == -40.0
    assert result["fixed_radial_shape_operator_preserves_smooth_pole_domain"] is False
    assert result["not_a_physical_instability_claim"]


def test_completion_advances_to_full_constraint_reduction() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["physical_nonround_eigenmode_derived"] is False
    assert len(payload["Hindsight_20_20"]["OPEN"]) == 1


def test_materialization_is_deterministic(tmp_path) -> None:
    path = materialize(tmp_path)
    first = path.read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
