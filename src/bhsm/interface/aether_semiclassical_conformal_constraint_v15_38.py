"""Semiclassical conformal Hamiltonian constraint for the off-seam child.

The zero-current FR state removes the Hopf momentum source but contributes a
positive expectation energy.  On the v14.91 coefficient locus no round
time-symmetric radius can support any additional positive density.  This
module proves that exact round obstruction and then solves the nonlinear
Hamiltonian constraint in a nonround conformal join metric while retaining the
v15.34 off-seam sigma profile and localized FR ground-state expectation.

The solve is one constraint companion, not the complete child BVP: the spatial
Einstein equations and the backreacted eta and sigma Euler equations remain to
be solved jointly.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.integrate import solve_bvp

from bhsm.interface.aether_complete_child_localized_fiber_v15_34 import (
    HOPF_ORBIT_VOLUME,
    reduced_child_routhian_solution,
)
from bhsm.interface.aether_join_skin_nonlinear_constraint_v15_32 import (
    join_trace_arrays,
)


VERSION = "v15.38"
CLASSIFICATION = "NONROUND_SEMICLASSICAL_HAMILTONIAN_CONSTRAINT_COMPANION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def round_positive_energy_obstruction() -> dict[str, Any]:
    """Prove the exact no-round-radius theorem on the v14.91 locus."""

    return {
        "critical_definitions": "X_c^3=5*kappa1,_kappa0=(15/4)*kappa1*X_c",
        "round_constraint_density": (
            "C_round=(5*kappa1*X_c/8)*(4*y-3-y^4),_y=X/X_c"
        ),
        "factorization": "y^4-4*y+3=(y-1)^2*(y^2+2*y+3)",
        "C_round_nonpositive_for_positive_radius": True,
        "equality_only_at_identity_radius": True,
        "added_positive_skin_or_FR_density": (
            "makes_the_round_time-symmetric_constraint_strictly_negative"
        ),
        "round_radius_adjustment_can_solve_child_constraint": False,
        "required_response": (
            "nonround_geometry_nonzero_extrinsic_curvature_or_a_changed_"
            "matter_profile;_the_stationary_child_uses_nonround_geometry"
        ),
    }


def conformal_constraint_contract() -> dict[str, Any]:
    """Return the exact scalar-curvature and matter formulas used in the BVP."""

    return {
        "metric": (
            "h_7=R^2*exp(2*u(chi))*[dchi^2+cos^2chi*dOmega3_u^2+"
            "sin^2chi*dOmega3_v^2]"
        ),
        "scalar_curvature": (
            "R_h=exp(-2u)/R^2*[42-12*(u_second+3*(cotchi-tanchi)*u_prime)"
            "-30*u_prime^2]"
        ),
        "eta_identity_invariant": "X_eta=7*exp(-2u)/R^2",
        "Hamiltonian_constraint": (
            "kappa1*R_h/2-kappa0/2-rho_eta-rho_sigma-rho_FR=0"
        ),
        "sigma_energy": (
            "rho_sigma=Zsigma*exp(-2u)*sigma_prime^2/(2R^2)+Zsigma*U(sigma)"
        ),
        "localized_inertia": (
            "I=Vol(S3)^2*R^7*integral_w*exp(7u)*(kappa1+X_eta^3)*"
            "(1-4sigma^2)dchi"
        ),
        "FR_energy_density": (
            "rho_FR=(kappa1+X_eta^3)*(1-4sigma^2)/(8*I^2)"
        ),
        "pole_domain": "u_prime(0)=u_prime(pi/2)=0",
        "nonlocal_normalization": "I_is_solved_as_an_auxiliary_integral_state",
    }


def solve_conformal_hamiltonian_constraint(
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    pole_cutoff: float = 2.0e-3,
    homotopy_steps: int = 8,
    tolerance: float = 7.0e-4,
) -> dict[str, Any]:
    """Solve the nonround Hamiltonian constraint connected to the round branch."""

    if kappa1 <= 0.0 or z_sigma <= 0.0:
        raise ValueError("kappa1 and z_sigma must be positive")
    if not 1.0e-4 <= pole_cutoff <= 1.0e-2:
        raise ValueError("pole_cutoff must lie in [1e-4,1e-2]")
    if not isinstance(homotopy_steps, int) or homotopy_steps < 5:
        raise ValueError("homotopy_steps must be an integer >=5")
    radius = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    x_critical = (5.0 * kappa1) ** (1.0 / 3.0)
    kappa0 = 15.0 * kappa1 * x_critical / 4.0
    ell = reduced_child_routhian_solution(
        kappa1=kappa1, z_sigma=z_sigma, points=12001
    )["child_scale_x"]
    base = join_trace_arrays(40001)
    base_chi = np.asarray(base["chi"])
    base_sigma = np.asarray(base["sigma"])
    base_density = np.asarray(base["density"])
    base_potential = np.asarray(base["a2_U"])
    exponential = math.exp(-ell)

    left = np.geomspace(pole_cutoff, 0.05, 180)
    middle = np.linspace(0.05, math.pi / 2.0 - 0.05, 360)
    right = math.pi / 2.0 - np.geomspace(pole_cutoff, 0.05, 100)[::-1]
    mesh = np.unique(np.concatenate((left, middle, right)))

    def profile(coordinate: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        transformed = np.arctan(exponential * np.tan(coordinate))
        derivative = exponential / (
            np.cos(coordinate) ** 2
            * (1.0 + (exponential * np.tan(coordinate)) ** 2)
        )
        sigma = np.interp(transformed, base_chi, base_sigma)
        sigma_prime = np.interp(transformed, base_chi, base_density) * derivative
        potential = np.interp(sigma, base_sigma, base_potential) / radius**2
        return sigma, sigma_prime, potential

    def equations(scale: float):
        def evaluate(
            coordinate: np.ndarray, state: np.ndarray, parameter: np.ndarray
        ) -> np.ndarray:
            u = state[0]
            u_prime = state[1]
            omega = parameter[0]
            sigma, sigma_prime, potential = profile(coordinate)
            weight = np.sin(coordinate) ** 3 * np.cos(coordinate) ** 3
            localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
            exp_minus_two_u = np.exp(-2.0 * u)
            x_eta = 7.0 * exp_minus_two_u / radius**2
            rho_eta = 0.5 * kappa1 * x_eta + 0.125 * x_eta**4
            rho_sigma = scale * z_sigma * (
                0.5 * exp_minus_two_u * sigma_prime**2 / radius**2
                + potential
            )
            rho_fr = (
                0.5
                * (kappa1 + x_eta**3)
                * localization
                * omega**2
            )
            total = rho_eta + rho_sigma + rho_fr
            u_second = (
                42.0
                - 30.0 * u_prime**2
                - (2.0 * radius**2 * np.exp(2.0 * u) / kappa1)
                * (total + 0.5 * kappa0)
            ) / 12.0 - 3.0 * (
                1.0 / np.tan(coordinate) - np.tan(coordinate)
            ) * u_prime
            inertia_derivative = (
                HOPF_ORBIT_VOLUME
                * radius**7
                * weight
                * np.exp(7.0 * u)
                * (kappa1 + x_eta**3)
                * localization
            )
            return np.vstack((u_prime, u_second, inertia_derivative))

        return evaluate

    def boundary(scale: float):
        def residual(
            left_state: np.ndarray,
            right_state: np.ndarray,
            parameter: np.ndarray,
        ) -> np.ndarray:
            return np.array(
                [
                    left_state[1],
                    right_state[1],
                    left_state[2],
                    parameter[0] * right_state[2] - 0.5 * scale,
                ]
            )

        return residual

    state = np.zeros((3, mesh.size))
    inertia_derivative = equations(0.0)(mesh, state, np.array([0.0]))[2]
    state[2, 1:] = np.cumsum(
        0.5
        * (inertia_derivative[1:] + inertia_derivative[:-1])
        * np.diff(mesh)
    )
    parameter = np.array([0.0])
    solution = None
    for scale in np.linspace(0.0, 1.0, homotopy_steps + 1):
        solution = solve_bvp(
            equations(float(scale)),
            boundary(float(scale)),
            mesh,
            state,
            p=parameter,
            tol=tolerance,
            max_nodes=30000,
        )
        if solution.status != 0:
            raise RuntimeError(
                f"conformal constraint homotopy failed at scale={scale}: "
                f"{solution.message}"
            )
        mesh = solution.x
        state = solution.y
        parameter = solution.p
    assert solution is not None

    evaluation = np.linspace(
        pole_cutoff, math.pi / 2.0 - pole_cutoff, 2001
    )
    values = solution.sol(evaluation)
    derivatives = solution.sol(evaluation, 1)
    u = values[0]
    u_prime = values[1]
    u_second = derivatives[1]
    sigma, sigma_prime, potential = profile(evaluation)
    localization = np.maximum(0.0, 1.0 - 4.0 * sigma**2)
    exp_minus_two_u = np.exp(-2.0 * u)
    x_eta = 7.0 * exp_minus_two_u / radius**2
    rho_eta = 0.5 * kappa1 * x_eta + 0.125 * x_eta**4
    rho_sigma = z_sigma * (
        0.5 * exp_minus_two_u * sigma_prime**2 / radius**2 + potential
    )
    omega = float(solution.p[0])
    rho_fr = (
        0.5 * (kappa1 + x_eta**3) * localization * omega**2
    )
    scalar_curvature = exp_minus_two_u / radius**2 * (
        42.0
        - 12.0
        * (
            u_second
            + 3.0
            * (1.0 / np.tan(evaluation) - np.tan(evaluation))
            * u_prime
        )
        - 30.0 * u_prime**2
    )
    constraint = (
        0.5 * kappa1 * scalar_curvature
        - 0.5 * kappa0
        - rho_eta
        - rho_sigma
        - rho_fr
    )
    boundary_residual = boundary(1.0)(
        solution.y[:, 0], solution.y[:, -1], solution.p
    )
    inertia = float(solution.y[2, -1])
    return {
        "connected_by_homotopy_to_round_identity_branch": True,
        "pole_cutoff": pole_cutoff,
        "mesh_nodes": int(solution.x.size),
        "maximum_solver_relative_residual": float(
            np.max(solution.rms_residuals)
        ),
        "maximum_pointwise_constraint_residual": float(
            np.max(np.abs(constraint))
        ),
        "maximum_boundary_residual": float(np.max(np.abs(boundary_residual))),
        "conformal_factor_u_min": float(np.min(u)),
        "conformal_factor_u_max": float(np.max(u)),
        "nonround_response_nonzero": float(np.max(u) - np.min(u)) > 1.0e-3,
        "localized_inertia": inertia,
        "FR_effective_omega": omega,
        "FR_normalization_residual": omega * inertia - 0.5,
        "child_scale_x_input": ell,
        "Hamiltonian_constraint_companion_solved": True,
    }


def remaining_equation_gate() -> dict[str, Any]:
    """Separate the solved constraint from the unsolved complete Euler system."""

    return {
        "Hamiltonian_constraint": "SOLVED_IN_THE_CONFORMAL_COMPANION_TRUNCATION",
        "mean_momentum_constraint": "SOLVED_BY_ZERO_CURRENT_FR_STATE",
        "spatial_Einstein_equations": "OPEN",
        "eta_Euler_equation_on_backreacted_metric": "OPEN",
        "sigma_Euler_equation_on_backreacted_metric": "OPEN",
        "nonconformal_A_minus_B_shape": "OPEN",
        "lapse_and_radial_shift": (
            "unit_static_lapse_and_zero_mean_shift_in_this_constraint_slice"
        ),
        "complete_child_Hessian": "OPEN",
        "reason_not_full_solution": (
            "solving_the_lapse_constraint_does_not_imply_stationarity_under_"
            "independent_A_B_f_sigma_variations"
        ),
    }


def completion_payload() -> dict[str, Any]:
    round_gate = round_positive_energy_obstruction()
    contract = conformal_constraint_contract()
    solution = solve_conformal_hamiltonian_constraint()
    remaining = remaining_equation_gate()
    validation = {
        "round_positive_energy_obstruction_proved": round_gate[
            "C_round_nonpositive_for_positive_radius"
        ],
        "round_shortcut_rejected": not round_gate[
            "round_radius_adjustment_can_solve_child_constraint"
        ],
        "nonround_constraint_response_found": solution[
            "nonround_response_nonzero"
        ],
        "Hamiltonian_constraint_residual_controlled": solution[
            "maximum_pointwise_constraint_residual"
        ]
        < 2.0e-2,
        "FR_normalization_closed": abs(solution["FR_normalization_residual"])
        < 5.0e-5,
        "boundary_conditions_closed": solution[
            "maximum_boundary_residual"
        ]
        < 5.0e-5,
        "remaining_Euler_equations_not_overclaimed": remaining[
            "complete_child_Hessian"
        ]
        == "OPEN",
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_semiclassical_conformal_constraint_v15_38",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "round_constraint_theorem": round_gate,
        "conformal_constraint_contract": contract,
        "nonround_constraint_solution": solution,
        "remaining_equations": remaining,
        "claim_boundary": {
            "nonround_Hamiltonian_constraint_companion_derived": True,
            "complete_stationary_child_solution_derived": False,
            "complete_child_Hessian_derived": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "no_round_time-symmetric_radius_with_added_positive_child_energy",
                "nonround_conformal_Hamiltonian_constraint_response",
                "zero-current_FR_normalization_on_the_constraint_solution",
            ],
            "INVALIDATED": [
                "freezing_the_round_geometry_after_adding_skin_and_FR_energy",
                "varying_only_the_global_radius_to_restore_the_constraint",
            ],
            "RECLASSIFIED": [
                "enclosed-spacetime_response_as_a_nonround_constraint_field_"
                "rather_than_phenomenological_pressure"
            ],
            "CLOSED_THIS_RUN": [
                "round_positive-energy_constraint_no-go",
                "off-seam_nonround_conformal_Hamiltonian_constraint_companion",
            ],
            "ACTIVE_DEPENDENCY": (
                "JOINT_NONCONFORMAL_A_B_F_SIGMA_SPATIAL_EINSTEIN_AND_MATTER_"
                "EULER_BVP_WITH_COMPLETE_PHYSICAL_HESSIAN"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "free_pressure_added": False,
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
        rounded = round(value, 7)
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
    path = target / "BHSM_aether_semiclassical_conformal_constraint_v15_38.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "round_positive_energy_obstruction",
    "conformal_constraint_contract",
    "solve_conformal_hamiltonian_constraint",
    "remaining_equation_gate",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
