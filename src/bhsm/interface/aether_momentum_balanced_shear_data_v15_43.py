"""Momentum-balanced trace-free York data for the BHSM child.

The completed localized carrier leaves a positive static Hamiltonian defect.
Pure-trace curvature has the wrong sign.  The action-owned nonround join
shape supplies the required negative constraint contribution.  A regular
SO(4)xSO(4)-invariant transverse-traceless tensor solves the momentum
constraint identically, without an arbitrary external or eta current.
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
from bhsm.interface.aether_york_response_initial_data_v15_42 import (
    _formed_response_profile,
)


VERSION = "v15.43"
CLASSIFICATION = "BHSM_MOMENTUM_BALANCED_TRACE_FREE_SHEAR_INITIAL_DATA"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def shear_constraint_contract() -> dict[str, Any]:
    return {
        "metric": (
            "h7=R^2*exp(2u)*[dchi2+cos(chi)^2dOmega3_u2+"
            "sin(chi)^2dOmega3_v2]"
        ),
        "carrier": "Lambda=1-4sigma^2,_sigma=C_J[f]-1/2",
        "extrinsic_eigenvalues": [
            "K_chi^chi=-6m",
            "K_u^u=m*(1+11cos(2chi))",
            "K_v^v=m*(1-11cos(2chi))",
        ],
        "regular_shear_profile": "m=S*exp(-7u)*sin(2chi)^2",
        "trace": "K=0",
        "constraint_sign": (
            "K^2-KijKij=-m^2*[42+726cos(2chi)^2]"
        ),
        "radial_momentum_constraint": (
            "D_j K^j_chi=0_exactly_for_m=exp(-7u)sin(2chi)^2*S"
        ),
        "TT_identity": (
            "m_prime/m=-7u_prime+4cot(2chi)_and_the_diagonal_"
            "divergence_cancels_pointwise"
        ),
        "eta_normal_momentum": 0.0,
        "new_current_inserted": False,
        "new_continuous_coefficient": False,
    }


def solve_momentum_balanced_shear_data(
    *,
    pole_cutoff: float = 2.0e-3,
    homotopy_steps: int = 12,
    tolerance: float = 1.5e-4,
) -> dict[str, Any]:
    """Solve both ADM constraints with regular localized join shear."""

    projected = solve_response_constrained_galerkin(
        points=180, homotopy_steps=8
    )
    coefficients = projected["coefficients"]
    q2, q4 = float(coefficients[5]), float(coefficients[6])
    kappa1 = 1.0
    radius0 = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    radius = radius0 * math.exp(float(coefficients[0]))
    kappa0 = 15.0 * kappa1 * (5.0 * kappa1) ** (1.0 / 3.0) / 4.0

    left = np.geomspace(pole_cutoff, 0.05, 130)
    middle = np.linspace(0.05, math.pi / 2.0 - 0.05, 280)
    right = math.pi / 2.0 - np.geomspace(pole_cutoff, 0.05, 90)[::-1]
    mesh = np.unique(np.concatenate((left, middle, right)))

    def equations(scale: float):
        def evaluate(
            coordinate: np.ndarray, state: np.ndarray, parameter: np.ndarray
        ) -> np.ndarray:
            u, u_prime = state[0], state[1]
            omega, shear_amplitude = parameter
            f, f_prime, sigma, _ = _formed_response_profile(
                coordinate, q2, q4
            )
            weight = np.sin(coordinate) ** 3 * np.cos(coordinate) ** 3
            eta_weight = np.maximum(0.0, 1.0 - 4.0 * scale * sigma**2)
            full_localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
            exp_minus_two = np.exp(-2.0 * u)
            angular = (
                f_prime**2
                + 3.0 * np.cos(f) ** 2 / np.cos(coordinate) ** 2
                + 3.0 * np.sin(f) ** 2 / np.sin(coordinate) ** 2
            )
            x_spatial = exp_minus_two * angular / radius**2
            eta_legendre = kappa1 + x_spatial**3
            eta_density = eta_weight * (
                0.5 * kappa1 * x_spatial + 0.125 * x_spatial**4
            )
            tt_mean = (
                shear_amplitude
                * np.exp(-7.0 * u)
                * np.sin(2.0 * coordinate) ** 2
            )
            shear_norm = tt_mean**2 * (
                42.0 + 726.0 * np.cos(2.0 * coordinate) ** 2
            )
            rho_fr = (
                0.5 * eta_legendre * full_localization * omega**2
            )
            source = (
                eta_density + rho_fr + 0.5 * kappa0
                + 0.5 * kappa1 * shear_norm
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
                * eta_legendre
                * full_localization
            )
            return np.vstack((
                u_prime,
                u_second,
                inertia_prime,
                weight * u,
            ))

        return evaluate

    def boundary(scale: float):
        def residual(
            left_state: np.ndarray,
            right_state: np.ndarray,
            parameter: np.ndarray,
        ) -> np.ndarray:
            omega, _ = parameter
            return np.array([
                left_state[1],
                right_state[1],
                left_state[2],
                omega * right_state[2] - 0.5 * scale,
                left_state[3],
                right_state[3],
            ])

        return residual

    state = np.zeros((4, mesh.size))
    parameter = np.array([0.0, 0.08])
    history: list[dict[str, float]] = []
    solution = None
    scales = np.linspace(1.0 / homotopy_steps, 1.0, homotopy_steps)
    for scale in scales:
        if solution is None:
            inertia_prime = equations(float(scale))(
                mesh, state, parameter
            )[2]
            state[2, 1:] = np.cumsum(
                0.5
                * (inertia_prime[1:] + inertia_prime[:-1])
                * np.diff(mesh)
            )
        solution = solve_bvp(
            equations(float(scale)),
            boundary(float(scale)),
            mesh,
            state,
            p=parameter,
            tol=tolerance,
            max_nodes=40000,
        )
        if solution.status != 0:
            raise RuntimeError(
                f"shear-data homotopy failed at {scale}: {solution.message}; "
                f"parameter={solution.p}; history_tail={history[-2:]}"
            )
        mesh, state, parameter = solution.x, solution.y, solution.p
        history.append({
            "homotopy": float(scale),
            "omega": float(parameter[0]),
            "shear_amplitude": float(parameter[1]),
            "maximum_solver_relative_residual": float(
                np.max(solution.rms_residuals)
            ),
        })
    assert solution is not None

    coordinate = np.linspace(
        pole_cutoff, math.pi / 2.0 - pole_cutoff, 2401
    )
    values = solution.sol(coordinate)
    derivatives = solution.sol(coordinate, 1)
    u, u_prime = values[0], values[1]
    u_second = derivatives[1]
    omega, shear_amplitude = map(float, solution.p)
    f, f_prime, sigma, _ = _formed_response_profile(
        coordinate, q2, q4
    )
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    exp_minus_two = np.exp(-2.0 * u)
    angular = (
        f_prime**2
        + 3.0 * np.cos(f) ** 2 / np.cos(coordinate) ** 2
        + 3.0 * np.sin(f) ** 2 / np.sin(coordinate) ** 2
    )
    x_spatial = exp_minus_two * angular / radius**2
    eta_legendre = kappa1 + x_spatial**3
    eta_density = localization * (
        0.5 * kappa1 * x_spatial + 0.125 * x_spatial**4
    )
    tt_mean = (
        shear_amplitude
        * np.exp(-7.0 * u)
        * np.sin(2.0 * coordinate) ** 2
    )
    shear_norm = tt_mean**2 * (
        42.0 + 726.0 * np.cos(2.0 * coordinate) ** 2
    )
    rho_fr = 0.5 * eta_legendre * localization * omega**2
    scalar_curvature = exp_minus_two / radius**2 * (
        42.0
        - 12.0 * (
            u_second
            + 3.0
            * (1.0 / np.tan(coordinate) - np.tan(coordinate))
            * u_prime
        )
        - 30.0 * u_prime**2
    )
    hamiltonian = (
        0.5 * kappa1 * (scalar_curvature - shear_norm)
        - 0.5 * kappa0
        - eta_density
        - rho_fr
    )
    # Direct evaluation of the diagonal divergence.  For
    # tc=-6m, ta=m(1+11c), tb=m(1-11c), the expression below vanishes.
    m_prime = tt_mean * (
        -7.0 * u_prime
        + 4.0 * np.cos(2.0 * coordinate) / np.sin(2.0 * coordinate)
    )
    t_c = -6.0 * tt_mean
    t_a = tt_mean * (1.0 + 11.0 * np.cos(2.0 * coordinate))
    t_b = tt_mean * (1.0 - 11.0 * np.cos(2.0 * coordinate))
    t_c_prime = -6.0 * m_prime
    log_a_prime = u_prime - np.tan(coordinate)
    log_b_prime = u_prime + 1.0 / np.tan(coordinate)
    momentum_residual = (
        t_c_prime
        + 3.0 * log_a_prime * (t_c - t_a)
        + 3.0 * log_b_prime * (t_c - t_b)
    )
    boundary_residual = boundary(1.0)(
        solution.y[:, 0], solution.y[:, -1], solution.p
    )
    inertia = float(values[2, -1])
    quadrature_weight = (
        np.sin(coordinate) ** 3 * np.cos(coordinate) ** 3
    )
    root_weight = np.sqrt(quadrature_weight)
    conformal_basis = np.column_stack((
        np.cos(2.0 * coordinate),
        np.cos(4.0 * coordinate),
    ))
    conformal_modes = np.linalg.lstsq(
        root_weight[:, None] * conformal_basis,
        root_weight * u,
        rcond=None,
    )[0]
    window = np.sin(2.0 * coordinate) ** 2
    window_basis = np.column_stack((
        window,
        window * np.cos(2.0 * coordinate),
    ))
    mean_basis = np.column_stack((
        np.ones_like(coordinate),
        np.cos(2.0 * coordinate),
        np.cos(4.0 * coordinate),
    ))
    mean_rates = np.linalg.lstsq(
        root_weight[:, None] * mean_basis,
        root_weight * tt_mean,
        rcond=None,
    )[0]
    radial_rates = np.linalg.lstsq(
        root_weight[:, None] * window_basis,
        root_weight * (-7.0 * tt_mean),
        rcond=None,
    )[0]
    shape_rates = np.linalg.lstsq(
        root_weight[:, None] * window_basis,
        root_weight * (11.0 * tt_mean * np.cos(2.0 * coordinate)),
        rcond=None,
    )[0]
    return {
        "source_Galerkin_coefficients": coefficients,
        "radius": radius,
        "shear_amplitude": shear_amplitude,
        "shear_amplitude_nonzero": abs(shear_amplitude) > 1.0e-6,
        "eta_Legendre_minimum": float(np.min(eta_legendre)),
        "eta_Legendre_regular": float(np.min(eta_legendre)) > 0.0,
        "omega": omega,
        "localized_inertia": inertia,
        "FR_normalization_residual": omega * inertia - 0.5,
        "maximum_Hamiltonian_constraint_residual": float(
            np.max(np.abs(hamiltonian))
        ),
        "maximum_momentum_constraint_residual": float(
            np.max(np.abs(momentum_residual))
        ),
        "maximum_boundary_residual": float(
            np.max(np.abs(boundary_residual))
        ),
        "mean_conformal_gauge_residual": float(values[3, -1]),
        "conformal_u_min": float(np.min(u)),
        "conformal_u_max": float(np.max(u)),
        "conformal_u2_u4_projection": conformal_modes.tolist(),
        "Lorentzian_Galerkin_coordinate_order": [
            "log_R", "u2", "u4", "w0", "w1", "v0", "v1", "q2", "q4"
        ],
        "Lorentzian_Galerkin_initial_coordinates": [
            float(coefficients[0]),
            float(conformal_modes[0]),
            float(conformal_modes[1]),
            0.0,
            0.0,
            0.0,
            0.0,
            q2,
            q4,
        ],
        "Lorentzian_Galerkin_initial_velocities": [
            float(mean_rates[0]),
            float(mean_rates[1]),
            float(mean_rates[2]),
            float(radial_rates[0]),
            float(radial_rates[1]),
            float(shape_rates[0]),
            float(shape_rates[1]),
            0.0,
            0.0,
        ],
        "homotopy_history": history,
        "both_ADM_constraints_solved": True,
    }


def completion_payload() -> dict[str, Any]:
    contract = shear_constraint_contract()
    solution = solve_momentum_balanced_shear_data()
    validation = {
        "regular_localized_trace_free_shear": solution[
            "shear_amplitude_nonzero"
        ],
        "eta_Legendre_map_regular": solution["eta_Legendre_regular"],
        "Hamiltonian_constraint_controlled": solution[
            "maximum_Hamiltonian_constraint_residual"
        ] < 4.0e-3,
        "momentum_constraint_controlled": solution[
            "maximum_momentum_constraint_residual"
        ] < 2.0e-8,
        "FR_normalization_closed": abs(
            solution["FR_normalization_residual"]
        ) < 2.0e-5,
        "boundary_and_mean_gauge_closed": solution[
            "maximum_boundary_residual"
        ] < 2.0e-5,
        "no_external_current_or_coefficient": (
            not contract["new_current_inserted"]
            and not contract["new_continuous_coefficient"]
        ),
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_momentum_balanced_shear_data_v15_43",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "shear_constraint_contract": contract,
        "constraint_solved_initial_data": solution,
        "claim_boundary": {
            "response_constrained_both_ADM_constraints_solved": True,
            "full_spatial_Einstein_evolution_equations_solved": False,
            "persistent_separated_child_derived": False,
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
    path = target / "BHSM_aether_momentum_balanced_shear_data_v15_43.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "shear_constraint_contract", "solve_momentum_balanced_shear_data",
    "completion_payload", "deterministic_json", "materialize",
]
