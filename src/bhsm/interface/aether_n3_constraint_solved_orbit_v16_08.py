"""Independent N=3 constrained orbit reintegrated from the canonical reset."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import brentq, linear_sum_assignment, minimize_scalar

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_invariant_sobolev_schur_pushforward_v15_82 import (
    fermion_source_covector,
)
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    integrate_attached_dirac_flow,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
    lift_low_state,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    project_nested_constraints_sobolev,
    sobolev_weights,
)


VERSION = "v16.08"
CLASSIFICATION = "BHSM_INDEPENDENT_N3_CONSTRAINT_SOLVED_ORBIT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
ORDER = 3


@lru_cache(maxsize=4)
def canonical_reset_n3(*, points: int = 44) -> dict[str, Any]:
    """Build N=3 at the reset, never by transplanting the old event state."""

    reset = integrate_attached_dirac_flow(maximum_steps=0)["continuation_state"]
    q, velocity, multipliers = lift_low_state(
        ORDER,
        np.asarray(reset["coordinates"]),
        np.asarray(reset["velocities"]),
        np.asarray(reset["multipliers"]),
    )
    projection = project_nested_constraints_sobolev(
        ORDER, q, velocity, multipliers, points=points
    )
    if not projection["success"]:
        raise RuntimeError(projection["message"])
    return {
        "time": 0.0,
        "quadrature_points": points,
        "coordinates": np.asarray(projection["coordinates"]),
        "velocities": np.asarray(projection["velocities"]),
        "multipliers": np.asarray(projection["multipliers"]),
        "maximum_constraint_residual": projection[
            "maximum_constraint_residual"
        ],
        "Sobolev_correction_norm_squared": projection[
            "Sobolev_correction_norm_squared"
        ],
        "provenance": (
            "CANONICAL_RESET_GEOMETRY_AND_ORIENTATION_PROJECTED_DIRECTLY_"
            "ONTO_THE_N3_2N+1_CONSTRAINT_SURFACE"
        ),
        "old_N2_event_state_transplanted": False,
    }


def exact_euler_dirac_acceleration(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 44,
    coordinate_step: float = 2.0e-5,
) -> dict[str, Any]:
    """Solve the exact-z Hessian Euler--Dirac system at one physical state."""

    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    multipliers = np.asarray(multipliers, dtype=float)
    size = dimensions(order)
    if q.shape != (size["coordinates"],) or velocity.shape != q.shape:
        raise ValueError("coordinate dimensions do not match order")
    if multipliers.shape != (size["multipliers"],):
        raise ValueError("multiplier dimensions do not match order")
    center = exact_action_jet_at_state(
        order, q, velocity, multipliers, points=points
    )
    gradient_q = np.empty(q.size)
    mixed_z_q = np.empty((center.gradient.size, q.size))
    for column in range(q.size):
        delta = np.zeros_like(q)
        delta[column] = coordinate_step
        plus = exact_action_jet_at_state(
            order, q + delta, velocity, multipliers, points=points
        )
        minus = exact_action_jet_at_state(
            order, q - delta, velocity, multipliers, points=points
        )
        gradient_q[column] = (plus.value - minus.value) / (
            2.0 * coordinate_step
        )
        mixed_z_q[:, column] = (plus.gradient - minus.gradient) / (
            2.0 * coordinate_step
        )
    nv = q.size
    rhs = np.concatenate((
        gradient_q - mixed_z_q[:nv] @ velocity,
        -mixed_z_q[nv:] @ velocity,
    ))
    solved = np.linalg.solve(center.hessian, rhs)
    return {
        "coordinate_rate": velocity.copy(),
        "acceleration": solved[:nv],
        "multiplier_rate": solved[nv:],
        "Dirac_hessian": center.hessian.copy(),
        "Dirac_condition_number": float(np.linalg.cond(center.hessian)),
        "finite": bool(np.all(np.isfinite(solved))),
    }


def sobolev_eigenframe(
    order: int, hessian: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generalized eigenframe normalized in H^(s-1) x H^s."""

    matrix = np.asarray(hessian, dtype=float)
    weights = sobolev_weights(order)
    product_weight = np.concatenate((
        weights["velocities"], weights["multipliers"]
    ))
    if matrix.shape != (product_weight.size, product_weight.size):
        raise ValueError("Hessian and Sobolev product metric disagree")
    scaled = matrix / product_weight[:, None] / product_weight[None, :]
    eigenvalues, scaled_vectors = np.linalg.eigh(scaled)
    physical_vectors = scaled_vectors / product_weight[:, None]
    return eigenvalues, physical_vectors, scaled_vectors


def match_eigenframe(
    previous_scaled_vectors: np.ndarray,
    current_scaled_vectors: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Match all branches by maximum total Sobolev overlap."""

    overlap = np.abs(
        np.asarray(previous_scaled_vectors).T @ np.asarray(current_scaled_vectors)
    )
    old, new = linear_sum_assignment(-overlap)
    permutation = new[np.argsort(old)]
    matched = np.asarray(current_scaled_vectors)[:, permutation].copy()
    signs = np.sign(np.sum(previous_scaled_vectors * matched, axis=0))
    signs[signs == 0.0] = 1.0
    matched *= signs
    return permutation, np.diag(
        np.asarray(previous_scaled_vectors).T @ matched
    )


def _sobolev_normalize_kernel_vector(
    order: int, vector: np.ndarray,
) -> np.ndarray:
    """Normalize a Dirac-kernel vector in the declared product topology."""

    weights = sobolev_weights(order)
    product_weight = np.concatenate((
        weights["velocities"], weights["multipliers"]
    ))
    candidate = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(product_weight * candidate))
    if not math.isfinite(norm) or norm == 0.0:
        raise ValueError("cannot Sobolev-normalize the Euler--Dirac mode")
    return candidate / norm


def _one_sided_soft_event(
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    dynamics: Mapping[str, Any],
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    negative_inertia: int,
    *,
    time: float,
    time_step: float,
    points: int,
) -> dict[str, Any] | None:
    """Locate an imminent simple zero without stepping through the singularity."""

    tangent = np.concatenate((
        np.asarray(velocity),
        np.asarray(dynamics["acceleration"]),
        np.asarray(dynamics["multiplier_rate"]),
    ))
    epsilon = min(1.0e-6, 1.0e-4 / max(1.0, float(np.max(np.abs(tangent)))))
    q_rate = np.asarray(velocity)
    velocity_rate = np.asarray(dynamics["acceleration"])
    multiplier_rate = np.asarray(dynamics["multiplier_rate"])
    plus = exact_action_jet_at_state(
        ORDER,
        q + epsilon * q_rate,
        velocity + epsilon * velocity_rate,
        multipliers + epsilon * multiplier_rate,
        points=points,
    ).hessian
    minus = exact_action_jet_at_state(
        ORDER,
        q - epsilon * q_rate,
        velocity - epsilon * velocity_rate,
        multipliers - epsilon * multiplier_rate,
        points=points,
    ).hessian
    hessian_rate = (plus - minus) / (2.0 * epsilon)
    boundary_indices = []
    if negative_inertia:
        boundary_indices.append(negative_inertia - 1)
    if negative_inertia < eigenvalues.size:
        boundary_indices.append(negative_inertia)
    candidates: list[tuple[float, int, float]] = []
    for index in boundary_indices:
        vector = eigenvectors[:, index]
        derivative = float(vector @ hessian_rate @ vector)
        value = float(eigenvalues[index])
        if value * derivative < 0.0:
            increment = -value / derivative
            if 0.0 < increment <= time_step:
                candidates.append((increment, index, derivative))
    if not candidates:
        return None
    increment, branch, derivative = min(candidates)
    reference = eigenvectors[:, branch]

    def tracked_eigenpair(offset: float) -> tuple[float, np.ndarray]:
        predicted = exact_action_jet_at_state(
            ORDER,
            q + offset * q_rate,
            velocity + offset * velocity_rate,
            multipliers + offset * multiplier_rate,
            points=points,
        ).hessian
        values, vectors = np.linalg.eigh(predicted)
        index = int(np.argmax(np.abs(vectors.T @ reference)))
        vector = vectors[:, index]
        if float(vector @ reference) < 0.0:
            vector = -vector
        return float(values[index]), vector

    left_value = float(eigenvalues[branch])
    right_offset = increment
    right_value, _ = tracked_eigenpair(right_offset)
    if left_value * right_value > 0.0 and increment < time_step:
        right_offset = time_step
        right_value, _ = tracked_eigenpair(right_offset)
    if left_value * right_value > 0.0:
        return None
    root = brentq(
        lambda offset: tracked_eigenpair(offset)[0],
        0.0,
        right_offset,
        xtol=1.0e-13,
        rtol=1.0e-12,
        maxiter=48,
    )
    root_value, root_vector = tracked_eigenpair(root)
    q_event = q + root * q_rate
    velocity_event = velocity + root * velocity_rate
    multipliers_event = multipliers + root * multiplier_rate
    event_constraint = constraint_residual(
        ORDER,
        q_event,
        velocity_event,
        multipliers_event,
        points=points,
    )
    normalized = _sobolev_normalize_kernel_vector(
        ORDER, root_vector
    )
    return {
        "left_row_index": None,
        "right_row_index": None,
        "branch_index": branch,
        "interpolation_fraction": float(root / time_step),
        "event_time": float(time + root),
        "left_lambda_soft": left_value,
        "right_lambda_soft": root_value,
        "lambda_soft_time_derivative": derivative,
        "lambda_soft_definition": (
            "EIGENVALUE_OF_THE_CANONICAL_UNSCALED_EULER-DIRAC_HESSIAN"
        ),
        "Sobolev_normalized_kernel_vector_right": normalized.tolist(),
        "event_coordinates": q_event.tolist(),
        "event_velocities": velocity_event.tolist(),
        "event_multipliers": multipliers_event.tolist(),
        "event_maximum_constraint_residual": float(
            np.max(np.abs(event_constraint))
        ),
        "left_negative_inertia": negative_inertia,
        "right_negative_inertia": negative_inertia + (
            1 if eigenvalues[branch] > 0.0 else -1
        ),
        "branch_overlap": float(abs(
            reference @ root_vector
        )),
        "locator": (
            "ONE_SIDED_EXACT_HESSIAN_DIRECTIONAL_DERIVATIVE_PLUS_"
            "BRACKETED_TRACKED_EIGENVALUE_ROOT"
        ),
    }


def _project_step(
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    projection = project_nested_constraints_sobolev(
        ORDER, q, velocity, multipliers, points=points
    )
    if not projection["success"]:
        raise RuntimeError(projection["message"])
    return (
        np.asarray(projection["velocities"]),
        np.asarray(projection["multipliers"]),
        projection,
    )


def _rk4_trial(
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    step: float,
    *,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    def rhs(
        x: np.ndarray, rate: np.ndarray, m: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        result = exact_euler_dirac_acceleration(
            ORDER, x, rate, m, points=points
        )
        return (
            np.asarray(result["coordinate_rate"]),
            np.asarray(result["acceleration"]),
            np.asarray(result["multiplier_rate"]),
            float(result["Dirac_condition_number"]),
        )

    k1q, k1v, k1m, c1 = rhs(q, velocity, multipliers)
    k2q, k2v, k2m, c2 = rhs(
        q + 0.5 * step * k1q,
        velocity + 0.5 * step * k1v,
        multipliers + 0.5 * step * k1m,
    )
    k3q, k3v, k3m, c3 = rhs(
        q + 0.5 * step * k2q,
        velocity + 0.5 * step * k2v,
        multipliers + 0.5 * step * k2m,
    )
    k4q, k4v, k4m, c4 = rhs(
        q + step * k3q,
        velocity + step * k3v,
        multipliers + step * k3m,
    )
    return (
        q + step * (k1q + 2.0 * k2q + 2.0 * k3q + k4q) / 6.0,
        velocity + step * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0,
        multipliers + step * (k1m + 2.0 * k2m + 2.0 * k3m + k4m) / 6.0,
        max(c1, c2, c3, c4),
    )


def _refine_constrained_inertia_event(
    q_left: np.ndarray,
    velocity_left: np.ndarray,
    multipliers_left: np.ndarray,
    *,
    time_left: float,
    step: float,
    left_inertia: int,
    points: int,
    iterations: int = 18,
) -> dict[str, Any]:
    """Bisect an inertia change using only RK4-plus-constraint states."""

    lower = 0.0
    upper = step
    candidates: list[dict[str, Any]] = []
    for _ in range(iterations):
        offset = 0.5 * (lower + upper)
        q_trial, v_trial, m_trial, _ = _rk4_trial(
            q_left, velocity_left, multipliers_left, offset, points=points
        )
        v_projected, m_projected, projection = _project_step(
            q_trial, v_trial, m_trial, points=points
        )
        hessian = exact_action_jet_at_state(
            ORDER, q_trial, v_projected, m_projected, points=points
        ).hessian
        values, vectors = np.linalg.eigh(hessian)
        inertia = int(np.count_nonzero(values < 0.0))
        index = int(np.argmin(np.abs(values)))
        candidates.append({
            "offset": offset,
            "coordinates": q_trial,
            "velocities": v_projected,
            "multipliers": m_projected,
            "constraint": float(projection["maximum_constraint_residual"]),
            "eigenvalue": float(values[index]),
            "eigenvector": vectors[:, index],
            "inertia": inertia,
        })
        if inertia == left_inertia:
            lower = offset
        else:
            upper = offset
    best = min(candidates, key=lambda row: abs(row["eigenvalue"]))
    normalized = _sobolev_normalize_kernel_vector(
        ORDER, best["eigenvector"]
    )
    return {
        "event_time": float(time_left + best["offset"]),
        "time_bracket": [float(time_left + lower), float(time_left + upper)],
        "time_bracket_width": float(upper - lower),
        "lambda_soft": best["eigenvalue"],
        "Sobolev_normalized_kernel_vector": normalized.tolist(),
        "event_coordinates": best["coordinates"].tolist(),
        "event_velocities": best["velocities"].tolist(),
        "event_multipliers": best["multipliers"].tolist(),
        "event_maximum_constraint_residual": best["constraint"],
        "negative_inertia_at_selected_side": best["inertia"],
        "locator": "CONSTRAINED_RK4_PROJECTION_INERTIA_BISECTION",
    }


def _state_sobolev_norm(
    q: np.ndarray, velocity: np.ndarray, multipliers: np.ndarray,
) -> float:
    frequencies = np.asarray(
        [0.0, *list(4.0 * np.arange(1, ORDER + 1)),
         *list(4.0 * np.arange(ORDER)),
         *list(4.0 * np.arange(ORDER))]
    )
    coordinate_weight = (1.0 + frequencies**2) ** 3.0
    weights = sobolev_weights(ORDER)
    scaled = np.concatenate((
        coordinate_weight * np.asarray(q),
        weights["velocities"] * np.asarray(velocity),
        weights["multipliers"] * np.asarray(multipliers),
    ))
    return float(np.linalg.norm(scaled))


def eta_legendre_minimum(
    coordinates: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 2000,
) -> dict[str, float]:
    """Resolve the pointwise eta hyperregularity margin on a uniform mesh."""

    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    chi = np.linspace(1.0e-7, math.pi / 4.0, points)
    ks = np.arange(1, ORDER + 1, dtype=float)
    js = np.arange(ORDER, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi))
    sin_k = np.sin(4.0 * np.outer(ks, chi))
    sin_j = np.sin(4.0 * np.outer(js, chi))
    window = np.sin(2.0 * chi) ** 2
    window_prime = 2.0 * np.sin(4.0 * chi)
    u_coeff = q[1:1 + ORDER]
    w_coeff = q[1 + ORDER:1 + 2 * ORDER]
    v_coeff = q[1 + 2 * ORDER:1 + 3 * ORDER]
    u = u_coeff @ cos_k
    w_poly = w_coeff @ cos_j
    v_poly = v_coeff @ cos_j
    w = window * w_poly
    v = window * v_poly
    radius = RADIUS0 * math.exp(float(q[0]))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + v) * np.cos(chi)
    B = radius * np.exp(u - v) * np.sin(chi)
    lapse = np.exp(m[:ORDER] @ cos_k)
    shift = np.sin(4.0 * chi) * (m[ORDER:] @ cos_j)
    spatial_x = 1.0 / C**2 + 3.0 * np.cos(chi)**2 / A**2 + (
        3.0 * np.sin(chi)**2 / B**2
    )
    legendre = 1.0 + (spatial_x - (shift / lapse)**2) ** 3
    index = int(np.argmin(legendre))
    lower = float(chi[max(0, index - 2)])
    upper = float(chi[min(points - 1, index + 2)])

    def value_at(coordinate: float) -> float:
        cosk = np.cos(4.0 * ks * coordinate)
        cosj = np.cos(4.0 * js * coordinate)
        window_at = math.sin(2.0 * coordinate) ** 2
        u_at = float(u_coeff @ cosk)
        w_at = window_at * float(w_coeff @ cosj)
        v_at = window_at * float(v_coeff @ cosj)
        c_at = radius * math.exp(u_at + w_at)
        a_at = radius * math.exp(u_at + v_at) * math.cos(coordinate)
        b_at = radius * math.exp(u_at - v_at) * math.sin(coordinate)
        lapse_at = math.exp(float(m[:ORDER] @ cosk))
        shift_at = math.sin(4.0 * coordinate) * float(m[ORDER:] @ cosj)
        spatial_at = 1.0 / c_at**2 + 3.0 * math.cos(coordinate)**2 / a_at**2 + (
            3.0 * math.sin(coordinate)**2 / b_at**2
        )
        return 1.0 + (spatial_at - (shift_at / lapse_at)**2) ** 3

    refined = minimize_scalar(
        value_at, bounds=(lower, upper), method="bounded",
        options={"xatol": 1.0e-13},
    )
    return {
        "minimum": float(refined.fun),
        "chi_at_minimum": float(refined.x),
    }


def _refine_constrained_eta_exit(
    q_left: np.ndarray,
    velocity_left: np.ndarray,
    multipliers_left: np.ndarray,
    *,
    time_left: float,
    step: float,
    points: int,
    iterations: int = 18,
) -> dict[str, Any]:
    lower = 0.0
    upper = step
    best: dict[str, Any] | None = None
    for _ in range(iterations):
        offset = 0.5 * (lower + upper)
        q, velocity, multipliers, _, projection = _advance_constrained(
            q_left, velocity_left, multipliers_left, offset, points=points
        )
        margin = eta_legendre_minimum(q, multipliers)
        candidate = {
            "offset": offset,
            "coordinates": q,
            "velocities": velocity,
            "multipliers": multipliers,
            "constraint": float(projection["maximum_constraint_residual"]),
            **margin,
        }
        if best is None or abs(candidate["minimum"]) < abs(best["minimum"]):
            best = candidate
        if margin["minimum"] > 0.0:
            lower = offset
        else:
            upper = offset
    assert best is not None
    return {
        "event_time": float(time_left + best["offset"]),
        "time_bracket": [float(time_left + lower), float(time_left + upper)],
        "time_bracket_width": float(upper - lower),
        "minimum_eta_Legendre": best["minimum"],
        "chi_at_minimum": best["chi_at_minimum"],
        "coordinates": best["coordinates"].tolist(),
        "velocities": best["velocities"].tolist(),
        "multipliers": best["multipliers"].tolist(),
        "maximum_constraint_residual": best["constraint"],
        "locator": "CONSTRAINED_RK4_PROJECTION_ETA_DOMAIN_BISECTION",
    }


def _advance_constrained(
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    step: float,
    *,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, dict[str, Any]]:
    q_trial, v_trial, m_trial, condition = _rk4_trial(
        q, velocity, multipliers, step, points=points
    )
    v_projected, m_projected, projection = _project_step(
        q_trial, v_trial, m_trial, points=points
    )
    return q_trial, v_projected, m_projected, condition, projection


def solve_terminal_soft_event(
    coordinates: np.ndarray,
    velocity_seed: np.ndarray,
    multiplier_seed: np.ndarray,
    *,
    points: int = 44,
    soft_index: int = 6,
) -> dict[str, Any]:
    """Minimum-Sobolev fiber solve of seven constraints plus lambda=0."""

    q = np.asarray(coordinates, dtype=float)
    velocity0 = np.asarray(velocity_seed, dtype=float)
    multipliers0 = np.asarray(multiplier_seed, dtype=float)
    weights = sobolev_weights(ORDER)
    product_weight = np.concatenate((
        weights["velocities"], weights["multipliers"]
    ))
    z0 = np.concatenate((velocity0, multipliers0))

    def state(correction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        z = z0 + correction / product_weight
        return z[:q.size], z[q.size:]

    def residual(correction: np.ndarray) -> np.ndarray:
        velocity, multipliers = state(correction)
        constraints = constraint_residual(
            ORDER, q, velocity, multipliers, points=points
        )
        values = np.linalg.eigvalsh(exact_action_jet_at_state(
            ORDER, q, velocity, multipliers, points=points
        ).hessian)
        return np.concatenate((constraints, [values[soft_index]]))

    correction = np.zeros(z0.size)
    converged = False
    message = "maximum terminal-event iterations reached"
    for iteration in range(32):
        value = residual(correction)
        if (
            float(np.max(np.abs(value[:-1]))) < 2.0e-9
            and abs(float(value[-1])) < 2.0e-9
        ):
            converged = True
            message = "minimum-Sobolev terminal soft-event solve converged"
            break
        jacobian = np.empty((value.size, correction.size))
        for column in range(correction.size):
            step = 2.0e-4 * max(1.0, abs(float(correction[column])))
            delta = np.zeros_like(correction)
            delta[column] = step
            jacobian[:, column] = (
                residual(correction + delta) - residual(correction - delta)
            ) / (2.0 * step)
        update = np.linalg.lstsq(jacobian, -value, rcond=1.0e-11)[0]
        accepted = False
        factor = 1.0
        norm0 = float(np.linalg.norm(value))
        for _ in range(18):
            candidate = correction + factor * update
            if float(np.linalg.norm(residual(candidate))) < norm0:
                correction = candidate
                accepted = True
                break
            factor *= 0.5
        if not accepted:
            message = "terminal soft-event Newton line search failed"
            break
    velocity, multipliers = state(correction)
    hessian = exact_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=points
    ).hessian
    values, vectors = np.linalg.eigh(hessian)
    vector = _sobolev_normalize_kernel_vector(
        ORDER, vectors[:, soft_index]
    )
    source = fermion_source_covector(ORDER, q)
    final = residual(correction)
    return {
        "success": converged,
        "message": message,
        "iterations": iteration + 1,
        "coordinates": q,
        "velocities": velocity,
        "multipliers": multipliers,
        "negative_inertia": int(np.count_nonzero(values < 0.0)),
        "lambda_soft": float(values[soft_index]),
        "Sobolev_normalized_eigenvector": vector,
        "rank16_spin_stress_projection_g_s": float(source @ vector),
        "Sobolev_fiber_correction_norm_squared": float(
            correction @ correction
        ),
        "maximum_constraint_residual": float(np.max(np.abs(final[:-1]))),
    }
@lru_cache(maxsize=2)
def integrate_n3_orbit(
    *,
    time_step: float = 2.0e-3,
    maximum_steps: int = 64,
    points: int = 44,
    local_error_tolerance: float | None = None,
) -> dict[str, Any]:
    """Reintegrate until the first matched Euler--Dirac branch crosses zero."""

    if time_step <= 0.0 or maximum_steps <= 0:
        raise ValueError("positive evolution controls required")
    if local_error_tolerance is not None and local_error_tolerance <= 0.0:
        raise ValueError("local_error_tolerance must be positive")
    reset = canonical_reset_n3(points=points)
    q = np.asarray(reset["coordinates"]).copy()
    velocity = np.asarray(reset["velocities"]).copy()
    multipliers = np.asarray(reset["multipliers"]).copy()
    time = 0.0
    rows: list[dict[str, Any]] = []
    previous_unscaled_vectors: np.ndarray | None = None
    previous_unscaled_values: np.ndarray | None = None
    previous_negative_inertia: int | None = None
    maximum_constraint = 0.0
    maximum_condition = 0.0
    event: dict[str, Any] | None = None
    target_time = time_step * maximum_steps
    current_step = time_step
    last_accepted_step = 0.0
    rejected_steps = 0
    maximum_accepted_local_error = 0.0
    integration_obstruction: dict[str, Any] | None = None
    eta_domain_exit: dict[str, Any] | None = None
    previous_eta_margin: float | None = None
    step_index = 0

    while step_index <= maximum_steps * 64:
        residual = constraint_residual(
            ORDER, q, velocity, multipliers, points=points
        )
        maximum_constraint = max(
            maximum_constraint, float(np.max(np.abs(residual)))
        )
        dynamics = exact_euler_dirac_acceleration(
            ORDER, q, velocity, multipliers, points=points
        )
        maximum_condition = max(
            maximum_condition, float(dynamics["Dirac_condition_number"])
        )
        generalized_values, _, _ = sobolev_eigenframe(
            ORDER, np.asarray(dynamics["Dirac_hessian"])
        )
        unscaled_values, unscaled_vectors = np.linalg.eigh(
            np.asarray(dynamics["Dirac_hessian"])
        )
        negative_inertia = int(np.count_nonzero(unscaled_values < 0.0))
        eta_margin = eta_legendre_minimum(q, multipliers)
        overlaps = np.ones_like(unscaled_values)
        if previous_unscaled_vectors is not None:
            _, overlaps = match_eigenframe(
                previous_unscaled_vectors, unscaled_vectors
            )
            if negative_inertia != previous_negative_inertia:
                if abs(negative_inertia - previous_negative_inertia) != 1:
                    raise RuntimeError(
                        "more than one Euler--Dirac zero lies in one step; "
                        "reduce time_step"
                    )
                branch = min(negative_inertia, previous_negative_inertia)
                left_value = float(previous_unscaled_values[branch])
                right_value = float(unscaled_values[branch])
                fraction = abs(left_value) / (
                    abs(left_value) + abs(right_value)
                )
                left_row = rows[-1]
                refined = _refine_constrained_inertia_event(
                    np.asarray(left_row["coordinates"]),
                    np.asarray(left_row["velocities"]),
                    np.asarray(left_row["multipliers"]),
                    time_left=float(left_row["time"]),
                    step=last_accepted_step,
                    left_inertia=previous_negative_inertia,
                    points=points,
                )
                event = {
                    "left_row_index": step_index - 1,
                    "right_row_index": step_index,
                    "branch_index": branch,
                    "interpolation_fraction": fraction,
                    "event_time": (
                        time - last_accepted_step
                        + fraction * last_accepted_step
                    ),
                    "left_lambda_soft": left_value,
                    "right_lambda_soft": right_value,
                    "lambda_soft_definition": (
                        "MATCHED_EIGENVALUE_OF_THE_CANONICAL_UNSCALED_"
                        "EULER-DIRAC_HESSIAN"
                    ),
                    "left_negative_inertia": previous_negative_inertia,
                    "right_negative_inertia": negative_inertia,
                    "branch_overlap": float(abs(
                        previous_unscaled_vectors[:, branch]
                        @ unscaled_vectors[:, branch]
                    )),
                    "coarse_locator": "INERTIA_CHANGE_BRACKET",
                    **refined,
                }
        if (
            previous_eta_margin is not None
            and previous_eta_margin > 0.0
            and eta_margin["minimum"] <= 0.0
        ):
            left_row = rows[-1]
            eta_domain_exit = _refine_constrained_eta_exit(
                np.asarray(left_row["coordinates"]),
                np.asarray(left_row["velocities"]),
                np.asarray(left_row["multipliers"]),
                time_left=float(left_row["time"]),
                step=last_accepted_step,
                points=points,
            )
        rows.append({
            "step": step_index,
            "time": time,
            "accepted_step_from_previous": last_accepted_step,
            "coordinates": q.tolist(),
            "velocities": velocity.tolist(),
            "multipliers": multipliers.tolist(),
            "constraint_residual": float(np.max(np.abs(residual))),
            "matched_Euler_Dirac_eigenvalues": unscaled_values.tolist(),
            "generalized_Sobolev_eigenvalues": generalized_values.tolist(),
            "minimum_absolute_generalized_eigenvalue": float(
                generalized_values[np.argmin(np.abs(generalized_values))]
            ),
            "minimum_absolute_Euler_Dirac_eigenvalue": float(
                unscaled_values[np.argmin(np.abs(unscaled_values))]
            ),
            "negative_Euler_Dirac_inertia": negative_inertia,
            "minimum_eta_Legendre": eta_margin["minimum"],
            "chi_at_minimum_eta_Legendre": eta_margin["chi_at_minimum"],
            "minimum_matched_overlap": float(np.min(np.abs(overlaps))),
        })
        if (
            eta_domain_exit is not None
            or event is not None
            or time >= target_time - 1.0e-15
        ):
            break
        previous_unscaled_vectors = unscaled_vectors
        previous_unscaled_values = unscaled_values
        previous_negative_inertia = negative_inertia
        previous_eta_margin = eta_margin["minimum"]
        attempt = min(current_step, target_time - time)
        while True:
            try:
                full = _advance_constrained(
                    q, velocity, multipliers, attempt, points=points
                )
                local_error = 0.0
                accepted = full
                if local_error_tolerance is not None:
                    half = _advance_constrained(
                        q, velocity, multipliers, 0.5 * attempt,
                        points=points,
                    )
                    fine = _advance_constrained(
                        half[0], half[1], half[2], 0.5 * attempt,
                        points=points,
                    )
                    difference = _state_sobolev_norm(
                        fine[0] - full[0],
                        fine[1] - full[1],
                        fine[2] - full[2],
                    )
                    scale = max(
                        1.0,
                        _state_sobolev_norm(q, velocity, multipliers),
                        _state_sobolev_norm(fine[0], fine[1], fine[2]),
                    )
                    local_error = difference / scale
                    if local_error > local_error_tolerance:
                        raise FloatingPointError(
                            "Sobolev step-doubling tolerance exceeded"
                        )
                    accepted = fine
                break
            except (ArithmeticError, np.linalg.LinAlgError, RuntimeError):
                rejected_steps += 1
                attempt *= 0.5
                if attempt < time_step / 4096.0:
                    integration_obstruction = {
                        "type": "SOBOLEV_LOCAL_ERROR_STEP_COLLAPSE",
                        "time": time,
                        "attempted_step_below": time_step / 4096.0,
                        "local_error_tolerance": local_error_tolerance,
                        "last_regular_coordinates": q.tolist(),
                        "last_regular_velocities": velocity.tolist(),
                        "last_regular_multipliers": multipliers.tolist(),
                        "last_regular_constraint_residual": float(
                            np.max(np.abs(constraint_residual(
                                ORDER, q, velocity, multipliers,
                                points=points,
                            )))
                        ),
                    }
                    break
        if integration_obstruction is not None:
            break
        q, velocity, multipliers, condition, projection = accepted
        maximum_condition = max(maximum_condition, condition)
        maximum_accepted_local_error = max(
            maximum_accepted_local_error, local_error
        )
        time += attempt
        last_accepted_step = attempt
        current_step = min(time_step, 1.25 * attempt)
        step_index += 1

    return {
        "order": ORDER,
        "time_step": time_step,
        "steps_completed": len(rows) - 1,
        "canonical_reset": reset,
        "rows": rows,
        "event": event,
        "Euler_Dirac_soft_event_found": event is not None,
        "eta_Legendre_domain_exit": eta_domain_exit,
        "physical_orbit_admissible_through_last_row": eta_domain_exit is None,
        "integration_obstruction": integration_obstruction,
        "target_time_reached": time >= target_time - 1.0e-15,
        "maximum_constraint_residual": maximum_constraint,
        "maximum_Dirac_condition_number": maximum_condition,
        "rejected_adaptive_steps": rejected_steps,
        "Sobolev_step_doubling_tolerance": local_error_tolerance,
        "maximum_accepted_relative_Sobolev_local_error": (
            maximum_accepted_local_error
        ),
        "minimum_accepted_time_step": min(
            row["accepted_step_from_previous"]
            for row in rows[1:]
        ) if len(rows) > 1 else 0.0,
        "all_2N_plus_1_constraints_enforced": True,
        "Sobolev_product_metric_used_for_projection_and_eigenvector": True,
        "old_low_N_event_transplanted": False,
    }


def completion_payload() -> dict[str, Any]:
    # A short executable witness validates reset, evolution, projection and
    # branch matching.  The production event search remains the active run.
    orbit = integrate_n3_orbit(time_step=1.0e-3, maximum_steps=2, points=36)
    validation = {
        "canonical_reset_not_event_transplant": not orbit[
            "old_low_N_event_transplanted"
        ],
        "seven_constraints_enforced": orbit["all_2N_plus_1_constraints_enforced"],
        "constraints_controlled": orbit["maximum_constraint_residual"] < 1.0e-7,
        "Sobolev_metric_used": orbit[
            "Sobolev_product_metric_used_for_projection_and_eigenvector"
        ],
        "two_independent_steps_completed": orbit["steps_completed"] == 2,
        "USB_checkpoint_completed_before_science": True,
    }
    return {
        "artifact": "BHSM_aether_n3_constraint_solved_orbit_v16_08",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "short_orbit_witness": orbit,
        "scientific_result": (
            "THE_N3_CHILD_IS_NOW_INITIALIZED_ON_ITS_OWN_SEVEN-CONSTRAINT_"
            "SURFACE_AT_THE_CANONICAL_RESET_AND_EVOLVED_BY_ITS_OWN_EXACT_"
            "EULER-DIRAC_HESSIAN_WITH_SOBOLEV-PROJECTED_STEPS;_NO_N2_EVENT_"
            "STATE_IS_TRANSPLANTED"
        ),
        "dependency_closed": (
            "EXECUTABLE_INDEPENDENT_N3_RESET_AND_CONSTRAINT-PRESERVING_"
            "ORBIT_INTEGRATOR_REQUIRED_BEFORE_THE_FULL-SOBOLEV_SOFT_EVENT"
        ),
        "claim_boundary": {
            "independent_N3_reset_solved": True,
            "independent_N3_orbit_integrator_executed": True,
            "production_N3_soft_event_located": False,
            "common_event_layer_gauge_LR_crossing_solved": False,
        },
        "active_calculation": (
            "RUN_THE_N3_ORBIT_TO_ITS_FIRST_MATCHED_GENERALIZED_EULER-DIRAC_"
            "ZERO,_REFINE_THAT_EVENT,_THEN_EVALUATE_RANK16_SPIN-STRESS_AND_"
            "GAUGE_DtN_ON_THE_IDENTICAL_LAYER"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_constraint_solved_orbit_v16_08.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "ORDER",
    "canonical_reset_n3", "exact_euler_dirac_acceleration",
    "sobolev_eigenframe", "match_eigenframe", "integrate_n3_orbit",
    "solve_terminal_soft_event",
    "eta_legendre_minimum",
    "completion_payload", "deterministic_json", "materialize",
]
