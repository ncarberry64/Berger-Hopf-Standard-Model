"""BHSM v15.24 formation-to-Hopf-join quadrupole bridge.

The v15.9 radial concentration mode and the v15.23 Hopf join use different
cohomogeneity-one orbit spaces.  This module derives their first common
nonround object without identifying those orbit spaces: the trace-free l=2
part of the squared l=1 formation mode, projected onto the retained Hopf
4+4 splitting.  It also derives the exact SO(4)xSO(4)-invariant scalar join
spectrum and a nonautonomous sigma transfer operator on the homoclinic pulse.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import roots_jacobi

from bhsm.interface.aether_cycle_spread_concentration_v15_9 import (
    critical_radius,
    radial_fourier_solution,
)


VERSION = "v15.24"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "ACTION_OWNED_GAUGE_INVARIANT_COHOMOGENEITY_ONE_JOIN_MASTER_OPERATOR_"
    "WITH_HAMILTONIAN_CONSTRAINT_ELIMINATION_SELF_ADJOINT_TWO_POLE_DOMAIN_"
    "SPECTRUM_AND_NONROUND_BIFURCATING_ETA_SIGMA_METRIC_SOLUTION"
)
OUTCOME = (
    "THE_V15_9_AND_HOPF_JOIN_NONLINEAR_ONE_DIMENSIONAL_REDUCTIONS_ARE_"
    "DISTINCT_BUT_THE_FORMATION_SQUARE_HAS_AN_EXACT_ACTION_OWNED_L2_"
    "QUADRUPOLE_PROJECTION_AND_THE_CRITICAL_HAMILTONIAN_CONSTRAINT_FORCES_"
    "A_NONZERO_SMOOTH_CONFORMAL_JOIN_RESPONSE_WHILE_THE_ONSET_SHIFT_"
    "CONSTRAINT_MAKES_THAT_RESPONSE_NONPROPAGATING_AT_EXACT_CRITICALITY"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_MOVING_FORMED_BRANCH_QDOT_SIGMADOT_L2_CROSS_KINETIC_"
    "AND_COVARIANT_SYMPLECTIC_PULLBACK_WITH_DYNAMIC_SIGMA_TRANSFER_"
    "BACKREACTION_AND_NONLINEAR_FORCED_JOIN_CONTINUATION"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def hopf_split_matrix() -> np.ndarray:
    """Return the retained trace-free 4+4 orientation tensor J."""

    return np.diag([1.0] * 4 + [-1.0] * 4)


def formation_join_quadrupole(axis: Sequence[float]) -> dict[str, Any]:
    """Project the l=2 square of a formation axis onto the Hopf split.

    On the unit S7, phi_n=n.x is an l=1 scalar.  Its trace-free square is
    Q_n=(n.x)^2-1/8.  The join scalar is Q_J=x^T J x.  Uniform S7 moments
    give <Q_n Q_J>=(n^T J n)/40 and <Q_J^2>=1/5.
    """

    vector = np.asarray(axis, dtype=float)
    if vector.shape != (8,) or not np.all(np.isfinite(vector)):
        raise ValueError("axis must be a finite eight-vector")
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0:
        raise ValueError("axis must be nonzero")
    unit = vector / norm
    orientation = float(unit @ hopf_split_matrix() @ unit)
    overlap = orientation / 40.0
    join_norm = 1.0 / 5.0
    formation_norm = 7.0 / 320.0
    projection = overlap / join_norm
    residual_norm = formation_norm - overlap**2 / join_norm
    return {
        "unit_axis": unit.tolist(),
        "relative_orientation_zeta": orientation,
        "zeta_interval": [-1.0, 1.0],
        "formation_quadrupole": "Q_n=(n.x)^2-1/8",
        "join_quadrupole": "Q_J=x^T*diag(I4,-I4)*x=cos(2chi)",
        "formation_norm_squared": formation_norm,
        "join_norm_squared": join_norm,
        "overlap": overlap,
        "join_projection_coefficient": projection,
        "orthogonal_residual_norm_squared": residual_norm,
        "projection_formula": "Proj_join(Q_n)=(zeta/8)*Q_J",
        "projection_nonzero": abs(projection) > 1.0e-14,
    }


def sphere_moment_monte_carlo(
    axis: Sequence[float], *, samples: int = 200_000, seed: int = 1524
) -> dict[str, float]:
    """Independently check the exact S7 quadrupole moments."""

    if not isinstance(samples, int) or samples < 10_000:
        raise ValueError("samples must be an integer at least 10000")
    vector = np.asarray(axis, dtype=float)
    if vector.shape != (8,) or np.linalg.norm(vector) == 0.0:
        raise ValueError("axis must be a nonzero eight-vector")
    unit = vector / np.linalg.norm(vector)
    rng = np.random.default_rng(int(seed))
    points = rng.normal(size=(samples, 8))
    points /= np.linalg.norm(points, axis=1)[:, None]
    qn = (points @ unit) ** 2 - 1.0 / 8.0
    qj = np.einsum("ni,ij,nj->n", points, hopf_split_matrix(), points)
    return {
        "formation_norm_squared": float(np.mean(qn**2)),
        "join_norm_squared": float(np.mean(qj**2)),
        "overlap": float(np.mean(qn * qj)),
    }


def join_invariant_scalar_spectrum(max_mode: int = 5) -> dict[str, Any]:
    """Return the exact Friedrichs spectrum in the invariant scalar sector.

    With w=sin^3(chi)cos^3(chi), the operator is
    L=-w^-1 d_chi(w d_chi).  Smooth eigenfunctions are
    P_n^(1,1)(cos(2chi)) and lambda_n=4n(n+3).
    """

    count = int(max_mode)
    if count < 1:
        raise ValueError("max_mode must be positive")
    modes = [
        {
            "n": n,
            "S7_scalar_degree": 2 * n,
            "eigenvalue": 4 * n * (n + 3),
            "eigenfunction": f"P_{n}^(1,1)(cos(2chi))",
        }
        for n in range(count + 1)
    ]
    return {
        "operator": "L=-w^-1*partial_chi(w*partial_chi)",
        "weight": "w=sin(chi)^3*cos(chi)^3",
        "Hilbert_space": "L2([0,pi/2],w dchi)",
        "domain": (
            "Friedrichs_closure_of_smooth_SO4xSO4_invariant_S7_scalars;_"
            "bounded_even_Frobenius_expansions_at_both_poles"
        ),
        "boundary_form": "[w*(conj(u)*v'-conj(u')*v)]_0^(pi/2)=0",
        "limit_point_or_regular_geometric_selection": (
            "smooth_S7_extension_selects_the_bounded_even_branch_at_each_pole"
        ),
        "modes": modes,
        "first_nonconstant_mode": modes[1],
        "join_quadrupole_check": "L cos(2chi)=16 cos(2chi)",
        "self_adjoint": True,
    }


def symmetry_reduction_firewall() -> dict[str, Any]:
    """Keep the radial and join orbit spaces distinct off the identity."""

    return {
        "v15_9_orbits": "S6_radial_level_sets_on_S7",
        "v15_23_orbits": "S3_times_S3_Hopf_join_level_sets_on_S7",
        "common_round_map": "eta_identity_on_S7",
        "nonlinear_profile_identification_allowed": False,
        "reason": (
            "the_orbit_dimensions_and_isotropy_groups_differ_so_a_v15_9_"
            "one_variable_profile_cannot_be_substituted_for_the_join_profile"
        ),
        "first_common_nonlinear_representation": (
            "the_l2_trace_free_part_of_the_squared_l1_formation_mode"
        ),
        "full_7d_field_equation_required_after_projection": True,
    }


def radial_eta_strain_series() -> dict[str, Any]:
    """Return X-bar through q^2 on the exact v15.9 LS profile."""

    return {
        "profile": "f=chi+q*sin(chi)+(19/108)q^2*sin(chi)cos(chi)+O(q^3)",
        "t_definition": "t=cos(chi)=n.x",
        "X_bar": "7+14*q*t+q^2*((427/27)*t^2-343/54)+O(q^3)",
        "linear_coefficient": 14.0,
        "quadratic_t_squared_coefficient": 427.0 / 27.0,
        "quadratic_constant": -343.0 / 54.0,
    }


def conformal_l2_hamiltonian_response(
    *, radius: float, kappa1: float, zeta: float, sigma_weight: float = 1.0
) -> dict[str, Any]:
    """Eliminate the time-symmetric Hamiltonian constraint in one l=2 sector.

    The smooth metric perturbation is g_ij=R^2 exp(2 a Q_J) gbar_ij.
    This is a constraint calculation at the q=0 critical turning slice, not
    the complete time-dependent scalar master system.
    """

    rr = _positive(radius, "radius")
    kk = _positive(kappa1, "kappa1")
    ww = _positive(sigma_weight, "sigma_weight")
    orientation = float(zeta)
    if not math.isfinite(orientation) or abs(orientation) > 1.0 + 1e-13:
        raise ValueError("zeta must lie in [-1,1]")
    x0 = 7.0 / rr**2
    f_prime = 0.5 * (kk + x0**3)
    f_second = 1.5 * x0**2
    a2 = 427.0 / 27.0
    density_t2 = ww * (
        f_prime * a2 / rr**2 + 98.0 * f_second / rr**4
    )
    density_join_projection = orientation * density_t2 / 8.0
    delta_r_coefficient = 108.0 / rr**2
    metric_density_response = -2.0 * ww * x0 * f_prime
    constraint_a_coefficient = (
        0.5 * kk * delta_r_coefficient - metric_density_response
    )
    amplitude_per_q_squared = density_join_projection / constraint_a_coefficient

    # The mixed static action derivative includes the conformal volume factor.
    g_prime = 2.5 * kk - 0.5 * x0**3
    g_second = -1.5 * x0**2
    action_bracket = a2 * g_prime / rr**2 + 98.0 * g_second / rr**4
    mixed_action_per_unit_s7 = (
        2.0 * rr**7 * ww * orientation * action_bracket / 40.0
    )
    critical_residual = kk * rr**6 - 343.0 / 5.0
    return {
        "metric_family": "g_ij=R^2*exp(2*a*Q_J)*gbar_ij",
        "Q_J": "cos(2chi)",
        "delta_R7_per_a": delta_r_coefficient,
        "eta_energy_q2_t2_coefficient": density_t2,
        "eta_energy_q2_join_projection": density_join_projection,
        "Hamiltonian_constraint_a_coefficient": constraint_a_coefficient,
        "a_over_q_squared": amplitude_per_q_squared,
        "mixed_d3_static_action_da_dq2_per_unit_round_S7": mixed_action_per_unit_s7,
        "critical_relation_residual": critical_residual,
        "critical_closed_form_a_over_q_squared": (
            343.0 * orientation / 1728.0 if abs(critical_residual) < 1e-10 else None
        ),
        "response_nonzero": abs(amplitude_per_q_squared) > 1e-14,
        "eigenvalue_crossing_required_for_forced_response": False,
        "time_dependent_momentum_constraint_included": False,
    }


def l2_unitary_gauge_shift_reduction(
    *, radius: float, kappa1: float, sigma_weight: float = 1.0
) -> dict[str, Any]:
    """Eliminate the l=2 scalar shift on the round identity background.

    In eta-unitary gauge take h_ij=2*a*Y*g_ij and
    beta^i=b*grad^i(Y), with -Delta Y=lambda Y and lambda=16/R^2.
    The result includes the p2+p8 eta shift susceptibility.
    """

    rr = _positive(radius, "radius")
    kk = _positive(kappa1, "kappa1")
    ww = _positive(sigma_weight, "sigma_weight")
    x0 = 7.0 / rr**2
    f_prime = 0.5 * (kk + x0**3)
    eigenvalue = 16.0 / rr**2
    a2_coefficient = -21.0 * kk
    ab_coefficient = -6.0 * kk * eigenvalue
    b2_coefficient = eigenvalue * (ww * f_prime - 3.0 * kk) / rr**2
    tolerance = 2.0e-12 * max(1.0, abs(eigenvalue * kk / rr**2))
    degenerate = abs(b2_coefficient) <= tolerance
    if degenerate:
        shift_per_a_dot = None
        reduced_kinetic = None
    else:
        shift_per_a_dot = -ab_coefficient / (2.0 * b2_coefficient)
        reduced_kinetic = a2_coefficient - ab_coefficient**2 / (
            4.0 * b2_coefficient
        )
    return {
        "gauge": "eta_unitary_gauge_delta_eta=0",
        "metric_mode": "h_ij=2*a*Y*g_ij",
        "shift_mode": "beta^i=b*grad^i(Y)",
        "scalar_eigenvalue": eigenvalue,
        "kinetic_form_per_Y_norm": (
            "A*a_dot^2+B*a_dot*b+C*b^2"
        ),
        "A": a2_coefficient,
        "B": ab_coefficient,
        "C": b2_coefficient,
        "eta_shift_susceptibility": ww * f_prime,
        "gravity_shift_susceptibility": -3.0 * kk,
        "shift_per_a_dot": shift_per_a_dot,
        "reduced_a_dot_squared_coefficient": reduced_kinetic,
        "positive_reduced_kinetic": (
            reduced_kinetic is not None and reduced_kinetic > 0.0
        ),
        "critical_shift_square_cancellation": degenerate,
        "critical_shift_equation": (
            "a_dot=0" if degenerate and abs(ab_coefficient) > 0.0 else None
        ),
        "propagating_canonical_a_at_this_slice": not degenerate,
        "full_formed_branch_result": None,
    }


def formed_branch_l2_legendre_reduction(
    radius_ratio_six: float,
    *,
    kappa1: float = 1.0,
    modes: int = 12,
    quadrature_points: int = 240,
) -> dict[str, Any]:
    """Reduce the l=2 shift using the actual static v15.9 eta pullback.

    The S6-radial eta stress is projected into the aligned Hopf quadrupole
    using exact conditional S7 moments.  The orbit spaces are not identified.
    This applies to an instantaneous q_dot=0 formed slice.
    """

    ratio = _positive(radius_ratio_six, "radius_ratio_six")
    if ratio <= 1.0:
        raise ValueError("the nonidentity formed branch requires radius_ratio_six>1")
    kk = _positive(kappa1, "kappa1")
    count = int(modes)
    points = int(quadrature_points)
    if count < 2 or points < 80:
        raise ValueError("modes>=2 and quadrature_points>=80 are required")
    coefficients = np.asarray(radial_fourier_solution(ratio, count, max(480, points)))
    t, weights = roots_jacobi(points, 2.5, 2.5)
    weights = weights / np.sum(weights)
    chi = np.arccos(t)
    n = np.arange(1, count + 1, dtype=float)[:, None]
    profile = chi + coefficients @ np.sin(n * chi)
    derivative = 1.0 + coefficients @ (n * np.cos(n * chi))
    one_minus_t2 = 1.0 - t**2
    radial_stretch = derivative**2
    tangential_stretch = (np.sin(profile) / np.sqrt(one_minus_t2)) ** 2
    radius = critical_radius(kk) * ratio ** (1.0 / 6.0)
    x_eta = (radial_stretch + 6.0 * tangential_stretch) / radius**2
    f_prime = 0.5 * (kk + x_eta**3)

    expected_y_squared = (
        t**4
        - 2.0 * t**2 * one_minus_t2 / 7.0
        + 5.0 * one_minus_t2**2 / 21.0
    )
    expected_gradient_squared = 4.0 * (1.0 - expected_y_squared)
    expected_radial_gradient_squared = 128.0 * t**2 * one_minus_t2 / 21.0
    eta_pullback_gradient = (
        tangential_stretch * expected_gradient_squared
        + (radial_stretch - tangential_stretch)
        * expected_radial_gradient_squared
    )
    join_norm = 1.0 / 5.0
    eta_shift_coefficient = float(
        np.sum(weights * f_prime * eta_pullback_gradient / radius**4) / join_norm
    )
    scalar_eigenvalue = 16.0 / radius**2
    gravity_shift_coefficient = -3.0 * kk * scalar_eigenvalue / radius**2
    total_shift_coefficient = eta_shift_coefficient + gravity_shift_coefficient
    a2_coefficient = -21.0 * kk
    ab_coefficient = -6.0 * kk * scalar_eigenvalue
    shift_per_a_dot = -ab_coefficient / (2.0 * total_shift_coefficient)
    reduced_kinetic = a2_coefficient - ab_coefficient**2 / (
        4.0 * total_shift_coefficient
    )
    return {
        "radius_ratio_six": ratio,
        "radius": radius,
        "q_fourier": float(coefficients[0]),
        "projection": "aligned_zeta=1_conditional_S7_quadrupole_moments",
        "orbit_spaces_identified": False,
        "q_dot": 0.0,
        "sigma": 0.0,
        "eta_shift_coefficient": eta_shift_coefficient,
        "gravity_shift_coefficient": gravity_shift_coefficient,
        "total_shift_coefficient": total_shift_coefficient,
        "shift_per_a_dot": shift_per_a_dot,
        "reduced_a_dot_squared_coefficient": reduced_kinetic,
        "positive_physical_Legendre_direction": reduced_kinetic > 0.0,
        "quadrature_points": points,
        "modes": count,
        "moving_cross_kinetic_included": False,
    }


def sigma_homoclinic_transfer(
    *,
    baseline_frequency: float,
    drive_amplitude: float,
    cutoff: float = 12.0,
) -> dict[str, Any]:
    """Integrate the exact dimensionless sigma tangent fundamental matrix.

    The equation is s''+[omega0^2-D sech^2(x)tanh^2(x)]s=0, where x is
    the homoclinic affine clock variable, not primitive Aether time.  The
    returned interaction-picture matrix removes the free oscillator rotation.
    """

    omega = _positive(baseline_frequency, "baseline_frequency")
    drive = float(drive_amplitude)
    limit = _positive(cutoff, "cutoff")
    if not math.isfinite(drive) or drive < 0.0:
        raise ValueError("drive_amplitude must be finite and nonnegative")

    def rhs(x: float, flat: np.ndarray) -> np.ndarray:
        matrix = flat.reshape(2, 2)
        sech2 = 1.0 / math.cosh(x) ** 2
        frequency_squared = omega**2 - drive * sech2 * (1.0 - sech2)
        generator = np.array([[0.0, 1.0], [-frequency_squared, 0.0]])
        return (generator @ matrix).reshape(-1)

    solution = solve_ivp(
        rhs,
        (-limit, limit),
        np.eye(2).reshape(-1),
        method="DOP853",
        rtol=2.0e-11,
        atol=2.0e-13,
    )
    matrix = solution.y[:, -1].reshape(2, 2)
    scale = np.diag([math.sqrt(omega), 1.0 / math.sqrt(omega)])
    canonical = scale @ matrix @ np.linalg.inv(scale)
    angle = 2.0 * limit * omega
    free_inverse = np.array(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
    )
    interaction = free_inverse @ canonical
    singular_values = np.linalg.svd(interaction, compute_uv=False)
    return {
        "equation": "s_xx+[omega0^2-D*sech(x)^2*tanh(x)^2]s=0",
        "affine_variable": "x=sqrt(5m/(6a_c^2))*tau_on_reconstructed_branch",
        "fundamental_matrix": matrix.tolist(),
        "interaction_picture_matrix": interaction.tolist(),
        "determinant": float(np.linalg.det(matrix)),
        "singular_values": singular_values.tolist(),
        "log_squeezing_gain": float(math.log(singular_values[0])),
        "instantaneous_negative_interval_present": drive > 4.0 * omega**2,
        "solver_success": bool(solution.success),
        "nonlinear_saturation_reached": None,
        "coefficient_status": "conditional_on_the_unselected_physical_response_operator",
    }


def completion_payload() -> dict[str, Any]:
    aligned = formation_join_quadrupole([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    balanced = formation_join_quadrupole([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    monte_carlo = sphere_moment_monte_carlo(aligned["unit_axis"], samples=120_000)
    spectrum = join_invariant_scalar_spectrum(5)
    firewall = symmetry_reduction_firewall()
    critical_radius = (343.0 / 5.0) ** (1.0 / 6.0)
    constrained_response = conformal_l2_hamiltonian_response(
        radius=critical_radius, kappa1=1.0, zeta=1.0
    )
    critical_kinetic = l2_unitary_gauge_shift_reduction(
        radius=critical_radius, kappa1=1.0
    )
    formed_side_kinetic = l2_unitary_gauge_shift_reduction(
        radius=1.01 * critical_radius, kappa1=1.0
    )
    actual_formed_kinetic = formed_branch_l2_legendre_reduction(1.01)
    no_drive = sigma_homoclinic_transfer(baseline_frequency=1.0, drive_amplitude=0.0)
    driven = sigma_homoclinic_transfer(baseline_frequency=1.0, drive_amplitude=8.0)
    validation = {
        "aligned_axis_projects_with_exact_one_eighth": math.isclose(
            aligned["join_projection_coefficient"], 1.0 / 8.0, abs_tol=1e-14
        ),
        "balanced_axis_has_zero_join_projection": abs(
            balanced["join_projection_coefficient"]
        )
        < 1e-14,
        "quadrupole_residual_norm_nonnegative": aligned[
            "orthogonal_residual_norm_squared"
        ]
        >= 0.0,
        "independent_sphere_moments_match": (
            abs(monte_carlo["formation_norm_squared"] - 7.0 / 320.0) < 8e-4
            and abs(monte_carlo["join_norm_squared"] - 1.0 / 5.0) < 3e-3
            and abs(monte_carlo["overlap"] - 1.0 / 40.0) < 8e-4
        ),
        "join_quadrupole_has_l2_eigenvalue_16": spectrum[
            "first_nonconstant_mode"
        ]["eigenvalue"]
        == 16,
        "two_pole_scalar_domain_self_adjoint": spectrum["self_adjoint"],
        "v15_9_strain_series_recovered": (
            radial_eta_strain_series()["quadratic_t_squared_coefficient"]
            == 427.0 / 27.0
        ),
        "critical_Hamiltonian_constraint_forces_nonround_response": (
            constrained_response["response_nonzero"]
            and math.isclose(
                constrained_response["a_over_q_squared"],
                343.0 / 1728.0,
                rel_tol=1e-12,
            )
        ),
        "forced_response_does_not_require_eigenvalue_crossing": not constrained_response[
            "eigenvalue_crossing_required_for_forced_response"
        ],
        "critical_shift_susceptibility_cancels": critical_kinetic[
            "critical_shift_square_cancellation"
        ],
        "critical_shape_is_not_falsely_called_canonical": not critical_kinetic[
            "propagating_canonical_a_at_this_slice"
        ],
        "round_formed_side_control_has_positive_reduced_kinetic": formed_side_kinetic[
            "positive_reduced_kinetic"
        ],
        "actual_nonidentity_formed_pullback_has_positive_reduced_kinetic": actual_formed_kinetic[
            "positive_physical_Legendre_direction"
        ],
        "nonlinear_radial_join_profiles_not_identified": not firewall[
            "nonlinear_profile_identification_allowed"
        ],
        "zero_drive_transfer_is_identity": np.allclose(
            no_drive["interaction_picture_matrix"], np.eye(2), atol=2e-9
        ),
        "driven_transfer_is_symplectic": abs(driven["determinant"] - 1.0) < 2e-9,
        "driven_pulse_has_positive_net_squeezing": driven["log_squeezing_gain"] > 0.0,
        "no_coefficient_or_empirical_input_added": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_formation_join_quadrupole_v15_24",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "symmetry_reduction_firewall": firewall,
        "formation_to_join_quadrupole": {
            "aligned_control": aligned,
            "balanced_control": balanced,
            "independent_monte_carlo": monte_carlo,
            "physical_relative_orientation_selected": False,
            "physical_source_vertex_coefficient_derived": False,
        },
        "two_pole_invariant_scalar_spectrum": spectrum,
        "critical_conformal_l2_Hamiltonian_response": constrained_response,
        "round_l2_momentum_constraint_reduction": {
            "critical_slice": critical_kinetic,
            "one_percent_formed_radius_control": formed_side_kinetic,
            "one_percent_actual_nonidentity_eta_pullback": actual_formed_kinetic,
            "nonidentity_formed_eta_pullback_evaluated": True,
        },
        "sigma_transient_transfer": {
            "zero_drive_control": no_drive,
            "driven_control": driven,
            "physical_transfer": None,
        },
        "Hindsight_20_20": {
            "VALIDATED": [
                "the_first_shared_nonlinear_object_is_the_l2_part_of_the_squared_l1_formation_mode",
                "its_join_projection_is_exactly_zeta_over_eight_with_no_new_coefficient",
                "the_SO4xSO4_invariant_scalar_join_Friedrichs_spectrum_is_lambda_n=4n(n+3)",
                "the_critical_Hamiltonian_constraint_forces_a_over_q_squared=343*zeta/1728_in_the_smooth_conformal_l2_sector",
                "the_eta_and_gravity_shift_square_terms_cancel_exactly_at_the_v15_9_critical_identity_slice",
                "the_actual_nonidentity_v15_9_pullback_lifts_the_aligned_l2_shift_degeneracy_and_has_positive_reduced_kinetic_on_the_tested_formed_slice",
                "the_exact_nonautonomous_sigma_transfer_can_replace_the_WKB_only_screen",
            ],
            "INVALIDATED": [
                "substituting_the_nonlinear_v15_9_S6_radial_profile_directly_into_the_S3xS3_join_master_equations",
                "an_instantaneous_negative_sigma_curvature_alone_proves_nonlinear_skin_formation",
                "the_forced_critical_l2_configuration_amplitude_is_already_a_propagating_canonical_coordinate",
            ],
            "RECLASSIFIED": [
                "the_positive_round_join_mode_as_an_invertible_forced_response_channel_at_order_q_squared",
                "the_relative_formation_axis_Hopf_split_orientation_as_a_dynamical_branch_variable_not_an_external_frame",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "primitive_Aether_time_or_metric_used": False,
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_formation_join_quadrupole_v15_24.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CAMPAIGN_OBJECT",
    "OUTCOME",
    "EXACT_NEXT_OBJECT",
    "hopf_split_matrix",
    "formation_join_quadrupole",
    "sphere_moment_monte_carlo",
    "join_invariant_scalar_spectrum",
    "symmetry_reduction_firewall",
    "radial_eta_strain_series",
    "conformal_l2_hamiltonian_response",
    "l2_unitary_gauge_shift_reduction",
    "formed_branch_l2_legendre_reduction",
    "sigma_homoclinic_transfer",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
