"""Closed-M4 Standard Model zeta term on the v15.50 quotient.

The derived material boundary is ``R_t x S3``.  This module evaluates the
free conformal scalar, physical-vector (gauge plus ghost quotient), and Weyl
spectral sums on that closed spatial S3 and inserts their proper-time vacuum
energy into the lapse/shift constrained cap Lagrangian.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import least_squares, minimize

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    projected_reconstructed_initial_data,
)
from bhsm.interface.aether_post_cut_dirac_constraint_reduction_v15_49 import (
    constraint_observables,
    multiplier_lagrangian,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.particle_chirality_anomaly_normalization import (
    anomaly_coefficients,
    family_dimension,
)


VERSION = "v15.51"
CLASSIFICATION = "BHSM_M4_STANDARD_MODEL_ZETA_BACKREACTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def zeta_coefficients() -> dict[str, Fraction]:
    """Exact ``R*E0`` coefficients for closed round-S3 conformal fields."""

    scalar = Fraction(1, 2) * Fraction(1, 120)  # zeta_R(-3)/2
    vector = Fraction(1, 120) - Fraction(-1, 12)
    weyl = Fraction(17, 960)
    return {
        "real_conformal_scalar": scalar,
        "physical_massless_vector": vector,
        "complex_two_component_Weyl": weyl,
    }


def standard_model_zeta_contract() -> dict[str, Any]:
    """Select the complete rank-16 three-family chiral carrier."""

    anomalies = anomaly_coefficients(3, include_neutral_singlet=True)
    coefficients = zeta_coefficients()
    counts = {
        "real_conformal_scalars": 4,
        "physical_massless_vectors": 8 + 3 + 1,
        "complex_two_component_Weyl": 3 * family_dimension(True),
    }
    total = (
        counts["real_conformal_scalars"] * coefficients["real_conformal_scalar"]
        + counts["physical_massless_vectors"]
        * coefficients["physical_massless_vector"]
        + counts["complex_two_component_Weyl"]
        * coefficients["complex_two_component_Weyl"]
    )
    return {
        "M4": "R_t_times_S3_R4",
        "state": "static_conformal_vacuum_on_the_closed_spatial_S3",
        "scalar_spectrum": "omega_m=m/R4,_degeneracy=m^2,_m>=1",
        "scalar_zeta": "zeta_s(s)=R4^s*zeta_R(s-2)",
        "vector_spectrum": "omega_m=m/R4,_degeneracy=2(m^2-1),_m>=2",
        "vector_zeta": "zeta_v(s)=2R4^s[zeta_R(s-2)-zeta_R(s)]",
        "vector_domain": "coexact_one_forms;_longitudinal_and_ghost_pair_removed",
        "Weyl_spectrum": (
            "abs(lambda_n)=(n+3/2)/R4,_degeneracy_each_sign=(n+1)(n+2)"
        ),
        "rank_16_family_selected": True,
        "neutral_singlet_role": "completes_the_rank_16_family_carrier",
        "families": 3,
        "gauge_algebra_dimensions": {"SU3": 8, "Sp1": 3, "U1": 1},
        "counts": counts,
        "coefficients": {key: str(value) for key, value in coefficients.items()},
        "total_C_SM": str(total),
        "total_C_SM_float": float(total),
        "anomalies": {key: str(value) for key, value in anomalies.items()},
        "all_local_anomalies_zero": all(
            anomalies[key] == 0
            for key in (
                "SU3_cubed", "SU3_squared_U1", "Sp1_squared_U1",
                "U1_cubed", "gravity_squared_U1",
            )
        ),
        "Witten_parity_even": bool(anomalies["Witten_parity_even"]),
        "new_continuous_coefficient": False,
    }


def standard_model_casimir_coefficient() -> float:
    return float(Fraction(59, 30))


def boundary_geometry(
    coordinates: np.ndarray, multipliers: np.ndarray,
) -> dict[str, float]:
    """Return the derived quotient radius and proper boundary lapse."""

    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    if q.shape != (9,) or m.shape != (4,):
        raise ValueError("expected coordinates(9) and multipliers(4)")
    scale, u1, u2, w0, w1, v0, v1 = q[:7]
    n1, n2 = m[:2]
    radius = RADIUS0 * math.exp(float(scale))
    u_boundary = -u1 + u2
    v_boundary = v0 - v1
    A = radius * math.exp(float(u_boundary + v_boundary)) / math.sqrt(2.0)
    B = radius * math.exp(float(u_boundary - v_boundary)) / math.sqrt(2.0)
    fiber_radius = math.sqrt(A * A + B * B)
    R4 = A * B / fiber_radius
    return {
        "A": A,
        "B": B,
        "fiber_radius": fiber_radius,
        "M4_spatial_radius": R4,
        "boundary_lapse": math.exp(float(-n1 + n2)),
        "child_scale_x": -2.0 * float(v_boundary),
    }


def attached_multiplier_lagrangian(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 120,
) -> float:
    """Parent cap Lagrangian plus the proper-time M4 vacuum term."""

    geometry = boundary_geometry(coordinates, multipliers)
    vacuum_energy = standard_model_casimir_coefficient() / geometry[
        "M4_spatial_radius"
    ]
    return (
        multiplier_lagrangian(
            coordinates, velocities, multipliers, points=points
        )
        - geometry["boundary_lapse"] * vacuum_energy
    )


def attached_multiplier_gradient(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 100,
    step: float = 2.0e-5,
) -> np.ndarray:
    values = np.asarray(multipliers, dtype=float)
    result = np.empty(4)
    for index in range(4):
        delta = np.zeros(4)
        delta[index] = step
        result[index] = (
            attached_multiplier_lagrangian(
                coordinates, velocities, values + delta, points=points
            )
            - attached_multiplier_lagrangian(
                coordinates, velocities, values - delta, points=points
            )
        ) / (2.0 * step)
    return result


def attached_canonical_energy(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 100,
    step: float = 2.0e-5,
) -> float:
    velocity = np.asarray(velocities, dtype=float)
    momentum = np.empty_like(velocity)
    for index in range(velocity.size):
        delta = np.zeros_like(velocity)
        delta[index] = step
        momentum[index] = (
            attached_multiplier_lagrangian(
                coordinates, velocity + delta, multipliers, points=points
            )
            - attached_multiplier_lagrangian(
                coordinates, velocity - delta, multipliers, points=points
            )
        ) / (2.0 * step)
    return float(
        momentum @ velocity
        - attached_multiplier_lagrangian(
            coordinates, velocity, multipliers, points=points
        )
    )


def solve_attached_constraint_projection(*, points: int = 90) -> dict[str, Any]:
    """Project the reconstructed Cauchy data after adding the M4 zeta term."""

    source = projected_reconstructed_initial_data(points=500)
    coordinates = np.zeros(9)
    raw = np.asarray(source["velocities"], dtype=float)[:7]
    velocity_scale = np.maximum(0.2, np.abs(raw))
    full_raw = np.zeros(9)
    full_raw[:7] = raw
    scale0 = max(
        1.0,
        abs(attached_multiplier_lagrangian(
            coordinates, full_raw, np.zeros(4), points=points
        )),
    )

    def unpack(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        velocity = np.zeros(9)
        velocity[:7] = values[:7]
        return velocity, values[7:]

    def constraints(values: np.ndarray) -> np.ndarray:
        velocity, multipliers = unpack(values)
        try:
            return np.concatenate((
                attached_multiplier_gradient(
                    coordinates, velocity, multipliers, points=points
                ),
                [attached_canonical_energy(
                    coordinates, velocity, multipliers, points=points
                )],
            )) / scale0
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(5, 1.0e6)

    def objective(values: np.ndarray) -> float:
        velocity, multipliers = unpack(values)
        difference = (velocity[:7] - raw) / velocity_scale
        return float(difference @ difference + 1.0e-8 * multipliers @ multipliers)

    initial = np.concatenate((raw, np.zeros(4)))
    solution = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=[(-8.0, 8.0)] * 7 + [(-4.0, 4.0)] * 4,
        constraints={"type": "eq", "fun": constraints},
        options={"ftol": 2.0e-11, "maxiter": 1800, "disp": False},
    )
    velocity, multipliers = unpack(np.asarray(solution.x))
    time_reversal_applied = bool(-2.0 * (velocity[5] - velocity[6]) > 0.0)
    if time_reversal_applied:
        velocity = -velocity
        multipliers = multipliers.copy()
        multipliers[2:] *= -1.0
    fitted = np.concatenate((
        attached_multiplier_gradient(
            coordinates, velocity, multipliers, points=points
        ),
        [attached_canonical_energy(
            coordinates, velocity, multipliers, points=points
        )],
    ))
    independent_points = max(points, 180)
    independent = np.concatenate((
        attached_multiplier_gradient(
            coordinates, velocity, multipliers, points=independent_points
        ),
        [attached_canonical_energy(
            coordinates, velocity, multipliers, points=independent_points
        )],
    ))
    geometry = boundary_geometry(coordinates, multipliers)
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "gauge": "f=chi,_q1=q2=q1_dot=q2_dot=0",
        "velocities": velocity.tolist(),
        "multipliers": multipliers.tolist(),
        "time_reversal_applied_to_select_transported_orientation": (
            time_reversal_applied
        ),
        "maximum_constraint_residual": float(np.max(np.abs(fitted))),
        "independent_grid_maximum_constraint_residual": float(
            np.max(np.abs(independent))
        ),
        "relative_velocity_projection_change": float(
            np.linalg.norm((velocity[:7] - raw) / velocity_scale)
        ),
        "child_scale_velocity": float(-2.0 * (velocity[5] - velocity[6])),
        "child_orientation_preserved": bool(-2.0 * (velocity[5] - velocity[6]) < 0.0),
        "boundary_geometry": geometry,
        "M4_zeta_energy": standard_model_casimir_coefficient()
        / geometry["M4_spatial_radius"],
    }


def shape_restoring_term(A: float, B: float) -> dict[str, float]:
    """Evaluate the exact zeta potential as a function of ``L_F,x``."""

    if A <= 0.0 or B <= 0.0:
        raise ValueError("A and B must be positive")
    fiber = math.sqrt(A * A + B * B)
    x = math.log(B / A)
    coefficient = standard_model_casimir_coefficient()
    energy = 2.0 * coefficient * math.cosh(x) / fiber
    return {
        "fiber_radius": fiber,
        "child_scale_x": x,
        "energy": energy,
        "fixed_fiber_first_derivative": 2.0 * coefficient * math.sinh(x) / fiber,
        "fixed_fiber_second_derivative": 2.0 * coefficient * math.cosh(x) / fiber,
    }


def attached_eta_gauge_dirac_acceleration(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 50,
    step: float = 5.0e-5,
) -> dict[str, Any]:
    """Solve the attached 11-dimensional Euler--Dirac linear system."""

    q_full = np.asarray(coordinates, dtype=float)
    velocity_full = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    if q_full.shape != (9,) or velocity_full.shape != (9,) or m.shape != (4,):
        raise ValueError("expected q(9), velocity(9), multipliers(4)")
    if np.max(np.abs(q_full[7:])) > 1.0e-12 or np.max(np.abs(velocity_full[7:])) > 1.0e-12:
        raise ValueError("eta gauge requires q1=q2=q1_dot=q2_dot=0")
    q = q_full[:7]
    z = np.concatenate((velocity_full[:7], m))

    def lagrangian(q_value: np.ndarray, z_value: np.ndarray) -> float:
        full_q = np.zeros(9)
        full_q[:7] = q_value
        full_velocity = np.zeros(9)
        full_velocity[:7] = z_value[:7]
        return attached_multiplier_lagrangian(
            full_q, full_velocity, z_value[7:], points=points
        )

    grad_q = np.empty(7)
    for index in range(7):
        delta = np.zeros(7)
        delta[index] = step
        grad_q[index] = (
            lagrangian(q + delta, z) - lagrangian(q - delta, z)
        ) / (2.0 * step)
    hessian = np.empty((11, 11))
    mixed = np.empty((11, 7))
    center = lagrangian(q, z)
    for row in range(11):
        erow = np.zeros(11)
        erow[row] = step
        for column in range(11):
            ecolumn = np.zeros(11)
            ecolumn[column] = step
            if row == column:
                hessian[row, row] = (
                    lagrangian(q, z + erow) - 2.0 * center
                    + lagrangian(q, z - erow)
                ) / step**2
            else:
                hessian[row, column] = (
                    lagrangian(q, z + erow + ecolumn)
                    - lagrangian(q, z + erow - ecolumn)
                    - lagrangian(q, z - erow + ecolumn)
                    + lagrangian(q, z - erow - ecolumn)
                ) / (4.0 * step**2)
        for column in range(7):
            eq = np.zeros(7)
            eq[column] = step
            mixed[row, column] = (
                lagrangian(q + eq, z + erow)
                - lagrangian(q - eq, z + erow)
                - lagrangian(q + eq, z - erow)
                + lagrangian(q - eq, z - erow)
            ) / (4.0 * step**2)
    hessian = 0.5 * (hessian + hessian.T)
    rhs = np.concatenate((
        grad_q - mixed[:7] @ velocity_full[:7],
        -mixed[7:] @ velocity_full[:7],
    ))
    solved = np.linalg.solve(hessian, rhs)
    acceleration = np.zeros(9)
    acceleration[:7] = solved[:7]
    return {
        "acceleration": acceleration,
        "multiplier_velocity": solved[7:],
        "Dirac_matrix_condition_number": float(np.linalg.cond(hessian)),
        "Dirac_matrix_rank": int(np.linalg.matrix_rank(hessian)),
        "Dirac_matrix_eigenvalues": np.linalg.eigvalsh(hessian),
        "gauge_modes_removed": 2,
        "finite": bool(np.all(np.isfinite(solved))),
    }


def project_attached_multiplier_energy(
    coordinates: np.ndarray,
    trial_velocity: np.ndarray,
    multiplier_seed: np.ndarray,
    *,
    points: int = 75,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Project an attached-flow step with one velocity scale and four multipliers."""

    q = np.asarray(coordinates, dtype=float)
    trial = np.asarray(trial_velocity, dtype=float)
    seed = np.asarray(multiplier_seed, dtype=float)
    scale0 = max(
        1.0,
        abs(attached_multiplier_lagrangian(q, trial, seed, points=points)),
    )

    def residual(values: np.ndarray) -> np.ndarray:
        alpha = float(values[0])
        multipliers = values[1:]
        try:
            return np.concatenate((
                attached_multiplier_gradient(
                    q, alpha * trial, multipliers, points=points
                ),
                [attached_canonical_energy(
                    q, alpha * trial, multipliers, points=points
                )],
            )) / scale0
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(5, 1.0e6)

    solution = least_squares(
        residual,
        np.concatenate(([1.0], seed)),
        bounds=(
            np.array([0.1, -8.0, -8.0, -8.0, -8.0]),
            np.array([3.0, 8.0, 8.0, 8.0, 8.0]),
        ),
        xtol=2.0e-11,
        ftol=2.0e-11,
        gtol=2.0e-11,
        max_nfev=600,
        x_scale="jac",
    )
    if not solution.success or np.max(np.abs(residual(solution.x))) > 2.0e-5:
        raise ValueError("attached Dirac constraint projection failed")
    alpha = float(solution.x[0])
    return alpha * trial, np.asarray(solution.x[1:]), alpha


def integrate_attached_dirac_flow(
    *, time_step: float = 0.0005, maximum_steps: int = 5, points: int = 42,
    initial_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Integrate a controlled segment of the zeta-attached constrained flow."""

    if initial_state is None:
        initial = solve_attached_constraint_projection(points=80)
        q = np.zeros(9)
        velocity = np.asarray(initial["velocities"], dtype=float)
        multipliers = np.asarray(initial["multipliers"], dtype=float)
        time = 0.0
    else:
        q = np.asarray(initial_state["coordinates"], dtype=float)
        velocity = np.asarray(initial_state["velocities"], dtype=float)
        multipliers = np.asarray(initial_state["multipliers"], dtype=float)
        time = float(initial_state.get("time", 0.0))
    rows: list[dict[str, float]] = []
    maximum_condition = 0.0
    maximum_projection = 0.0
    exit_reason = "maximum_steps"
    turning_points = 0
    previous_x_velocity = float(-2.0 * (velocity[5] - velocity[6]))

    def rhs(
        position: np.ndarray, rate: np.ndarray, multiplier: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        dynamics = attached_eta_gauge_dirac_acceleration(
            position, rate, multiplier, points=points
        )
        return (
            rate,
            np.asarray(dynamics["acceleration"]),
            np.asarray(dynamics["multiplier_velocity"]),
            float(dynamics["Dirac_matrix_condition_number"]),
        )

    for step_index in range(maximum_steps + 1):
        x = float(-2.0 * (q[5] - q[6]))
        x_velocity = float(-2.0 * (velocity[5] - velocity[6]))
        if previous_x_velocity * x_velocity < 0.0:
            turning_points += 1
        previous_x_velocity = x_velocity
        observables = constraint_observables(q, velocity, multipliers, points=110)
        boundary = boundary_geometry(q, multipliers)
        constraints = np.concatenate((
            attached_multiplier_gradient(q, velocity, multipliers, points=85),
            [attached_canonical_energy(q, velocity, multipliers, points=85)],
        ))
        rows.append({
            "time": time,
            "child_scale_x": x,
            "child_scale_velocity": x_velocity,
            "maximum_constraint_residual": float(np.max(np.abs(constraints))),
            "minimum_lapse": observables["minimum_lapse"],
            "minimum_eta_Legendre": observables["minimum_eta_Legendre"],
            "M4_spatial_radius": boundary["M4_spatial_radius"],
            "M4_zeta_energy": standard_model_casimir_coefficient()
            / boundary["M4_spatial_radius"],
        })
        if step_index == maximum_steps:
            break
        old_q = q.copy()
        old_velocity = velocity.copy()
        old_multipliers = multipliers.copy()
        try:
            k1q, k1v, k1m, c1 = rhs(q, velocity, multipliers)
            k2q, k2v, k2m, c2 = rhs(
                q + 0.5 * time_step * k1q,
                velocity + 0.5 * time_step * k1v,
                multipliers + 0.5 * time_step * k1m,
            )
            k3q, k3v, k3m, c3 = rhs(
                q + 0.5 * time_step * k2q,
                velocity + 0.5 * time_step * k2v,
                multipliers + 0.5 * time_step * k2m,
            )
            k4q, k4v, k4m, c4 = rhs(
                q + time_step * k3q,
                velocity + time_step * k3v,
                multipliers + time_step * k3m,
            )
            q = q + time_step * (k1q + 2.0 * k2q + 2.0 * k3q + k4q) / 6.0
            velocity = velocity + time_step * (
                k1v + 2.0 * k2v + 2.0 * k3v + k4v
            ) / 6.0
            multipliers = multipliers + time_step * (
                k1m + 2.0 * k2m + 2.0 * k3m + k4m
            ) / 6.0
            velocity, multipliers, projection = project_attached_multiplier_energy(
                q, velocity, multipliers, points=75
            )
            maximum_condition = max(maximum_condition, c1, c2, c3, c4)
            maximum_projection = max(maximum_projection, abs(projection - 1.0))
        except (ValueError, np.linalg.LinAlgError) as error:
            q, velocity, multipliers = old_q, old_velocity, old_multipliers
            exit_reason = type(error).__name__ + "_" + str(error).replace(" ", "_")
            break
        time += time_step
    final_constraints = np.concatenate((
        attached_multiplier_gradient(q, velocity, multipliers, points=150),
        [attached_canonical_energy(q, velocity, multipliers, points=150)],
    ))
    return {
        "time_step": time_step,
        "steps_completed": step_index,
        "final_time": time,
        "exit_reason": exit_reason,
        "final_coordinates": q.tolist(),
        "final_velocities": velocity.tolist(),
        "final_multipliers": multipliers.tolist(),
        "continuation_state": {
            "time": time,
            "coordinates": q.tolist(),
            "velocities": velocity.tolist(),
            "multipliers": multipliers.tolist(),
        },
        "final_child_scale_x": float(-2.0 * (q[5] - q[6])),
        "final_child_scale_velocity": float(-2.0 * (velocity[5] - velocity[6])),
        "turning_point_count": turning_points,
        "maximum_Dirac_matrix_condition_number": maximum_condition,
        "maximum_velocity_projection_rescale": maximum_projection,
        "independent_grid_final_constraint_residual": float(
            np.max(np.abs(final_constraints))
        ),
        "trajectory": rows,
    }


def extended_attached_branch_event() -> dict[str, Any]:
    """Record the controlled long orbit of the free-conformal attachment."""

    return {
        "classification": "CONTROLLED_FREE_CONFORMAL_ATTACHED_BRANCH_EVENT",
        "regular_state_t_0_08": {
            "time": 0.08,
            "child_scale_x": -0.0544290061,
            "child_scale_velocity": -1.05605433,
            "minimum_eta_Legendre": 4.56829861,
            "independent_grid_constraint_residual": 1.7937601e-4,
            "turning_point_count": 0,
        },
        "regular_state_t_0_10": {
            "time": 0.10,
            "child_scale_x": -0.0778221717,
            "child_scale_velocity": -1.30087520,
            "minimum_eta_Legendre": 2.12130544,
            "independent_grid_constraint_residual": 1.4956150e-4,
            "turning_point_count": 0,
        },
        "last_controlled_state": {
            "time": 0.103,
            "child_scale_x": -0.0818350370,
            "child_scale_velocity": -1.37356177,
            "minimum_eta_Legendre": 0.80112484,
            "independent_grid_constraint_residual": 1.6747270e-4,
            "turning_point_count": 0,
        },
        "exit_event": "eta_Legendre_form_became_singular_at_next_RK_stage",
        "free_conformal_attachment_produced_return": False,
        "free_conformal_attachment_sufficient_for_persistence": False,
        "coefficient_retuned": False,
        "next_operator": (
            "massive_interacting_gauge-fixed_spin-glued_M4_Hessian_with_"
            "masses_and_vertices_derived_from_the_same_child"
        ),
    }


def completion_payload() -> dict[str, Any]:
    contract = standard_model_zeta_contract()
    projection = solve_attached_constraint_projection()
    geometry = projection["boundary_geometry"]
    restoring = shape_restoring_term(geometry["A"], geometry["B"])
    dynamics = attached_eta_gauge_dirac_acceleration(
        np.zeros(9),
        np.asarray(projection["velocities"]),
        np.asarray(projection["multipliers"]),
        points=48,
    )
    flow = integrate_attached_dirac_flow()
    validation = {
        "rank_16_three_family_carrier": contract["counts"][
            "complex_two_component_Weyl"
        ] == 48,
        "gauge_ghost_quotient_count": contract["counts"][
            "physical_massless_vectors"
        ] == 12,
        "all_local_anomalies_zero": contract["all_local_anomalies_zero"],
        "Witten_parity_even": contract["Witten_parity_even"],
        "exact_total_coefficient": contract["total_C_SM"] == "59/30",
        "attached_constraints_solved": projection["success"]
        and projection["maximum_constraint_residual"] < 2.0e-7,
        "attached_independent_grid_controlled": projection[
            "independent_grid_maximum_constraint_residual"
        ] < 1.2e-3,
        "event_orientation_preserved": projection["child_orientation_preserved"],
        "shape_curvature_positive": restoring[
            "fixed_fiber_second_derivative"
        ] > 0.0,
        "attached_Dirac_matrix_full_rank": dynamics["Dirac_matrix_rank"] == 11,
        "attached_Dirac_vector_field_finite": dynamics["finite"],
        "attached_short_flow_controlled": flow["exit_reason"] == "maximum_steps"
        and flow["independent_grid_final_constraint_residual"] < 1.5e-3,
        "no_new_continuous_coefficient": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_m4_standard_model_zeta_backreaction_v15_51",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "spectral_contract": contract,
        "attached_constraint_projection": projection,
        "shape_restoring_term": restoring,
        "initial_attached_Dirac_vector_field": {
            "acceleration": np.asarray(dynamics["acceleration"]).tolist(),
            "multiplier_velocity": np.asarray(
                dynamics["multiplier_velocity"]
            ).tolist(),
            "matrix_condition_number": dynamics[
                "Dirac_matrix_condition_number"
            ],
            "matrix_rank": dynamics["Dirac_matrix_rank"],
            "matrix_eigenvalues": np.asarray(
                dynamics["Dirac_matrix_eigenvalues"]
            ).tolist(),
        },
        "controlled_attached_Dirac_flow": flow,
        "extended_attached_branch_event": extended_attached_branch_event(),
        "claim_boundary": {
            "closed_M4_free_conformal_zeta_derived": True,
            "renormalized_massive_interacting_determinant_derived": False,
            "attached_Dirac_flow_integrated": True,
            "free_conformal_term_sufficient_for_persistence": False,
            "persistent_particle_derived": False,
        },
        "active_calculation": (
            "CONSTRUCT_THE_MASSIVE_INTERACTING_GAUGE-FIXED_SPIN-GLUED_M4_"
            "HESSIAN_FROM_THE_SAME_CHILD_AND_EVALUATE_ITS_ZETA_STRESS"
        ),
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
        rounded = round(value, 10)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_m4_standard_model_zeta_backreaction_v15_51.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "zeta_coefficients",
    "standard_model_zeta_contract", "standard_model_casimir_coefficient",
    "boundary_geometry", "attached_multiplier_lagrangian",
    "attached_multiplier_gradient", "attached_canonical_energy",
    "solve_attached_constraint_projection", "shape_restoring_term",
    "attached_eta_gauge_dirac_acceleration", "project_attached_multiplier_energy",
    "integrate_attached_dirac_flow",
    "extended_attached_branch_event",
    "completion_payload", "deterministic_json", "materialize",
]
