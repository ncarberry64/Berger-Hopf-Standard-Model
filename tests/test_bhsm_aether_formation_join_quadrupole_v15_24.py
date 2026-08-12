from __future__ import annotations

import json

import numpy as np

from bhsm.interface.aether_formation_join_quadrupole_v15_24 import (
    FULL_BHSM_COMPLETE,
    completion_payload,
    conformal_l2_hamiltonian_response,
    formation_join_quadrupole,
    formed_branch_l2_legendre_reduction,
    join_invariant_scalar_spectrum,
    l2_unitary_gauge_shift_reduction,
    materialize,
    radial_eta_strain_series,
    sigma_homoclinic_transfer,
    sphere_moment_monte_carlo,
    symmetry_reduction_firewall,
)


def test_exact_formation_join_projection_extrema_and_balanced_zero() -> None:
    plus = formation_join_quadrupole([1, 0, 0, 0, 0, 0, 0, 0])
    minus = formation_join_quadrupole([0, 0, 0, 0, 1, 0, 0, 0])
    zero = formation_join_quadrupole([1, 0, 0, 0, 1, 0, 0, 0])
    assert np.isclose(plus["relative_orientation_zeta"], 1.0)
    assert np.isclose(minus["relative_orientation_zeta"], -1.0)
    assert np.isclose(zero["relative_orientation_zeta"], 0.0)
    assert np.isclose(plus["join_projection_coefficient"], 1.0 / 8.0)
    assert np.isclose(minus["join_projection_coefficient"], -1.0 / 8.0)
    assert np.isclose(zero["join_projection_coefficient"], 0.0)


def test_exact_s7_moments_and_projection_residual() -> None:
    result = formation_join_quadrupole([1, 0, 0, 0, 0, 0, 0, 0])
    assert np.isclose(result["formation_norm_squared"], 7.0 / 320.0)
    assert np.isclose(result["join_norm_squared"], 1.0 / 5.0)
    assert np.isclose(result["overlap"], 1.0 / 40.0)
    assert np.isclose(result["orthogonal_residual_norm_squared"], 3.0 / 160.0)


def test_independent_monte_carlo_confirms_sphere_moments() -> None:
    result = sphere_moment_monte_carlo(
        [1, 0, 0, 0, 0, 0, 0, 0], samples=120_000, seed=1524
    )
    assert abs(result["formation_norm_squared"] - 7.0 / 320.0) < 8e-4
    assert abs(result["join_norm_squared"] - 1.0 / 5.0) < 3e-3
    assert abs(result["overlap"] - 1.0 / 40.0) < 8e-4


def test_join_friedrichs_spectrum_and_l2_mode() -> None:
    result = join_invariant_scalar_spectrum(4)
    assert [row["eigenvalue"] for row in result["modes"]] == [0, 16, 40, 72, 112]
    assert result["first_nonconstant_mode"]["S7_scalar_degree"] == 2
    assert result["self_adjoint"]


def test_exact_radial_eta_strain_series_and_critical_constraint_response() -> None:
    strain = radial_eta_strain_series()
    assert np.isclose(strain["quadratic_t_squared_coefficient"], 427.0 / 27.0)
    assert np.isclose(strain["quadratic_constant"], -343.0 / 54.0)
    radius = (343.0 / 5.0) ** (1.0 / 6.0)
    response = conformal_l2_hamiltonian_response(
        radius=radius, kappa1=1.0, zeta=1.0
    )
    assert np.isclose(response["critical_relation_residual"], 0.0, atol=2e-13)
    assert np.isclose(response["a_over_q_squared"], 343.0 / 1728.0)
    assert np.isclose(
        response["mixed_d3_static_action_da_dq2_per_unit_round_S7"],
        -7203.0 / (20.0 * radius),
    )
    assert response["response_nonzero"]
    assert response["time_dependent_momentum_constraint_included"] is False


def test_balanced_orientation_has_no_forced_join_response() -> None:
    radius = (343.0 / 5.0) ** (1.0 / 6.0)
    response = conformal_l2_hamiltonian_response(
        radius=radius, kappa1=1.0, zeta=0.0
    )
    assert response["a_over_q_squared"] == 0.0
    assert response["response_nonzero"] is False


def test_critical_shift_constraint_freezes_onset_shape_velocity() -> None:
    radius = (343.0 / 5.0) ** (1.0 / 6.0)
    result = l2_unitary_gauge_shift_reduction(radius=radius, kappa1=1.0)
    assert np.isclose(result["eta_shift_susceptibility"], 3.0)
    assert np.isclose(result["C"], 0.0, atol=2e-12)
    assert result["critical_shift_square_cancellation"]
    assert result["critical_shift_equation"] == "a_dot=0"
    assert result["propagating_canonical_a_at_this_slice"] is False
    assert result["reduced_a_dot_squared_coefficient"] is None


def test_formed_radius_side_lifts_shift_degeneracy_with_positive_kinetic() -> None:
    radius = 1.01 * (343.0 / 5.0) ** (1.0 / 6.0)
    result = l2_unitary_gauge_shift_reduction(radius=radius, kappa1=1.0)
    assert result["critical_shift_square_cancellation"] is False
    assert result["shift_per_a_dot"] is not None
    assert result["reduced_a_dot_squared_coefficient"] > 0.0
    assert result["positive_reduced_kinetic"]


def test_actual_nonidentity_formed_eta_pullback_lifts_l2_degeneracy() -> None:
    coarse = formed_branch_l2_legendre_reduction(1.01, quadrature_points=160)
    fine = formed_branch_l2_legendre_reduction(1.01, quadrature_points=320)
    assert fine["orbit_spaces_identified"] is False
    assert fine["q_fourier"] > 0.0
    assert fine["total_shift_coefficient"] < 0.0
    assert fine["reduced_a_dot_squared_coefficient"] > 0.0
    assert fine["positive_physical_Legendre_direction"]
    assert fine["moving_cross_kinetic_included"] is False
    assert np.isclose(
        coarse["reduced_a_dot_squared_coefficient"],
        fine["reduced_a_dot_squared_coefficient"],
        rtol=2e-10,
    )


def test_radial_and_join_profiles_are_not_identified_off_identity() -> None:
    result = symmetry_reduction_firewall()
    assert result["common_round_map"] == "eta_identity_on_S7"
    assert result["nonlinear_profile_identification_allowed"] is False
    assert result["full_7d_field_equation_required_after_projection"]


def test_sigma_zero_drive_transfer_is_identity_and_symplectic() -> None:
    result = sigma_homoclinic_transfer(
        baseline_frequency=1.0, drive_amplitude=0.0, cutoff=12.0
    )
    assert result["solver_success"]
    assert np.isclose(result["determinant"], 1.0, atol=2e-9)
    assert np.allclose(result["interaction_picture_matrix"], np.eye(2), atol=2e-9)
    assert np.isclose(result["log_squeezing_gain"], 0.0, atol=2e-9)


def test_sigma_driven_transfer_has_reciprocal_singular_values() -> None:
    result = sigma_homoclinic_transfer(
        baseline_frequency=1.0, drive_amplitude=8.0, cutoff=12.0
    )
    values = result["singular_values"]
    assert result["instantaneous_negative_interval_present"]
    assert np.isclose(result["determinant"], 1.0, atol=2e-9)
    assert np.isclose(values[0] * values[1], 1.0, atol=2e-9)
    assert result["log_squeezing_gain"] > 0.0
    assert result["nonlinear_saturation_reached"] is None


def test_completion_advances_to_coupled_l2_source_vertex() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["formation_to_join_quadrupole"][
        "physical_source_vertex_coefficient_derived"
    ] is False
    assert len(payload["Hindsight_20_20"]["OPEN"]) == 1


def test_materialization_is_deterministic(tmp_path) -> None:
    path = materialize(tmp_path)
    first = path.read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
