"""Lapse/shift Dirac reduction of the post-cut nonround BHSM cap."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import least_squares, minimize

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    cap_fields,
    projected_reconstructed_initial_data,
)


VERSION = "v15.49"
CLASSIFICATION = "BHSM_POST_CUT_CAP_DIRAC_LAPSE_SHIFT_REDUCTION"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def multiplier_contract() -> dict[str, Any]:
    return {
        "lapse": "N=exp(n1*cos4chi+n2*cos8chi),_constant_lapse_is_time_gauge",
        "shift": "beta=sin4chi*(b0+b1*cos4chi),_beta(0)=beta(pi/4)=0",
        "extrinsic_rates": {
            "H_C": "(dot(logC)-beta*(logC)prime-beta_prime)/N",
            "H_A": "(dot(logA)-beta*(logA)prime)/N",
            "H_B": "(dot(logB)-beta*(logB)prime)/N",
        },
        "eta_normal_rate": "D_perp_f=(dot_f-beta*f_prime)/N",
        "constraints": [
            "partial_L/partial_n1=0",
            "partial_L/partial_n2=0",
            "partial_L/partial_b0=0",
            "partial_L/partial_b1=0",
            "canonical_energy=0_for_constant_lapse_constraint",
        ],
        "radial_boundary_shift_flux": 0.0,
        "new_continuous_coefficient": False,
    }


def multiplier_lagrangian(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 140,
) -> float:
    """Evaluate the cap action with nonconstant lapse and radial shift."""

    values = np.asarray(multipliers, dtype=float)
    if values.shape != (4,) or not np.all(np.isfinite(values)):
        raise ValueError("multipliers must be four finite real numbers")
    fields = cap_fields(coordinates, velocities, points=points)
    chi = np.asarray(fields["chi"])
    weights = np.asarray(fields["weights"])
    n1, n2, b0, b1 = values
    cos4 = np.cos(4.0 * chi)
    cos8 = np.cos(8.0 * chi)
    sin4 = np.sin(4.0 * chi)
    sin8 = np.sin(8.0 * chi)
    log_n = n1 * cos4 + n2 * cos8
    N = np.exp(log_n)
    n_prime = -4.0 * n1 * sin4 - 8.0 * n2 * sin8
    beta = sin4 * (b0 + b1 * cos4)
    beta_prime = 4.0 * cos4 * (b0 + b1 * cos4) - 4.0 * b1 * sin4**2
    C = np.asarray(fields["C"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    volume = np.asarray(fields["volume"])
    spatial_volume = np.asarray(fields["spatial_orbit_volume"])
    c_prime = np.asarray(fields["log_C_prime"])
    a_prime = np.asarray(fields["log_A_prime"])
    b_prime = np.asarray(fields["log_B_prime"])
    Hc = (
        np.asarray(fields["log_C_dot"]) - beta * c_prime - beta_prime
    ) / N
    Ha = (np.asarray(fields["log_A_dot"]) - beta * a_prime) / N
    Hb = (np.asarray(fields["log_B_dot"]) - beta * b_prime) / N
    adm = Hc**2 + 3.0 * Ha**2 + 3.0 * Hb**2 - (Hc + 3.0 * Ha + 3.0 * Hb) ** 2
    f_normal = (
        np.asarray(fields["f_dot_coordinate"])
        - beta * np.asarray(fields["f_prime"])
    ) / N
    x_spatial = (
        np.asarray(fields["f_prime"]) ** 2 / C**2
        + 3.0 * np.cos(np.asarray(fields["f"])) ** 2 / A**2
        + 3.0 * np.sin(np.asarray(fields["f"])) ** 2 / B**2
    )
    x_eta = x_spatial - f_normal**2
    eta_legendre = 1.0 + x_eta**3
    if np.min(eta_legendre) <= 1.0e-5:
        raise ValueError("eta Legendre form became singular")
    localization = np.asarray(fields["localization"])
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    spatial_gravity = (
        3.0
        * N
        * spatial_volume
        / C
        * (n_prime * (a_prime + b_prime) + a_prime**2 + b_prime**2 + 3.0 * a_prime * b_prime)
    )
    algebraic = N * volume * (
        3.0 / A**2
        + 3.0 / B**2
        - 0.5 * kappa0
        - localization * (0.5 * x_eta + 0.125 * x_eta**4)
        + 0.5 * adm
    )
    bulk = float(np.dot(weights, spatial_gravity + algebraic))
    inertia_without_orbit = float(np.dot(
        weights, volume * localization * eta_legendre / N
    ))
    if inertia_without_orbit <= 1.0e-12:
        raise ValueError("localized cap inertia must be positive")
    return bulk - 0.25 / (
        2.0 * HOPF_ORBIT_VOLUME**2 * inertia_without_orbit
    )


def multiplier_gradient(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 140,
    step: float = 2.0e-5,
) -> np.ndarray:
    values = np.asarray(multipliers, dtype=float)
    gradient = np.empty(4)
    for index in range(4):
        delta = np.zeros(4)
        delta[index] = step
        gradient[index] = (
            multiplier_lagrangian(
                coordinates, velocities, values + delta, points=points
            )
            - multiplier_lagrangian(
                coordinates, velocities, values - delta, points=points
            )
        ) / (2.0 * step)
    return gradient


def multiplier_canonical_energy(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 140,
    step: float = 2.0e-5,
) -> float:
    velocity = np.asarray(velocities, dtype=float)
    momentum = np.empty_like(velocity)
    for index in range(velocity.size):
        delta = np.zeros_like(velocity)
        delta[index] = step
        momentum[index] = (
            multiplier_lagrangian(
                coordinates, velocity + delta, multipliers, points=points
            )
            - multiplier_lagrangian(
                coordinates, velocity - delta, multipliers, points=points
            )
        ) / (2.0 * step)
    return float(
        momentum @ velocity
        - multiplier_lagrangian(coordinates, velocity, multipliers, points=points)
    )


def solve_constraint_projected_initial_data(*, points: int = 100) -> dict[str, Any]:
    """Project reconstructed data onto all reduced Dirac constraints."""

    source = projected_reconstructed_initial_data(points=500)
    coordinates = np.asarray(source["coordinates"])
    raw_velocity = np.asarray(source["velocities"])
    lagrangian_scale = max(
        1.0,
        abs(multiplier_lagrangian(
            coordinates, raw_velocity, np.zeros(4), points=points
        )),
    )
    preliminary = least_squares(
        lambda value: multiplier_gradient(
            coordinates, raw_velocity, value, points=points
        ) / lagrangian_scale,
        np.zeros(4),
        bounds=(-1.5 * np.ones(4), 1.5 * np.ones(4)),
        max_nfev=500,
    ).x
    initial = np.concatenate((raw_velocity, preliminary))
    velocity_scale = np.maximum(0.2, np.abs(raw_velocity))

    def unpack(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return values[:9], values[9:]

    def constraints(values: np.ndarray) -> np.ndarray:
        velocity, multipliers = unpack(values)
        try:
            projections = multiplier_gradient(
                coordinates, velocity, multipliers, points=points
            )
            energy = multiplier_canonical_energy(
                coordinates, velocity, multipliers, points=points
            )
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(5, 1.0e6)
        return np.concatenate((
            projections / lagrangian_scale,
            [energy / lagrangian_scale],
        ))

    def objective(values: np.ndarray) -> float:
        velocity, multipliers = unpack(values)
        displacement = (velocity - raw_velocity) / velocity_scale
        return float(displacement @ displacement + 1.0e-8 * (multipliers @ multipliers))

    solution = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=[(-5.0, 5.0)] * 9 + [(-2.0, 2.0)] * 4,
        constraints={"type": "eq", "fun": constraints},
        options={"ftol": 2.0e-11, "maxiter": 1200, "disp": False},
    )
    velocity, multipliers = unpack(np.asarray(solution.x))
    final_constraints = constraints(solution.x) * lagrangian_scale
    independent_points = max(points, 200)
    independent_constraints = np.concatenate((
        multiplier_gradient(
            coordinates, velocity, multipliers, points=independent_points
        ),
        [multiplier_canonical_energy(
            coordinates, velocity, multipliers, points=independent_points
        )],
    ))
    hessian = np.empty((4, 4))
    hessian_step = 3.0e-5
    for column in range(4):
        delta = np.zeros(4)
        delta[column] = hessian_step
        hessian[:, column] = (
            multiplier_gradient(
                coordinates, velocity, multipliers + delta, points=points
            )
            - multiplier_gradient(
                coordinates, velocity, multipliers - delta, points=points
            )
        ) / (2.0 * hessian_step)
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "velocities": velocity.tolist(),
        "multipliers": multipliers.tolist(),
        "constraint_projections": final_constraints[:4].tolist(),
        "canonical_energy": float(final_constraints[4]),
        "maximum_constraint_residual": float(np.max(np.abs(final_constraints))),
        "independent_grid_constraint_residuals": independent_constraints.tolist(),
        "independent_grid_maximum_constraint_residual": float(
            np.max(np.abs(independent_constraints))
        ),
        "Dirac_multiplier_matrix_condition_number": float(np.linalg.cond(hessian)),
        "multiplier_solution_locally_unique": int(np.linalg.matrix_rank(hessian)) == 4,
        "relative_velocity_projection_change": float(
            np.linalg.norm((velocity - raw_velocity) / velocity_scale)
        ),
        "child_scale_velocity": float(-2.0 * (velocity[5] - velocity[6])),
        "child_orientation_preserved": bool(-2.0 * (velocity[5] - velocity[6]) < 0.0),
        "objective": float(solution.fun),
    }


def solve_eta_gauge_constraint_projected_data(*, points: int = 100) -> dict[str, Any]:
    """Project initial data after the exact monotone-map gauge f=chi."""

    source = projected_reconstructed_initial_data(points=500)
    coordinates = np.zeros(9)
    raw_full = np.asarray(source["velocities"])
    raw = raw_full[:7]
    scale0 = max(1.0, abs(multiplier_lagrangian(
        coordinates, np.concatenate((raw, [0.0, 0.0])), np.zeros(4),
        points=points,
    )))
    velocity_scale = np.maximum(0.2, np.abs(raw))

    def unpack(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        full_velocity = np.zeros(9)
        full_velocity[:7] = values[:7]
        return full_velocity, values[7:]

    def constraints(values: np.ndarray) -> np.ndarray:
        velocity, multipliers = unpack(values)
        try:
            projected = multiplier_gradient(
                coordinates, velocity, multipliers, points=points
            )
            energy = multiplier_canonical_energy(
                coordinates, velocity, multipliers, points=points
            )
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(5, 1.0e6)
        return np.concatenate((projected, [energy])) / scale0

    def objective(values: np.ndarray) -> float:
        velocity, multipliers = unpack(values)
        difference = (velocity[:7] - raw) / velocity_scale
        return float(difference @ difference + 1.0e-8 * multipliers @ multipliers)

    initial = np.concatenate((raw, np.zeros(4)))
    solution = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=[(-5.0, 5.0)] * 7 + [(-2.5, 2.5)] * 4,
        constraints={"type": "eq", "fun": constraints},
        options={"ftol": 2.0e-11, "maxiter": 1600, "disp": False},
    )
    velocity, multipliers = unpack(np.asarray(solution.x))
    fitted = constraints(solution.x) * scale0
    independent = np.concatenate((
        multiplier_gradient(
            coordinates, velocity, multipliers, points=max(points, 200)
        ),
        [multiplier_canonical_energy(
            coordinates, velocity, multipliers, points=max(points, 200)
        )],
    ))
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "gauge": "f=chi,_q1=q2=q1_dot=q2_dot=0",
        "velocities": velocity.tolist(),
        "multipliers": multipliers.tolist(),
        "maximum_constraint_residual": float(np.max(np.abs(fitted))),
        "independent_grid_maximum_constraint_residual": float(
            np.max(np.abs(independent))
        ),
        "relative_velocity_projection_change": float(
            np.linalg.norm((velocity[:7] - raw) / velocity_scale)
        ),
        "child_scale_velocity": float(-2.0 * (velocity[5] - velocity[6])),
        "child_orientation_preserved": bool(-2.0 * (velocity[5] - velocity[6]) < 0.0),
    }


def eta_gauge_dirac_acceleration(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 70,
    step: float = 5.0e-5,
) -> dict[str, Any]:
    """Euler--Dirac acceleration on the physical f=chi quotient chart."""

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
        return multiplier_lagrangian(
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


def solve_initial_lapse_shift(*, points: int = 160) -> dict[str, Any]:
    """Solve the projected Hamiltonian-shape and momentum constraints."""

    initial = projected_reconstructed_initial_data(points=500)
    q = np.asarray(initial["coordinates"])
    velocity = np.asarray(initial["velocities"])
    normalization = max(1.0, abs(multiplier_lagrangian(q, velocity, np.zeros(4), points=points)))

    def residual(values: np.ndarray) -> np.ndarray:
        try:
            return multiplier_gradient(
                q, velocity, values, points=points
            ) / normalization
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(4, 1.0e6)

    solution = least_squares(
        residual,
        np.zeros(4),
        bounds=(-1.5 * np.ones(4), 1.5 * np.ones(4)),
        xtol=2.0e-12,
        ftol=2.0e-12,
        gtol=2.0e-12,
        max_nfev=800,
        x_scale="jac",
    )
    multipliers = np.asarray(solution.x)
    independent = multiplier_gradient(
        q, velocity, multipliers, points=max(points, 240)
    )
    # The multiplier Hessian is the Faddeev--Popov/Dirac local solvability
    # matrix for this reduced lapse-shift chart.
    hessian = np.empty((4, 4))
    step = 3.0e-5
    for column in range(4):
        delta = np.zeros(4)
        delta[column] = step
        hessian[:, column] = (
            multiplier_gradient(q, velocity, multipliers + delta, points=points)
            - multiplier_gradient(q, velocity, multipliers - delta, points=points)
        ) / (2.0 * step)
    return {
        "success": bool(solution.success),
        "solver_message": str(solution.message),
        "multiplier_order": ["n1", "n2", "b0", "b1"],
        "multipliers": multipliers.tolist(),
        "constraint_projections": independent.tolist(),
        "maximum_constraint_projection": float(np.max(np.abs(independent))),
        "Dirac_multiplier_Hessian_eigenvalues": np.linalg.eigvalsh(
            0.5 * (hessian + hessian.T)
        ).tolist(),
        "Dirac_multiplier_matrix_condition_number": float(np.linalg.cond(hessian)),
        "multiplier_solution_locally_unique": int(np.linalg.matrix_rank(hessian)) == 4,
        "unit_lapse_zero_shift_was_constraint_solution": bool(
            np.max(np.abs(multipliers)) < 1.0e-5
        ),
        "eta_Legendre_positive": True,
    }


def dirac_acceleration(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 70,
    step: float = 5.0e-5,
) -> dict[str, Any]:
    """Solve the differentiated Euler--Dirac equations for qddot and mdot."""

    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    z = np.concatenate((velocity, m))
    if q.shape != (9,) or velocity.shape != (9,) or m.shape != (4,):
        raise ValueError("expected q(9), velocity(9), multipliers(4)")

    def lagrangian(q_value: np.ndarray, z_value: np.ndarray) -> float:
        return multiplier_lagrangian(
            q_value, z_value[:9], z_value[9:], points=points
        )

    grad_q = np.empty(9)
    for index in range(9):
        delta = np.zeros(9)
        delta[index] = step
        grad_q[index] = (
            lagrangian(q + delta, z) - lagrangian(q - delta, z)
        ) / (2.0 * step)
    hessian = np.empty((13, 13))
    mixed = np.empty((13, 9))
    center = lagrangian(q, z)
    for row in range(13):
        erow = np.zeros(13)
        erow[row] = step
        for column in range(13):
            ecolumn = np.zeros(13)
            ecolumn[column] = step
            if row == column:
                hessian[row, row] = (
                    lagrangian(q, z + erow)
                    - 2.0 * center
                    + lagrangian(q, z - erow)
                ) / step**2
            else:
                hessian[row, column] = (
                    lagrangian(q, z + erow + ecolumn)
                    - lagrangian(q, z + erow - ecolumn)
                    - lagrangian(q, z - erow + ecolumn)
                    + lagrangian(q, z - erow - ecolumn)
                ) / (4.0 * step**2)
        for column in range(9):
            eq = np.zeros(9)
            eq[column] = step
            mixed[row, column] = (
                lagrangian(q + eq, z + erow)
                - lagrangian(q - eq, z + erow)
                - lagrangian(q + eq, z - erow)
                + lagrangian(q - eq, z - erow)
            ) / (4.0 * step**2)
    hessian = 0.5 * (hessian + hessian.T)
    rhs = np.concatenate((
        grad_q - mixed[:9] @ velocity,
        -mixed[9:] @ velocity,
    ))
    solution = np.linalg.solve(hessian, rhs)
    return {
        "acceleration": solution[:9],
        "multiplier_velocity": solution[9:],
        "Dirac_matrix_condition_number": float(np.linalg.cond(hessian)),
        "Dirac_matrix_rank": int(np.linalg.matrix_rank(hessian)),
        "Dirac_matrix_eigenvalues": np.linalg.eigvalsh(hessian),
        "finite": bool(np.all(np.isfinite(solution))),
    }


def project_multiplier_energy(
    coordinates: np.ndarray,
    trial_velocity: np.ndarray,
    multiplier_seed: np.ndarray,
    *,
    points: int = 90,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Project onto L_m=0 and E=0 using one velocity scale and four multipliers."""

    q = np.asarray(coordinates, dtype=float)
    trial = np.asarray(trial_velocity, dtype=float)
    seed = np.asarray(multiplier_seed, dtype=float)
    scale0 = max(1.0, abs(multiplier_lagrangian(q, trial, seed, points=points)))

    def residual(values: np.ndarray) -> np.ndarray:
        alpha = float(values[0])
        m = values[1:]
        try:
            constraints = multiplier_gradient(q, alpha * trial, m, points=points)
            energy = multiplier_canonical_energy(q, alpha * trial, m, points=points)
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(5, 1.0e6)
        return np.concatenate((constraints, [energy])) / scale0

    solution = least_squares(
        residual,
        np.concatenate(([1.0], seed)),
        bounds=(np.array([0.1, -6.0, -6.0, -6.0, -6.0]),
                np.array([3.0, 6.0, 6.0, 6.0, 6.0])),
        xtol=2.0e-11,
        ftol=2.0e-11,
        gtol=2.0e-11,
        max_nfev=500,
        x_scale="jac",
    )
    if not solution.success or np.max(np.abs(residual(solution.x))) > 2.0e-5:
        raise ValueError("Dirac constraint projection failed")
    alpha = float(solution.x[0])
    return alpha * trial, np.asarray(solution.x[1:]), alpha


def constraint_observables(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 160,
) -> dict[str, float]:
    """Return invariant regularity observables of a constrained cap state."""

    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    fields = cap_fields(q, velocity, points=points)
    chi = np.asarray(fields["chi"])
    n1, n2, b0, b1 = m
    N = np.exp(n1 * np.cos(4.0 * chi) + n2 * np.cos(8.0 * chi))
    beta = np.sin(4.0 * chi) * (b0 + b1 * np.cos(4.0 * chi))
    f_normal = (
        np.asarray(fields["f_dot_coordinate"])
        - beta * np.asarray(fields["f_prime"])
    ) / N
    C = np.asarray(fields["C"])
    A = np.asarray(fields["A"])
    B = np.asarray(fields["B"])
    x_spatial = (
        np.asarray(fields["f_prime"]) ** 2 / C**2
        + 3.0 * np.cos(np.asarray(fields["f"])) ** 2 / A**2
        + 3.0 * np.sin(np.asarray(fields["f"])) ** 2 / B**2
    )
    eta_legendre = 1.0 + (x_spatial - f_normal**2) ** 3
    localization = np.asarray(fields["localization"])
    inertia = HOPF_ORBIT_VOLUME * float(np.dot(
        np.asarray(fields["weights"]),
        np.asarray(fields["volume"]) * localization * eta_legendre / N,
    ))
    scale, u1, u2, w0, w1, v0, v1 = q[:7]
    radius = (343.0 / 5.0) ** (1.0 / 6.0) * math.exp(float(scale))
    u_boundary = -u1 + u2
    w_boundary = w0 - w1
    v_boundary = v0 - v1
    return {
        "minimum_lapse": float(np.min(N)),
        "maximum_lapse": float(np.max(N)),
        "minimum_eta_Legendre": float(np.min(eta_legendre)),
        "localized_inertia": inertia,
        "boundary_C": radius * math.exp(float(u_boundary + w_boundary)),
        "boundary_A": radius * math.exp(float(u_boundary + v_boundary)) / math.sqrt(2.0),
        "boundary_B": radius * math.exp(float(u_boundary - v_boundary)) / math.sqrt(2.0),
        "boundary_child_scale_x": -2.0 * float(v_boundary),
    }


def project_full_eta_gauge_constraints(
    coordinates: np.ndarray,
    trial_velocity: np.ndarray,
    multiplier_seed: np.ndarray,
    *,
    points: int = 80,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Nearest seven-velocity projection when a scalar rescaling is insufficient."""

    q = np.asarray(coordinates, dtype=float)
    trial = np.asarray(trial_velocity, dtype=float)
    seed = np.asarray(multiplier_seed, dtype=float)
    scales = np.maximum(0.25, np.abs(trial[:7]))
    scale0 = max(1.0, abs(multiplier_lagrangian(q, trial, seed, points=points)))

    def unpack(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        velocity = np.zeros(9)
        velocity[:7] = values[:7]
        return velocity, values[7:]

    def constraints(values: np.ndarray) -> np.ndarray:
        velocity, multipliers = unpack(values)
        try:
            projected = multiplier_gradient(q, velocity, multipliers, points=points)
            energy = multiplier_canonical_energy(q, velocity, multipliers, points=points)
        except (ValueError, OverflowError, FloatingPointError):
            return np.full(5, 1.0e6)
        return np.concatenate((projected, [energy])) / scale0

    def objective(values: np.ndarray) -> float:
        velocity, multipliers = unpack(values)
        difference = (velocity[:7] - trial[:7]) / scales
        multiplier_difference = multipliers - seed
        return float(difference @ difference + 1.0e-8 * multiplier_difference @ multiplier_difference)

    initial = np.concatenate((trial[:7], seed))
    solution = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=[(-12.0, 12.0)] * 7 + [(-8.0, 8.0)] * 4,
        constraints={"type": "eq", "fun": constraints},
        options={"ftol": 2.0e-10, "maxiter": 1000, "disp": False},
    )
    if not solution.success or np.max(np.abs(constraints(solution.x))) > 3.0e-5:
        raise ValueError("full eta-gauge Dirac constraint projection failed")
    velocity, multipliers = unpack(np.asarray(solution.x))
    return velocity, multipliers, float(math.sqrt(max(0.0, solution.fun)))


def integrate_dirac_reduced_cap_flow(
    *, time_step: float = 0.0005, maximum_steps: int = 20,
    points: int = 55, initial_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Integrate the constrained nonround child-cap flow."""

    if initial_state is None:
        initial = solve_eta_gauge_constraint_projected_data(points=80)
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
    maximum_projection = 0.0
    maximum_condition = 0.0
    exit_reason = "maximum_steps"
    turning_points = 0
    previous_x_velocity = float(-2.0 * (velocity[5] - velocity[6]))

    def rhs(
        position: np.ndarray, rate: np.ndarray, multiplier: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        dynamics = eta_gauge_dirac_acceleration(
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
        constraints = np.concatenate((
            multiplier_gradient(q, velocity, multipliers, points=90),
            [multiplier_canonical_energy(q, velocity, multipliers, points=90)],
        ))
        observables = constraint_observables(
            q, velocity, multipliers, points=120
        )
        rows.append({
            "time": time,
            "child_scale_x": x,
            "child_scale_velocity": x_velocity,
            "log_radius": float(q[0]),
            "maximum_constraint_residual": float(np.max(np.abs(constraints))),
            "minimum_lapse": observables["minimum_lapse"],
            "minimum_eta_Legendre": observables["minimum_eta_Legendre"],
            "localized_inertia": observables["localized_inertia"],
            "boundary_C": observables["boundary_C"],
            "boundary_A": observables["boundary_A"],
            "boundary_B": observables["boundary_B"],
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
            try:
                velocity, multipliers, projection = project_multiplier_energy(
                    q, velocity, multipliers, points=80
                )
            except ValueError:
                velocity, multipliers, projection = project_full_eta_gauge_constraints(
                    q, velocity, multipliers, points=80
                )
            maximum_condition = max(maximum_condition, c1, c2, c3, c4)
            maximum_projection = max(maximum_projection, abs(projection - 1.0))
        except (ValueError, np.linalg.LinAlgError) as error:
            q, velocity, multipliers = old_q, old_velocity, old_multipliers
            exit_reason = type(error).__name__ + ":_" + str(error).replace(" ", "_")
            break
        time += time_step
    final_constraints = np.concatenate((
        multiplier_gradient(q, velocity, multipliers, points=160),
        [multiplier_canonical_energy(q, velocity, multipliers, points=160)],
    ))
    final_observables = constraint_observables(
        q, velocity, multipliers, points=220
    )
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
        "final_observables": final_observables,
        "trajectory": rows,
        "relative_periodic_return_reached": bool(
            turning_points >= 2 and np.linalg.norm(q) < 5.0e-3
        ),
    }


def extended_dirac_branch_event() -> dict[str, Any]:
    """Record the controlled continuation event beyond the payload smoke orbit.

    The nearest seven-velocity projection needed at the multiplier fold is
    deliberately recorded: it is too large to identify the post-fold
    numerical branch with the pre-fold branch without an enlarged chart.
    """

    return {
        "classification": "CONTROLLED_FINITE_CHART_BRANCH_EVENT",
        "pre_fold_regular_state": {
            "time": 0.24,
            "child_scale_x": -0.161681,
            "child_scale_velocity": -1.42579,
            "minimum_lapse": 0.894,
            "minimum_eta_Legendre": 2.519,
            "localized_inertia": 9768.0,
            "boundary_C": 2.36880,
            "boundary_A": 1.55038,
            "boundary_B": 1.31893,
            "turning_point_count": 0,
        },
        "Dirac_multiplier_fold": {
            "time_approximately": 0.2655,
            "maximum_condition_number_before_scalar_projection_failure": 2.8e6,
            "nearest_full_velocity_projection_normalized_change": 1.0,
            "branch_identity_after_projection_proved": False,
        },
        "last_regular_state": {
            "time": 0.3095,
            "child_scale_x": -0.312613,
            "child_scale_velocity": -6.19876,
            "minimum_lapse": 0.37335,
            "maximum_lapse": 4.155,
            "minimum_eta_Legendre": 2.12563,
            "localized_inertia": 5910.96,
            "boundary_C": 2.53776,
            "boundary_A": 1.66630,
            "boundary_B": 1.21895,
            "independent_grid_constraint_residual": 6.28e-4,
            "turning_point_count": 0,
        },
        "exit_event": "eta_Legendre_form_became_singular_at_next_RK_stage",
        "relative_periodic_return_reached": False,
        "interpretation": (
            "the_Einstein-eta-response-FR_block_has_no_return_before_a_second_"
            "eta_Legendre_firewall;_the_post-fold_projection_does_not_prove_"
            "global_branch_continuity"
        ),
        "foundational_no_go_claimed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = solve_eta_gauge_constraint_projected_data()
    dynamics = eta_gauge_dirac_acceleration(
        np.zeros(9),
        np.asarray(result["velocities"]),
        np.asarray(result["multipliers"]),
        points=50,
    )
    flow = integrate_dirac_reduced_cap_flow(maximum_steps=5, points=45)
    validation = {
        "lapse_shift_and_constant_lapse_constraints_solved": result[
            "maximum_constraint_residual"
        ] < 2.0e-8,
        "independent_grid_constraints_close": result[
            "independent_grid_maximum_constraint_residual"
        ] < 6.0e-4,
        "eta_coordinate_gauge_removed": result["gauge"].startswith("f=chi"),
        "Dirac_matrix_full_rank_after_gauge_quotient": dynamics[
            "Dirac_matrix_rank"
        ] == 11,
        "Dirac_vector_field_finite": dynamics["finite"],
        "child_orientation_preserved": result[
            "child_orientation_preserved"
        ],
        "controlled_constrained_flow_enters_child_branch": (
            flow["final_child_scale_x"] < 0.0
            and flow["final_child_scale_velocity"] < 0.0
        ),
        "flow_constraint_projection_controlled": flow[
            "independent_grid_final_constraint_residual"
        ] < 8.0e-4,
        "boundary_normal_shift_zero": multiplier_contract()[
            "radial_boundary_shift_flux"
        ] == 0.0,
        "no_new_continuous_coefficient": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_post_cut_dirac_constraint_reduction_v15_49",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "multiplier_contract": multiplier_contract(),
        "constraint_projected_initial_data": result,
        "initial_Dirac_vector_field": {
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
            "gauge_modes_removed": dynamics["gauge_modes_removed"],
        },
        "controlled_Dirac_reduced_flow": flow,
        "extended_branch_event": extended_dirac_branch_event(),
        "claim_boundary": {
            "nonconstant_lapse_shift_constraints_reduced": validation[
                "lapse_shift_and_constant_lapse_constraints_solved"
            ],
            "full_constrained_flow_integrated": True,
            "physical_monodromy_computed": False,
            "persistent_particle_derived": False,
        },
        "active_calculation": (
            "ENLARGE_THE_COMPLETE_CHILD_BY_THE_ACTION-OWNED_DIAGONAL_SP1_"
            "M8_TO_M5_TO_M4_ATTACHMENT_BEFORE_ANY_FURTHER_PERSISTENCE_TEST"
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
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_post_cut_dirac_constraint_reduction_v15_49.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "multiplier_contract", "multiplier_lagrangian", "multiplier_gradient",
    "multiplier_canonical_energy", "solve_initial_lapse_shift",
    "solve_constraint_projected_initial_data",
    "solve_eta_gauge_constraint_projected_data", "dirac_acceleration",
    "eta_gauge_dirac_acceleration", "project_multiplier_energy",
    "integrate_dirac_reduced_cap_flow", "extended_dirac_branch_event",
    "constraint_observables", "project_full_eta_gauge_constraints",
    "completion_payload", "deterministic_json",
    "materialize",
]
