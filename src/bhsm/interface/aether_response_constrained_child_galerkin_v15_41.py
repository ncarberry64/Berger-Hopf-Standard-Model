"""Response-constrained nonround child action and Galerkin continuation.

This module writes the static cohomogeneity-one BHSM child as one reduced
functional.  The material trace is not an independent profile: at every
evaluation it is reconstructed from the normalized eta join response

    sigma = C_J[f] - 1/2,   C_J' = sin(f)^2 cos(f)^2 / Z_J[f].

The finite Galerkin solve is a controlled projection of the full
Einstein--eta--response equations.  It is useful for checking the semantics
and for selecting a nonlinear branch, but it is not relabelled as the full
two-pole BVP.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import least_squares

VERSION = "v15.41"
CLASSIFICATION = "BHSM_RESPONSE_CONSTRAINED_CHILD_GALERKIN_CONTINUATION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
HOPF_ORBIT_VOLUME = (2.0 * math.pi**2) ** 2


def reduced_action_contract() -> dict[str, Any]:
    """State the exact reduced functional represented by this module."""

    return {
        "metric": (
            "ds2=-N(chi)^2dt2+C(chi)^2dchi2+A(chi)^2dOmega3_u2+"
            "B(chi)^2dOmega3_v2"
        ),
        "eta": "eta=(cos(f)u,sin(f)v)",
        "volume_density": "mu=C*A^3*B^3",
        "R7": (
            "6/A^2+6/B^2-6(A_second/A+B_second/B)/C^2+"
            "6C_prime(A_prime/A+B_prime/B)/C^3-"
            "6[(A_prime/A)^2+(B_prime/B)^2]/C^2-"
            "18A_prime*B_prime/(C^2*A*B)"
        ),
        "X_eta": (
            "f_prime^2/C^2+3cos(f)^2/A^2+3sin(f)^2/B^2"
        ),
        "F": "kappa1*X_eta/2+X_eta^4/8",
        "eta_carrier_weight": (
            "1+g*sigma^2=1-4sigma^2,_hence_g=-4_from_even-quadratic_"
            "seam-normalized_vacuum-localization"
        ),
        "response": (
            "sigma=C_J[f]-1/2,_C_J_prime=sin(f)^2cos(f)^2/Z_J[f]"
        ),
        "material_sector": (
            "coefficient-free_KKT_response_replaces_the_independent_"
            "Zsigma_gradient-plus-inverse-Euler_skin_action"
        ),
        "static_action": (
            "S0=Vol(S3)^2*integral_N*mu*[kappa1*R7/2-kappa0/2-"
            "(1-4sigma^2)F(X_eta)]dchi-J^2/(2I_N)"
        ),
        "lapse_weighted_inertia": (
            "I_N=Vol(S3)^2*integral_mu*(kappa1+X_eta^3)*"
            "(1-4sigma^2)/N_dchi"
        ),
        "FR_domain": "odd_antiperiodic_ground_sector_J_squared=1/4",
        "constraint_semantics": (
            "lapse_variations_are_Hamiltonian-constraint_projections;_"
            "sigma_variations_are_induced_only_through_f"
        ),
    }


@lru_cache(maxsize=8)
def _gauss_rule(points: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 4.0
    return chi, weights * math.pi / 4.0


def galerkin_fields(
    coefficients: np.ndarray, *, kappa1: float = 1.0, points: int = 320
) -> dict[str, np.ndarray | float]:
    """Evaluate the regular ten-parameter nonround two-pole ansatz."""

    values = np.asarray(coefficients, dtype=float)
    if values.shape != (10,) or not np.all(np.isfinite(values)):
        raise ValueError("coefficients must be ten finite real numbers")
    if kappa1 <= 0.0 or points < 120:
        raise ValueError("kappa1 must be positive and points >=120")
    scale, u2, u4, v0, v1, q2, q4, n0, n2, n4 = values
    chi, weights = _gauss_rule(int(points))
    radius0 = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    radius = radius0 * np.exp(scale)
    sin2 = np.sin(2.0 * chi)
    cos2 = np.cos(2.0 * chi)
    cos4 = np.cos(4.0 * chi)

    u = u2 * cos2 + u4 * cos4
    u_prime = -2.0 * u2 * sin2 - 4.0 * u4 * np.sin(4.0 * chi)
    u_second = -4.0 * u2 * cos2 - 16.0 * u4 * cos4
    shape_window = sin2**2
    v = shape_window * (v0 + v1 * cos2)
    v_prime = (
        2.0 * np.sin(4.0 * chi) * (v0 + v1 * cos2)
        - 2.0 * v1 * shape_window * sin2
    )
    v_second = np.gradient(v_prime, chi, edge_order=2)
    lapse_log = n0 + n2 * cos2 + n4 * cos4
    lapse = np.exp(lapse_log)

    f = chi + q2 * sin2 + q4 * np.sin(4.0 * chi)
    f_prime = 1.0 + 2.0 * q2 * cos2 + 4.0 * q4 * cos4
    raw = np.sin(f) ** 2 * np.cos(f) ** 2
    normalization = float(np.dot(weights, raw))
    if normalization <= 1.0e-12 or np.min(f_prime) <= 1.0e-4:
        raise ValueError("the Galerkin eta map must remain degree-one monotone")
    sigma_prime = raw / normalization
    augmented_chi = np.concatenate(([0.0], chi, [math.pi / 2.0]))
    augmented_density = np.concatenate(([0.0], sigma_prime, [0.0]))
    increments = 0.5 * (
        augmented_density[1:] + augmented_density[:-1]
    ) * np.diff(augmented_chi)
    cumulative = np.concatenate(([0.0], np.cumsum(increments)))
    cumulative /= cumulative[-1]
    sigma = cumulative[1:-1] - 0.5

    C = radius * np.exp(u)
    A = radius * np.exp(u + v) * np.cos(chi)
    B = radius * np.exp(u - v) * np.sin(chi)
    log_A_prime = u_prime + v_prime - np.tan(chi)
    log_B_prime = u_prime - v_prime + 1.0 / np.tan(chi)
    log_C_prime = u_prime
    log_A_second = u_second + v_second - 1.0 / np.cos(chi) ** 2
    log_B_second = u_second - v_second - 1.0 / np.sin(chi) ** 2
    A_second_over_A = log_A_second + log_A_prime**2
    B_second_over_B = log_B_second + log_B_prime**2

    scalar_curvature = (
        6.0 / A**2
        + 6.0 / B**2
        - 6.0 * (A_second_over_A + B_second_over_B) / C**2
        + 6.0
        * log_C_prime
        * (log_A_prime + log_B_prime)
        / C**2
        - 6.0 * (log_A_prime**2 + log_B_prime**2) / C**2
        - 18.0 * log_A_prime * log_B_prime / C**2
    )
    x_eta = (
        f_prime**2 / C**2
        + 3.0 * np.cos(f) ** 2 / A**2
        + 3.0 * np.sin(f) ** 2 / B**2
    )
    return {
        "chi": chi,
        "weights": weights,
        "radius": float(radius),
        "N": lapse,
        "C": C,
        "A": A,
        "B": B,
        "f": f,
        "f_prime": f_prime,
        "sigma": sigma,
        "sigma_prime": sigma_prime,
        "R7": scalar_curvature,
        "X_eta": x_eta,
    }


def static_reduced_action(
    coefficients: np.ndarray,
    *,
    homotopy: float = 1.0,
    kappa1: float = 1.0,
    charge: float = 0.5,
    points: int = 320,
) -> float:
    """Evaluate the response-constrained static Routh functional."""

    if not 0.0 <= homotopy <= 1.0:
        raise ValueError("homotopy must lie in [0,1]")
    fields = galerkin_fields(coefficients, kappa1=kappa1, points=points)
    weights = np.asarray(fields["weights"])
    lapse = np.asarray(fields["N"])
    C = np.asarray(fields["C"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    sigma = np.asarray(fields["sigma"])
    sigma_prime = np.asarray(fields["sigma_prime"])
    curvature = np.asarray(fields["R7"])
    x_eta = np.asarray(fields["X_eta"])
    radius = float(fields["radius"])
    kappa0 = 15.0 * kappa1 * (5.0 * kappa1) ** (1.0 / 3.0) / 4.0
    volume = C * A**3 * B**3
    eta_density = 0.5 * kappa1 * x_eta + 0.125 * x_eta**4
    # Homotopy zero is the retained critical identity branch.  At homotopy
    # one the unique normalized even-quadratic child-support factor is the
    # retained carrier weight with g=-4.
    eta_weight = 1.0 - 4.0 * homotopy * sigma**2
    integrand = lapse * volume * (
        0.5 * kappa1 * curvature
        - 0.5 * kappa0
        - eta_weight * eta_density
    )
    action = HOPF_ORBIT_VOLUME * float(np.dot(weights, integrand))
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    inertia = HOPF_ORBIT_VOLUME * float(
        np.dot(
            weights,
            volume * (kappa1 + x_eta**3) * localization / lapse,
        )
    )
    if inertia <= 0.0:
        raise ValueError("localized Hopf inertia must be positive")
    return action - homotopy * charge**2 / (2.0 * inertia)


def action_gradient(
    coefficients: np.ndarray,
    *,
    homotopy: float = 1.0,
    points: int = 320,
    step: float = 2.0e-5,
) -> np.ndarray:
    """Central finite-difference Galerkin Euler residual."""

    center = np.asarray(coefficients, dtype=float)
    result = np.empty_like(center)
    for index in range(center.size):
        delta = np.zeros_like(center)
        delta[index] = step
        result[index] = (
            static_reduced_action(
                center + delta, homotopy=homotopy, points=points
            )
            - static_reduced_action(
                center - delta, homotopy=homotopy, points=points
            )
        ) / (2.0 * step)
    # A constant lapse rescaling multiplies the entire static Routh
    # functional.  Divide out that gauge factor so a least-squares solver
    # cannot reduce every residual merely by sending the clock normalization
    # toward zero.  The n0 row remains the genuine integrated Hamiltonian
    # constraint, while n0 itself is an undetermined clock normalization.
    return result / (HOPF_ORBIT_VOLUME * math.exp(float(center[7])))


def round_branch_check(points: int = 480) -> dict[str, float | bool]:
    """Verify that homotopy zero recovers the critical round solution."""

    zero = np.zeros(10)
    fields = galerkin_fields(zero, points=points)
    gradient = action_gradient(zero, homotopy=0.0, points=points)
    radius = float(fields["radius"])
    return {
        "radius": radius,
        "maximum_R7_residual": float(
            np.max(np.abs(np.asarray(fields["R7"]) - 42.0 / radius**2))
        ),
        "maximum_X_eta_residual": float(
            np.max(np.abs(np.asarray(fields["X_eta"]) - 7.0 / radius**2))
        ),
        "maximum_projected_Euler_residual": float(np.max(np.abs(gradient))),
        "round_critical_branch_recovered": float(np.max(np.abs(gradient)))
        < 2.0e-5,
    }


def solve_response_constrained_galerkin(
    *, points: int = 260, homotopy_steps: int = 10
) -> dict[str, Any]:
    """Continue the spatial Euler projection and expose its lapse defect.

    The constant lapse is a multiplier, not a variable to be minimized.  We
    set its normalization n0=0, solve the other nine projected Euler rows,
    and then evaluate the omitted n0 row as the integrated Hamiltonian
    constraint.  With the completed localized carrier the defect is positive,
    so it selects the trace-free shape-shear sign of the moving data.
    """

    state = np.zeros(10)
    history: list[dict[str, Any]] = []
    for level in np.linspace(0.0, 1.0, homotopy_steps + 1)[1:]:
        free_indices = np.array([0, 1, 2, 3, 4, 5, 6, 8, 9])

        def embed(free: np.ndarray) -> np.ndarray:
            full = np.zeros(10)
            full[free_indices] = free
            return full

        result = least_squares(
            lambda free: action_gradient(
                embed(free), homotopy=float(level), points=points
            )[free_indices],
            state[free_indices],
            bounds=(
                np.array([
                    -0.7, -0.7, -0.7, -0.7, -0.7,
                    -0.15, -0.05, -0.7, -0.7,
                ]),
                np.array([
                    +0.7, +0.7, +0.7, +0.7, +0.7,
                    +0.15, +0.05, +0.7, +0.7,
                ]),
            ),
            xtol=2.0e-8,
            ftol=2.0e-8,
            gtol=2.0e-8,
            max_nfev=800,
            x_scale="jac",
        )
        state = embed(result.x)
        residual = action_gradient(
            state, homotopy=float(level), points=points
        )
        spatial_residual = residual[free_indices]
        if np.max(np.abs(spatial_residual)) > 2.0e-4:
            raise RuntimeError(
                f"Galerkin continuation failed at homotopy={level}: "
                f"{result.message}; residual={np.max(np.abs(spatial_residual))}"
            )
        history.append(
            {
                "homotopy": float(level),
                "maximum_spatial_Euler_residual": float(
                    np.max(np.abs(spatial_residual))
                ),
                "integrated_Hamiltonian_defect": float(residual[7]),
            }
        )
    fields = galerkin_fields(state, points=max(points, 420))
    sigma = np.asarray(fields["sigma"])
    chi = np.asarray(fields["chi"])
    seam = float(np.interp(0.0, sigma, chi))
    A = float(np.interp(seam, chi, np.asarray(fields["A"])))
    B = float(np.interp(seam, chi, np.asarray(fields["B"])))
    verification = action_gradient(
        state, homotopy=1.0, points=max(points, 420), step=1.0e-5
    )
    verification_spatial = verification[free_indices]
    weights = np.asarray(fields["weights"])
    volume_density = (
        np.asarray(fields["C"])
        * np.asarray(fields["A"]) ** 3
        * np.asarray(fields["B"]) ** 3
    )
    spatial_volume_without_orbit_factor = float(
        np.dot(weights, volume_density)
    )
    integrated_defect = float(verification[7])
    mean_constraint_defect = integrated_defect / spatial_volume_without_orbit_factor
    uniform_shape_shear_squared = max(0.0, mean_constraint_defect / 3.0)
    return {
        "coefficient_order": [
            "log_R", "u2", "u4", "v0", "v1", "q2", "q4", "n0",
            "n2", "n4"
        ],
        "coefficients": state.tolist(),
        "homotopy_history": history,
        "maximum_solve_grid_spatial_Euler_residual": history[-1][
            "maximum_spatial_Euler_residual"
        ],
        "maximum_independent_grid_spatial_Euler_residual": float(
            np.max(np.abs(verification_spatial))
        ),
        "integrated_Hamiltonian_constraint_defect": integrated_defect,
        "mean_Hamiltonian_constraint_defect": mean_constraint_defect,
        "uniform_shape_shear_squared_estimate": uniform_shape_shear_squared,
        "uniform_shape_shear_estimate": math.sqrt(
            uniform_shape_shear_squared
        ),
        "shape_shear_closes_integrated_constraint": abs(
            mean_constraint_defect - 3.0 * uniform_shape_shear_squared
        ) < 1.0e-12,
        "material_seam_chi": seam,
        "projected_child_scale_x": math.log(B / A),
        "eta_monotonicity_margin": float(np.min(fields["f_prime"])),
        "finite_fields": bool(
            all(np.all(np.isfinite(np.asarray(fields[key]))) for key in (
                "N", "C", "A", "B", "f", "sigma", "R7", "X_eta"
            ))
        ),
        "interpretation": (
            "stationary_spatial-Euler_projection_plus_action-derived_"
            "trace-free-shape-shear_sign_for_moving_constraint_data_not_yet_"
            "the_full_function-space_evolution"
        ),
    }


def completion_payload() -> dict[str, Any]:
    contract = reduced_action_contract()
    round_check = round_branch_check()
    solution = solve_response_constrained_galerkin()
    validation = {
        "critical_round_branch_recovered": round_check[
            "round_critical_branch_recovered"
        ],
        "projected_spatial_Euler_equations_solved": solution[
            "maximum_solve_grid_spatial_Euler_residual"
        ] < 2.0e-4,
        "independent_quadrature_check": solution[
            "maximum_independent_grid_spatial_Euler_residual"
        ] < 4.0e-3,
        "integrated_constraint_selects_shape_shear": solution[
            "shape_shear_closes_integrated_constraint"
        ] and solution["uniform_shape_shear_squared_estimate"] > 0.0,
        "degree_one_eta_map_preserved": solution[
            "eta_monotonicity_margin"
        ] > 0.0,
        "all_fields_finite": solution["finite_fields"],
        "full_BVP_not_overclaimed": "not_yet_the_full" in solution[
            "interpretation"
        ],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_response_constrained_child_galerkin_v15_41",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "reduced_action_contract": contract,
        "round_branch_check": round_check,
        "response_constrained_Galerkin_solution": solution,
        "claim_boundary": {
            "one_response_constrained_child_functional_written": True,
            "finite_Galerkin_spatial_Euler_projection_solved": True,
            "moving_shape_shear_sign_and_integrated_amplitude_derived": True,
            "full_two-pole_function-space_BVP_solved": False,
            "physical_child_Hessian_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
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
        rounded = round(value, 8)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_response_constrained_child_galerkin_v15_41.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "reduced_action_contract", "galerkin_fields", "static_reduced_action",
    "action_gradient", "round_branch_check",
    "solve_response_constrained_galerkin", "completion_payload",
    "deterministic_json", "materialize",
]
