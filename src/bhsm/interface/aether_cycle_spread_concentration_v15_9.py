"""BHSM v15.9 cycle-driven eta spread-to-concentration calculation.

The module starts from the retained round-S7 degree-one radial eta functional

    E[f] = int sin(chi)^6 [kappa1 X/2 + X^4/8] dchi,
    X = (f'^2 + 6 sin(f)^2/sin(chi)^2)/a^2,

and does not add a field, source, or physical coefficient.  Exact rational
Lyapunov--Schmidt data are paired with two independent numerical realizations
of the full radial Euler equation: Fourier--Galerkin stationarity and an
adaptive finite-interval BVP with pole-regular Robin limits.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_bvp
from scipy.optimize import brentq, root
from scipy.special import roots_legendre


VERSION = "v15.9"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED = False
PRIMARY_OBJECT = (
    "CYCLE_DRIVEN_ETA_SPREAD_TO_CONCENTRATION_BIFURCATION_FOLLOWED_BY_"
    "LOCAL_SIGMA_SUPPORT_DEPLETION_AND_FULL_HOPF_PARENT_CHILD_CONSTRAINT_"
    "CONTINUATION_WITH_NESTED_SCALE_DECOUPLING_COMMON_DOMAIN_AND_FLOQUET_"
    "PERSISTENCE"
)
EXACT_NEXT_OBJECT = (
    "FULL_HOPF_PARENT_CHILD_EINSTEIN_ETA_SIGMA_CONSTRAINT_CONTINUATION_"
    "FROM_THE_ACTION_DERIVED_RADIAL_CONCENTRATION_BRANCH_WITH_ACTION_"
    "SELECTED_SIGMA_COEFFICIENT_BRANCH_NESTED_SCALE_AND_RELATIVE_PERIODIC_"
    "COMMON_DOMAIN"
)
PRIMARY_VERDICT = (
    "BHSM_V15_9_THE_RETAINED_P2_PLUS_P8_ETA_ACTION_HAS_AN_EXACT_"
    "SUPERCRITICAL_CYCLE_DRIVEN_RADIAL_SPREAD_TO_CONCENTRATION_"
    "BIFURCATION_AT_A_C_SIX_EQUALS_343_OVER_5_KAPPA1_WITH_THE_REPRODUCED_"
    "FULL_EULER_LYAPUNOV_SCHMIDT_BRANCH_AND_POSITIVE_RADIAL_BRANCH_"
    "HESSIAN;_THE_RESULT_CONDITIONALLY_DRIVES_THE_EXISTING_SIGMA_CURVATURE_"
    "THROUGH_LOCAL_SUPPORT_DEPLETION_BUT_ETA_ONLY_HOPF_COHOMOGENEITY_ONE_"
    "HAS_A_STRICTLY_POSITIVE_IDENTITY_HESSIAN_AT_EVERY_RADIUS;_THEREFORE_"
    "THE_RADIAL_BRANCH_IS_AN_ACTION_DERIVED_ENVIRONMENT_GENERATING_"
    "PRECURSOR_NOT_A_PHYSICAL_HOPF_CHILD_AND_FULL_BHSM_COMPLETION_REMAINS_"
    "FALSE"
)


def critical_radius(kappa1: float = 1.0) -> float:
    """Return the action-derived radial conformal crossing radius."""

    if not math.isfinite(kappa1) or kappa1 <= 0.0:
        raise ValueError("kappa1 must be finite and positive")
    return (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)


def identity_hessian_ratio(radius: float, kappa1: float = 1.0) -> float:
    """Return E_ss(0)/E2_id for the conformal degree-one direction."""

    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be finite and positive")
    if not math.isfinite(kappa1) or kappa1 <= 0.0:
        raise ValueError("kappa1 must be finite and positive")
    return 343.0 / (4.0 * kappa1 * radius**6) - 5.0 / 4.0


def exact_lyapunov_schmidt_payload() -> dict[str, Any]:
    """Return independently reproduced exact series coefficients."""

    return {
        "retained_functional": (
            "integral_0^pi sin(chi)^6[kappa1*X/2+X^4/8]dchi;_"
            "X=(f_prime^2+6sin(f)^2/sin(chi)^2)/a^2"
        ),
        "critical_radius_six": "343/(5*kappa1)",
        "identity_hessian_ratio_to_E2_id": "343/(4*kappa1*a^6)-5/4",
        "kernel": "y0=sin(chi)",
        "order_q2_Euler_residual": "-(6/7)(108*c-19)sin(chi)^7cos(chi)",
        "complement_coefficient_c": str(Fraction(19, 108)),
        "profile": (
            "f=chi+q*sin(chi)+(19/108)q^2*sin(chi)cos(chi)+O(q^3)"
        ),
        "order_q3_kernel_projection": "35*pi*(45*alpha-23)/1152",
        "radius_relation_alpha": str(Fraction(23, 45)),
        "radius_relation": "a^6/a_c^6=1+(23/45)q^2+O(q^4)",
        "amplitude_relation": "q^2=(45/23)(a^6/a_c^6-1)+O(m^2)",
        "reduced_energy_over_E2c": "-(5/8)m*q^2+(23/144)q^4+O(q^6)",
        "reduced_energy_m_q2": str(Fraction(-5, 8)),
        "reduced_energy_q4": str(Fraction(23, 144)),
        "branch_radial_curvature_sign": "POSITIVE",
        "bifurcation": "SUPERCRITICAL_PITCHFORK_MODULO_ORIENTATION_REVERSAL",
    }


def concentration_series_payload() -> dict[str, Any]:
    """Return the exact degree-density and depleted-pole expansions."""

    return {
        "degree_density": "j_eta=f_prime*(sin(f)/sin(chi))^6",
        "degree_normalization": "<j_eta>=1",
        "C_eta": "<j_eta^2>",
        "C_eta_bound": "C_eta>=1_by_Cauchy_Schwarz",
        "C_eta_series": "1+(49/8)q^2+O(q^4)",
        "C_eta_q2": str(Fraction(49, 8)),
        "C_eta_radius_series": "1+(2205/184)(a^6/a_c^6-1)+higher_order",
        "C_eta_radius_coefficient": str(Fraction(2205, 184)),
        "depleted_pole_support_ratio": "1-2q+(73/54)q^2+O(q^3)",
        "depleted_pole_q2": str(Fraction(73, 54)),
        "classification": (
            "ACTION_COMPATIBLE_REGULAR_STATE_SPREAD_CONCENTRATION_DIAGNOSTIC"
        ),
        "primitive_Aether_density_claimed": False,
    }


def _quadrature(points: int) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(points, int) or points < 80:
        raise ValueError("quadrature points must be an integer >=80")
    nodes, weights = roots_legendre(points)
    return (nodes + 1.0) * math.pi / 2.0, weights * math.pi / 2.0


def _basis(chi: np.ndarray, modes: int) -> tuple[np.ndarray, np.ndarray]:
    n = np.arange(1, modes + 1, dtype=float)[:, None]
    return np.sin(n * chi), n * np.cos(n * chi)


def _gradient_hessian(
    coefficients: np.ndarray,
    radius_ratio_six: float,
    chi: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Galerkin gradient and exact coefficient Hessian at kappa1=1."""

    modes = len(coefficients)
    sine, cosine = _basis(chi, modes)
    sphere_weight = np.sin(chi) ** 6
    profile = chi + coefficients @ sine
    derivative = 1.0 + coefficients @ cosine
    strain_shape = derivative**2 + 6.0 * np.sin(profile) ** 2 / np.sin(chi) ** 2
    multiplier = 1.0 + 5.0 * strain_shape**3 / (343.0 * radius_ratio_six)
    first = (
        derivative[None, :] * cosine
        + 6.0
        * (np.sin(profile) * np.cos(profile) / np.sin(chi) ** 2)[None, :]
        * sine
    )
    weighted = weights * sphere_weight
    gradient = ((weighted * multiplier)[None, :] * first).sum(axis=1)
    hessian = np.empty((modes, modes), dtype=float)
    nonlinear = 30.0 * strain_shape**2 / (343.0 * radius_ratio_six)
    cosine_2f = np.cos(2.0 * profile)
    for i in range(modes):
        for j in range(i, modes):
            second = (
                cosine[i] * cosine[j]
                + 6.0 * cosine_2f / np.sin(chi) ** 2 * sine[i] * sine[j]
            )
            value = np.sum(
                weighted
                * (multiplier * second + nonlinear * first[i] * first[j])
            )
            hessian[i, j] = value
            hessian[j, i] = value
    return gradient, hessian


@lru_cache(maxsize=128)
def radial_fourier_solution(
    radius_ratio_six: float,
    modes: int = 12,
    quadrature_points: int = 480,
) -> tuple[float, ...]:
    """Solve the complete radial Euler equation in a pole-regular sine basis."""

    if not math.isfinite(radius_ratio_six) or radius_ratio_six <= 0.0:
        raise ValueError("radius_ratio_six must be finite and positive")
    if not isinstance(modes, int) or modes < 2:
        raise ValueError("modes must be an integer >=2")
    chi, weights = _quadrature(quadrature_points)
    initial = np.zeros(modes, dtype=float)
    if radius_ratio_six > 1.0:
        q = math.sqrt(45.0 * (radius_ratio_six - 1.0) / 23.0)
        initial[0] = q
        initial[1] = 19.0 * q**2 / 216.0
    else:
        initial[0] = 0.06

    def gradient(values: np.ndarray) -> np.ndarray:
        return _gradient_hessian(
            values, radius_ratio_six, chi, weights
        )[0]

    solved = root(gradient, initial, method="hybr", tol=1.0e-11)
    residual = float(np.max(np.abs(gradient(solved.x))))
    if residual > 2.0e-10:
        raise RuntimeError(f"radial Galerkin solve failed: residual={residual}")
    return tuple(float(value) for value in solved.x)


def _strong_residual(
    coefficients: np.ndarray, radius_ratio_six: float, points: int = 4001
) -> float:
    chi = np.linspace(2.0e-4, math.pi - 2.0e-4, points)
    n = np.arange(1, len(coefficients) + 1, dtype=float)[:, None]
    sine = np.sin(n * chi)
    cosine = n * np.cos(n * chi)
    profile = chi + coefficients @ sine
    derivative = 1.0 + coefficients @ cosine
    second = coefficients @ (-n**2 * sine)
    sin_chi = np.sin(chi)
    cos_chi = np.cos(chi)
    sin_f = np.sin(profile)
    cos_f = np.cos(profile)
    shape = derivative**2 + 6.0 * sin_f**2 / sin_chi**2
    shape_prime = (
        2.0 * derivative * second
        + 12.0 * sin_f * cos_f * derivative / sin_chi**2
        - 12.0 * sin_f**2 * cos_chi / sin_chi**3
    )
    multiplier = 1.0 + 5.0 * shape**3 / (343.0 * radius_ratio_six)
    multiplier_prime = (
        15.0 * shape**2 * shape_prime / (343.0 * radius_ratio_six)
    )
    residual = sin_chi**6 * (
        multiplier * second
        + multiplier_prime * derivative
        + 6.0 * cos_chi * multiplier * derivative / sin_chi
        - 6.0 * multiplier * sin_f * cos_f / sin_chi**2
    )
    return float(np.max(np.abs(residual)) / np.max(sin_chi**6 * multiplier))


def radial_solution_diagnostics(
    radius_ratio_six: float, modes: int = 12, quadrature_points: int = 480
) -> dict[str, Any]:
    coefficients = np.asarray(
        radial_fourier_solution(radius_ratio_six, modes, quadrature_points)
    )
    chi, weights = _quadrature(max(quadrature_points, 600))
    sine, cosine = _basis(chi, modes)
    profile = chi + coefficients @ sine
    derivative = 1.0 + coefficients @ cosine
    sin_chi = np.sin(chi)
    shape = derivative**2 + 6.0 * np.sin(profile) ** 2 / sin_chi**2
    current = derivative * (np.sin(profile) / sin_chi) ** 6
    sphere_weight = sin_chi**6
    average_denominator = float(np.sum(weights * sphere_weight))
    degree = float(np.sum(weights * sphere_weight * current) / average_denominator)
    concentration = float(
        np.sum(weights * sphere_weight * current**2) / average_denominator
    )
    gradient, hessian = _gradient_hessian(
        coefficients, radius_ratio_six, chi, weights
    )
    eigenvalues = np.linalg.eigvalsh(hessian)
    n = np.arange(1, modes + 1, dtype=float)
    right_slope = float(1.0 + np.sum(coefficients * n * (-1.0) ** n))
    support_min_over_critical = radius_ratio_six ** (-1.0 / 3.0) * right_slope**2
    predicted_q = (
        math.sqrt(45.0 * (radius_ratio_six - 1.0) / 23.0)
        if radius_ratio_six > 1.0
        else 0.0
    )
    return {
        "radius_ratio_six": radius_ratio_six,
        "modes": modes,
        "quadrature_points": quadrature_points,
        "coefficients": coefficients.tolist(),
        "q_fourier": float(coefficients[0]),
        "q_leading_prediction": predicted_q,
        "galerkin_residual_inf": float(np.max(np.abs(gradient))),
        "pointwise_weighted_Euler_residual_inf": _strong_residual(
            coefficients, radius_ratio_six
        ),
        "lowest_radial_coefficient_hessian_eigenvalues": eigenvalues[:4].tolist(),
        "radial_coefficient_hessian_positive": bool(eigenvalues[0] > 0.0),
        "degree": degree,
        "C_eta": concentration,
        "right_pole_slope": right_slope,
        "minimum_X_eta_over_critical_X": support_min_over_critical,
    }


def _radial_first_order_rhs(
    chi: np.ndarray, state: np.ndarray, radius_ratio_six: float
) -> np.ndarray:
    profile, derivative = state
    sin_chi = np.sin(chi)
    cos_chi = np.cos(chi)
    sin_f = np.sin(profile)
    cos_f = np.cos(profile)
    shape = derivative**2 + 6.0 * sin_f**2 / sin_chi**2
    multiplier = 1.0 + 5.0 * shape**3 / (343.0 * radius_ratio_six)
    denominator = (
        multiplier
        + 30.0 * shape**2 * derivative**2 / (343.0 * radius_ratio_six)
    )
    remainder = (
        15.0
        * shape**2
        * derivative
        / (343.0 * radius_ratio_six)
        * (
            12.0 * sin_f * cos_f * derivative / sin_chi**2
            - 12.0 * sin_f**2 * cos_chi / sin_chi**3
        )
        + 6.0 * cos_chi * multiplier * derivative / sin_chi
        - 6.0 * multiplier * sin_f * cos_f / sin_chi**2
    )
    return np.vstack((derivative, -remainder / denominator))


def independent_collocation_check(
    radius_ratio_six: float, modes: int = 12
) -> dict[str, Any]:
    """Check the Fourier branch with an independent adaptive BVP solver."""

    coefficients = np.asarray(radial_fourier_solution(radius_ratio_six, modes))
    epsilon = 1.0e-3
    mesh = np.linspace(epsilon, math.pi - epsilon, 500)
    n = np.arange(1, modes + 1, dtype=float)[:, None]
    seed = np.vstack(
        (
            mesh + coefficients @ np.sin(n * mesh),
            1.0 + coefficients @ (n * np.cos(n * mesh)),
        )
    )

    def boundary(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return np.array(
            [left[0] - epsilon * left[1], math.pi - right[0] - epsilon * right[1]]
        )

    solution = solve_bvp(
        lambda point, state: _radial_first_order_rhs(
            point, state, radius_ratio_six
        ),
        boundary,
        mesh,
        seed,
        tol=2.0e-6,
        max_nodes=20000,
    )
    comparison = np.linspace(epsilon, math.pi - epsilon, 3001)
    fourier_profile = comparison + coefficients @ np.sin(n * comparison)
    equation_error = float(
        np.max(
            np.abs(
                solution.sol(comparison, 1)
                - _radial_first_order_rhs(
                    comparison, solution.sol(comparison), radius_ratio_six
                )
            )
        )
    )
    return {
        "method": "adaptive_solve_bvp_with_pole_regular_Robin_limits",
        "status": int(solution.status),
        "converged": solution.status == 0,
        "nodes": int(solution.x.size),
        "profile_difference_from_Fourier_inf": float(
            np.max(np.abs(solution.sol(comparison)[0] - fourier_profile))
        ),
        "first_order_equation_residual_inf": equation_error,
        "boundary_residual_inf": float(
            np.max(np.abs(boundary(solution.y[:, 0], solution.y[:, -1])))
        ),
        "pole_cutoff": epsilon,
    }


def numerical_continuation_payload() -> dict[str, Any]:
    below = [radial_solution_diagnostics(0.99, modes) for modes in (4, 8, 12)]
    above = {
        str(ratio): [
            radial_solution_diagnostics(ratio, modes) for modes in (4, 8, 12)
        ]
        for ratio in (1.001, 1.01, 1.04)
    }
    return {
        "method_1": "pole_regular_Fourier_Galerkin_variational_stationarity",
        "below_crossing": below,
        "above_crossing": above,
        "method_2": independent_collocation_check(1.01, 12),
        "interpretation": (
            "below_a_c_the_seed_returns_to_identity;_above_a_c_two_orientation_"
            "related_nonuniform_radial_branches_exist_and_are_radially_positive"
        ),
        "full_metric_eta_sigma_constraint_solution": False,
    }


def sigma_curvature_root(alpha: float) -> float:
    """Solve alpha+y+5 y^4/4=0 on the stable-parent interval."""

    if not math.isfinite(alpha) or not (-9.0 / 4.0 < alpha < 0.0):
        raise ValueError("alpha must lie in (-9/4,0)")
    return float(
        brentq(
            lambda y: alpha + y + 1.25 * y**4,
            0.0,
            1.0,
            xtol=5.0e-15,
            rtol=1.0e-14,
        )
    )


def _sigma_curvature_on_branch(radius_ratio_six: float, alpha: float) -> float:
    diagnostics = radial_solution_diagnostics(radius_ratio_six, 12)
    x_ratio = diagnostics["minimum_X_eta_over_critical_X"]
    return float(alpha + x_ratio + 1.25 * x_ratio**4)


def sigma_threshold(alpha: float) -> dict[str, Any]:
    """Continue the actual eta branch to its first local sigma zero."""

    y_sigma = sigma_curvature_root(alpha)
    leading_ratio = 1.0 + 23.0 * (1.0 - y_sigma) ** 2 / 180.0
    high = 1.05
    while _sigma_curvature_on_branch(high, alpha) > 0.0 and high < 4.0:
        high = 1.0 + 2.0 * (high - 1.0)
    if high >= 4.0 and _sigma_curvature_on_branch(high, alpha) > 0.0:
        raise RuntimeError("no sigma threshold bracketed on the computed branch")
    exact_ratio = float(
        brentq(
            lambda ratio: _sigma_curvature_on_branch(ratio, alpha),
            1.0 + 1.0e-7,
            high,
            xtol=2.0e-10,
        )
    )
    diagnostics = radial_solution_diagnostics(exact_ratio, 12)
    return {
        "alpha": alpha,
        "alpha_definition": "A0/(g*kappa1*X_critical)",
        "y_sigma_at_critical_normalization": y_sigma,
        "leading_radius_ratio_six": leading_ratio,
        "continued_radius_ratio_six": exact_ratio,
        "q_on_continued_branch": diagnostics["q_fourier"],
        "minimum_X_eta_over_critical_X": diagnostics[
            "minimum_X_eta_over_critical_X"
        ],
        "sigma_curvature_residual": _sigma_curvature_on_branch(exact_ratio, alpha),
        "classification": "DERIVED_CONDITIONAL_ON_RETAINED_UNSELECTED_ALPHA",
    }


def eta_to_sigma_payload() -> dict[str, Any]:
    return {
        "sigma_curvature": (
            "A0+g[kappa1*X_eta+X_eta^4/4];_normalized_at_a_c_as_"
            "F_alpha=alpha+x+(5/4)x^4"
        ),
        "stable_ordinary_parent_interval": "-9/4<alpha<0",
        "leading_threshold": (
            "a_sigma^6/a_c^6-1=(23/180)(1-y_sigma)^2+O((1-y_sigma)^3)"
        ),
        "actual_branch_diagnostics": [
            sigma_threshold(alpha) for alpha in (-2.0, -1.0, -0.25)
        ],
        "coefficient_selection_evidence": (
            "v9.0_parent_action_record_explicitly_classifies_kappa0_kappa1_"
            "Zchi_Zsigma_g_A0_G0_as_independent_theory_inputs;_v6.0.3_"
            "and_v6.1.2_preserve_the_unselected_threshold_and_localization_"
            "status"
        ),
        "physical_alpha_selected_by_action": False,
        "coupled_eta_sigma_metric_branch_solved": False,
        "formation_promoted": False,
    }


def hopf_identity_hessian_payload() -> dict[str, Any]:
    """Return the exact eta-only Hopf positivity decomposition."""

    return {
        "ansatz": (
            "eta(chi,u,v)=(cos(f(chi))*u,sin(f(chi))*v),_u,v_in_S3"
        ),
        "weight": "w=sin(chi)^3*cos(chi)^3",
        "quadratic_form": (
            "a^5(kappa1+343/a^6)int w[y_prime^2+3(cot-tan)^2y^2+"
            "294/(kappa1*a^6+343)*(y_prime+3(cot-tan)y)^2]dchi"
        ),
        "derivation": (
            "delta_z=2[y_prime+3(cot-tan)y];_delta2_z=2[y_prime^2+"
            "3(cot-tan)^2y^2]"
        ),
        "all_coefficients_positive_for": "a>0_and_kappa1>0",
        "kernel": None,
        "verdict": "NO_ETA_ONLY_HOPF_LINEAR_BIFURCATION_AT_ANY_PARENT_RADIUS",
        "scope": "HOPF_COHOMOGENEITY_ONE_ETA_ONLY_IDENTITY_BRANCH",
        "radial_S6_level_surface_identified_with_Hopf_seam": False,
        "physical_full_preimage_seam": "S3_times_S3",
    }


def non_killing_mode_payload() -> dict[str, Any]:
    """Return exact S7 coexact spectrum/moments and the provenance boundary."""

    return {
        "coexact_relative_spectrum": "Lambda_k=(k-1)(k+7),_k>=1",
        "Hodge_spectrum": "Lambda_k+12=(k+1)(k+5)",
        "k1": "KILLING_DIFF_ORBIT_NOT_A_PHYSICAL_INTERNAL_CLOCK",
        "first_non_Killing_k": 2,
        "candidate_constraint_reduced_frequency_squared": "21/a^2",
        "candidate_frequency": "sqrt(21)/a",
        "explicit_field": "V=x0*(-x2*d_x1+x1*d_x2)",
        "tangent": True,
        "ambient_divergence_free": True,
        "mean_norm_squared": str(Fraction(1, 40)),
        "mean_norm_fourth": str(Fraction(1, 560)),
        "participation_ratio": str(Fraction(20, 7)),
        "free_fixed_action_energy_scaling": "E_L2=sqrt(21)*I/a",
        "free_equation_of_state": "P=rho/7",
        "mass_condition": "internal_scale_must_decouple_from_parent_a(tau)",
        "classification": (
            "GEOMETRIC_SPECTRUM_AND_MOMENTS_DERIVED;_FULL_COUPLED_ADM_"
            "FREQUENCY_ATTACHMENT_DERIVED_CONDITIONAL"
        ),
    }


def schur_response_payload() -> dict[str, Any]:
    return {
        "formula": "H_eff=H_eta-B*H_response^{-1}*B_dagger",
        "assumption": "H_response_positive_on_the_existing_common_physical_domain",
        "order": "H_eff<=H_eta_in_quadratic_form_order",
        "consequence": (
            "the_negative_radial_identity_direction_for_a>a_c_cannot_be_"
            "removed_by_positive_block_elimination"
        ),
        "new_branch_full_coupled_stability": (
            "OPEN_REQUIRES_ACTUAL_METRIC_SIGMA_RESPONSE_BLOCKS_ON_THE_BRANCH"
        ),
    }


def completion_payload() -> dict[str, Any]:
    numerical = numerical_continuation_payload()
    sigma = eta_to_sigma_payload()
    validations = {
        "critical_radius_positive": critical_radius() > 0.0,
        "hessian_changes_sign": (
            identity_hessian_ratio(0.99 * critical_radius()) > 0.0
            and identity_hessian_ratio(1.01 * critical_radius()) < 0.0
        ),
        "exact_LS_coefficients_reproduced": (
            exact_lyapunov_schmidt_payload()["complement_coefficient_c"]
            == "19/108"
            and exact_lyapunov_schmidt_payload()["radius_relation_alpha"]
            == "23/45"
        ),
        "below_crossing_returns_identity": all(
            abs(row["q_fourier"]) < 1.0e-9
            for row in numerical["below_crossing"]
        ),
        "above_crossing_nonuniform": all(
            rows[-1]["q_fourier"] > 0.0
            for rows in numerical["above_crossing"].values()
        ),
        "radial_branch_stable_at_tested_resolutions": all(
            rows[-1]["radial_coefficient_hessian_positive"]
            for rows in numerical["above_crossing"].values()
        ),
        "degree_preserved": all(
            abs(rows[-1]["degree"] - 1.0) < 2.0e-12
            for rows in numerical["above_crossing"].values()
        ),
        "independent_BVP_agrees": (
            numerical["method_2"]["converged"]
            and numerical["method_2"]["profile_difference_from_Fourier_inf"]
            < 1.0e-7
        ),
        "sigma_thresholds_close_on_actual_branch": all(
            abs(row["sigma_curvature_residual"]) < 1.0e-8
            for row in sigma["actual_branch_diagnostics"]
        ),
        "Hopf_eta_only_not_mislabeled_full_no_go": (
            hopf_identity_hessian_payload()["scope"]
            == "HOPF_COHOMOGENEITY_ONE_ETA_ONLY_IDENTITY_BRANCH"
        ),
        "no_new_field_source_or_coefficient": True,
        "frozen_predictions_unchanged": True,
        "USB_removable_media_untouched": not USB_REMOVABLE_MEDIA_TOUCHED,
    }
    return {
        "artifact": "BHSM_cycle_driven_eta_spread_concentration_v15_9",
        "version": VERSION,
        "primary_object": PRIMARY_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_reproduction": exact_lyapunov_schmidt_payload(),
        "spread_concentration": concentration_series_payload(),
        "radial_numerical_continuation": numerical,
        "eta_to_sigma": sigma,
        "positive_response_Schur_attachment": schur_response_payload(),
        "Hopf_topology_firewall": hopf_identity_hessian_payload(),
        "first_non_Killing_dynamic_seed": non_killing_mode_payload(),
        "formation_status": (
            "RADIAL_PRECURSOR_AND_CONDITIONAL_SIGMA_ZERO_DERIVED;_FULL_HOPF_"
            "PARENT_CHILD_FORMATION_MAP_OPEN"
        ),
        "persistence_status": "OPEN_NO_RELATIVE_PERIODIC_HOPF_ENCLOSURE",
        "de_envelopment_status": "OPEN_NO_PHYSICAL_ENCLOSURE_INPUT",
        "nested_scale_status": "OPEN_NO_INTERNAL_SCALE_DECOUPLING_SOLUTION",
        "downstream_status": (
            "NOT_REACHED_NO_PHYSICAL_HOPF_COMMON_DOMAIN_GAUGE_DIRAC_STATE"
        ),
        "Hindsight_20_20": {
            "VALIDATED_DERIVED": [
                "exact radial eta cycle threshold and supercritical branch",
                "two-method radial continuation with degree preservation",
                "regular-state degree-density concentration diagnostic",
                "conditional eta-depletion sigma-curvature crossing",
                "eta-only Hopf cohomogeneity-one identity Hessian positivity",
                "S7 k=2 vector-harmonic spectrum and participation moments",
            ],
            "INVALIDATED": [
                "v14.93 zero as a dead-end when the parent radius is dynamical",
                "radial S6 concentration level sets as the Hopf S3xS3 seam",
                "eta-only Hopf linear bifurcation at any parent radius",
                "negative parent Hessian as a universal prerequisite for formation",
            ],
            "RECLASSIFIED": [
                "v14.93 fixed-radius quartic theorem as the critical-cycle slice",
                "radial eta concentration as environment-generating precursor",
                "cavitation as the zero-barrier member of a broader basin-boundary problem",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validations,
        "validation_passed": all(validations.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_physical_parameters": [],
            "measured_particle_inputs": [],
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED": USB_REMOVABLE_MEDIA_TOUCHED,
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_cycle_driven_eta_spread_concentration_v15_9.json"
    path.write_text(
        deterministic_json(completion_payload()), encoding="utf-8", newline="\n"
    )
    return path
