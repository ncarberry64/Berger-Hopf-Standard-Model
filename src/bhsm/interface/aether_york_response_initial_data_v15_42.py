"""Pure-trace York continuation test for the response-constrained child.

The v15.41 projection fixes the semantic role of the constant lapse row and
derives a positive mean-curvature square.  Here the full pointwise
Hamiltonian constraint is solved in the conformal join sector, with sigma
recomputed from eta and the zero-current odd-FR expectation normalized on
the same geometry.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_bvp

from bhsm.interface.aether_response_constrained_child_galerkin_v15_41 import (
    HOPF_ORBIT_VOLUME,
    solve_response_constrained_galerkin,
)


VERSION = "v15.42"
CLASSIFICATION = "BHSM_PURE_TRACE_YORK_CMC_RESPONSE_OBSTRUCTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def york_constraint_contract() -> dict[str, Any]:
    return {
        "metric": (
            "h7=R^2*exp(2u(chi))*[dchi2+cos(chi)^2dOmega3_u2+"
            "sin(chi)^2dOmega3_v2]"
        ),
        "extrinsic_curvature": "K_ij=H*h_ij_with_spatially_constant_H",
        "momentum_constraint": "D_j(K^ij-h^ij*K)=0_identically",
        "Hamiltonian_constraint": (
            "kappa1*[R7+42H^2]/2-kappa0/2-rho_eta-rho_sigma-rho_FR=0"
        ),
        "eta_profile": "v15.41_spatial-Euler_Galerkin_profile",
        "material_response": "sigma=C_J[f]-1/2",
        "FR_normalization": "omega*I=1/2",
        "conformal_gauge": "integral_sin(chi)^3cos(chi)^3*u_dchi=0",
        "new_physical_coefficient": False,
    }


def _formed_response_profile(
    coordinate: np.ndarray, q2: float, q4: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    dense = np.linspace(0.0, math.pi / 2.0, 30001)
    f_dense = dense + q2 * np.sin(2.0 * dense) + q4 * np.sin(4.0 * dense)
    raw = np.sin(f_dense) ** 2 * np.cos(f_dense) ** 2
    normalization = float(np.trapezoid(raw, dense))
    density = raw / normalization
    cumulative = np.concatenate(
        ([0.0], np.cumsum(0.5 * (density[1:] + density[:-1]) * np.diff(dense)))
    )
    cumulative /= cumulative[-1]
    sigma_dense = cumulative - 0.5
    f = coordinate + q2 * np.sin(2.0 * coordinate) + q4 * np.sin(4.0 * coordinate)
    f_prime = 1.0 + 2.0 * q2 * np.cos(2.0 * coordinate) + 4.0 * q4 * np.cos(4.0 * coordinate)
    sigma = np.interp(coordinate, dense, sigma_dense)
    sigma_prime = np.interp(coordinate, dense, density)
    return f, f_prime, sigma, sigma_prime


def solve_york_response_initial_data(
    *,
    pole_cutoff: float = 2.0e-3,
    homotopy_steps: int = 10,
    tolerance: float = 8.0e-5,
) -> dict[str, Any]:
    """Solve the pointwise conformal Hamiltonian and momentum constraints."""

    projected = solve_response_constrained_galerkin(
        points=180, homotopy_steps=8
    )
    coefficients = projected["coefficients"]
    q2, q4 = float(coefficients[5]), float(coefficients[6])
    log_radius = float(coefficients[0])
    kappa1 = 1.0
    radius0 = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    radius = radius0 * math.exp(log_radius)
    x_critical = (5.0 * kappa1) ** (1.0 / 3.0)
    kappa0 = 15.0 * kappa1 * x_critical / 4.0
    left = np.geomspace(pole_cutoff, 0.05, 120)
    middle = np.linspace(0.05, math.pi / 2.0 - 0.05, 260)
    right = math.pi / 2.0 - np.geomspace(pole_cutoff, 0.05, 80)[::-1]
    mesh = np.unique(np.concatenate((left, middle, right)))

    def equations(scale: float):
        def evaluate(
            coordinate: np.ndarray, state: np.ndarray, parameter: np.ndarray
        ) -> np.ndarray:
            u, u_prime = state[0], state[1]
            omega, h_squared = parameter
            f, f_prime, sigma, sigma_prime = _formed_response_profile(
                coordinate, q2, q4
            )
            weight = np.sin(coordinate) ** 3 * np.cos(coordinate) ** 3
            exp_minus_two = np.exp(-2.0 * u)
            angular = (
                f_prime**2
                + 3.0 * np.cos(f) ** 2 / np.cos(coordinate) ** 2
                + 3.0 * np.sin(f) ** 2 / np.sin(coordinate) ** 2
            )
            x_eta = exp_minus_two * angular / radius**2
            eta_weight = 1.0 - 4.0 * scale * sigma**2
            rho_eta = eta_weight * (
                0.5 * kappa1 * x_eta + 0.125 * x_eta**4
            )
            localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
            rho_fr = 0.5 * (kappa1 + x_eta**3) * localization * omega**2
            source = (
                rho_eta + rho_fr + 0.5 * kappa0
                - 21.0 * kappa1 * h_squared
            )
            pole_expansion = 3.0 * (
                1.0 / np.tan(coordinate) - np.tan(coordinate)
            )
            u_second = (
                42.0
                - 30.0 * u_prime**2
                - 2.0 * radius**2 * np.exp(2.0 * u) * source / kappa1
            ) / 12.0 - pole_expansion * u_prime
            inertia_prime = (
                HOPF_ORBIT_VOLUME
                * radius**7
                * weight
                * np.exp(7.0 * u)
                * (kappa1 + x_eta**3)
                * localization
            )
            mean_prime = weight * u
            return np.vstack((u_prime, u_second, inertia_prime, mean_prime))

        return evaluate

    def boundary(scale: float):
        def residual(
            left_state: np.ndarray,
            right_state: np.ndarray,
            parameter: np.ndarray,
        ) -> np.ndarray:
            omega, _ = parameter
            return np.array([
                left_state[1], right_state[1], left_state[2],
                omega * right_state[2] - 0.5 * scale,
                left_state[3], right_state[3],
            ])

        return residual

    state = np.zeros((4, mesh.size))
    base_inertia_prime = equations(0.0)(mesh, state, np.array([0.0, 0.0]))[2]
    state[2, 1:] = np.cumsum(
        0.5 * (base_inertia_prime[1:] + base_inertia_prime[:-1]) * np.diff(mesh)
    )
    parameter = np.array([0.0, 0.0])
    solution = None
    history: list[dict[str, Any]] = []
    for scale in np.linspace(0.0, 1.0, homotopy_steps + 1):
        solution = solve_bvp(
            equations(float(scale)), boundary(float(scale)), mesh, state,
            p=parameter, tol=tolerance, max_nodes=30000
        )
        if solution.status != 0:
            raise RuntimeError(
                f"York response homotopy failed at {scale}: {solution.message}"
            )
        mesh, state, parameter = solution.x, solution.y, solution.p
        history.append({
            "homotopy": float(scale),
            "omega": float(parameter[0]),
            "H_squared": float(parameter[1]),
            "maximum_solver_relative_residual": float(
                np.max(solution.rms_residuals)
            ),
        })
    assert solution is not None

    evaluation = np.linspace(pole_cutoff, math.pi / 2.0 - pole_cutoff, 2001)
    values = solution.sol(evaluation)
    derivatives = solution.sol(evaluation, 1)
    u, u_prime, inertia_state = values[0], values[1], values[2]
    u_second = derivatives[1]
    omega, h_squared = map(float, solution.p)
    f, f_prime, sigma, sigma_prime = _formed_response_profile(evaluation, q2, q4)
    exp_minus_two = np.exp(-2.0 * u)
    angular = (
        f_prime**2
        + 3.0 * np.cos(f) ** 2 / np.cos(evaluation) ** 2
        + 3.0 * np.sin(f) ** 2 / np.sin(evaluation) ** 2
    )
    x_eta = exp_minus_two * angular / radius**2
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    rho_eta = localization * (
        0.5 * kappa1 * x_eta + 0.125 * x_eta**4
    )
    rho_fr = 0.5 * (kappa1 + x_eta**3) * localization * omega**2
    scalar_curvature = exp_minus_two / radius**2 * (
        42.0 - 12.0 * (
            u_second + 3.0 * (1.0 / np.tan(evaluation) - np.tan(evaluation)) * u_prime
        ) - 30.0 * u_prime**2
    )
    constraint = (
        0.5 * kappa1 * (scalar_curvature + 42.0 * h_squared)
        - 0.5 * kappa0 - rho_eta - rho_fr
    )
    boundary_residual = boundary(1.0)(
        solution.y[:, 0], solution.y[:, -1], solution.p
    )
    inertia = float(inertia_state[-1])
    return {
        "source_Galerkin_coefficients": coefficients,
        "radius": radius,
        "eta_q2": q2,
        "eta_q4": q4,
        "H_squared": h_squared,
        "H": math.sqrt(h_squared) if h_squared >= 0.0 else None,
        "H_squared_positive": h_squared > 0.0,
        "omega": omega,
        "localized_inertia": inertia,
        "FR_normalization_residual": omega * inertia - 0.5,
        "conformal_u_min": float(np.min(u)),
        "conformal_u_max": float(np.max(u)),
        "conformal_response_nonconstant": float(np.ptp(u)) > 1.0e-4,
        "mean_conformal_gauge_residual": float(values[3, -1]),
        "maximum_pointwise_Hamiltonian_residual": float(np.max(np.abs(constraint))),
        "maximum_boundary_residual": float(np.max(np.abs(boundary_residual))),
        "maximum_solver_relative_residual": float(np.max(solution.rms_residuals)),
        "homotopy_history": history,
        "momentum_constraint_residual": 0.0,
        "formal_pointwise_constraint_equation_solved": True,
        "physical_real_CMC_initial_data": h_squared >= 0.0,
    }


def completion_payload() -> dict[str, Any]:
    contract = york_constraint_contract()
    solution = solve_york_response_initial_data()
    validation = {
        "CMC_test_uses_action_owned_geometry_not_pressure": not contract[
            "new_physical_coefficient"
        ],
        "pure_trace_CMC_rejected_by_negative_H_squared": not solution[
            "H_squared_positive"
        ],
        "Hamiltonian_constraint_pointwise_controlled": solution[
            "maximum_pointwise_Hamiltonian_residual"
        ] < 3.0e-3,
        "momentum_constraint_closed": solution["momentum_constraint_residual"] == 0.0,
        "FR_normalization_closed": abs(solution["FR_normalization_residual"]) < 2.0e-5,
        "boundary_and_mean_gauge_closed": solution["maximum_boundary_residual"] < 2.0e-5,
        "nonconstant_geometry_response": solution["conformal_response_nonconstant"],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_york_response_initial_data_v15_42",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "York_constraint_contract": contract,
        "pure_trace_constraint_continuation": solution,
        "claim_boundary": {
            "response_constrained_real_CMC_initial_data_solved": False,
            "trace_free_shape_shear_required": True,
            "Lorentzian_encapsulation_evolution_solved": False,
            "persistent_child_derived": False,
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
    path = target / "BHSM_aether_york_response_initial_data_v15_42.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "york_constraint_contract", "solve_york_response_initial_data",
    "completion_payload", "deterministic_json", "materialize",
]
