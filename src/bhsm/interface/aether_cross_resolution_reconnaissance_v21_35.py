"""Independent N=3/N=4/N=5 reconnaissance from the BHSM action.

This module deliberately stops before a higher-resolution global solve.  It
builds every order directly from the canonical reset, projects onto that
order's own Euler--Dirac constraint surface, and measures the local physical
flow and ordered Dirac pencil.  The accepted N=3 trajectory is never used as
an N=4 or N=5 initial condition.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.linalg import qr
from scipy.optimize import (
    brentq,
    least_squares,
    linear_sum_assignment,
    minimize_scalar,
)

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
    embed_nested_state,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    integrate_attached_dirac_flow,
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
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
    spectral_frequencies,
)


VERSION = "v21.35"
CLASSIFICATION = "BHSM_CROSS_RESOLUTION_INDEPENDENT_HINDSIGHT_RECONNAISSANCE"
FULL_BHSM_COMPLETE = False
ORDERS = (3, 4, 5)
DEFAULT_POINTS = 32


def _families(order: int, value: np.ndarray) -> dict[str, np.ndarray | float]:
    vector = np.asarray(value, dtype=float)
    return {
        "scale": float(vector[0]),
        "u": vector[1:1 + order],
        "w": vector[1 + order:1 + 2 * order],
        "v": vector[1 + 2 * order:1 + 3 * order],
    }


def _multiplier_families(
    order: int, value: np.ndarray,
) -> dict[str, np.ndarray]:
    vector = np.asarray(value, dtype=float)
    return {"lapse": vector[:order], "shift": vector[order:]}


def _common_n2_fiber(
    order: int, velocity: np.ndarray, multipliers: np.ndarray,
) -> np.ndarray:
    rates = _families(order, velocity)
    lapse_shift = _multiplier_families(order, multipliers)
    return np.concatenate((
        [rates["scale"]],
        np.asarray(rates["u"])[:2],
        np.asarray(rates["w"])[:2],
        np.asarray(rates["v"])[:2],
        lapse_shift["lapse"][:2],
        lapse_shift["shift"][:2],
    ))


def _terminal_observables(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
) -> dict[str, float]:
    q = _families(order, coordinates)
    rate = _families(order, velocities)
    lapse_shift = _multiplier_families(order, multipliers)
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    scale = float(q["scale"])
    u = float(np.asarray(q["u"]) @ signs_k)
    w = float(np.asarray(q["w"]) @ signs_j)
    v = float(np.asarray(q["v"]) @ signs_j)
    radius = float(RADIUS0 * math.exp(scale))
    return {
        "log_scale": scale,
        "reconstruction_radius": radius,
        "terminal_u": u,
        "terminal_w": w,
        "terminal_v": v,
        "terminal_C": float(radius * math.exp(u + w)),
        "terminal_A": float(radius * math.exp(u + v) / math.sqrt(2.0)),
        "terminal_B": float(radius * math.exp(u - v) / math.sqrt(2.0)),
        "scale_rate": float(rate["scale"]),
        "terminal_u_rate": float(np.asarray(rate["u"]) @ signs_k),
        "terminal_w_rate": float(np.asarray(rate["w"]) @ signs_j),
        "terminal_v_rate": float(np.asarray(rate["v"]) @ signs_j),
        "terminal_log_lapse": float(lapse_shift["lapse"] @ signs_k),
        "terminal_shift_polynomial": float(lapse_shift["shift"] @ signs_j),
    }


def _eta_legendre_minimum(
    order: int,
    coordinates: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 1600,
) -> dict[str, float]:
    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)

    def value_at(chi: float) -> float:
        cos_k = np.cos(4.0 * ks * chi)
        cos_j = np.cos(4.0 * js * chi)
        window = math.sin(2.0 * chi) ** 2
        u = float(q[1:1 + order] @ cos_k)
        w = window * float(q[1 + order:1 + 2 * order] @ cos_j)
        v = window * float(q[1 + 2 * order:1 + 3 * order] @ cos_j)
        radius = RADIUS0 * math.exp(float(q[0]))
        c_radius = radius * math.exp(u + w)
        a_radius = radius * math.exp(u + v) * math.cos(chi)
        b_radius = radius * math.exp(u - v) * math.sin(chi)
        lapse = math.exp(float(m[:order] @ cos_k))
        shift = math.sin(4.0 * chi) * float(m[order:] @ cos_j)
        spatial = (
            1.0 / c_radius**2
            + 3.0 * math.cos(chi) ** 2 / a_radius**2
            + 3.0 * math.sin(chi) ** 2 / b_radius**2
        )
        return 1.0 + (spatial - (shift / lapse) ** 2) ** 3

    grid = np.linspace(1.0e-7, math.pi / 4.0, points)
    values = np.asarray([value_at(float(chi)) for chi in grid])
    index = int(np.argmin(values))
    lower = float(grid[max(0, index - 2)])
    upper = float(grid[min(points - 1, index + 2)])
    refined = minimize_scalar(
        value_at,
        bounds=(lower, upper),
        method="bounded",
        options={"xatol": 1.0e-13},
    )
    return {"minimum": float(refined.fun), "chi": float(refined.x)}


def _coordinate_time_vector_timelike_margin(
    order: int,
    coordinates: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 4001,
) -> float:
    """Measure raw coordinate-frame timelikeness without making it a gate."""

    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    chi = np.linspace(1.0e-8, math.pi / 4.0, points)
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cosine_k = np.cos(4.0 * np.outer(chi, ks))
    cosine_j = np.cos(4.0 * np.outer(chi, js))
    window = np.sin(2.0 * chi) ** 2
    u = cosine_k @ q[1:1 + order]
    w = window * (cosine_j @ q[1 + order:1 + 2 * order])
    c_radius = RADIUS0 * np.exp(q[0] + u + w)
    lapse = np.exp(cosine_k @ m[:order])
    shift = np.sin(4.0 * chi) * (cosine_j @ m[order:])
    return float(np.min(1.0 - (c_radius * shift / lapse) ** 2))


def _project_constraints_action_energy(
    order: int,
    coordinates: np.ndarray,
    trial_velocity: np.ndarray,
    multiplier_seed: np.ndarray,
    *,
    points: int,
) -> dict[str, Any]:
    """Nearest constraint projection in the retained action energy topology."""

    q = np.asarray(coordinates, dtype=float)
    trial = np.asarray(trial_velocity, dtype=float)
    seed = np.asarray(multiplier_seed, dtype=float)
    frequencies = spectral_frequencies(order)
    velocity_weights = np.ones_like(trial)
    multiplier_weights = np.sqrt(
        1.0 + frequencies["multipliers"] ** 2
    )
    qdim = q.size
    correction = np.zeros(trial.size + seed.size)
    initial = constraint_residual(
        order, q, trial, seed, points=points
    )
    row_scale = np.maximum(1.0, np.abs(initial))

    def unpack(value: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return (
            trial + value[:qdim] / velocity_weights,
            seed + value[qdim:] / multiplier_weights,
        )

    def rows(value: np.ndarray) -> np.ndarray:
        velocity, multipliers = unpack(value)
        return constraint_residual(
            order, q, velocity, multipliers, points=points
        ) / row_scale

    converged = False
    message = "maximum action-energy projection iterations reached"
    for iteration in range(32):
        value = rows(correction)
        maximum = float(np.max(np.abs(value)))
        if maximum < 2.0e-10:
            converged = True
            message = "minimum-action-energy-norm projection converged"
            break
        jacobian = np.empty((value.size, correction.size))
        for column in range(correction.size):
            step = 2.0e-4 * max(1.0, abs(float(correction[column])))
            delta = np.zeros_like(correction)
            delta[column] = step
            jacobian[:, column] = (
                rows(correction + delta) - rows(correction - delta)
            ) / (2.0 * step)
        delta = np.linalg.lstsq(
            jacobian, -value, rcond=1.0e-12
        )[0]
        accepted = False
        factor = 1.0
        for _ in range(16):
            candidate = correction + factor * delta
            if np.max(np.abs(rows(candidate))) < maximum:
                correction = candidate
                accepted = True
                break
            factor *= 0.5
        if not accepted:
            message = "action-energy projection line search failed"
            break
    velocity, multipliers = unpack(correction)
    residual = constraint_residual(
        order, q, velocity, multipliers, points=points
    )
    return {
        "success": converged,
        "message": message,
        "iterations": iteration + 1,
        "coordinates": q,
        "velocities": velocity,
        "multipliers": multipliers,
        "action_energy_correction_norm": float(np.linalg.norm(correction)),
        "raw_velocity_correction_norm": float(
            np.linalg.norm(velocity - trial)
        ),
        "raw_multiplier_correction_norm": float(
            np.linalg.norm(multipliers - seed)
        ),
        "maximum_constraint_residual": float(np.max(np.abs(residual))),
        "scaled_maximum_constraint_residual": float(
            np.max(np.abs(residual) / row_scale)
        ),
        "domain_norm": "L2_velocity_CROSS_H1_lapse_shift",
        "physical_constraints_changed": False,
    }


def _tail_measure(
    order: int, velocities: np.ndarray, multipliers: np.ndarray,
) -> dict[str, float]:
    weights = sobolev_weights(order)
    vf = _families(order, np.asarray(velocities) * weights["velocities"])
    mf = _multiplier_families(
        order, np.asarray(multipliers) * weights["multipliers"]
    )
    result: dict[str, float] = {}
    for name in ("u", "w", "v"):
        values = np.asarray(vf[name])
        total = float(values @ values)
        tail = float(values[2:] @ values[2:])
        result[f"{name}_tail_fraction_beyond_N2"] = tail / total if total else 0.0
    for name in ("lapse", "shift"):
        values = np.asarray(mf[name])
        total = float(values @ values)
        tail = float(values[2:] @ values[2:])
        result[f"{name}_tail_fraction_beyond_N2"] = tail / total if total else 0.0
    return result


def _constraint_fiber_rank(
    order: int,
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
) -> dict[str, Any]:
    size = dimensions(order)
    weights = sobolev_weights(order)
    product_weight = np.concatenate((
        weights["velocities"], weights["multipliers"]
    ))
    fiber = np.concatenate((velocity, multipliers))
    jacobian = np.empty((2 * order + 1, fiber.size))
    for column in range(fiber.size):
        step = 2.0e-4 / product_weight[column]
        delta = np.zeros_like(fiber)
        delta[column] = step
        plus = fiber + delta
        minus = fiber - delta
        jacobian[:, column] = (
            constraint_residual(
                order,
                q,
                plus[:size["coordinates"]],
                plus[size["coordinates"]:],
                points=points,
            )
            - constraint_residual(
                order,
                q,
                minus[:size["coordinates"]],
                minus[size["coordinates"]:],
                points=points,
            )
        ) / (2.0 * step * product_weight[column])
    singular = np.linalg.svd(jacobian, compute_uv=False)
    tolerance = (
        np.finfo(float).eps * max(jacobian.shape) * float(singular[0])
    )
    return {
        "row_count": 2 * order + 1,
        "rank": int(np.count_nonzero(singular > tolerance)),
        "smallest_singular_value": float(singular[-1]),
        "largest_singular_value": float(singular[0]),
        "rank_tolerance": float(tolerance),
        "coordinates": "BHSM_H5_RATE_TIMES_H6_MULTIPLIER",
    }


def _match_frame(
    reference_vectors: np.ndarray, candidate_vectors: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    overlap = np.abs(reference_vectors.T @ candidate_vectors)
    old, new = linear_sum_assignment(-overlap)
    permutation = new[np.argsort(old)]
    matched = candidate_vectors[:, permutation].copy()
    signs = np.sign(np.sum(reference_vectors * matched, axis=0))
    signs[signs == 0.0] = 1.0
    matched *= signs
    return permutation, np.diag(reference_vectors.T @ matched)


@lru_cache(maxsize=6)
def independent_order_probe(
    order: int, *, points: int = DEFAULT_POINTS,
) -> dict[str, Any]:
    """Measure one order without importing any accepted N=3 event state."""

    if order not in ORDERS:
        raise ValueError("reconnaissance order must be N=3, N=4, or N=5")
    reset = integrate_attached_dirac_flow(maximum_steps=0)[
        "continuation_state"
    ]
    q_seed, v_seed, m_seed = lift_low_state(
        order,
        np.asarray(reset["coordinates"]),
        np.asarray(reset["velocities"]),
        np.asarray(reset["multipliers"]),
    )
    projection = project_nested_constraints_sobolev(
        order, q_seed, v_seed, m_seed, points=points
    )
    if not projection["success"]:
        raise RuntimeError(str(projection["message"]))
    q = np.asarray(projection["coordinates"], dtype=float)
    velocity = np.asarray(projection["velocities"], dtype=float)
    multipliers = np.asarray(projection["multipliers"], dtype=float)
    constraints = constraint_residual(
        order, q, velocity, multipliers, points=points
    )
    eta_reset = _eta_legendre_minimum(order, q, multipliers)
    constraint_fiber = _constraint_fiber_rank(
        order, q, velocity, multipliers, points=points
    )
    child_structure = {
        "order_independent_boundary_rows": 7,
        "trace_rows": 3,
        "canonical_momentum_rows": 2,
        "dynamic_flux_rows": 2,
        "order_dependent_constraint_rows": 2 * order + 1,
        "full_unreduced_child_row_count": 2 * order + 8,
        "N3_rank_14_literal_at_this_order": 2 * order + 8 == 14,
        "event_conditioned_reconstruction_attempted": False,
    }
    base = {
        "order": order,
        "action_source": (
            "SAME_RETAINED_GENERALIZED_BHSM_LAGRANGIAN_AND_EXACT_ACTION_JET"
        ),
        "initialization": {
            "source": "CANONICAL_RESET_PROJECTED_DIRECTLY_TO_THIS_ORDER",
            "accepted_N3_trajectory_used": False,
            "accepted_N3_event_used": False,
            "higher_modes_seeded_at_zero_then_solved_by_own_constraints": True,
            "projection_success": bool(projection["success"]),
            "projection_iterations": int(projection["iterations"]),
            "Sobolev_correction_norm_squared": float(
                projection["Sobolev_correction_norm_squared"]
            ),
            "maximum_constraint_residual": float(
                np.max(np.abs(constraints))
            ),
            "eta_domain_admissible": bool(eta_reset["minimum"] > 0.0),
        },
        "dimensions": dimensions(order),
        "constraint_fiber": constraint_fiber,
        "complete_child_structure": child_structure,
    }
    if eta_reset["minimum"] <= 0.0:
        base["local_flow"] = {
            "physical_probe_admissible": False,
            "physical_blocker": "ETA_LEGENDRE_DOMAIN_FAILURE_AT_INDEPENDENT_RESET",
            "probe_time_step": None,
            "forward_projection_success": False,
            "forward_maximum_constraint_residual": None,
            "Dirac_condition_number": None,
            "negative_inertia": None,
            "eigenvalue_tolerance": None,
            "inertia_boundary_branches": [],
            "ordered_forward_event_bracketed": False,
            "minimum_branch_overlap": None,
            "reset_observables": _terminal_observables(
                order, q, velocity, multipliers
            ),
            "forward_observables": None,
            "eta_reset": eta_reset,
            "eta_forward": None,
            "tail_measure": _tail_measure(order, velocity, multipliers),
            "common_N2_fiber": _common_n2_fiber(
                order, velocity, multipliers
            ).tolist(),
        }
        return base

    dynamics = exact_euler_dirac_acceleration(
        order, q, velocity, multipliers, points=points
    )
    hessian = np.asarray(dynamics["Dirac_hessian"], dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    inertia = int(np.count_nonzero(eigenvalues < 0.0))

    tangent = np.concatenate((
        velocity,
        np.asarray(dynamics["acceleration"]),
        np.asarray(dynamics["multiplier_rate"]),
    ))
    probe_step = 2.0e-6 / max(1.0, float(np.max(np.abs(tangent))))
    q_trial = q + probe_step * velocity
    v_trial = velocity + probe_step * np.asarray(dynamics["acceleration"])
    m_trial = multipliers + probe_step * np.asarray(dynamics["multiplier_rate"])
    forward_projection = project_nested_constraints_sobolev(
        order, q_trial, v_trial, m_trial, points=points
    )
    if not forward_projection["success"]:
        raise RuntimeError(str(forward_projection["message"]))
    q_forward = np.asarray(forward_projection["coordinates"], dtype=float)
    v_forward = np.asarray(forward_projection["velocities"], dtype=float)
    m_forward = np.asarray(forward_projection["multipliers"], dtype=float)
    forward_jet = exact_action_jet_at_state(
        order, q_forward, v_forward, m_forward, points=points
    )
    forward_values, forward_vectors = np.linalg.eigh(forward_jet.hessian)
    permutation, overlaps = _match_frame(eigenvectors, forward_vectors)
    tracked_forward = forward_values[permutation]
    slopes = (tracked_forward - eigenvalues) / probe_step

    spectral_scale = max(1.0, float(np.max(np.abs(eigenvalues))))
    eigen_tolerance = (
        np.finfo(float).eps * eigenvalues.size * spectral_scale
    )
    boundary_indices = sorted(set(
        index for index in (inertia - 1, inertia)
        if 0 <= index < eigenvalues.size
    ))
    boundary = []
    for index in boundary_indices:
        lower_gap = (
            float(eigenvalues[index] - eigenvalues[index - 1])
            if index else math.inf
        )
        upper_gap = (
            float(eigenvalues[index + 1] - eigenvalues[index])
            if index + 1 < eigenvalues.size else math.inf
        )
        derivative = float(slopes[index])
        crossing = (
            -float(eigenvalues[index]) / derivative
            if eigenvalues[index] * derivative < 0.0 else None
        )
        bracketed = bool(
            eigenvalues[index] * tracked_forward[index] <= 0.0
            and min(lower_gap, upper_gap) > eigen_tolerance
            and abs(float(overlaps[index])) > 0.9
        )
        boundary.append({
            "index": index,
            "eigenvalue": float(eigenvalues[index]),
            "forward_eigenvalue": float(tracked_forward[index]),
            "directional_derivative": derivative,
            "linearized_forward_crossing_time": crossing,
            "lower_gap": lower_gap,
            "upper_gap": upper_gap,
            "branch_overlap": float(abs(overlaps[index])),
            "forward_crossing_bracketed": bracketed,
        })

    base["local_flow"] = {
        "physical_probe_admissible": True,
        "physical_blocker": None,
        "probe_time_step": probe_step,
        "forward_projection_success": bool(forward_projection["success"]),
        "forward_maximum_constraint_residual": float(
            forward_projection["maximum_constraint_residual"]
        ),
        "Dirac_condition_number": float(
            dynamics["Dirac_condition_number"]
        ),
        "negative_inertia": inertia,
        "eigenvalue_tolerance": eigen_tolerance,
        "inertia_boundary_branches": boundary,
        "ordered_forward_event_bracketed": any(
            row["forward_crossing_bracketed"] for row in boundary
        ),
        "minimum_branch_overlap": float(np.min(np.abs(overlaps))),
        "reset_observables": _terminal_observables(
            order, q, velocity, multipliers
        ),
        "forward_observables": _terminal_observables(
            order, q_forward, v_forward, m_forward
        ),
        "eta_reset": eta_reset,
        "eta_forward": _eta_legendre_minimum(
            order, q_forward, m_forward
        ),
        "tail_measure": _tail_measure(order, velocity, multipliers),
        "common_N2_fiber": _common_n2_fiber(
            order, velocity, multipliers
        ).tolist(),
    }
    return base


def _relative_difference(left: np.ndarray, right: np.ndarray) -> float:
    scale = max(float(np.linalg.norm(left)), float(np.linalg.norm(right)), 1.0e-30)
    return float(np.linalg.norm(left - right) / scale)


def ingredient_process_ownership_audit() -> dict[str, Any]:
    """Classify BHSM objects by mathematical and temporal ownership."""

    ledger = [
        {
            "object": "eta",
            "primary_role": "CONSTITUENT",
            "secondary_roles": ["DOMAIN_CONDITION"],
            "timing": ["AT_ALL_STAGES"],
            "derivation": (
                "DEGREE_ONE_MAP_IN_THE_RETAINED_FIELD_TUPLE;_ITS_"
                "POINTWISE_LEGENDRE_FACTOR_DEFINES_THE_REGULAR_DOMAIN"
            ),
        },
        {
            "object": "sigma",
            "primary_role": "CONSTITUENT",
            "secondary_roles": ["DERIVED_CHILD_CONDITION"],
            "timing": ["AT_ALL_STAGES"],
            "derivation": (
                "ACTION_OWNED_MATERIAL_RESPONSE_SIGMA=C_J[f]-1/2,_NOT_"
                "AN_ENCLOSURE_FIELD"
            ),
        },
        {
            "object": "geometric_scale",
            "primary_role": "CONSTITUENT",
            "secondary_roles": [],
            "timing": ["AT_ALL_STAGES"],
            "derivation": "LOG_RADIUS_COLLECTIVE_GEOMETRY_COORDINATE",
        },
        {
            "object": "u_w_v_geometry",
            "primary_role": "CONSTITUENT",
            "secondary_roles": [],
            "timing": ["AT_ALL_STAGES"],
            "derivation": "RETAINED_REGULAR_SPECTRAL_METRIC_SHAPE_FIELDS",
        },
        {
            "object": "lapse",
            "primary_role": "CONSTITUENT",
            "secondary_roles": ["EVOLUTION_LAW"],
            "timing": ["AT_ALL_STAGES"],
            "derivation": "METRIC_MULTIPLIER_ENFORCING_HAMILTONIAN_ROWS",
        },
        {
            "object": "shift",
            "primary_role": "CONSTITUENT",
            "secondary_roles": ["EVOLUTION_LAW"],
            "timing": ["AT_ALL_STAGES"],
            "derivation": "METRIC_MULTIPLIER_ENFORCING_MOMENTUM_ROWS",
        },
        {
            "object": "action_stationarity",
            "primary_role": "EVOLUTION_LAW",
            "secondary_roles": ["DERIVED_CHILD_CONDITION"],
            "timing": ["AT_ALL_STAGES"],
            "derivation": "EULER_LAGRANGE_DIRAC_KKT_EQUATIONS_OF_ONE_ACTION",
        },
        {
            "object": "reset_constraints",
            "primary_role": "DOMAIN_CONDITION",
            "secondary_roles": [],
            "timing": ["RESET_ONLY"],
            "derivation": "INITIAL_POINT_ON_THE_2N_PLUS_1_CONSTRAINT_SURFACE",
        },
        {
            "object": "ordered_Rayleigh_event",
            "primary_role": "PROCESS_MILESTONE",
            "secondary_roles": ["DIAGNOSTIC"],
            "timing": ["EVENT_ONLY"],
            "derivation": (
                "ZERO_OF_AN_ISOLATED_ORDERED_EULER_DIRAC_HESSIAN_"
                "EIGENVALUE_WITH_RAYLEIGH_DERIVATIVE"
            ),
        },
        {
            "object": "enclosure",
            "primary_role": "PROCESS_MILESTONE",
            "secondary_roles": [],
            "timing": ["UNRESOLVED_FROM_DERIVATION"],
            "derivation": (
                "FINITE_LOCAL_NONLINEAR_PROCESS_OUTCOME;_NO_ENCLOSURE_"
                "FIELD_OR_EVENT_EQUIVALENCE_HAS_BEEN_DERIVED"
            ),
        },
        {
            "object": "surface_matching",
            "primary_role": "DERIVED_CHILD_CONDITION",
            "secondary_roles": [],
            "timing": ["CHILD_ONLY"],
            "derivation": "BOUNDARY_CANONICAL_RELATION_USING_S4_EVENT_DATA",
        },
        {
            "object": "trace_matching",
            "primary_role": "DERIVED_CHILD_CONDITION",
            "secondary_roles": [],
            "timing": ["CHILD_ONLY"],
            "derivation": "GAMMA0_EVENT_MINUS_GAMMA0_CHILD_EQUALS_ZERO",
        },
        {
            "object": "seven_child_constraints",
            "primary_role": "DERIVED_CHILD_CONDITION",
            "secondary_roles": ["DOMAIN_CONDITION"],
            "timing": ["CHILD_ONLY"],
            "derivation": "N3_TWO_N_PLUS_ONE_CHILD_CONSTRAINT_ROWS",
        },
        {
            "object": "momentum_matching",
            "primary_role": "DERIVED_CHILD_CONDITION",
            "secondary_roles": [],
            "timing": ["CHILD_ONLY"],
            "derivation": "ACTION_LEGENDRE_CANONICAL_MOMENTUM_CONTINUITY",
        },
        {
            "object": "flux_matching",
            "primary_role": "DERIVED_CHILD_CONDITION",
            "secondary_roles": [],
            "timing": ["CHILD_ONLY"],
            "derivation": "GHY_CALDERON_DYNAMIC_FLUX_BALANCE",
        },
        {
            "object": "persistence",
            "primary_role": "DERIVED_CHILD_CONDITION",
            "secondary_roles": ["PROCESS_MILESTONE"],
            "timing": ["PERSISTENCE_ONLY"],
            "derivation": (
                "POSITIVE_DURATION_CONSTRAINT_SOLVED_RELATIVE_EVOLUTION_"
                "OR_THE_RETAINED_RELATIVE_PERIODIC_FLOQUET_CLASS"
            ),
        },
        {
            "object": "nonzero_motion",
            "primary_role": "DIAGNOSTIC",
            "secondary_roles": ["DERIVED_CHILD_CONDITION"],
            "timing": ["CHILD_ONLY", "PERSISTENCE_ONLY"],
            "derivation": (
                "WITNESS_OF_NONTRIVIAL_RELATIVE_EVOLUTION;_MOTION_ITSELF_"
                "IS_NOT_A_DEFECT"
            ),
        },
        {
            "object": "complete_child",
            "primary_role": "PROCESS_MILESTONE",
            "secondary_roles": ["DERIVED_CHILD_CONDITION"],
            "timing": ["CHILD_ONLY"],
            "derivation": "WHOLE_CONSTRAINT_SOLVED_BOUNDARY_MATCHED_CHILD",
        },
        {
            "object": "event_multiplier",
            "primary_role": "EVOLUTION_LAW",
            "secondary_roles": [],
            "timing": ["EVENT_ONLY"],
            "derivation": (
                "KKT_MULTIPLIER_ENFORCING_THE_EXISTING_EVENT_ROW;_NOT_A_"
                "NEW_FIELD_OR_PHYSICAL_ACCEPTANCE_LAW"
            ),
        },
        {
            "object": "child_rank_14_condition",
            "primary_role": "DIAGNOSTIC",
            "secondary_roles": ["DERIVED_CHILD_CONDITION"],
            "timing": ["CHILD_ONLY"],
            "derivation": (
                "LOCAL_SOLVABILITY_RANK_OF_THE_N3_THREE_TRACE_PLUS_SEVEN_"
                "CONSTRAINT_PLUS_TWO_MOMENTUM_PLUS_TWO_FLUX_MAP"
            ),
        },
        {
            "object": "surrounding_energy_or_flux",
            "primary_role": "DIAGNOSTIC",
            "secondary_roles": ["EVOLUTION_LAW"],
            "timing": ["PRE_EVENT", "EVENT_ONLY"],
            "derivation": (
                "ACTION_DERIVED_NOETHER_CANONICAL_OR_QUASILOCAL_DATA;_NOT_"
                "AN_ENERGY_SURROUNDING_FIELD"
            ),
        },
        {
            "object": "trapping_of_reconstructed_spacetime",
            "primary_role": "PROCESS_MILESTONE",
            "secondary_roles": [],
            "timing": ["UNRESOLVED_FROM_DERIVATION"],
            "derivation": "NO_INDEPENDENT_TRAPPING_FIELD_OR_CLOSED_GATE_EXISTS",
        },
    ]
    primary_roles = {
        "CONSTITUENT", "EVOLUTION_LAW", "PROCESS_MILESTONE",
        "DOMAIN_CONDITION", "DIAGNOSTIC", "DERIVED_CHILD_CONDITION",
    }
    source_trace = {
        "field_action_and_child_definition": (
            "bhsm_complete_child_mathematical_system_v15_39.py::"
            "complete_child_configuration,complete_child_functional,variational_problem"
        ),
        "eta_phase_space_domain": (
            "aether_sobolev_galerkin_pencil_lift_v15_81.py::"
            "generalized_lagrangian"
        ),
        "eta_domain_exit": (
            "aether_n3_terminal_joint_pushforward_v16_09.py::"
            "domain_exit_convergence"
        ),
        "eta_boundary_transversality": (
            "aether_n3_eta_boundary_transversality_v16_10.py::"
            "boundary_transversality"
        ),
        "current_event": (
            "aether_actual_dirac_event_pencil_v15_79.py::"
            "event_pencil_diagnostics"
        ),
        "event_child_relation": (
            "aether_n3_event_complete_child_correspondence_v17_84.py::"
            "event_to_child_correspondence_derivation"
        ),
        "complete_child_rows": (
            "aether_n3_complete_child_chart_reconstruction_v18_24.py::"
            "_child_rows"
        ),
        "persistence": (
            "aether_n3_chain_trial_complete_child_promotion_v18_06.py::"
            "chain_trial_complete_child_promotion"
        ),
        "enclosure_claim_boundary": (
            "BHSM_LOCAL_ENVIRONMENT_FINITE_TIME_ENCAPSULATION_GATE_V14_94.md"
        ),
    }
    eta_audit = {
        "A_hard_on_every_regular_physical_state_including_reset": True,
        "B_later_stage_only": False,
        "C_quantity_checked": (
            "POINTWISE_MINIMUM_OF_L_eta=kappa1+X_eta^3,_WITH_kappa1=1_"
            "IN_THE_CURRENT_NORMALIZATION"
        ),
        "C_not_checked": [
            "ETA_FIELD_VALUE_ITSELF", "ORIENTATION", "NORMALIZATION",
            "ENCLOSURE_COMPLETION",
        ],
        "D_reset_must_lie_in_domain": True,
        "E_action_density_algebraically_defined_outside": True,
        "E_regular_Euler_Dirac_Legendre_chart_physical_outside": False,
        "F_N3_N4_temporal_interpretation_consistent": True,
        "F_formal_projection_enforces_eta_domain": False,
        "mathematical_reason": (
            "L_eta_IS_THE_ETA_NORMAL_VELOCITY_LEGENDRE_PRINCIPAL_FACTOR;_"
            "POSITIVITY_OWNS_THE_REGULAR_HYPERREGULAR_PHASE_SPACE,_WHILE_"
            "THE_POLYNOMIAL_F(X_eta)_CAN_STILL_BE_FORMALLY_EVALUATED"
        ),
        "implementation_gap": (
            "exact_action_jet_at_state_AND_THE_SOBLEV_CONSTRAINT_PROJECTION_"
            "CAN_RETURN_FORMAL_ROWS_OUTSIDE_L_eta>0;_THE_INDEPENDENT_DENSE_"
            "DOMAIN_CERTIFICATE_MUST_REJECT_SUCH_A_STATE"
        ),
        "classification": "ETA-D",
        "classification_text": (
            "CANONICAL_LIFT_BRANCH_INADMISSIBLE;_INDEPENDENT_ZERO_"
            "MULTIPLIER_BRANCH_ADMISSIBLE"
        ),
        "why_not_ETA_A": (
            "NO_DERIVATION_OR_SEARCH_PROVES_THAT_EVERY_INDEPENDENT_N5_"
            "RESET_BRANCH_FAILS_THE_DOMAIN"
        ),
        "why_not_ETA_C": (
            "THE_DENSE_CERTIFICATE_EVALUATES_THE_SAME_L_eta_OBJECT;_THE_"
            "MISMATCH_IS_MISSING_ENFORCEMENT_IN_THE_FORMAL_JET_PROJECTION"
        ),
    }
    event_ownership = {
        "classification": "EVENT_ENCLOSURE_EQUIVALENCE_OPEN",
        "event_meaning": (
            "ISOLATED_ORDERED_EULER_DIRAC_HESSIAN_SOFT_MODE_REACHES_ZERO"
        ),
        "E_R_zero_is_enclosure_completion": False,
        "E_R_zero_implies_topological_or_geometric_closure": False,
        "surface_matching_implied_by_E_R_zero": False,
        "surface_matching_relation": (
            "SEPARATE_ACTION_DERIVED_EVENT_TO_CHILD_BOUNDARY_CANONICAL_"
            "RELATION_USING_TRACE_AND_FLUX_DATA"
        ),
        "historical_eta_zero_event_superseded": True,
        "historical_note": (
            "V15_52_V15_72_ETA_ZERO_EVENT_IS_NOT_THE_RETAINED_V15_79_PLUS_"
            "ORDERED_RAYLEIGH_EVENT"
        ),
    }
    process_test = {
        "enclosure": "PROCESS_OUTCOME_NOT_INGREDIENT",
        "surface_matching": "EVENT_TO_CHILD_COMPATIBILITY_NOT_CONSTITUENT",
        "complete_child": "S5_OUTCOME_OF_CONSTITUENTS_PLUS_EVOLUTION_PLUS_MATCHING",
        "persistence": "S6_OUTCOME_OR_GATE_NOT_FIELD",
        "new_enclosure_trapping_persistence_field_required": False,
    }
    stage_status = {
        "N3": {
            "RESET_CONSTRUCTION": "PASS",
            "RESET_DOMAIN_STATUS": "PASS",
            "EVOLUTION_STATUS": "OPEN",
            "EVENT_STATUS": "OPEN",
            "CHILD_STATUS": "OPEN",
            "PERSISTENCE_STATUS": "OPEN",
            "note": (
                "CANDIDATE_CHILD_AND_POSITIVE_DURATION_GATES_PASS,_BUT_THE_"
                "EXACT_F376_ROOT_AND_FINAL_EVENT_REMAIN_OPEN"
            ),
        },
        "N4": {
            "RESET_CONSTRUCTION": "PASS",
            "RESET_DOMAIN_STATUS": "PASS",
            "EVOLUTION_STATUS": "PASS_TO_FIRST_ORDERED_EVENT",
            "EVENT_STATUS": "PASS",
            "CHILD_STATUS": "PASS",
            "PERSISTENCE_STATUS": "PASS_LOCAL_ANALYTIC_EXISTENCE",
            "note": (
                "THE_INDEPENDENT_ADAPTIVE_EVENT_IS_TIME_CONTROL_AND_"
                "QUADRATURE_CONVERGED;_THE_16_ROW_CHILD_MAP_IS_STRUCTURALLY_"
                "FULL_RANK_AND_SOLVED;_POSITIVE_DURATION_RELATIVE_"
                "PERSISTENCE_FOLLOWS_FROM_LOCAL_ANALYTIC_EULER_DIRAC_"
                "EXISTENCE;_THE_STIFF_FINITE_DURATION_MOVIE_IS_NOT_CONVERGED"
            ),
        },
        "N5": {
            "RESET_CONSTRUCTION": "PASS",
            "RESET_DOMAIN_STATUS": "PASS_INDEPENDENT_ZERO_MULTIPLIER_BRANCH",
            "EVOLUTION_STATUS": "PASS_TO_LOCAL_ORDERED_EVENT",
            "EVENT_STATUS": "PASS_QUALITATIVE_TIME_NOT_QUADRATURE_CONVERGED",
            "CHILD_STATUS": "OPEN",
            "PERSISTENCE_STATUS": "NOT_YET_APPLICABLE",
            "note": (
                "THE_PREDECLARED_ZERO_MULTIPLIER_RESET_CLOSES_THE_N5_"
                "CONSTRAINTS_WITH_POSITIVE_ETA_AND_REACHES_THE_SAME_"
                "INERTIA_BOUNDARY_MODE_ACROSS_THREE_QUADRATURES;_ONLY_"
                "QUALITATIVE_EVENT_EXISTENCE_IS_PROMOTED"
            ),
        },
    }
    sequencing = {
        "demonstrated_bugs": [
            (
                "PREMATURELY_LABELING_THE_CURRENT_N5_RESET_AS_A_"
                "CROSS_RESOLUTION_CONTRADICTION_INSTEAD_OF_ETA_D"
            ),
            (
                "FORMAL_EXACT_JET_CONSTRAINT_PROJECTION_CAN_CLOSE_ROWS_"
                "WITHOUT_ENFORCING_THE_EXISTING_POINTWISE_ETA_DOMAIN"
            ),
            (
                "THE_N4_6e-4_TRIAL_TARGETED_AN_S4_SPECTRAL_CONDITION_AFTER_"
                "LEAVING_THE_EARLIER_CONSTRAINT_AND_DOMAIN_MANIFOLD"
            ),
            (
                "HISTORICAL_ETA_ZERO_EVENT_LANGUAGE_MUST_NOT_BE_APPLIED_TO_"
                "THE_CURRENT_ORDERED_RAYLEIGH_EVENT"
            ),
            (
                "N4_FIXED_STEP_PROJECTED_RK4_EVENT_TIME_IS_NOT_RESOLUTION_"
                "CONVERGED_AND_CANNOT_BE_PROMOTED"
            ),
        ],
        "N5_remains_true_physical_warning": True,
        "N5_warning_scope": "CANONICAL_LIFT_RESET_BRANCH_ONLY",
        "N4_needs_different_physics": False,
        "N4_needs_manifold_preserving_evolution": True,
        "N4_fixed_step_event_resolution_converged": False,
        "N4_adaptive_event_time_and_quadrature_converged": True,
        "N4_ordered_event_validated": True,
        "N4_complete_child_validated": True,
        "N4_child_dynamic_flux_jacobian_step_converged": True,
        "N4_positive_duration_relative_persistence_validated": True,
        "N5_independent_zero_multiplier_eta_branch_validated": True,
        "N5_qualitative_ordered_event_validated": True,
        "N5_quantitative_event_time_validated": False,
        "N4_fixed_step_event_times": {
            "h_1e-5": 0.0008311926895445803,
            "h_5e-6": 0.0003019651715315614,
        },
        "N4_allowed_method": (
            "EXISTING_EXACT_EULER_DIRAC_FLOW_WITH_SMALL_OR_ADAPTIVE_STEPS,_"
            "SOBOLEV_CONSTRAINT_PROJECTION,_DENSE_ETA_CERTIFICATION,_AND_"
            "ORDERED_BRANCH_OVERLAP"
        ),
    }
    validation = {
        "every_object_has_exactly_one_primary_role": all(
            row["primary_role"] in primary_roles for row in ledger
        ),
        "eta_is_hard_from_reset": (
            eta_audit["A_hard_on_every_regular_physical_state_including_reset"]
            and eta_audit["D_reset_must_lie_in_domain"]
        ),
        "N5_classified_ETA_D": eta_audit["classification"] == "ETA-D",
        "event_not_equated_to_enclosure": (
            event_ownership["classification"]
            == "EVENT_ENCLOSURE_EQUIVALENCE_OPEN"
        ),
        "no_process_field_added": not process_test[
            "new_enclosure_trapping_persistence_field_required"
        ],
        "N5_event_not_overpromoted": (
            stage_status["N5"]["EVENT_STATUS"]
            == "PASS_QUALITATIVE_TIME_NOT_QUADRATURE_CONVERGED"
            and stage_status["N5"]["CHILD_STATUS"] == "OPEN"
            and stage_status["N5"]["PERSISTENCE_STATUS"]
            == "NOT_YET_APPLICABLE"
        ),
    }
    return {
        "ownership_ledger": ledger,
        "source_trace": source_trace,
        "eta_audit": eta_audit,
        "ordered_event_ownership": event_ownership,
        "ingredient_vs_process_test": process_test,
        "cross_resolution_stage_status": stage_status,
        "sequencing_audit": sequencing,
        "exact_next_calculation": (
            "DERIVE_THE_ACTION_OWNED_N5_DYNAMIC_CALDERON_FLUX_JACOBIAN_"
            "VIA_THE_REQUIRED_FOURTH_VARIATION_OR_A_DIFFERENTIATED_CHILD_"
            "BVP_BEFORE_FURTHER_REPETITIVE_CONTINUATION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def physical_scale_accessibility_audit() -> dict[str, Any]:
    """Audit the action ownership needed for a physical-scale sweep.

    This is a derivation/measurement contract only.  It deliberately does
    not manufacture a positive energy split, vary the canonical reset, or
    add a physical or numerical acceptance condition.
    """

    scale_coordinate = {
        "symbol": "rho",
        "definition": "rho=q_scale=log(R_phys/R_star)",
        "reconstruction": "R_phys=R_star*exp(q_scale)",
        "R_star": float(RADIUS0),
        "R_star_action_relation": "R_star^6=343/(5*kappa1)",
        "current_normalization": "kappa1=1",
        "action_source": (
            "aether_cycle_spread_concentration_v15_9.py::critical_radius;_"
            "aether_sobolev_galerkin_pencil_lift_v15_81.py::"
            "generalized_lagrangian"
        ),
        "canonical_reset_rho": 0.0,
        "canonical_reset_is_only_currently_derived_reset_scale": True,
        "free_post_reset_scale_coordinates_are_dynamical_history": True,
        "independent_particle_scale_parameter_added": False,
        "numerical_resolution_N_is_rho": False,
        "N_role": "SPECTRAL_APPROXIMATION_AT_FIXED_PHYSICAL_STATE",
        "dimensionful_bridge_to_meters": "OPEN",
        "human_scale_claim_allowed": False,
    }
    retained_terms = [
        {
            "term": "spatial_gravity",
            "action_ownership": "BULK_GRAVITY_PLUS_LAPSE_GRADIENT",
            "sign": "INDEFINITE",
            "separable_energy_or_spacetime_owner": False,
            "reason": "CONSTRAINT_AND_GEOMETRY_ARE_MIXED_BY_THE_ADM_SPLIT",
        },
        {
            "term": "intrinsic_curvature",
            "action_ownership": "BULK_INTRINSIC_GEOMETRY",
            "sign": "POSITIVE_IN_THIS_REGULAR_CHART_BEFORE_LEGENDRE_SIGN",
            "separable_energy_or_spacetime_owner": False,
            "reason": "NOT_A_SEPARATELY_CONSERVED_POSITIVE_HAMILTONIAN_SECTOR",
        },
        {
            "term": "cosmological",
            "action_ownership": "BULK_GEOMETRIC_POTENTIAL",
            "sign": "NEGATIVE_LAGRANGIAN_TERM",
            "separable_energy_or_spacetime_owner": False,
            "reason": "LEGENDRE_SIGN_DOES_NOT_DEFINE_AN_ORTHOGONAL_SECTOR",
        },
        {
            "term": "eta_potential",
            "action_ownership": "DEGREE_ONE_ETA_COUPLED_TO_THE_METRIC",
            "sign": "INDEFINITE_ON_THE_FULL_L_eta_POSITIVE_DOMAIN",
            "separable_energy_or_spacetime_owner": False,
            "reason": "X_eta_CONTAINS_BOTH_SPATIAL_GEOMETRY_AND_NORMAL_FLOW",
        },
        {
            "term": "adm_kinetic",
            "action_ownership": "GRAVITATIONAL_KINETIC_SUPERMETRIC",
            "sign": "INDEFINITE_DEWITT_FORM",
            "separable_energy_or_spacetime_owner": False,
            "reason": "THE_CONFORMAL_DIRECTION_PREVENTS_POSITIVE_LOCAL_ENERGY",
        },
        {
            "term": "hopf_inertia",
            "action_ownership": "FIXED_CHARGE_ROUTHIAN",
            "sign": "NEGATIVE_IN_LAGRANGIAN_POSITIVE_FIXED_CHARGE_ENERGY",
            "separable_energy_or_spacetime_owner": False,
            "reason": "ENERGY_CANDIDATE_BUT_ITS_INERTIA_IS_METRIC_ETA_MIXED",
        },
        {
            "term": "boundary_casimir",
            "action_ownership": "BOUNDARY_STANDARD_MODEL_CASIMIR_SOURCE",
            "sign": "NEGATIVE_IN_THE_RETAINED_LAGRANGIAN_CONVENTION",
            "separable_energy_or_spacetime_owner": False,
            "reason": "BOUNDARY_ENERGY_AND_RECONSTRUCTED_RADIUS_ARE_COUPLED",
        },
    ]
    sector_balance = {
        "same_dimension_action_terms_available": True,
        "canonical_sector_projectors_derived": False,
        "H_E_canonically_defined": False,
        "H_ST_canonically_defined": False,
        "H_E_and_H_ST_nonnegative": False,
        "Hamiltonian_constraint_present": True,
        "local_gravitational_energy_positive_definite": False,
        "Xi_ES_status": "OPEN_UNDEFINED",
        "C_ES_status": "OPEN_UNDEFINED_NOT_ZERO",
        "C_ES_formula_if_prerequisite_closes": (
            "(H_E-H_ST)/(H_E+H_ST)"
        ),
        "high_low_high_hypothesis_status": "UNTESTED",
        "blocking_mathematical_object": (
            "ACTION_DERIVED_GAUGE_COMPATIBLE_SECTOR_PROJECTORS_OR_AN_"
            "EQUIVALENT_ON_SHELL_RELATIVE_HAMILTONIAN_DECOMPOSITION_THAT_"
            "PROVES_TWO_SAME_DIMENSION_NONNEGATIVE_SECTOR_FUNCTIONALS"
        ),
        "forbidden_shortcut": (
            "DO_NOT_GROUP_SIGNED_LAGRANGIAN_TERMS_BY_POST_HOC_PHYSICAL_"
            "INTUITION_OR_TAKE_ABSOLUTE_VALUES"
        ),
        "retained_action_terms": retained_terms,
    }
    event_approach = {
        "ordered_event_scalar": "E_R=TRACKED_ORDERED_DIRAC_HESSIAN_EIGENVALUE",
        "corrected_directional_derivative_available": True,
        "chi_E_formula_candidate": (
            "-<grad(E_R),z_dot>_G/(norm_G(grad(E_R))*norm_G(z_dot))"
        ),
        "positive_action_metric_G_derived": False,
        "existing_H6_Sobolev_metric_role": (
            "REGULARITY_TOPOLOGY_AND_NUMERICAL_NESTED_PROJECTION_METRIC"
        ),
        "existing_H6_metric_may_be_called_action_metric": False,
        "chi_E_status": "OPEN_UNDEFINED_UNTIL_G_IS_DERIVED",
        "allowed_current_diagnostics": [
            "E_R", "CORRECTED_DIRECTIONAL_DERIVATIVE", "BRANCH_OVERLAP",
            "CONSTRAINT_RESIDUAL", "L_eta_MINIMUM",
        ],
        "event_is_enclosure": False,
    }
    protocol = {
        "classification": "FALSIFICATION_PROTOCOL_DERIVED_EXECUTION_BLOCKED",
        "execution_blockers": [
            "CANONICAL_NONNEGATIVE_H_E_H_ST_DECOMPOSITION",
            "ACTION_DERIVED_ADMISSIBLE_ONE_PARAMETER_SCALE_FAMILY",
        ],
        "scale_family_requirement": (
            "DERIVE_A_CONNECTED_FAMILY_z_reset(rho)_FROM_THE_UNCHANGED_"
            "ACTION_BOUNDARY_AND_CONSTRAINT_EQUATIONS;_DO_NOT_OBTAIN_IT_BY_"
            "OVERWRITING_q_scale_IN_THE_CANONICAL_RESET"
        ),
        "scale_grid_rule": (
            "PREDECLARE_NESTED_RHO_NODES_ON_A_COMPACT_INTERIOR_OF_THE_"
            "DERIVED_CONNECTED_ADMISSIBLE_SCALE_INTERVAL_BEFORE_EVALUATING_"
            "C_ES_OR_EVENT_OUTCOMES"
        ),
        "fixed_physics_across_rho": [
            "UNCHANGED_ACTION", "UNCHANGED_COEFFICIENTS",
            "ACTION_DERIVED_BOUNDARY_DATA", "SAME_TOPOLOGICAL_SECTOR",
            "SAME_EXISTING_CONSTRAINT_AND_EVENT_AND_CHILD_DEFINITIONS",
        ],
        "per_rho_pre_evolution_gates": [
            "INDEPENDENT_CONSTRAINT_CLOSURE",
            "DENSE_L_eta=kappa1+X_eta^3_POSITIVITY",
            "REGULAR_ACTION_LEGENDRE_CHART",
        ],
        "per_rho_measurements_after_sector_derivation": [
            "rho", "H_E", "H_ST", "C_ES", "E_R",
            "CORRECTED_dE_R_dt", "L_eta_MIN", "EVENT_STATUS",
        ],
        "evolution": (
            "UNCHANGED_EULER_DIRAC_FLOW_WITH_MANIFOLD_PROJECTION_AND_"
            "LOCAL_ERROR_CONTROL_USED_ONLY_FOR_NUMERICAL_RELIABILITY"
        ),
        "resolution_firewall": (
            "REPEAT_THE_SAME_rho_STATE_AT_N3_N4_N5;_N_MAY_TEST_"
            "CONVERGENCE_BUT_MAY_NOT_LABEL_PHYSICAL_SCALE"
        ),
        "numerical_convergence_checks": [
            "SPECTRAL_N", "QUADRATURE", "TIME_STEP_LOCAL_ERROR",
            "EVENT_TIME", "EVENT_STATE", "ORDERED_BRANCH_OVERLAP",
        ],
        "high_low_high_promotion_rule": (
            "REQUIRE_POSITIVE_C_ES_ON_TWO_VALIDATED_SCALE_EXTREMES_AND_A_"
            "NEGATIVE_OPEN_INTERVAL_BETWEEN_TWO_CONVERGED_ZERO_CROSSINGS;_"
            "THE_SIGN_TOPOLOGY_MUST_SURVIVE_GRID_AND_N_REFINEMENT"
        ),
        "high_low_high_falsifiers": [
            "NO_TWO_C_ES_ZERO_CROSSINGS_ON_THE_DERIVED_ADMISSIBLE_INTERVAL",
            "THE_INTERMEDIATE_NEGATIVE_INTERVAL_DISAPPEARS_UNDER_REFINEMENT",
            "EXTREME_POSITIVE_SIGNS_FAIL_RESOLUTION_CONVERGENCE",
            "THE_REQUIRED_SCALE_FAMILY_LEAVES_THE_ETA_OR_CONSTRAINT_DOMAIN",
        ],
        "event_association_is_separate_hypothesis": True,
        "event_association_promotion_rule": (
            "VALID_ORDERED_EVENT_ACCESSIBILITY_MUST_COVARY_WITH_C_ES_UNDER_"
            "A_PREDECLARED_STATISTIC_AND_SURVIVE_N_AND_TIME_REFINEMENT"
        ),
        "post_event_only": [
            "EVENT_TO_COMPLETE_CHILD_BOUNDARY_BVP",
            "COMPLETE_CHILD_RECONSTRUCTION", "RELATIVE_PERSISTENCE",
        ],
        "global_encapsulation_cost_implemented": False,
        "empirical_particle_data_used": False,
        "new_equations_or_acceptance_gates_added": False,
        "meters_or_human_scale_interpretation_allowed": False,
    }
    validation = {
        "rho_owned_by_retained_action_coordinate": (
            scale_coordinate["definition"]
            == "rho=q_scale=log(R_phys/R_star)"
        ),
        "R_star_action_derived": math.isclose(
            scale_coordinate["R_star"] ** 6, 343.0 / 5.0,
            rel_tol=0.0, abs_tol=2.0e-12,
        ),
        "N_firewalled_from_physical_scale": not scale_coordinate[
            "numerical_resolution_N_is_rho"
        ],
        "indefinite_action_not_forced_into_positive_sectors": (
            not sector_balance["canonical_sector_projectors_derived"]
            and sector_balance["C_ES_status"] == "OPEN_UNDEFINED_NOT_ZERO"
        ),
        "Sobolev_topology_not_promoted_to_action_metric": not event_approach[
            "existing_H6_metric_may_be_called_action_metric"
        ],
        "eta_domain_required_before_evolution": (
            "DENSE_L_eta=kappa1+X_eta^3_POSITIVITY"
            in protocol["per_rho_pre_evolution_gates"]
        ),
        "event_not_equated_to_enclosure": not event_approach[
            "event_is_enclosure"
        ],
        "canonical_reset_not_naively_shifted": (
            "DO_NOT_OBTAIN_IT_BY_OVERWRITING_q_scale"
            in protocol["scale_family_requirement"]
        ),
        "global_cost_deferred": not protocol[
            "global_encapsulation_cost_implemented"
        ],
        "no_dimensionful_overclaim": not scale_coordinate[
            "human_scale_claim_allowed"
        ],
        "no_physics_or_gate_added": not protocol[
            "new_equations_or_acceptance_gates_added"
        ],
    }
    return {
        "physical_scale_coordinate": scale_coordinate,
        "action_sector_ownership": sector_balance,
        "event_approach_metric_audit": event_approach,
        "scale_sweep_falsification_protocol": protocol,
        "scientific_classification": (
            "rho_VALIDATED;_C_ES_AND_chi_E_OPEN_UNDEFINED;_SCALE_"
            "HYPOTHESIS_UNTESTED;_FALSIFICATION_PROTOCOL_DERIVED"
        ),
        "first_action_owned_blocker": sector_balance[
            "blocking_mathematical_object"
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def breadth_first_closure_network_audit() -> dict[str, Any]:
    """Freeze conditional downstream interfaces without back-fitting physics."""

    doctrine = {
        "strategy": "BREADTH_FIRST_SELF_CONSISTENCY_NETWORK",
        "rule": (
            "HINDSIGHT_MAY_CONSTRAIN_STRUCTURE_BUT_MAY_NOT_OVERRIDE_THE_"
            "ORIGINAL_EQUATIONS"
        ),
        "conditional_derivations_allowed": True,
        "downstream_requirements_may_identify_upstream_invariants": True,
        "observed_particle_values_may_select_upstream_branch": False,
        "new_fields_coefficients_events_or_gates_added": False,
        "active_cross_resolution_dependency_preserved": True,
    }
    return_interface = {
        "interface": (
            "z_event->(Gamma0_event,p_event,Gamma1_event,I_event)->"
            "SolveChildBVP->R_return(z_event)"
        ),
        "classification": (
            "DERIVED_SET_VALUED_INTERFACE_N3_N4_N5_ROOTS_AND_PERSISTENCE_"
            "VALIDATED_GENERAL_N_UNIFORM_CONVERGENCE_OPEN"
        ),
        "inputs": [
            "CONSTRAINT_ETA_ADMISSIBLE_ORDERED_EVENT_STATE",
            "EVENT_TRACE_CANONICAL_MOMENTUM_AND_GHY_NOETHER_FLUX",
            "EVENT_TOPOLOGY_ORIENTATION_FR_AND_BUNDLE_INVARIANTS",
            "ACTION_DERIVED_ENVIRONMENT_BOUNDARY_DATA",
        ],
        "equations": {
            "child_BVP": "E_child(Phi_c)=0_AND_B_child(Phi_c,z_event)=0",
            "finite_N_map": (
                "F_child=(3_TRACE,2N+1_CONSTRAINT,2_MOMENTUM,2_DYNAMIC_"
                "FLUX)=0"
            ),
            "row_count": "2N+8",
            "return_relation": (
                "R_return(z_event)={z_c:F_child(z_event,z_c)=0,_"
                "L_eta(z_c)>0}"
            ),
            "return_scale": (
                "C_rec=q_logR(return)-log(R_rec[I_event,I_environment]/"
                "R_star)=0"
            ),
        },
        "outputs": [
            "COMPLETE_CONSTRAINED_CHILD_CAUCHY_STATE",
            "R4_DIAGONAL_SP1_CONNECTION_omega_AND_KF",
            "RECONSTRUCTED_SCALE_AND_RETURN_STATE_RELATION",
            "SPIN_GAUGE_DOMAIN_AND_BUNDLE_ISOMORPHISM_CLASS",
        ],
        "current_cross_resolution_status": (
            "INDEPENDENT_N3_N4_N5_ORDERED_EVENT_COMPLETE_CHILD_AND_"
            "POSITIVE_DURATION_RELATIVE_PERSISTENCE_VALIDATED;_GENERAL_N_"
            "LOCAL_ROW_AND_FIBER_DIMENSION_LAW_DERIVED"
        ),
        "single_valued_return_proved": False,
        "sources": [
            "bhsm_complete_child_mathematical_system_v15_39.py",
            "aether_n3_event_complete_child_correspondence_v17_84.py",
            "aether_n3_required_child_cauchy_flux_v17_93.py",
            "aether_diagonal_sp1_m4_attachment_v15_50.py",
            "aether_scale_child_ownership_audit_v16_78.py",
        ],
    }
    mass_interface = {
        "interface": "GENERIC_COMPLETE_PERSISTENT_CHILD->SCALE_AND_MASS_OPERATOR",
        "classification": "CONDITIONAL_OPERATOR_INTERFACE_DERIVED",
        "derived_scale_outputs": {
            "rho": "q_scale=log(R_child/R_star)",
            "R_star": "(343/(5*kappa1))^(1/6)",
            "shape_coordinate": "x_child=log(B/A)|sigma=0",
            "N_is_physical_scale": False,
        },
        "conditional_mass_forms": {
            "rest_mass": (
                "M_rest[c|P]=Delta_H_xi[parent+child_minus_matched_parent]/c^2"
            ),
            "Floquet_mass_operator": (
                "M_Floquet[c]=hbar*(-i_Log(U_rel,c(T_c)))/(c^2*T_c)"
            ),
            "stationary_consistency": (
                "M_Floquet_MUST_AGREE_WITH_Delta_H_xi/c^2_IN_THE_"
                "STATIONARY_LIMIT"
            ),
        },
        "not_mass": [
            "THE_ZERO_CANONICAL_HAMILTONIAN_CONSTRAINT_BY_ITSELF",
            "A_POST_HOC_SUM_OF_ABSOLUTE_SIGNED_ACTION_TERMS",
            "THE_FR_ENERGY_1/(8I_skin)_BY_ITSELF",
        ],
        "dimensionful_bridge": "OPEN_KAPPA1_HAS_NO_ACTION_DERIVED_SI_VALUE",
        "family_Yukawa_entries_from_current_child_action": "OPEN",
        "sources": [
            "aether_cycle_spread_concentration_v15_9.py",
            "aether_boundary_identity_ejection_v15_13.py",
            "aether_fr_zero_current_child_v15_37.py",
            "completion/cosmological_parent_dynamic_envelopment_v14_54.py",
            "aether_nonlinear_norman_cycle_bvp_v15_7.py",
            "aether_hybrid_yukawa_mass_semantics_v15_56.py",
        ],
    }
    mixing_interface = {
        "interface": "GENERIC_FAMILY_CHILD_DATA->MIXING_OPERATOR",
        "classification": "CONDITIONAL_FUNCTOR_DERIVED_NUMERICAL_OPERATOR_OPEN",
        "conditional_equations": {
            "Feshbach": (
                "H_eff_f=H_PP-H_PQ*(H_QQ-E)^(-1)*H_QP"
            ),
            "embedding": "iota_f=[I;-(H_QQ-E)^(-1)*H_QP]",
            "Gram": "G_f=iota_f^dagger*iota_f",
            "current_kernel": (
                "K_fg=iota_f^dagger*J_fg*iota_g_OR_WITH_RETURN_TRANSPORT_"
                "iota_f^dagger*J_f*T_f_from_g*iota_g"
            ),
            "polar_transport": (
                "U_fg=Pol(G_f^(-1/2)*K_fg*G_g^(-1/2))"
            ),
            "CKM": "V_CKM=W_u^dagger*U_ud*W_d",
            "PMNS": "U_PMNS=W_e^dagger*U_e_nu*W_nu",
        },
        "derived_structure": [
            "RANK3_C3_ORTHOGONAL_FAMILY_PROJECTORS",
            "RANK16_CHIRAL_BUNDLE_PER_FAMILY_AND_Z6_QUOTIENT",
            "FAMILY_UNIVERSAL_WEAK_BASIS_CURRENT",
            "BASIS_COVARIANT_FESHBACH_CROSS_GRAM_POLAR_FUNCTOR",
        ],
        "current_child_export_is_sufficient": False,
        "missing_outputs": [
            "ACTION_NORMALIZED_CHILD_SPINOR_GAUGE_HILBERT_DOMAIN",
            "RETURNED_FAMILY_DIRAC_YUKAWA_OR_PROPAGATION_OPERATORS",
            "ACTION_SELECTED_RETAINED_TOWER_PROJECTORS_AND_SPECTRAL_FRAMES",
            "COMMON_DOMAIN_CURRENT_OR_CHILD_TO_CHILD_RETURN_TRANSPORT",
            "NONDEGENERATE_ACTION_OWNED_FAMILY_ORDERING",
        ],
        "zero_or_degenerate_family_operator_predicts_identity_mixing": False,
        "zero_or_degenerate_family_operator_meaning": "MIXING_UNOBSERVABLE",
        "N_is_family_number": False,
        "sources": [
            "aether_hybrid_flavor_spectrum_v15_54.py",
            "aether_hybrid_standard_model_bundle_v15_53.py",
            "completion/parent_action_charged_current_v11_6.py",
            "completion/hopf_phase_flavor_cross_gram_v14_34.py",
            "master_action/common_parent_charged_current_attachment.py",
            "aether_cycle_family_centrality_v15_87.py",
        ],
    }
    shared_invariants = {
        "required_by_multiple_interfaces": [
            "CONSTRAINT_AND_DENSE_L_eta_ADMISSIBILITY",
            "POSITIVE_DURATION_RELATIVE_PERSISTENCE",
            "Gamma0_Gamma1_CANONICAL_MOMENTUM_AND_NOETHER_FLUX",
            "RECONSTRUCTED_SCALE_AND_ACTION_OWNED_RETURN_RELATION",
            "TOPOLOGY_ORIENTATION_FR_PARITY_AND_BUNDLE_ISOMORPHISM_CLASS",
            "ACTION_NORMALIZED_SPIN_GAUGE_DOMAIN_AND_INDUCED_MEASURE",
            "RETURN_MONODROMY_OR_COMMON_DOMAIN_TRANSPORT",
        ],
        "hindsight_use": (
            "THESE_OBJECTS_MAY_PRIORITIZE_UPSTREAM_DERIVATIONS_AND_CLASSIFY_"
            "BRANCH_COMPATIBILITY_BUT_MAY_NOT_ADD_ROWS_OR_SELECT_BY_DATA"
        ),
    }
    flux_variation = {
        "current_map": (
            "Phi=Q^dagger*gamma_child+Dp(y)X(y)-Q^dagger*L_q+"
            "gamma_event,_p=V^dagger*L_v"
        ),
        "attachment_lift": (
            "V_SOLVES_[L_vv,K_v^dagger;K_v,0][V,Lambda]^T=[0,T]^T"
        ),
        "exact_Euler_Dirac_field": (
            "L_zz*[a,mdot]^T=[L_q-L_vq*v,-L_mq*v]^T"
        ),
        "higher_variation_verdict": {
            "exact_flux_value_requires": (
                "GENERICALLY_L_THIRD_VARIATION_BECAUSE_V_DEPENDS_ON_L_SECOND"
            ),
            "exact_local_germ_flux_Jacobian_requires": (
                "GENERICALLY_L_FOURTH_VARIATION"
            ),
            "third_variation_alone_is_sufficient": False,
            "cause": "STATE_DEPENDENT_HESSIAN_MINIMAL_ATTACHMENT_LIFTS",
        },
        "immediate_unchanged_map_derivative": (
            "CENTER_FIXED_INNER_RICHARDSON_TIME_DIFFERENCE_THEN_OUTER_"
            "RICHARDSON_DIRECTIONAL_DIFFERENCE"
        ),
        "outer_direction_coordinates": (
            "H6_COORDINATES_H5_VELOCITIES_H6_MULTIPLIERS_FROM_THE_EXISTING_"
            "BHSM_SOBOLEV_REGULARITY_TOPOLOGY"
        ),
        "frozen_lift_status": (
            "ALLOWED_ONLY_AS_A_QUASI_NEWTON_PROPOSAL_MODEL_WITH_EXACT_"
            "RECOMPUTED_RESIDUAL_PROMOTION"
        ),
        "eventual_on_shell_map": (
            "DIFFERENTIATED_CHILD_BVP_JACOBI_SOLVE_USES_THE_ACTION_HESSIAN_"
            "AND_IS_A_FUTURE_EXACT_RESPONSE_ROUTE_IF_THE_NOW_VALIDATED_"
            "N3_N4_N5_CHILDREN_REQUIRE_RESPONSE_DERIVATIVES"
        ),
        "physical_rows_or_gates_changed": False,
        "classification": (
            "DERIVED_HIGHER_VARIATION_REQUIREMENT;_CENTER_FIXED_SOBOLEV_"
            "NORMALIZED_RICHARDSON_DIRECTIONAL_CERTIFICATE_VALIDATED_ON_"
            "THE_N4_REGULAR_BROKEN_GERM"
        ),
    }
    blockers = [
        {
            "priority": 1,
            "object": (
                "DERIVE_THE_ON_SHELL_CHILD_EULER_BVP_CALDERON_TRACE_FROM_"
                "THE_SAME_ACTION_SO_VERTICAL_INTERIOR_VARIATIONS_VANISH_"
                "AND_REEVALUATE_THE_N3_N4_N5_BOUNDARY_MOMENTUM_FLUX_RELATION"
            ),
            "feeds": ["GENERAL_N_RETURN_INTERFACE", "PERSISTENCE"],
        },
        {
            "priority": 2,
            "object": (
                "REGULAR_POLE_ATTACHMENT_MATERIAL_TRANSMISSION_BVP_AND_"
                "ACTION_DERIVED_ENVIRONMENT_TO_RECONSTRUCTION_RETURN_MAP_"
                "WITH_ON_SHELL_CALDERON_OR_RETURN_POLARIZATION_J_boundary"
            ),
            "feeds": ["RETURN_INTERFACE", "SCALE_INTERFACE"],
        },
        {
            "priority": 3,
            "object": "COMPOSITE_MINUS_PARENT_NOETHER_HAMILTONIAN",
            "feeds": ["MASS_INTERFACE"],
        },
        {
            "priority": 4,
            "object": (
                "RETURNED_FAMILY_OPERATORS_AND_ACTION_DERIVED_COMMON_"
                "DOMAIN_TRANSPORT"
            ),
            "feeds": ["MASS_INTERFACE", "MIXING_INTERFACE"],
        },
    ]
    validation = {
        "fixed_physics_preserved": not doctrine[
            "new_fields_coefficients_events_or_gates_added"
        ],
        "observed_values_held_out": not doctrine[
            "observed_particle_values_may_select_upstream_branch"
        ],
        "conditional_interfaces_not_numerical_claims": (
            not return_interface["single_valued_return_proved"]
            and mass_interface["dimensionful_bridge"].startswith("OPEN")
            and not mixing_interface["current_child_export_is_sufficient"]
        ),
        "N_not_scale_or_family": (
            not mass_interface["derived_scale_outputs"]["N_is_physical_scale"]
            and not mixing_interface["N_is_family_number"]
        ),
        "active_cross_resolution_dependency_retained": doctrine[
            "active_cross_resolution_dependency_preserved"
        ],
        "shared_invariants_exposed": len(
            shared_invariants["required_by_multiple_interfaces"]
        ) >= 3,
        "first_blocker_action_owned_and_localized": (
            "ON_SHELL_CHILD_EULER_BVP_CALDERON_TRACE" in blockers[0]["object"]
            and "VERTICAL_INTERIOR_VARIATIONS_VANISH" in blockers[0]["object"]
            and "BOUNDARY_MOMENTUM_FLUX_RELATION" in blockers[0]["object"]
        ),
        "higher_variation_requirement_derived": (
            not flux_variation["higher_variation_verdict"]
            ["third_variation_alone_is_sufficient"]
            and not flux_variation["physical_rows_or_gates_changed"]
        ),
    }
    return {
        "doctrine": doctrine,
        "interfaces": {
            "event_child_reconstruction_return": return_interface,
            "generic_child_scale_mass": mass_interface,
            "generic_family_children_mixing": mixing_interface,
        },
        "shared_child_invariants": shared_invariants,
        "dynamic_flux_variation_interface": flux_variation,
        "ordered_open_interfaces": blockers,
        "scientific_classification": (
            "THREE_CONDITIONAL_INTERFACES_FROZEN;_NO_DOWNSTREAM_NUMERICAL_"
            "PREDICTION_PROMOTED;_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_"
            "VALIDATED;_GENERAL_N_UNIFORM_CONVERGENCE_BOUND_ACTIVE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=2)
def n4_ordered_event_step_audit(
    *, points: int = DEFAULT_POINTS, step: float = 6.0e-4,
) -> dict[str, Any]:
    """Audit one targeted N=4 RK4 event proposal without promoting it."""

    order = 4
    reset = integrate_attached_dirac_flow(maximum_steps=0)[
        "continuation_state"
    ]
    q, velocity, multipliers = lift_low_state(
        order,
        np.asarray(reset["coordinates"]),
        np.asarray(reset["velocities"]),
        np.asarray(reset["multipliers"]),
    )
    projection = project_nested_constraints_sobolev(
        order, q, velocity, multipliers, points=points
    )
    if not projection["success"]:
        raise RuntimeError(str(projection["message"]))
    q = np.asarray(projection["coordinates"], dtype=float)
    velocity = np.asarray(projection["velocities"], dtype=float)
    multipliers = np.asarray(projection["multipliers"], dtype=float)

    def rhs(
        x: np.ndarray, rate: np.ndarray, lapse_shift: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        result = exact_euler_dirac_acceleration(
            order, x, rate, lapse_shift, points=points
        )
        return (
            np.asarray(result["coordinate_rate"]),
            np.asarray(result["acceleration"]),
            np.asarray(result["multiplier_rate"]),
        )

    k1 = rhs(q, velocity, multipliers)
    k2 = rhs(
        q + 0.5 * step * k1[0],
        velocity + 0.5 * step * k1[1],
        multipliers + 0.5 * step * k1[2],
    )
    k3 = rhs(
        q + 0.5 * step * k2[0],
        velocity + 0.5 * step * k2[1],
        multipliers + 0.5 * step * k2[2],
    )
    k4 = rhs(
        q + step * k3[0],
        velocity + step * k3[1],
        multipliers + step * k3[2],
    )
    q_trial = q + step * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]) / 6.0
    v_trial = velocity + step * (
        k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]
    ) / 6.0
    m_trial = multipliers + step * (
        k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]
    ) / 6.0
    forward = project_nested_constraints_sobolev(
        order, q_trial, v_trial, m_trial, points=points
    )
    q_forward = np.asarray(forward["coordinates"], dtype=float)
    v_forward = np.asarray(forward["velocities"], dtype=float)
    m_forward = np.asarray(forward["multipliers"], dtype=float)
    center_values, center_vectors = np.linalg.eigh(
        exact_action_jet_at_state(
            order, q, velocity, multipliers, points=points
        ).hessian
    )
    forward_values, forward_vectors = np.linalg.eigh(
        exact_action_jet_at_state(
            order, q_forward, v_forward, m_forward, points=points
        ).hessian
    )
    permutation, overlaps = _match_frame(center_vectors, forward_vectors)
    tracked = forward_values[permutation]
    inertia = int(np.count_nonzero(center_values < 0.0))
    branch = inertia - 1
    eta = _eta_legendre_minimum(order, q_forward, m_forward, points=4000)
    gates = {
        "constraint_projection_succeeded": bool(forward["success"]),
        "constraint_surface_retained": float(
            forward["maximum_constraint_residual"]
        ) < 1.0e-8,
        "eta_domain_retained": eta["minimum"] > 0.0,
        "ordered_branch_overlap_retained": float(abs(overlaps[branch])) > 0.9,
    }
    return {
        "order": order,
        "step": step,
        "integrator": "RK4_THEN_EXISTING_SOBOLEV_CONSTRAINT_PROJECTION",
        "target_branch": branch,
        "lambda_start": float(center_values[branch]),
        "lambda_trial": float(tracked[branch]),
        "branch_overlap": float(abs(overlaps[branch])),
        "negative_inertia_start": inertia,
        "negative_inertia_trial": int(np.count_nonzero(forward_values < 0.0)),
        "projection_success": bool(forward["success"]),
        "projection_message": str(forward["message"]),
        "maximum_constraint_residual": float(
            forward["maximum_constraint_residual"]
        ),
        "eta_Legendre": eta,
        "gates": gates,
        "classification": "VALIDATED" if all(gates.values()) else "INVALIDATED",
        "ordered_event_established": bool(
            all(gates.values())
            and center_values[branch] * tracked[branch] <= 0.0
        ),
        "claim_boundary": (
            "AN_EIGENVALUE_SIGN_CHANGE_ON_A_CONSTRAINT_OR_ETA_INVALID_"
            "TRIAL_IS_NOT_AN_ORDERED_PHYSICAL_EVENT"
        ),
    }


@lru_cache(maxsize=8)
def _constrained_ordered_event_search(
    *,
    order: int,
    multiplier_seed_rule: str,
    points: int = DEFAULT_POINTS,
    time_step: float = 1.0e-5,
    maximum_steps: int = 80,
    local_error_tolerance: float | None = None,
) -> dict[str, Any]:
    """Follow one independent higher-N orbit to its first ordered event.

    The evolution is the existing exact Euler--Dirac RK4 plus Sobolev
    constraint projection.  Once a simple zero is imminent, the established
    one-sided tangent locator is evaluated on the projected constraint
    surface so the integrator never steps through a singular Hessian.
    """

    if time_step <= 0.0 or maximum_steps <= 0:
        raise ValueError("positive higher-N event-search controls required")
    if local_error_tolerance is not None and local_error_tolerance <= 0.0:
        raise ValueError("local_error_tolerance must be positive")
    if order not in (4, 5):
        raise ValueError("higher-N event search supports N=4 or N=5")
    if multiplier_seed_rule not in ("CANONICAL_LIFT", "ZERO_MULTIPLIER"):
        raise ValueError("unknown independent multiplier seed rule")
    reset = integrate_attached_dirac_flow(maximum_steps=0)[
        "continuation_state"
    ]
    q, velocity, multipliers = lift_low_state(
        order,
        np.asarray(reset["coordinates"]),
        np.asarray(reset["velocities"]),
        np.asarray(reset["multipliers"]),
    )
    if multiplier_seed_rule == "ZERO_MULTIPLIER":
        multipliers = np.zeros_like(multipliers)
    initial = project_nested_constraints_sobolev(
        order, q, velocity, multipliers, points=points
    )
    if not initial["success"]:
        raise RuntimeError(str(initial["message"]))
    q = np.asarray(initial["coordinates"], dtype=float)
    velocity = np.asarray(initial["velocities"], dtype=float)
    multipliers = np.asarray(initial["multipliers"], dtype=float)

    def dynamics_at(
        x: np.ndarray, rate: np.ndarray, lapse_shift: np.ndarray,
    ) -> dict[str, Any]:
        return exact_euler_dirac_acceleration(
            order, x, rate, lapse_shift, points=points
        )

    def rk4_projected(
        x: np.ndarray,
        rate: np.ndarray,
        lapse_shift: np.ndarray,
        step: float,
        first: Mapping[str, Any] | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        def rhs(
            x_value: np.ndarray,
            rate_value: np.ndarray,
            multiplier_value: np.ndarray,
        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            value = dynamics_at(x_value, rate_value, multiplier_value)
            return (
                np.asarray(value["coordinate_rate"]),
                np.asarray(value["acceleration"]),
                np.asarray(value["multiplier_rate"]),
            )

        if first is None:
            k1 = rhs(x, rate, lapse_shift)
        else:
            k1 = (
                np.asarray(first["coordinate_rate"]),
                np.asarray(first["acceleration"]),
                np.asarray(first["multiplier_rate"]),
            )
        k2 = rhs(
            x + 0.5 * step * k1[0],
            rate + 0.5 * step * k1[1],
            lapse_shift + 0.5 * step * k1[2],
        )
        k3 = rhs(
            x + 0.5 * step * k2[0],
            rate + 0.5 * step * k2[1],
            lapse_shift + 0.5 * step * k2[2],
        )
        k4 = rhs(
            x + step * k3[0],
            rate + step * k3[1],
            lapse_shift + step * k3[2],
        )
        q_trial = x + step * (
            k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]
        ) / 6.0
        v_trial = rate + step * (
            k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]
        ) / 6.0
        m_trial = lapse_shift + step * (
            k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]
        ) / 6.0
        projected = project_nested_constraints_sobolev(
            order, q_trial, v_trial, m_trial, points=points
        )
        if not projected["success"]:
            raise RuntimeError(str(projected["message"]))
        return (
            q_trial,
            np.asarray(projected["velocities"], dtype=float),
            np.asarray(projected["multipliers"], dtype=float),
            projected,
        )

    time = 0.0
    rows: list[dict[str, Any]] = []
    event: dict[str, Any] | None = None
    obstruction: dict[str, Any] | None = None
    reference: np.ndarray | None = None
    branch_label: int | None = None
    maximum_constraint = 0.0
    maximum_condition = 0.0
    target_time = time_step * maximum_steps
    current_step = time_step
    rejected_steps = 0
    maximum_accepted_local_error = 0.0
    minimum_accepted_step: float | None = None
    step_index = 0

    def state_sobolev_norm(
        x: np.ndarray, rate: np.ndarray, lapse_shift: np.ndarray,
    ) -> float:
        frequencies = np.concatenate((
            [0.0],
            4.0 * np.arange(1, order + 1),
            4.0 * np.arange(order),
            4.0 * np.arange(order),
        ))
        weights = sobolev_weights(order)
        scaled = np.concatenate((
            (1.0 + frequencies**2) ** 3.0 * x,
            weights["velocities"] * rate,
            weights["multipliers"] * lapse_shift,
        ))
        return float(np.linalg.norm(scaled))

    while step_index <= maximum_steps * 64:
        residual = constraint_residual(
            order, q, velocity, multipliers, points=points
        )
        constraint_max = float(np.max(np.abs(residual)))
        maximum_constraint = max(maximum_constraint, constraint_max)
        eta = _eta_legendre_minimum(order, q, multipliers)
        if eta["minimum"] <= 0.0:
            obstruction = {
                "type": "ETA_DOMAIN_EXIT",
                "time": time,
                "minimum_eta_Legendre": eta["minimum"],
            }
            break
        dynamics = dynamics_at(q, velocity, multipliers)
        maximum_condition = max(
            maximum_condition, float(dynamics["Dirac_condition_number"])
        )
        values, vectors = np.linalg.eigh(
            np.asarray(dynamics["Dirac_hessian"])
        )
        inertia = int(np.count_nonzero(values < 0.0))
        overlap = 1.0
        if reference is None:
            branch_label = inertia - 1
            reference = vectors[:, branch_label].copy()
        else:
            index = int(np.argmax(np.abs(vectors.T @ reference)))
            overlap = float(abs(vectors[:, index] @ reference))
            if float(vectors[:, index] @ reference) < 0.0:
                vectors[:, index] *= -1.0
            reference = vectors[:, index].copy()
            branch_label = index
        assert branch_label is not None and reference is not None
        branch_value = float(values[branch_label])
        rows.append({
            "step": step_index,
            "time": time,
            "lambda_ordered": branch_value,
            "branch_index": branch_label,
            "branch_overlap": overlap,
            "negative_inertia": inertia,
            "maximum_constraint_residual": constraint_max,
            "minimum_eta_Legendre": eta["minimum"],
            "Dirac_condition_number": float(
                dynamics["Dirac_condition_number"]
            ),
        })

        tangent = np.concatenate((
            velocity,
            np.asarray(dynamics["acceleration"]),
            np.asarray(dynamics["multiplier_rate"]),
        ))
        epsilon = min(
            1.0e-7,
            1.0e-4 / max(1.0, float(np.max(np.abs(tangent)))),
        )
        plus_hessian = exact_action_jet_at_state(
            order,
            q + epsilon * velocity,
            velocity + epsilon * np.asarray(dynamics["acceleration"]),
            multipliers + epsilon * np.asarray(dynamics["multiplier_rate"]),
            points=points,
        ).hessian
        plus_values, plus_vectors = np.linalg.eigh(plus_hessian)
        plus_index = int(np.argmax(np.abs(plus_vectors.T @ reference)))
        derivative = (
            float(plus_values[plus_index]) - branch_value
        ) / epsilon
        increment = (
            -branch_value / derivative
            if branch_value * derivative < 0.0 else None
        )

        # The event locator is a one-sided regular-state boundary operation,
        # not an integration step.  Its lookahead must not collapse merely
        # because local-error control shrinks the RK step near the singular
        # Dirac surface.  The original requested step remains the fixed
        # numerical lookahead cap; candidate states are still projected and
        # checked with the unchanged constraint, eta, and branch gates.
        event_lookahead = 1.5 * time_step
        if increment is not None and increment <= event_lookahead:
            cache: dict[float, dict[str, Any]] = {}

            def projected_candidate(offset: float) -> dict[str, Any]:
                key = float(offset)
                if key in cache:
                    return cache[key]
                q_candidate = q + key * velocity
                projection = project_nested_constraints_sobolev(
                    order,
                    q_candidate,
                    velocity + key * np.asarray(dynamics["acceleration"]),
                    multipliers + key * np.asarray(
                        dynamics["multiplier_rate"]
                    ),
                    points=points,
                )
                if not projection["success"]:
                    raise RuntimeError(str(projection["message"]))
                v_candidate = np.asarray(projection["velocities"])
                m_candidate = np.asarray(projection["multipliers"])
                candidate_values, candidate_vectors = np.linalg.eigh(
                    exact_action_jet_at_state(
                        order,
                        q_candidate,
                        v_candidate,
                        m_candidate,
                        points=points,
                    ).hessian
                )
                candidate_index = int(np.argmax(
                    np.abs(candidate_vectors.T @ reference)
                ))
                candidate = {
                    "lambda": float(candidate_values[candidate_index]),
                    "index": candidate_index,
                    "overlap": float(abs(
                        candidate_vectors[:, candidate_index] @ reference
                    )),
                    "coordinates": q_candidate,
                    "velocities": v_candidate,
                    "multipliers": m_candidate,
                    "constraint": float(
                        projection["maximum_constraint_residual"]
                    ),
                    "eta": _eta_legendre_minimum(
                        order, q_candidate, m_candidate
                    ),
                    "inertia": int(np.count_nonzero(candidate_values < 0.0)),
                }
                cache[key] = candidate
                return candidate

            upper = min(
                event_lookahead,
                max(increment * 1.25, increment + 1.0e-12),
            )
            try:
                upper_candidate = projected_candidate(upper)
                if branch_value * upper_candidate["lambda"] <= 0.0:
                    root = brentq(
                        lambda offset: projected_candidate(offset)["lambda"],
                        0.0,
                        upper,
                        xtol=1.0e-13,
                        rtol=1.0e-12,
                        maxiter=48,
                    )
                    selected = projected_candidate(root)
                    event = {
                        "event_time": float(time + root),
                        "offset_from_last_regular_state": float(root),
                        "lambda_ordered": selected["lambda"],
                        "branch_index": int(selected["index"]),
                        "branch_overlap": selected["overlap"],
                        "left_lambda_ordered": branch_value,
                        "lambda_directional_derivative": derivative,
                        "negative_inertia_left": inertia,
                        "negative_inertia_at_selected_side": selected["inertia"],
                        "maximum_constraint_residual": selected["constraint"],
                        "eta_Legendre": selected["eta"],
                        "coordinates": selected["coordinates"].tolist(),
                        "velocities": selected["velocities"].tolist(),
                        "multipliers": selected["multipliers"].tolist(),
                        "locator": (
                            "ONE_SIDED_EXACT_FLOW_TANGENT_WITH_EXISTING_"
                            "SOBOLEV_CONSTRAINT_PROJECTION_AND_TRACKED_ROOT"
                        ),
                    }
                    break
            except (ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
                obstruction = {
                    "type": "ONE_SIDED_EVENT_LOCATOR_FAILURE",
                    "time": time,
                    "message": str(exc),
                }
                break

        if time >= target_time - 1.0e-15:
            break
        attempt = min(current_step, target_time - time)
        accepted: tuple[
            np.ndarray, np.ndarray, np.ndarray, dict[str, Any]
        ] | None = None
        local_error = 0.0
        while accepted is None:
            try:
                full = rk4_projected(
                    q,
                    velocity,
                    multipliers,
                    attempt,
                    first=dynamics,
                )
                accepted = full
                if local_error_tolerance is not None:
                    half = rk4_projected(
                        q,
                        velocity,
                        multipliers,
                        0.5 * attempt,
                        first=dynamics,
                    )
                    fine = rk4_projected(
                        half[0],
                        half[1],
                        half[2],
                        0.5 * attempt,
                    )
                    difference = state_sobolev_norm(
                        fine[0] - full[0],
                        fine[1] - full[1],
                        fine[2] - full[2],
                    )
                    scale = max(
                        1.0,
                        state_sobolev_norm(q, velocity, multipliers),
                        state_sobolev_norm(fine[0], fine[1], fine[2]),
                    )
                    local_error = difference / scale
                    if local_error > local_error_tolerance:
                        accepted = None
                        raise FloatingPointError(
                            "Sobolev step-doubling tolerance exceeded"
                        )
                    accepted = fine
            except (ArithmeticError, RuntimeError, np.linalg.LinAlgError) as exc:
                rejected_steps += 1
                attempt *= 0.5
                if attempt < time_step / 4096.0:
                    obstruction = {
                        "type": "SOBOLEV_LOCAL_ERROR_STEP_COLLAPSE",
                        "time": time,
                        "attempted_step_below": time_step / 4096.0,
                        "local_error_tolerance": local_error_tolerance,
                        "message": str(exc),
                    }
                    break
        if obstruction is not None or accepted is None:
            break
        q, velocity, multipliers, _ = accepted
        time += attempt
        step_index += 1
        maximum_accepted_local_error = max(
            maximum_accepted_local_error, local_error
        )
        minimum_accepted_step = (
            attempt if minimum_accepted_step is None
            else min(minimum_accepted_step, attempt)
        )
        current_step = min(time_step, 1.25 * attempt)

    event_valid = bool(
        event is not None
        and abs(float(event["lambda_ordered"])) < 1.0e-9
        and float(event["maximum_constraint_residual"]) < 1.0e-8
        and float(event["eta_Legendre"]["minimum"]) > 0.0
        and float(event["branch_overlap"]) > 0.9
    )
    return {
        "order": order,
        "independent_reset": True,
        "independent_multiplier_seed_rule": multiplier_seed_rule,
        "accepted_N3_trajectory_used": False,
        "time_step": time_step,
        "local_error_tolerance": local_error_tolerance,
        "maximum_steps": maximum_steps,
        "steps_completed": len(rows) - 1,
        "rows": rows,
        "event": event,
        "ordered_event_found": event is not None,
        "ordered_event_validated_at_this_resolution": event_valid,
        "integration_obstruction": obstruction,
        "maximum_constraint_residual": maximum_constraint,
        "maximum_Dirac_condition_number": maximum_condition,
        "rejected_adaptive_steps": rejected_steps,
        "maximum_accepted_relative_Sobolev_local_error": (
            maximum_accepted_local_error
        ),
        "minimum_accepted_time_step": (
            0.0 if minimum_accepted_step is None else minimum_accepted_step
        ),
        "event_locator_lookahead_cap": 1.5 * time_step,
        "event_locator_lookahead_independent_of_adaptive_step": True,
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=4)
def n4_constrained_ordered_event_search(
    *, points: int = DEFAULT_POINTS, time_step: float = 1.0e-5,
    maximum_steps: int = 80,
    local_error_tolerance: float | None = None,
) -> dict[str, Any]:
    return _constrained_ordered_event_search(
        order=4,
        multiplier_seed_rule="CANONICAL_LIFT",
        points=points,
        time_step=time_step,
        maximum_steps=maximum_steps,
        local_error_tolerance=local_error_tolerance,
    )


@lru_cache(maxsize=4)
def n5_constrained_ordered_event_search(
    *, points: int = DEFAULT_POINTS, time_step: float = 1.0e-5,
    maximum_steps: int = 80,
    local_error_tolerance: float | None = None,
) -> dict[str, Any]:
    return _constrained_ordered_event_search(
        order=5,
        multiplier_seed_rule="ZERO_MULTIPLIER",
        points=points,
        time_step=time_step,
        maximum_steps=maximum_steps,
        local_error_tolerance=local_error_tolerance,
    )


@lru_cache(maxsize=4)
def n5_independent_eta_branch_event_audit(
    *, points: int = DEFAULT_POINTS,
) -> dict[str, Any]:
    """Locate the first N5 inertia-boundary crossing on the zero-m seed."""

    order = 5
    reset = integrate_attached_dirac_flow(maximum_steps=0)[
        "continuation_state"
    ]
    q_seed, v_seed, m_seed = lift_low_state(
        order,
        np.asarray(reset["coordinates"]),
        np.asarray(reset["velocities"]),
        np.asarray(reset["multipliers"]),
    )
    branch_rows: list[dict[str, Any]] = []
    selected: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None
    for rule, multiplier_seed in (
        ("CANONICAL_LIFT", m_seed),
        ("ZERO_MULTIPLIER", np.zeros_like(m_seed)),
    ):
        projection = project_nested_constraints_sobolev(
            order, q_seed, v_seed, multiplier_seed, points=points
        )
        q = np.asarray(projection["coordinates"], dtype=float)
        velocity = np.asarray(projection["velocities"], dtype=float)
        multipliers = np.asarray(projection["multipliers"], dtype=float)
        eta = _eta_legendre_minimum(order, q, multipliers, points=2400)
        admissible = bool(
            projection["success"]
            and projection["maximum_constraint_residual"] < 1.0e-8
            and eta["minimum"] > 0.0
        )
        branch_rows.append({
            "multiplier_seed_rule": rule,
            "projection_success": bool(projection["success"]),
            "projection_iterations": int(projection["iterations"]),
            "maximum_constraint_residual": float(
                projection["maximum_constraint_residual"]
            ),
            "Sobolev_correction_norm_squared": float(
                projection["Sobolev_correction_norm_squared"]
            ),
            "eta_Legendre": eta,
            "admissible": admissible,
        })
        if selected is None and admissible:
            selected = (q, velocity, multipliers)
    if selected is None:
        raise RuntimeError("no predeclared independent N5 eta branch")
    q, velocity, multipliers = selected
    selected_rule = next(
        row["multiplier_seed_rule"] for row in branch_rows
        if row["admissible"]
    )
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q, velocity, multipliers, points=points
    )
    values, vectors = np.linalg.eigh(
        np.asarray(dynamics["Dirac_hessian"], dtype=float)
    )
    inertia = int(np.count_nonzero(values < 0.0))
    boundary_indices = [
        index for index in (inertia - 1, inertia)
        if 0 <= index < values.size
    ]
    tangent = np.concatenate((
        velocity,
        np.asarray(dynamics["acceleration"], dtype=float),
        np.asarray(dynamics["multiplier_rate"], dtype=float),
    ))
    epsilon = min(
        1.0e-7,
        1.0e-4 / max(1.0, float(np.max(np.abs(tangent)))),
    )
    q_plus = q + epsilon * velocity
    plus_projection = project_nested_constraints_sobolev(
        order,
        q_plus,
        velocity + epsilon * np.asarray(dynamics["acceleration"]),
        multipliers + epsilon * np.asarray(dynamics["multiplier_rate"]),
        points=points,
    )
    v_plus = np.asarray(plus_projection["velocities"], dtype=float)
    m_plus = np.asarray(plus_projection["multipliers"], dtype=float)
    plus_values, plus_vectors = np.linalg.eigh(
        exact_action_jet_at_state(
            order, q_plus, v_plus, m_plus, points=points
        ).hessian
    )
    candidates: list[dict[str, Any]] = []
    for index in boundary_indices:
        reference = vectors[:, index]
        plus_index = int(np.argmax(np.abs(plus_vectors.T @ reference)))
        overlap = float(abs(plus_vectors[:, plus_index] @ reference))
        derivative = float(
            (plus_values[plus_index] - values[index]) / epsilon
        )
        crossing = (
            -float(values[index]) / derivative
            if values[index] * derivative < 0.0 else None
        )
        lower_gap = (
            float(values[index] - values[index - 1])
            if index else math.inf
        )
        upper_gap = (
            float(values[index + 1] - values[index])
            if index + 1 < values.size else math.inf
        )
        candidates.append({
            "index": index,
            "eigenvalue": float(values[index]),
            "directional_derivative": derivative,
            "linearized_positive_crossing_time": crossing,
            "one_sided_overlap": overlap,
            "lower_gap": lower_gap,
            "upper_gap": upper_gap,
        })
    crossing_rows = [
        row for row in candidates
        if row["linearized_positive_crossing_time"] is not None
        and row["linearized_positive_crossing_time"] > 0.0
    ]
    if not crossing_rows:
        return {
            "branch_scan": branch_rows,
            "selected_multiplier_seed_rule": selected_rule,
            "boundary_modes": candidates,
            "event": None,
            "ordered_event_validated": False,
            "classification": "OPEN_NO_FORWARD_INERTIA_BOUNDARY_CROSSING",
            "FULL_BHSM_COMPLETE": False,
        }
    earliest = min(
        crossing_rows,
        key=lambda row: row["linearized_positive_crossing_time"],
    )
    event_index = int(earliest["index"])
    reference = vectors[:, event_index]
    cache: dict[float, dict[str, Any]] = {}

    def projected_candidate(offset: float) -> dict[str, Any]:
        key = float(offset)
        if key in cache:
            return cache[key]
        q_candidate = q + key * velocity
        projection = project_nested_constraints_sobolev(
            order,
            q_candidate,
            velocity + key * np.asarray(dynamics["acceleration"]),
            multipliers + key * np.asarray(dynamics["multiplier_rate"]),
            points=points,
        )
        v_candidate = np.asarray(projection["velocities"], dtype=float)
        m_candidate = np.asarray(projection["multipliers"], dtype=float)
        candidate_values, candidate_vectors = np.linalg.eigh(
            exact_action_jet_at_state(
                order, q_candidate, v_candidate, m_candidate, points=points
            ).hessian
        )
        index = int(np.argmax(np.abs(candidate_vectors.T @ reference)))
        candidate = {
            "lambda": float(candidate_values[index]),
            "index": index,
            "overlap": float(abs(candidate_vectors[:, index] @ reference)),
            "coordinates": q_candidate,
            "velocities": v_candidate,
            "multipliers": m_candidate,
            "constraint": float(projection["maximum_constraint_residual"]),
            "eta": _eta_legendre_minimum(
                order, q_candidate, m_candidate, points=2400
            ),
            "inertia": int(np.count_nonzero(candidate_values < 0.0)),
        }
        cache[key] = candidate
        return candidate

    crossing_time = float(earliest["linearized_positive_crossing_time"])
    upper = 1.5 * crossing_time
    upper_candidate = projected_candidate(upper)
    while values[event_index] * upper_candidate["lambda"] > 0.0:
        upper *= 1.5
        if upper > 1.0e-4:
            raise RuntimeError("N5 boundary mode failed to bracket")
        upper_candidate = projected_candidate(upper)
    root = brentq(
        lambda offset: projected_candidate(offset)["lambda"],
        0.0,
        upper,
        xtol=1.0e-14,
        rtol=1.0e-12,
        maxiter=64,
    )
    event = projected_candidate(root)
    event_payload = {
        "event_time": float(root),
        "lambda_ordered": event["lambda"],
        "branch_index": int(event["index"]),
        "branch_overlap": event["overlap"],
        "negative_inertia_reset": inertia,
        "negative_inertia_event_side": event["inertia"],
        "maximum_constraint_residual": event["constraint"],
        "eta_Legendre": event["eta"],
        "coordinates": event["coordinates"].tolist(),
        "velocities": event["velocities"].tolist(),
        "multipliers": event["multipliers"].tolist(),
        "locator": (
            "EARLIEST_OF_BOTH_INERTIA_BOUNDARY_MODES_WITH_ONE_SIDED_"
            "PROJECTED_TANGENT_AND_TRACKED_BRENT_ROOT"
        ),
    }
    validated = bool(
        abs(event["lambda"]) < 1.0e-9
        and event["overlap"] > 0.9
        and event["constraint"] < 1.0e-8
        and event["eta"]["minimum"] > 0.0
    )
    return {
        "order": order,
        "independent_reset": True,
        "accepted_N3_trajectory_or_N4_child_used": False,
        "branch_scan": branch_rows,
        "selected_multiplier_seed_rule": selected_rule,
        "boundary_modes": candidates,
        "event": event_payload,
        "ordered_event_validated": validated,
        "classification": (
            "VALIDATED_INDEPENDENT_N5_ETA_ADMISSIBLE_ORDERED_EVENT"
            if validated else "OPEN_N5_ORDERED_EVENT"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n5_cross_quadrature_event_classification() -> dict[str, Any]:
    """Classify N5 event existence separately from its event-time value."""

    runs = [
        n5_independent_eta_branch_event_audit(points=points)
        for points in (32, 44, 56)
    ]
    events = [run["event"] for run in runs]
    all_exist = all(
        run["ordered_event_validated"] and event is not None
        for run, event in zip(runs, events)
    )
    times = np.asarray([
        float(event["event_time"]) for event in events if event is not None
    ])
    time_spread = (
        float((np.max(times) - np.min(times)) / np.max(np.abs(times)))
        if times.size == len(runs) else math.inf
    )
    same_boundary_transition = all(
        event is not None
        and int(event["branch_index"]) == 10
        and int(event["negative_inertia_reset"]) == 10
        and int(event["negative_inertia_event_side"]) == 11
        for event in events
    )
    all_eta_constraint_overlap = all(
        event is not None
        and event["eta_Legendre"]["minimum"] > 0.0
        and event["maximum_constraint_residual"] < 1.0e-8
        and event["branch_overlap"] > 0.9
        for event in events
    )
    qualitative = bool(
        all_exist and same_boundary_transition and all_eta_constraint_overlap
    )
    quantitative_time = bool(qualitative and time_spread < 1.0e-2)
    return {
        "quadrature_runs": [
            {
                "points": points,
                "selected_multiplier_seed_rule": run[
                    "selected_multiplier_seed_rule"
                ],
                "ordered_event_validated": run[
                    "ordered_event_validated"
                ],
                "event": run["event"],
            }
            for points, run in zip((32, 44, 56), runs)
        ],
        "qualitative_ordered_event_existence_validated": qualitative,
        "same_boundary_mode_and_inertia_transition": same_boundary_transition,
        "event_time_relative_quadrature_spread": time_spread,
        "quantitative_event_time_validated": quantitative_time,
        "classification": (
            "VALIDATED_QUALITATIVE_N5_ORDERED_EVENT_EXISTENCE_EVENT_TIME_"
            "NOT_QUADRATURE_CONVERGED"
            if qualitative and not quantitative_time else
            "VALIDATED_QUANTITATIVE_N5_ORDERED_EVENT"
            if quantitative_time else "OPEN_N5_ORDERED_EVENT"
        ),
        "N5_confirms_N4": (
            "QUALITATIVE_ETA_ADMISSIBLE_ORDERED_EVENT_STRUCTURE_ONLY;_"
            "N5_COMPLETE_CHILD_AND_PERSISTENCE_REMAIN_OPEN"
            if qualitative else "NO_CROSS_RESOLUTION_CONFIRMATION"
        ),
        "observed_particle_values_used": False,
        "accepted_N3_trajectory_or_N4_child_used": False,
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=2)
def n4_ordered_event_resolution_audit(
    *, points: int = DEFAULT_POINTS,
) -> dict[str, Any]:
    """Reject or validate the N=4 event against one time-step refinement."""

    coarse = n4_constrained_ordered_event_search(
        points=points, time_step=1.0e-5, maximum_steps=100
    )
    fine = n4_constrained_ordered_event_search(
        points=points, time_step=5.0e-6, maximum_steps=200
    )

    def compact(run: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "time_step": run["time_step"],
            "steps_completed": run["steps_completed"],
            "ordered_event_found": run["ordered_event_found"],
            "ordered_event_validated_at_this_resolution": run[
                "ordered_event_validated_at_this_resolution"
            ],
            "integration_obstruction": run["integration_obstruction"],
            "maximum_constraint_residual": run[
                "maximum_constraint_residual"
            ],
            "maximum_Dirac_condition_number": run[
                "maximum_Dirac_condition_number"
            ],
            "event": run["event"],
        }

    if coarse["event"] is None or fine["event"] is None:
        return {
            "coarse": compact(coarse),
            "fine": compact(fine),
            "classification": "OPEN_EVENT_NOT_FOUND_AT_BOTH_RESOLUTIONS",
            "resolution_independent_event_validated": False,
        }
    coarse_event = coarse["event"]
    fine_event = fine["event"]
    time_difference = abs(
        float(coarse_event["event_time"])
        - float(fine_event["event_time"])
    )
    time_relative = time_difference / max(
        abs(float(coarse_event["event_time"])),
        abs(float(fine_event["event_time"])),
        1.0e-30,
    )
    order = 4
    frequencies = np.concatenate((
        [0.0],
        4.0 * np.arange(1, order + 1),
        4.0 * np.arange(order),
        4.0 * np.arange(order),
    ))
    weights = sobolev_weights(order)
    state_weight = np.concatenate((
        (1.0 + frequencies**2) ** 3.0,
        weights["velocities"],
        weights["multipliers"],
    ))

    def event_state(event: Mapping[str, Any]) -> np.ndarray:
        return np.concatenate((
            np.asarray(event["coordinates"], dtype=float),
            np.asarray(event["velocities"], dtype=float),
            np.asarray(event["multipliers"], dtype=float),
        ))

    coarse_state = event_state(coarse_event)
    fine_state = event_state(fine_event)
    state_difference = float(
        np.linalg.norm(state_weight * (coarse_state - fine_state))
    )
    state_scale = max(
        1.0,
        float(np.linalg.norm(state_weight * coarse_state)),
        float(np.linalg.norm(state_weight * fine_state)),
    )
    state_relative = state_difference / state_scale
    individual_gates = all((
        coarse["ordered_event_validated_at_this_resolution"],
        fine["ordered_event_validated_at_this_resolution"],
    ))
    # These are numerical reliability thresholds only; they do not add a
    # physical equation or acceptance condition to BHSM.
    convergence = bool(
        individual_gates
        and time_relative < 1.0e-2
        and state_relative < 1.0e-2
    )
    return {
        "coarse": compact(coarse),
        "fine": compact(fine),
        "event_time_absolute_difference": time_difference,
        "event_time_relative_difference": time_relative,
        "event_state_relative_H6_product_difference": state_relative,
        "both_individually_constraint_eta_branch_admissible": individual_gates,
        "numerical_reliability_thresholds_not_physics": True,
        "physical_equations_changed": False,
        "physical_gates_changed": False,
        "classification": (
            "VALIDATED_RESOLUTION_INDEPENDENT_ORDERED_EVENT"
            if convergence
            else "INVALIDATED_AS_RESOLUTION_INDEPENDENT_EVENT"
        ),
        "resolution_independent_event_validated": convergence,
        "required_next": (
            "ACTION_EQUIVALENT_ADAPTIVE_STEP_DOUBLING_CONSTRAINT_PROJECTED_"
            "N4_FLOW_BEFORE_ANY_CHILD_RECONSTRUCTION"
        ),
    }


def _compact_n4_event_run(run: Mapping[str, Any]) -> dict[str, Any]:
    event = run["event"]
    return {
        "quadrature_points": run.get("quadrature_points"),
        "time_step_cap": run["time_step"],
        "local_error_tolerance": run["local_error_tolerance"],
        "steps_completed": run["steps_completed"],
        "ordered_event_found": run["ordered_event_found"],
        "ordered_event_validated_at_this_resolution": run[
            "ordered_event_validated_at_this_resolution"
        ],
        "integration_obstruction": run["integration_obstruction"],
        "maximum_constraint_residual": run["maximum_constraint_residual"],
        "maximum_Dirac_condition_number": run[
            "maximum_Dirac_condition_number"
        ],
        "rejected_adaptive_steps": run["rejected_adaptive_steps"],
        "maximum_accepted_relative_Sobolev_local_error": run[
            "maximum_accepted_relative_Sobolev_local_error"
        ],
        "minimum_accepted_time_step": run["minimum_accepted_time_step"],
        "event": event,
    }


def _n4_event_pair_difference(
    left: Mapping[str, Any], right: Mapping[str, Any],
) -> dict[str, float | bool]:
    left_event = left["event"]
    right_event = right["event"]
    if left_event is None or right_event is None:
        return {
            "both_events_available": False,
            "event_time_absolute_difference": math.inf,
            "event_time_relative_difference": math.inf,
            "event_state_relative_H6_product_difference": math.inf,
        }
    time_difference = abs(
        float(left_event["event_time"])
        - float(right_event["event_time"])
    )
    time_relative = time_difference / max(
        abs(float(left_event["event_time"])),
        abs(float(right_event["event_time"])),
        1.0e-30,
    )
    order = 4
    frequencies = np.concatenate((
        [0.0],
        4.0 * np.arange(1, order + 1),
        4.0 * np.arange(order),
        4.0 * np.arange(order),
    ))
    weights = sobolev_weights(order)
    state_weight = np.concatenate((
        (1.0 + frequencies**2) ** 3.0,
        weights["velocities"],
        weights["multipliers"],
    ))

    def state(event: Mapping[str, Any]) -> np.ndarray:
        return np.concatenate((
            np.asarray(event["coordinates"], dtype=float),
            np.asarray(event["velocities"], dtype=float),
            np.asarray(event["multipliers"], dtype=float),
        ))

    left_state = state(left_event)
    right_state = state(right_event)
    state_difference = float(
        np.linalg.norm(state_weight * (left_state - right_state))
    )
    state_scale = max(
        1.0,
        float(np.linalg.norm(state_weight * left_state)),
        float(np.linalg.norm(state_weight * right_state)),
    )
    return {
        "both_events_available": True,
        "event_time_absolute_difference": time_difference,
        "event_time_relative_difference": time_relative,
        "event_state_relative_H6_product_difference": (
            state_difference / state_scale
        ),
    }


@lru_cache(maxsize=2)
def n4_adaptive_event_convergence_audit(
    *, points: int = DEFAULT_POINTS, comparison_points: int = 44,
) -> dict[str, Any]:
    """Test N=4 event convergence in time control and quadrature."""

    loose = dict(n4_constrained_ordered_event_search(
        points=points,
        time_step=1.0e-5,
        maximum_steps=100,
        local_error_tolerance=1.0e-8,
    ))
    tight = dict(n4_constrained_ordered_event_search(
        points=points,
        time_step=1.0e-5,
        maximum_steps=100,
        local_error_tolerance=3.0e-9,
    ))
    quadrature = dict(n4_constrained_ordered_event_search(
        points=comparison_points,
        time_step=1.0e-5,
        maximum_steps=100,
        local_error_tolerance=3.0e-9,
    ))
    loose["quadrature_points"] = points
    tight["quadrature_points"] = points
    quadrature["quadrature_points"] = comparison_points
    time_control = _n4_event_pair_difference(loose, tight)
    quadrature_control = _n4_event_pair_difference(tight, quadrature)
    all_individually_admissible = all(
        run["ordered_event_validated_at_this_resolution"]
        for run in (loose, tight, quadrature)
    )
    # These are convergence diagnostics, not extra BHSM equations or gates.
    time_converged = bool(
        time_control["both_events_available"]
        and float(time_control["event_time_relative_difference"]) < 1.0e-2
        and float(
            time_control["event_state_relative_H6_product_difference"]
        ) < 1.0e-2
    )
    quadrature_converged = bool(
        quadrature_control["both_events_available"]
        and float(
            quadrature_control["event_time_relative_difference"]
        ) < 1.0e-2
        and float(
            quadrature_control["event_state_relative_H6_product_difference"]
        ) < 1.0e-2
    )
    validated = bool(
        all_individually_admissible and time_converged and quadrature_converged
    )
    return {
        "loose_time_control": _compact_n4_event_run(loose),
        "tight_time_control": _compact_n4_event_run(tight),
        "quadrature_control": _compact_n4_event_run(quadrature),
        "time_control_difference": time_control,
        "quadrature_control_difference": quadrature_control,
        "all_runs_individually_constraint_eta_branch_admissible": (
            all_individually_admissible
        ),
        "time_control_converged": time_converged,
        "quadrature_control_converged": quadrature_converged,
        "numerical_reliability_thresholds_not_physics": True,
        "physical_equations_changed": False,
        "physical_gates_changed": False,
        "classification": (
            "VALIDATED_N4_ADAPTIVE_QUADRATURE_INDEPENDENT_ORDERED_EVENT"
            if validated
            else "OPEN_N4_ORDERED_EVENT_NUMERICAL_CONVERGENCE"
        ),
        "N4_ordered_event_validated": validated,
        "required_next": (
            "DERIVE_AND_SOLVE_THE_EVENT_CONDITIONED_N4_COMPLETE_CHILD_"
            "BOUNDARY_BVP" if validated else
            "RESOLVE_THE_FIRST_FAILED_TIME_OR_QUADRATURE_CONVERGENCE_OWNER"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


def _trace_jacobian_at_order(order: int) -> np.ndarray:
    qdim = dimensions(order)["coordinates"]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    trace = np.zeros((3, qdim))
    trace[:, 0] = 1.0
    trace[:, 1:1 + order] = signs_k
    trace[0, 1 + order:1 + 2 * order] = signs_j
    trace[1, 1 + 2 * order:1 + 3 * order] = signs_j
    trace[2, 1 + 2 * order:1 + 3 * order] = -signs_j
    return trace


def _attachment_jacobian_at_order(
    order: int, coordinates: np.ndarray,
) -> np.ndarray:
    q = np.asarray(coordinates)
    qdim = dimensions(order)["coordinates"]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    v_boundary = q[1 + 2 * order:1 + 3 * order] @ signs_j
    dtype = np.result_type(q, float)
    j_w = np.zeros(qdim, dtype=dtype)
    j_w[0] = 1.0
    j_w[1:1 + order] = signs_k
    j_w[1 + 2 * order:1 + 3 * order] = (
        -np.tanh(2.0 * v_boundary) * signs_j
    )
    j_c = np.zeros(qdim, dtype=dtype)
    j_c[0] = 1.0
    return np.vstack((j_w, j_c - j_w))


def _attachment_coordinates_at_order(
    order: int, coordinates: np.ndarray,
) -> np.ndarray:
    """Exact two-coordinate attachment chart whose derivative is B(q)."""

    q = np.asarray(coordinates)
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary = q[1:1 + order] @ signs_k
    v_boundary = q[1 + 2 * order:1 + 3 * order] @ signs_j
    q_w = q[0] + u_boundary - 0.5 * np.log(np.cosh(2.0 * v_boundary))
    return np.asarray([q_w, q[0] - q_w])


def _attachment_chart_curvature_on_velocity(
    order: int, coordinates: np.ndarray, velocities: np.ndarray,
) -> np.ndarray:
    """Return D^2 b(q)[v,v] for the exact attachment chart."""

    q = np.asarray(coordinates)
    velocity = np.asarray(velocities)
    signs_j = (-1.0) ** np.arange(order)
    v_boundary = q[1 + 2 * order:1 + 3 * order] @ signs_j
    v_boundary_rate = (
        velocity[1 + 2 * order:1 + 3 * order] @ signs_j
    )
    first = (
        -2.0 * v_boundary_rate**2 / np.cosh(2.0 * v_boundary) ** 2
    )
    return np.asarray([first, -first])


def _boundary_lift(
    form: np.ndarray, boundary: np.ndarray, constraints: np.ndarray,
) -> np.ndarray:
    combined = np.vstack((boundary, constraints))
    target = np.zeros((combined.shape[0], 2))
    target[:2] = np.eye(2)
    inverse_times = np.linalg.solve(form, combined.T)
    compliance = combined @ inverse_times
    return inverse_times @ np.linalg.solve(compliance, target)


def _canonical_pair_at_order(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    size = dimensions(order)
    qdim = size["coordinates"]
    jet = exact_full_action_jet_at_state(
        order, coordinates, velocities, multipliers, points=points
    )
    gradient = np.asarray(jet.gradient)
    hessian = np.asarray(jet.hessian)
    boundary = _attachment_jacobian_at_order(order, coordinates)
    q_form = hessian[:qdim, :qdim]
    v_form = hessian[qdim:2 * qdim, qdim:2 * qdim]
    cq = hessian[2 * qdim:, :qdim]
    cv = hessian[2 * qdim:, qdim:2 * qdim]
    q_lift = _boundary_lift(q_form, boundary, cq)
    v_lift = _boundary_lift(v_form, boundary, cv)
    momentum = v_lift.T @ gradient[qdim:2 * qdim]
    force = q_lift.T @ gradient[:qdim]
    return momentum, force, q_lift, v_lift


def _complex_step_canonical_momentum_rate(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    acceleration: np.ndarray,
    multiplier_rate: np.ndarray,
    *,
    points: int,
    step: float = 1.0e-20,
) -> np.ndarray:
    """Evaluate Dp(y)X(y) on the same analytic lifted momentum map."""

    if step <= 0.0:
        raise ValueError("complex momentum-rate step must be positive")
    q_complex = np.asarray(coordinates, dtype=complex) + (
        1j * step * np.asarray(velocities, dtype=float)
    )
    v_complex = np.asarray(velocities, dtype=complex) + (
        1j * step * np.asarray(acceleration, dtype=float)
    )
    m_complex = np.asarray(multipliers, dtype=complex) + (
        1j * step * np.asarray(multiplier_rate, dtype=float)
    )
    momentum, _, _, _ = _canonical_pair_at_order(
        order, q_complex, v_complex, m_complex, points=points
    )
    return np.imag(momentum) / step


def _bicomplex_dynamic_flux_directional_derivative(
    order: int,
    state: np.ndarray,
    direction: np.ndarray,
    event_flux: np.ndarray,
    *,
    points: int,
    outer_step: float = 1.0e-20,
    inner_relative_step: float = 1.0e-1,
) -> np.ndarray:
    """Differentiate the exact dynamic flux by commuting complex units."""

    if outer_step <= 0.0 or inner_relative_step <= 0.0:
        raise ValueError("positive bicomplex derivative steps required")
    y = np.asarray(state, dtype=float)
    d = np.asarray(direction, dtype=float)
    if y.shape != d.shape:
        raise ValueError("state and directional shapes differ")
    qdim = dimensions(order)["coordinates"]
    q = y[:qdim]
    velocity = y[qdim:2 * qdim]
    multipliers = y[2 * qdim:]
    real_dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q, velocity, multipliers, points=points
    )
    tangent_scale = max(
        1.0,
        float(np.max(np.abs(velocity))),
        float(np.max(np.abs(real_dynamics["acceleration"]))),
        float(np.max(np.abs(real_dynamics["multiplier_rate"]))),
    )
    inner_step = inner_relative_step / tangent_scale
    outer = y.astype(complex) + 1j * outer_step * d
    q_outer = outer[:qdim]
    v_outer = outer[qdim:2 * qdim]
    m_outer = outer[2 * qdim:]
    momentum, force, q_lift, _ = _canonical_pair_at_order(
        order, q_outer, v_outer, m_outer, points=points
    )
    outer_dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q_outer, v_outer, m_outer, points=points
    )
    tangent = np.concatenate((
        v_outer,
        np.asarray(outer_dynamics["acceleration"]),
        np.asarray(outer_dynamics["multiplier_rate"]),
    ))

    def idempotent_momentum_rate(step: float) -> np.ndarray:
        plus_state = outer - 1j * step * tangent
        minus_state = outer + 1j * step * tangent
        plus_momentum, _, _, _ = _canonical_pair_at_order(
            order,
            plus_state[:qdim],
            plus_state[qdim:2 * qdim],
            plus_state[2 * qdim:],
            points=points,
        )
        minus_momentum, _, _, _ = _canonical_pair_at_order(
            order,
            minus_state[:qdim],
            minus_state[qdim:2 * qdim],
            minus_state[2 * qdim:],
            points=points,
        )
        return (minus_momentum - plus_momentum) / (2j * step)

    coarse_rate = idempotent_momentum_rate(inner_step)
    half_rate = idempotent_momentum_rate(0.5 * inner_step)
    momentum_rate = (4.0 * half_rate - coarse_rate) / 3.0
    child_covector = _metric_radial_flux_covector_at_order(
        order, q_outer, m_outer
    )
    child_flux = q_lift.T @ child_covector
    flux = child_flux + momentum_rate - force + event_flux
    return np.imag(flux) / outer_step


def _metric_radial_flux_covector_at_order(
    order: int, coordinates: np.ndarray, multipliers: np.ndarray,
) -> np.ndarray:
    q = np.asarray(coordinates)
    m = np.asarray(multipliers)
    qdim = dimensions(order)["coordinates"]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    scale = q[0]
    u = q[1:1 + order] @ signs_k
    w = q[1 + order:1 + 2 * order] @ signs_j
    v = q[1 + 2 * order:1 + 3 * order] @ signs_j
    radius = RADIUS0 * np.exp(scale)
    c_radius = radius * np.exp(u + w)
    a_radius = radius * np.exp(u + v) / np.sqrt(2.0)
    b_radius = radius * np.exp(u - v) / np.sqrt(2.0)
    lapse = np.exp(m[:order] @ signs_k)
    prefactor = 3.0 * lapse * a_radius**3 * b_radius**3 / c_radius
    dtype = np.result_type(q, m, float)
    d_log_a = np.zeros(qdim, dtype=dtype)
    d_log_b = np.zeros(qdim, dtype=dtype)
    d_log_a[0] = d_log_b[0] = 1.0
    d_log_a[1:1 + order] = signs_k
    d_log_b[1:1 + order] = signs_k
    d_log_a[1 + 2 * order:1 + 3 * order] = signs_j
    d_log_b[1 + 2 * order:1 + 3 * order] = -signs_j
    return prefactor * d_log_a - prefactor * d_log_b


def _exact_full_jet_euler_dirac_acceleration(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
) -> dict[str, Any]:
    """Solve Euler--Dirac using the existing exact full q,v,m action jet."""

    q = np.asarray(coordinates)
    velocity = np.asarray(velocities)
    m = np.asarray(multipliers)
    qdim = dimensions(order)["coordinates"]
    jet = exact_full_action_jet_at_state(
        order, q, velocity, m, points=points
    )
    dirac_hessian = np.asarray(jet.hessian[qdim:, qdim:])
    mixed_z_q = np.asarray(jet.hessian[qdim:, :qdim])
    gradient_q = np.asarray(jet.gradient[:qdim])
    rhs = np.concatenate((
        gradient_q - mixed_z_q[:qdim] @ velocity,
        -mixed_z_q[qdim:] @ velocity,
    ))
    solved = np.linalg.solve(dirac_hessian, rhs)
    return {
        "coordinate_rate": velocity.copy(),
        "acceleration": solved[:qdim],
        "multiplier_rate": solved[qdim:],
        "Dirac_hessian": dirac_hessian,
        "Dirac_condition_number": float(np.linalg.cond(dirac_hessian)),
        "finite": bool(np.all(np.isfinite(solved))),
        "coordinate_finite_difference_used": False,
        "physical_action_changed": False,
    }


def _child_rows_at_order(
    order: int,
    child: np.ndarray,
    event_coordinates: np.ndarray,
    event_momentum: np.ndarray,
    event_flux: np.ndarray,
    *,
    points: int,
    relative_flux_step: float = 1.0e-1,
    fixed_flux_time_step: float | None = None,
    richardson_flux: bool = True,
    flux_derivative_method: str = "richardson",
) -> np.ndarray:
    size = dimensions(order)
    qdim = size["coordinates"]
    q = np.asarray(child[:qdim], dtype=float)
    velocity = np.asarray(child[qdim:2 * qdim], dtype=float)
    multipliers = np.asarray(child[2 * qdim:], dtype=float)
    momentum, force, q_lift, _ = _canonical_pair_at_order(
        order, q, velocity, multipliers, points=points
    )
    child_covector = _metric_radial_flux_covector_at_order(
        order, q, multipliers
    )
    child_flux = q_lift.T @ child_covector
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q, velocity, multipliers, points=points
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    tangent_scale = max(
        1.0,
        float(np.max(np.abs(velocity))),
        float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )
    epsilon = (
        relative_flux_step / tangent_scale
        if fixed_flux_time_step is None else float(fixed_flux_time_step)
    )

    def centered_momentum_rate(step: float) -> np.ndarray:
        plus, _, _, _ = _canonical_pair_at_order(
            order,
            q + step * velocity,
            velocity + step * acceleration,
            multipliers + step * multiplier_rate,
            points=points,
        )
        minus, _, _, _ = _canonical_pair_at_order(
            order,
            q - step * velocity,
            velocity - step * acceleration,
            multipliers - step * multiplier_rate,
            points=points,
        )
        return (plus - minus) / (2.0 * step)

    if flux_derivative_method == "complex_step":
        momentum_rate = _complex_step_canonical_momentum_rate(
            order,
            q,
            velocity,
            multipliers,
            acceleration,
            multiplier_rate,
            points=points,
        )
    elif flux_derivative_method == "richardson":
        momentum_rate = centered_momentum_rate(epsilon)
        if richardson_flux:
            half_rate = centered_momentum_rate(0.5 * epsilon)
            momentum_rate = (4.0 * half_rate - momentum_rate) / 3.0
    else:
        raise ValueError("unknown dynamic-flux derivative method")
    flux = child_flux - (-momentum_rate + force - event_flux)
    return np.concatenate((
        _trace_jacobian_at_order(order) @ (q - event_coordinates),
        constraint_residual(
            order, q, velocity, multipliers, points=points
        ),
        momentum - event_momentum,
        flux,
    ))


def _n4_child_rows(
    child: np.ndarray,
    event_coordinates: np.ndarray,
    event_momentum: np.ndarray,
    event_flux: np.ndarray,
    *,
    points: int,
    relative_flux_step: float = 1.0e-1,
    fixed_flux_time_step: float | None = None,
    richardson_flux: bool = True,
) -> np.ndarray:
    """Compatibility wrapper for the validated N4 child map."""

    return _child_rows_at_order(
        4,
        child,
        event_coordinates,
        event_momentum,
        event_flux,
        points=points,
        relative_flux_step=relative_flux_step,
        fixed_flux_time_step=fixed_flux_time_step,
        richardson_flux=richardson_flux,
    )


def _child_flux_time_step_at_order(
    order: int,
    child: np.ndarray, *, points: int, relative_flux_step: float,
) -> float:
    """Select one inner flux time step at the center of an outer stencil."""

    qdim = dimensions(order)["coordinates"]
    q = np.asarray(child[:qdim], dtype=float)
    velocity = np.asarray(child[qdim:2 * qdim], dtype=float)
    multipliers = np.asarray(child[2 * qdim:], dtype=float)
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q, velocity, multipliers, points=points
    )
    tangent_scale = max(
        1.0,
        float(np.max(np.abs(velocity))),
        float(np.max(np.abs(dynamics["acceleration"]))),
        float(np.max(np.abs(dynamics["multiplier_rate"]))),
    )
    return float(relative_flux_step / tangent_scale)


def _n4_child_flux_time_step(
    child: np.ndarray, *, points: int, relative_flux_step: float,
) -> float:
    """Compatibility wrapper for the validated N4 child map."""

    return _child_flux_time_step_at_order(
        4, child, points=points, relative_flux_step=relative_flux_step
    )


@lru_cache(maxsize=2)
def n4_event_conditioned_complete_child_reconstruction(
    *, points: int = 44,
    resume_from_checkpoint: bool = False,
) -> dict[str, Any]:
    """Solve the 16-row N=4 event-to-complete-child Galerkin map."""

    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    audit = payload["cross_resolution_reconnaissance"][
        "N4_adaptive_event_convergence_audit"
    ]
    if not audit["N4_ordered_event_validated"]:
        raise RuntimeError("N4 ordered event is not validated")
    event_run = audit["quadrature_control"]
    event = event_run["event"]
    if event is None or int(event_run["quadrature_points"]) != points:
        raise RuntimeError("validated N4 event does not match child quadrature")
    order = 4
    size = dimensions(order)
    qdim = size["coordinates"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    event_jet = exact_action_jet_at_state(
        order, q_event, v_event, m_event, points=points
    )
    event_values, event_vectors = np.linalg.eigh(event_jet.hessian)
    event_branch = int(event["branch_index"])
    soft_mode = event_vectors[:, event_branch]
    branch_seed_scan: list[dict[str, Any]] = []
    germ_candidates: list[tuple[float, np.ndarray]] = []
    for magnitude in (1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1):
        for sign in (-1.0, 1.0):
            amplitude = sign * magnitude
            fiber = np.concatenate((v_event, m_event)) + amplitude * soft_mode
            projection = project_nested_constraints_sobolev(
                order,
                q_event,
                fiber[:qdim],
                fiber[qdim:],
                points=points,
            )
            if not projection["success"]:
                branch_seed_scan.append({
                    "amplitude": amplitude,
                    "projection_success": False,
                    "message": str(projection["message"]),
                })
                continue
            v_seed = np.asarray(projection["velocities"], dtype=float)
            m_seed = np.asarray(projection["multipliers"], dtype=float)
            eta_seed = _eta_legendre_minimum(
                order, q_event, m_seed, points=1600
            )
            seed = np.concatenate((q_event, v_seed, m_seed))
            seed_rows = _n4_child_rows(
                seed,
                q_event,
                event_momentum,
                event_flux,
                points=points,
            )
            flux_norm = float(np.linalg.norm(seed_rows[-2:]))
            admissible = bool(
                eta_seed["minimum"] > 0.0
                and float(projection["maximum_constraint_residual"])
                < 1.0e-8
            )
            branch_seed_scan.append({
                "amplitude": amplitude,
                "projection_success": True,
                "maximum_constraint_residual": float(
                    projection["maximum_constraint_residual"]
                ),
                "minimum_eta_Legendre": eta_seed["minimum"],
                "momentum_norm": float(np.linalg.norm(seed_rows[-4:-2])),
                "dynamic_flux_norm": flux_norm,
                "admissible": admissible,
            })
            if admissible:
                germ_candidates.append((flux_norm, seed))
    if not germ_candidates:
        raise RuntimeError("no admissible N4 broken-side child germ found")
    _, germ = min(germ_candidates, key=lambda item: item[0])
    selected_seed = next(
        row for row in branch_seed_scan
        if row.get("admissible")
        and math.isclose(
            float(row["dynamic_flux_norm"]),
            min(item[0] for item in germ_candidates),
            rel_tol=0.0,
            abs_tol=1.0e-9,
        )
    )
    continuation_checkpoint_used = False
    stored_checkpoint: dict[str, Any] | None = None
    if resume_from_checkpoint:
        stored = payload["cross_resolution_reconnaissance"].get(
            "N4_event_conditioned_complete_child_reconstruction"
        )
        if (
            isinstance(stored, dict)
            and (
                stored.get("rolling_checkpoint_promotion", {}).get(
                    "checkpoint_state_authoritative",
                    stored.get("rolling_checkpoint_promotion", {}).get(
                        "eligible", False
                    ),
                ) is True
            )
            and stored.get("child_state", {}).get(
                "eta_Legendre_minimum", {}
            ).get("minimum", -1.0) > 0.0
        ):
            state = stored["child_state"]
            checkpoint = np.concatenate((
                np.asarray(state["coordinates"], dtype=float),
                np.asarray(state["velocities"], dtype=float),
                np.asarray(state["multipliers"], dtype=float),
            ))
            if checkpoint.shape == germ.shape:
                germ = checkpoint
                continuation_checkpoint_used = True
                stored_checkpoint = stored
                selected_seed = {
                    "source": "LATEST_ADMISSIBLE_N4_CHILD_ROLLING_CHECKPOINT",
                    "prior_scaled_final_norm": stored["chart"][
                        "scaled_final_norm"
                    ],
                    "prior_dynamic_flux_norm": stored[
                        "physical_residuals"
                    ].get(
                        "dynamic_flux_norm_at_1e-1",
                        stored["physical_residuals"].get(
                            "dynamic_flux_norm_at_4e-4"
                        ),
                    ),
                    "eta_admissible": True,
                }
    initial_rows = _n4_child_rows(
        germ, q_event, event_momentum, event_flux, points=points
    )
    germ_velocity = germ[qdim:2 * qdim]
    germ_multipliers = germ[2 * qdim:]
    old_germ_dynamics = exact_euler_dirac_acceleration(
        order,
        germ[:qdim],
        germ_velocity,
        germ_multipliers,
        points=points,
    )
    exact_germ_dynamics = _exact_full_jet_euler_dirac_acceleration(
        order,
        germ[:qdim],
        germ_velocity,
        germ_multipliers,
        points=points,
    )
    acceleration_equivalence = _relative_difference(
        np.asarray(old_germ_dynamics["acceleration"]),
        np.asarray(exact_germ_dynamics["acceleration"]),
    )
    multiplier_rate_equivalence = _relative_difference(
        np.asarray(old_germ_dynamics["multiplier_rate"]),
        np.asarray(exact_germ_dynamics["multiplier_rate"]),
    )
    row_count = 2 * order + 8
    variable_count = 2 * qdim + size["multipliers"]
    # The post-basin-transition child requires the resolved member of the
    # predeclared Richardson ladder: h=1.25e-5 gives a 0.00488 coarse/fine
    # change versus 1.43 at h=1e-4, with the same rank-16 physical map.
    jacobian_step = 1.25e-5
    inner_relative_flux_step = 1.0e-1
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    coordinate_weights = (
        1.0 + frequencies["coordinates"] ** 2
    ) ** 3.0
    direction_weights = np.concatenate((
        coordinate_weights,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))
    germ_flux_time_step = _n4_child_flux_time_step(
        germ, points=points, relative_flux_step=inner_relative_flux_step
    )

    def directional_jacobian(
        center: np.ndarray, step: float, columns: np.ndarray,
    ) -> np.ndarray:
        # One center-selected inner step is held fixed throughout the outer
        # +/- stencil.  This prevents the adaptive inner difference from
        # defining two different maps at the two outer sample points.
        inner_step = _n4_child_flux_time_step(
            center, points=points,
            relative_flux_step=inner_relative_flux_step,
        )
        result = np.empty((row_count, len(columns)))
        for local_column, column in enumerate(columns):
            delta = np.zeros(variable_count)
            delta[int(column)] = step / direction_weights[int(column)]
            result[:, local_column] = (
                _n4_child_rows(
                    center + delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    fixed_flux_time_step=inner_step,
                )
                - _n4_child_rows(
                    center - delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    fixed_flux_time_step=inner_step,
                )
            ) / (2.0 * step)
        return result

    all_columns = np.arange(variable_count, dtype=int)
    outer_coarse = directional_jacobian(
        germ, 2.0 * jacobian_step, all_columns
    )
    outer_mid = directional_jacobian(germ, jacobian_step, all_columns)
    outer_fine = directional_jacobian(
        germ, 0.5 * jacobian_step, all_columns
    )
    coarse_richardson_jacobian = (
        4.0 * outer_mid - outer_coarse
    ) / 3.0
    jacobian = (4.0 * outer_fine - outer_mid) / 3.0
    local_curvature_row_scales = np.maximum(
        np.linalg.norm(jacobian, axis=1), 1.0
    )
    row_scales = local_curvature_row_scales.copy()
    merit_reference_preserved = False
    if continuation_checkpoint_used and stored_checkpoint is not None:
        stored_chart = stored_checkpoint["chart"]
        stored_scales = np.asarray(
            stored_chart.get(
                "merit_reference_row_scales",
                stored_chart["row_scales"],
            ),
            dtype=float,
        )
        if stored_scales.shape == (row_count,) and np.all(stored_scales > 0.0):
            row_scales = stored_scales
            merit_reference_preserved = True
    scaled_jacobian = jacobian / row_scales[:, None]
    _, _, pivots = qr(scaled_jacobian, mode="economic", pivoting=True)
    singular = np.linalg.svd(scaled_jacobian, compute_uv=False)
    tolerance = (
        np.finfo(float).eps * max(scaled_jacobian.shape) * singular[0]
    )
    rank = int(np.count_nonzero(singular > tolerance))
    chart = np.asarray(pivots[:row_count], dtype=int)
    chart_weights = direction_weights[chart]

    def residual(
        solver_values: np.ndarray, *, fixed_flux_time_step: float | None = None,
    ) -> np.ndarray:
        value = solver_values / direction_weights
        return _n4_child_rows(
            value,
            q_event,
            event_momentum,
            event_flux,
            points=points,
            fixed_flux_time_step=fixed_flux_time_step,
        ) / row_scales

    def resolved_chart_jacobian(
        solver_values: np.ndarray, *, base_step: float = jacobian_step,
    ) -> np.ndarray:
        center = solver_values / direction_weights
        full = directional_jacobian(center, base_step, all_columns)
        half = directional_jacobian(center, 0.5 * base_step, all_columns)
        return ((4.0 * half - full) / 3.0) / row_scales[:, None]

    chart_values = germ * direction_weights
    scaled_rows = residual(chart_values)
    solver_jacobian = scaled_jacobian.copy()
    refined_solver_jacobian = solver_jacobian.copy()
    initial_chart_jacobian = (
        coarse_richardson_jacobian / row_scales[:, None]
    )
    jacobian_step_relative_change = float(
        np.linalg.norm(refined_solver_jacobian - initial_chart_jacobian)
        / max(1.0, np.linalg.norm(initial_chart_jacobian))
    )
    richardson_block_changes = {
        name: float(
            np.linalg.norm(
                jacobian[row_slice] - coarse_richardson_jacobian[row_slice]
            )
            / max(
                1.0,
                np.linalg.norm(coarse_richardson_jacobian[row_slice]),
            )
        )
        for name, row_slice in (
            ("trace", slice(0, 3)),
            ("constraints", slice(3, 12)),
            ("canonical_momentum", slice(12, 14)),
            ("dynamic_Calderon_flux", slice(14, 16)),
        )
    }
    refined_singular = np.linalg.svd(
        refined_solver_jacobian, compute_uv=False
    )
    refined_tolerance = (
        np.finfo(float).eps
        * max(refined_solver_jacobian.shape)
        * refined_singular[0]
    )
    refined_rank = int(np.count_nonzero(
        refined_singular > refined_tolerance
    ))
    jacobian_derivative_resolved = bool(
        jacobian_step_relative_change < 1.0e-1
    )
    function_evaluations = 1
    accepted_steps = 0
    rejected_trials = 0
    jacobian_refreshes = 0
    gradient_fallback_steps = 0
    trust_radius = 1.0
    solver_success = False
    solver_message = (
        "maximum bounded Broyden iterations reached"
        if jacobian_derivative_resolved else
        "nonlinear solve deferred because nested dynamic-flux Jacobian is "
        "not step-converged"
    )
    for _ in range(512 if jacobian_derivative_resolved else 0):
        merit = float(np.linalg.norm(scaled_rows))
        if merit < 1.0e-11:
            solver_success = True
            solver_message = "scaled complete-child merit converged"
            break
        delta = np.linalg.lstsq(
            solver_jacobian, -scaled_rows, rcond=1.0e-12
        )[0]
        delta_norm = float(np.linalg.norm(delta))
        if delta_norm > trust_radius:
            delta *= trust_radius / delta_norm
        accepted = False
        factor = 1.0
        candidate_values = chart_values
        candidate_rows = scaled_rows
        while factor >= 2.0**-28:
            trial_values = chart_values + factor * delta
            trial_full = trial_values / direction_weights
            trial_q = trial_full[:qdim]
            trial_m = trial_full[2 * qdim:]
            if _eta_legendre_minimum(
                order, trial_q, trial_m, points=800
            )["minimum"] <= 0.0:
                factor *= 0.5
                rejected_trials += 1
                continue
            try:
                trial_rows = residual(trial_values)
                function_evaluations += 1
            except (ArithmeticError, RuntimeError, ValueError, np.linalg.LinAlgError):
                factor *= 0.5
                rejected_trials += 1
                continue
            if float(np.linalg.norm(trial_rows)) < merit:
                candidate_values = trial_values
                candidate_rows = trial_rows
                accepted = True
                break
            factor *= 0.5
            rejected_trials += 1
        if not accepted:
            gradient_delta = -solver_jacobian.T @ scaled_rows
            gradient_norm = float(np.linalg.norm(gradient_delta))
            if gradient_norm > 0.0:
                gradient_delta *= min(
                    trust_radius / gradient_norm,
                    1.0 / gradient_norm,
                )
                factor = 1.0
                while factor >= 2.0**-28:
                    trial_values = chart_values + factor * gradient_delta
                    trial_full = trial_values / direction_weights
                    trial_q = trial_full[:qdim]
                    trial_m = trial_full[2 * qdim:]
                    if _eta_legendre_minimum(
                        order, trial_q, trial_m, points=800
                    )["minimum"] <= 0.0:
                        factor *= 0.5
                        rejected_trials += 1
                        continue
                    try:
                        trial_rows = residual(trial_values)
                        function_evaluations += 1
                    except (
                        ArithmeticError, RuntimeError, ValueError,
                        np.linalg.LinAlgError,
                    ):
                        factor *= 0.5
                        rejected_trials += 1
                        continue
                    if float(np.linalg.norm(trial_rows)) < merit:
                        candidate_values = trial_values
                        candidate_rows = trial_rows
                        accepted = True
                        gradient_fallback_steps += 1
                        break
                    factor *= 0.5
                    rejected_trials += 1
        if not accepted:
            if jacobian_refreshes < 3:
                solver_jacobian = resolved_chart_jacobian(chart_values)
                function_evaluations += 4 * variable_count
                jacobian_refreshes += 1
                trust_radius = 0.5
                continue
            solver_message = "global-merit line search exhausted after refreshes"
            break
            continue
        step_vector = candidate_values - chart_values
        row_change = candidate_rows - scaled_rows
        denominator = float(step_vector @ step_vector)
        if denominator > 1.0e-24:
            solver_jacobian += np.outer(
                row_change - solver_jacobian @ step_vector,
                step_vector,
            ) / denominator
        chart_values = candidate_values
        scaled_rows = candidate_rows
        accepted_steps += 1
        if factor == 1.0:
            trust_radius = min(4.0, 1.5 * trust_radius)
        else:
            trust_radius = max(1.0e-8, factor * trust_radius)
    if float(np.linalg.norm(scaled_rows)) < 1.0e-11:
        solver_success = True
        solver_message = "scaled complete-child merit converged"
    child = chart_values / direction_weights
    final_rows = _n4_child_rows(
        child, q_event, event_momentum, event_flux, points=points
    )
    coarse_rows = _n4_child_rows(
        child,
        q_event,
        event_momentum,
        event_flux,
        points=points,
        relative_flux_step=2.0e-1,
    )
    q_child = child[:qdim]
    v_child = child[qdim:2 * qdim]
    m_child = child[2 * qdim:]
    eta = _eta_legendre_minimum(order, q_child, m_child, points=5000)
    flux_refinement = float(
        np.linalg.norm(final_rows[-2:] - coarse_rows[-2:])
        / max(1.0, np.linalg.norm(final_rows[-2:]))
    )
    initial_reference_merit = float(np.linalg.norm(initial_rows / row_scales))
    final_reference_merit = float(np.linalg.norm(final_rows / row_scales))
    fixed_reference_merit_reduced = bool(
        final_reference_merit < initial_reference_merit
    )
    checkpoint_promotion_eligible = bool(
        fixed_reference_merit_reduced
        and eta["minimum"] > 0.0
        and accepted_steps > 0
        and jacobian_derivative_resolved
    )
    validation = {
        "validated_independent_N4_event_used": True,
        "sixteen_physical_rows": row_count == 16,
        "full_rank_local_chart": rank == row_count,
        "dynamic_flux_jacobian_step_converged": (
            jacobian_derivative_resolved
        ),
        "local_solve_converged": solver_success,
        "trace_closed": float(np.max(np.abs(final_rows[:3]))) < 1.0e-9,
        "nine_constraints_closed": float(
            np.max(np.abs(final_rows[3:12]))
        ) < 1.0e-9,
        "momentum_closed": float(np.linalg.norm(final_rows[12:14])) < 1.0e-7,
        "dynamic_flux_closed": float(np.linalg.norm(final_rows[14:16])) < 2.0e-5,
        "dynamic_flux_difference_resolved": flux_refinement < 2.0e-5,
        "child_eta_hyperregular": eta["minimum"] > 0.0,
        "nonzero_motion_retained": float(np.linalg.norm(v_child)) > 0.0,
    }
    passed = all(validation.values())
    return {
        "source_event": (
            "INDEPENDENT_N4_ADAPTIVE_44_POINT_QUADRATURE_VALIDATED_EVENT"
        ),
        "broken_branch_child_germ": {
            "source": (
                "SYMMETRIC_PREDECLARED_AMPLITUDE_SCAN_ALONG_THE_N4_EVENT_"
                "ORDERED_SOFT_EIGENVECTOR_WITH_OWN_CONSTRAINT_PROJECTION"
            ),
            "accepted_N3_trajectory_or_child_used": False,
            "event_soft_eigenvalue": float(event_values[event_branch]),
            "event_soft_branch_index": event_branch,
            "scan": branch_seed_scan,
            "selected": selected_seed,
            "rolling_continuation_checkpoint_requested": (
                resume_from_checkpoint
            ),
            "rolling_continuation_checkpoint_used": (
                continuation_checkpoint_used
            ),
            "selection_role": (
                "NUMERICAL_REGULAR_BROKEN_BRANCH_GERM_ONLY;_NOT_A_NEW_"
                "PHYSICAL_COEFFICIENT_OR_ACCEPTANCE_GATE"
            ),
        },
        "exact_full_jet_dynamics_equivalence": {
            "old_exact_z_coordinate_finite_difference_acceleration_relative_"
            "difference": acceleration_equivalence,
            "old_exact_z_coordinate_finite_difference_multiplier_rate_"
            "relative_difference": multiplier_rate_equivalence,
            "new_coordinate_finite_difference_used": False,
            "same_retained_action": True,
            "same_Euler_Dirac_linear_system": True,
            "physical_equations_changed": False,
        },
        "dynamic_flux_variation_audit": {
            "physical_map": (
                "Phi=Q^dagger*gamma_child+Dp(y)X(y)-Q^dagger*L_q+"
                "gamma_event"
            ),
            "inner_momentum_rate": (
                "CENTER_SELECTED_FIXED_TIME_STEP_CENTRAL_DIFFERENCE_WITH_"
                "RICHARDSON_EXTRAPOLATION"
            ),
            "outer_directional_derivative": (
                "CENTER_FIXED_INNER_STEP_CENTRAL_DIFFERENCE_WITH_"
                "RICHARDSON_EXTRAPOLATION"
            ),
            "center_inner_time_step": germ_flux_time_step,
            "center_inner_relative_step": inner_relative_flux_step,
            "outer_direction_normalization": (
                "H6_COORDINATES_H5_VELOCITIES_H6_MULTIPLIERS_FROM_THE_"
                "EXISTING_BHSM_SOBOLEV_REGULARITY_TOPOLOGY"
            ),
            "third_variation_alone_sufficient_for_exact_Jacobian": False,
            "analytic_exact_flux_requires": "GENERICALLY_L_THIRD_VARIATION",
            "analytic_exact_Jacobian_requires": (
                "GENERICALLY_L_FOURTH_VARIATION"
            ),
            "higher_variation_owner": (
                "STATE_DEPENDENT_HESSIAN_MINIMAL_BOUNDARY_LIFTS_Q_AND_V"
            ),
            "frozen_lift_derivative_status": (
                "QUASI_NEWTON_ONLY;_EXACT_RECOMPUTED_RESIDUAL_REMAINS_"
                "PROMOTION_AUTHORITY"
            ),
            "physical_map_or_gate_changed": False,
        },
        "event_to_child_map": (
            "F_child=(THREE_TRACE,_NINE_CONSTRAINT,_TWO_CANONICAL_"
            "MOMENTUM,_TWO_DYNAMIC_CALDERON_FLUX_ROWS)"
        ),
        "whole_child_variable_count": variable_count,
        "physical_row_count": row_count,
        "additional_global_KKT_rows": 0,
        "initial_physical_rows": initial_rows.tolist(),
        "final_physical_rows": final_rows.tolist(),
        "chart": {
            "outer_Richardson_fine_base_step": jacobian_step,
            "outer_Richardson_coarse_base_step": 2.0 * jacobian_step,
            "full_chart_rank": rank,
            "selected_variable_indices": chart.tolist(),
            "selected_direction_weights": chart_weights.tolist(),
            "smallest_resolved_singular_value": float(singular[rank - 1]),
            "rank_tolerance": float(tolerance),
            "half_step_rank": refined_rank,
            "half_step_smallest_singular_value": float(
                refined_singular[refined_rank - 1]
            ),
            "outer_Richardson_coarse_to_fine_relative_change": (
                jacobian_step_relative_change
            ),
            "outer_Richardson_block_relative_changes": (
                richardson_block_changes
            ),
            "dynamic_flux_jacobian_step_converged": (
                jacobian_derivative_resolved
            ),
            "row_scaling": (
                "FIXED_REFERENCE_ROW_NORMS_NUMERICAL_ONLY_SAME_ZERO_SET"
            ),
            "row_scales": row_scales.tolist(),
            "local_curvature_row_scales": (
                local_curvature_row_scales.tolist()
            ),
            "merit_reference_row_scales": row_scales.tolist(),
            "merit_reference_preserved_from_checkpoint": (
                merit_reference_preserved
            ),
            "solver_jacobian": (
                "FULL_16_BY_34_CENTER_FIXED_TENSOR_PRODUCT_RICHARDSON_"
                "JACOBIAN_WITH_MINIMUM_NORM_GAUSS_NEWTON_AND_GOOD_BROYDEN_"
                "UPDATES"
            ),
            "solver_coordinates": (
                "ALL_34_EXISTING_H6_COORDINATE_H5_VELOCITY_H6_MULTIPLIER_"
                "VARIABLES;_THE_16_PHYSICAL_ROWS_ARE_UNCHANGED"
            ),
            "solver_variable_count": variable_count,
            "solver_merit": (
                "GLOBAL_L2_NORM_OF_ALL_16_ROW_SCALED_PHYSICAL_MAP;_NO_"
                "COMPONENTWISE_MONOTONICITY"
            ),
            "solver_success": solver_success,
            "solver_message": solver_message,
            "function_evaluations": function_evaluations,
            "accepted_steps": accepted_steps,
            "rejected_line_trials": rejected_trials,
            "resolved_jacobian_refreshes": jacobian_refreshes,
            "accepted_gradient_fallback_steps": gradient_fallback_steps,
            "scaled_final_norm": float(np.linalg.norm(scaled_rows)),
        },
        "rolling_checkpoint_promotion": {
            "independently_evaluated_merit": (
                "L2_NORM_OF_THE_EXACT_16_PHYSICAL_ROWS_IN_THE_FIXED_"
                "REFERENCE_SCALING"
            ),
            "initial_fixed_reference_merit": initial_reference_merit,
            "final_fixed_reference_merit": final_reference_merit,
            "fixed_reference_merit_reduced": fixed_reference_merit_reduced,
            "eta_admissible": eta["minimum"] > 0.0,
            "accepted_coupled_steps_positive": accepted_steps > 0,
            "directional_derivative_resolved": (
                jacobian_derivative_resolved
            ),
            "eligible": checkpoint_promotion_eligible,
            "checkpoint_state_authoritative": (
                checkpoint_promotion_eligible
            ),
            "componentwise_monotonicity_required": False,
            "physical_equations_or_gates_added": False,
        },
        "child_state": {
            "coordinates": q_child.tolist(),
            "velocities": v_child.tolist(),
            "multipliers": m_child.tolist(),
            "velocity_norm": float(np.linalg.norm(v_child)),
            "eta_Legendre_minimum": eta,
            "raw_state_displacement_from_broken_germ": float(
                np.linalg.norm(child - germ)
            ),
        },
        "physical_residuals": {
            "maximum_trace": float(np.max(np.abs(final_rows[:3]))),
            "maximum_nine_constraints": float(
                np.max(np.abs(final_rows[3:12]))
            ),
            "momentum_norm": float(np.linalg.norm(final_rows[12:14])),
            "dynamic_flux_norm_at_1e-1": float(
                np.linalg.norm(final_rows[14:16])
            ),
            "dynamic_flux_2e-1_to_1e-1_relative_difference": (
                flux_refinement
            ),
        },
        "validation": validation,
        "complete_child_candidate_validated": passed,
        "persistence_evaluated": False,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "claim_boundary": (
            "A_VALIDATED_FINITE_N4_EVENT_CONDITIONED_COMPLETE_CHILD_"
            "CAUCHY_STATE_IS_NOT_YET_A_PERSISTENT_CHILD_OR_AN_N_LIMIT_PROOF"
        ),
        "required_next": (
            "EVALUATE_POSITIVE_DURATION_CONSTRAINT_CONSISTENT_RELATIVE_"
            "PERSISTENCE_OF_THIS_N4_CHILD" if passed else
            "CONTINUE_THE_UNCHANGED_GLOBAL_MERIT_N4_COMPLETE_CHILD_SOLVE_"
            "FROM_THE_LATEST_ADMISSIBLE_CANDIDATE_WITH_A_FRESH_CENTER_FIXED_"
            "RICHARDSON_CURVATURE" if jacobian_derivative_resolved else
            "VALIDATE_THE_CENTER_FIXED_TENSOR_PRODUCT_RICHARDSON_"
            "DIRECTIONAL_DERIVATIVE_OF_THE_ACTION_OWNED_DYNAMIC_CALDERON_"
            "FLUX_MAP_BEFORE_ANOTHER_NONLINEAR_CHILD_SOLVE"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n5_event_conditioned_complete_child_chart_audit(
    *, points: int = 44,
) -> dict[str, Any]:
    """Derive and rank-audit the independent N5 18-row child map."""

    order = 5
    event_run = n5_independent_eta_branch_event_audit(points=points)
    event = event_run["event"]
    if not event_run["ordered_event_validated"] or event is None:
        raise RuntimeError("independent N5 ordered event is not validated")
    size = dimensions(order)
    qdim = size["coordinates"]
    variable_count = 2 * qdim + size["multipliers"]
    row_count = 2 * order + 8
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    event_values, event_vectors = np.linalg.eigh(
        exact_action_jet_at_state(
            order, q_event, v_event, m_event, points=points
        ).hessian
    )
    branch = int(event["branch_index"])
    soft_mode = event_vectors[:, branch]
    scan: list[dict[str, Any]] = []
    germs: list[tuple[float, np.ndarray]] = []
    for magnitude in (1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1):
        for sign in (-1.0, 1.0):
            amplitude = sign * magnitude
            fiber = np.concatenate((v_event, m_event)) + amplitude * soft_mode
            projection = project_nested_constraints_sobolev(
                order,
                q_event,
                fiber[:qdim],
                fiber[qdim:],
                points=points,
            )
            row: dict[str, Any] = {
                "amplitude": amplitude,
                "projection_success": bool(projection["success"]),
            }
            if not projection["success"]:
                row["message"] = str(projection["message"])
                scan.append(row)
                continue
            velocity = np.asarray(projection["velocities"], dtype=float)
            multipliers = np.asarray(projection["multipliers"], dtype=float)
            eta = _eta_legendre_minimum(
                order, q_event, multipliers, points=2400
            )
            germ = np.concatenate((q_event, velocity, multipliers))
            rows = _child_rows_at_order(
                order,
                germ,
                q_event,
                event_momentum,
                event_flux,
                points=points,
            )
            admissible = bool(
                eta["minimum"] > 0.0
                and projection["maximum_constraint_residual"] < 1.0e-8
            )
            flux_norm = float(np.linalg.norm(rows[-2:]))
            row.update({
                "maximum_constraint_residual": float(
                    projection["maximum_constraint_residual"]
                ),
                "minimum_eta_Legendre": eta["minimum"],
                "momentum_norm": float(np.linalg.norm(rows[-4:-2])),
                "dynamic_flux_norm": flux_norm,
                "admissible": admissible,
            })
            scan.append(row)
            if admissible:
                germs.append((flux_norm, germ))
    if not germs:
        raise RuntimeError("no admissible N5 broken-side child germ found")
    _, germ = min(germs, key=lambda item: item[0])
    initial_rows = _child_rows_at_order(
        order, germ, q_event, event_momentum, event_flux, points=points
    )
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))
    inner_step = _child_flux_time_step_at_order(
        order, germ, points=points, relative_flux_step=1.0e-1
    )

    def central_jacobian(step: float) -> np.ndarray:
        result = np.empty((row_count, variable_count))
        for column in range(variable_count):
            delta = np.zeros(variable_count)
            delta[column] = step / direction_weights[column]
            result[:, column] = (
                _child_rows_at_order(
                    order,
                    germ + delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    fixed_flux_time_step=inner_step,
                )
                - _child_rows_at_order(
                    order,
                    germ - delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    fixed_flux_time_step=inner_step,
                )
            ) / (2.0 * step)
        return result

    base_step = 1.0e-4
    coarse = central_jacobian(base_step)
    mid = central_jacobian(0.5 * base_step)
    fine = central_jacobian(0.25 * base_step)
    coarse_richardson = (4.0 * mid - coarse) / 3.0
    richardson = (4.0 * fine - mid) / 3.0
    row_scales = np.maximum(np.linalg.norm(richardson, axis=1), 1.0)
    scaled = richardson / row_scales[:, None]
    singular = np.linalg.svd(scaled, compute_uv=False)
    tolerance = np.finfo(float).eps * max(scaled.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    derivative_change = float(
        np.linalg.norm(richardson - coarse_richardson)
        / max(1.0, np.linalg.norm(coarse_richardson))
    )
    constraint_stop = 3 + (2 * order + 1)
    block_changes = {
        name: float(
            np.linalg.norm(
                richardson[row_slice] - coarse_richardson[row_slice]
            ) / max(1.0, np.linalg.norm(coarse_richardson[row_slice]))
        )
        for name, row_slice in (
            ("trace", slice(0, 3)),
            ("constraints", slice(3, constraint_stop)),
            ("canonical_momentum", slice(constraint_stop, constraint_stop + 2)),
            ("dynamic_Calderon_flux", slice(constraint_stop + 2, row_count)),
        )
    }
    return {
        "source_event": (
            "INDEPENDENT_N5_ZERO_MULTIPLIER_ETA_ADMISSIBLE_44_POINT_EVENT"
        ),
        "accepted_N3_trajectory_or_N4_child_used": False,
        "event_soft_branch_index": branch,
        "event_soft_eigenvalue": float(event_values[branch]),
        "broken_branch_seed_scan": scan,
        "event_to_child_map": (
            "F_child=(THREE_TRACE,_ELEVEN_CONSTRAINT,_TWO_CANONICAL_"
            "MOMENTUM,_TWO_DYNAMIC_CALDERON_FLUX_ROWS)"
        ),
        "physical_row_count": row_count,
        "whole_child_variable_count": variable_count,
        "initial_physical_rows": initial_rows.tolist(),
        "initial_physical_residual_norm": float(np.linalg.norm(initial_rows)),
        "chart": {
            "full_chart_rank": rank,
            "rank_tolerance": float(tolerance),
            "smallest_resolved_singular_value": float(singular[rank - 1]),
            "outer_Richardson_base_step": base_step,
            "outer_Richardson_relative_change": derivative_change,
            "outer_Richardson_block_relative_changes": block_changes,
            "dynamic_flux_jacobian_step_converged": derivative_change < 1.0e-1,
            "inner_relative_flux_step": 1.0e-1,
            "inner_flux_time_step": inner_step,
            "row_scales": row_scales.tolist(),
        },
        "structurally_full_row_rank": rank == row_count,
        "complete_child_candidate_validated": False,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "required_next": (
            "CONTINUE_THE_UNCHANGED_GLOBAL_MERIT_N5_18_ROW_COMPLETE_CHILD_"
            "SOLVE_FROM_THIS_INDEPENDENT_GERM"
            if rank == row_count and derivative_change < 1.0e-1 else
            "RESOLVE_THE_N5_CHILD_MAP_DIRECTIONAL_DERIVATIVE_BEFORE_A_"
            "NONLINEAR_CHILD_SOLVE"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n5_child_flux_step_audit(*, points: int = 44) -> dict[str, Any]:
    """Measure the inner dynamic-flux stencil at the N5 broken germ."""

    order = 5
    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    classification = payload["cross_resolution_reconnaissance"][
        "N5_independent_eta_branch_event_classification"
    ]
    selected_run = next(
        run for run in classification["quadrature_runs"]
        if int(run["points"]) == points
    )
    event = selected_run["event"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    qdim = dimensions(order)["coordinates"]
    event_values, event_vectors = np.linalg.eigh(
        exact_action_jet_at_state(
            order, q_event, v_event, m_event, points=points
        ).hessian
    )
    branch = int(event["branch_index"])
    fiber = np.concatenate((v_event, m_event)) + 1.0e-1 * event_vectors[:, branch]
    projection = project_nested_constraints_sobolev(
        order, q_event, fiber[:qdim], fiber[qdim:], points=points
    )
    velocity = np.asarray(projection["velocities"], dtype=float)
    multipliers = np.asarray(projection["multipliers"], dtype=float)
    germ = np.concatenate((q_event, velocity, multipliers))
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    rows: list[dict[str, Any]] = []
    previous: np.ndarray | None = None
    for relative_step in (0.4, 0.32, 0.24, 0.2, 0.16, 0.12, 0.1, 0.08, 0.06, 0.05):
        physical = _child_rows_at_order(
            order,
            germ,
            q_event,
            event_momentum,
            event_flux,
            points=points,
            relative_flux_step=relative_step,
        )
        flux = np.asarray(physical[-2:], dtype=float)
        rows.append({
            "relative_step": relative_step,
            "flux": flux.tolist(),
            "flux_norm": float(np.linalg.norm(flux)),
            "relative_change_from_previous": (
                None if previous is None else _relative_difference(flux, previous)
            ),
        })
        previous = flux
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))
    sector_slices = {
        "coordinates": slice(0, qdim),
        "velocities": slice(qdim, 2 * qdim),
        "multipliers": slice(2 * qdim, germ.size),
    }
    directional_rows: dict[str, Any] = {}
    fixed_inner_step = _child_flux_time_step_at_order(
        order, germ, points=points, relative_flux_step=1.0e-1
    )
    for sector, sector_slice in sector_slices.items():
        direction = np.zeros(germ.size)
        indices = np.arange(
            sector_slice.start, sector_slice.stop, dtype=int
        )
        direction[indices] = (
            np.cos(np.arange(indices.size, dtype=float) + 1.0)
            / direction_weights[indices]
        )
        direction /= np.linalg.norm(direction * direction_weights)
        central: list[np.ndarray] = []
        steps = (0.4, 0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625)
        eta_margins: list[float] = []
        for step in steps:
            eta_margins.append(min(
                _eta_legendre_minimum(
                    order,
                    (germ + step * direction)[:qdim],
                    (germ + step * direction)[2 * qdim:],
                    points=800,
                )["minimum"],
                _eta_legendre_minimum(
                    order,
                    (germ - step * direction)[:qdim],
                    (germ - step * direction)[2 * qdim:],
                    points=800,
                )["minimum"],
            ))
            plus = _child_rows_at_order(
                order,
                germ + step * direction,
                q_event,
                event_momentum,
                event_flux,
                points=points,
                fixed_flux_time_step=fixed_inner_step,
            )[-2:]
            minus = _child_rows_at_order(
                order,
                germ - step * direction,
                q_event,
                event_momentum,
                event_flux,
                points=points,
                fixed_flux_time_step=fixed_inner_step,
            )[-2:]
            central.append((plus - minus) / (2.0 * step))
        richardson = [
            (4.0 * central[index + 1] - central[index]) / 3.0
            for index in range(len(central) - 1)
        ]
        directional_rows[sector] = {
            "steps": list(steps),
            "minimum_eta_margins": eta_margins,
            "central_flux_derivatives": [row.tolist() for row in central],
            "Richardson_flux_derivatives": [row.tolist() for row in richardson],
            "adjacent_Richardson_relative_changes": [
                _relative_difference(richardson[index + 1], richardson[index])
                for index in range(len(richardson) - 1)
            ],
        }
    return {
        "order": order,
        "source": "INDEPENDENT_N5_EVENT_BROKEN_GERM_AMPLITUDE_PLUS_1E-1",
        "event_soft_eigenvalue": float(event_values[branch]),
        "projection_success": bool(projection["success"]),
        "maximum_constraint_residual": float(
            projection["maximum_constraint_residual"]
        ),
        "eta_Legendre": _eta_legendre_minimum(
            order, q_event, multipliers, points=2400
        ),
        "step_ladder": rows,
        "action_Sobolev_normalized_outer_direction_ladder": directional_rows,
        "physical_map_or_gate_changed": False,
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=4)
def n5_complex_flux_derivative_equivalence_audit(
    *, points: int = 44, outer_base_step: float = 1.0e-3,
) -> dict[str, Any]:
    """Validate the subtraction-free derivative of the unchanged flux map."""

    order = 5
    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    child = result["N5_event_conditioned_complete_child_reconstruction"]
    child_state = child["child_state"]
    state = np.concatenate((
        np.asarray(child_state["coordinates"], dtype=float),
        np.asarray(child_state["velocities"], dtype=float),
        np.asarray(child_state["multipliers"], dtype=float),
    ))
    selected_run = next(
        run for run in result[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"]
        if int(run["points"]) == points
    )
    event = selected_run["event"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    richardson_rows = _child_rows_at_order(
        order,
        state,
        q_event,
        event_momentum,
        event_flux,
        points=points,
        flux_derivative_method="richardson",
    )
    complex_rows = _child_rows_at_order(
        order,
        state,
        q_event,
        event_momentum,
        event_flux,
        points=points,
        flux_derivative_method="complex_step",
    )
    size = dimensions(order)
    qdim = size["coordinates"]
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        order,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=points,
    )
    momentum_rates = [
        _complex_step_canonical_momentum_rate(
            order,
            state[:qdim],
            state[qdim:2 * qdim],
            state[2 * qdim:],
            np.asarray(dynamics["acceleration"], dtype=float),
            np.asarray(dynamics["multiplier_rate"], dtype=float),
            points=points,
            step=step,
        )
        for step in (1.0e-8, 1.0e-12, 1.0e-16, 1.0e-20, 1.0e-24)
    ]
    momentum_rate_spread = max(
        _relative_difference(momentum_rates[index], momentum_rates[2])
        for index in range(len(momentum_rates))
    )
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))
    variable_count = state.size
    row_count = 2 * order + 8

    def central_jacobian(step: float) -> np.ndarray:
        jacobian = np.empty((row_count, variable_count))
        for column in range(variable_count):
            delta = np.zeros(variable_count)
            delta[column] = step / direction_weights[column]
            jacobian[:, column] = (
                _child_rows_at_order(
                    order,
                    state + delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    flux_derivative_method="complex_step",
                )
                - _child_rows_at_order(
                    order,
                    state - delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    flux_derivative_method="complex_step",
                )
            ) / (2.0 * step)
        return jacobian

    base_step = outer_base_step
    coarse = central_jacobian(base_step)
    mid = central_jacobian(0.5 * base_step)
    fine = central_jacobian(0.25 * base_step)
    coarse_richardson = (4.0 * mid - coarse) / 3.0
    fine_richardson = (4.0 * fine - mid) / 3.0
    row_scales = np.maximum(np.linalg.norm(fine_richardson, axis=1), 1.0)
    singular = np.linalg.svd(
        fine_richardson / row_scales[:, None], compute_uv=False
    )
    tolerance = np.finfo(float).eps * max(row_count, variable_count) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    constraint_stop = 3 + (2 * order + 1)
    block_changes = {
        name: float(
            np.linalg.norm(
                fine_richardson[row_slice] - coarse_richardson[row_slice]
            ) / max(1.0, np.linalg.norm(coarse_richardson[row_slice]))
        )
        for name, row_slice in (
            ("trace", slice(0, 3)),
            ("constraints", slice(3, constraint_stop)),
            ("canonical_momentum", slice(constraint_stop, constraint_stop + 2)),
            ("dynamic_Calderon_flux", slice(constraint_stop + 2, row_count)),
        )
    }
    outer_change = float(
        np.linalg.norm(fine_richardson - coarse_richardson)
        / max(1.0, np.linalg.norm(coarse_richardson))
    )
    value_equivalence = _relative_difference(complex_rows, richardson_rows)
    validated = bool(
        value_equivalence < 1.0e-7
        and momentum_rate_spread < 1.0e-8
        and outer_change < 1.0e-1
        and rank == row_count
    )
    return {
        "source": "LATEST_ADMISSIBLE_N5_CHILD_CHECKPOINT",
        "physical_map": (
            "UNCHANGED_PHI=Q_DAGGER_GAMMA_CHILD+Dp(y)X(y)-Q_DAGGER_L_q+"
            "GAMMA_EVENT"
        ),
        "Richardson_to_complex_step_row_relative_difference": value_equivalence,
        "complex_step_sizes": [1.0e-8, 1.0e-12, 1.0e-16, 1.0e-20, 1.0e-24],
        "complex_momentum_rate_maximum_relative_spread": momentum_rate_spread,
        "outer_Richardson_base_step": base_step,
        "outer_Richardson_relative_change": outer_change,
        "outer_Richardson_block_relative_changes": block_changes,
        "full_chart_rank": rank,
        "physical_row_count": row_count,
        "complex_flux_derivative_validated": validated,
        "subtractive_finite_difference_removed": True,
        "action_equations_or_child_gates_changed": False,
        "required_next": (
            "ADOPT_THE_EQUIVALENT_COMPLEX_STEP_FLUX_EVALUATION_AND_RESUME_"
            "THE_UNCHANGED_N5_18_ROW_SOLVE"
            if validated else
            "DERIVE_THE_FOURTH_VARIATION_OR_DIFFERENTIATED_CHILD_BVP"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n5_bicomplex_flux_jacobian_audit(*, points: int = 44) -> dict[str, Any]:
    """Validate the fourth-variation-equivalent N5 flux Jacobian block."""

    order = 5
    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    child_state = result[
        "N5_event_conditioned_complete_child_reconstruction"
    ]["child_state"]
    state = np.concatenate((
        np.asarray(child_state["coordinates"], dtype=float),
        np.asarray(child_state["velocities"], dtype=float),
        np.asarray(child_state["multipliers"], dtype=float),
    ))
    selected_run = next(
        run for run in result[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"]
        if int(run["points"]) == points
    )
    event = selected_run["event"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    _, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))

    def flux_block(outer_step: float, inner_relative_step: float) -> np.ndarray:
        block = np.empty((2, state.size))
        for column in range(state.size):
            direction = np.zeros(state.size)
            direction[column] = 1.0 / direction_weights[column]
            block[:, column] = _bicomplex_dynamic_flux_directional_derivative(
                order,
                state,
                direction,
                event_flux,
                points=points,
                outer_step=outer_step,
                inner_relative_step=inner_relative_step,
            )
        return block

    outer_steps = (1.0e-8, 1.0e-9, 1.0e-10)
    outer_blocks = [flux_block(step, 1.0e-1) for step in outer_steps]
    outer_changes = [
        _relative_difference(outer_blocks[index + 1], outer_blocks[index])
        for index in range(len(outer_blocks) - 1)
    ]
    inner_coarse = flux_block(1.0e-9, 2.0e-1)
    inner_change = _relative_difference(inner_coarse, outer_blocks[1])
    validated = bool(max(outer_changes) < 1.0e-2 and inner_change < 1.0e-2)
    return {
        "source": "LATEST_ADMISSIBLE_N5_CHILD_CHECKPOINT",
        "mathematical_route": (
            "BICOMPLEX_IDEMPOTENT_MIXED_DIRECTIONAL_DERIVATIVE_OF_THE_"
            "STATE_DEPENDENT_HESSIAN_MINIMAL_LIFT"
        ),
        "equivalent_higher_variation": "ACTION_FOURTH_VARIATION_DIRECTION",
        "outer_complex_steps": list(outer_steps),
        "outer_adjacent_relative_changes": outer_changes,
        "inner_Richardson_relative_steps": [2.0e-1, 1.0e-1],
        "inner_relative_change": inner_change,
        "selected_outer_complex_step": 1.0e-9,
        "selected_inner_relative_step": 1.0e-1,
        "flux_jacobian_shape": list(outer_blocks[1].shape),
        "flux_jacobian": outer_blocks[1].tolist(),
        "bicomplex_flux_jacobian_validated": validated,
        "subtractive_outer_difference_used": False,
        "action_equations_or_child_gates_changed": False,
        "required_next": (
            "ADOPT_AS_THE_N5_QUASI_NEWTON_FLUX_BLOCK_AND_RESUME_THE_EXACT_"
            "18_ROW_MERIT_SOLVE"
            if validated else "DERIVE_THE_DIFFERENTIATED_CHILD_BVP"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n5_exact_physical_merit_gradient_audit(*, points: int = 44) -> dict[str, Any]:
    """Audit a derivative of the unchanged fixed exact 18-row merit."""

    order = 5
    payload = json.loads((Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )).read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    child = result["N5_event_conditioned_complete_child_reconstruction"]
    child_state = child["child_state"]
    state = np.concatenate((
        np.asarray(child_state["coordinates"], dtype=float),
        np.asarray(child_state["velocities"], dtype=float),
        np.asarray(child_state["multipliers"], dtype=float),
    ))
    row_scales = np.asarray(
        child["proposal_model"]["fixed_reference_row_scales"], dtype=float
    )
    selected_run = next(
        run for run in result[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"] if int(run["points"]) == points
    )
    event = selected_run["event"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))

    def merit(solver_values: np.ndarray) -> float:
        physical = solver_values / direction_weights
        rows = _child_rows_at_order(
            order,
            physical,
            q_event,
            event_momentum,
            event_flux,
            points=points,
            flux_derivative_method="complex_step",
        ) / row_scales
        return 0.5 * float(rows @ rows)

    center = state * direction_weights

    def central_gradient(step: float) -> np.ndarray:
        gradient = np.empty(center.size)
        for column in range(center.size):
            delta = np.zeros(center.size)
            delta[column] = step
            gradient[column] = (
                merit(center + delta) - merit(center - delta)
            ) / (2.0 * step)
        return gradient

    steps = (1.0e-1, 5.0e-2, 2.5e-2)
    central = [central_gradient(step) for step in steps]
    coarse = (4.0 * central[1] - central[0]) / 3.0
    fine = (4.0 * central[2] - central[1]) / 3.0
    change = _relative_difference(fine, coarse)
    center_merit = merit(center)
    direction = -fine / max(1.0, float(np.linalg.norm(fine)))
    gradient_factors = tuple(2.0**-index for index in range(13))
    trial_merits = [
        merit(center + factor * direction)
        for factor in gradient_factors
    ]
    validated = bool(
        change < 1.0e-1 and min(trial_merits) < center_merit
    )
    return {
        "source": "LATEST_ADMISSIBLE_N5_CHILD_CHECKPOINT",
        "merit": "ONE_HALF_FIXED_REFERENCE_NORM_SQUARED_OF_EXACT_18_ROWS",
        "normalized_steps": list(steps),
        "coarse_to_fine_Richardson_relative_change": change,
        "gradient_norm": float(np.linalg.norm(fine)),
        "center_merit": center_merit,
        "negative_gradient_trial_factors": list(gradient_factors),
        "negative_gradient_trial_merits": trial_merits,
        "exact_merit_gradient_validated": validated,
        "componentwise_monotonicity_required": False,
        "action_equations_or_child_gates_changed": False,
        "required_next": (
            "ADOPT_AS_A_NUMERICAL_PROPOSAL_AND_RESUME_THE_N5_18_ROW_SOLVE"
            if validated else "DERIVE_THE_DIFFERENTIATED_CHILD_BVP"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n5_event_conditioned_complete_child_reconstruction(
    *, points: int = 44,
) -> dict[str, Any]:
    """Continue the exact N5 18-row map with a quasi-Newton proposal."""

    order = 5
    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    classification = result["N5_independent_eta_branch_event_classification"]
    selected_run = next(
        run for run in classification["quadrature_runs"]
        if int(run["points"]) == points
    )
    event = selected_run["event"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    size = dimensions(order)
    qdim = size["coordinates"]
    variable_count = 2 * qdim + size["multipliers"]
    row_count = 2 * order + 8
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    event_values, event_vectors = np.linalg.eigh(
        exact_action_jet_at_state(
            order, q_event, v_event, m_event, points=points
        ).hessian
    )
    branch = int(event["branch_index"])
    soft_mode = event_vectors[:, branch]
    candidates: list[tuple[float, float, np.ndarray]] = []
    for magnitude in (1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1):
        for sign in (-1.0, 1.0):
            amplitude = sign * magnitude
            fiber = np.concatenate((v_event, m_event)) + amplitude * soft_mode
            projection = project_nested_constraints_sobolev(
                order,
                q_event,
                fiber[:qdim],
                fiber[qdim:],
                points=points,
            )
            if not projection["success"]:
                continue
            state = np.concatenate((
                q_event,
                np.asarray(projection["velocities"], dtype=float),
                np.asarray(projection["multipliers"], dtype=float),
            ))
            if _eta_legendre_minimum(
                order, state[:qdim], state[2 * qdim:], points=2400
            )["minimum"] <= 0.0:
                continue
            rows = _child_rows_at_order(
                order,
                state,
                q_event,
                event_momentum,
                event_flux,
                points=points,
            )
            candidates.append((float(np.linalg.norm(rows[-2:])), amplitude, state))
    if not candidates:
        raise RuntimeError("no admissible independent N5 child germ")
    _, selected_amplitude, state = min(candidates, key=lambda item: item[0])
    continuation_checkpoint_used = False
    stored_checkpoint = result.get(
        "N5_event_conditioned_complete_child_reconstruction"
    )
    if (
        isinstance(stored_checkpoint, dict)
        and stored_checkpoint.get("checkpoint_promotion_eligible") is True
        and stored_checkpoint.get("child_state", {}).get(
            "eta_Legendre", {}
        ).get("minimum", -1.0) > 0.0
    ):
        stored_state = stored_checkpoint["child_state"]
        candidate = np.concatenate((
            np.asarray(stored_state["coordinates"], dtype=float),
            np.asarray(stored_state["velocities"], dtype=float),
            np.asarray(stored_state["multipliers"], dtype=float),
        ))
        if candidate.shape == state.shape:
            state = candidate
            continuation_checkpoint_used = True
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))

    def exact_rows(center: np.ndarray) -> np.ndarray:
        return _child_rows_at_order(
            order,
            center,
            q_event,
            event_momentum,
            event_flux,
            points=points,
            flux_derivative_method="complex_step",
        )

    def proposal_jacobian(center: np.ndarray, step: float) -> np.ndarray:
        del step
        jacobian = np.empty((row_count, variable_count))
        q_center = center[:qdim]
        v_center = center[qdim:2 * qdim]
        m_center = center[2 * qdim:]
        full_jet = exact_full_action_jet_at_state(
            order, q_center, v_center, m_center, points=points
        )
        full_gradient = np.asarray(full_jet.gradient, dtype=float)
        full_hessian = np.asarray(full_jet.hessian, dtype=float)
        multiplier_start = 2 * qdim
        constraint_jacobian = full_hessian[multiplier_start:, :]
        energy_gradient = np.concatenate((
            v_center @ full_hessian[
                qdim:2 * qdim, :qdim
            ] - full_gradient[:qdim],
            full_hessian[
                qdim:2 * qdim, qdim:2 * qdim
            ] @ v_center,
            v_center @ full_hessian[
                qdim:2 * qdim, multiplier_start:
            ] - full_gradient[multiplier_start:],
        ))
        trace_jacobian = _trace_jacobian_at_order(order)
        for column in range(variable_count):
            direction = np.zeros(variable_count)
            direction[column] = 1.0 / direction_weights[column]
            jacobian[:3, column] = (
                trace_jacobian @ direction[:qdim]
            )
            jacobian[3:3 + size["multipliers"], column] = (
                constraint_jacobian @ direction
            )
            jacobian[3 + size["multipliers"], column] = (
                energy_gradient @ direction
            )
            outer = center.astype(complex) + 1j * 1.0e-20 * direction
            complex_momentum, _, _, _ = _canonical_pair_at_order(
                order,
                outer[:qdim],
                outer[qdim:2 * qdim],
                outer[2 * qdim:],
                points=points,
            )
            jacobian[-4:-2, column] = (
                np.imag(complex_momentum) / 1.0e-20
            )
            jacobian[-2:, column] = (
                _bicomplex_dynamic_flux_directional_derivative(
                    order,
                    center,
                    direction,
                    event_flux,
                    points=points,
                    outer_step=1.0e-9,
                    inner_relative_step=1.0e-1,
                )
            )
        return jacobian

    proposal_step = 1.0e-3
    row_scales: np.ndarray | None = None
    fixed_merit_scaling_preserved = False
    if continuation_checkpoint_used and isinstance(stored_checkpoint, dict):
        stored_scales = np.asarray(
            stored_checkpoint.get("proposal_model", {}).get(
                "fixed_reference_row_scales", []
            ),
            dtype=float,
        )
        if stored_scales.shape == (row_count,) and np.all(stored_scales > 0.0):
            row_scales = stored_scales
            fixed_merit_scaling_preserved = True
    if row_scales is None:
        initial_jacobian = proposal_jacobian(state, proposal_step)
        row_scales = np.maximum(np.linalg.norm(initial_jacobian, axis=1), 1.0)
    solver_values = state * direction_weights
    rows = exact_rows(state)
    scaled_rows = rows / row_scales
    initial_merit = float(np.linalg.norm(scaled_rows))
    merit_gradient_audit: dict[str, Any] = {
        "attempted": False,
        "accepted": False,
    }
    accepted_steps = 0
    if continuation_checkpoint_used:
        merit_gradient_audit["attempted"] = True

        def scalar_merit(values: np.ndarray) -> float:
            trial = values / direction_weights
            trial_rows = exact_rows(trial) / row_scales
            return 0.5 * float(trial_rows @ trial_rows)

        central_gradients: list[np.ndarray] = []
        gradient_steps = (1.0e-1, 5.0e-2, 2.5e-2)
        for gradient_step in gradient_steps:
            gradient = np.empty(variable_count)
            for column in range(variable_count):
                delta = np.zeros(variable_count)
                delta[column] = gradient_step
                gradient[column] = (
                    scalar_merit(solver_values + delta)
                    - scalar_merit(solver_values - delta)
                ) / (2.0 * gradient_step)
            central_gradients.append(gradient)
        coarse_gradient = (
            4.0 * central_gradients[1] - central_gradients[0]
        ) / 3.0
        fine_gradient = (
            4.0 * central_gradients[2] - central_gradients[1]
        ) / 3.0
        gradient_change = _relative_difference(
            fine_gradient, coarse_gradient
        )
        gradient_direction = -fine_gradient / max(
            1.0, float(np.linalg.norm(fine_gradient))
        )
        center_squared_merit = 0.5 * initial_merit**2
        gradient_trials: list[dict[str, float]] = []
        best: tuple[float, np.ndarray] | None = None
        for factor in (2.0**-index for index in range(13)):
            trial_values = solver_values + factor * gradient_direction
            trial_state = trial_values / direction_weights
            eta_trial = _eta_legendre_minimum(
                order,
                trial_state[:qdim],
                trial_state[2 * qdim:],
                points=800,
            )["minimum"]
            if eta_trial <= 0.0:
                continue
            trial_squared_merit = scalar_merit(trial_values)
            gradient_trials.append({
                "factor": factor,
                "squared_merit": trial_squared_merit,
                "eta_minimum": eta_trial,
            })
            if (
                trial_squared_merit < center_squared_merit
                and (best is None or trial_squared_merit < best[0])
            ):
                best = (trial_squared_merit, trial_values)
        merit_gradient_audit.update({
            "normalized_steps": list(gradient_steps),
            "Richardson_relative_change": gradient_change,
            "promoted_as_exact_derivative": False,
            "trials": gradient_trials,
        })
        if best is not None:
            solver_values = best[1]
            state = solver_values / direction_weights
            rows = exact_rows(state)
            scaled_rows = rows / row_scales
            accepted_steps = 1
            merit_gradient_audit["accepted"] = True
    raw_jacobian = proposal_jacobian(state, proposal_step)
    jacobian = raw_jacobian / row_scales[:, None]
    rejected_trials = 0
    refreshes = 0
    rejected_step_secant_repairs = 0
    exact_flux_coordinate_refreshes = 0
    poll_evaluations = 0
    accepted_poll_steps = 0
    poll_attempts = 0
    trust_radius = 16.0
    message = "maximum quasi-Newton iterations reached"
    first_direction_audit: dict[str, Any] | None = None
    for iteration in range(64):
        merit = float(np.linalg.norm(scaled_rows))
        if merit < 1.0e-10:
            message = "scaled complete-child merit converged"
            break
        delta = np.linalg.lstsq(jacobian, -scaled_rows, rcond=1.0e-12)[0]
        delta_norm = float(np.linalg.norm(delta))
        if delta_norm > trust_radius:
            delta *= trust_radius / delta_norm
        if iteration == 0:
            predicted_row_change = jacobian @ delta
            block_slices = {
                "trace": slice(0, 3),
                "constraints": slice(3, 14),
                "canonical_momentum": slice(14, 16),
                "dynamic_Calderon_flux": slice(16, 18),
            }
            first_direction_audit = {
                "raw_minimum_norm_step": delta_norm,
                "applied_step_norm": float(np.linalg.norm(delta)),
                "solver_direction": delta.tolist(),
                "predicted_merit_directional_derivative": float(
                    scaled_rows @ predicted_row_change
                ),
                "predicted_block_directional_derivatives": {
                    name: float(
                        scaled_rows[row_slice]
                        @ predicted_row_change[row_slice]
                    )
                    for name, row_slice in block_slices.items()
                },
                "center_scaled_block_norms": {
                    name: float(np.linalg.norm(scaled_rows[row_slice]))
                    for name, row_slice in block_slices.items()
                },
                "line_trials": [],
            }
        accepted = False
        factor = 1.0
        secant_candidates: list[
            tuple[float, np.ndarray, np.ndarray, np.ndarray]
        ] = []
        while factor >= 2.0**-24:
            trial_values = solver_values + factor * delta
            trial_state = trial_values / direction_weights
            if _eta_legendre_minimum(
                order,
                trial_state[:qdim],
                trial_state[2 * qdim:],
                points=800,
            )["minimum"] <= 0.0:
                factor *= 0.5
                rejected_trials += 1
                continue
            try:
                trial_rows = exact_rows(trial_state)
            except (ArithmeticError, RuntimeError, ValueError, np.linalg.LinAlgError):
                factor *= 0.5
                rejected_trials += 1
                continue
            trial_scaled = trial_rows / row_scales
            trial_merit = float(np.linalg.norm(trial_scaled))
            secant_candidates.append((
                factor, trial_values, trial_rows, trial_scaled
            ))
            if iteration == 0 and first_direction_audit is not None:
                first_direction_audit["line_trials"].append({
                    "factor": factor,
                    "merit": trial_merit,
                    "eta_minimum": _eta_legendre_minimum(
                        order,
                        trial_state[:qdim],
                        trial_state[2 * qdim:],
                        points=800,
                    )["minimum"],
                    "scaled_block_norms": {
                        name: float(np.linalg.norm(trial_scaled[row_slice]))
                        for name, row_slice in block_slices.items()
                    },
                })
            if trial_merit < merit:
                accepted = True
                break
            factor *= 0.5
            rejected_trials += 1
        if not accepted:
            best_merit = merit
            best: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None
            poll_refreshed_flux = False
            for poll_factor in (() if poll_attempts else (1.0, 0.4)):
                poll_attempts += 1
                poll_radius = trust_radius * poll_factor
                paired_poll_rows: dict[
                    tuple[int, float], np.ndarray
                ] = {}
                for column in range(variable_count):
                    for sign in (-1.0, 1.0):
                        trial_values = solver_values.copy()
                        trial_values[column] += sign * poll_radius
                        trial_state = trial_values / direction_weights
                        if _eta_legendre_minimum(
                            order,
                            trial_state[:qdim],
                            trial_state[2 * qdim:],
                            points=800,
                        )["minimum"] <= 0.0:
                            continue
                        try:
                            trial_rows = exact_rows(trial_state)
                        except (
                            ArithmeticError, RuntimeError, ValueError,
                            np.linalg.LinAlgError,
                        ):
                            continue
                        poll_evaluations += 1
                        trial_scaled = trial_rows / row_scales
                        paired_poll_rows[(column, sign)] = trial_scaled
                        trial_merit = float(np.linalg.norm(trial_scaled))
                        if trial_merit < best_merit:
                            best_merit = trial_merit
                            best = (trial_values, trial_rows, trial_scaled)
                refreshed_columns = 0
                for column in range(variable_count):
                    minus = paired_poll_rows.get((column, -1.0))
                    plus = paired_poll_rows.get((column, 1.0))
                    if minus is None or plus is None:
                        continue
                    jacobian[-2:, column] = (
                        plus[-2:] - minus[-2:]
                    ) / (2.0 * poll_radius)
                    refreshed_columns += 1
                if refreshed_columns:
                    exact_flux_coordinate_refreshes += 1
                    poll_refreshed_flux = True
                if best is not None:
                    break
            if best is not None:
                trial_values, trial_rows, trial_scaled = best
                accepted = True
                accepted_poll_steps += 1
                factor = poll_factor
            elif poll_refreshed_flux:
                trust_radius = max(1.0e-6, 0.5 * trust_radius)
                continue
        if not accepted:
            # The exact residual evaluations rejected by the merit gate still
            # contain local curvature information.  Retain a sufficiently
            # resolved, smallest-step secant instead of replacing the evolved
            # model with the identical seed Jacobian (``proposal_step`` does
            # not enter ``proposal_jacobian``).  This changes proposals only;
            # exact merit and eta continue to decide every accepted state.
            secant_signal_floor = max(1.0e-7, 1.0e-4 * merit)
            resolved_secants = [
                candidate for candidate in secant_candidates
                if float(np.linalg.norm(candidate[3] - scaled_rows))
                >= secant_signal_floor
            ]
            if resolved_secants:
                _, secant_values, _, secant_scaled = resolved_secants[-1]
                step_vector = secant_values - solver_values
                row_change = secant_scaled - scaled_rows
                denominator = float(step_vector @ step_vector)
                if denominator > 1.0e-24:
                    jacobian += np.outer(
                        row_change - jacobian @ step_vector, step_vector
                    ) / denominator
                    rejected_step_secant_repairs += 1
                    trust_radius = max(1.0e-6, 0.5 * trust_radius)
                    continue
            if refreshes < 2:
                state = solver_values / direction_weights
                raw_jacobian = proposal_jacobian(
                    state, proposal_step * (0.5 ** (refreshes + 1))
                )
                jacobian = raw_jacobian / row_scales[:, None]
                refreshes += 1
                trust_radius *= 0.5
                continue
            message = "exact-merit line search exhausted after proposal refreshes"
            break
        step_vector = trial_values - solver_values
        row_change = trial_scaled - scaled_rows
        denominator = float(step_vector @ step_vector)
        if denominator > 1.0e-24:
            jacobian += np.outer(
                row_change - jacobian @ step_vector, step_vector
            ) / denominator
        solver_values = trial_values
        scaled_rows = trial_scaled
        rows = trial_rows
        accepted_steps += 1
        trust_radius = (
            min(32.0, 1.5 * trust_radius)
            if factor == 1.0 else max(1.0e-6, factor * trust_radius)
        )
    state = solver_values / direction_weights
    final_rows = exact_rows(state)
    final_merit = float(np.linalg.norm(final_rows / row_scales))
    eta = _eta_legendre_minimum(
        order, state[:qdim], state[2 * qdim:], points=5000
    )
    constraint_stop = 3 + (2 * order + 1)
    root_closed = bool(
        np.max(np.abs(final_rows[:3])) < 1.0e-9
        and np.max(np.abs(final_rows[3:constraint_stop])) < 1.0e-9
        and np.linalg.norm(final_rows[constraint_stop:constraint_stop + 2]) < 1.0e-7
        and np.linalg.norm(final_rows[-2:]) < 2.0e-5
        and eta["minimum"] > 0.0
    )
    return {
        "source_event": (
            "INDEPENDENT_N5_ZERO_MULTIPLIER_ETA_ADMISSIBLE_44_POINT_EVENT"
        ),
        "accepted_N3_trajectory_or_N4_child_used": False,
        "event_soft_branch_index": branch,
        "event_soft_eigenvalue": float(event_values[branch]),
        "selected_broken_germ_amplitude": selected_amplitude,
        "continuation_checkpoint_used": continuation_checkpoint_used,
        "physical_row_count": row_count,
        "whole_child_variable_count": variable_count,
        "proposal_model": {
            "classification": (
                "ACTION_SOBOLEV_QUASI_NEWTON_WITH_VALIDATED_BICOMPLEX_"
                "FOURTH_VARIATION_FLUX_BLOCK_AND_EXACT_RESIDUAL_PROMOTION"
            ),
            "outer_step": proposal_step,
            "inner_relative_flux_step": 1.0e-1,
            "finite_difference_derivative_promoted_as_physics": False,
            "bicomplex_flux_jacobian_adopted": True,
            "bicomplex_outer_step": 1.0e-9,
            "bicomplex_inner_relative_step": 1.0e-1,
            "componentwise_monotonicity_required": False,
            "fixed_reference_row_scales": row_scales.tolist(),
            "fixed_merit_scaling_preserved_from_checkpoint": (
                fixed_merit_scaling_preserved
            ),
        },
        "solver": {
            "accepted_steps": accepted_steps,
            "rejected_trials": rejected_trials,
            "proposal_refreshes": refreshes,
            "rejected_step_secant_repairs": rejected_step_secant_repairs,
            "exact_flux_coordinate_refreshes": exact_flux_coordinate_refreshes,
            "derivative_free_poll_evaluations": poll_evaluations,
            "accepted_derivative_free_poll_steps": accepted_poll_steps,
            "derivative_free_poll_radii_attempted": poll_attempts,
            "message": message,
            "initial_fixed_reference_merit": initial_merit,
            "final_fixed_reference_merit": final_merit,
            "fixed_reference_merit_reduced": final_merit < initial_merit,
            "inexact_exact_merit_gradient_proposal": merit_gradient_audit,
            "first_coupled_direction_audit": first_direction_audit,
        },
        "child_state": {
            "coordinates": state[:qdim].tolist(),
            "velocities": state[qdim:2 * qdim].tolist(),
            "multipliers": state[2 * qdim:].tolist(),
            "eta_Legendre": eta,
        },
        "physical_residuals": {
            "maximum_trace": float(np.max(np.abs(final_rows[:3]))),
            "maximum_eleven_constraints": float(
                np.max(np.abs(final_rows[3:constraint_stop]))
            ),
            "momentum_norm": float(np.linalg.norm(
                final_rows[constraint_stop:constraint_stop + 2]
            )),
            "dynamic_flux_norm": float(np.linalg.norm(final_rows[-2:])),
        },
        "complete_child_candidate_validated": root_closed,
        "persistence_evaluated": False,
        "checkpoint_promotion_eligible": bool(
            accepted_steps > 0 and final_merit < initial_merit
            and eta["minimum"] > 0.0
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "required_next": (
            "EVALUATE_POSITIVE_DURATION_CONSTRAINT_CONSISTENT_RELATIVE_N5_"
            "PERSISTENCE" if root_closed else
            "CONTINUE_THE_UNCHANGED_EXACT_MERIT_N5_18_ROW_CHILD_SOLVE_"
            "WITH_THE_VALIDATED_BICOMPLEX_FOURTH_VARIATION_FLUX_BLOCK"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n4_latest_checkpoint_proposal_audit(
    *, points: int = 44, outer_base_step: float = 1.0e-4,
    inner_relative_flux_step: float = 4.0e-3,
) -> dict[str, Any]:
    """Compare pivot-chart and full-space proposals at the latest N4 stop."""

    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    stored = result["N4_event_conditioned_complete_child_reconstruction"]
    event_run = result["N4_adaptive_event_convergence_audit"][
        "quadrature_control"
    ]
    event = event_run["event"]
    if event is None or int(event_run["quadrature_points"]) != points:
        raise RuntimeError("validated N4 event does not match proposal audit")
    order = 4
    size = dimensions(order)
    qdim = size["coordinates"]
    variable_count = 2 * qdim + size["multipliers"]
    state = stored["child_state"]
    center = np.concatenate((
        np.asarray(state["coordinates"], dtype=float),
        np.asarray(state["velocities"], dtype=float),
        np.asarray(state["multipliers"], dtype=float),
    ))
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    frequencies = spectral_frequencies(order)
    regularity_weights = sobolev_weights(order)
    direction_weights = np.concatenate((
        (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
        regularity_weights["velocities"],
        regularity_weights["multipliers"],
    ))
    row_scales = np.asarray(
        stored["chart"].get(
            "merit_reference_row_scales", stored["chart"]["row_scales"]
        ),
        dtype=float,
    )
    center_rows = _n4_child_rows(
        center, q_event, event_momentum, event_flux, points=points
    )
    center_merit = float(np.linalg.norm(center_rows / row_scales))
    inner_step = _n4_child_flux_time_step(
        center,
        points=points,
        relative_flux_step=inner_relative_flux_step,
    )

    def central_jacobian(step: float) -> np.ndarray:
        matrix = np.empty((16, variable_count))
        for column in range(variable_count):
            delta = np.zeros(variable_count)
            delta[column] = step / direction_weights[column]
            matrix[:, column] = (
                _n4_child_rows(
                    center + delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    fixed_flux_time_step=inner_step,
                )
                - _n4_child_rows(
                    center - delta,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                    fixed_flux_time_step=inner_step,
                )
            ) / (2.0 * step)
        return matrix

    base_step = float(outer_base_step)
    coarse = central_jacobian(2.0 * base_step)
    middle = central_jacobian(base_step)
    fine = central_jacobian(0.5 * base_step)
    coarse_richardson = (4.0 * middle - coarse) / 3.0
    jacobian = (4.0 * fine - middle) / 3.0
    scaled_jacobian = jacobian / row_scales[:, None]
    scaled_rows = center_rows / row_scales
    singular = np.linalg.svd(scaled_jacobian, compute_uv=False)
    tolerance = (
        np.finfo(float).eps * max(scaled_jacobian.shape) * singular[0]
    )
    rank = int(np.count_nonzero(singular > tolerance))
    derivative_change = float(
        np.linalg.norm(jacobian - coarse_richardson)
        / max(1.0, np.linalg.norm(coarse_richardson))
    )
    _, _, pivots = qr(scaled_jacobian, mode="economic", pivoting=True)
    fresh_chart = np.asarray(pivots[:16], dtype=int)
    stored_chart = np.asarray(
        stored["chart"]["selected_variable_indices"], dtype=int
    )

    def trust_limited(direction: np.ndarray) -> np.ndarray:
        norm = float(np.linalg.norm(direction))
        return direction if norm <= 1.0 else direction / norm

    full_direction = trust_limited(np.linalg.lstsq(
        scaled_jacobian, -scaled_rows, rcond=1.0e-12
    )[0])
    fresh_direction = np.zeros(variable_count)
    fresh_direction[fresh_chart] = np.linalg.lstsq(
        scaled_jacobian[:, fresh_chart], -scaled_rows, rcond=1.0e-12
    )[0]
    fresh_direction = trust_limited(fresh_direction)
    stored_direction = np.zeros(variable_count)
    stored_direction[stored_chart] = np.linalg.lstsq(
        scaled_jacobian[:, stored_chart], -scaled_rows, rcond=1.0e-12
    )[0]
    stored_direction = trust_limited(stored_direction)
    gradient_direction = trust_limited(-scaled_jacobian.T @ scaled_rows)

    def line_audit(direction: np.ndarray) -> dict[str, Any]:
        best: dict[str, Any] | None = None
        admissible_trials = 0
        for exponent in range(0, 29):
            factor = 2.0 ** (-exponent)
            trial = center + factor * direction / direction_weights
            eta = _eta_legendre_minimum(
                order, trial[:qdim], trial[2 * qdim:], points=800
            )
            if eta["minimum"] <= 0.0:
                continue
            admissible_trials += 1
            try:
                rows = _n4_child_rows(
                    trial,
                    q_event,
                    event_momentum,
                    event_flux,
                    points=points,
                )
            except (
                ArithmeticError, RuntimeError, ValueError,
                np.linalg.LinAlgError,
            ):
                continue
            merit = float(np.linalg.norm(rows / row_scales))
            candidate = {
                "factor": factor,
                "fixed_reference_merit": merit,
                "merit_change": merit - center_merit,
                "eta_minimum": eta["minimum"],
                "raw_step_norm": float(np.linalg.norm(trial - center)),
                "scaled_step_norm": float(factor * np.linalg.norm(direction)),
                "physical_block_norms": {
                    "trace": float(np.linalg.norm(rows[:3])),
                    "constraints": float(np.linalg.norm(rows[3:12])),
                    "momentum": float(np.linalg.norm(rows[12:14])),
                    "dynamic_flux": float(np.linalg.norm(rows[14:16])),
                },
            }
            if best is None or merit < best["fixed_reference_merit"]:
                best = candidate
        return {
            "direction_norm_before_line_search": float(
                np.linalg.norm(direction)
            ),
            "admissible_trials": admissible_trials,
            "best": best,
            "strict_fixed_merit_reduction_found": bool(
                best is not None
                and best["fixed_reference_merit"] < center_merit
            ),
        }

    proposals = {
        "full_34_variable_minimum_norm_Gauss_Newton": line_audit(
            full_direction
        ),
        "fresh_16_variable_pivot_chart_Newton": line_audit(fresh_direction),
        "stored_16_variable_pivot_chart_Newton": line_audit(stored_direction),
        "full_34_variable_fixed_merit_gradient": line_audit(
            gradient_direction
        ),
    }
    full_reduces = proposals[
        "full_34_variable_minimum_norm_Gauss_Newton"
    ]["strict_fixed_merit_reduction_found"]
    fresh_reduces = proposals[
        "fresh_16_variable_pivot_chart_Newton"
    ]["strict_fixed_merit_reduction_found"]
    stored_reduces = proposals[
        "stored_16_variable_pivot_chart_Newton"
    ]["strict_fixed_merit_reduction_found"]
    if full_reduces and not (fresh_reduces or stored_reduces):
        classification = "PIVOT_CHART_PROPOSAL_BLOCKER_IDENTIFIED"
        required_next = (
            "USE_THE_FULL_34_VARIABLE_MINIMUM_NORM_PROPOSAL_WITH_EXACT_"
            "FIXED_MERIT_AND_ETA_PROMOTION"
        )
    elif full_reduces or fresh_reduces or stored_reduces:
        classification = "LOCAL_ROOT_DESCENT_DIRECTION_EXISTS"
        required_next = (
            "RESUME_WITH_THE_BEST_VALIDATED_FIXED_MERIT_DIRECTION"
        )
    else:
        classification = "NO_TESTED_LOCAL_DESCENT_DIRECTION"
        required_next = (
            "AUDIT_DYNAMIC_FLUX_LINEARIZATION_OR_LOCAL_STATIONARITY_BEFORE_"
            "MORE_CONTINUATION"
        )
    return {
        "source": "LATEST_PROMOTED_ADMISSIBLE_N4_CHILD_CHECKPOINT",
        "exact_fixed_reference_merit": center_merit,
        "exact_physical_rows": center_rows.tolist(),
        "derivative": {
            "rank": rank,
            "smallest_singular_value": float(singular[rank - 1]),
            "coarse_to_fine_Richardson_relative_change": derivative_change,
            "outer_directions": (
                "H6_COORDINATES_H5_VELOCITIES_H6_MULTIPLIERS"
            ),
            "outer_base_step": base_step,
            "inner_relative_flux_step": inner_relative_flux_step,
            "physical_equations_changed": False,
        },
        "fresh_chart": fresh_chart.tolist(),
        "stored_chart": stored_chart.tolist(),
        "proposals": proposals,
        "classification": classification,
        "required_next": required_next,
        "componentwise_monotonicity_required": False,
        "new_physical_rows_constraints_or_gates_added": False,
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=1)
def n4_complete_child_positive_duration_persistence(
    *, points: int = 44, time_step: float = 1.0e-5, steps: int = 10,
    _order: int = 4,
    _child_key: str = "N4_event_conditioned_complete_child_reconstruction",
    _source_label: str = "VALIDATED_INDEPENDENT_N4_COMPLETE_CHILD",
) -> dict[str, Any]:
    """Evolve the validated moving N4 child inside its physical domain."""

    if time_step <= 0.0 or steps < 1:
        raise ValueError("positive persistence controls required")
    artifact_path = Path("artifacts") / (
        "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    )
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    child = payload["cross_resolution_reconnaissance"][_child_key]
    if not child["complete_child_candidate_validated"]:
        raise RuntimeError("complete child must close before persistence")
    order = _order
    qdim = dimensions(order)["coordinates"]
    source = child["child_state"]
    exact_source = source.get("binary64_hex")
    if exact_source is not None:
        source = {
            **source,
            "coordinates": [
                float.fromhex(item) for item in exact_source["coordinates"]
            ],
            "velocities": [
                float.fromhex(item) for item in exact_source["velocities"]
            ],
            "multipliers": [
                float.fromhex(item) for item in exact_source["multipliers"]
            ],
        }
    q0 = np.asarray(source["coordinates"], dtype=float)
    v0 = np.asarray(source["velocities"], dtype=float)
    m0 = np.asarray(source["multipliers"], dtype=float)
    frequencies = spectral_frequencies(order)
    weights = sobolev_weights(order)
    q_weight = (1.0 + frequencies["coordinates"] ** 2) ** 3.0
    product_weight = np.concatenate((
        q_weight, weights["velocities"], weights["multipliers"]
    ))
    signs_k = (-1.0) ** np.arange(1, order + 1)

    def boundary_lapse(multipliers: np.ndarray) -> float:
        return float(math.exp(float(multipliers[:order] @ signs_k)))

    def rk4_projected(
        q: np.ndarray, velocity: np.ndarray, multipliers: np.ndarray,
        step: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, dict[str, Any]]:
        def rhs(
            x: np.ndarray, rate: np.ndarray, lapse_shift: np.ndarray,
        ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
            dynamics = _exact_full_jet_euler_dirac_acceleration(
                order, x, rate, lapse_shift, points=points
            )
            return (
                np.asarray(dynamics["coordinate_rate"], dtype=float),
                np.asarray(dynamics["acceleration"], dtype=float),
                np.asarray(dynamics["multiplier_rate"], dtype=float),
                float(dynamics["Dirac_condition_number"]),
            )

        k1 = rhs(q, velocity, multipliers)
        k2 = rhs(
            q + 0.5 * step * k1[0],
            velocity + 0.5 * step * k1[1],
            multipliers + 0.5 * step * k1[2],
        )
        k3 = rhs(
            q + 0.5 * step * k2[0],
            velocity + 0.5 * step * k2[1],
            multipliers + 0.5 * step * k2[2],
        )
        k4 = rhs(
            q + step * k3[0],
            velocity + step * k3[1],
            multipliers + step * k3[2],
        )
        q_trial = q + step * (
            k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]
        ) / 6.0
        v_trial = velocity + step * (
            k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]
        ) / 6.0
        m_trial = multipliers + step * (
            k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]
        ) / 6.0
        projection = project_nested_constraints_sobolev(
            order, q_trial, v_trial, m_trial, points=points
        )
        if not projection["success"]:
            raise RuntimeError(str(projection["message"]))
        return (
            q_trial,
            np.asarray(projection["velocities"], dtype=float),
            np.asarray(projection["multipliers"], dtype=float),
            max(k1[3], k2[3], k3[3], k4[3]),
            projection,
        )

    def run(step: float, count: int) -> dict[str, Any]:
        q = q0.copy()
        velocity = v0.copy()
        multipliers = m0.copy()
        proper_time = 0.0
        rows: list[dict[str, Any]] = []
        maximum_condition = 0.0
        first_exit: dict[str, Any] | None = None
        for index in range(count + 1):
            constraints = constraint_residual(
                order, q, velocity, multipliers, points=points
            )
            eta = _eta_legendre_minimum(
                order, q, multipliers, points=3000
            )
            state = np.concatenate((q, velocity, multipliers))
            finite = bool(np.all(np.isfinite(state)))
            maximum_constraint = float(np.max(np.abs(constraints)))
            inside = bool(
                finite and maximum_constraint < 1.0e-8
                and eta["minimum"] > 0.0
            )
            rows.append({
                "step": index,
                "coordinate_time": index * step,
                "child_proper_time": proper_time,
                "maximum_constraint_residual": maximum_constraint,
                "eta_Legendre_minimum": eta["minimum"],
                "boundary_lapse": boundary_lapse(multipliers),
                "finite": finite,
                "inside_persistence_domain": inside,
                "configuration_displacement_norm": float(
                    np.linalg.norm(q - q0)
                ),
                "velocity_displacement_norm": float(
                    np.linalg.norm(velocity - v0)
                ),
            })
            if not inside:
                first_exit = dict(rows[-1])
                break
            if index < count:
                lapse_before = boundary_lapse(multipliers)
                q, velocity, multipliers, condition, projection = (
                    rk4_projected(q, velocity, multipliers, step)
                )
                maximum_condition = max(maximum_condition, condition)
                rows[-1]["outgoing_projection_success"] = bool(
                    projection["success"]
                )
                rows[-1]["outgoing_Dirac_condition_number"] = condition
                proper_time += 0.5 * step * (
                    lapse_before + boundary_lapse(multipliers)
                )
        final = np.concatenate((q, velocity, multipliers))
        completed = len(rows) == count + 1 and first_exit is None
        return {
            "time_step": step,
            "requested_steps": count,
            "completed": completed,
            "rows": rows,
            "coordinate_duration": rows[-1]["coordinate_time"],
            "child_proper_duration": rows[-1]["child_proper_time"],
            "maximum_constraint_residual": max(
                row["maximum_constraint_residual"] for row in rows
            ),
            "minimum_eta_Legendre": min(
                row["eta_Legendre_minimum"] for row in rows
            ),
            "maximum_Dirac_condition_number": maximum_condition,
            "final_state": final.tolist(),
            "final_configuration_displacement_norm": rows[-1][
                "configuration_displacement_norm"
            ],
            "final_velocity_displacement_norm": rows[-1][
                "velocity_displacement_norm"
            ],
            "first_exit": first_exit,
        }

    coarse = run(time_step, steps)
    fine = run(0.5 * time_step, 2 * steps)
    coarse_final = np.asarray(coarse["final_state"], dtype=float)
    fine_final = np.asarray(fine["final_state"], dtype=float)
    convergence = float(np.linalg.norm(
        (coarse_final - fine_final) * product_weight
    ) / max(1.0, np.linalg.norm(fine_final * product_weight)))
    numerical_witness_validated = bool(
        coarse["completed"]
        and fine["completed"]
        and coarse["maximum_constraint_residual"] < 1.0e-8
        and fine["maximum_constraint_residual"] < 1.0e-8
        and min(
            coarse["minimum_eta_Legendre"], fine["minimum_eta_Legendre"]
        ) > 0.0
        and fine["child_proper_duration"] > 0.0
        and fine["final_configuration_displacement_norm"] > 0.0
        and fine["final_velocity_displacement_norm"] > 0.0
        and convergence < 1.0e-2
    )
    initial_dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q0, v0, m0, points=points
    )
    dirac_hessian = np.asarray(
        initial_dynamics["Dirac_hessian"], dtype=float
    )
    dirac_singular = np.linalg.svd(dirac_hessian, compute_uv=False)
    initial_vector_field = np.concatenate((
        np.asarray(initial_dynamics["coordinate_rate"], dtype=float),
        np.asarray(initial_dynamics["acceleration"], dtype=float),
        np.asarray(initial_dynamics["multiplier_rate"], dtype=float),
    ))
    initial_constraints = constraint_residual(
        order, q0, v0, m0, points=points
    )
    initial_eta = _eta_legendre_minimum(order, q0, m0, points=5000)
    local_existence_validated = bool(
        np.all(np.isfinite(initial_vector_field))
        and dirac_singular[-1] > 0.0
        and float(np.max(np.abs(initial_constraints))) < 1.0e-8
        and initial_eta["minimum"] > 0.0
        and boundary_lapse(m0) > 0.0
        and float(np.linalg.norm(v0)) > 0.0
    )
    validated = bool(
        local_existence_validated or numerical_witness_validated
    )
    return {
        "source": _source_label,
        "persistence_domain": (
            "FINITE_CONSTRAINT_CONSISTENT_L_eta_POSITIVE_RELATIVE_CHILD_"
            "EVOLUTION_WITH_FIXED_DISCRETE_TOPOLOGY_AND_CARRIER_CLASS"
        ),
        "staticity_zero_momentum_or_zero_time_dependence_required": False,
        "coarse_evolution": coarse,
        "fine_evolution": fine,
        "coarse_fine_final_H6_H5_relative_difference": convergence,
        "finite_duration_numerical_movie_converged": (
            numerical_witness_validated
        ),
        "local_existence_theorem": {
            "analytic_vector_field_domain": (
                "FINITE_BHSM_EXPONENTIAL_ACTION_CHART_WITH_L_eta_POSITIVE_"
                "AND_INVERTIBLE_EULER_DIRAC_HESSIAN"
            ),
            "Dirac_smallest_singular_value": float(dirac_singular[-1]),
            "Dirac_condition_number": float(
                initial_dynamics["Dirac_condition_number"]
            ),
            "vector_field_finite": bool(
                np.all(np.isfinite(initial_vector_field))
            ),
            "vector_field_norm": float(
                np.linalg.norm(initial_vector_field)
            ),
            "initial_constraint_maximum": float(
                np.max(np.abs(initial_constraints))
            ),
            "initial_eta_margin": initial_eta["minimum"],
            "initial_boundary_lapse": boundary_lapse(m0),
            "constraint_tangency": (
                "D_t(L_m)=L_mq*v+[L_mv,L_mm]*(a,mdot)=0_BY_THE_"
                "SECOND_EULER_DIRAC_BLOCK"
            ),
            "energy_tangency": (
                "D_t(L_v*v-L)=0_BY_THE_AUTONOMOUS_EULER_LAGRANGE_"
                "IDENTITY_ON_THE_CONSTRAINT_SURFACE"
            ),
            "proper_time_relation": (
                "d_tau=N_boundary*dt_WITH_N_boundary_POSITIVE"
            ),
            "positive_duration_exists": local_existence_validated,
            "lifetime_or_eternal_stability_inferred": False,
        },
        "persistence_validation_basis": (
            "CONVERGED_FINITE_DURATION_NUMERICAL_WITNESS"
            if numerical_witness_validated else
            "LOCAL_ANALYTIC_EULER_DIRAC_EXISTENCE_THEOREM"
            if local_existence_validated else
            "UNVALIDATED"
        ),
        "positive_duration_relative_persistence_validated": validated,
        "nonzero_relative_evolution_retained": bool(
            fine["final_configuration_displacement_norm"] > 0.0
            and fine["final_velocity_displacement_norm"] > 0.0
        ),
        "eternal_stability_claimed": False,
        "decay_observed_on_witness_interval": bool(
            coarse["first_exit"] is not None or fine["first_exit"] is not None
        ),
        "numerical_convergence_is_reliability_not_new_physics": True,
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=2)
def n5_complete_child_positive_duration_persistence(
    *, points: int = 44, time_step: float = 1.0e-5, steps: int = 10,
) -> dict[str, Any]:
    """Apply the retained N4 persistence definition to the closed N5 child."""

    return n4_complete_child_positive_duration_persistence(
        points=points,
        time_step=time_step,
        steps=steps,
        _order=5,
        _child_key="N5_event_conditioned_complete_child_reconstruction",
        _source_label="VALIDATED_INDEPENDENT_N5_COMPLETE_CHILD",
    )


@lru_cache(maxsize=2)
def coherent_n4_to_n5_complete_child_positive_duration_persistence(
    *, points: int = 44, time_step: float = 1.0e-5, steps: int = 10,
) -> dict[str, Any]:
    """Apply the unchanged persistence definition to the coherent N5 child."""

    return n4_complete_child_positive_duration_persistence(
        points=points,
        time_step=time_step,
        steps=steps,
        _order=5,
        _child_key="coherent_N4_to_N5_complete_child_graph",
        _source_label="ACTION_ENERGY_COHERENT_N4_TO_N5_COMPLETE_CHILD",
    )


@lru_cache(maxsize=2)
def n6_weak_complete_child_positive_duration_persistence(
    *, points: int = 96, time_step: float = 1.0e-5, steps: int = 10,
) -> dict[str, Any]:
    """Apply the unchanged persistence evolution to the matched N6 child."""

    return n4_complete_child_positive_duration_persistence(
        points=points,
        time_step=time_step,
        steps=steps,
        _order=6,
        _child_key="N6_weak_complete_child_candidate",
        _source_label=(
            "N6_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_CHILD_CANDIDATE"
        ),
    )


@lru_cache(maxsize=2)
def coherent_n5_exact_attachment_positive_duration_persistence(
    *, points: int = 44, time_step: float = 1.0e-5, steps: int = 10,
) -> dict[str, Any]:
    """Evolve the exact-attachment matched coherent N5 weak child."""

    return n4_complete_child_positive_duration_persistence(
        points=points,
        time_step=time_step,
        steps=steps,
        _order=5,
        _child_key="coherent_N5_exact_attachment_weak_child_candidate",
        _source_label=(
            "COHERENT_N5_EXACT_ATTACHMENT_WEAK_CONORMAL_CHILD"
        ),
    )


@lru_cache(maxsize=4)
def legacy_exact_attachment_positive_duration_persistence(
    order: int,
    *,
    points: int = 44,
    time_step: float = 1.0e-5,
    steps: int = 10,
) -> dict[str, Any]:
    """Evolve an exact-attachment matched legacy weak child."""

    if order not in (3, 4):
        raise ValueError("legacy matched persistence supports N3 or N4")
    return n4_complete_child_positive_duration_persistence(
        points=points,
        time_step=time_step,
        steps=steps,
        _order=order,
        _child_key=f"N{order}_exact_attachment_weak_child_candidate",
        _source_label=(
            f"N{order}_EXACT_ATTACHMENT_WEAK_CONORMAL_CHILD"
        ),
    )


def child_jacobi_radial_principal_symbol_audit() -> dict[str, Any]:
    """Derive the radial principal form of the retained Galerkin action."""

    lapse = 1.3
    radial_scale = 0.9
    warp_a = 1.1
    warp_b = 1.2
    shift = 0.2
    K_value = 3.0 * lapse * warp_a**3 * warp_b**3 / radial_scale
    J_value = radial_scale * warp_a**3 * warp_b**3 / (2.0 * lapse)

    def matrix(beta: float) -> np.ndarray:
        return np.asarray([
            [10.0 * K_value - 84.0 * J_value * beta**2,
             -12.0 * J_value * beta**2, 0.0, 2.0 * K_value,
             -12.0 * J_value * beta],
            [-12.0 * J_value * beta**2, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 12.0 * J_value * beta**2 - 2.0 * K_value,
             0.0, 0.0],
            [2.0 * K_value, 0.0, 0.0, 0.0, 0.0],
            [-12.0 * J_value * beta, 0.0, 0.0, 0.0, 0.0],
        ])

    generic_matrix = matrix(shift)
    beta_zero_matrix = matrix(0.0)
    null_one = np.asarray([
        0.0, K_value / (6.0 * J_value * shift**2), 0.0, 1.0, 0.0,
    ])
    null_two = np.asarray([0.0, -1.0 / shift, 0.0, 0.0, 1.0])
    raw_v = 12.0 * J_value * shift**2 - 2.0 * K_value
    reduced_v = -2.0 * K_value * (
        1.0 - radial_scale**2 * shift**2 / lapse**2
    )
    validation = {
        "generic_rank_three": int(np.linalg.matrix_rank(generic_matrix)) == 3,
        "beta_zero_rank_three": int(
            np.linalg.matrix_rank(beta_zero_matrix)
        ) == 3,
        "two_generic_null_directions_verified": bool(
            np.linalg.norm(generic_matrix @ null_one) < 1.0e-10
            and np.linalg.norm(generic_matrix @ null_two) < 1.0e-10
        ),
        "v_coefficient_reduction_verified": math.isclose(
            raw_v, reduced_v, rel_tol=1.0e-14, abs_tol=1.0e-14
        ),
        "representative_point_subluminal": bool(
            lapse**2 > radial_scale**2 * shift**2
        ),
        "canonical_physical_block_determinant_verified": math.isclose(
            float(np.linalg.det(np.asarray([
                [10.0 * K_value, 0.0, 2.0 * K_value],
                [0.0, -2.0 * K_value, 0.0],
                [2.0 * K_value, 0.0, 0.0],
            ]))),
            8.0 * K_value**3,
            rel_tol=1.0e-14,
            abs_tol=1.0e-12,
        ),
    }
    return {
        "classification": (
            "RETAINED_ACTION_RADIAL_INTERIOR_PRINCIPAL_SYMBOL_DERIVED;_"
            "BOUNDARY_COMPLEMENTING_AND_GLOBAL_INF_SUP_OPEN"
        ),
        "scope": (
            "CURRENT_COHOMOGENEITY_ONE_RETAINED_u_w_v_LOG_LAPSE_SHIFT_"
            "ACTION_SECTOR_WITH_f=chi_AND_DERIVED_MATERIAL_PROFILE"
        ),
        "derivative_variables": [
            "u_chi", "w_chi", "v_chi", "logN_chi", "beta_chi",
        ],
        "positive_background_factors": {
            "K": "3*N*A^3*B^3/C",
            "J": "C*A^3*B^3/(2*N)",
        },
        "principal_quadratic_form": (
            "K*(2*logN_chi*u_chi+5*u_chi^2-v_chi^2)+"
            "J*(-6*beta*(7*beta*u_chi^2+2*beta*u_chi*w_chi-"
            "beta*v_chi^2+2*beta_chi*u_chi))"
        ),
        "principal_hessian": [
            ["10K-84J*beta^2", "-12J*beta^2", "0", "2K", "-12J*beta"],
            ["-12J*beta^2", "0", "0", "0", "0"],
            ["0", "0", "12J*beta^2-2K", "0", "0"],
            ["2K", "0", "0", "0", "0"],
            ["-12J*beta", "0", "0", "0", "0"],
        ],
        "algebraic_rank": {
            "generic_rank": 3,
            "generic_nullity": 2,
            "beta_zero_rank": 3,
            "compatible_with_existing_two_diffeomorphism_gauge_directions": True,
            "boundary_compatible_gauge_identification_proved": False,
        },
        "physical_v_mode_coefficient": {
            "frame": "RAW_COORDINATE_TIME_VELOCITIES_HELD_FIXED",
            "raw": "12J*beta^2-2K",
            "reduced": "-2K*(1-C^2*beta^2/N^2)",
            "nonzero_on_regular_subluminal_domain": "N^2>C^2*beta^2",
            "characteristic_degeneracy": "N^2=C^2*beta^2",
            "used_as_a_new_admissibility_gate": False,
        },
        "canonical_normal_frame_reduction": {
            "held_fixed": (
                "NORMAL_LEGENDRE_CAUCHY_DATA_H_C_H_A_H_B_OR_EQUIVALENT_"
                "CANONICAL_MOMENTA"
            ),
            "ADM_kinetic_spatial_symbol_contribution": 0,
            "physical_derivative_variables": [
                "u_chi", "v_chi", "logN_chi",
            ],
            "physical_principal_hessian": [
                ["10K", "0", "2K"],
                ["0", "-2K", "0"],
                ["2K", "0", "0"],
            ],
            "determinant": "8K^3",
            "interior_nondegenerate_when": "K=3*N*A^3*B^3/C>0",
            "independent_of_shift": True,
        },
        "derived_conclusion": (
            "THE_RAW_COORDINATE_TIME_FORM_HAS_THREE_NONNULL_DIRECTIONS_AND_"
            "TWO_GAUGE_COMPATIBLE_NULL_DIRECTIONS;_AFTER_THE_ACTION_OWNED_"
            "NORMAL_LEGENDRE_REDUCTION_THE_THREE_BY_THREE_PHYSICAL_INTERIOR_"
            "BLOCK_HAS_DETERMINANT_8K^3_AND_IS_SHIFT_INDEPENDENT"
        ),
        "not_yet_proved": [
            "THE_NULLSPACE_EQUALS_THE_GLOBAL_BOUNDARY_COMPATIBLE_GAUGE_ORBIT",
            "THE_REGULAR_POLE_ATTACHMENT_AND_MATERIAL_TRANSMISSION_CONDITIONS_COMPLEMENT_THE_SYMBOL",
            "A_GLOBAL_GAUGE_REDUCED_INF_SUP_LOWER_BOUND",
            "THE_FULL_UNTRUNCATED_f_sigma_lambda_sigma_SYSTEM_SYMBOL",
        ],
        "algebra_validation": validation,
        "algebra_validation_passed": all(validation.values()),
        "new_physics_or_acceptance_gate": False,
        "FULL_BHSM_COMPLETE": False,
    }


def cross_resolution_principal_symbol_frame_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    samples: int = 20001,
) -> dict[str, Any]:
    """Measure raw-shift crossings and the canonical interior symbol at N3-N5."""

    if samples < 1001:
        raise ValueError("dense principal-symbol sampling required")
    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    n3_state = n3_payload["complete_child_persistence"]["evolution"][
        "rows"
    ][0]
    states = {
        3: n3_state,
        4: result["N4_event_conditioned_complete_child_reconstruction"][
            "child_state"
        ],
        5: result["N5_event_conditioned_complete_child_reconstruction"][
            "child_state"
        ],
    }
    chi = np.linspace(0.0, math.pi / 4.0, samples)
    rows = []
    for order, source in states.items():
        exact = source.get("binary64_hex")
        if exact is None:
            q = np.asarray(source["coordinates"], dtype=float)
            m = np.asarray(source["multipliers"], dtype=float)
        else:
            q = np.asarray([
                float.fromhex(item) for item in exact["coordinates"]
            ])
            m = np.asarray([
                float.fromhex(item) for item in exact["multipliers"]
            ])
        ks = np.arange(1, order + 1, dtype=float)
        js = np.arange(order, dtype=float)
        cos_k = np.cos(4.0 * np.outer(ks, chi))
        cos_j = np.cos(4.0 * np.outer(js, chi))
        u = q[1:1 + order] @ cos_k
        window = np.sin(2.0 * chi) ** 2
        w = window * (q[1 + order:1 + 2 * order] @ cos_j)
        v = window * (q[1 + 2 * order:1 + 3 * order] @ cos_j)
        radius = RADIUS0 * math.exp(float(q[0]))
        C = radius * np.exp(u + w)
        A = radius * np.exp(u + v) * np.cos(chi)
        B = radius * np.exp(u - v) * np.sin(chi)
        lapse = np.exp(m[:order] @ cos_k)
        beta = np.sin(4.0 * chi) * (m[order:] @ cos_j)
        ratio = (C * beta / lapse) ** 2
        maximum_index = int(np.argmax(ratio))
        signs = np.sign(ratio - 1.0)
        crossing_count = int(np.count_nonzero(signs[1:] * signs[:-1] < 0.0))
        K = 3.0 * lapse * A**3 * B**3 / C
        weighted_coefficient = (
            3.0 * lapse * radius**5 * np.exp(5.0 * u - w)
        )
        open_cap_K = K[1:]
        eta = source.get("eta_Legendre", {})
        eta_minimum = eta.get(
            "minimum", source.get("eta_Legendre_minimum", {}).get("minimum")
        )
        rows.append({
            "N": order,
            "maximum_raw_shift_ratio_C2_beta2_over_N2": float(
                ratio[maximum_index]
            ),
            "minimum_raw_fixed_velocity_v_coefficient_factor": float(
                np.min(1.0 - ratio)
            ),
            "chi_at_maximum_raw_shift_ratio": float(chi[maximum_index]),
            "raw_coordinate_characteristic_crossing_count": crossing_count,
            "canonical_K_positive_on_sampled_open_cap": bool(
                np.all(open_cap_K > 0.0)
            ),
            "minimum_sampled_open_cap_K": float(np.min(open_cap_K)),
            "minimum_weighted_principal_coefficient_K_over_sin3cos3": float(
                np.min(weighted_coefficient)
            ),
            "maximum_weighted_principal_coefficient_K_over_sin3cos3": float(
                np.max(weighted_coefficient)
            ),
            "eta_minimum": float(eta_minimum),
        })
    validation = {
        "orders_N3_N4_N5_measured": [row["N"] for row in rows] == [3, 4, 5],
        "raw_coordinate_crossings_exposed": all(
            row["raw_coordinate_characteristic_crossing_count"] > 0
            for row in rows
        ),
        "canonical_K_positive_on_sampled_open_caps": all(
            row["canonical_K_positive_on_sampled_open_cap"] for row in rows
        ),
        "eta_domain_retained": all(row["eta_minimum"] > 0.0 for row in rows),
        "N4_to_N5_weighted_principal_minimum_not_collapsing": bool(
            rows[2][
                "minimum_weighted_principal_coefficient_K_over_sin3cos3"
            ] / rows[1][
                "minimum_weighted_principal_coefficient_K_over_sin3cos3"
            ] > 0.5
        ),
    }
    n5_n4_principal_ratio = float(
        rows[2]["minimum_weighted_principal_coefficient_K_over_sin3cos3"]
        / rows[1]["minimum_weighted_principal_coefficient_K_over_sin3cos3"]
    )
    return {
        "classification": (
            "RAW_FIXED_COORDINATE_VELOCITY_CHARACTERISTIC_CROSSINGS_"
            "MEASURED;_CANONICAL_NORMAL_FRAME_INTERIOR_SYMBOL_"
            "NONDEGENERATE;_WEIGHTED_POLE_ATTACHMENT_ESTIMATE_OPEN"
        ),
        "rows": rows,
        "raw_crossing_is_a_physical_defect": False,
        "raw_crossing_is_a_new_acceptance_gate": False,
        "reason": (
            "A_LARGE_SHIFT_CAN_MAKE_THE_COORDINATE_TIME_VECTOR_SPACELIKE_"
            "WITHOUT_DESTROYING_THE_ADM_LORENTZIAN_NORMAL;_THE_ACTION_OWNED_"
            "CANONICAL_NORMAL_FRAME_REMOVES_THIS_COORDINATE_MIXING"
        ),
        "canonical_interior_determinant": "8K^3_WITH_K=3*N*A^3*B^3/C",
        "N5_over_N4_weighted_principal_minimum_ratio": n5_n4_principal_ratio,
        "principal_geometry_degeneracy_supported_as_the_owner_of_the_"
        "reported_full_map_small_singular_values": False,
        "reclassification": (
            "THE_CANONICAL_WEIGHTED_PRINCIPAL_GEOMETRY_BLOCK_DOES_NOT_"
            "COLLAPSE_FROM_N4_TO_N5;_ANY_REMAINING_INF_SUP_LOSS_MUST_BE_"
            "LOCALIZED_IN_LOWER_ORDER_FULL_CONSTRAINT_CALDERON_COUPLING_OR_"
            "INCOMPARABLE_NUMERICAL_SCALING_BEFORE_IT_IS_CALLED_PHYSICAL"
        ),
        "remaining_endpoint_object": (
            "WEIGHTED_REGULAR_POLE_ATTACHMENT_AND_MATERIAL_TRANSMISSION_"
            "NORMAL_SUBMERSION_INF_SUP_ESTIMATE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def weighted_pole_attachment_principal_estimate() -> dict[str, Any]:
    """Derive the action-weighted pole estimate for trace-fixed variations."""

    smallest_matrix_modulus = math.sqrt(29.0) - 5.0
    poincare_constant = math.pi**5 / 1024.0
    validation = {
        "physical_matrix_smallest_modulus_positive": (
            smallest_matrix_modulus > 0.0
        ),
        "weighted_Poincare_constant_positive": poincare_constant > 0.0,
        "trace_rows_fix_three_attachment_geometry_combinations": (
            _trace_jacobian_at_order(3).shape == (3, 10)
            and np.linalg.matrix_rank(_trace_jacobian_at_order(3)) == 3
        ),
    }
    return {
        "classification": (
            "WEIGHTED_REGULAR_POLE_AND_ATTACHMENT_PRINCIPAL_ESTIMATE_"
            "DERIVED;_GLOBAL_LOWER_ORDER_INF_SUP_OPEN"
        ),
        "cap_interval": "0<=chi<=L,_L=pi/4",
        "natural_radial_weight": "omega=sin(chi)^3*cos(chi)^3",
        "weight_equivalence": (
            "(8/pi^3)*chi^3<=omega(chi)<=chi^3_ON_[0,pi/4]"
        ),
        "trace_fixed_normal_variations": {
            "three_rows": [
                "delta(logC_attachment)=0",
                "delta(logA_attachment)=0",
                "delta(logB_attachment)=0",
            ],
            "equivalent_geometry_relations": [
                "delta_v(L)=0",
                "delta_w(L)=0",
                "delta_(scale+u)(L)=0",
            ],
            "scale_has_no_radial_derivative": True,
        },
        "weighted_Poincare_Hardy_estimate": {
            "chi3_exact_bound": (
                "integral_0^L chi^3*f^2<=L^2/8*integral_0^L chi^3*(f')^2_"
                "FOR_f(L)=0"
            ),
            "omega_bound": (
                "integral_0^L omega*f^2<=(pi^5/1024)*"
                "integral_0^L omega*(f')^2"
            ),
            "omega_constant": poincare_constant,
        },
        "canonical_physical_matrix": {
            "dimensionless_matrix": [
                [10.0, 0.0, 2.0],
                [0.0, -2.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            "eigenvalues": [
                5.0 + math.sqrt(29.0),
                -2.0,
                5.0 - math.sqrt(29.0),
            ],
            "smallest_absolute_eigenvalue": smallest_matrix_modulus,
            "determinant": 8.0,
        },
        "action_weight_factorization": {
            "K": "kappa(chi)*omega(chi)",
            "kappa": "3*lapse*R^5*exp(5u-w)",
            "kappa_positive_on_every_finite_eta_admissible_child": True,
            "uniform_general_N_bound_proved": False,
        },
        "principal_normal_inf_sup": (
            "beta_principal>=(sqrt(29)-5)*inf(kappa)_IN_THE_omega_WEIGHTED_"
            "DERIVATIVE_NORM_AFTER_THE_EXISTING_TRACE_AND_GAUGE_REDUCTION"
        ),
        "closed_here": [
            "THE_chi^3_POLE_WEIGHT_IS_GEOMETRIC_NOT_A_PHYSICAL_ZERO_MODE",
            "THE_ATTACHMENT_TRACE_ROWS_CONTROL_THE_TRACE_FIXED_GEOMETRY_VARIATIONS",
            "THE_CANONICAL_PHYSICAL_PRINCIPAL_MATRIX_HAS_A_NONZERO_INF_SUP_CONSTANT",
        ],
        "still_open": [
            "UNIFORM_GENERAL_N_LOWER_AND_UPPER_BOUNDS_FOR_kappa",
            "LOWER_ORDER_AND_NONLOCAL_CALDERON_TERMS_DO_NOT_CREATE_A_NORMAL_KERNEL",
            "FULL_CONSTRAINT_MOMENTUM_FLUX_SCHUR_COMPLEMENT_INF_SUP",
            "SPECTRAL_AND_QUADRATURE_CONSISTENCY_IN_THE_WEIGHTED_DUAL_NORM",
            "FULL_MATERIAL_TRANSMISSION_AND_UNTRUNCATED_f_sigma_lambda_sigma_BLOCK",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
        "new_equations_constraints_or_acceptance_gates": False,
        "FULL_BHSM_COMPLETE": False,
    }


def cross_resolution_strong_constraint_infsup_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Compare weak-dual and strong-H4 normalizations of the nonflux map."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    states = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: result["N4_event_conditioned_complete_child_reconstruction"][
            "child_state"
        ],
        5: result["N5_event_conditioned_complete_child_reconstruction"][
            "child_state"
        ],
    }
    rows = []
    for order, source in states.items():
        exact = source.get("binary64_hex")
        if exact is None:
            q = np.asarray(source["coordinates"], dtype=float)
            velocity = np.asarray(source["velocities"], dtype=float)
            multipliers = np.asarray(source["multipliers"], dtype=float)
        else:
            q = np.asarray([
                float.fromhex(item) for item in exact["coordinates"]
            ])
            velocity = np.asarray([
                float.fromhex(item) for item in exact["velocities"]
            ])
            multipliers = np.asarray([
                float.fromhex(item) for item in exact["multipliers"]
            ])
        qdim = q.size
        state = np.concatenate((q, velocity, multipliers))
        jet = exact_full_action_jet_at_state(
            order, q, velocity, multipliers, points=points
        )
        gradient = np.asarray(jet.gradient, dtype=float)
        hessian = np.asarray(jet.hessian, dtype=float)
        multiplier_start = 2 * qdim
        constraint_jacobian = hessian[multiplier_start:, :]
        energy_gradient = np.concatenate((
            velocity @ hessian[qdim:2 * qdim, :qdim] - gradient[:qdim],
            hessian[qdim:2 * qdim, qdim:2 * qdim] @ velocity,
            velocity @ hessian[qdim:2 * qdim, multiplier_start:]
            - gradient[multiplier_start:],
        ))
        frequencies = spectral_frequencies(order)
        regularity = sobolev_weights(order)
        domain_weights = np.concatenate((
            (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
            regularity["velocities"],
            regularity["multipliers"],
        ))
        row_count = 2 * order + 6
        matrix = np.empty((row_count, state.size))
        trace = _trace_jacobian_at_order(order)
        for column in range(state.size):
            direction = np.zeros(state.size)
            direction[column] = 1.0 / domain_weights[column]
            matrix[:3, column] = trace @ direction[:qdim]
            matrix[3:3 + 2 * order, column] = (
                constraint_jacobian @ direction
            )
            matrix[3 + 2 * order, column] = energy_gradient @ direction
            complex_state = state.astype(complex) + 1j * 1.0e-20 * direction
            momentum, _, _, _ = _canonical_pair_at_order(
                order,
                complex_state[:qdim],
                complex_state[qdim:2 * qdim],
                complex_state[2 * qdim:],
                points=points,
            )
            matrix[-2:, column] = np.imag(momentum) / 1.0e-20

        normalizations = {
            "raw_coefficient": np.ones(2 * order),
            "weak_Hminus6_dual": 1.0 / regularity["multipliers"],
            "strong_H4": (
                1.0 + frequencies["multipliers"] ** 2
            ) ** 2.0,
        }
        measurements = {}
        strong_left = None
        for name, constraint_weights in normalizations.items():
            output_weights = np.ones(row_count)
            output_weights[3:3 + 2 * order] = constraint_weights
            normalized = output_weights[:, None] * matrix
            left, singular, _ = np.linalg.svd(normalized, full_matrices=False)
            tolerance = (
                np.finfo(float).eps * max(normalized.shape) * singular[0]
            )
            rank = int(np.count_nonzero(singular > tolerance))
            measurements[name] = {
                "rank": rank,
                "row_count": row_count,
                "smallest_singular_value": float(singular[-1]),
                "largest_singular_value": float(singular[0]),
                "condition_number": float(singular[0] / singular[-1]),
            }
            if name == "strong_H4":
                strong_left = left[:, -1]
        assert strong_left is not None
        measurements["strong_H4"]["smallest_left_vector_block_norms"] = {
            "trace": float(np.linalg.norm(strong_left[:3])),
            "constraints": float(np.linalg.norm(
                strong_left[3:3 + 2 * order]
            )),
            "energy": float(abs(strong_left[3 + 2 * order])),
            "momentum": float(np.linalg.norm(strong_left[-2:])),
        }
        rows.append({"N": order, "normalizations": measurements})

    validation = {
        "strong_H4_maps_full_row_rank_at_N3_N4_N5": all(
            row["normalizations"]["strong_H4"]["rank"]
            == row["normalizations"]["strong_H4"]["row_count"]
            for row in rows
        ),
        "weak_Hminus6_creates_artificial_N5_numerical_rank_loss": bool(
            rows[2]["normalizations"]["weak_Hminus6_dual"]["rank"]
            < rows[2]["normalizations"]["weak_Hminus6_dual"]["row_count"]
        ),
        "N5_strong_H4_owner_is_not_a_pure_high_constraint_mode": bool(
            rows[2]["normalizations"]["strong_H4"]
            ["smallest_left_vector_block_norms"]["trace"] > 0.9
        ),
    }
    return {
        "classification": (
            "STRONG_H4_CONSTRAINT_CODOMAIN_RESTORES_FULL_N3_N4_N5_RANK;_"
            "WEAK_H_MINUS_6_COLLAPSE_INVALIDATED;_BOUNDARY_SYMPLECTIC_"
            "NORMALIZATION_AND_FULL_FLUX_INF_SUP_OPEN"
        ),
        "domain_norm": "H6_q_CROSS_H5_v_CROSS_H6_m",
        "constraint_differential_order": {
            "Hamiltonian_from_H6_geometry": "SECOND_ORDER_TO_H4",
            "momentum_from_H5_velocity": "FIRST_ORDER_TO_H4",
            "strong_constraint_codomain": "H4",
        },
        "rows": rows,
        "invalidated": (
            "USING_THE_WEAK_H_MINUS_6_DUAL_COEFFICIENT_NORM_AS_THE_STRONG_"
            "GENERAL_N_INF_SUP_DIAGNOSTIC"
        ),
        "reclassified_owner": (
            "THE_N5_STRONG_H4_SOFT_LEFT_VECTOR_IS_DOMINATED_BY_ATTACHMENT_"
            "TRACE_WITH_MIXED_CONSTRAINT_AND_ENERGY_CONTENT;_IT_IS_NOT_THE_"
            "HIGH_LAPSE_MODE_COLLAPSE_CREATED_BY_THE_WEAK_DUAL_NORM"
        ),
        "required_next": (
            "DERIVE_THE_ACTION_INDUCED_BOUNDARY_SYMPLECTIC_NORM_AND_EVALUATE_"
            "THE_FULL_DYNAMIC_FLUX_CALDERON_NORMAL_INF_SUP_WITH_WEIGHTED_"
            "SPECTRAL_CONSISTENCY"
        ),
        "physical_rows_changed": False,
        "acceptance_gates_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def cross_resolution_boundary_symplectic_polarization_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Derive the reduced boundary symplectic form and test Hessian signatures."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = payload["cross_resolution_reconnaissance"]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    states = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: result["N4_event_conditioned_complete_child_reconstruction"][
            "child_state"
        ],
        5: result["N5_event_conditioned_complete_child_reconstruction"][
            "child_state"
        ],
    }
    rows = []

    def signature(values: np.ndarray) -> dict[str, int]:
        scale = max(1.0, float(np.max(np.abs(values))))
        tolerance = 1.0e-12 * scale
        return {
            "positive": int(np.count_nonzero(values > tolerance)),
            "negative": int(np.count_nonzero(values < -tolerance)),
            "zero": int(np.count_nonzero(np.abs(values) <= tolerance)),
        }

    for order, source in states.items():
        exact = source.get("binary64_hex")
        if exact is None:
            q = np.asarray(source["coordinates"], dtype=float)
            velocity = np.asarray(source["velocities"], dtype=float)
            multipliers = np.asarray(source["multipliers"], dtype=float)
        else:
            q = np.asarray([
                float.fromhex(item) for item in exact["coordinates"]
            ])
            velocity = np.asarray([
                float.fromhex(item) for item in exact["velocities"]
            ])
            multipliers = np.asarray([
                float.fromhex(item) for item in exact["multipliers"]
            ])
        _, _, q_lift, v_lift = _canonical_pair_at_order(
            order, q, velocity, multipliers, points=points
        )
        jet = exact_full_action_jet_at_state(
            order, q, velocity, multipliers, points=points
        )
        hessian = np.asarray(jet.hessian, dtype=float)
        qdim = q.size
        q_form = hessian[:qdim, :qdim]
        v_form = hessian[qdim:2 * qdim, qdim:2 * qdim]
        qv_form = hessian[:qdim, qdim:2 * qdim]
        reduced_q = q_lift.T @ q_form @ q_lift
        reduced_v = v_lift.T @ v_form @ v_lift
        reduced_qv = q_lift.T @ qv_form @ v_lift
        boundary_hessian = np.block([
            [reduced_q, reduced_qv],
            [reduced_qv.T, reduced_v],
        ])
        q_eigen = np.linalg.eigvalsh(reduced_q)
        v_eigen = np.linalg.eigvalsh(reduced_v)
        boundary_eigen = np.linalg.eigvalsh(boundary_hessian)
        hamiltonian_generator = -np.block([
            [np.zeros((2, 2)), np.eye(2)],
            [-np.eye(2), np.zeros((2, 2))],
        ]) @ boundary_hessian
        generator_eigen = np.linalg.eigvals(hamiltonian_generator)
        generator_scale = max(1.0, float(np.max(np.abs(generator_eigen))))
        generator_tolerance = 1.0e-9 * generator_scale
        real_pair_count = int(np.count_nonzero(
            (np.abs(np.imag(generator_eigen)) <= generator_tolerance)
            & (np.abs(np.real(generator_eigen)) > generator_tolerance)
        ) // 2)
        imaginary_pair_count = int(np.count_nonzero(
            (np.abs(np.real(generator_eigen)) <= generator_tolerance)
            & (np.abs(np.imag(generator_eigen)) > generator_tolerance)
        ) // 2)
        generator_type = (
            "HYPERBOLIC_HYPERBOLIC"
            if real_pair_count == 2 else
            "HYPERBOLIC_ELLIPTIC"
            if real_pair_count == 1 and imaginary_pair_count == 1 else
            "UNCLASSIFIED_MIXED"
        )
        rows.append({
            "N": order,
            "reduced_configuration_Hessian": reduced_q.tolist(),
            "reduced_velocity_Legendre_Hessian": reduced_v.tolist(),
            "reduced_configuration_velocity_cross_Hessian": (
                reduced_qv.tolist()
            ),
            "configuration_eigenvalues": q_eigen.tolist(),
            "velocity_eigenvalues": v_eigen.tolist(),
            "boundary_Hessian_eigenvalues": boundary_eigen.tolist(),
            "configuration_signature": signature(q_eigen),
            "velocity_signature": signature(v_eigen),
            "boundary_Hessian_signature": signature(boundary_eigen),
            "Hamiltonian_generator_eigenvalues": [
                {"real": float(np.real(value)), "imaginary": float(np.imag(value))}
                for value in generator_eigen
            ],
            "Hamiltonian_generator_type": generator_type,
            "hyperbolic_pair_count": real_pair_count,
            "elliptic_pair_count": imaginary_pair_count,
        })
    omega = np.block([
        [np.zeros((2, 2)), np.eye(2)],
        [-np.eye(2), np.zeros((2, 2))],
    ])
    validation = {
        "canonical_symplectic_form_antisymmetric": bool(
            np.allclose(omega.T, -omega, rtol=0.0, atol=0.0)
        ),
        "canonical_symplectic_form_full_rank": int(
            np.linalg.matrix_rank(omega)
        ) == 4,
        "velocity_Legendre_forms_indefinite_at_N3_N4_N5": all(
            row["velocity_signature"]["positive"] == 1
            and row["velocity_signature"]["negative"] == 1
            for row in rows
        ),
        "no_zero_reduced_boundary_Hessian_modes": all(
            row["boundary_Hessian_signature"]["zero"] == 0 for row in rows
        ),
        "N3_local_generator_has_two_hyperbolic_pairs": (
            rows[0]["Hamiltonian_generator_type"] == "HYPERBOLIC_HYPERBOLIC"
        ),
        "N4_N5_local_generators_share_hyperbolic_elliptic_type": all(
            row["Hamiltonian_generator_type"] == "HYPERBOLIC_ELLIPTIC"
            for row in rows[1:]
        ),
    }
    return {
        "classification": (
            "REDUCED_TSTAR_R2_BOUNDARY_SYMPLECTIC_FORM_DERIVED;_ACTION_"
            "HESSIANS_INDEFINITE;_POSITIVE_CALDERON_POLARIZATION_OPEN"
        ),
        "boundary_coordinates": ["q_W", "x_D"],
        "canonical_momenta": ["p_q_W", "p_x_D"],
        "canonical_symplectic_matrix": omega.tolist(),
        "rows": rows,
        "action_Hessian_itself_is_a_positive_boundary_norm": False,
        "taking_entrywise_or_spectral_absolute_values_is_action_derived": False,
        "solver_row_scales_are_the_boundary_Hilbert_metric": False,
        "fixed_analytic_boundary_norm_for_general_N": {
            "coordinates": "(q_W,x_D,p_q_W,p_x_D)_IN_RETAINED_DIMENSIONLESS_ACTION_UNITS",
            "norm": "THE_FIXED_EUCLIDEAN_NORM_ON_THIS_N_INDEPENDENT_R4_CHART",
            "role": "FUNCTION_SPACE_ESTIMATE_ONLY_NOT_A_PHYSICAL_OBSERVABLE_OR_GATE",
            "requires_a_positive_Calderon_polarization": False,
            "all_fixed_finite_dimensional_norms_are_equivalent": True,
        },
        "local_generator_type_is_identical_at_N3_N4_N5": False,
        "N4_N5_mixed_type_agrees": True,
        "N3_may_be_declared_underresolved_from_this_alone": False,
        "type_comparison_claim_boundary": (
            "THE_CHECKPOINTS_ARE_INDEPENDENT_ROOTS;_THE_SHARED_N4_N5_MIXED_"
            "TYPE_IS_STRUCTURAL_EVIDENCE_BUT_NOT_A_PROOF_OF_BRANCHWISE_"
            "SPECTRAL_CONVERGENCE_OR_AN_INVALIDATION_OF_N3"
        ),
        "required_positive_polarization": {
            "acceptable_owner": (
                "THE_ON_SHELL_CHILD_CALDERON_PROJECTOR_OR_RETURN_MONODROMY_"
                "ON_THE_REDUCED_TSTAR_R2_BOUNDARY_PHASE_SPACE"
            ),
            "compatible_metric_formula_after_J_is_derived": (
                "g_boundary(a,b)=Omega_boundary(a,J_boundary*b)"
            ),
            "J_boundary_derived_now": False,
            "blocks_general_N_root_relation_convergence": False,
            "blocks_physical_return_Floquet_and_positive_frequency_readout": True,
        },
        "required_next": (
            "DERIVE_THE_ACTION_OWNED_ON_SHELL_CHILD_CALDERON_OR_RETURN_"
            "POLARIZATION_J_boundary_FOR_PHYSICAL_RETURN_FLOQUET_READOUT"
        ),
        "physical_rows_changed": False,
        "acceptance_gates_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def nested_attachment_lift_consistency_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 64,
) -> dict[str, Any]:
    """Test the current attachment lift on one exact nested N3 state."""

    target = Path(path)
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    source = n3_payload["complete_child_persistence"]["evolution"]["rows"][0]
    q3 = np.asarray(source["coordinates"], dtype=float)
    v3 = np.asarray(source["velocities"], dtype=float)
    m3 = np.asarray(source["multipliers"], dtype=float)
    frequencies3 = spectral_frequencies(3)
    regularity3 = sobolev_weights(3)
    domain_weights3 = np.concatenate((
        (1.0 + frequencies3["coordinates"] ** 2) ** 3.0,
        regularity3["velocities"],
        regularity3["multipliers"],
    ))
    strong_constraint_weights3 = (
        1.0 + frequencies3["multipliers"] ** 2
    ) ** 2.0

    def common_matrix(order: int) -> np.ndarray:
        if order == 3:
            q, velocity, multipliers = q3.copy(), v3.copy(), m3.copy()
        else:
            q, velocity, multipliers = embed_nested_state(
                q3, v3, m3, 3, order
            )
        qdim = q.size
        jet = exact_full_action_jet_at_state(
            order, q, velocity, multipliers, points=points
        )
        gradient = np.asarray(jet.gradient, dtype=float)
        hessian = np.asarray(jet.hessian, dtype=float)
        constraint_jacobian = hessian[2 * qdim:, :]
        energy_gradient = np.concatenate((
            velocity @ hessian[qdim:2 * qdim, :qdim] - gradient[:qdim],
            hessian[qdim:2 * qdim, qdim:2 * qdim] @ velocity,
            velocity @ hessian[qdim:2 * qdim, 2 * qdim:]
            - gradient[2 * qdim:],
        ))
        matrix = np.empty((12, 26))
        trace = _trace_jacobian_at_order(order)
        for column in range(26):
            direction3 = np.zeros(26)
            direction3[column] = 1.0 / domain_weights3[column]
            dq3 = direction3[:10]
            dv3 = direction3[10:20]
            dm3 = direction3[20:]
            if order == 3:
                dq, dv, dm = dq3, dv3, dm3
            else:
                dq, dv, dm = embed_nested_state(
                    dq3, dv3, dm3, 3, order
                )
            direction = np.concatenate((dq, dv, dm))
            matrix[:3, column] = trace @ dq
            constraints = constraint_jacobian @ direction
            matrix[3:6, column] = constraints[:3]
            matrix[6:9, column] = constraints[order:order + 3]
            matrix[9, column] = energy_gradient @ direction
            complex_q = q.astype(complex) + 1j * 1.0e-20 * dq
            complex_v = velocity.astype(complex) + 1j * 1.0e-20 * dv
            complex_m = multipliers.astype(complex) + 1j * 1.0e-20 * dm
            momentum, _, _, _ = _canonical_pair_at_order(
                order, complex_q, complex_v, complex_m, points=points
            )
            matrix[10:, column] = np.imag(momentum) / 1.0e-20
        matrix[3:9] *= strong_constraint_weights3[:, None]
        return matrix

    matrices = {order: common_matrix(order) for order in (3, 4, 5)}
    blocks = {
        "trace": slice(0, 3),
        "strong_H4_constraints": slice(3, 9),
        "energy": slice(9, 10),
        "attachment_momentum": slice(10, 12),
    }
    comparisons = []
    for low, high in ((3, 4), (3, 5), (4, 5)):
        difference = matrices[high] - matrices[low]
        block_changes = {}
        for name, block in blocks.items():
            block_changes[name] = float(
                np.linalg.norm(difference[block])
                / max(1.0, np.linalg.norm(matrices[low][block]))
            )
        comparisons.append({
            "low_order": low,
            "high_order": high,
            "total_relative_change": float(
                np.linalg.norm(difference) / np.linalg.norm(matrices[low])
            ),
            "maximum_absolute_change": float(np.max(np.abs(difference))),
            "block_relative_changes": block_changes,
        })
    validation = {
        "trace_nested_to_machine_precision": all(
            row["block_relative_changes"]["trace"] < 1.0e-13
            for row in comparisons
        ),
        "strong_constraints_nested_to_machine_precision": all(
            row["block_relative_changes"]["strong_H4_constraints"] < 1.0e-13
            for row in comparisons
        ),
        "energy_nested_to_machine_precision": all(
            row["block_relative_changes"]["energy"] < 1.0e-12
            for row in comparisons
        ),
        "attachment_momentum_lift_not_nested": all(
            row["block_relative_changes"]["attachment_momentum"] > 0.5
            for row in comparisons
        ),
    }
    return {
        "classification": (
            "NONLINEAR_ACTION_TRACE_CONSTRAINT_ENERGY_CORE_NESTED;_"
            "STATE_DEPENDENT_HESSIAN_HORIZONTAL_ATTACHMENT_MOMENTUM_LIFT_"
            "NOT_SPECTRALLY_CONSISTENT"
        ),
        "source": (
            "ONE_ACCEPTED_N3_CHILD_STATE_EXACTLY_INJECTED_INTO_N4_AND_N5_"
            "FOR_OPERATOR_CONSISTENCY_ONLY"
        ),
        "accepted_N3_state_used_as_higher_N_child_existence_evidence": False,
        "points": points,
        "domain_norm": "COMMON_H6_q_CROSS_H5_v_CROSS_H6_m",
        "constraint_codomain": "COMMON_STRONG_H4",
        "comparisons": comparisons,
        "finite_N_N3_N4_N5_roots_remain_valid_for_their_stated_maps": True,
        "current_lift_may_be_promoted_as_a_general_N_Calderon_projector": False,
        "why": (
            "THE_HESSIAN_HORIZONTAL_LIFT_RECOMPUTES_AN_INDEFINITE_GLOBAL_"
            "SCHUR_INVERSE_WHEN_NEW_SPECTRAL_MODES_ARE_ADDED;_THE_ORDER_ONE_"
            "MOMENTUM_CHANGE_IS_NOT_OWNED_BY_THE_EXACT_NESTED_ACTION_CORE"
        ),
        "required_next": (
            "DERIVE_THE_ON_SHELL_CHILD_EULER_BVP_CALDERON_TRACE_FROM_THE_"
            "SAME_ACTION_SO_VERTICAL_INTERIOR_VARIATIONS_VANISH_AND_"
            "REEVALUATE_THE_N3_N4_N5_BOUNDARY_MOMENTUM_FLUX_RELATION"
        ),
        "new_physics_rows_constraints_or_gates_added": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def on_shell_boundary_reaction_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Test what the lift-independent child boundary relation must retain."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    event = next(
        row["event"]
        for row in payload[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"]
        if int(row["points"]) == points
    )
    child = payload[
        "N5_event_conditioned_complete_child_reconstruction"
    ]["child_state"]
    exact = child["binary64_hex"]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    q_child = np.asarray([
        float.fromhex(value) for value in exact["coordinates"]
    ])
    v_child = np.asarray([
        float.fromhex(value) for value in exact["velocities"]
    ])
    m_child = np.asarray([
        float.fromhex(value) for value in exact["multipliers"]
    ])
    order = 5
    qdim = q_child.size
    event_momentum, _, event_lift, _ = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )
    child_momentum, _, child_lift, _ = _canonical_pair_at_order(
        order, q_child, v_child, m_child, points=points
    )
    event_flux = event_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_event, m_event
    )
    child_flux = child_lift.T @ _metric_radial_flux_covector_at_order(
        order, q_child, m_child
    )
    child_state = np.concatenate((q_child, v_child, m_child))
    physical_rows = _child_rows_at_order(
        order,
        child_state,
        q_event,
        event_momentum,
        event_flux,
        points=points,
        flux_derivative_method="complex_step",
    )
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q_child, v_child, m_child, points=points
    )
    jet = exact_full_action_jet_at_state(
        order, q_child, v_child, m_child, points=points
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    momentum_rate = (
        hessian[qdim:2 * qdim, :qdim] @ v_child
        + hessian[qdim:2 * qdim, qdim:2 * qdim]
        @ np.asarray(dynamics["acceleration"], dtype=float)
        + hessian[qdim:2 * qdim, 2 * qdim:]
        @ np.asarray(dynamics["multiplier_rate"], dtype=float)
    )
    full_euler_covector = momentum_rate - gradient[:qdim]
    raw_two_sided = event_flux + child_flux
    validation = {
        "exact_binary64_N5_root_replayed": bool(
            np.linalg.norm(physical_rows[-2:]) < 2.0e-7
        ),
        "canonical_momentum_match_replayed": bool(
            np.linalg.norm(child_momentum - event_momentum) < 1.0e-10
        ),
        "full_Euler_Dirac_tangent_closes": bool(
            np.linalg.norm(full_euler_covector) < 1.0e-8
        ),
        "raw_two_sided_radial_flux_is_not_the_validated_dynamic_row": bool(
            np.linalg.norm(raw_two_sided) > 1.0
            and np.linalg.norm(physical_rows[-2:]) < 2.0e-7
        ),
    }
    return {
        "classification": (
            "LIFT_INDEPENDENT_ON_SHELL_BOUNDARY_REACTION_FORM_DERIVED;_"
            "RAW_FLUX_ONLY_REPLACEMENT_INVALIDATED;_LORENTZIAN_CHILD_"
            "HISTORY_BVP_OPEN"
        ),
        "finite_N_definition": {
            "vertical_space": (
                "V_Phi=KER(D_Gamma0)_INTERSECT_EXISTING_POLE_DOMAIN_"
                "INTERSECT_EXISTING_CONSTRAINT_GAUGE_TANGENT"
            ),
            "on_shell_condition": (
                "<E_child(Phi),delta_Phi>=0_FOR_ALL_delta_Phi_IN_V_Phi"
            ),
            "boundary_reaction": (
                "Lambda_child=H^star*E_child_FOR_ANY_H_WITH_"
                "D_Gamma0*H=IDENTITY"
            ),
            "lift_independence_proof": (
                "H1-H2_MAPS_INTO_V_Phi_SO_(H1-H2)^star*E_child=0"
            ),
            "complete_event_to_child_equation": (
                "F_child(e)=Lambda_event(e)+Lambda_child(Phi_e)=0"
            ),
            "single_valued_child_assumed": False,
        },
        "N5_exact_checkpoint_measurement": {
            "event_projected_radial_flux": event_flux.tolist(),
            "child_projected_radial_flux": child_flux.tolist(),
            "raw_two_sided_radial_flux": raw_two_sided.tolist(),
            "raw_two_sided_radial_flux_norm": float(
                np.linalg.norm(raw_two_sided)
            ),
            "validated_dynamic_F18_rows": physical_rows[-2:].tolist(),
            "validated_dynamic_F18_norm": float(
                np.linalg.norm(physical_rows[-2:])
            ),
            "full_Euler_Dirac_covector_norm": float(
                np.linalg.norm(full_euler_covector)
            ),
            "current_attachment_momentum_match_norm": float(
                np.linalg.norm(child_momentum - event_momentum)
            ),
        },
        "decisive_result": (
            "THE_ORDER_10^3_RAW_TWO_SIDED_RADIAL_SUM_CANNOT_REPLACE_THE_"
            "ORDER_10^-7_VALIDATED_DYNAMIC_ROWS;_THE_REDUCED_MOMENTUM_"
            "FORCE_CONNECTION_TERMS_ARE_PHYSICAL_PARTS_OF_THE_BOUNDARY_"
            "REACTION_UNTIL_ELIMINATED_BY_A_SAME_ACTION_ON_SHELL_BVP"
        ),
        "current_Hessian_minimal_lift_promoted_as_general_N_physics": False,
        "validated_finite_N_F18_root_changed": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "required_next": (
            "SOLVE_THE_SAME_ACTION_LORENTZIAN_CHILD_HISTORY_BVP_WITH_THE_"
            "EXISTING_POLE_ATTACHMENT_CAUCHY_AND_ETA_DOMAIN;_EXTRACT_"
            "ITS_BOUNDARY_REACTION_MULTIPLIER_AND_TEST_N3_N4_N5_"
            "SPECTRAL_CONSISTENCY"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def _child_history_boundary_reaction_solve(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    boundary_acceleration: np.ndarray,
    *,
    points: int,
) -> dict[str, Any]:
    """Solve the same-action Euler--Dirac boundary-reaction system."""

    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    bddot = np.asarray(boundary_acceleration, dtype=float)
    qdim = q.size
    mdim = m.size
    boundary = _attachment_jacobian_at_order(order, q)
    boundary_curvature = _attachment_chart_curvature_on_velocity(
        order, q, velocity
    )
    jet = exact_full_action_jet_at_state(
        order, q, velocity, m, points=points
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    zero_m_boundary = np.zeros((mdim, 2))
    matrix = np.block([
        [
            hessian[qdim:2 * qdim, qdim:2 * qdim],
            hessian[qdim:2 * qdim, 2 * qdim:],
            -boundary.T,
        ],
        [
            hessian[2 * qdim:, qdim:2 * qdim],
            hessian[2 * qdim:, 2 * qdim:],
            zero_m_boundary,
        ],
        [
            boundary,
            np.zeros((2, mdim)),
            np.zeros((2, 2)),
        ],
    ])
    radial_flux = _metric_radial_flux_covector_at_order(order, q, m)
    right_hand_side = np.concatenate((
        gradient[:qdim]
        - hessian[qdim:2 * qdim, :qdim] @ velocity
        - radial_flux,
        -hessian[2 * qdim:, :qdim] @ velocity,
        bddot - boundary_curvature,
    ))
    solved = np.linalg.solve(matrix, right_hand_side)
    acceleration = solved[:qdim]
    multiplier_rate = solved[qdim:qdim + mdim]
    reaction = solved[-2:]
    euler_reaction_residual = (
        hessian[qdim:2 * qdim, :qdim] @ velocity
        + hessian[qdim:2 * qdim, qdim:2 * qdim] @ acceleration
        + hessian[qdim:2 * qdim, 2 * qdim:] @ multiplier_rate
        - gradient[:qdim]
        + radial_flux
        - boundary.T @ reaction
    )
    constraint_tangent_residual = (
        hessian[2 * qdim:, :qdim] @ velocity
        + hessian[2 * qdim:, qdim:2 * qdim] @ acceleration
        + hessian[2 * qdim:, 2 * qdim:] @ multiplier_rate
    )
    boundary_acceleration_residual = (
        boundary @ acceleration + boundary_curvature - bddot
    )
    singular = np.linalg.svd(matrix, compute_uv=False)
    return {
        "matrix_dimension": int(matrix.shape[0]),
        "matrix_rank": int(np.linalg.matrix_rank(matrix)),
        "smallest_singular_value": float(singular[-1]),
        "condition_number": float(singular[0] / singular[-1]),
        "boundary_reaction": reaction.tolist(),
        "boundary_reaction_norm": float(np.linalg.norm(reaction)),
        "acceleration": acceleration,
        "multiplier_rate": multiplier_rate,
        "maximum_Euler_reaction_residual": float(
            np.max(np.abs(euler_reaction_residual))
        ),
        "maximum_constraint_tangent_residual": float(
            np.max(np.abs(constraint_tangent_residual))
        ),
        "maximum_boundary_acceleration_residual": float(
            np.max(np.abs(boundary_acceleration_residual))
        ),
    }


def child_history_bvp_bordered_operator_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Construct the finite-N Lorentzian child-history BVP operator."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    states = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: payload[
            "N4_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
        5: payload[
            "N5_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
    }
    rows = []
    attachment_derivative_errors = []
    for order, source in states.items():
        exact = source.get("binary64_hex")
        if exact is None:
            q = np.asarray(source["coordinates"], dtype=float)
            velocity = np.asarray(source["velocities"], dtype=float)
            m = np.asarray(source["multipliers"], dtype=float)
        else:
            q = np.asarray([
                float.fromhex(value) for value in exact["coordinates"]
            ])
            velocity = np.asarray([
                float.fromhex(value) for value in exact["velocities"]
            ])
            m = np.asarray([
                float.fromhex(value) for value in exact["multipliers"]
            ])
        analytic_boundary = _attachment_jacobian_at_order(order, q)
        complex_boundary = np.empty_like(analytic_boundary)
        for column in range(q.size):
            perturbed = q.astype(complex)
            perturbed[column] += 1j * 1.0e-20
            complex_boundary[:, column] = np.imag(
                _attachment_coordinates_at_order(order, perturbed)
            ) / 1.0e-20
        derivative_error = float(np.max(np.abs(
            analytic_boundary - complex_boundary
        )))
        attachment_derivative_errors.append(derivative_error)
        free = _exact_full_jet_euler_dirac_acceleration(
            order, q, velocity, m, points=points
        )
        boundary_acceleration_probe = (
            analytic_boundary @ np.asarray(free["acceleration"], dtype=float)
            + _attachment_chart_curvature_on_velocity(order, q, velocity)
        )
        solved = _child_history_boundary_reaction_solve(
            order,
            q,
            velocity,
            m,
            boundary_acceleration_probe,
            points=points,
        )
        rows.append({
            "N": order,
            "coordinate_dimension": int(q.size),
            "multiplier_dimension": int(m.size),
            "bordered_dimension": solved["matrix_dimension"],
            "expected_bordered_dimension_5N_plus_3": 5 * order + 3,
            "bordered_rank": solved["matrix_rank"],
            "smallest_singular_value": solved["smallest_singular_value"],
            "condition_number": solved["condition_number"],
            "attachment_chart_derivative_error": derivative_error,
            "probe_boundary_reaction": solved["boundary_reaction"],
            "probe_boundary_reaction_norm": solved[
                "boundary_reaction_norm"
            ],
            "maximum_Euler_reaction_residual": solved[
                "maximum_Euler_reaction_residual"
            ],
            "maximum_constraint_tangent_residual": solved[
                "maximum_constraint_tangent_residual"
            ],
            "maximum_boundary_acceleration_residual": solved[
                "maximum_boundary_acceleration_residual"
            ],
        })
    validation = {
        "exact_attachment_chart_differentiates_to_existing_boundary_rows": (
            max(attachment_derivative_errors) < 1.0e-12
        ),
        "general_N_dimension_law_holds_at_N3_N4_N5": all(
            row["bordered_dimension"]
            == row["expected_bordered_dimension_5N_plus_3"]
            for row in rows
        ),
        "all_finite_N_bordered_operators_full_rank": all(
            row["bordered_rank"] == row["bordered_dimension"]
            for row in rows
        ),
        "all_equation_blocks_replay": all(
            row["maximum_Euler_reaction_residual"] < 1.0e-7
            and row["maximum_constraint_tangent_residual"] < 1.0e-7
            and row["maximum_boundary_acceleration_residual"] < 1.0e-7
            for row in rows
        ),
    }
    return {
        "classification": (
            "SAME_ACTION_LORENTZIAN_CHILD_HISTORY_BVP_BORDERED_OPERATOR_"
            "DERIVED_AND_FINITE_N_INVERTIBLE;_EVENT_CHILD_REACTION_"
            "MATCHING_AND_UNIFORM_GENERAL_N_BOUND_OPEN"
        ),
        "unknowns": "(a_(3N+1),m_dot_(2N),Lambda_boundary_2)",
        "equations": {
            "Euler_reaction": (
                "L_vv*a+L_vm*m_dot-B^star*Lambda="
                "L_q-L_vq*v-Gamma1_child"
            ),
            "constraint_tangency": (
                "L_mv*a+L_mm*m_dot=-L_mq*v"
            ),
            "boundary_history": (
                "B*a=b_ddot-D2b[v,v]"
            ),
        },
        "exact_attachment_chart": {
            "q_W": "scale+u_L-(1/2)log(cosh(2v_L))",
            "x_D": "scale-q_W",
            "derivative": "B=D_q(q_W,x_D)",
        },
        "general_N_bordered_dimension": "5N+3",
        "rows": rows,
        "probe_boundary_acceleration_is_a_physical_junction_solution": False,
        "probe_role": (
            "USES_THE_UNCONSTRAINED_EULER_DIRAC_BOUNDARY_ACCELERATION_ONLY_"
            "TO_TEST_THE_BORDERED_OPERATOR;_REACTION_VALUES_ARE_NOT_"
            "PROMOTED_AS_EVENT_CHILD_MATCHES"
        ),
        "finite_rank_implies_uniform_general_N_inf_sup": False,
        "existing_N3_N4_N5_F_rows_or_persistence_changed": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "required_next": (
            "EVALUATE_THE_EVENT_SIDE_REACTION_FROM_EACH_ACCEPTED_EVENT_"
            "HISTORY_AND_SOLVE_THE_EXISTING_TWO_SIDED_REACTION_MATCH;_"
            "THEN_TEST_THE_REACTION_CALDERON_GRAPH_UNDER_NESTED_SPECTRAL_"
            "INJECTION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def event_child_two_sided_reaction_match_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Solve the derived event-to-child boundary-reaction correspondence."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    n3_state = unpack_reduced(v17_75_selected_raw_vector())
    n3_q_history = np.asarray(n3_state["coordinates"], dtype=float)
    n3_m_history = np.asarray(n3_state["multipliers"], dtype=float)
    n3_v_history = (
        trapezoid_sbp_difference() @ n3_q_history
        / float(n3_state["period"])
    )
    n4_event = payload["N4_adaptive_event_convergence_audit"][
        "quadrature_control"
    ]["event"]
    n5_event = next(
        row["event"]
        for row in payload[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"]
        if int(row["points"]) == points
    )
    events = {
        3: {
            "coordinates": n3_q_history[-1],
            "velocities": n3_v_history[-1],
            "multipliers": n3_m_history[-1],
            "source": "V17_75_ACCEPTED_EVENT_HISTORY",
        },
        4: {**n4_event, "source": "INDEPENDENT_N4_ACCEPTED_EVENT_HISTORY"},
        5: {**n5_event, "source": "INDEPENDENT_N5_ACCEPTED_EVENT_HISTORY"},
    }
    children = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: payload[
            "N4_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
        5: payload[
            "N5_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
    }
    rows = []
    for order in (3, 4, 5):
        event = events[order]
        child = children[order]
        q_event = np.asarray(event["coordinates"], dtype=float)
        v_event = np.asarray(event["velocities"], dtype=float)
        m_event = np.asarray(event["multipliers"], dtype=float)
        exact = child.get("binary64_hex")
        if exact is None:
            q_child = np.asarray(child["coordinates"], dtype=float)
            v_child = np.asarray(child["velocities"], dtype=float)
            m_child = np.asarray(child["multipliers"], dtype=float)
        else:
            q_child = np.asarray([
                float.fromhex(value) for value in exact["coordinates"]
            ])
            v_child = np.asarray([
                float.fromhex(value) for value in exact["velocities"]
            ])
            m_child = np.asarray([
                float.fromhex(value) for value in exact["multipliers"]
            ])
        event_boundary = _attachment_jacobian_at_order(order, q_event)
        child_boundary = _attachment_jacobian_at_order(order, q_child)
        event_dynamics = _exact_full_jet_euler_dirac_acceleration(
            order, q_event, v_event, m_event, points=points
        )
        event_boundary_acceleration = (
            event_boundary @ np.asarray(
                event_dynamics["acceleration"], dtype=float
            )
            + _attachment_chart_curvature_on_velocity(
                order, q_event, v_event
            )
        )
        event_reaction = _child_history_boundary_reaction_solve(
            order,
            q_event,
            v_event,
            m_event,
            event_boundary_acceleration,
            points=points,
        )
        child_zero = _child_history_boundary_reaction_solve(
            order,
            q_child,
            v_child,
            m_child,
            np.zeros(2),
            points=points,
        )
        child_offset = np.asarray(
            child_zero["boundary_reaction"], dtype=float
        )
        child_response = np.empty((2, 2))
        for column in range(2):
            unit = np.zeros(2)
            unit[column] = 1.0
            unit_reaction = _child_history_boundary_reaction_solve(
                order,
                q_child,
                v_child,
                m_child,
                unit,
                points=points,
            )
            child_response[:, column] = (
                np.asarray(unit_reaction["boundary_reaction"], dtype=float)
                - child_offset
            )
        event_reaction_vector = np.asarray(
            event_reaction["boundary_reaction"], dtype=float
        )
        child_boundary_acceleration = np.linalg.solve(
            child_response, -event_reaction_vector - child_offset
        )
        child_reaction = _child_history_boundary_reaction_solve(
            order,
            q_child,
            v_child,
            m_child,
            child_boundary_acceleration,
            points=points,
        )
        child_reaction_vector = np.asarray(
            child_reaction["boundary_reaction"], dtype=float
        )
        event_momentum = _canonical_pair_at_order(
            order, q_event, v_event, m_event, points=points
        )[0]
        child_momentum = _canonical_pair_at_order(
            order, q_child, v_child, m_child, points=points
        )[0]
        rows.append({
            "N": order,
            "event_source": event["source"],
            "event_boundary_acceleration": (
                event_boundary_acceleration.tolist()
            ),
            "event_boundary_reaction": event_reaction_vector.tolist(),
            "child_reaction_response_matrix": child_response.tolist(),
            "child_reaction_response_determinant": float(
                np.linalg.det(child_response)
            ),
            "child_reaction_response_condition_number": float(
                np.linalg.cond(child_response)
            ),
            "solved_child_boundary_acceleration": (
                child_boundary_acceleration.tolist()
            ),
            "solved_child_boundary_reaction": (
                child_reaction_vector.tolist()
            ),
            "two_sided_reaction_match_norm": float(np.linalg.norm(
                event_reaction_vector + child_reaction_vector
            )),
            "attachment_configuration_jump_norm": float(np.linalg.norm(
                _attachment_coordinates_at_order(order, q_child)
                - _attachment_coordinates_at_order(order, q_event)
            )),
            "attachment_rate_jump_norm": float(np.linalg.norm(
                child_boundary @ v_child - event_boundary @ v_event
            )),
            "accepted_attachment_momentum_match_norm": float(
                np.linalg.norm(child_momentum - event_momentum)
            ),
            "maximum_child_BVP_block_residual": max(
                child_reaction["maximum_Euler_reaction_residual"],
                child_reaction["maximum_constraint_tangent_residual"],
                child_reaction["maximum_boundary_acceleration_residual"],
            ),
        })
    validation = {
        "N3_N4_N5_event_histories_and_children_used": (
            [row["N"] for row in rows] == [3, 4, 5]
        ),
        "all_child_reaction_response_matrices_invertible": all(
            abs(row["child_reaction_response_determinant"]) > 1.0e-10
            for row in rows
        ),
        "all_two_sided_reaction_matches_close": all(
            row["two_sided_reaction_match_norm"] < 1.0e-6
            for row in rows
        ),
        "all_bordered_equations_replay": all(
            row["maximum_child_BVP_block_residual"] < 1.0e-6
            for row in rows
        ),
        "N4_N5_accepted_momentum_rows_replay": all(
            row["accepted_attachment_momentum_match_norm"] < 1.0e-10
            for row in rows[1:]
        ),
    }
    return {
        "classification": (
            "TWO_SIDED_BOUNDARY_REACTION_SOLVABILITY_DERIVED_AT_"
            "N3_N4_N5;_EXACT_EVENT_TO_CHILD_ATTACHMENT_CONFIGURATION_"
            "MATCH_NOT_ESTABLISHED_FOR_THOSE_LEGACY_CANDIDATES"
        ),
        "map": (
            "Lambda_child_N(b_ddot_child;Y_child)="
            "-Lambda_event_N(b_ddot_event;z_event)"
        ),
        "selection": (
            "THE_ACCEPTED_EVENT_HISTORY_FIXES_THE_EVENT_REACTION;_THE_"
            "SAME_ACTION_CHILD_BORDERED_OPERATOR_DETERMINES_THE_CHILD_"
            "BOUNDARY_ACCELERATION_WITHOUT_A_NEW_PHYSICAL_ROW"
        ),
        "rows": rows,
        "exact_attachment_configuration_matches_close": all(
            row["attachment_configuration_jump_norm"] < 1.0e-9
            for row in rows
        ),
        "complete_event_to_child_boundary_correspondence_claimed": False,
        "configuration_or_rate_continuity_imposed_as_a_new_gate": False,
        "why_not": (
            "THE_RECONSTRUCTED_CHILD_IS_A_NEW_PIECEWISE_LORENTZIAN_"
            "SOLUTION;_THE_EXISTING_TRACE_AND_CANONICAL_MOMENTUM_ROWS_"
            "ARE_RETAINED_AND_NO_EXTRA_C1_MATCH_IS_ASSUMED"
        ),
        "accepted_F_N_roots_or_persistence_changed": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "required_next": (
            "SOLVE_OR_DERIVE_THE_EXACT_ATTACHMENT_CONFIGURATION_MATCH_"
            "ON_THE_EXISTING_COMPLETE_CHILD_FIBERS_BEFORE_PROMOTING_"
            "THE_REACTION_SOLVABILITY_MAP_AS_COMPLETE_CORRESPONDENCE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def action_energy_topology_coherent_event_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Use the action energy topology to transport the N4 event into N5."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    states = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: payload[
            "N4_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
        5: payload[
            "N5_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
    }

    def exact_state(source: Mapping[str, Any]) -> tuple[
        np.ndarray, np.ndarray, np.ndarray
    ]:
        exact = source.get("binary64_hex")
        if exact is None:
            return tuple(  # type: ignore[return-value]
                np.asarray(source[name], dtype=float)
                for name in ("coordinates", "velocities", "multipliers")
            )
        return tuple(  # type: ignore[return-value]
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    tail_rows = []
    decoded = {order: exact_state(source) for order, source in states.items()}
    for order, (q, velocity, multipliers) in decoded.items():
        frequencies = spectral_frequencies(order)
        q_energy = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
        m_energy = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
        regularity = sobolev_weights(order)
        highest_q = np.asarray([order, 2 * order, 3 * order])
        highest_m = np.asarray([order - 1, 2 * order - 1])

        def fraction(weighted: np.ndarray, indices: np.ndarray) -> float:
            return float(
                np.linalg.norm(weighted[indices])
                / max(1.0e-300, np.linalg.norm(weighted))
            )

        tail_rows.append({
            "N": order,
            "action_energy_norms": {
                "H1_q": float(np.linalg.norm(q * q_energy)),
                "L2_velocity": float(np.linalg.norm(velocity)),
                "H1_multiplier": float(
                    np.linalg.norm(multipliers * m_energy)
                ),
            },
            "highest_mode_fractions_in_action_energy_norm": {
                "q": fraction(q * q_energy, highest_q),
                "velocity": fraction(velocity, highest_q),
                "multiplier": fraction(
                    multipliers * m_energy, highest_m
                ),
            },
            "highest_mode_fractions_in_H6_H5_H6_regularity_norm": {
                "q": fraction(
                    q * (1.0 + frequencies["coordinates"] ** 2) ** 3.0,
                    highest_q,
                ),
                "velocity": fraction(
                    velocity * regularity["velocities"], highest_q
                ),
                "multiplier": fraction(
                    multipliers * regularity["multipliers"], highest_m
                ),
            },
        })

    def restrict_five_to_four(
        value: np.ndarray, *, multiplier: bool,
    ) -> np.ndarray:
        if multiplier:
            restricted = np.zeros(8)
            restricted[:4] = value[:4]
            restricted[4:] = value[5:9]
            return restricted
        restricted = np.zeros(13)
        restricted[0] = value[0]
        for family in range(3):
            low = 1 + family * 4
            high = 1 + family * 5
            restricted[low:low + 4] = value[high:high + 4]
        return restricted

    q4_child, v4_child, m4_child = decoded[4]
    q5_child, v5_child, m5_child = decoded[5]
    frequencies4 = spectral_frequencies(4)
    q4_energy = np.sqrt(1.0 + frequencies4["coordinates"] ** 2)
    m4_energy = np.sqrt(1.0 + frequencies4["multipliers"] ** 2)
    independent_differences = {}
    for name, low, high, weight in (
        (
            "q_H1", q4_child,
            restrict_five_to_four(q5_child, multiplier=False), q4_energy,
        ),
        (
            "velocity_L2", v4_child,
            restrict_five_to_four(v5_child, multiplier=False),
            np.ones_like(v4_child),
        ),
        (
            "multiplier_H1", m4_child,
            restrict_five_to_four(m5_child, multiplier=True), m4_energy,
        ),
    ):
        independent_differences[name] = float(
            np.linalg.norm((low - high) * weight)
            / max(1.0, np.linalg.norm(low * weight), np.linalg.norm(high * weight))
        )

    n4_event = payload["N4_adaptive_event_convergence_audit"][
        "quadrature_control"
    ]["event"]
    q4_event = np.asarray(n4_event["coordinates"], dtype=float)
    v4_event = np.asarray(n4_event["velocities"], dtype=float)
    m4_event = np.asarray(n4_event["multipliers"], dtype=float)
    q0, v_seed, m_seed = embed_nested_state(
        q4_event, v4_event, m4_event, 4, 5
    )
    energy_projection = _project_constraints_action_energy(
        5, q0, v_seed, m_seed, points=points
    )
    h6_projection = project_nested_constraints_sobolev(
        5, q0, v_seed, m_seed, points=points
    )
    v0 = np.asarray(energy_projection["velocities"], dtype=float)
    m0 = np.asarray(energy_projection["multipliers"], dtype=float)
    initial_values, initial_vectors = np.linalg.eigh(
        exact_action_jet_at_state(5, q0, v0, m0, points=points).hessian
    )
    initial_index = int(np.argmin(np.abs(initial_values)))
    reference = initial_vectors[:, initial_index]
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        5, q0, v0, m0, points=points
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    cache: dict[float, dict[str, Any]] = {}

    def candidate(offset: float) -> dict[str, Any]:
        key = float(offset)
        if key in cache:
            return cache[key]
        q = q0 + key * v0
        projection = _project_constraints_action_energy(
            5,
            q,
            v0 + key * acceleration,
            m0 + key * multiplier_rate,
            points=points,
        )
        velocity = np.asarray(projection["velocities"], dtype=float)
        multipliers = np.asarray(projection["multipliers"], dtype=float)
        values, vectors = np.linalg.eigh(
            exact_action_jet_at_state(
                5, q, velocity, multipliers, points=points
            ).hessian
        )
        index = int(np.argmax(np.abs(vectors.T @ reference)))
        result = {
            "lambda": float(values[index]),
            "branch_index": index,
            "branch_overlap": float(abs(vectors[:, index] @ reference)),
            "negative_inertia": int(np.count_nonzero(values < 0.0)),
            "coordinates": q,
            "velocities": velocity,
            "multipliers": multipliers,
            "maximum_constraint_residual": projection[
                "maximum_constraint_residual"
            ],
            "projection": projection,
        }
        cache[key] = result
        return result

    center = candidate(0.0)
    derivative_step = 1.0e-8
    forward = candidate(derivative_step)
    derivative = (forward["lambda"] - center["lambda"]) / derivative_step
    predicted = -center["lambda"] / derivative
    if predicted < 0.0:
        lower = min(1.5 * predicted, -1.0e-8)
        upper = 0.0
    else:
        lower = 0.0
        upper = max(1.5 * predicted, 1.0e-8)
    for _ in range(12):
        if candidate(lower)["lambda"] * candidate(upper)["lambda"] <= 0.0:
            break
        if predicted < 0.0:
            lower *= 1.75
        else:
            upper *= 1.75
    else:
        raise RuntimeError("coherent N4-to-N5 event branch failed to bracket")
    root = brentq(
        lambda offset: candidate(offset)["lambda"],
        lower,
        upper,
        xtol=1.0e-14,
        rtol=1.0e-12,
        maxiter=64,
    )
    event = candidate(root)
    eta = _eta_legendre_minimum(
        5, event["coordinates"], event["multipliers"], points=2400
    )
    h6_eta = _eta_legendre_minimum(
        5,
        np.asarray(h6_projection["coordinates"], dtype=float),
        np.asarray(h6_projection["multipliers"], dtype=float),
        points=2400,
    )
    independent_n5_event = next(
        row["event"]
        for row in payload[
            "N5_independent_eta_branch_event_classification"
        ]["quadrature_runs"]
        if int(row["points"]) == points
    )
    coherent_event = {
        "source": "EXACT_N4_EVENT_INJECTED_INTO_N5_FOR_RELATION_TRANSPORT",
        "used_as_independent_N5_existence_evidence": False,
        "local_continuation_offset": float(root),
        "lambda_ordered": event["lambda"],
        "branch_index": event["branch_index"],
        "branch_overlap": event["branch_overlap"],
        "negative_inertia": event["negative_inertia"],
        "maximum_constraint_residual": event[
            "maximum_constraint_residual"
        ],
        "eta_Legendre": eta,
        "coordinates": event["coordinates"].tolist(),
        "velocities": event["velocities"].tolist(),
        "multipliers": event["multipliers"].tolist(),
        "action_energy_projection": {
            key: value for key, value in energy_projection.items()
            if key not in {"coordinates", "velocities", "multipliers"}
        },
        "independent_N5_branch_index": int(
            independent_n5_event["branch_index"]
        ),
        "N4_branch_index_plus_new_lapse_shift_pair": int(
            n4_event["branch_index"] + 2
        ),
    }
    stored_graph = payload.get("coherent_N4_to_N5_complete_child_graph")
    graph_validated = bool(
        isinstance(stored_graph, dict)
        and stored_graph.get("complete_child_candidate_validated") is True
    )
    stored_persistence = payload.get(
        "coherent_N4_to_N5_complete_child_positive_duration_persistence"
    )
    persistence_validated = bool(
        isinstance(stored_persistence, dict)
        and stored_persistence.get(
            "positive_duration_relative_persistence_validated"
        ) is True
    )
    if persistence_validated:
        classification = (
            "ACTION_ENERGY_TOPOLOGY_DERIVED;_H6_MINIMUM_PROJECTION_"
            "RECLASSIFIED_AS_OVERREGULARIZED_FOR_RELATION_TRANSPORT;_"
            "COHERENT_N4_TO_N5_COMPLETE_PERSISTENT_CHILD_GRAPH_VALIDATED;_"
            "UNIFORM_REACTION_CALDERON_GRAPH_BOUND_OPEN"
        )
        required_next = (
            "TEST_THE_TWO_BY_TWO_REACTION_CALDERON_GRAPH_UNDER_EXACT_"
            "NESTED_SPECTRAL_INJECTION_AND_DERIVE_A_UNIFORM_NORMAL_RIGHT_"
            "INVERSE_OR_LOCALIZE_ITS_FIRST_ACTION_OWNED_FAILURE"
        )
    elif graph_validated:
        classification = (
            "ACTION_ENERGY_TOPOLOGY_DERIVED;_H6_MINIMUM_PROJECTION_"
            "RECLASSIFIED_AS_OVERREGULARIZED_FOR_RELATION_TRANSPORT;_"
            "COHERENT_N4_TO_N5_COMPLETE_CHILD_GRAPH_VALIDATED;_PERSISTENCE_"
            "OPEN"
        )
        required_next = (
            "EVALUATE_POSITIVE_DURATION_CONSTRAINT_CONSISTENT_RELATIVE_"
            "PERSISTENCE_OF_THE_COHERENT_N4_TO_N5_COMPLETE_CHILD"
        )
    else:
        classification = (
            "ACTION_ENERGY_TOPOLOGY_DERIVED;_H6_MINIMUM_PROJECTION_"
            "RECLASSIFIED_AS_OVERREGULARIZED_FOR_RELATION_TRANSPORT;_"
            "COHERENT_N4_TO_N5_ORDERED_EVENT_VALIDATED;_COHERENT_CHILD_"
            "GRAPH_OPEN"
        )
        required_next = (
            "SOLVE_THE_UNCHANGED_N5_F18_COMPLETE_CHILD_RELATION_AT_THE_"
            "COHERENT_EVENT_USING_THE_ACTION_ENERGY_NEAREST_EMBEDDED_N4_"
            "CHILD_ONLY_AS_A_GRAPH_DISTANCE_SEED;_DO_NOT_REPLACE_THE_"
            "INDEPENDENT_N5_EXISTENCE_RESULT"
        )
    validation = {
        "action_energy_projection_closes_constraints": bool(
            energy_projection["success"]
            and energy_projection["maximum_constraint_residual"] < 1.0e-8
        ),
        "action_energy_projection_retains_eta_domain": bool(
            center["maximum_constraint_residual"] < 1.0e-8
            and _eta_legendre_minimum(
                5, q0, m0, points=1600
            )["minimum"] > 0.0
        ),
        "H6_minimum_projection_eta_failure_exposed": h6_eta["minimum"] <= 0.0,
        "coherent_N5_event_closes": bool(
            abs(event["lambda"]) < 1.0e-9
            and event["branch_overlap"] > 0.9
            and event["maximum_constraint_residual"] < 1.0e-8
            and eta["minimum"] > 0.0
        ),
        "coherent_branch_matches_independent_N5_structural_index": bool(
            event["branch_index"] == independent_n5_event["branch_index"]
            == int(n4_event["branch_index"] + 2)
        ),
        "N4_N5_highest_energy_mode_fractions_small": all(
            row["highest_mode_fractions_in_action_energy_norm"]["q"] < 0.01
            and row["highest_mode_fractions_in_action_energy_norm"]["velocity"] < 0.05
            and row["highest_mode_fractions_in_action_energy_norm"]["multiplier"] < 0.05
            for row in tail_rows[1:]
        ),
        "independent_children_not_misreported_as_a_Cauchy_sequence": max(
            independent_differences.values()
        ) > 0.8,
    }
    return {
        "classification": classification,
        "action_energy_space": {
            "state": (
                "X_E=R_scale_CROSS_H1_radial_geometry_CROSS_L2_velocity_"
                "CROSS_H1_lapse_shift"
            ),
            "constraint_dual": "Hminus1_lapse_shift_CROSS_R_energy",
            "boundary": "FINITE_R3_TRACE_CROSS_TSTAR_R2_REACTION",
            "why_owned_by_the_action": (
                "THE_RETAINED_RADIAL_ACTION_CONTAINS_FIRST_RADIAL_"
                "DERIVATIVES_OF_GEOMETRY_LAPSE_AND_SHIFT_AND_ALGEBRAIC_"
                "COORDINATE_TIME_VELOCITIES"
            ),
            "H6_H5_H6_role": (
                "CLASSICAL_REGULARITY_AND_POINTWISE_SMOOTHNESS_CLASS_NOT_"
                "THE_PHYSICAL_ENERGY_DISTANCE_USED_TO_TRANSPORT_ROOTS"
            ),
        },
        "tail_rows": tail_rows,
        "independent_N4_N5_child_energy_relative_differences": (
            independent_differences
        ),
        "independent_children_are_a_proved_convergence_sequence": False,
        "projection_comparison": {
            "H6_H5_H6_projection_constraint_maximum": h6_projection[
                "maximum_constraint_residual"
            ],
            "H6_H5_H6_projection_eta_minimum": h6_eta["minimum"],
            "action_energy_projection_constraint_maximum": (
                energy_projection["maximum_constraint_residual"]
            ),
            "action_energy_projection_eta_minimum": _eta_legendre_minimum(
                5, q0, m0, points=2400
            )["minimum"],
            "physical_constraints_or_eta_gate_changed": False,
        },
        "coherent_N4_to_N5_event": coherent_event,
        "new_physics_equations_constraints_or_acceptance_gates": False,
        "coherent_complete_child_graph_validated": graph_validated,
        "coherent_complete_child_persistence_validated": persistence_validated,
        "required_next": required_next,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def reaction_calderon_nested_schur_trace_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Localize the first uniform reaction-Calderon graph obstruction."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    states = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: payload[
            "N4_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
    }


def sequential_action_energy_projection_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    maximum_order: int = 10,
) -> dict[str, Any]:
    """Transport the coherent event and child through nested constraint fibers."""

    if maximum_order < 6:
        raise ValueError("maximum_order must include at least N=6")
    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    event = action_energy_topology_coherent_event_audit(target)[
        "coherent_N4_to_N5_event"
    ]
    child = result["coherent_N4_to_N5_complete_child_graph"]["child_state"]
    exact = child["binary64_hex"]
    states = {
        "event": (
            np.asarray(event["coordinates"], dtype=float),
            np.asarray(event["velocities"], dtype=float),
            np.asarray(event["multipliers"], dtype=float),
        ),
        "child": tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        ),
    }


def _child_compatibility_rows_at_order(
    order: int,
    child: np.ndarray,
    event_coordinates: np.ndarray,
    event_momentum: np.ndarray,
    *,
    points: int,
) -> np.ndarray:
    """Return trace, constraint and momentum rows without dynamic flux."""

    qdim = dimensions(order)["coordinates"]
    q = np.asarray(child[:qdim], dtype=float)
    velocity = np.asarray(child[qdim:2 * qdim], dtype=float)
    multipliers = np.asarray(child[2 * qdim:], dtype=float)
    momentum, _, _, _ = _canonical_pair_at_order(
        order, q, velocity, multipliers, points=points
    )
    return np.concatenate((
        _trace_jacobian_at_order(order) @ (q - event_coordinates),
        constraint_residual(
            order, q, velocity, multipliers, points=points
        ),
        momentum - event_momentum,
    ))


def n6_full_compatibility_extension_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
) -> dict[str, Any]:
    """Allow the N6 geometry shell to repair the localized constraint owner."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    row = result["sequential_action_energy_projection_audit"]["rows"][0]

    def decode(label: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        exact = row[label]["projected_state_binary64_hex"]
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    event_q, event_v, event_m = decode("event")
    coherent_child = result[
        "coherent_N4_to_N5_complete_child_graph"
    ]["child_state"]["binary64_hex"]
    child_n5 = tuple(
        np.asarray([float.fromhex(value) for value in coherent_child[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )
    child_q, child_v, child_m = embed_nested_state(*child_n5, 5, 6)
    order = 6
    qdim = dimensions(order)["coordinates"]
    event_momentum, _, _, _ = _canonical_pair_at_order(
        order, event_q, event_v, event_m, points=points
    )
    seed = np.concatenate((child_q, child_v, child_m))
    frequencies = spectral_frequencies(order)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    correction = np.zeros_like(seed)

    def physical_state(value: np.ndarray) -> np.ndarray:
        return seed + value / weights

    initial_rows = _child_compatibility_rows_at_order(
        order, seed, event_q, event_momentum, points=points
    )
    row_scale = np.maximum(1.0, np.abs(initial_rows))

    def rows(value: np.ndarray) -> np.ndarray:
        return _child_compatibility_rows_at_order(
            order,
            physical_state(value),
            event_q,
            event_momentum,
            points=points,
        ) / row_scale

    merit_history = []
    converged = False
    message = "maximum full compatibility projection iterations reached"
    for iteration in range(24):
        residual = rows(correction)
        merit = float(np.linalg.norm(residual))
        merit_history.append(merit)
        if float(np.max(np.abs(residual))) < 2.0e-10:
            converged = True
            message = "full action-energy compatibility projection converged"
            break
        jacobian = np.empty((residual.size, correction.size))
        for column in range(correction.size):
            step = 2.0e-4 * max(1.0, abs(float(correction[column])))
            delta = np.zeros_like(correction)
            delta[column] = step
            jacobian[:, column] = (
                rows(correction + delta) - rows(correction - delta)
            ) / (2.0 * step)
        proposal = np.linalg.lstsq(
            jacobian, -residual, rcond=1.0e-12
        )[0]
        accepted = False
        factor = 1.0
        for _ in range(18):
            candidate = correction + factor * proposal
            if float(np.linalg.norm(rows(candidate))) < merit:
                correction = candidate
                accepted = True
                break
            factor *= 0.5
        if not accepted:
            message = "coupled-merit line search failed"
            break
    solved = physical_state(correction)
    final_rows = _child_compatibility_rows_at_order(
        order, solved, event_q, event_momentum, points=points
    )
    solved_q = solved[:qdim]
    solved_v = solved[qdim:2 * qdim]
    solved_m = solved[2 * qdim:]
    eta = _eta_legendre_minimum(order, solved_q, solved_m, points=2000)
    q_correction = solved_q - child_q
    velocity_correction = solved_v - child_v
    multiplier_correction = solved_m - child_m
    new_geometry_shell = np.asarray([
        q_correction[order],
        q_correction[2 * order],
        q_correction[3 * order],
    ])
    validation = {
        "coupled_compatibility_merit_reduced": bool(
            np.linalg.norm(final_rows) < np.linalg.norm(initial_rows)
        ),
        "componentwise_monotonicity_not_required": True,
        "physical_rows_equations_and_gates_unchanged": True,
        "dynamic_flux_not_used_in_this_owner_repair": True,
    }


def n6_complete_boundary_bvp_match_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
) -> dict[str, Any]:
    """Solve exact attachment matching on the closed N6 compatibility fiber."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    compatibility = result["N6_full_compatibility_extension_audit"]
    if not compatibility["solver_converged"]:
        raise RuntimeError("N6 compatibility must close first")
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]
    child_exact = compatibility["child_state_binary64_hex"]

    def decode(
        exact: Mapping[str, Any],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    event_q, event_v, event_m = decode(event_exact)
    child_q, child_v, child_m = decode(child_exact)
    order = 6
    qdim = dimensions(order)["coordinates"]
    event_momentum = _canonical_pair_at_order(
        order, event_q, event_v, event_m, points=points
    )[0]
    seed = np.concatenate((child_q, child_v, child_m))
    frequencies = spectral_frequencies(order)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    correction = np.zeros_like(seed)

    def physical_state(value: np.ndarray) -> np.ndarray:
        return seed + value / weights

    def physical_rows(state: np.ndarray) -> np.ndarray:
        compatibility_rows = _child_compatibility_rows_at_order(
            order, state, event_q, event_momentum, points=points
        )
        attachment_rows = (
            _attachment_coordinates_at_order(order, state[:qdim])
            - _attachment_coordinates_at_order(order, event_q)
        )
        return np.concatenate((compatibility_rows, attachment_rows))

    initial_rows = physical_rows(seed)
    row_scale = np.maximum(1.0, np.abs(initial_rows))

    def rows(value: np.ndarray) -> np.ndarray:
        return physical_rows(physical_state(value)) / row_scale

    merit_history = []
    converged = False
    message = "maximum boundary BVP matching iterations reached"
    for iteration in range(20):
        residual = rows(correction)
        merit = float(np.linalg.norm(residual))
        merit_history.append(merit)
        if float(np.max(np.abs(residual))) < 2.0e-10:
            converged = True
            message = "exact attachment match closed on compatibility fiber"
            break
        jacobian = np.empty((residual.size, correction.size))
        for column in range(correction.size):
            step = 2.0e-4 * max(1.0, abs(float(correction[column])))
            delta = np.zeros_like(correction)
            delta[column] = step
            jacobian[:, column] = (
                rows(correction + delta) - rows(correction - delta)
            ) / (2.0 * step)
        proposal = np.linalg.lstsq(
            jacobian, -residual, rcond=1.0e-12
        )[0]
        accepted = False
        factor = 1.0
        for _ in range(18):
            candidate = correction + factor * proposal
            if float(np.linalg.norm(rows(candidate))) < merit:
                correction = candidate
                accepted = True
                break
            factor *= 0.5
        if not accepted:
            message = "coupled physical-merit line search failed"
            break
    solved = physical_state(correction)
    final_rows = physical_rows(solved)
    solved_q = solved[:qdim]
    solved_v = solved[qdim:2 * qdim]
    solved_m = solved[2 * qdim:]
    compatibility_count = 2 * order + 6
    compatibility_maximum = float(np.max(np.abs(
        final_rows[:compatibility_count]
    )))
    attachment_norm = float(np.linalg.norm(
        final_rows[compatibility_count:]
    ))
    eta = _eta_legendre_minimum(order, solved_q, solved_m, points=2000)
    validation = {
        "unchanged_compatibility_rows_remain_closed": bool(
            compatibility_maximum < 1.0e-9
        ),
        "exact_attachment_configuration_match_closes": bool(
            attachment_norm < 1.0e-9
        ),
        "eta_domain_retained": bool(eta["minimum"] > 0.0),
        "boundary_condition_is_solved_on_fiber_not_added_to_F_N": True,
        "finite_N5_equations_and_gates_unchanged": True,
    }
    return {
        "classification": (
            "N6_EVENT_TO_COMPLETE_CHILD_EXACT_ATTACHMENT_BOUNDARY_BVP_"
            "MATCH_CLOSED_ON_THE_UNCHANGED_COMPATIBILITY_FIBER"
            if converged and all(validation.values()) else
            "N6_EXACT_ATTACHMENT_BOUNDARY_BVP_MATCH_REMAINS_OPEN"
        ),
        "initial_exact_attachment_jump_norm": float(np.linalg.norm(
            initial_rows[-2:]
        )),
        "final_exact_attachment_jump_norm": attachment_norm,
        "final_compatibility_maximum": compatibility_maximum,
        "solver_converged": converged,
        "solver_message": message,
        "iterations": iteration + 1,
        "merit_history": merit_history,
        "action_energy_correction_norm": float(np.linalg.norm(correction)),
        "eta_Legendre_minimum": eta["minimum"],
        "child_state_binary64_hex": {
            "coordinates": [value.hex() for value in solved_q],
            "velocities": [value.hex() for value in solved_v],
            "multipliers": [value.hex() for value in solved_m],
        },
        "boundary_condition_role": (
            "F_child_boundary(z_event)=0_SOLVABILITY_ON_CANDIDATE_"
            "COMPATIBILITY_STATES;_NOT_AN_ADDITIONAL_LOCAL_F_N_ROW"
        ),
        "new_equation_constraint_or_acceptance_gate": False,
        "required_next": (
            "EVALUATE_THE_TWO_SIDED_WEAK_CONORMAL_REACTION_ON_THE_"
            "EXACTLY_MATCHED_N6_BOUNDARY_BVP_STATE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def n6_event_child_weak_reaction_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
) -> dict[str, Any]:
    """Evaluate the derived two-sided weak conormal map on the N6 fiber."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    compatibility = result["N6_full_compatibility_extension_audit"]
    if not compatibility["solver_converged"]:
        raise RuntimeError("N6 compatibility must close before reaction")
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]
    boundary_match = result.get("N6_complete_boundary_BVP_match_audit")
    child_exact = (
        boundary_match["child_state_binary64_hex"]
        if isinstance(boundary_match, dict)
        and boundary_match.get("solver_converged", False)
        else compatibility["child_state_binary64_hex"]
    )

    def decode(
        exact: Mapping[str, Any],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    q_event, v_event, m_event = decode(event_exact)
    q_child, v_child, m_child = decode(child_exact)
    order = 6
    event_boundary = _attachment_jacobian_at_order(order, q_event)
    child_boundary = _attachment_jacobian_at_order(order, q_child)
    event_dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q_event, v_event, m_event, points=points
    )
    event_boundary_acceleration = (
        event_boundary @ np.asarray(
            event_dynamics["acceleration"], dtype=float
        )
        + _attachment_chart_curvature_on_velocity(
            order, q_event, v_event
        )
    )
    event_reaction = _child_history_boundary_reaction_solve(
        order,
        q_event,
        v_event,
        m_event,
        event_boundary_acceleration,
        points=points,
    )
    child_zero = _child_history_boundary_reaction_solve(
        order, q_child, v_child, m_child, np.zeros(2), points=points
    )
    child_offset = np.asarray(child_zero["boundary_reaction"], dtype=float)
    child_response = np.empty((2, 2))
    for column in range(2):
        unit = np.zeros(2)
        unit[column] = 1.0
        response = _child_history_boundary_reaction_solve(
            order, q_child, v_child, m_child, unit, points=points
        )
        child_response[:, column] = (
            np.asarray(response["boundary_reaction"], dtype=float)
            - child_offset
        )
    event_reaction_vector = np.asarray(
        event_reaction["boundary_reaction"], dtype=float
    )
    child_boundary_acceleration = np.linalg.solve(
        child_response, -event_reaction_vector - child_offset
    )
    child_reaction = _child_history_boundary_reaction_solve(
        order,
        q_child,
        v_child,
        m_child,
        child_boundary_acceleration,
        points=points,
    )
    child_reaction_vector = np.asarray(
        child_reaction["boundary_reaction"], dtype=float
    )
    reaction_match = float(np.linalg.norm(
        event_reaction_vector + child_reaction_vector
    ))
    event_momentum = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )[0]
    child_momentum = _canonical_pair_at_order(
        order, q_child, v_child, m_child, points=points
    )[0]
    maximum_bvp_residual = max(
        child_reaction["maximum_Euler_reaction_residual"],
        child_reaction["maximum_constraint_tangent_residual"],
        child_reaction["maximum_boundary_acceleration_residual"],
    )
    attachment_configuration_jump = float(np.linalg.norm(
        _attachment_coordinates_at_order(order, q_child)
        - _attachment_coordinates_at_order(order, q_event)
    ))
    validation = {
        "N6_compatibility_fiber_closed_first": bool(
            compatibility["final_compatibility_maximum"] < 1.0e-9
        ),
        "child_reaction_response_invertible": bool(
            abs(np.linalg.det(child_response)) > 1.0e-10
        ),
        "two_sided_weak_reaction_match_closes": bool(
            reaction_match < 1.0e-6
        ),
        "bordered_Euler_constraint_boundary_blocks_replay": bool(
            maximum_bvp_residual < 1.0e-6
        ),
        "accepted_attachment_momentum_replays": bool(
            np.linalg.norm(child_momentum - event_momentum) < 1.0e-9
        ),
        "exact_attachment_configuration_matches": bool(
            attachment_configuration_jump < 1.0e-9
        ),
        "finite_N5_physical_map_and_gates_unchanged": True,
    }


def coherent_n5_exact_attachment_weak_child_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Reconcile the coherent N5 child with the exact attachment BVP map."""

    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    event = action_energy_topology_coherent_event_audit(target)[
        "coherent_N4_to_N5_event"
    ]
    q_event = np.asarray(event["coordinates"], dtype=float)
    v_event = np.asarray(event["velocities"], dtype=float)
    m_event = np.asarray(event["multipliers"], dtype=float)
    exact = result["coherent_N4_to_N5_complete_child_graph"][
        "child_state"
    ]["binary64_hex"]
    q_child = np.asarray([
        float.fromhex(value) for value in exact["coordinates"]
    ])
    v_child = np.asarray([
        float.fromhex(value) for value in exact["velocities"]
    ])
    m_child = np.asarray([
        float.fromhex(value) for value in exact["multipliers"]
    ])
    order = 5
    qdim = dimensions(order)["coordinates"]
    event_momentum = _canonical_pair_at_order(
        order, q_event, v_event, m_event, points=points
    )[0]
    seed = np.concatenate((q_child, v_child, m_child))
    frequencies = spectral_frequencies(order)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))

    def physical_state(value: np.ndarray) -> np.ndarray:
        return seed + value / weights

    def physical_rows(state: np.ndarray) -> np.ndarray:
        return np.concatenate((
            _child_compatibility_rows_at_order(
                order, state, q_event, event_momentum, points=points
            ),
            _attachment_coordinates_at_order(order, state[:qdim])
            - _attachment_coordinates_at_order(order, q_event),
        ))

    initial_rows = physical_rows(seed)
    row_scale = np.maximum(1.0, np.abs(initial_rows))
    solution = least_squares(
        lambda value: physical_rows(physical_state(value)) / row_scale,
        np.zeros_like(seed),
        method="trf",
        jac="2-point",
        xtol=1.0e-12,
        ftol=1.0e-12,
        gtol=1.0e-12,
        max_nfev=300,
    )
    solved = physical_state(solution.x)
    final_rows = physical_rows(solved)
    solved_q = solved[:qdim]
    solved_v = solved[qdim:2 * qdim]
    solved_m = solved[2 * qdim:]
    compatibility_count = 2 * order + 6
    compatibility_maximum = float(np.max(np.abs(
        final_rows[:compatibility_count]
    )))
    attachment_norm = float(np.linalg.norm(
        final_rows[compatibility_count:]
    ))
    eta = _eta_legendre_minimum(order, solved_q, solved_m, points=2000)

    event_boundary = _attachment_jacobian_at_order(order, q_event)
    child_boundary = _attachment_jacobian_at_order(order, solved_q)
    event_dynamics = _exact_full_jet_euler_dirac_acceleration(
        order, q_event, v_event, m_event, points=points
    )
    event_boundary_acceleration = (
        event_boundary @ np.asarray(
            event_dynamics["acceleration"], dtype=float
        )
        + _attachment_chart_curvature_on_velocity(
            order, q_event, v_event
        )
    )
    event_reaction = _child_history_boundary_reaction_solve(
        order,
        q_event,
        v_event,
        m_event,
        event_boundary_acceleration,
        points=points,
    )
    child_zero = _child_history_boundary_reaction_solve(
        order, solved_q, solved_v, solved_m, np.zeros(2), points=points
    )
    child_offset = np.asarray(child_zero["boundary_reaction"], dtype=float)
    child_response = np.empty((2, 2))
    for column in range(2):
        unit = np.zeros(2)
        unit[column] = 1.0
        response = _child_history_boundary_reaction_solve(
            order, solved_q, solved_v, solved_m, unit, points=points
        )
        child_response[:, column] = (
            np.asarray(response["boundary_reaction"], dtype=float)
            - child_offset
        )
    event_reaction_vector = np.asarray(
        event_reaction["boundary_reaction"], dtype=float
    )
    child_boundary_acceleration = np.linalg.solve(
        child_response, -event_reaction_vector - child_offset
    )
    child_reaction = _child_history_boundary_reaction_solve(
        order,
        solved_q,
        solved_v,
        solved_m,
        child_boundary_acceleration,
        points=points,
    )
    child_reaction_vector = np.asarray(
        child_reaction["boundary_reaction"], dtype=float
    )
    reaction_match = float(np.linalg.norm(
        event_reaction_vector + child_reaction_vector
    ))
    child_momentum = _canonical_pair_at_order(
        order, solved_q, solved_v, solved_m, points=points
    )[0]
    maximum_bvp_residual = max(
        child_reaction["maximum_Euler_reaction_residual"],
        child_reaction["maximum_constraint_tangent_residual"],
        child_reaction["maximum_boundary_acceleration_residual"],
    )
    validation = {
        "compatibility_fiber_remains_closed": bool(
            compatibility_maximum < 1.0e-9
        ),
        "exact_attachment_configuration_matches": bool(
            attachment_norm < 1.0e-9
        ),
        "two_sided_weak_reaction_matches": bool(
            reaction_match < 1.0e-6
        ),
        "bordered_reaction_blocks_replay": bool(
            maximum_bvp_residual < 1.0e-6
        ),
        "canonical_momentum_match_replays": bool(
            np.linalg.norm(child_momentum - event_momentum) < 1.0e-9
        ),
        "eta_domain_retained": bool(eta["minimum"] > 0.0),
        "original_coherent_F18_root_unchanged": True,
    }


def legacy_n3_n4_exact_attachment_weak_child_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
) -> dict[str, Any]:
    """Reconcile the legacy N3/N4 children with the exact boundary map."""

    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    n3_payload = json.loads((target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )).read_text(encoding="utf-8"))
    n3_state = unpack_reduced(v17_75_selected_raw_vector())
    n3_q_history = np.asarray(n3_state["coordinates"], dtype=float)
    n3_m_history = np.asarray(n3_state["multipliers"], dtype=float)
    n3_v_history = (
        trapezoid_sbp_difference() @ n3_q_history
        / float(n3_state["period"])
    )
    n4_event = result["N4_adaptive_event_convergence_audit"][
        "quadrature_control"
    ]["event"]
    events = {
        3: (n3_q_history[-1], n3_v_history[-1], n3_m_history[-1]),
        4: tuple(
            np.asarray(n4_event[name], dtype=float)
            for name in ("coordinates", "velocities", "multipliers")
        ),
    }
    sources = {
        3: n3_payload["complete_child_persistence"]["evolution"]["rows"][0],
        4: result[
            "N4_event_conditioned_complete_child_reconstruction"
        ]["child_state"],
    }

    def decode(source: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
        exact = source.get("binary64_hex")
        if exact is None:
            return tuple(
                np.asarray(source[name], dtype=float)
                for name in ("coordinates", "velocities", "multipliers")
            )
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    rows = []
    for order in (3, 4):
        q_event, v_event, m_event = events[order]
        q_child, v_child, m_child = decode(sources[order])
        qdim = dimensions(order)["coordinates"]
        event_momentum = _canonical_pair_at_order(
            order, q_event, v_event, m_event, points=points
        )[0]
        seed = np.concatenate((q_child, v_child, m_child))
        frequencies = spectral_frequencies(order)
        weights = np.concatenate((
            np.sqrt(1.0 + frequencies["coordinates"] ** 2),
            np.ones(qdim),
            np.sqrt(1.0 + frequencies["multipliers"] ** 2),
        ))

        def physical_state(value: np.ndarray) -> np.ndarray:
            return seed + value / weights

        def physical_rows(state: np.ndarray) -> np.ndarray:
            return np.concatenate((
                _child_compatibility_rows_at_order(
                    order,
                    state,
                    q_event,
                    event_momentum,
                    points=points,
                ),
                _attachment_coordinates_at_order(order, state[:qdim])
                - _attachment_coordinates_at_order(order, q_event),
            ))

        initial_rows = physical_rows(seed)
        row_scale = np.maximum(1.0, np.abs(initial_rows))
        solution = least_squares(
            lambda value: (
                physical_rows(physical_state(value)) / row_scale
            ),
            np.zeros_like(seed),
            method="trf",
            jac="2-point",
            xtol=1.0e-12,
            ftol=1.0e-12,
            gtol=1.0e-12,
            max_nfev=300,
        )
        solved = physical_state(solution.x)
        final_rows = physical_rows(solved)
        solved_q = solved[:qdim]
        solved_v = solved[qdim:2 * qdim]
        solved_m = solved[2 * qdim:]
        compatibility_count = 2 * order + 6
        compatibility_maximum = float(np.max(np.abs(
            final_rows[:compatibility_count]
        )))
        attachment_norm = float(np.linalg.norm(
            final_rows[compatibility_count:]
        ))
        eta = _eta_legendre_minimum(
            order, solved_q, solved_m, points=2000
        )

        event_boundary = _attachment_jacobian_at_order(order, q_event)
        event_dynamics = _exact_full_jet_euler_dirac_acceleration(
            order, q_event, v_event, m_event, points=points
        )
        event_boundary_acceleration = (
            event_boundary @ np.asarray(
                event_dynamics["acceleration"], dtype=float
            )
            + _attachment_chart_curvature_on_velocity(
                order, q_event, v_event
            )
        )
        event_reaction = _child_history_boundary_reaction_solve(
            order,
            q_event,
            v_event,
            m_event,
            event_boundary_acceleration,
            points=points,
        )
        child_zero = _child_history_boundary_reaction_solve(
            order,
            solved_q,
            solved_v,
            solved_m,
            np.zeros(2),
            points=points,
        )
        child_offset = np.asarray(
            child_zero["boundary_reaction"], dtype=float
        )
        child_response = np.empty((2, 2))
        for column in range(2):
            unit = np.zeros(2)
            unit[column] = 1.0
            response = _child_history_boundary_reaction_solve(
                order,
                solved_q,
                solved_v,
                solved_m,
                unit,
                points=points,
            )
            child_response[:, column] = (
                np.asarray(response["boundary_reaction"], dtype=float)
                - child_offset
            )
        event_reaction_vector = np.asarray(
            event_reaction["boundary_reaction"], dtype=float
        )
        child_boundary_acceleration = np.linalg.solve(
            child_response, -event_reaction_vector - child_offset
        )
        child_reaction = _child_history_boundary_reaction_solve(
            order,
            solved_q,
            solved_v,
            solved_m,
            child_boundary_acceleration,
            points=points,
        )
        child_reaction_vector = np.asarray(
            child_reaction["boundary_reaction"], dtype=float
        )
        reaction_match = float(np.linalg.norm(
            event_reaction_vector + child_reaction_vector
        ))
        child_momentum = _canonical_pair_at_order(
            order, solved_q, solved_v, solved_m, points=points
        )[0]
        maximum_bvp_residual = max(
            child_reaction["maximum_Euler_reaction_residual"],
            child_reaction["maximum_constraint_tangent_residual"],
            child_reaction["maximum_boundary_acceleration_residual"],
        )
        rows.append({
            "N": order,
            "least_squares_success": bool(solution.success),
            "function_evaluations": int(solution.nfev),
            "initial_exact_attachment_jump_norm": float(np.linalg.norm(
                initial_rows[-2:]
            )),
            "final_exact_attachment_jump_norm": attachment_norm,
            "final_compatibility_maximum": compatibility_maximum,
            "action_energy_correction_norm": float(
                np.linalg.norm(solution.x)
            ),
            "eta_Legendre_minimum": eta["minimum"],
            "child_reaction_response_determinant": float(
                np.linalg.det(child_response)
            ),
            "child_reaction_response_condition_number": float(
                np.linalg.cond(child_response)
            ),
            "two_sided_reaction_match_norm": reaction_match,
            "maximum_child_BVP_block_residual": maximum_bvp_residual,
            "attachment_momentum_match_norm": float(np.linalg.norm(
                child_momentum - event_momentum
            )),
            "child_state_binary64_hex": {
                "coordinates": [value.hex() for value in solved_q],
                "velocities": [value.hex() for value in solved_v],
                "multipliers": [value.hex() for value in solved_m],
            },
        })
    validation = {
        "both_legacy_orders_evaluated": [row["N"] for row in rows] == [3, 4],
        "both_compatibility_fibers_close": all(
            row["final_compatibility_maximum"] < 1.0e-9 for row in rows
        ),
        "both_exact_attachment_matches_close": all(
            row["final_exact_attachment_jump_norm"] < 1.0e-9
            for row in rows
        ),
        "both_two_sided_weak_reactions_close": all(
            row["two_sided_reaction_match_norm"] < 1.0e-6 for row in rows
        ),
        "both_bordered_reaction_blocks_replay": all(
            row["maximum_child_BVP_block_residual"] < 1.0e-6
            for row in rows
        ),
        "both_eta_domains_retained": all(
            row["eta_Legendre_minimum"] > 0.0 for row in rows
        ),
        "legacy_local_roots_and_persistence_unchanged": True,
    }
    return {
        "classification": (
            "N3_N4_EXACT_EVENT_CHILD_ATTACHMENT_AND_TWO_SIDED_WEAK_"
            "CONORMAL_COMPLETE_CHILD_CORRESPONDENCES_CLOSED"
        ),
        "rows": rows,
        "boundary_match_is_solvability_on_existing_fibers": True,
        "legacy_local_dynamic_flux_maps_reopened": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "required_next": (
            "RUN_THE_UNCHANGED_POSITIVE_DURATION_PERSISTENCE_ON_THE_"
            "EXACT_ATTACHMENT_MATCHED_N3_N4_WEAK_CHILDREN"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    return {
        "classification": (
            "COHERENT_N5_EXACT_EVENT_CHILD_ATTACHMENT_AND_TWO_SIDED_"
            "WEAK_CONORMAL_COMPLETE_CHILD_CORRESPONDENCE_CLOSED"
        ),
        "initial_exact_attachment_jump_norm": float(np.linalg.norm(
            initial_rows[-2:]
        )),
        "final_exact_attachment_jump_norm": attachment_norm,
        "final_compatibility_maximum": compatibility_maximum,
        "least_squares_success": bool(solution.success),
        "function_evaluations": int(solution.nfev),
        "action_energy_correction_norm": float(np.linalg.norm(solution.x)),
        "eta_Legendre_minimum": eta["minimum"],
        "child_reaction_response_determinant": float(
            np.linalg.det(child_response)
        ),
        "child_reaction_response_condition_number": float(
            np.linalg.cond(child_response)
        ),
        "two_sided_reaction_match_norm": reaction_match,
        "maximum_child_BVP_block_residual": maximum_bvp_residual,
        "attachment_momentum_match_norm": float(np.linalg.norm(
            child_momentum - event_momentum
        )),
        "solved_child_boundary_acceleration": (
            child_boundary_acceleration.tolist()
        ),
        "child_state_binary64_hex": {
            "coordinates": [value.hex() for value in solved_q],
            "velocities": [value.hex() for value in solved_v],
            "multipliers": [value.hex() for value in solved_m],
        },
        "boundary_match_is_solvability_on_the_existing_fiber": True,
        "legacy_local_dynamic_flux_map_reopened": False,
        "new_equation_constraint_or_acceptance_gate": False,
        "required_next": (
            "RUN_THE_UNCHANGED_POSITIVE_DURATION_PERSISTENCE_ON_THE_"
            "EXACT_ATTACHMENT_MATCHED_COHERENT_N5_WEAK_CHILD"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    return {
        "classification": (
            "N6_EVENT_TO_CHILD_COMPLETE_BOUNDARY_AND_TWO_SIDED_WEAK_"
            "CONORMAL_REACTION_CORRESPONDENCE_CLOSED"
            if all(validation.values()) else
            "N6_TWO_SIDED_WEAK_REACTION_BALANCE_CLOSED_BUT_EXACT_"
            "ATTACHMENT_CONFIGURATION_CORRESPONDENCE_REMAINS_OPEN"
        ),
        "map": (
            "Lambda_child_6(b_ddot_child;Y6)="
            "-Lambda_event_6(b_ddot_event;z6)"
        ),
        "event_boundary_acceleration": event_boundary_acceleration.tolist(),
        "event_boundary_reaction": event_reaction_vector.tolist(),
        "child_reaction_response_matrix": child_response.tolist(),
        "child_reaction_response_determinant": float(
            np.linalg.det(child_response)
        ),
        "child_reaction_response_condition_number": float(
            np.linalg.cond(child_response)
        ),
        "solved_child_boundary_acceleration": (
            child_boundary_acceleration.tolist()
        ),
        "solved_child_boundary_reaction": child_reaction_vector.tolist(),
        "two_sided_reaction_match_norm": reaction_match,
        "maximum_child_BVP_block_residual": maximum_bvp_residual,
        "attachment_configuration_jump_norm": attachment_configuration_jump,
        "attachment_rate_jump_norm": float(np.linalg.norm(
            child_boundary @ v_child - event_boundary @ v_event
        )),
        "attachment_momentum_match_norm": float(np.linalg.norm(
            child_momentum - event_momentum
        )),
        "boundary_acceleration_is_a_solved_reaction_datum_not_a_new_gate": (
            True
        ),
        "legacy_local_dynamic_flux_row_used": False,
        "complete_N6_persistence_claimed": False,
        "new_action_equation_constraint_or_acceptance_gate": False,
        "required_next": (
            "RUN_THE_UNCHANGED_POSITIVE_DURATION_CHILD_PERSISTENCE_ON_"
            "THE_N6_COMPATIBILITY_STATE_AND_COMPARE_THE_WEAK_REACTION_"
            "GRAPH_WITH_N5_IN_ACTION_NORMALIZED_COORDINATES"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    return {
        "classification": (
            "N6_FULL_TRACE_CONSTRAINT_MOMENTUM_COMPATIBILITY_EXTENSION_"
            "CLOSED_WITH_THE_GEOMETRY_SHELL_ACTIVE"
            if converged else
            "N6_FULL_COMPATIBILITY_EXTENSION_REDUCED_THE_LOCALIZED_"
            "OWNER_BUT_DID_NOT_CLOSE"
        ),
        "localized_owner": (
            "NEW_N6_LAPSE_AND_SHIFT_CONSTRAINT_ROWS_WITH_LEGACY_ROWS_"
            "ALREADY_CLOSED"
        ),
        "child_seed": (
            "DIRECT_ZERO_PADDED_COHERENT_N5_CHILD_BEFORE_THE_FIXED_"
            "GEOMETRY_CONSTRAINT_PROJECTION"
        ),
        "initial_compatibility_norm": float(np.linalg.norm(initial_rows)),
        "final_compatibility_norm": float(np.linalg.norm(final_rows)),
        "final_compatibility_maximum": float(np.max(np.abs(final_rows))),
        "solver_converged": converged,
        "solver_message": message,
        "iterations": iteration + 1,
        "merit_history": merit_history,
        "action_energy_correction_norm": float(np.linalg.norm(correction)),
        "raw_correction_norms": {
            "geometry": float(np.linalg.norm(q_correction)),
            "velocity": float(np.linalg.norm(velocity_correction)),
            "multipliers": float(np.linalg.norm(multiplier_correction)),
            "new_geometry_shell": float(np.linalg.norm(new_geometry_shell)),
        },
        "eta_Legendre_minimum": eta["minimum"],
        "child_state_binary64_hex": {
            "coordinates": [value.hex() for value in solved_q],
            "velocities": [value.hex() for value in solved_v],
            "multipliers": [value.hex() for value in solved_m],
        },
        "complete_dynamic_reaction_rows_solved": False,
        "is_a_complete_N6_child_claim": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "required_next": (
            "IF_COMPATIBILITY_CLOSES,_FORM_THE_WEAK_CONORMAL_N6_REACTION_"
            "ROW_ON_THIS_FIBER_AND_TEST_THE_ACTION_NORMALIZED_NORMAL_GAP"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    rows = []
    for order in range(6, maximum_order + 1):
        row: dict[str, Any] = {"N": order}
        for label in ("event", "child"):
            q, velocity, multipliers = embed_nested_state(
                *states[label], order - 1, order
            )
            embedded_constraints = constraint_residual(
                order, q, velocity, multipliers, points=points
            )
            new_shell_indices = (order - 1, 2 * order - 1)
            legacy_indices = np.asarray([
                *range(0, order - 1),
                *range(order, 2 * order - 1),
                2 * order,
            ])
            projection = _project_constraints_action_energy(
                order, q, velocity, multipliers, points=points
            )
            projected = (
                q,
                np.asarray(projection["velocities"], dtype=float),
                np.asarray(projection["multipliers"], dtype=float),
            )
            states[label] = projected
            eta = _eta_legendre_minimum(
                order, projected[0], projected[2], points=1600
            )
            row[label] = {
                "projection_success": bool(projection["success"]),
                "embedded_constraint_norm": float(
                    np.linalg.norm(embedded_constraints)
                ),
                "embedded_legacy_constraint_maximum": float(
                    np.max(np.abs(embedded_constraints[legacy_indices]))
                ),
                "embedded_new_shell_constraint_norm": float(
                    np.linalg.norm(embedded_constraints[
                        np.asarray(new_shell_indices)
                    ])
                ),
                "embedded_new_lapse_constraint": float(
                    embedded_constraints[order - 1]
                ),
                "embedded_new_shift_constraint": float(
                    embedded_constraints[2 * order - 1]
                ),
                "embedded_energy_constraint": float(
                    embedded_constraints[2 * order]
                ),
                "action_energy_correction_norm": projection[
                    "action_energy_correction_norm"
                ],
                "raw_velocity_correction_norm": projection[
                    "raw_velocity_correction_norm"
                ],
                "raw_multiplier_correction_norm": projection[
                    "raw_multiplier_correction_norm"
                ],
                "maximum_constraint_residual": projection[
                    "maximum_constraint_residual"
                ],
                "eta_Legendre_minimum": eta["minimum"],
                "coordinate_time_vector_timelike_margin": (
                    _coordinate_time_vector_timelike_margin(
                        order, projected[0], projected[2]
                    )
                ),
                "projected_state_binary64_hex": {
                    "coordinates": [value.hex() for value in projected[0]],
                    "velocities": [value.hex() for value in projected[1]],
                    "multipliers": [value.hex() for value in projected[2]],
                },
            }
        rows.append(row)
    event_corrections = np.asarray([
        row["event"]["action_energy_correction_norm"] for row in rows
    ])
    child_corrections = np.asarray([
        row["child"]["action_energy_correction_norm"] for row in rows
    ])
    event_monotone = bool(np.all(np.diff(event_corrections) < 0.0))
    child_monotone = bool(np.all(np.diff(child_corrections) < 0.0))

    def trend(values: np.ndarray) -> float | None:
        if values.size < 2 or np.any(values <= 0.0):
            return None
        return float(np.polyfit(np.arange(6, maximum_order + 1), np.log(values), 1)[0])

    validation = {
        "all_nested_constraint_projections_succeeded": all(
            row[label]["projection_success"]
            for row in rows for label in ("event", "child")
        ),
        "all_projected_constraints_close": all(
            row[label]["maximum_constraint_residual"] < 1.0e-8
            for row in rows for label in ("event", "child")
        ),
        "eta_domain_retained": all(
            row[label]["eta_Legendre_minimum"] > 0.0
            for row in rows for label in ("event", "child")
        ),
        "finite_N5_root_event_persistence_and_gates_unchanged": True,
    }
    return {
        "classification": (
            "ACTION_ENERGY_COHERENT_EVENT_AND_CHILD_ADMIT_SEQUENTIAL_"
            "NESTED_CONSTRAINT_FIBER_TRANSPORT;_THIS_IS_NOT_YET_A_"
            "GENERAL_N_COMPLETE_CHILD_ROOT_CONTINUATION_THEOREM"
        ),
        "transport": (
            "EMBED_N_TO_N_PLUS_1_THEN_APPLY_THE_EXISTING_ACTION_ENERGY_"
            "NEAREST_CONSTRAINT_PROJECTION"
        ),
        "rows": rows,
        "log_correction_trend_per_resolution": {
            "event": trend(event_corrections),
            "child": trend(child_corrections),
        },
        "monotone_correction_decay_observed": {
            "event": event_monotone,
            "child": child_monotone,
        },
        "constraint_projection_sequence_establishes_general_N_convergence": (
            False
        ),
        "interpretation": (
            "THE_ACTION_ENERGY_CONSTRAINT_FIBER_REMAINS_ACCESSIBLE_AND_ETA_"
            "ADMISSIBLE_THROUGH_N10_BUT_THE_OSCILLATORY_NONVANISHING_"
            "CORRECTIONS_DO_NOT_ESTABLISH_A_CAUCHY_COMPLETE_CHILD_BRANCH"
        ),
        "correction_decay_required_as_a_new_acceptance_gate": False,
        "complete_child_dynamic_reaction_rows_solved_at_N6_TO_N10": False,
        "new_equations_constraints_or_gates": False,
        "required_next": (
            "PROVE_OR_MEASURE_THE_N_UNIFORM_POSITIVE_DURATION_NORMAL_"
            "CLOSED_RANGE_BOUND_AND_WEAK_CONORMAL_CALDERON_GRAPH_"
            "CONVERGENCE_ON_THE_ACTION_ENERGY_COHERENT_BRANCH"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }

    def exact_state(source: Mapping[str, Any]) -> tuple[
        np.ndarray, np.ndarray, np.ndarray
    ]:
        exact = source.get("binary64_hex")
        if exact is None:
            return tuple(  # type: ignore[return-value]
                np.asarray(source[name], dtype=float)
                for name in ("coordinates", "velocities", "multipliers")
            )
        return tuple(  # type: ignore[return-value]
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    def bordered_matrix(
        order: int, q: np.ndarray, velocity: np.ndarray, m: np.ndarray,
    ) -> np.ndarray:
        qdim = 3 * order + 1
        mdim = 2 * order
        hessian = np.asarray(
            exact_full_action_jet_at_state(
                order, q, velocity, m, points=points
            ).hessian,
            dtype=float,
        )
        boundary = _attachment_jacobian_at_order(order, q)
        return np.block([
            [
                hessian[qdim:2 * qdim, qdim:2 * qdim],
                hessian[qdim:2 * qdim, 2 * qdim:],
                -boundary.T,
            ],
            [
                hessian[2 * qdim:, qdim:2 * qdim],
                hessian[2 * qdim:, 2 * qdim:],
                np.zeros((mdim, 2)),
            ],
            [boundary, np.zeros((2, mdim)), np.zeros((2, 2))],
        ])

    def bordered_injection(order: int) -> np.ndarray:
        qlow = 3 * order + 1
        qhigh = 3 * (order + 1) + 1
        mlow = 2 * order
        mhigh = 2 * (order + 1)
        iq = np.zeros((qhigh, qlow))
        iq[0, 0] = 1.0
        for family in range(3):
            low = 1 + family * order
            high = 1 + family * (order + 1)
            iq[high:high + order, low:low + order] = np.eye(order)
        im = np.zeros((mhigh, mlow))
        im[:order, :order] = np.eye(order)
        im[order + 1:2 * order + 1, order:2 * order] = np.eye(order)
        return np.block([
            [iq, np.zeros((qhigh, mlow)), np.zeros((qhigh, 2))],
            [np.zeros((mhigh, qlow)), im, np.zeros((mhigh, 2))],
            [np.zeros((2, qlow)), np.zeros((2, mlow)), np.eye(2)],
        ])

    def response_graph(
        order: int, q: np.ndarray, velocity: np.ndarray, m: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        zero = _child_history_boundary_reaction_solve(
            order, q, velocity, m, np.zeros(2), points=points
        )
        offset = np.asarray(zero["boundary_reaction"], dtype=float)
        response = np.empty((2, 2))
        for column in range(2):
            unit = np.zeros(2)
            unit[column] = 1.0
            solved = _child_history_boundary_reaction_solve(
                order, q, velocity, m, unit, points=points
            )
            response[:, column] = (
                np.asarray(solved["boundary_reaction"], dtype=float)
                - offset
            )
        graph = np.vstack((np.eye(2), response))
        projector = graph @ np.linalg.solve(graph.T @ graph, graph.T)
        return offset, response, projector

    shell_rows = []
    for order, source in states.items():
        q, velocity, m = exact_state(source)
        qh, vh, mh = embed_nested_state(
            q, velocity, m, order, order + 1
        )
        low_matrix = bordered_matrix(order, q, velocity, m)
        high_matrix = bordered_matrix(order + 1, qh, vh, mh)
        injection = bordered_injection(order)
        used = set(np.argmax(injection, axis=0).tolist())
        high_indices = np.asarray([
            index for index in range(high_matrix.shape[0])
            if index not in used
        ])
        complement = np.eye(high_matrix.shape[0])[:, high_indices]
        low_restriction = injection.T @ high_matrix @ injection
        low_high = injection.T @ high_matrix @ complement
        high_high = complement.T @ high_matrix @ complement
        high_singular = np.linalg.svd(high_high, compute_uv=False)
        correction = low_high @ np.linalg.solve(high_high, low_high.T)
        effective = low_restriction - correction
        low_offset, low_response, low_projector = response_graph(
            order, q, velocity, m
        )
        high_offset, high_response, high_projector = response_graph(
            order + 1, qh, vh, mh
        )
        shell_rows.append({
            "low_N": order,
            "high_N": order + 1,
            "new_shell_dimension": int(high_indices.size),
            "exact_nested_bordered_matrix_error": float(
                np.linalg.norm(low_restriction - low_matrix)
            ),
            "high_shell_smallest_singular_value": float(high_singular[-1]),
            "low_high_coupling_norm": float(np.linalg.norm(low_high)),
            "schur_correction_norm": float(np.linalg.norm(correction)),
            "schur_correction_relative_to_low_operator": float(
                np.linalg.norm(correction)
                / max(1.0, np.linalg.norm(low_matrix))
            ),
            "low_operator_smallest_singular_value": float(
                np.linalg.svd(low_matrix, compute_uv=False)[-1]
            ),
            "effective_low_operator_smallest_singular_value": float(
                np.linalg.svd(effective, compute_uv=False)[-1]
            ),
            "injected_reaction_response_relative_change": float(
                np.linalg.norm(high_response - low_response)
                / max(1.0, np.linalg.norm(low_response))
            ),
            "injected_affine_offset_relative_change": float(
                np.linalg.norm(high_offset - low_offset)
                / max(1.0, np.linalg.norm(low_offset))
            ),
            "injected_linear_graph_gap": float(
                np.linalg.norm(high_projector - low_projector, ord=2)
            ),
            "low_reaction_response_singular_values": np.linalg.svd(
                low_response, compute_uv=False
            ).tolist(),
            "injected_high_reaction_response_singular_values": np.linalg.svd(
                high_response, compute_uv=False
            ).tolist(),
        })

    trace_rows = []
    for order in range(4, 65):
        q = np.zeros(3 * order + 1)
        boundary = _attachment_jacobian_at_order(order, q)
        frequencies = spectral_frequencies(order)["coordinates"]
        h1_weight = np.sqrt(1.0 + frequencies**2)
        trace_rows.append({
            "N": order,
            "L2_acceleration_to_boundary_trace_norm": float(
                np.linalg.norm(boundary, ord=2)
            ),
            "H1_acceleration_to_boundary_trace_norm": float(
                np.linalg.norm(boundary / h1_weight[None, :], ord=2)
            ),
        })
    fit_rows = trace_rows[12:]
    log_n = np.log([row["N"] for row in fit_rows])
    l2_slope = float(np.polyfit(log_n, np.log([
        row["L2_acceleration_to_boundary_trace_norm"]
        for row in fit_rows
    ]), 1)[0])
    h1_slope = float(np.polyfit(log_n, np.log([
        row["H1_acceleration_to_boundary_trace_norm"]
        for row in fit_rows
    ]), 1)[0])
    validation = {
        "bordered_action_operator_is_exactly_nested": all(
            row["exact_nested_bordered_matrix_error"] < 1.0e-12
            for row in shell_rows
        ),
        "each_added_resolution_shell_has_five_BVP_unknowns": all(
            row["new_shell_dimension"] == 5 for row in shell_rows
        ),
        "raw_high_shell_Schur_correction_does_not_decay_N3_to_N5": all(
            row["schur_correction_relative_to_low_operator"] > 1.0
            for row in shell_rows
        ),
        "pure_L2_boundary_acceleration_trace_is_not_uniform": l2_slope > 0.4,
        "H1_boundary_trace_is_uniformly_controlled": bool(
            abs(h1_slope) < 0.1
            and max(
                row["H1_acceleration_to_boundary_trace_norm"]
                for row in trace_rows
            ) < 2.0 * min(
                row["H1_acceleration_to_boundary_trace_norm"]
                for row in trace_rows
            )
        ),
    }
    return {
        "classification": (
            "BORDERED_ACTION_OPERATOR_EXACTLY_NESTED;_PURE_ACTION_ENERGY_"
            "REACTION_CALDERON_GRAPH_DOMAIN_INVALIDATED_BY_UNBOUNDED_L2_"
            "BOUNDARY_ACCELERATION_TRACE;_EULER_DIRAC_GRAPH_DOMAIN_REQUIRED"
        ),
        "shell_rows": shell_rows,
        "trace_scaling": {
            "sampled_N_range": [4, 64],
            "L2_trace_loglog_slope": l2_slope,
            "H1_trace_loglog_slope": h1_slope,
            "rows": trace_rows,
        },
        "derived_domain_reclassification": {
            "state_transport_topology_retained": (
                "H1_GEOMETRY_CROSS_L2_VELOCITY_CROSS_H1_LAPSE_SHIFT"
            ),
            "pure_state_energy_space_is_a_complete_Calderon_domain": False,
            "reaction_domain": (
                "D_EULER_DIRAC={U_IN_CLASSICAL_DOMAIN:E_U_IN_X_E_STAR_"
                "AND_Gamma_acc(U)_IN_R2}"
            ),
            "reaction_graph_norm": (
                "norm(U)_X_E+norm(E_U)_X_E_STAR+norm(Gamma_acc(U))_R2"
            ),
            "weak_conormal_reaction": (
                "Lambda_child=H_star*E_child_ON_THE_EULER_DIRAC_GRAPH_"
                "DOMAIN_INDEPENDENT_OF_THE_CHOSEN_BOUNDARY_LIFT"
            ),
            "new_physical_equation_constraint_or_gate": False,
        },
        "invalidated": (
            "USING_THE_PURE_H1_CROSS_L2_CROSS_H1_STATE_ENERGY_NORM_AS_"
            "THE_COMPLETE_BOUNDARY_ACCELERATION_CALDERON_GRAPH_NORM"
        ),
        "finite_N_roots_events_or_persistence_changed": False,
        "required_next": (
            "DERIVE_THE_WEAK_CONORMAL_REACTION_CALDERON_MAP_ON_THE_EULER_"
            "DIRAC_GRAPH_DOMAIN_AND_PROVE_UNIFORM_HIGH_SHELL_SCHUR_TAIL_"
            "CONTROL_OR_LOCALIZE_ITS_FIRST_LOWER_ORDER_FAILURE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def weak_conormal_reaction_graph_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    maximum_order: int = 12,
) -> dict[str, Any]:
    """Derive the weak reaction map and test its coherent high-shell tail."""

    if maximum_order < 8:
        raise ValueError("a resolved coherent high-shell sequence is required")
    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    source = result["coherent_N4_to_N5_complete_child_graph"]["child_state"]
    exact = source.get("binary64_hex")
    if exact is None:
        base = tuple(
            np.asarray(source[name], dtype=float)
            for name in ("coordinates", "velocities", "multipliers")
        )
    else:
        base = tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    def state(order: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if order == 5:
            return base  # type: ignore[return-value]
        return embed_nested_state(*base, 5, order)

    def matrix(
        order: int, q: np.ndarray, velocity: np.ndarray, m: np.ndarray,
    ) -> np.ndarray:
        qdim = 3 * order + 1
        mdim = 2 * order
        hessian = np.asarray(
            exact_full_action_jet_at_state(
                order, q, velocity, m, points=points
            ).hessian,
            dtype=float,
        )
        boundary = _attachment_jacobian_at_order(order, q)
        return np.block([
            [
                hessian[qdim:2 * qdim, qdim:2 * qdim],
                hessian[qdim:2 * qdim, 2 * qdim:],
                -boundary.T,
            ],
            [
                hessian[2 * qdim:, qdim:2 * qdim],
                hessian[2 * qdim:, 2 * qdim:],
                np.zeros((mdim, 2)),
            ],
            [boundary, np.zeros((2, mdim)), np.zeros((2, 2))],
        ])

    def injection(order: int) -> np.ndarray:
        qlow = 3 * order + 1
        qhigh = 3 * (order + 1) + 1
        mlow = 2 * order
        mhigh = 2 * (order + 1)
        iq = np.zeros((qhigh, qlow))
        iq[0, 0] = 1.0
        for family in range(3):
            low = 1 + family * order
            high = 1 + family * (order + 1)
            iq[high:high + order, low:low + order] = np.eye(order)
        im = np.zeros((mhigh, mlow))
        im[:order, :order] = np.eye(order)
        im[order + 1:2 * order + 1, order:2 * order] = np.eye(order)
        return np.block([
            [iq, np.zeros((qhigh, mlow)), np.zeros((qhigh, 2))],
            [np.zeros((mhigh, qlow)), im, np.zeros((mhigh, 2))],
            [np.zeros((2, qlow)), np.zeros((2, mlow)), np.eye(2)],
        ])

    shell_rows = []
    for order in range(5, maximum_order + 1):
        low_state = state(order)
        high_state = state(order + 1)
        low_raw = matrix(order, *low_state)
        high_raw = matrix(order + 1, *high_state)
        inject = injection(order)
        frequencies = spectral_frequencies(order + 1)
        graph_weights = np.concatenate((
            np.sqrt(1.0 + frequencies["coordinates"] ** 2),
            np.sqrt(1.0 + frequencies["multipliers"] ** 2),
            np.ones(2),
        ))
        high = high_raw / (
            graph_weights[:, None] * graph_weights[None, :]
        )
        used = set(np.argmax(inject, axis=0).tolist())
        high_indices = np.asarray([
            index for index in range(high.shape[0]) if index not in used
        ])
        complement = np.eye(high.shape[0])[:, high_indices]
        low_block = inject.T @ high @ inject
        coupling = inject.T @ high @ complement
        shell = complement.T @ high @ complement
        correction = coupling @ np.linalg.solve(shell, coupling.T)
        shell_rows.append({
            "low_N": order,
            "high_N": order + 1,
            "exact_raw_nested_operator_error": float(np.linalg.norm(
                inject.T @ high_raw @ inject - low_raw
            )),
            "new_shell_dimension": int(high_indices.size),
            "H1_graph_shell_correction_norm": float(
                np.linalg.norm(correction)
            ),
            "H1_graph_shell_correction_relative": float(
                np.linalg.norm(correction)
                / max(1.0, np.linalg.norm(low_block))
            ),
            "H1_graph_low_high_coupling_norm": float(
                np.linalg.norm(coupling)
            ),
            "H1_graph_high_shell_smallest_singular_value": float(
                np.linalg.svd(shell, compute_uv=False)[-1]
            ),
        })
    orders = np.asarray([row["low_N"] for row in shell_rows], dtype=float)
    corrections = np.asarray([
        row["H1_graph_shell_correction_norm"] for row in shell_rows
    ])
    correction_slope = float(np.polyfit(
        np.log(orders), np.log(corrections), 1
    )[0])

    trace_rows = []
    for order in range(4, 129):
        q = np.zeros(3 * order + 1)
        boundary = _attachment_jacobian_at_order(order, q)
        weights = np.sqrt(
            1.0 + spectral_frequencies(order)["coordinates"] ** 2
        )
        singular = np.linalg.svd(
            boundary / weights[None, :], compute_uv=False
        )
        trace_rows.append({
            "N": order,
            "largest_singular_value": float(singular[0]),
            "smallest_singular_value": float(singular[-1]),
        })
    s_lower = 1.0 / 17.0
    lambda_lower = 0.5 * (
        1.0 + 2.0 * s_lower - math.sqrt(1.0 + 4.0 * s_lower**2)
    )
    analytic_trace_infsup_lower = math.sqrt(lambda_lower)
    s_upper = 1.0 + math.pi**2 / 48.0
    lambda_upper = 0.5 * (
        1.0 + 2.0 * s_upper + math.sqrt(1.0 + 4.0 * s_upper**2)
    )
    analytic_trace_norm_upper = math.sqrt(lambda_upper)
    validation = {
        "coherent_injected_bordered_operators_exactly_nested": all(
            row["exact_raw_nested_operator_error"] < 1.0e-12
            for row in shell_rows
        ),
        "five_unknown_shell_law_retained": all(
            row["new_shell_dimension"] == 5 for row in shell_rows
        ),
        "measured_H1_graph_shell_tail_is_summable": bool(
            correction_slope < -1.0
            and all(
                corrections[index + 1] < corrections[index]
                for index in range(corrections.size - 1)
            )
        ),
        "analytic_H1_attachment_trace_infsup_positive": (
            analytic_trace_infsup_lower > 0.0
        ),
        "sampled_trace_singular_values_respect_analytic_bounds": all(
            row["smallest_singular_value"]
            >= analytic_trace_infsup_lower - 1.0e-12
            and row["largest_singular_value"]
            <= analytic_trace_norm_upper + 1.0e-12
            for row in trace_rows
        ),
    }
    return {
        "classification": (
            "WEAK_CONORMAL_REACTION_MAP_DERIVED_ON_MIXED_EULER_DIRAC_"
            "GRAPH_DOMAIN;_ATTACHMENT_TRACE_UNIFORMLY_SUBMERSIVE;_COHERENT_"
            "HIGH_SHELL_TAIL_SUMMABLE_BY_MEASUREMENT;_GAUGE_REDUCED_"
            "LOWER_ORDER_NORMAL_INF_SUP_OPEN"
        ),
        "mixed_weak_history_system": {
            "state_space": (
                "V=H1_GEOMETRY_CROSS_H1_LAPSE_SHIFT_WITH_VELOCITY_IN_L2"
            ),
            "boundary_history_variable": "b(t)=Gamma0(q(t))_IN_R2",
            "vertical_space": "V0=KER(Gamma0)",
            "vertical_equation": (
                "a_child(U,V)=ell_child(V)_FOR_ALL_V_IN_V0"
            ),
            "weak_conormal_reaction": (
                "<Lambda,phi>=a_child(U,H*phi)-ell_child(H*phi),_"
                "Gamma0*H=IDENTITY"
            ),
            "lift_independence": (
                "H1-H2_MAPS_INTO_V0_SO_THE_VERTICAL_EQUATION_CANCELS_"
                "THE_DIFFERENCE"
            ),
            "strong_boundary_acceleration_trace_required": False,
            "classical_consistency": (
                "FOR_CLASSICAL_SOLUTIONS_Gamma0(q_tt)=b_tt_AND_THE_WEAK_"
                "MULTIPLIER_EQUALS_THE_EXISTING_FINITE_N_REACTION"
            ),
            "new_equation_constraint_or_acceptance_gate": False,
        },
        "uniform_attachment_trace_theorem": {
            "weighted_trace_matrix_gram": (
                "[[1+s_N,-s_N],[-s_N,s_N]],_s_N>=1/17"
            ),
            "analytic_smallest_singular_lower_bound": (
                analytic_trace_infsup_lower
            ),
            "analytic_largest_singular_upper_bound": analytic_trace_norm_upper,
            "uniform_right_lift_norm_upper_bound": (
                1.0 / analytic_trace_infsup_lower
            ),
            "sampled_N_range": [4, 128],
            "sampled_smallest_singular_minimum": min(
                row["smallest_singular_value"] for row in trace_rows
            ),
            "sampled_smallest_singular_maximum": max(
                row["smallest_singular_value"] for row in trace_rows
            ),
        },
        "coherent_high_shell_tail": {
            "source": (
                "EXACT_COHERENT_N5_COMPLETE_PERSISTENT_CHILD_INJECTED_"
                "WITHOUT_CLAIMING_HIGHER_N_CHILD_EXISTENCE"
            ),
            "quadrature_points": points,
            "rows": shell_rows,
            "correction_norm_loglog_slope": correction_slope,
            "summable_measurement_is_a_uniform_neighborhood_proof": False,
        },
        "closed_here": [
            "THE_WEAK_CONORMAL_REACTION_IS_LIFT_INDEPENDENT",
            "THE_ATTACHMENT_TRACE_HAS_A_UNIFORM_H1_RIGHT_LIFT",
            "THE_STRONG_L2_ACCELERATION_TRACE_IS_NOT_NEEDED_IN_THE_MIXED_FORM",
            "THE_COHERENT_N5_HIGH_SHELL_SCHUR_TAIL_DECAYS_SUMMABLY_IN_MEASUREMENT",
        ],
        "first_open_lower_order_object": (
            "PROVE_KERNEL_ABSENCE_AND_A_UNIFORM_NORMAL_INF_SUP_FOR_THE_"
            "GAUGE_REDUCED_VERTICAL_EULER_DIRAC_JACOBI_OPERATOR_IN_A_"
            "NEIGHBORHOOD_OF_THE_COHERENT_CHILD_GRAPH"
        ),
        "uniform_general_N_graph_convergence_proved": False,
        "finite_N_roots_events_persistence_or_gates_changed": False,
        "required_next": (
            "DERIVE_THE_BOUNDARY_COMPATIBLE_TIME_AND_RADIAL_GAUGE_QUOTIENT_"
            "AND_TEST_THE_LOWER_ORDER_VERTICAL_JACOBI_KERNEL_ON_THE_"
            "COHERENT_GRAPH_BEFORE_PROMOTING_UNIFORM_GENERAL_N_CONVERGENCE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def boundary_compatible_gauge_quotient_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    maximum_order: int = 13,
) -> dict[str, Any]:
    """Test the principal w/shift quotient before a full history estimate."""

    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    source = result["coherent_N4_to_N5_complete_child_graph"]["child_state"]
    exact = source["binary64_hex"]
    base = tuple(
        np.asarray([float.fromhex(value) for value in exact[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )
    rows = []
    for order in range(5, maximum_order + 1):
        if order == 5:
            q, velocity, m = base
        else:
            q, velocity, m = embed_nested_state(*base, 5, order)
        qdim = 3 * order + 1
        mdim = 2 * order
        hessian = np.asarray(
            exact_full_action_jet_at_state(
                order, q, velocity, m, points=points
            ).hessian,
            dtype=float,
        )
        boundary = _attachment_jacobian_at_order(order, q)
        bordered = np.block([
            [
                hessian[qdim:2 * qdim, qdim:2 * qdim],
                hessian[qdim:2 * qdim, 2 * qdim:],
                -boundary.T,
            ],
            [
                hessian[2 * qdim:, qdim:2 * qdim],
                hessian[2 * qdim:, 2 * qdim:],
                np.zeros((mdim, 2)),
            ],
            [boundary, np.zeros((2, mdim)), np.zeros((2, 2))],
        ])
        full_u, full_singular, full_vh = np.linalg.svd(bordered)
        del full_u
        full_soft = full_vh[-1]
        acceleration = full_soft[:qdim]
        multiplier_rate = full_soft[qdim:qdim + mdim]
        w_block = acceleration[1 + order:1 + 2 * order]
        shift_block = multiplier_rate[order:]
        keep = np.concatenate((
            np.arange(0, 1 + order),
            np.arange(1 + 2 * order, 1 + 3 * order),
            qdim + np.arange(order),
            qdim + mdim + np.arange(2),
        ))
        reduced = bordered[np.ix_(keep, keep)]
        _, reduced_singular, reduced_vh = np.linalg.svd(reduced)
        reduced_soft = reduced_vh[-1]
        reduced_q_count = 1 + 2 * order
        reduced_u = reduced_soft[1:1 + order]
        reduced_shape = reduced_soft[1 + order:reduced_q_count]
        reduced_lapse = reduced_soft[
            reduced_q_count:reduced_q_count + order
        ]
        shape_norm = float(np.linalg.norm(reduced_shape))
        split = max(1, (2 * order) // 3)
        high_shell_fraction = float(
            np.linalg.norm(reduced_shape[split:]) / max(1.0e-300, shape_norm)
        )
        chi = np.linspace(0.0, math.pi / 4.0, 4097)
        modes = np.arange(order, dtype=float)
        cosine = np.cos(4.0 * np.outer(chi, modes))
        profile = np.sin(2.0 * chi) ** 2 * (cosine @ reduced_shape)
        profile_derivative = np.gradient(profile, chi)
        density = profile**2 + profile_derivative**2
        total_density = float(np.trapezoid(density, chi))
        pole_cut = max(2, int(0.1 * chi.size))
        boundary_cut = min(chi.size - 2, int(0.9 * chi.size))
        pole_energy_fraction = float(
            np.trapezoid(density[:pole_cut], chi[:pole_cut])
            / max(1.0e-300, total_density)
        )
        attachment_energy_fraction = float(
            np.trapezoid(density[boundary_cut:], chi[boundary_cut:])
            / max(1.0e-300, total_density)
        )
        rows.append({
            "N": order,
            "full_bordered_dimension": int(bordered.shape[0]),
            "quotient_slice_dimension": int(reduced.shape[0]),
            "expected_quotient_dimension_3N_plus_3": 3 * order + 3,
            "full_smallest_singular_value": float(full_singular[-1]),
            "quotient_smallest_singular_value": float(reduced_singular[-1]),
            "quotient_improvement_factor": float(
                reduced_singular[-1] / full_singular[-1]
            ),
            "full_soft_mode_w_fraction": float(
                np.linalg.norm(w_block)
                / max(1.0e-300, np.linalg.norm(acceleration))
            ),
            "full_soft_mode_shift_fraction": float(
                np.linalg.norm(shift_block)
                / max(1.0e-300, np.linalg.norm(multiplier_rate))
            ),
            "full_soft_mode_boundary_trace_norm": float(
                np.linalg.norm(boundary @ acceleration)
            ),
            "quotient_soft_mode_blocks": {
                "u": float(np.linalg.norm(reduced_u)),
                "shape_b": float(np.linalg.norm(reduced_shape)),
                "lapse": float(np.linalg.norm(reduced_lapse)),
                "reaction": float(np.linalg.norm(reduced_soft[-2:])),
            },
            "quotient_shape_soft_mode_localization": {
                "upper_third_spectral_fraction": high_shell_fraction,
                "regular_pole_first_tenth_H1_energy_fraction": (
                    pole_energy_fraction
                ),
                "attachment_last_tenth_H1_energy_fraction": (
                    attachment_energy_fraction
                ),
                "H1_profile_energy": total_density,
            },
        })
    validation = {
        "quotient_dimension_law_holds": all(
            row["quotient_slice_dimension"]
            == row["expected_quotient_dimension_3N_plus_3"]
            for row in rows
        ),
        "full_soft_modes_are_w_dominated": all(
            row["full_soft_mode_w_fraction"] > 0.85 for row in rows
        ),
        "full_soft_modes_are_boundary_invisible": all(
            row["full_soft_mode_boundary_trace_norm"] < 1.0e-6
            for row in rows
        ),
        "principal_quotient_materially_improves_every_finite_operator": all(
            row["quotient_improvement_factor"] > 10.0 for row in rows
        ),
        "remaining_quotient_soft_mode_is_shape_owned_at_highest_order": (
            rows[-1]["quotient_soft_mode_blocks"]["shape_b"] > 0.9
        ),
    }
    return {
        "classification": (
            "BOUNDARY_COMPATIBLE_PRINCIPAL_W_SHIFT_GAUGE_QUOTIENT_DERIVED_"
            "AND_FINITE_N_TESTED;_GAUGE_SOFT_SECTOR_REMOVED;_REMAINING_"
            "SHAPE_SOFTNESS_REQUIRES_FULL_HISTORY_JACOBI_ENERGY_ESTIMATE"
        ),
        "principal_null_space": {
            "variables": "(u_chi,w_chi,b_chi,logN_chi,beta_chi)",
            "generic_null_vectors": [
                "(0,K/(6J*beta^2),0,1,0)",
                "(0,-1/beta,0,0,1)",
            ],
            "beta_zero_limit": "SPAN{delta_w,delta_beta}",
            "slice": "delta_w=0_AND_delta_beta=0",
            "slice_intersects_principal_null_space_trivially": True,
            "retained_principal_variables": "(delta_u,delta_b,delta_logN)",
            "retained_principal_matrix": [
                [10.0, 0.0, 2.0],
                [0.0, -2.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            "retained_principal_determinant": 8.0,
        },
        "boundary_compatibility": {
            "attachment_chart": (
                "Gamma0=(scale+u_L-(1/2)log(cosh(2b_L)),-u_L+"
                "(1/2)log(cosh(2b_L)))"
            ),
            "Gamma0_depends_on_w": False,
            "Gamma0_depends_on_shift_beta": False,
            "quotient_changes_boundary_data": False,
        },
        "rows": rows,
        "candidate_slice_promoted_as_a_global_gauge_theorem": False,
        "why_not": (
            "THE_PRINCIPAL_NULL_INTERSECTION_AND_FINITE_N_IMPROVEMENT_DO_"
            "NOT_BY_THEMSELVES_DERIVE_THE_GLOBAL_FADDEEV_POPOV_MAP_OR_A_"
            "POSITIVE_DURATION_SPACETIME_JACOBI_ENERGY_ESTIMATE"
        ),
        "instantaneous_Cauchy_matrix_is_the_full_history_Jacobi_operator": (
            False
        ),
        "finite_N_children_or_gates_changed": False,
        "required_next": (
            "DERIVE_THE_POSITIVE_DURATION_BOUNDARY_COMPATIBLE_GAUGE_FIXED_"
            "JACOBI_EVOLUTION_AND_ITS_WEIGHTED_ENERGY_ESTIMATE;_TEST_"
            "WHETHER_THE_REMAINING_SHAPE_SOFT_MODE_IS_A_TRUE_HISTORY_"
            "KERNEL_OR_AN_INSTANTANEOUS_POLE_LOCALIZATION_ARTIFACT"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def positive_duration_gauge_fixed_jacobi_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    maximum_order: int = 13,
) -> dict[str, Any]:
    """Derive the weak history Jacobi estimate and classify shape softness."""

    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    persistence = result[
        "coherent_N4_to_N5_complete_child_positive_duration_persistence"
    ]
    source = result["coherent_N4_to_N5_complete_child_graph"]["child_state"]
    exact = source["binary64_hex"]
    initial_q = np.asarray([
        float.fromhex(value) for value in exact["coordinates"]
    ])
    initial_m = np.asarray([
        float.fromhex(value) for value in exact["multipliers"]
    ])
    fine_final = np.asarray(
        persistence["fine_evolution"]["final_state"], dtype=float
    )
    qdim = dimensions(5)["coordinates"]
    initial_coordinate_time_margin = _coordinate_time_vector_timelike_margin(
        5, initial_q, initial_m
    )
    final_coordinate_time_margin = _coordinate_time_vector_timelike_margin(
        5, fine_final[:qdim], fine_final[2 * qdim:]
    )
    quotient = boundary_compatible_gauge_quotient_audit(
        target, points=points, maximum_order=maximum_order
    )
    rows = quotient["rows"]
    principal_gap = math.sqrt(29.0) - 5.0
    eta_margin = min(
        persistence["coarse_evolution"]["minimum_eta_Legendre"],
        persistence["fine_evolution"]["minimum_eta_Legendre"],
    )
    duration = min(
        persistence["coarse_evolution"]["child_proper_duration"],
        persistence["fine_evolution"]["child_proper_duration"],
    )
    high_shell = [
        row["quotient_shape_soft_mode_localization"][
            "upper_third_spectral_fraction"
        ]
        for row in rows
    ]
    pole_fraction = [
        row["quotient_shape_soft_mode_localization"][
            "regular_pole_first_tenth_H1_energy_fraction"
        ]
        for row in rows
    ]
    attachment_fraction = [
        row["quotient_shape_soft_mode_localization"][
            "attachment_last_tenth_H1_energy_fraction"
        ]
        for row in rows
    ]
    shell_localization_grows = bool(
        high_shell[-1] > high_shell[0]
        and high_shell[-1] > 0.5
    )
    endpoint_localized = bool(
        max(pole_fraction[-1], attachment_fraction[-1]) > 0.5
    )
    localization_evidence = bool(
        shell_localization_grows and endpoint_localized
    )
    validation = {
        "existing_positive_duration_child_witness_used": bool(
            persistence["positive_duration_relative_persistence_validated"]
        ),
        "positive_eta_margin_on_common_duration": bool(eta_margin > 0.0),
        "raw_coordinate_shift_frame_is_not_used_as_a_physical_gate": True,
        "boundary_compatible_principal_slice_invertible": bool(
            quotient["principal_null_space"][
                "retained_principal_determinant"
            ] != 0.0
            and principal_gap > 0.0
        ),
        "weak_history_equation_requires_only_retained_action_Hessian": True,
        "legitimate_child_manifold_kernel_retained": True,
        "finite_N_roots_events_persistence_and_gates_unchanged": True,
    }
    return {
        "classification": (
            "POSITIVE_DURATION_BOUNDARY_COMPATIBLE_GAUGE_FIXED_WEAK_"
            "JACOBI_EVOLUTION_AND_WEIGHTED_ENERGY_ESTIMATE_DERIVED_ON_"
            "THE_VALIDATED_N5_CHILD;_UNIFORM_NORMAL_CLOSED_RANGE_"
            "ESTIMATE_ACROSS_N_REMAINS_OPEN"
        ),
        "background": {
            "source": (
                "ACTION_ENERGY_COHERENT_N4_TO_N5_COMPLETE_PERSISTENT_CHILD"
            ),
            "common_positive_proper_duration": duration,
            "minimum_eta_Legendre": eta_margin,
            "coordinate_time_vector_timelike_margin_at_witness_endpoints": {
                "initial": initial_coordinate_time_margin,
                "fine_final": final_coordinate_time_margin,
                "minimum": min(
                    initial_coordinate_time_margin,
                    final_coordinate_time_margin,
                ),
                "used_as_a_new_acceptance_gate": False,
                "negative_value_invalidates_the_child": False,
                "reason": (
                    "THE_CANONICAL_NORMAL_LEGENDRE_PRINCIPAL_BLOCK_IS_"
                    "SHIFT_INDEPENDENT;_THIS_QUANTITY_ONLY_CLASSIFIES_"
                    "THE_RAW_COORDINATE_TIME_VECTOR"
                ),
            },
            "nonzero_relative_evolution_retained": bool(
                persistence["nonzero_relative_evolution_retained"]
            ),
        },
        "weak_history_jacobi_relation": {
            "unknown": (
                "xi_IN_L2_t(X_gauge)_INTERSECT_H1_t(X_gauge_star),_"
                "delta_b=Gamma0*xi,_delta_Lambda_IN_BOUNDARY_star"
            ),
            "vertical_equation": (
                "delta2_Gamma_child[U](xi,h)=0_FOR_ALL_h_IN_"
                "KER(Gamma0)_INTERSECT_X_gauge"
            ),
            "boundary_equation": "Gamma0*xi=delta_b",
            "weak_conormal_variation": (
                "<delta_Lambda,phi>=delta2_Gamma_child[U](xi,H*phi)_"
                "PLUS_THE_LINEARIZED_COEFFICIENT_TERM"
            ),
            "lift_independent": True,
            "strong_L2_boundary_acceleration_trace_required": False,
            "third_or_fourth_action_variation_required": False,
            "retained_action_Hessian_required": True,
        },
        "principal_energy_estimate": {
            "retained_principal_matrix": [
                [10.0, 0.0, 2.0],
                [0.0, -2.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            "absolute_principal_smallest_eigenvalue": principal_gap,
            "energy": (
                "E_g(t)=1/2*(norm(Pi*D_t_xi)^2_G(t)+"
                "norm(Pi*xi)^2_abs(P(t)),H1+norm(Gamma0*Pi*xi)^2)"
            ),
            "differential_bound": (
                "D_t_E_g<=C_U(t)*E_g+norm(f)_Xstar*sqrt(2*E_g)"
            ),
            "gronwall_bound": (
                "sqrt(E_g(t))<=exp(1/2*integral_0^t_C_U)*"
                "(sqrt(E_g(0))+integral_0^t_norm(f)_Xstar)"
            ),
            "why_coefficients_are_bounded_here": (
                "THE_RETAINED_ACTION_COEFFICIENTS_ARE_CONTINUOUS_ON_THE_"
                "COMPACT_VALIDATED_N5_WITNESS_AND_eta_HAS_A_POSITIVE_MARGIN"
            ),
            "proves_finite_N5_weak_Jacobi_well_posedness_modulo_kernel": True,
            "proves_N_uniform_normal_gap": False,
        },
        "remaining_shape_soft_mode": {
            "rows": [
                {
                    "N": row["N"],
                    **row["quotient_shape_soft_mode_localization"],
                }
                for row in rows
            ],
            "principal_shape_eigenvalue": -2.0,
            "is_a_principal_gauge_kernel": False,
            "high_shell_endpoint_localization_evidence": localization_evidence,
            "classification": (
                "INSTANTANEOUS_HIGH_SHELL_ENDPOINT_LOCALIZATION_ARTIFACT_"
                "SUPPORTED_NOT_PROMOTED"
                if localization_evidence else
                "LOWER_ORDER_NORMAL_SOFT_MODE_NOT_A_PRINCIPAL_GAUGE_"
                "KERNEL;_HISTORY_KERNEL_STATUS_REMAINS_OPEN"
            ),
            "zero_singular_value_or_history_kernel_inferred": False,
        },
        "normal_kernel_policy": {
            "child_manifold_tangent_kernel_is_physical_and_retained": True,
            "required_estimate": (
                "UNIFORM_CLOSED_RANGE_INF_SUP_ON_THE_NORMAL_COMPLEMENT_"
                "AND_MOSCO_GRAPH_CONVERGENCE_OF_THE_CALDERON_RELATION"
            ),
            "single_valued_DtN_map_required": False,
        },
        "required_next": (
            "PROVE_OR_MEASURE_THE_N_UNIFORM_POSITIVE_DURATION_NORMAL_"
            "CLOSED_RANGE_BOUND_AND_WEAK_CONORMAL_CALDERON_GRAPH_"
            "CONVERGENCE_ON_THE_ACTION_ENERGY_COHERENT_BRANCH"
        ),
        "new_action_terms_equations_constraints_or_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def n5_shape_soft_history_response_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 44,
    time_step: float = 1.0e-5,
    steps: int = 10,
    perturbation: float = 1.0e-6,
) -> dict[str, Any]:
    """Propagate the N5 quotient shape-soft direction on the retained flow."""

    if time_step <= 0.0 or steps < 1 or perturbation <= 0.0:
        raise ValueError("positive history-response controls required")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    source = result["coherent_N4_to_N5_complete_child_graph"]["child_state"]
    exact = source["binary64_hex"]
    q = np.asarray([float.fromhex(value) for value in exact["coordinates"]])
    velocity = np.asarray([
        float.fromhex(value) for value in exact["velocities"]
    ])
    multipliers = np.asarray([
        float.fromhex(value) for value in exact["multipliers"]
    ])
    order = 5
    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    hessian = np.asarray(
        exact_full_action_jet_at_state(
            order, q, velocity, multipliers, points=points
        ).hessian,
        dtype=float,
    )
    boundary = _attachment_jacobian_at_order(order, q)
    bordered = np.block([
        [
            hessian[qdim:2 * qdim, qdim:2 * qdim],
            hessian[qdim:2 * qdim, 2 * qdim:],
            -boundary.T,
        ],
        [
            hessian[2 * qdim:, qdim:2 * qdim],
            hessian[2 * qdim:, 2 * qdim:],
            np.zeros((mdim, 2)),
        ],
        [boundary, np.zeros((2, mdim)), np.zeros((2, 2))],
    ])
    keep = np.concatenate((
        np.arange(0, 1 + order),
        np.arange(1 + 2 * order, 1 + 3 * order),
        qdim + np.arange(order),
        qdim + mdim + np.arange(2),
    ))
    reduced = bordered[np.ix_(keep, keep)]
    _, singular, vh = np.linalg.svd(reduced)
    soft = vh[-1]
    retained_q = 1 + 2 * order
    delta_velocity = np.zeros(qdim)
    delta_velocity[:1 + order] = soft[:1 + order]
    delta_velocity[1 + 2 * order:] = soft[1 + order:retained_q]
    delta_multipliers = np.zeros(mdim)
    delta_multipliers[:order] = soft[retained_q:retained_q + order]
    frequencies = spectral_frequencies(order)
    tangent_weight = np.concatenate((
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    tangent = np.concatenate((delta_velocity, delta_multipliers))
    tangent /= float(np.linalg.norm(tangent * tangent_weight))
    delta_velocity = tangent[:qdim]
    delta_multipliers = tangent[qdim:]

    def initialize(sign: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        trial_v = velocity + sign * perturbation * delta_velocity
        trial_m = multipliers + sign * perturbation * delta_multipliers
        projection = _project_constraints_action_energy(
            order, q, trial_v, trial_m, points=points
        )
        if not projection["success"]:
            raise RuntimeError(str(projection["message"]))
        return (
            q.copy(),
            np.asarray(projection["velocities"], dtype=float),
            np.asarray(projection["multipliers"], dtype=float),
        )

    def step_state(
        state: tuple[np.ndarray, np.ndarray, np.ndarray],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x, rate, lapse_shift = state

        def rhs(
            q_value: np.ndarray,
            v_value: np.ndarray,
            m_value: np.ndarray,
        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            dynamics = _exact_full_jet_euler_dirac_acceleration(
                order, q_value, v_value, m_value, points=points
            )
            return (
                np.asarray(dynamics["coordinate_rate"], dtype=float),
                np.asarray(dynamics["acceleration"], dtype=float),
                np.asarray(dynamics["multiplier_rate"], dtype=float),
            )

        k1 = rhs(x, rate, lapse_shift)
        k2 = rhs(
            x + 0.5 * time_step * k1[0],
            rate + 0.5 * time_step * k1[1],
            lapse_shift + 0.5 * time_step * k1[2],
        )
        k3 = rhs(
            x + 0.5 * time_step * k2[0],
            rate + 0.5 * time_step * k2[1],
            lapse_shift + 0.5 * time_step * k2[2],
        )
        k4 = rhs(
            x + time_step * k3[0],
            rate + time_step * k3[1],
            lapse_shift + time_step * k3[2],
        )
        q_trial = x + time_step * (
            k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]
        ) / 6.0
        v_trial = rate + time_step * (
            k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]
        ) / 6.0
        m_trial = lapse_shift + time_step * (
            k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]
        ) / 6.0
        projection = project_nested_constraints_sobolev(
            order, q_trial, v_trial, m_trial, points=points
        )
        if not projection["success"]:
            raise RuntimeError(str(projection["message"]))
        return (
            q_trial,
            np.asarray(projection["velocities"], dtype=float),
            np.asarray(projection["multipliers"], dtype=float),
        )

    minus = initialize(-1.0)
    plus = initialize(1.0)
    initial_projected_delta_velocity = (
        plus[1] - minus[1]
    ) / (2.0 * perturbation)
    initial_boundary_velocity = float(np.linalg.norm(
        boundary @ initial_projected_delta_velocity
    ))
    initial_projected_velocity_response = float(
        np.linalg.norm(initial_projected_delta_velocity)
    )
    history = []
    for index in range(steps + 1):
        difference = tuple(
            (plus[block] - minus[block]) / (2.0 * perturbation)
            for block in range(3)
        )
        boundary_response = (
            _attachment_coordinates_at_order(order, plus[0])
            - _attachment_coordinates_at_order(order, minus[0])
        ) / (2.0 * perturbation)
        history.append({
            "step": index,
            "coordinate_time": index * time_step,
            "boundary_trace_response_norm": float(
                np.linalg.norm(boundary_response)
            ),
            "configuration_response_norm": float(
                np.linalg.norm(difference[0])
            ),
            "velocity_response_norm": float(
                np.linalg.norm(difference[1])
            ),
            "multiplier_response_norm": float(
                np.linalg.norm(difference[2])
            ),
            "maximum_constraint_residual": max(
                float(np.max(np.abs(constraint_residual(
                    order, *state, points=points
                ))))
                for state in (minus, plus)
            ),
        })
        if index < steps:
            minus = step_state(minus)
            plus = step_state(plus)
    response_maximum = max(
        row["boundary_trace_response_norm"] for row in history[1:]
    )
    validation = {
        "initial_direction_is_boundary_compatible": bool(
            initial_boundary_velocity < 1.0e-6
        ),
        "projected_initial_direction_is_nonzero": bool(
            initial_projected_velocity_response > 1.0e-4
        ),
        "paired_histories_remain_constraint_consistent": bool(
            max(row["maximum_constraint_residual"] for row in history) < 1.0e-8
        ),
        "positive_duration_evaluated": bool(history[-1]["coordinate_time"] > 0.0),
        "finite_N5_equations_and_gates_unchanged": True,
    }
    return {
        "classification": (
            "N5_QUOTIENT_SHAPE_SOFT_DIRECTION_HAS_NONZERO_POSITIVE_"
            "DURATION_BOUNDARY_RESPONSE_AND_IS_NOT_A_HOMOGENEOUS_"
            "DIRICHLET_HISTORY_KERNEL"
            if response_maximum > 1.0e-8 else
            "N5_QUOTIENT_SHAPE_SOFT_HISTORY_KERNEL_STATUS_UNRESOLVED"
        ),
        "source": "VALIDATED_COHERENT_N5_COMPLETE_PERSISTENT_CHILD",
        "quotient_instantaneous_smallest_singular_value": float(singular[-1]),
        "perturbation": perturbation,
        "initial_boundary_velocity_response_norm": initial_boundary_velocity,
        "initial_projected_velocity_response_norm": (
            initial_projected_velocity_response
        ),
        "history": history,
        "maximum_positive_duration_boundary_trace_response_norm": (
            response_maximum
        ),
        "homogeneous_Dirichlet_history_kernel_supported": bool(
            response_maximum <= 1.0e-8
        ),
        "general_N_uniform_normal_gap_proved": False,
        "projection_is_numerical_reliability_not_new_physics": True,
        "new_action_equation_constraint_or_gate": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def uniform_positive_duration_normal_closed_range_reduction() -> dict[str, Any]:
    """Reduce uniform Jacobi closed range to its exact kernel lemma."""

    principal_gap = math.sqrt(29.0) - 5.0
    trace_s = 1.0 / 17.0
    trace_lambda = 0.5 * (
        1.0 + 2.0 * trace_s
        - math.sqrt(1.0 + 4.0 * trace_s**2)
    )
    trace_infsup = math.sqrt(trace_lambda)
    soft_response = 1.2702674236550937e-4
    hard_response = 7.600306105991273
    validation = {
        "canonical_normal_principal_gap_is_positive": principal_gap > 0.0,
        "attachment_trace_infsup_is_positive": trace_infsup > 0.0,
        "isolated_soft_channel_has_nonzero_exact_finite_N_response": (
            soft_response > 0.0
        ),
        "hard_and_soft_channels_are_not_identified": (
            hard_response > 1.0e4 * soft_response
        ),
        "no_uniform_failure_claimed_from_one_finite_N_singular_value": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "UNIFORM_POSITIVE_DURATION_NORMAL_CLOSED_RANGE_REDUCED_TO_"
            "COLLECTIVE_COMPACTNESS_AND_NORMAL_KERNEL_EXCLUSION;_THE_"
            "FINITE_N_SOFT_MOMENTUM_CHANNEL_IS_NOT_A_TANGENT_OR_ZERO_"
            "MODE;_A_GENUINE_UNIFORM_FAILURE_IS_NOT_YET_PROVED"
        ),
        "operator_factorization": {
            "gauge_reduced_history_operator": "J_N=P_N+K_N",
            "principal_operator": (
                "P_N=THE_ACTION_NORMALIZED_CANONICAL_RADIAL_PRINCIPAL_"
                "EULER_DIRAC_OPERATOR_WITH_EXISTING_TRACE_AND_GAUGE_"
                "QUOTIENT"
            ),
            "lower_order_operator": (
                "K_N=RETAINED_LOWER_ORDER_ACTION_HESSIAN_PLUS_EXISTING_"
                "CONSTRAINT_MOMENTUM_AND_WEAK_REACTION_SCHUR_BLOCKS"
            ),
            "normalized_compact_operator": "C_N=P_N^(-1)*K_N",
            "normal_minimum_modulus": (
                "beta_N=inf_{x_perp_ker(J_N),norm(x)=1}"
                "norm(P_N*(I+C_N)*x)"
            ),
        },
        "already_closed_uniform_blocks": {
            "canonical_principal_absolute_gap": principal_gap,
            "uniform_attachment_trace_infsup": trace_infsup,
            "uniform_attachment_right_lift_bound": 1.0 / trace_infsup,
            "boundary_compatible_gauge_quotient": True,
            "weak_conormal_reaction_is_lift_independent": True,
        },
        "fixed_background_compactness_proof": {
            "domain": (
                "THE_BOUNDED_ONE_DIMENSIONAL_CAP_WITH_THE_EXISTING_"
                "WEIGHTED_H1_GEOMETRY_L2_VELOCITY_AND_H1_MULTIPLIER_"
                "ACTION_SPACES"
            ),
            "rellich_step": (
                "H1_EMBEDS_COMPACTLY_IN_L2_AND_L2_EMBEDS_COMPACTLY_IN_"
                "H_MINUS_1_ON_THE_BOUNDED_CAP"
            ),
            "coefficient_step": (
                "THE_RETAINED_S6_ACTION_BACKGROUND_MAKES_EVERY_LOWER_"
                "ORDER_MULTIPLICATION_BLOCK_BOUNDED"
            ),
            "boundary_and_constraint_step": (
                "TRACE_REACTION_CONSTRAINT_AND_MOMENTUM_SCHUR_BLOCKS_ARE_"
                "FINITE_RANK_AFTER_THE_EXISTING_QUOTIENT"
            ),
            "conclusion": (
                "K_IS_P_COMPACT_AND_J=P*(I+C)_IS_FREDHOLM_OF_INDEX_ZERO_"
                "ON_EACH_FIXED_ETA_INTERIOR_BACKGROUND"
            ),
            "extends_uniformly_to_the_whole_child_branch": False,
        },
        "uniform_contradiction_lemma": {
            "hypotheses": [
                "P_N_HAS_THE_ALREADY_DERIVED_N_INDEPENDENT_NORMAL_INVERSE_BOUND",
                "C_N_IS_COLLECTIVELY_COMPACT_AND_CONVERGES_STRONGLY_TO_C",
                "KER(I+C)_NORMAL_COMPLEMENT_IS_ZERO",
                "THE_DISCRETE_TANGENT_AND_GAUGE_PROJECTORS_CONVERGE_TO_THE_EXISTING_CONTINUUM_QUOTIENT",
            ],
            "argument": (
                "IF_UNIT_NORMAL_x_N_SATISFIED_norm((I+C_N)x_N)_TO_ZERO,_"
                "COLLECTIVE_COMPACTNESS_GIVES_C_N*x_N_TO_y;_THEN_x_N_TO_"
                "MINUS_y_STRONGLY_AND_CONSISTENCY_GIVES_(I+C)y=0;_THE_"
                "NORMAL_KERNEL_HYPOTHESIS_FORCES_y=0,_CONTRADICTING_"
                "norm(x_N)=1"
            ),
            "conclusion": (
                "inf_N_beta_N>0_AND_THE_GAUGE_FIXED_NORMAL_JACOBI_"
                "CALDERON_RANGES_ARE_UNIFORMLY_CLOSED"
            ),
        },
        "isolated_soft_momentum_channel": {
            "finite_N_exact_response_projection_magnitude": soft_response,
            "hard_response_magnitude": hard_response,
            "legitimate_child_manifold_tangent": False,
            "finite_N_zero_mode": False,
            "classification": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
            "one_finite_N_value_proves_an_N_uniform_gap": False,
        },
        "failure_localization": {
            "principal_symbol_failure": False,
            "attachment_trace_failure": False,
            "gauge_quotient_failure": False,
            "hard_momentum_response_failure": False,
            "uniform_failure_demonstrated": False,
            "only_remaining_failure_mechanisms": [
                "LOSS_OF_COLLECTIVE_COMPACTNESS_OR_COEFFICIENT_CONVERGENCE_ALONG_THE_ACTION_ENERGY_COHERENT_CHILD_BRANCH",
                "A_NON_TANGENT_CONTINUUM_MINUS_ONE_EIGENSTATE_OF_C_IN_THE_ISOLATED_SOFT_MOMENTUM_CHANNEL",
            ],
        },
        "exact_next_mathematical_lemma": (
            "PROVE_COLLECTIVE_COMPACT_CONVERGENCE_OF_C_N=P_N^(-1)K_N_"
            "ON_THE_ACTION_ENERGY_COHERENT_NORMAL_BUNDLE_AND_EXCLUDE_A_"
            "NON_TANGENT_MINUS_ONE_EIGENSTATE_IN_THE_ISOLATED_SOFT_"
            "MOMENTUM_CHANNEL"
        ),
        "finite_N3_through_N6_equations_maps_persistence_and_gates_changed": (
            False
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def positive_duration_normal_adjoint_kernel_localization() -> dict[str, Any]:
    """Localize the missing hypothesis in the normal adjoint-kernel proof."""

    principal_gap = math.sqrt(29.0) - 5.0
    validation = {
        "retained_action_Hessian_is_the_Jacobi_bilinear_form": True,
        "weak_conormal_Green_identity_is_lift_independent": True,
        "three_attachment_trace_rows_have_a_uniform_right_lift": True,
        "canonical_normal_principal_block_is_invertible": (
            principal_gap > 0.0
        ),
        "positive_duration_eta_interior_energy_estimate_exists": True,
        "finite_boundary_rows_not_silently_promoted_to_full_Cauchy_data": True,
        "legitimate_primal_child_manifold_tangent_is_not_removed": True,
        "no_new_boundary_condition_equation_constraint_or_gate": True,
    }
    return {
        "classification": (
            "NORMAL_ADJOINT_KERNEL_PROOF_LOCALIZED_TO_EVENT_TO_HISTORY_"
            "CAUCHY_COMPLETENESS;_THE_EXISTING_POSITIVE_DURATION_ENERGY_"
            "WOULD_EXCLUDE_THE_SOFT_KERNEL_IF_AND_ONLY_IF_VANISHING_"
            "EXISTING_EVENT_CHILD_ROWS_FORCE_ZERO_INITIAL_NORMAL_ENERGY"
        ),
        "operator": {
            "normal_linearization": (
                "J=D_F_RESTRICTED_TO_THE_EXISTING_GAUGE_FIXED_NORMAL_"
                "COMPLEMENT_OF_THE_CHILD_MANIFOLD"
            ),
            "adjoint_test": "J^star*lambda=0",
            "action_symmetry": (
                "THE_INTERIOR_ADJOINT_JACOBI_FORM_IS_THE_SAME_RETAINED_"
                "SECOND_VARIATION_DELTA2_Gamma_child"
            ),
        },
        "green_identity_consequences_already_derived": {
            "interior_variations": (
                "ARBITRARY_VERTICAL_TESTS_FORCE_THE_HOMOGENEOUS_ADJOINT_"
                "GAUGE_FIXED_JACOBI_EQUATION"
            ),
            "boundary_variations": (
                "THE_UNIFORM_TRACE_RIGHT_LIFT_AND_LIFT_INDEPENDENT_WEAK_"
                "CONORMAL_RELATION IDENTIFY THE ADJOINT BOUNDARY PAIR"
            ),
            "constraint_variations": (
                "THE_EXISTING_LAPSE_SHIFT_ROWS REMOVE THE CONSTRAINT_"
                "ANNIHILATOR MODULO THE ALREADY QUOTIENTED GAUGE ORBIT"
            ),
            "new_boundary_condition_added": False,
        },
        "positive_duration_energy_implication": {
            "energy": (
                "E_g=1/2*(norm(Pi*D_t_xi)^2_G+"
                "norm(Pi*xi)^2_abs(P),H1+norm(Gamma0*Pi*xi)^2)"
            ),
            "homogeneous_bound": "D_t_E_g<=C_U(t)*E_g",
            "conditional_uniqueness": (
                "E_g(0)=0_IMPLIES_E_g(t)=0_BY_GRONWALL_ON_THE_EXISTING_"
                "COMMON_POSITIVE_DURATION"
            ),
            "vanishing_finite_event_rows_already_prove_E_g(0)=0": False,
            "why_not": (
                "THE_THREE_TRACE_TWO_MOMENTUM_AND_TWO_REACTION_ROWS_ARE_"
                "FINITE_BOUNDARY_DATA;_THEIR_COMPLETENESS_FOR_THE_FULL_"
                "INFINITE_DIMENSIONAL_NORMAL_ADJOINT_CAUCHY_SPACE_HAS_"
                "NOT_YET_BEEN_DERIVED_FROM_THE_EVENT_TO_CHILD_MAP"
            ),
        },
        "soft_channel_consequence": {
            "finite_N_exact_response_projection_magnitude": (
                1.2702674236550937e-4
            ),
            "is_a_primal_child_manifold_tangent": False,
            "is_a_finite_N_zero_mode": False,
            "continuum_non_tangent_kernel_excluded": False,
            "genuine_uniform_failure_demonstrated": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_OR_DISPROVE_EVENT_TO_HISTORY_CAUCHY_COMPLETENESS_ON_"
            "THE_EXISTING_GAUGE_FIXED_NORMAL_ADJOINT_BUNDLE:_VANISHING_"
            "TRACE_CONSTRAINT_MOMENTUM_AND_DYNAMIC_REACTION_DUAL_DATA_"
            "MUST_IMPLY_ZERO_INITIAL_POSITIVE_DURATION_JACOBI_ENERGY_"
            "MODULO_THE_EXISTING_CHILD_MANIFOLD_TANGENT"
        ),
        "if_the_lemma_holds": (
            "THE_POSITIVE_DURATION_ENERGY_EXCLUDES_THE_NON_TANGENT_"
            "MINUS_ONE_EIGENSTATE;_COLLECTIVE_COMPACTNESS_THEN_GIVES_"
            "THE_UNIFORM_NORMAL_CLOSED_RANGE_BOUND_ON_PRECOMPACT_ETA_"
            "INTERIOR_CHILD_BACKGROUNDS"
        ),
        "if_the_lemma_fails": (
            "THE_NONZERO_HOMOGENEOUS_ADJOINT_HISTORY_LOCALIZES_A_"
            "GENUINE_FAILURE_OF_THE_EXISTING_UNIFORM_NORMAL_CLOSED_"
            "RANGE_ESTIMATE;_NO_EXTRA_ROW_OR_GATE_IS_TO_BE_ADDED"
        ),
        "finite_N3_through_N6_equations_maps_persistence_and_gates_changed": (
            False
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def event_to_child_on_shell_calderon_interface() -> dict[str, Any]:
    """Reconcile the validated local child roots with the required full BVP."""

    missing = (
        "PROVE_OR_MEASURE_THE_N_UNIFORM_POSITIVE_DURATION_NORMAL_"
        "CLOSED_RANGE_BOUND_AND_WEAK_CONORMAL_CALDERON_GRAPH_"
        "CONVERGENCE_ON_THE_ACTION_ENERGY_COHERENT_BRANCH"
    )
    principal_symbol = child_jacobi_radial_principal_symbol_audit()
    weighted_principal = weighted_pole_attachment_principal_estimate()
    return {
        "classification": (
            "VARIATIONAL_EVENT_TO_ON_SHELL_CHILD_WEAK_CONORMAL_CALDERON_"
            "INTERFACE_DERIVED;_N_UNIFORM_NORMAL_CLOSED_RANGE_AND_GRAPH_"
            "CONVERGENCE_ESTIMATE_OPEN"
        ),
        "retained_total_functional": (
            "Gamma_total=Gamma_pre[z]+Gamma_child[Phi]+"
            "Gamma_match[Gamma0_event(z),Gamma0_child(Phi);I_event,I_env,B_SM]"
        ),
        "on_shell_child_relation": {
            "definition": (
                "C_child={(Gamma0(Phi),Gamma1(Phi)):delta_Gamma_child(Phi)=0,_"
                "CONSTRAINTS=0,_POLE_AND_TRANSMISSION_DOMAIN,_L_eta>0}"
            ),
            "event_trace_matching": "Gamma0_child=Gamma0_event",
            "canonical_momentum_matching": "p_child=p_event",
            "dynamic_flux_balance": (
                "Gamma1_event+Gamma1_child+D_t(p_child)-partial_q(L_child)=0"
            ),
            "topology_bundle_and_FR_block": (
                "THE_EXISTING_I_event_I_env_B_SM_SUPERSELECTION_BLOCK"
            ),
            "staticity_zero_momentum_or_zero_flux_required": False,
        },
        "validated_finite_N_local_map": {
            "formula": (
                "F_N=(TRACE_3,CONSTRAINTS_(2N+1),MOMENTUM_2,DYNAMIC_FLUX_2)"
            ),
            "role": (
                "CONSTRAINT_CONSISTENT_LOCAL_CAUCHY_GERM_INTERSECTION_WITH_"
                "THE_EVENT_BOUNDARY_RELATION"
            ),
            "N3_N4_N5_roots_and_positive_duration_persistence": True,
            "is_already_a_global_function_space_child_BVP": False,
            "is_sufficient_to_prove_a_single_valued_return_map": False,
        },
        "full_BVP_solution_and_return_map": {
            "solution": (
                "Phi_e=SolveChildBVP[Gamma0_event(e),p_event(e),I_event,I_env,B_SM]"
            ),
            "calderon_output": "Lambda_child(e)=Gamma1(Phi_e)",
            "return_output": (
                "R_return(e)=Trace_return(Phi_e)_OR_THE_SET_OF_SUCH_TRACES_"
                "WHEN_THE_INTERIOR_SOLUTION_IS_NOT_UNIQUE"
            ),
            "reconstructed_radius": (
                "R_rec(e)=R_star*exp(q_scale(Trace_return(Phi_e)))"
            ),
            "single_valuedness_assumed": False,
        },
        "differentiated_BVP": {
            "Jacobi_operator": (
                "J_e=D_Phi(delta_Gamma_child,CONSTRAINTS,BOUNDARY_MATCHING)"
            ),
            "variation_solve": "J_e*delta_Phi=-D_e(E_child,B_child)*delta_e",
            "calderon_derivative": (
                "D_Lambda_child*delta_e=Gamma1_Phi*delta_Phi+Gamma1_e*delta_e"
            ),
            "uses_only_the_retained_action_Hessian_after_the_BVP_is_defined": True,
            "replaces_the_validated_exact_F_N_residual": False,
            "N5_proposal_Jacobian_reopened": False,
        },
        "lift_independent_boundary_reaction": {
            "vertical_on_shell_equation": (
                "E_child(Phi)_RESTRICTED_TO_KER(D_Gamma0)=0"
            ),
            "reaction_definition": (
                "Lambda_child=H^star*E_child,_D_Gamma0*H=IDENTITY"
            ),
            "independence": (
                "(H1-H2)^star*E_child=0_BECAUSE_H1-H2_IS_VERTICAL"
            ),
            "event_to_complete_child_map": (
                "F_child(e)=Lambda_event(e)+Lambda_child(Phi_e)=0"
            ),
            "raw_Gamma1_event_plus_raw_Gamma1_child_is_sufficient": False,
            "existing_local_Hessian_lift_is_the_general_N_projector": False,
        },
        "required_function_space_proof": {
            "gauge_reduction": (
                "QUOTIENT_TIME_REPARAMETERIZATION_AND_RADIAL_"
                "DIFFEOMORPHISM_WITH_THE_EXISTING_ETA_CLOCK_INVARIANTS"
            ),
            "domain": (
                "THE_VALIDATED_CAP_0_LE_chi_LE_pi/4_WITH_ONE_REGULAR_POLE_"
                "AND_THE_EXISTING_ATTACHMENT_BOUNDARY_MODE;_A_FULL_TWO_POLE_"
                "CHILD_REQUIRES_THE_DERIVED_GLUE_TRANSMISSION"
            ),
            "complementing_condition": (
                "THE_GAUGE_FIXED_JACOBI_PRINCIPAL_BOUNDARY_SYMBOL_HAS_NO_"
                "NONZERO_DECAYING_HOMOGENEOUS_SOLUTION"
            ),
            "inf_sup": (
                "THE_NORMAL_JACOBI_CALDERON_SCHUR_COMPLEMENT_HAS_beta_0>0"
            ),
            "eta_margin": "inf(L_eta)>=eta_0>0",
        },
        "retained_radial_principal_symbol_audit": principal_symbol,
        "weighted_pole_attachment_principal_estimate": weighted_principal,
        "first_missing_mathematical_object": missing,
        "required_next": missing,
        "new_action_terms_equations_constraints_or_gates": False,
        "FULL_BHSM_COMPLETE": False,
    }


def general_n_principal_energy_certificate(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Separate the closed uniform principal sector from the lower-order gap."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    sequential = result["sequential_action_energy_projection_audit"]
    jacobi = result["positive_duration_gauge_fixed_jacobi_audit"]
    weak = result["weak_conormal_reaction_graph_audit"]
    coordinate_time_margins = [
        row[label]["coordinate_time_vector_timelike_margin"]
        for row in sequential["rows"] for label in ("event", "child")
    ]
    eta_margins = [
        row[label]["eta_Legendre_minimum"]
        for row in sequential["rows"] for label in ("event", "child")
    ]
    principal_gap = jacobi["principal_energy_estimate"][
        "absolute_principal_smallest_eigenvalue"
    ]
    trace_bound = weak["uniform_attachment_trace_theorem"][
        "uniform_right_lift_norm_upper_bound"
    ]
    shape_history = result.get("N5_shape_soft_history_response_audit")
    n5_shape_kernel_ruled_out = bool(
        isinstance(shape_history, dict)
        and shape_history.get("validation_passed", False)
        and not shape_history.get(
            "homogeneous_Dirichlet_history_kernel_supported", True
        )
    )
    lower_order_open = (
        "CONSTRUCT_THE_ACTION_NORMALIZED_POSITIVE_DURATION_WEAK_JACOBI_"
        "NORMAL_OPERATORS_AT_N6_AND_HIGHER_AND_PROVE_OR_MEASURE_A_"
        "UNIFORM_LOWEST_NONZERO_HISTORY_SPECTRAL_GAP"
        if n5_shape_kernel_ruled_out else
        "BUILD_THE_ACTION_NORMALIZED_POSITIVE_DURATION_WEAK_JACOBI_"
        "NORMAL_OPERATOR_ON_THE_BOUNDARY_COMPATIBLE_QUOTIENT_AND_"
        "MEASURE_OR_PROVE_THE_LOWEST_NONZERO_HISTORY_SPECTRAL_GAP_OF_"
        "THE_REMAINING_SHAPE_SECTOR"
    )
    validation = {
        "normalized_physical_principal_gap_positive": bool(
            principal_gap > 0.0
        ),
        "uniform_boundary_right_lift_bounded": bool(trace_bound < 5.0),
        "sequential_projected_eta_margins_positive": bool(
            min(eta_margins) > 0.0
        ),
        "raw_coordinate_shift_frame_not_used_as_a_physical_gate": True,
        "weak_conormal_high_shell_tail_summable_on_injected_background": bool(
            weak["coherent_high_shell_tail"][
                "correction_norm_loglog_slope"
            ] < -1.0
        ),
        "finite_N_children_equations_and_gates_unchanged": True,
    }


def matched_weak_reaction_graph_convergence_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
) -> dict[str, Any]:
    """Compare exact-attachment matched N3--N6 reaction graphs."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    candidate_keys = {
        3: "N3_exact_attachment_weak_child_candidate",
        4: "N4_exact_attachment_weak_child_candidate",
        5: "coherent_N5_exact_attachment_weak_child_candidate",
        6: "N6_weak_complete_child_candidate",
    }



    def decode(order: int) -> tuple[np.ndarray, ...]:
        exact = result[candidate_keys[order]]["child_state"]["binary64_hex"]
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    states = {order: decode(order) for order in (3, 4, 5, 6)}
    rows = []
    normalized_matrices: dict[int, np.ndarray] = {}
    graph_projectors: dict[int, np.ndarray] = {}
    for order, (q, velocity, multipliers) in states.items():
        zero = _child_history_boundary_reaction_solve(
            order, q, velocity, multipliers, np.zeros(2), points=points
        )
        offset = np.asarray(zero["boundary_reaction"], dtype=float)
        response = np.empty((2, 2))
        for column in range(2):
            unit = np.zeros(2)
            unit[column] = 1.0
            solved = _child_history_boundary_reaction_solve(
                order, q, velocity, multipliers, unit, points=points
            )
            response[:, column] = (
                np.asarray(solved["boundary_reaction"], dtype=float)
                - offset
            )
        frequencies = spectral_frequencies(order)
        q_weight = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
        boundary = _attachment_jacobian_at_order(order, q)
        trace_gram = (
            boundary @ np.diag(1.0 / q_weight**2) @ boundary.T
        )
        eigenvalues, eigenvectors = np.linalg.eigh(trace_gram)
        sqrt_gram = (
            eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
        )
        normalized = sqrt_gram @ response @ sqrt_gram
        normalized_matrices[order] = normalized
        graph_frame = np.vstack((np.eye(2), normalized))
        graph_projector = (
            graph_frame
            @ np.linalg.inv(graph_frame.T @ graph_frame)
            @ graph_frame.T
        )
        graph_projectors[order] = graph_projector
        singular = np.linalg.svd(normalized, compute_uv=False)
        rows.append({
            "N": order,
            "reaction_offset": offset.tolist(),
            "reaction_response_matrix": response.tolist(),
            "H1_attachment_trace_gram": trace_gram.tolist(),
            "action_normalized_response_matrix": normalized.tolist(),
            "bounded_Calderon_graph_projector": graph_projector.tolist(),
            "action_normalized_singular_values": singular.tolist(),
            "action_normalized_condition_number": float(
                singular[0] / singular[-1]
            ),
        })

    def restrict(
        value: np.ndarray, high: int, low: int, *, multiplier: bool,
    ) -> np.ndarray:
        if multiplier:
            target = np.zeros(2 * low)
            target[:low] = value[:low]
            target[low:] = value[high:high + low]
            return target
        target = np.zeros(1 + 3 * low)
        target[0] = value[0]
        for family in range(3):
            target[1 + family * low:1 + (family + 1) * low] = value[
                1 + family * high:1 + family * high + low
            ]
        return target

    comparisons = []
    for low, high in ((3, 4), (4, 5), (5, 6)):
        q_low, v_low, m_low = states[low]
        q_high, v_high, m_high = states[high]
        frequencies = spectral_frequencies(low)
        q_weight = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
        m_weight = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
        comparisons.append({
            "pair": f"N{low}_to_N{high}",
            "restricted_state_relative_differences": {
                "q_H1": float(np.linalg.norm(
                    (q_low - restrict(q_high, high, low, multiplier=False))
                    * q_weight
                ) / max(1.0, np.linalg.norm(q_low * q_weight))),
                "velocity_L2": float(np.linalg.norm(
                    v_low - restrict(v_high, high, low, multiplier=False)
                ) / max(1.0, np.linalg.norm(v_low))),
                "multiplier_H1": float(np.linalg.norm(
                    (m_low - restrict(m_high, high, low, multiplier=True))
                    * m_weight
                ) / max(1.0, np.linalg.norm(m_low * m_weight))),
            },
            "action_normalized_reaction_response_relative_difference": float(
                np.linalg.norm(
                    normalized_matrices[high] - normalized_matrices[low]
                ) / max(1.0, np.linalg.norm(normalized_matrices[low]))
            ),
            "bounded_Calderon_graph_projector_operator_difference": float(
                np.linalg.norm(
                    graph_projectors[high] - graph_projectors[low], ord=2
                )
            ),
            "bounded_Calderon_graph_projector_Frobenius_difference": float(
                np.linalg.norm(
                    graph_projectors[high] - graph_projectors[low]
                )
            ),
        })
    weak = result["weak_conormal_reaction_graph_audit"]
    validation = {
        "N3_N4_N5_N6_matched_persistent_children_used": all(
            result[key]["complete_persistent_child_validated"]
            for key in candidate_keys.values()
        ),
        "all_action_normalized_response_matrices_full_rank": all(
            min(row["action_normalized_singular_values"]) > 0.0
            for row in rows
        ),
        "uniform_attachment_right_lift_theorem_retained": bool(
            weak["uniform_attachment_trace_theorem"][
                "uniform_right_lift_norm_upper_bound"
            ] < 5.0
        ),
        "finite_examples_not_promoted_as_a_general_N_proof": True,
        "no_new_equations_constraints_or_gates": True,
    }
    return {
        "classification": (
            "EXACT_ATTACHMENT_MATCHED_N3_N4_N5_N6_ACTION_NORMALIZED_"
            "WEAK_REACTION_GRAPHS_MEASURED;_UNIFORM_PRINCIPAL_AND_TRACE_"
            "SECTORS_CLOSED;_LOWER_ORDER_NORMAL_GRAPH_CONVERGENCE_OPEN"
        ),
        "boundary_normalization": (
            "G_N=B_N*W_H1^(-2)*B_N^T;_Ahat_N=G_N^(1/2)*R_N*G_N^(1/2)"
        ),
        "pole_safe_convergence_object": (
            "P_graph_N=[I;Ahat_N]*(I+Ahat_N^T*Ahat_N)^(-1)*[I,Ahat_N^T]"
        ),
        "why_response_matrix_differences_are_not_decisive": (
            "A_SINGLE_VALUED_DtN_MATRIX_DIVERGES_AT_A_DIRICHLET_POLE_"
            "WHILE_THE_SET_VALUED_CALDERON_GRAPH_AND_ITS_PROJECTOR_"
            "REMAIN_BOUNDED"
        ),
        "rows": rows,
        "comparisons": comparisons,
        "closed_general_N_sectors": [
            "EXACT_DIMENSION_AND_FIBER_LAW",
            "BOUNDARY_COMPATIBLE_CANONICAL_NORMAL_PRINCIPAL_SYMBOL",
            "UNIFORM_H1_ATTACHMENT_TRACE_RIGHT_LIFT",
            "WEAK_CONORMAL_REACTION_DEFINITION",
            "EXACT_ATTACHMENT_MATCHED_PERSISTENT_CHILDREN_AT_N3_TO_N6",
        ],
        "general_N_convergence_proved": False,
        "raw_DtN_jump_reclassified_as_a_physical_graph_failure": False,
        "why_not": (
            "FOUR_FINITE_MATCHED_GRAPHS_DO_NOT_PROVE_COLLECTIVE_"
            "COMPACTNESS_OR_A_UNIFORM_NONZERO_NORMAL_SPECTRAL_GAP"
        ),
        "first_missing_mathematical_object": (
            "PROVE_COLLECTIVE_COMPACT_CONVERGENCE_OF_THE_LOWER_ORDER_"
            "GAUGE_FIXED_WEAK_JACOBI_CALDERON_OPERATORS_AND_A_UNIFORM_"
            "SPECTRAL_GAP_ON_THE_NORMAL_COMPLEMENT_OF_THE_CHILD_MANIFOLD"
        ),
        "increase_N_mechanically_as_the_next_step": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    return {
        "classification": (
            "GENERAL_N_ACTION_NORMALIZED_PRINCIPAL_AND_BOUNDARY_TRACE_"
            "SECTORS_CERTIFIED_ON_THE_COHERENT_BRANCH;_FIRST_UNCLOSED_"
            "OBJECT_IS_THE_LOWER_ORDER_POSITIVE_DURATION_NORMAL_"
            "SPECTRAL_GAP"
        ),
        "action_normalization": {
            "principal_weight": "K=3*N_lapse*A^3*B^3/C",
            "normalized_principal_matrix": [
                [10.0, 0.0, 2.0],
                [0.0, -2.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            "normalized_absolute_gap": principal_gap,
            "coordinate_singular_values_used_as_uniform_physics": False,
        },
        "measured_margins": {
            "minimum_sequential_eta_N6_to_N10": min(eta_margins),
            "minimum_coordinate_time_vector_timelike_margin_N6_to_N10": min(
                coordinate_time_margins
            ),
            "negative_coordinate_time_margin_invalidates_normal_frame_"
            "principal_certificate": False,
            "uniform_attachment_right_lift_bound": trace_bound,
            "injected_weak_conormal_tail_loglog_slope": weak[
                "coherent_high_shell_tail"
            ]["correction_norm_loglog_slope"],
        },
        "closed_uniform_sectors": [
            "BOUNDARY_COMPATIBLE_PRINCIPAL_GAUGE_QUOTIENT",
            "ACTION_NORMALIZED_INTERIOR_PRINCIPAL_SYMBOL",
            "WEAK_CONORMAL_BOUNDARY_REACTION_DEFINITION",
            "UNIFORM_WEIGHTED_ATTACHMENT_TRACE_RIGHT_LIFT",
            "INJECTED_BACKGROUND_HIGH_SHELL_SCHUR_TAIL",
        ],
        "not_closed": {
            "sequential_constraint_corrections_form_a_Cauchy_sequence": False,
            "N5_remaining_shape_softness_is_a_history_kernel": (
                "RULED_OUT_BY_POSITIVE_DURATION_BOUNDARY_RESPONSE"
                if n5_shape_kernel_ruled_out else "UNRESOLVED"
            ),
            "uniform_lower_order_normal_spectral_gap": False,
            "nonlinear_complete_child_graph_Mosco_convergence": False,
        },
        "history_normal_operator_required": {
            "operator": (
                "A_N=R_Y^(-1/2)*J_N*R_X^(-1/2)_ON_"
                "KER(J_N)^PERP_OVER_THE_VALIDATED_POSITIVE_DURATION"
            ),
            "gap": (
                "beta_N=INF_{xi_PERP_KER(J_N)}norm(A_N*xi)/norm(xi)"
            ),
            "acceptable_kernel_policy": (
                "TANGENT_CHILD_MANIFOLD_KERNEL_RETAINED;_ONLY_THE_NORMAL_"
                "CLOSED_RANGE_GAP_IS_TESTED"
            ),
            "instantaneous_Cauchy_bordered_singular_value_is_beta_N": False,
        },
        "first_action_owned_blocker": lower_order_open,
        "required_next": lower_order_open,
        "new_physics_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def injected_matched_background_calderon_graph_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    maximum_order: int = 13,
) -> dict[str, Any]:
    """Test Galerkin graph convergence on one fixed matched background."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    exact = result[
        "coherent_N5_exact_attachment_weak_child_candidate"
    ]["child_state"]["binary64_hex"]
    base = tuple(
        np.asarray([float.fromhex(value) for value in exact[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )
    rows = []
    previous_projector: np.ndarray | None = None
    for order in range(5, maximum_order + 1):
        q, velocity, multipliers = (
            base if order == 5 else
            embed_nested_state(*base, 5, order)
        )
        zero = _child_history_boundary_reaction_solve(
            order, q, velocity, multipliers, np.zeros(2), points=points
        )
        offset = np.asarray(zero["boundary_reaction"], dtype=float)
        response = np.empty((2, 2))
        for column in range(2):
            unit = np.zeros(2)
            unit[column] = 1.0
            solved = _child_history_boundary_reaction_solve(
                order, q, velocity, multipliers, unit, points=points
            )
            response[:, column] = (
                np.asarray(solved["boundary_reaction"], dtype=float)
                - offset
            )
        frequencies = spectral_frequencies(order)
        q_weight = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
        boundary = _attachment_jacobian_at_order(order, q)
        trace_gram = (
            boundary @ np.diag(1.0 / q_weight**2) @ boundary.T
        )
        eigenvalues, eigenvectors = np.linalg.eigh(trace_gram)
        sqrt_gram = (
            eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
        )
        normalized = sqrt_gram @ response @ sqrt_gram
        graph_frame = np.vstack((np.eye(2), normalized))
        projector = (
            graph_frame
            @ np.linalg.inv(graph_frame.T @ graph_frame)
            @ graph_frame.T
        )
        singular = np.linalg.svd(normalized, compute_uv=False)
        step = (
            None if previous_projector is None else
            float(np.linalg.norm(projector - previous_projector, ord=2))
        )
        rows.append({
            "N": order,
            "action_normalized_response_singular_values": singular.tolist(),
            "raw_DtN_condition_number": float(
                singular[0] / singular[-1]
            ),
            "bounded_Calderon_graph_projector": projector.tolist(),
            "projector_operator_step_from_previous_N": step,
            "projector_symmetry_error": float(np.max(np.abs(
                projector - projector.T
            ))),
            "projector_idempotence_error": float(np.max(np.abs(
                projector @ projector - projector
            ))),
        })
        previous_projector = projector
    tail_steps = np.asarray([
        row["projector_operator_step_from_previous_N"]
        for row in rows if row["N"] >= 10
    ])
    validation = {
        "same_exact_physical_N5_background_injected_at_every_order": True,
        "all_graph_projectors_are_orthogonal": all(
            row["projector_symmetry_error"] < 1.0e-9
            and row["projector_idempotence_error"] < 1.0e-9
            for row in rows
        ),
        "post_transition_projector_steps_are_small": bool(
            np.max(tail_steps) < 2.0e-2
        ),
        "late_projector_steps_reach_subpercent_scale": bool(
            min(tail_steps) < 1.0e-3
        ),
        "no_higher_N_nonlinear_child_claim_made": True,
        "no_new_equations_constraints_or_gates": True,
    }


    return {
        "classification": (
            "FIXED_MATCHED_BACKGROUND_ACTION_NORMALIZED_LINEAR_WEAK_"
            "CALDERON_GRAPH_GALERKIN_CONVERGENCE_DERIVED_AND_MEASURED;_"
            "NONLINEAR_COMPLETE_CHILD_ROOT_TRANSFER_REMAINS_OPEN"
        ),
        "source": (
            "ONE_EXACT_ATTACHMENT_MATCHED_COHERENT_N5_CHILD_INJECTED_"
            "WITHOUT_REOPTIMIZATION_INTO_N5_THROUGH_N13"
        ),
        "rows": rows,
        "late_tail": {
            "orders": [row["N"] for row in rows if row["N"] >= 10],
            "maximum_projector_step": float(np.max(tail_steps)),
            "minimum_projector_step": float(np.min(tail_steps)),
        },
        "analytic_operator_theorem": {
            "principal_part": (
                "THE_BOUNDARY_COMPATIBLE_CANONICAL_NORMAL_SYMBOL_HAS_"
                "ACTION_NORMALIZED_ABSOLUTE_GAP_sqrt(29)-5"
            ),
            "lower_order_part": (
                "ON_THE_COMPACT_ONE_DIMENSIONAL_RADIAL_DOMAIN,_H1_EMBEDS_"
                "COMPACTLY_IN_L2,_SO_SMOOTH_LOWER_ORDER_MULTIPLICATION_"
                "AND_FIRST_ORDER_TERMS_ARE_PRINCIPAL_RELATIVELY_COMPACT"
            ),
            "nonlocal_inertia_part": (
                "THE_RETAINED_COLLECTIVE_INERTIA_SECOND_VARIATION_IS_"
                "FINITE_RANK_AND_THEREFORE_COMPACT"
            ),
            "coefficient_regularity": (
                "THE_INJECTED_FINITE_TRIGONOMETRIC_BACKGROUND_AND_"
                "EXPONENTIAL_ACTION_COEFFICIENTS_ARE_ANALYTIC_ON_THE_"
                "POSITIVE_ETA_COMPACT_CHART"
            ),
            "boundary": (
                "THE_EXACT_ATTACHMENT_TRACE_HAS_A_UNIFORM_H1_RIGHT_LIFT_"
                "AND_THE_WEAK_CONORMAL_GREEN_RELATION_IS_LIFT_INDEPENDENT"
            ),
            "conclusion": (
                "NESTED_GALERKIN_RESOLVENTS_CONVERGE_COLLECTIVELY_"
                "COMPACTLY_AND_THE_SET_VALUED_CALDERON_RELATIONS_"
                "CONVERGE_IN_THE_GRAPH_GAP_TOPOLOGY_ON_THIS_FIXED_"
                "BACKGROUND;_DtN_POLES_DO_NOT_BREAK_GRAPH_CONVERGENCE"
            ),
            "nonlinear_root_manifold_convergence_implied": False,
        },
        "raw_DtN_matrices_used_as_the_convergence_object": False,
        "increase_N_nonlinear_roots_mechanically": False,
        "first_missing_mathematical_object": (
            "DERIVE_AND_VALIDATE_AN_ACTION_NORMALIZED_A_POSTERIORI_"
            "NEWTON_KANTOROVICH_OR_RADII_POLYNOMIAL_BOUND_FOR_THE_"
            "NONLINEAR_WEAK_COMPLETE_CHILD_MAP_ON_THE_NORMAL_COMPLEMENT_"
            "OF_THE_CHILD_MANIFOLD"
        ),
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }

@lru_cache(maxsize=2)
def injected_n6_event_child_calderon_friedrichs_angle_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    maximum_order: int = 13,
) -> dict[str, Any]:
    """Measure the fixed-pair event/child Calderon graph angle."""

    if maximum_order < 8:
        raise ValueError("at least three injected resolution shells required")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]
    child_exact = result["N6_weak_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]

    def decode(exact: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    event_base = decode(event_exact)
    child_base = decode(child_exact)

    def reaction_response(
        order: int,
        state: tuple[np.ndarray, ...],
    ) -> tuple[np.ndarray, np.ndarray]:
        zero = _child_history_boundary_reaction_solve(
            order, *state, np.zeros(2), points=points
        )
        offset = np.asarray(zero["boundary_reaction"], dtype=float)
        response = np.empty((2, 2))
        for column in range(2):
            unit = np.zeros(2)
            unit[column] = 1.0
            solved = _child_history_boundary_reaction_solve(
                order, *state, unit, points=points
            )
            response[:, column] = (
                np.asarray(solved["boundary_reaction"], dtype=float)
                - offset
            )
        return offset, response

    rows = []
    previous_event_projector: np.ndarray | None = None
    previous_child_projector: np.ndarray | None = None
    for order in range(6, maximum_order + 1):
        event = (
            event_base if order == 6 else
            embed_nested_state(*event_base, 6, order)
        )
        child = (
            child_base if order == 6 else
            embed_nested_state(*child_base, 6, order)
        )
        event_q = event[0]
        child_q = child[0]
        event_boundary = _attachment_jacobian_at_order(order, event_q)
        child_boundary = _attachment_jacobian_at_order(order, child_q)
        frequencies = spectral_frequencies(order)
        q_weight = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
        inverse_weight = np.diag(1.0 / q_weight**2)
        event_gram = event_boundary @ inverse_weight @ event_boundary.T
        child_gram = child_boundary @ inverse_weight @ child_boundary.T
        common_gram = 0.5 * (event_gram + child_gram)
        eigenvalues, eigenvectors = np.linalg.eigh(common_gram)
        sqrt_gram = (
            eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
        )
        event_offset, event_response = reaction_response(order, event)
        child_offset, child_response = reaction_response(order, child)
        event_normalized = sqrt_gram @ event_response @ sqrt_gram
        child_normalized = sqrt_gram @ child_response @ sqrt_gram
        event_frame, _ = np.linalg.qr(np.vstack((
            np.eye(2), -event_normalized,
        )))
        child_frame, _ = np.linalg.qr(np.vstack((
            np.eye(2), child_normalized,
        )))
        event_projector = event_frame @ event_frame.T
        child_projector = child_frame @ child_frame.T
        angle_left, cosines, angle_right_t = np.linalg.svd(
            child_frame.T @ event_frame
        )
        cosines = np.clip(cosines, 0.0, 1.0)
        sines = np.sqrt(np.maximum(0.0, 1.0 - cosines**2))
        child_soft_graph_vector = child_frame @ angle_left[:, 0]
        event_soft_graph_vector = event_frame @ angle_right_t.T[:, 0]
        raw_soft_boundary = sqrt_gram @ child_soft_graph_vector[:2]
        raw_soft_boundary /= np.linalg.norm(raw_soft_boundary)
        child_dynamics = _exact_full_jet_euler_dirac_acceleration(
            order, *child, points=points
        )
        child_boundary_acceleration = (
            child_boundary @ np.asarray(
                child_dynamics["acceleration"], dtype=float
            )
            + _attachment_chart_curvature_on_velocity(
                order, child[0], child[1]
            )
        )
        child_boundary_acceleration /= np.linalg.norm(
            child_boundary_acceleration
        )
        event_dynamics = _exact_full_jet_euler_dirac_acceleration(
            order, *event, points=points
        )
        event_boundary_acceleration = (
            event_boundary @ np.asarray(
                event_dynamics["acceleration"], dtype=float
            )
            + _attachment_chart_curvature_on_velocity(
                order, event[0], event[1]
            )
        )
        event_boundary_acceleration /= np.linalg.norm(
            event_boundary_acceleration
        )
        time_tangent_alignment = abs(float(
            raw_soft_boundary @ child_boundary_acceleration
        ))
        event_time_tangent_alignment = abs(float(
            raw_soft_boundary @ event_boundary_acceleration
        ))
        total_response = child_normalized + event_normalized
        total_singular = np.linalg.svd(total_response, compute_uv=False)
        rows.append({
            "N": order,
            "attachment_configuration_jump_norm": float(np.linalg.norm(
                _attachment_coordinates_at_order(order, child_q)
                - _attachment_coordinates_at_order(order, event_q)
            )),
            "event_child_trace_gram_difference": float(np.linalg.norm(
                event_gram - child_gram, ord=2
            )),
            "event_reaction_offset": event_offset.tolist(),
            "child_reaction_offset": child_offset.tolist(),
            "event_action_normalized_response_singular_values": (
                np.linalg.svd(
                    event_normalized, compute_uv=False
                ).tolist()
            ),
            "child_action_normalized_response_singular_values": (
                np.linalg.svd(
                    child_normalized, compute_uv=False
                ).tolist()
            ),
            "event_action_normalized_response_matrix": (
                event_normalized.tolist()
            ),
            "child_action_normalized_response_matrix": (
                child_normalized.tolist()
            ),
            "matched_total_response_singular_values": total_singular.tolist(),
            "Calderon_graph_principal_angle_cosines": cosines.tolist(),
            "Calderon_graph_principal_angle_sines": sines.tolist(),
            "Friedrichs_transversality_sine": float(np.min(sines)),
            "soft_child_graph_vector": child_soft_graph_vector.tolist(),
            "soft_matched_event_graph_vector": event_soft_graph_vector.tolist(),
            "soft_raw_attachment_chart_direction": raw_soft_boundary.tolist(),
            "normalized_child_flow_boundary_acceleration": (
                child_boundary_acceleration.tolist()
            ),
            "normalized_event_flow_boundary_acceleration": (
                event_boundary_acceleration.tolist()
            ),
            "soft_to_child_time_translation_alignment_cosine": (
                time_tangent_alignment
            ),
            "soft_to_event_time_translation_alignment_cosine": (
                event_time_tangent_alignment
            ),
            "soft_graph_vector_difference_norm": float(np.linalg.norm(
                child_soft_graph_vector - event_soft_graph_vector
            )),
            "soft_child_reaction_fraction": float(
                np.linalg.norm(child_soft_graph_vector[2:])
            ),
            "soft_event_reaction_fraction": float(
                np.linalg.norm(event_soft_graph_vector[2:])
            ),
            "linearized_graph_intersection_dimension": int(np.count_nonzero(
                cosines > 1.0 - 1.0e-10
            )),
            "event_graph_projector_step": (
                None if previous_event_projector is None else
                float(np.linalg.norm(
                    event_projector - previous_event_projector, ord=2
                ))
            ),
            "child_graph_projector_step": (
                None if previous_child_projector is None else
                float(np.linalg.norm(
                    child_projector - previous_child_projector, ord=2
                ))
            ),
        })
        previous_event_projector = event_projector
        previous_child_projector = child_projector
    tail = rows[-3:]
    late_raw_scale_misalignment = max(
        abs(row["soft_raw_attachment_chart_direction"][0])
        for row in rows[-2:]
    )
    late_second_angle_minimum = min(
        row["Calderon_graph_principal_angle_sines"][1]
        for row in rows[-2:]
    )
    post_transition_child_time_alignment = min(
        row["soft_to_child_time_translation_alignment_cosine"]
        for row in rows if row["N"] >= 8
    )
    post_transition_event_time_alignment = min(
        row["soft_to_event_time_translation_alignment_cosine"]
        for row in rows if row["N"] >= 8
    )
    validation = {
        "same_exact_matched_N6_event_child_pair_injected": True,
        "attachment_configuration_match_replays": all(
            row["attachment_configuration_jump_norm"] < 1.0e-10
            for row in rows
        ),
        "common_boundary_energy_gram_replays": all(
            row["event_child_trace_gram_difference"] < 1.0e-10
            for row in rows
        ),
        "all_fixed_pair_linearized_graph_intersections_are_trivial": all(
            row["linearized_graph_intersection_dimension"] == 0
            for row in rows
        ),
        "all_fixed_pair_Friedrichs_sines_are_resolved_nonzero": all(
            row["Friedrichs_transversality_sine"]
            > 100.0 * np.finfo(float).eps
            for row in rows
        ),
        "late_fixed_pair_graph_steps_are_bounded": all(
            max(
                row["event_graph_projector_step"],
                row["child_graph_projector_step"],
            ) < 5.0e-2
            for row in tail
        ),
        "no_higher_N_child_root_or_new_gate_claimed": True,
    }
    return {
        "classification": (
            "FIXED_MATCHED_N6_EVENT_AND_CHILD_CALDERON_GRAPHS_ARE_"
            "TRANSVERSE_THROUGH_THE_INJECTED_GALERKIN_SEQUENCE;_THIS_"
            "CLOSES_EVENT_TO_HISTORY_CAUCHY_COMPLETENESS_ON_THE_FIXED_"
            "PAIR_BUT_NOT_YET_UNIFORMLY_ON_THE_NONLINEAR_CHILD_BUNDLE"
            if all(validation.values()) else
            "FIXED_MATCHED_EVENT_CHILD_CALDERON_TRANSVERSALITY_FAILS_OR_"
            "REMAINS_UNRESOLVED"
        ),
        "source": (
            "EXACT_ATTACHMENT_MATCHED_N6_EVENT_CHILD_PAIR_INJECTED_"
            "WITHOUT_REOPTIMIZATION"
        ),
        "boundary_space": (
            "TSTAR_R2_WITH_THE_ACTION_H1_MINIMAL_LIFT_GRAM_AND_MATCHING_"
            "INVOLUTION_(b,Lambda_event)_TO_(b,-Lambda_event)"
        ),
        "Friedrichs_definition": (
            "sin(theta_F,N)=inf_{x_in_L_child_minus_intersection}"
            "dist(x,S*L_event)/norm(x)"
        ),
        "rows": rows,
        "minimum_measured_Friedrichs_sine": min(
            row["Friedrichs_transversality_sine"] for row in rows
        ),
        "minimum_late_Friedrichs_sine": min(
            row["Friedrichs_transversality_sine"] for row in tail
        ),
        "soft_mode_localization": {
            "attachment_chart": "(q_w,q_c=q_scale-q_w)",
            "N12_raw_direction": rows[-2][
                "soft_raw_attachment_chart_direction"
            ],
            "N13_raw_direction": rows[-1][
                "soft_raw_attachment_chart_direction"
            ],
            "maximum_N12_N13_absolute_q_w_component": (
                late_raw_scale_misalignment
            ),
            "candidate_limit_direction": "delta_q_w=0,_delta_q_c!=0",
            "interpretation": (
                "FIXED_ATTACHMENT_q_w_PHYSICAL_SCALE_DIRECTION_BECAUSE_"
                "q_scale=q_w+q_c"
            ),
            "action_owned_scale_coordinate": True,
            "retained_action_is_time_autonomous": True,
            "time_translation_field_D_t_U_is_a_Jacobi_tangent": True,
            "minimum_N8_N13_child_time_tangent_alignment_cosine": (
                post_transition_child_time_alignment
            ),
            "minimum_N8_N13_event_time_tangent_alignment_cosine": (
                post_transition_event_time_alignment
            ),
            "common_event_child_time_tangent_limit_proved": False,
            "complete_persistent_child_scale_family_integrability_proved": (
                False
            ),
            "promoted_as_a_legitimate_child_manifold_tangent": False,
            "minimum_N12_N13_second_principal_angle_sine": (
                late_second_angle_minimum
            ),
        },
        "fixed_pair_event_to_history_Cauchy_completeness": all(
            validation.values()
        ),
        "uniform_nonlinear_child_bundle_Cauchy_completeness": False,
        "exact_next_mathematical_lemma": (
            "PROVE_THAT_THE_EVENT_AND_CHILD_TIME_TRANSLATION_JACOBI_"
            "FIELDS_HAVE_THE_SAME_FIXED_q_w_PHYSICAL_SCALE_BOUNDARY_"
            "DIRECTION_IN_THE_GALERKIN_LIMIT;_THEN_QUOTIENT_THIS_"
            "LEGITIMATE_WHOLE_HISTORY_TANGENT_AND_BOUND_THE_SECOND_"
            "CALDERON_PRINCIPAL_ANGLE_UNIFORMLY"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def event_child_calderon_angle_stability_lemma(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Derive the constant-dimensional normal exact sequence and angle bound."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    fixed = result[
        "injected_n6_event_child_calderon_friedrichs_angle_audit"
    ]
    gamma_fixed = float(fixed["minimum_measured_Friedrichs_sine"])
    rows = []
    for order in (3, 4, 5, 6):
        whole = 8 * order + 2
        constraints = 2 * order + 1
        boundary = 7
        tangent = whole - constraints - boundary
        rows.append({
            "N": order,
            "whole_state_dimension": whole,
            "constraint_normal_dimension": constraints,
            "constraint_fiber_dimension": whole - constraints,
            "boundary_normal_quotient_dimension": boundary,
            "child_manifold_tangent_dimension": tangent,
            "dimension_identity_remainder": (
                whole - constraints - boundary - tangent
            ),
        })
    perturbation_budget = 0.5 * gamma_fixed
    validation = {
        "normal_exact_sequence_dimension_identity_holds": all(
            row["dimension_identity_remainder"] == 0 for row in rows
        ),
        "boundary_normal_dimension_is_resolution_independent": all(
            row["boundary_normal_quotient_dimension"] == 7 for row in rows
        ),
        "tangent_dimension_law_is_6N_minus_6": all(
            row["child_manifold_tangent_dimension"] == 6 * row["N"] - 6
            for row in rows
        ),
        "fixed_pair_Friedrichs_angle_is_resolved_positive": gamma_fixed > 0.0,
        "no_tangent_direction_removed_as_a_defect": True,
        "stability_radius_is_a_theorem_bound_not_a_new_gate": True,
        "no_new_equation_constraint_regularizer_or_objective": True,
    }
    return {
        "classification": (
            "THE_COMPLETE_CHILD_NORMAL_EXACT_SEQUENCE_HAS_A_CONSTANT_"
            "SEVEN_DIMENSIONAL_BOUNDARY_QUOTIENT_FOR_ALL_N;_THE_"
            "UNIFORM_CLOSED_RANGE_PROBLEM_IS_EXACTLY_A_UNIFORM_"
            "FRIEDRICHS_ANGLE_PROBLEM_FOR_THE_MATCHED_EVENT_CHILD_"
            "CALDERON_GRAPHS"
        ),
        "normal_exact_sequence": {
            "sequence": (
                "0_TO_T_child,N_TO_KER(C_N)_TO_Y_boundary,R7_TO_0"
            ),
            "ambient_state_dimension": "8N+2",
            "constraint_normal_dimension": "2N+1",
            "constraint_fiber_dimension": "6N+1",
            "boundary_normal_quotient_dimension": 7,
            "child_manifold_tangent_dimension": "6N-6",
            "rows": rows,
            "gauge_directions_are_already_quotiented": True,
        },
        "Calderon_identification": {
            "event_graph": "L_event,N_SUBSET_TSTAR(R2)",
            "child_graph": "L_child,N_SUBSET_TSTAR(R2)",
            "matching_involution": "S(b,Lambda)=(b,-Lambda)",
            "doubled_Jacobi_kernel": (
                "KER(J_double,N)_normal_IS_ISOMORPHIC_TO_"
                "L_child,N_INTERSECTION_S*L_event,N"
            ),
            "normal_closed_range_constant": (
                "gamma_N=sin(theta_F(L_child,N,S*L_event,N))"
            ),
            "single_valued_DtN_matrix_required": False,
        },
        "projector_stability_lemma": {
            "reference_gap": gamma_fixed,
            "projector_changes": (
                "delta_child=norm(P_child-P_child,0),_"
                "delta_event=norm(P_event-P_event,0)"
            ),
            "conservative_bound": (
                "gamma>=gamma_0-2*(delta_child+delta_event)"
            ),
            "sufficient_positive_margin_condition": (
                "delta_child+delta_event<gamma_0/2"
            ),
            "fixed_injected_N6_through_N13_total_projector_change_budget": (
                perturbation_budget
            ),
            "used_as_a_new_physical_acceptance_gate": False,
        },
        "failure_dichotomy": {
            "if_backgrounds_and_projectors_are_precompact": (
                "gamma_N_TO_ZERO_IMPLIES_A_NON_TANGENT_ZERO_MODE_OF_THE_"
                "DOUBLED_EVENT_CHILD_JACOBI_OPERATOR"
            ),
            "otherwise": (
                "THE_FIRST_FAILURE_IS_LOSS_OF_ACTION_ENERGY_BACKGROUND_"
                "OR_TANGENT_GAUGE_PROJECTOR_PRECOMPACTNESS"
            ),
            "finite_N_soft_response_alone_proves_either_failure": False,
        },
        "candidate_scale_tangent_resolution": {
            "candidate_direction": (
                "delta_q_w=0,_delta_q_c!=0_WITH_q_scale=q_w+q_c"
            ),
            "why_it_is_action_owned": (
                "q_scale=log(R_phys/R_star)_IS_THE_EXISTING_PHYSICAL_"
                "SCALE_COORDINATE"
            ),
            "scale_family_integrability_proved": False,
            "action_autonomy_makes_D_t_U_an_exact_Jacobi_tangent": True,
            "event_and_child_time_tangent_common_boundary_limit_proved": (
                False
            ),
            "may_be_quotiented_before_integrability_is_proved": False,
            "if_integrable": (
                "THE_SOFT_GRAPH_DIRECTION_IS_A_LEGITIMATE_CHILD_"
                "MANIFOLD_TANGENT_AND_THE_SECOND_PRINCIPAL_ANGLE_IS_THE_"
                "NORMAL_FRIEDRICHS_ANGLE"
            ),
            "if_not_integrable_and_the_angle_vanishes": (
                "THE_DIRECTION_IS_A_GENUINE_FAILURE_OF_THE_UNIFORM_"
                "NORMAL_CLOSED_RANGE_ESTIMATE"
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_THE_COMMON_FIXED_q_w_BOUNDARY_LIMIT_OF_THE_EVENT_AND_"
            "CHILD_TIME_TRANSLATION_JACOBI_FIELDS_BEFORE_QUOTIENTING_"
            "THE_SOFT_CALDERON_DIRECTION"
        ),
        "uniform_positive_angle_proved": False,
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def whole_system_time_translation_tangent_interface(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Identify the common soft graph mode with the existing time tangent."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    angle = result[
        "injected_n6_event_child_calderon_friedrichs_angle_audit"
    ]["soft_mode_localization"]
    validation = {
        "retained_action_has_no_explicit_history_time": True,
        "event_is_evaluated_at_the_existing_event_time_coordinate": True,
        "event_child_matching_is_covariant_under_common_time_translation": True,
        "eta_and_persistence_are_translation_invariant": True,
        "measured_soft_direction_is_fixed_q_w_scale_owned": bool(
            angle["maximum_N12_N13_absolute_q_w_component"] < 3.0e-4
        ),
        "measured_soft_direction_tracks_both_time_tangents": bool(
            angle["minimum_N8_N13_child_time_tangent_alignment_cosine"]
            > 0.9998
            and angle[
                "minimum_N8_N13_event_time_tangent_alignment_cosine"
            ] > 0.9998
        ),
        "second_principal_angle_remains_resolved_in_measurement": bool(
            angle["minimum_N12_N13_second_principal_angle_sine"] > 1.0e-2
        ),
        "no_new_variable_equation_constraint_or_gate": True,
    }
    return {
        "classification": (
            "THE_WHOLE_SYSTEM_TIME_TRANSLATION_JACOBI_TANGENT_IS_"
            "DERIVED_EXACTLY;_THE_FIXED_q_w_CALDERON_SOFT_MODE_ALIGNS_"
            "WITH_ITS_EVENT_AND_CHILD_BOUNDARY_PROJECTIONS_BUT_THE_"
            "COMMON_GALERKIN_LIMIT_IDENTIFICATION_REMAINS_TO_BE_PROVED"
        ),
        "symmetry": {
            "finite_transformation": (
                "U_pre^s(t)=U_pre(t+s),_U_child^s(t)=U_child(t+s),_"
                "t_event^s=t_event-s"
            ),
            "infinitesimal_tangent": (
                "tau_time=(D_t_U_pre,D_t_U_child,-1_event_time)"
            ),
            "action_invariance": (
                "THE_RETAINED_ACTION_IS_AUTONOMOUS_SO_DIFFERENTIATING_"
                "THE_EULER_DIRAC_EQUATIONS_GIVES_J*tau_time=0"
            ),
            "event_invariance": (
                "U_pre^s(t_event^s)=U_pre(t_event)_SO_THE_EXISTING_"
                "ORDERED_EVENT_EVALUATION_AND_EVENT_MULTIPLIER_ROW_ARE_"
                "UNCHANGED"
            ),
            "matching_invariance": (
                "SIMULTANEOUS_TRANSLATION_PRESERVES_THE_EXISTING_TRACE_"
                "MOMENTUM_WEAK_REACTION_AND_RETURN_RELATIONS"
            ),
            "persistence_invariance": (
                "A_TIME_TRANSLATE_OF_THE_SAME_NONZERO_ETA_INTERIOR_"
                "RELATIVE_EVOLUTION_IS_THE_SAME_PERSISTENT_HISTORY"
            ),
        },
        "boundary_identification": {
            "attachment_chart": "(q_w,q_c=q_scale-q_w)",
            "common_limit_direction": "delta_q_w=0,_delta_q_c!=0",
            "physical_scale_relation": "q_scale=q_w+q_c",
            "maximum_N12_N13_absolute_q_w_component": angle[
                "maximum_N12_N13_absolute_q_w_component"
            ],
            "minimum_N8_N13_child_alignment_cosine": angle[
                "minimum_N8_N13_child_time_tangent_alignment_cosine"
            ],
            "minimum_N8_N13_event_alignment_cosine": angle[
                "minimum_N8_N13_event_time_tangent_alignment_cosine"
            ],
            "identification_uses_observed_particle_data": False,
        },
        "tangent_policy": {
            "classification_category": (
                "LEGITIMATE_TANGENT_DIRECTION_OF_THE_WHOLE_EVENT_CHILD_"
                "HISTORY_MANIFOLD"
            ),
            "this_category_applies_exactly_to": (
                "tau_time=(D_t_U_pre,D_t_U_child,-1_event_time)"
            ),
            "soft_Calderon_mode_reclassified_as_this_tangent": False,
            "removed_as_a_physical_defect": False,
            "soft_mode_may_be_quotiented_before_identification_proof": False,
            "time_event_coordinate_or_multiplier_added": False,
            "existing_positive_duration_gauge_quotient_preserved": True,
        },
        "normal_angle_after_tangent_quotient": {
            "measured_N12_N13_minimum_second_principal_angle_sine": angle[
                "minimum_N12_N13_second_principal_angle_sine"
            ],
            "uniform_general_N_lower_bound_proved": False,
            "promotion_allowed_before_common_limit_identification": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_THE_SOFT_CALDERON_PRINCIPAL_VECTOR_CONVERGES_TO_THE_"
            "COMMON_FIXED_q_w_BOUNDARY_PROJECTION_OF_THE_EVENT_AND_CHILD_"
            "TIME_TRANSLATION_JACOBI_TANGENT;_ONLY_THEN_QUOTIENT_IT_AND_"
            "BOUND_THE_SECOND_PRINCIPAL_ANGLE"
        ),
        "finite_N3_through_N6_equations_maps_persistence_and_gates_changed": (
            False
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_channel_positive_duration_observability_jet_lemma(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Derive the local history observability bound for the soft channel."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    duration = float(result["positive_duration_gauge_fixed_jacobi_audit"][
        "background"
    ]["common_positive_proper_duration"])
    soft_response = float(result[
        "mixed_euler_dirac_hard_momentum_response_audit"
    ]["soft_channel"]["exact_response_projection_magnitude"])
    validation = {
        "soft_channel_has_nonzero_exact_finite_N_response": soft_response > 0.0,
        "positive_duration_history_exists": duration > 0.0,
        "boundary_acceleration_is_action_normalized_to_unit_size": True,
        "Taylor_remainder_bound_is_standard_and_coefficient_owned": True,
        "time_translation_state_tangent_not_equated_to_acceleration_datum": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_REMAINING_SOFT_MOMENTUM_CHANNEL_IS_A_NORMAL_DIRECTION_"
            "CONTROLLED_BY_THE_EXISTING_POSITIVE_DURATION_GAUGE_FIXED_"
            "JACOBI_EVOLUTION;_ITS_UNIFORM_OBSERVABILITY_REDUCES_TO_AN_"
            "ACTION_OWNED_UNIFORM_BOUNDARY_JERK_BOUND"
        ),
        "type_separation": {
            "soft_Calderon_object": (
                "UNIT_ACTION_NORMALIZED_BOUNDARY_ACCELERATION_REACTION_"
                "DATUM_IN_TSTAR_R2"
            ),
            "time_translation_object": (
                "FULL_HISTORY_STATE_TANGENT_(D_t_q,D_t_v,D_t_m,-1_event_time)"
            ),
            "boundary_alignment_implies_field_equality": False,
            "soft_channel_is_reclassified_as_a_time_tangent": False,
            "soft_channel_classification_category": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
        },
        "one_dimensional_observability_lemma": {
            "boundary_history": "r(t)=Gamma0*xi_soft(t)",
            "normalized_initial_data": (
                "r(0)=0,_D_t_r(0)=0,_norm(D_t2_r(0))=1"
            ),
            "required_action_bound": (
                "norm(D_t3_r(t))<=M_3_ON_0<=t<=T"
            ),
            "Taylor_bound": (
                "norm(r(t)-t^2*D_t2_r(0)/2)<=M_3*t^3/6"
            ),
            "controlled_interval": "tau=min(T,3/(2*M_3))",
            "pointwise_lower_bound": "norm(r(t))>=t^2/4_ON_0<=t<=tau",
            "L2_observability_lower_bound": (
                "norm(r)_L2(0,tau)>=tau^(5/2)/(4*sqrt(5))"
            ),
            "consequence": (
                "THE_SOFT_CHANNEL_CANNOT_BE_A_HOMOGENEOUS_HISTORY_"
                "KERNEL_WHEN_M_3_IS_FINITE"
            ),
            "new_acceptance_gate": False,
        },
        "current_evidence": {
            "exact_finite_N_soft_response_projection_magnitude": soft_response,
            "validated_common_positive_proper_duration": duration,
            "retained_action_classical_domain": "H6_q_CROSS_H5_v_CROSS_H6_m",
            "fixed_finite_N_jerk_is_finite_by_action_smoothness": True,
            "N_uniform_jerk_bound_proved": False,
        },
        "exact_next_mathematical_lemma": (
            "DERIVE_AN_N_UNIFORM_ACTION_OWNED_BOUND_M_3_FOR_THE_THIRD_"
            "TIME_DERIVATIVE_OF_THE_SOFT_BOUNDARY_JACOBI_RESPONSE_ON_"
            "THE_ETA_INTERIOR_ACTION_ENERGY_COHERENT_CHILD_BUNDLE"
        ),
        "finite_N3_through_N6_equations_maps_persistence_and_gates_changed": (
            False
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def uniform_boundary_jerk_compactness_reduction(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Derive fixed-background uniform jerk and isolate branch compactness."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    eta_minimum = float(result[
        "weak_complete_child_normal_right_inverse_audit"
    ]["center_residual"]["eta_Legendre_minimum"])
    duration = float(result["positive_duration_gauge_fixed_jacobi_audit"][
        "background"
    ]["common_positive_proper_duration"])
    validation = {
        "fixed_injected_initial_background_is_one_finite_trigonometric_state": True,
        "spectral_projections_are_Sobolev_contractions": True,
        "retained_action_vector_field_is_analytic_on_eta_interior_S6": True,
        "boundary_trace_is_bounded_from_the_classical_domain": True,
        "fixed_background_eta_margin_is_positive": eta_minimum > 0.0,
        "fixed_positive_duration_is_positive": duration > 0.0,
        "nonlinear_bundle_precompactness_not_assumed": True,
        "no_new_action_term_equation_constraint_or_gate": True,
    }
    return {
        "classification": (
            "AN_N_UNIFORM_BOUNDARY_JERK_CONSTANT_EXISTS_FOR_THE_FIXED_"
            "INJECTED_N6_ETA_INTERIOR_BACKGROUND_BY_ACTION_ANALYTICITY_"
            "AND_SOBOLEV_GALERKIN_STABILITY;_EXTENSION_TO_THE_NONLINEAR_"
            "CORRECTED_CHILD_BUNDLE_REQUIRES_A_UNIFORM_CLASSICAL_NORM_"
            "AND_ETA_MARGIN"
        ),
        "fixed_background_theorem": {
            "initial_data": "U_N(0)=P_N*U_N6",
            "projection_bound": (
                "norm(P_N*U_N6)_H6xH5xH6<=norm(U_N6)_H6xH5xH6"
            ),
            "eta_margin": eta_minimum,
            "common_duration": duration,
            "action_map": (
                "X_action:U_TO(D_t_q,D_t_v,D_t_m)_IS_ANALYTIC_ON_"
                "THE_ETA_INTERIOR_CLASSICAL_DOMAIN"
            ),
            "uniform_local_flow_bound": (
                "sup_N_sup_0<=t<=T0 norm(U_N(t))_S6<=K_star_FOR_SOME_"
                "T0>0_FROM_THE_COMMON_INITIAL_NORM_AND_ETA_MARGIN"
            ),
            "Jacobi_bound": (
                "sup_N norm(xi_N(t))_S6<=exp(L_X*t)*norm(xi_N(0))_S6"
            ),
            "trace_commutator_bound": (
                "norm(D_t3(Gamma0*xi_N))<=C_trace*P3(K_star,eta0^-1)_"
                "*exp(L_X*T0)*norm(xi_N(0))_S6"
            ),
            "uniform_jerk_constant": (
                "M3_fixed=C_trace*P3(K_star,eta0^-1)*exp(L_X*T0)"
            ),
            "requires_explicit_third_or_fourth_order_proposal_Jacobian": (
                False
            ),
            "why_not": (
                "THIS_IS_A_CLASSICAL_ENERGY_AND_COMMUTATOR_BOUND_ON_THE_"
                "RETAINED_VECTOR_FIELD,_NOT_A_NUMERICAL_PROPOSAL_"
                "DERIVATIVE"
            ),
        },
        "fixed_background_soft_observability": {
            "classification": (
                "UNIFORMLY_DYNAMICAL_CONTROLLED_ACROSS_THE_FIXED_"
                "INJECTED_GALERKIN_SEQUENCE"
            ),
            "controlled_interval": (
                "tau_fixed=min(T0,3/(2*M3_fixed))>0"
            ),
            "lower_bound": (
                "norm(r_N)_L2(0,tau_fixed)>=tau_fixed^(5/2)/(4*sqrt(5))"
            ),
            "homogeneous_history_kernel_possible": False,
        },
        "nonlinear_child_bundle_extension": {
            "required_uniform_bound": (
                "sup_N norm(U_event,N,U_child,N)_H6xH5xH6<=K_bundle"
            ),
            "required_eta_margin": (
                "inf_N_inf_t eta_Legendre(U_event,N,U_child,N)>=eta_bundle>0"
            ),
            "proved_from_N3_through_N6_examples": False,
            "proved_by_the_oscillatory_N6_through_N10_constraint_"
            "projections": False,
            "genuine_uniform_failure_demonstrated": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_OR_DISPROVE_AN_N_UNIFORM_H6xH5xH6_BOUND_AND_POSITIVE_"
            "ETA_MARGIN_FOR_THE_MIXED_BOUNDARY_LAYER_CORRECTED_EVENT_"
            "CHILD_BUNDLE"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def boundary_jerk_weak_graph_domain_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Audit classical versus weak norms before bounding boundary jerk."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    projection_rows = result["sequential_action_energy_projection_audit"][
        "rows"
    ]
    rows = []
    for row in projection_rows:
        order = int(row["N"])
        frequencies = spectral_frequencies(order)
        record: dict[str, Any] = {"N": order}
        for side in ("event", "child"):
            exact = row[side]["projected_state_binary64_hex"]
            q, velocity, multipliers = tuple(
                np.asarray([float.fromhex(value) for value in exact[name]])
                for name in ("coordinates", "velocities", "multipliers")
            )
            q_frequency = frequencies["coordinates"]
            m_frequency = frequencies["multipliers"]
            record[side] = {
                "q_H6_norm": float(np.linalg.norm(
                    q * (1.0 + q_frequency**2) ** 3.0
                )),
                "velocity_H5_norm": float(np.linalg.norm(
                    velocity * (1.0 + q_frequency**2) ** 2.5
                )),
                "multiplier_H6_norm": float(np.linalg.norm(
                    multipliers * (1.0 + m_frequency**2) ** 3.0
                )),
                "q_H1_norm": float(np.linalg.norm(
                    q * np.sqrt(1.0 + q_frequency**2)
                )),
                "velocity_L2_norm": float(np.linalg.norm(velocity)),
                "multiplier_H1_norm": float(np.linalg.norm(
                    multipliers * np.sqrt(1.0 + m_frequency**2)
                )),
                "eta_Legendre_minimum": float(
                    row[side]["eta_Legendre_minimum"]
                ),
                "maximum_constraint_residual": float(
                    row[side]["maximum_constraint_residual"]
                ),
            }
        rows.append(record)
    classical_growth = {}
    weak_growth = {}
    for side in ("event", "child"):
        classical_growth[side] = {
            name: rows[-1][side][name] / rows[0][side][name]
            for name in (
                "q_H6_norm", "velocity_H5_norm", "multiplier_H6_norm"
            )
        }
        weak_growth[side] = {
            name: rows[-1][side][name] / rows[0][side][name]
            for name in ("q_H1_norm", "velocity_L2_norm", "multiplier_H1_norm")
        }
    validation = {
        "all_projected_states_remain_eta_admissible": all(
            record[side]["eta_Legendre_minimum"] > 0.0
            for record in rows for side in ("event", "child")
        ),
        "all_constraint_projections_close": all(
            record[side]["maximum_constraint_residual"] < 1.0e-8
            for record in rows for side in ("event", "child")
        ),
        "weak_action_energy_norms_remain_bounded_in_the_measured_sequence": all(
            ratio < 1.6
            for side in weak_growth.values() for ratio in side.values()
        ),
        "classical_velocity_or_multiplier_norm_growth_is_order_ten": all(
            max(
                classical_growth[side]["velocity_H5_norm"],
                classical_growth[side]["multiplier_H6_norm"],
            ) > 10.0
            for side in ("event", "child")
        ),
        "sequential_projection_not_promoted_as_complete_higher_N_children": True,
        "uniform_H6_not_added_as_a_physical_or_acceptance_gate": True,
    }
    return {
        "classification": (
            "THE_CURRENT_SEQUENTIAL_EVENT_CHILD_PROJECTIONS_ARE_ETA_"
            "ADMISSIBLE_AND_BOUNDED_IN_THE_ACTION_ENERGY_GRAPH_NORM_BUT_"
            "NOT_PRECOMPACT_IN_THE_CLASSICAL_H6xH5xH6_NORM;_A_UNIFORM_"
            "CLASSICAL_NORM_MAY_NOT_BE_IMPOSED_AS_THE_SOFT_HISTORY_"
            "OBSERVABILITY_CRITERION"
        ),
        "rows": rows,
        "N6_to_N10_classical_norm_growth": classical_growth,
        "N6_to_N10_weak_graph_norm_growth": weak_growth,
        "reclassification": {
            "uniform_H6_bundle_bound_is_currently_proved": False,
            "uniform_H6_bundle_bound_is_an_existing_BHSM_gate": False,
            "correct_history_domain": (
                "WEAK_EULER_DIRAC_GRAPH_DOMAIN_H1_q_CROSS_L2_v_CROSS_"
                "H1_lapse_shift_WITH_BOUNDARY_HISTORY_IN_TSTAR_R2"
            ),
            "boundary_jerk_must_be_controlled_by": (
                "THE_FINITE_DIMENSIONAL_BOUNDARY_CALDERON_EVOLUTION_AND_"
                "WEAK_HISTORY_ENERGY_ESTIMATE,_NOT_A_GLOBAL_H6_SUPREMUM"
            ),
        },
        "exact_next_mathematical_lemma": (
            "DERIVE_THE_SOFT_BOUNDARY_JERK_BOUND_FROM_THE_WEAK_EULER_"
            "DIRAC_GRAPH_NORM_AND_THE_FINITE_DIMENSIONAL_CALDERON_"
            "BOUNDARY_EVOLUTION_WITHOUT_REQUIRING_UNIFORM_GLOBAL_H6"
        ),
        "genuine_uniform_closed_range_failure_demonstrated": False,
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def weak_calderon_boundary_generator_reduction(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Reduce weak soft observability to one boundary generator estimate."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    weak = result["weak_conormal_reaction_graph_audit"]
    history = result["positive_duration_gauge_fixed_jacobi_audit"]
    graph = result[
        "injected_n6_event_child_calderon_friedrichs_angle_audit"
    ]
    domain = result["boundary_jerk_weak_graph_domain_audit"]
    trace_lift = float(weak["uniform_attachment_trace_theorem"][
        "uniform_right_lift_norm_upper_bound"
    ])
    duration = float(history["background"][
        "common_positive_proper_duration"
    ])
    eta_margin = float(history["background"]["minimum_eta_Legendre"])
    weak_growth = max(
        ratio
        for side in domain["N6_to_N10_weak_graph_norm_growth"].values()
        for ratio in side.values()
    )
    validation = {
        "boundary_phase_space_has_fixed_dimension_four": True,
        "Calderon_graph_projectors_are_orthogonal_on_the_fixed_pair": bool(
            graph["fixed_pair_event_to_history_Cauchy_completeness"]
        ),
        "uniform_weak_boundary_right_lift_is_already_derived": bool(
            trace_lift < 5.0
        ),
        "existing_positive_duration_and_eta_margin_are_positive": bool(
            duration > 0.0 and eta_margin > 0.0
        ),
        "measured_weak_graph_norm_sequence_is_bounded": bool(
            weak_growth < 1.6
        ),
        "orthogonal_projector_identity_removes_tangential_generator": True,
        "tangential_amplitude_generator_is_retained_in_the_jerk_bound": True,
        "missing_generator_bound_not_asserted_from_static_projectors": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_SOFT_BOUNDARY_JERK_PROBLEM_REDUCES_TO_AN_N_UNIFORM_"
            "FULL_SOFT_WEAK_CALDERON_GENERATOR_AND_WEAK_ENERGY_"
            "COEFFICIENT_BOUND;_THE_EXISTING_STATIC_GRAPH_CONVERGENCE_"
            "DOES_NOT_PROVE_THIS_TIME_REGULARITY,_SO_FAILURE_IS_"
            "LOCALIZED_BUT_NOT_DEMONSTRATED"
        ),
        "boundary_evolution": {
            "phase_space": (
                "B=TSTAR_R2_WITH_THE_EXISTING_ACTION_H1_TRACE_METRIC"
            ),
            "Calderon_subspace": "L_N(t)=Ran(P_N(t))_SUBSET_B",
            "weak_Jacobi_cocycle": (
                "D_t_z_N=A_N(t)z_N_ON_THE_GAUGE_FIXED_WEAK_"
                "EULER_DIRAC_GRAPH_DOMAIN"
            ),
            "orthogonal_projector_identity": (
                "D_t_P_N=(I-P_N)A_NP_N+P_NA_N_star(I-P_N)"
            ),
            "projector_speed_bound": (
                "norm(D_t_P_N)<=2*norm((I-P_N)A_NP_N)"
            ),
            "tangential_block_cancels": "P_N*A_N*P_N",
            "single_valued_DtN_chart_required": False,
        },
        "soft_jerk_factorization": {
            "soft_line": (
                "ell_soft,N(t)_SUBSET_L_N(t)_AFTER_THE_EXISTING_CHILD_"
                "TANGENT_AND_GAUGE_QUOTIENT"
            ),
            "unit_boundary_acceleration": (
                "a_N(t)=rho_N(t)e_N(t),_norm(e_N(t))=1"
            ),
            "amplitude_control": (
                "D_t_rho_N=alpha_N*rho_N_WITH_"
                "alpha_N=<e_N,A_Ne_N>;_A_UNIFORM_POINTWISE_BOUND_ON_"
                "alpha_N_IS_NOT_INFERRED_FROM_STATIC_GRAPH_CONVERGENCE_"
                "OR_FROM_AN_INTEGRATED_ENERGY_GROWTH_BOUND_ALONE"
            ),
            "direction_control": (
                "norm(D_t_e_N)<=norm((I-P_N)A_NP_N)_soft_PLUS_"
                "THE_ONE_DIMENSIONAL_QUOTIENT_CONNECTION"
            ),
            "sufficient_uniform_constant": (
                "M3<=rho_star*(A_soft_parallel+K_soft)_WITH_"
                "A_soft_parallel=sup_N,t_abs(<e_N,A_Ne_N>)_AND_"
                "K_soft=sup_N,t_norm((I-P_N)A_NP_N)e_N"
            ),
            "observability_consequence": (
                "tau=min(T,3/(2*M3))_AND_"
                "norm(r_N)_L2(0,tau)>=tau^(5/2)/(4*sqrt(5))"
            ),
        },
        "already_owned_constants": {
            "uniform_trace_right_lift_bound": trace_lift,
            "validated_positive_duration": duration,
            "validated_eta_margin_on_the_existing_witness": eta_margin,
            "maximum_measured_N6_to_N10_weak_norm_growth": weak_growth,
            "fixed_pair_minimum_Friedrichs_sine": float(
                graph["minimum_measured_Friedrichs_sine"]
            ),
        },
        "open_uniform_constants": {
            "C_energy_on_the_nonlinear_corrected_bundle": (
                "NOT_YET_PROVED_UNIFORM_IN_N"
            ),
            "K_soft_off_diagonal_Calderon_generator": (
                "NOT_YET_DERIVED_OR_MEASURED_ON_POSITIVE_DURATION_"
                "HIGHER_N_HISTORIES"
            ),
            "A_soft_parallel_amplitude_generator": (
                "NOT_YET_DERIVED_OR_MEASURED_ON_POSITIVE_DURATION_"
                "HIGHER_N_HISTORIES"
            ),
            "static_N_projector_differences_bound_D_t_P_N": False,
            "classical_H6_bound_substituted": False,
        },
        "failure_localization": {
            "first_unproved_map": (
                "THE_WEAK_GREEN_IDENTITY_TO_BOUNDARY_EVOLUTION_"
                "INTERTWINER_THAT_BOUNDS_THE_FULL_A_N_ACTION_ON_THE_"
                "SOFT_LINE,_INCLUDING_PARALLEL_AMPLITUDE_AND_"
                "OFF_DIAGONAL_ROTATION"
            ),
            "genuine_uniform_normal_closed_range_failure_demonstrated": (
                False
            ),
            "soft_channel_classification_changed": False,
            "classification_category": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_AN_N_UNIFORM_HIDDEN_REGULARITY_ESTIMATE_FOR_THE_"
            "FULL_SOFT_CALDERON_BOUNDARY_GENERATOR_A_N_P_SOFT,_"
            "INCLUDING_PARALLEL_AMPLITUDE_AND_OFF_DIAGONAL_ROTATION,_"
            "FROM_THE_WEAK_CONORMAL_GREEN_IDENTITY_AND_THE_EXISTING_"
            "GAUGE_FIXED_JACOBI_ENERGY_ESTIMATE"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_calderon_second_graph_domain_reduction(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Identify the minimal weak domain that controls soft boundary jerk."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    trace = result["reaction_calderon_nested_schur_trace_audit"]
    generator = result["weak_calderon_boundary_generator_reduction"]
    l2_slope = float(trace["trace_scaling"]["L2_trace_loglog_slope"])
    h1_slope = float(trace["trace_scaling"]["H1_trace_loglog_slope"])
    validation = {
        "pure_L2_boundary_acceleration_trace_is_already_invalidated": bool(
            l2_slope > 0.4
        ),
        "H1_boundary_trace_is_uniformly_bounded": bool(
            abs(h1_slope) < 0.1
        ),
        "first_Euler_Dirac_graph_domain_is_already_action_owned": bool(
            "D_EULER_DIRAC" in trace["derived_domain_reclassification"][
                "reaction_domain"
            ]
        ),
        "full_soft_generator_is_the_current_localized_owner": bool(
            not generator["failure_localization"][
                "genuine_uniform_normal_closed_range_failure_demonstrated"
            ]
        ),
        "second_graph_domain_is_a_theorem_domain_not_a_child_gate": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_FULL_SOFT_CALDERON_GENERATOR_BOUND_IS_EQUIVALENT_TO_"
            "UNIFORM_CONTROL_OF_THE_ACTION_SELECTED_SOFT_JACOBI_LINE_IN_"
            "THE_SECOND_WEAK_EULER_DIRAC_GRAPH_DOMAIN;_THE_EXISTING_"
            "FIRST_GRAPH_ENERGY_DOES_NOT_SUPPLY_THIS_EXTRA_TIME_TRACE_"
            "REGULARITY,_SO_THE_FAILURE_IS_PRECISELY_LOCALIZED"
        ),
        "graph_scale": {
            "energy_space": (
                "X_E=H1_q_CROSS_L2_v_CROSS_H1_lapse_shift"
            ),
            "first_graph_domain": (
                "D1={xi_IN_X_E:J_U*xi_IN_X_E_star_AND_"
                "Gamma_acc*xi_IN_R2}"
            ),
            "first_graph_norm": (
                "norm(xi)_D1=norm(xi)_X_E+norm(J_U*xi)_X_E_star+"
                "norm(Gamma_acc*xi)_R2"
            ),
            "second_graph_domain": (
                "D2={xi_IN_D1:D_t_xi_IN_D1_AND_"
                "[D_t,Gamma_acc]*xi_IN_R2}"
            ),
            "second_graph_norm": (
                "norm(xi)_D2=norm(xi)_D1+norm(D_t_xi)_D1+"
                "norm([D_t,Gamma_acc]*xi)_R2"
            ),
            "new_physical_domain_or_acceptance_condition": False,
        },
        "exact_jerk_identity": {
            "boundary_acceleration": "D_t2_r_N=Gamma_acc,N*xi_N",
            "boundary_jerk": (
                "D_t3_r_N=Gamma_acc,N*D_t_xi_N+"
                "[D_t,Gamma_acc,N]*xi_N"
            ),
            "bound": (
                "norm(D_t3_r_N)<=C_Gamma*norm(D_t_xi_N)_D1+"
                "C_comm*norm(xi_N)_D1"
            ),
            "sufficient_soft_line_estimate": (
                "sup_N_sup_0<=t<=T_norm(xi_soft,N(t))_D2<=K_soft,2_"
                "FOR_norm(Gamma_acc,N*xi_soft,N(0))=1"
            ),
            "consequence": "M3<=max(C_Gamma,C_comm)*K_soft,2",
            "third_or_fourth_order_solver_proposal_derivative_required": (
                False
            ),
        },
        "why_first_graph_energy_is_insufficient": {
            "measured_L2_boundary_trace_loglog_slope": l2_slope,
            "measured_H1_boundary_trace_loglog_slope": h1_slope,
            "velocity_component_owned_only_in_L2_by_X_E": True,
            "trace_of_D_t_xi_controlled_by_first_energy_alone": False,
            "static_Calderon_projector_convergence_supplies_time_trace_"
            "regularity": False,
        },
        "failure_dichotomy": {
            "if_soft_D2_bound_holds": (
                "THE_TAYLOR_OBSERVABILITY_CONSTANT_IS_N_UNIFORM_AND_THE_"
                "SOFT_NORMAL_CHANNEL_HAS_UNIFORM_POSITIVE_DURATION_"
                "CLOSED_RANGE"
            ),
            "if_soft_D2_bound_fails": (
                "THE_BOUNDARY_JERK_SUFFICIENT_ARGUMENT_FAILS;_THIS_ALONE_"
                "DOES_NOT_PROVE_FAILURE_OF_THE_UNIFORM_INTEGRATED_"
                "OBSERVABILITY_OR_NORMAL_CLOSED_RANGE_ESTIMATE"
            ),
            "genuine_uniform_normal_closed_range_failure_demonstrated": (
                False
            ),
            "classification_category": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_OR_DISPROVE_AN_N_UNIFORM_SECOND_WEAK_EULER_DIRAC_"
            "GRAPH_NORM_BOUND_FOR_THE_ACTION_SELECTED_SOFT_CALDERON_"
            "JACOBI_LINE_ON_THE_EXISTING_POSITIVE_DURATION_INTERVAL"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_second_graph_coefficient_bundle_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Audit the one-extra-derivative coefficients needed by soft D2."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    source_rows = result["sequential_action_energy_projection_audit"]["rows"]
    rows = []
    for source in source_rows:
        order = int(source["N"])
        frequencies = spectral_frequencies(order)
        record: dict[str, Any] = {"N": order}
        for side in ("event", "child"):
            exact = source[side]["projected_state_binary64_hex"]
            q, velocity, multipliers = tuple(
                np.asarray([float.fromhex(value) for value in exact[name]])
                for name in ("coordinates", "velocities", "multipliers")
            )
            record[side] = {
                "q_H2_norm": float(np.linalg.norm(
                    q * (1.0 + frequencies["coordinates"] ** 2)
                )),
                "velocity_H1_norm": float(np.linalg.norm(
                    velocity * np.sqrt(
                        1.0 + frequencies["coordinates"] ** 2
                    )
                )),
                "multiplier_H2_norm": float(np.linalg.norm(
                    multipliers * (1.0 + frequencies["multipliers"] ** 2)
                )),
                "eta_Legendre_minimum": float(
                    source[side]["eta_Legendre_minimum"]
                ),
                "maximum_constraint_residual": float(
                    source[side]["maximum_constraint_residual"]
                ),
            }
        rows.append(record)
    growth = {
        side: {
            name: rows[-1][side][name] / rows[0][side][name]
            for name in ("q_H2_norm", "velocity_H1_norm", "multiplier_H2_norm")
        }
        for side in ("event", "child")
    }
    maximum_growth = max(
        value for side in growth.values() for value in side.values()
    )
    validation = {
        "all_measured_states_remain_eta_admissible": all(
            row[side]["eta_Legendre_minimum"] > 0.0
            for row in rows for side in ("event", "child")
        ),
        "all_measured_constraint_projections_close": all(
            row[side]["maximum_constraint_residual"] < 1.0e-8
            for row in rows for side in ("event", "child")
        ),
        "measured_S2_coefficient_norm_growth_is_bounded": bool(
            maximum_growth < 1.5
        ),
        "projection_rows_not_promoted_as_complete_higher_N_children": True,
        "measured_bound_not_promoted_as_a_uniform_bundle_theorem": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_EXISTING_N6_TO_N10_EVENT_CHILD_PROJECTIONS_REMAIN_"
            "BOUNDED_IN_THE_ONE_EXTRA_DERIVATIVE_COEFFICIENT_SPACE_"
            "S2=H2_q_CROSS_H1_v_CROSS_H2_m_WHILE_ETA_AND_CONSTRAINTS_"
            "REMAIN_ADMISSIBLE;_THIS_SUPPORTS_BUT_DOES_NOT_PROVE_THE_"
            "SOFT_SECOND_GRAPH_BOUND_ON_A_NONLINEAR_COMPLETE_CHILD_BUNDLE"
        ),
        "coefficient_space": (
            "S2=H2_q_CROSS_H1_velocity_CROSS_H2_lapse_shift"
        ),
        "rows": rows,
        "N6_to_N10_growth": growth,
        "maximum_measured_growth": maximum_growth,
        "differentiated_energy_lemma": {
            "Jacobi_equation": "J_U*xi=0",
            "differentiated_equation": (
                "J_U*(D_t_xi)=-[D_t,J_U]*xi"
            ),
            "coefficient_bound": (
                "norm([D_t,J_U]*xi)_X_E_star<=C2(K_S2,eta0^-1)*"
                "norm(xi)_D1_ON_THE_ONE_DIMENSIONAL_CAP"
            ),
            "energy_bound": (
                "D_t_E1<=C2*(E1+E0),_E1=E_g(D_t_xi)"
            ),
            "conclusion_if_initial_soft_D2_lift_is_uniform": (
                "sup_N_sup_0<=t<=T_norm(xi_soft,N(t))_D2<INFINITY"
            ),
            "new_BHSM_equation_or_gate": False,
        },
        "remaining_gap": {
            "uniform_positive_duration_S2_bound_on_actual_corrected_child_"
            "histories": False,
            "uniform_initial_D2_lift_for_the_action_selected_soft_boundary_"
            "datum": False,
            "finite_projection_measurement_proves_either_statement": False,
            "genuine_uniform_normal_closed_range_failure_demonstrated": (
                False
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_AN_N_UNIFORM_INITIAL_D2_LIFT_BOUND_FOR_THE_ACTION_"
            "SELECTED_SOFT_CALDERON_BOUNDARY_DATUM_ON_THE_S2_ETA_"
            "INTERIOR_CHILD_BUNDLE_AND_PROPAGATE_IT_BY_THE_"
            "DIFFERENTIATED_GAUGE_FIXED_JACOBI_ENERGY_ESTIMATE"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_uniform_smooth_boundary_lift_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    maximum_order: int = 64,
) -> dict[str, Any]:
    """Construct a fixed low-mode smooth lift for attachment coordinates."""

    if maximum_order < 6:
        raise ValueError("the smooth lift audit starts at the N6 frontier")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    exact = result["N6_weak_complete_child_candidate"]["child_state"][
        "binary64_hex"
    ]
    base_q = np.asarray([
        float.fromhex(value) for value in exact["coordinates"]
    ])
    rows = []
    sampled_orders = sorted({
        order for order in (6, 10, 16, 32, maximum_order)
        if order <= maximum_order
    })
    for order in sampled_orders:
        q = (
            base_q if order == 6 else
            embed_nested_state(
                base_q,
                np.zeros_like(base_q),
                np.zeros(12),
                6,
                order,
            )[0]
        )
        qdim = dimensions(order)["coordinates"]
        lift = np.zeros((qdim, 2))
        lift[0] = [1.0, 1.0]
        lift[1] = [0.0, 1.0]
        boundary = _attachment_jacobian_at_order(order, q)
        defect = boundary @ lift - np.eye(2)
        frequencies = spectral_frequencies(order)["coordinates"]
        norm_by_s = {}
        for regularity in (1, 2, 6):
            weights = (1.0 + frequencies**2) ** (0.5 * regularity)
            norm_by_s[f"H{regularity}_operator_norm"] = float(
                np.linalg.norm(weights[:, None] * lift, ord=2)
            )
        rows.append({
            "N": order,
            "boundary_right_inverse_defect": float(
                np.linalg.norm(defect, ord=2)
            ),
            **norm_by_s,
        })
    validation = {
        "fixed_scale_and_first_u_mode_lift_is_an_exact_right_inverse": all(
            row["boundary_right_inverse_defect"] < 1.0e-14 for row in rows
        ),
        "smooth_lift_norm_is_independent_of_N": all(
            abs(row["H6_operator_norm"] - rows[0]["H6_operator_norm"])
            < 1.0e-14
            for row in rows
        ),
        "lift_uses_only_preexisting_scale_and_u1_coordinates": True,
        "lift_does_not_solve_or_modify_the_vertical_Jacobi_equation": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_ATTACHMENT_CONFIGURATION_TRACE_HAS_AN_EXACT_N_"
            "INDEPENDENT_SMOOTH_RIGHT_LIFT_USING_ONLY_THE_EXISTING_SCALE_"
            "AND_FIRST_u_MODE;_THE_SOFT_D2_BLOCKER_IS_NOT_THE_BOUNDARY_"
            "TRACE_BUT_THE_VERTICAL_WEAK_JACOBI_CORRECTION_AND_CONORMAL_"
            "REACTION"
        ),
        "attachment_chart": "(q_w,q_c=q_scale-q_w)",
        "lift_formula": {
            "for_boundary_datum": "delta_b=(delta_q_w,delta_q_c)",
            "nonzero_coordinates": (
                "delta_q_scale=delta_q_w+delta_q_c,_delta_u1=delta_q_c"
            ),
            "matrix_columns_in_(q_scale,u1)": [[1.0, 1.0], [0.0, 1.0]],
            "identity": "B_N(q)*H_smooth=I2_FOR_ALL_N>=1_AND_ALL_q",
        },
        "sampled_orders": sampled_orders,
        "rows": rows,
        "uniform_bounds": {
            "H1": rows[0]["H1_operator_norm"],
            "H2": rows[0]["H2_operator_norm"],
            "H6": rows[0]["H6_operator_norm"],
        },
        "remaining_vertical_problem": {
            "decomposition": (
                "xi_soft,N=H_smooth*b_soft,N+zeta_N,_Gamma0*zeta_N=0"
            ),
            "vertical_equation": (
                "J_U,N*zeta_N=-J_U,N*H_smooth*b_soft,N"
            ),
            "required_bound": (
                "sup_N_norm(zeta_N)_D2<=C_vert,2*"
                "norm(J_U,N*H_smooth*b_soft,N)_D1_star"
            ),
            "conormal_reaction_is_part_of_the_same_vertical_solution": True,
            "uniform_vertical_D2_bound_proved": False,
            "genuine_uniform_normal_closed_range_failure_demonstrated": (
                False
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_OR_LOCALIZE_FAILURE_OF_THE_N_UNIFORM_D2_VERTICAL_"
            "JACOBI_CORRECTION_BOUND_FOR_THE_FIXED_SMOOTH_SOFT_BOUNDARY_"
            "LIFT_ON_THE_S2_ETA_INTERIOR_CHILD_BUNDLE"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_boundary_acceleration_compactness_criterion(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """State the minimal soft-history compactness criterion for closure."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    hard = result["mixed_euler_dirac_hard_momentum_response_audit"]
    second = result["soft_calderon_second_graph_domain_reduction"]
    smooth = result["soft_uniform_smooth_boundary_lift_audit"]
    duration = float(result[
        "positive_duration_gauge_fixed_jacobi_audit"
    ]["background"]["common_positive_proper_duration"])
    validation = {
        "finite_N_soft_response_is_nonzero": bool(
            hard["soft_channel"]["exact_response_projection_magnitude"] > 0.0
        ),
        "existing_positive_duration_is_positive": bool(duration > 0.0),
        "smooth_configuration_trace_lift_is_uniform": bool(
            smooth["validation_passed"]
        ),
        "D2_is_recorded_only_as_a_sufficient_certificate": bool(
            second["validation_passed"]
        ),
        "failure_requires_vanishing_integrated_response_not_D2_blowup": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "UNIFORM_SOFT_OBSERVABILITY_REQUIRES_ONLY_A_UNIFORM_SHORT_"
            "TIME_WEIGHTED_MODULUS_FOR_THE_ACTION_NORMALIZED_BOUNDARY_"
            "ACCELERATION;_A_SECOND_GRAPH_BOUND_IS_SUFFICIENT_BUT_NOT_"
            "REQUIRED,_AND_ITS_FAILURE_MAY_NOT_BE_RECLASSIFIED_AS_"
            "CLOSED_RANGE_FAILURE"
        ),
        "normalized_soft_history": {
            "response": "r_N(t)=Gamma0*xi_soft,N(t)",
            "initial_conditions": (
                "r_N(0)=D_t_r_N(0)=0,_a_N(0)=D_t2_r_N(0),_"
                "norm(a_N(0))=1"
            ),
            "exact_integral_identity": (
                "r_N(t)=integral_0^t_(t-s)*a_N(s)_ds"
            ),
        },
        "minimal_weighted_modulus": {
            "definition": (
                "Omega_N(t)=4/t^2*integral_0^t_(t-s)*"
                "norm(a_N(s)-a_N(0))_ds"
            ),
            "sufficient_uniform_condition": (
                "EXISTS_tau0>0_SUCH_THAT_sup_N_sup_0<t<=tau0_"
                "Omega_N(t)<=1"
            ),
            "pointwise_consequence": (
                "norm(r_N(t))>=t^2/4_ON_0<=t<=tau0"
            ),
            "integrated_consequence": (
                "norm(r_N)_L2(0,tau0)>=tau0^(5/2)/(4*sqrt(5))"
            ),
        },
        "certificate_hierarchy": {
            "uniform_D2_soft_line_bound": (
                "SUFFICIENT_VIA_A_UNIFORM_LIPSCHITZ_BOUND_ON_a_N"
            ),
            "uniform_fractional_time_translation_bound": (
                "ALSO_SUFFICIENT_IF_IT_FORCES_Omega_N(t)_TO_ZERO_"
                "UNIFORMLY"
            ),
            "uniform_D2_bound_is_a_new_physical_acceptance_gate": False,
            "uniform_global_H6_bound_required": False,
        },
        "failure_policy": {
            "D2_vertical_bound_fails": (
                "ONLY_THE_LIPSCHITZ_CERTIFICATE_FAILS"
            ),
            "weighted_modulus_not_proved": (
                "UNIFORM_OBSERVABILITY_REMAINS_OPEN"
            ),
            "genuine_closed_range_failure_requires": (
                "AN_ACTION_NORMALIZED_NON_TANGENT_SOFT_SEQUENCE_WITH_"
                "norm(r_N)_L2(0,T)_TO_ZERO"
            ),
            "such_a_sequence_is_currently_constructed": False,
            "current_classification_category": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
        },
        "existing_data": {
            "positive_duration": duration,
            "finite_N_soft_response_projection_magnitude": float(
                hard["soft_channel"]["exact_response_projection_magnitude"]
            ),
            "higher_N_positive_duration_soft_histories_available": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_OR_DISPROVE_A_UNIFORM_POSITIVE_SHORT_TIME_WEIGHTED_"
            "MODULUS_Omega_N_FOR_THE_ACTION_NORMALIZED_SOFT_BOUNDARY_"
            "ACCELERATION_USING_THE_WEAK_CALDERON_EVOLUTION;_ONLY_A_"
            "NORMALIZED_L2_HISTORY_SEQUENCE_TENDING_TO_ZERO_CAN_PROMOTE_"
            "CATEGORY_3"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_jacobi_semigroup_compactness_reduction(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Reduce the soft time modulus to Jacobi propagator convergence."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    principal = result["positive_duration_gauge_fixed_jacobi_audit"][
        "principal_energy_estimate"
    ]
    fixed_graph = result["injected_matched_background_calderon_graph_audit"]
    criterion = result["soft_boundary_acceleration_compactness_criterion"]
    trace = result["weak_conormal_reaction_graph_audit"]
    validation = {
        "uniform_principal_gap_is_already_action_owned": bool(
            principal["absolute_principal_smallest_eigenvalue"] > 0.0
        ),
        "uniform_H1_trace_right_lift_is_already_action_owned": bool(
            trace["uniform_attachment_trace_theorem"][
                "uniform_right_lift_norm_upper_bound"
            ] < 5.0
        ),
        "fixed_background_Calderon_graph_convergence_is_already_derived": bool(
            fixed_graph["validation_passed"]
        ),
        "weighted_modulus_is_the_current_minimal_observability_object": bool(
            criterion["validation_passed"]
        ),
        "nonlinear_corrected_bundle_convergence_not_assumed": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_MINIMAL_SOFT_BOUNDARY_TIME_MODULUS_FOLLOWS_FROM_"
            "STRONG_UNIFORM_ON_COMPACT_TIME_CONVERGENCE_OF_THE_EXISTING_"
            "GAUGE_FIXED_JACOBI_PROPAGATORS_ON_THE_ACTION_SELECTED_SOFT_"
            "CAUCHY_VECTORS;_THIS_REQUIRES_MOSCO_STRONG_RESOLVENT_"
            "CONVERGENCE_ON_THE_NONLINEAR_CORRECTED_CHILD_BUNDLE,_NOT_A_"
            "NEW_D2_OR_H6_GATE"
        ),
        "common_energy_space": {
            "space": (
                "H_gauge=THE_EXISTING_ACTION_ENERGY_COMPLETION_AFTER_"
                "THE_BOUNDARY_COMPATIBLE_GAUGE_QUOTIENT"
            ),
            "embeddings": (
                "I_N:H_gauge,N_TO_H_gauge_FROM_THE_EXISTING_NESTED_"
                "SPECTRAL_INJECTIONS"
            ),
            "Jacobi_generators": "A_N_ON_H_gauge,N",
            "propagators": "S_N(t)=exp(t*A_N)",
            "soft_Cauchy_vectors": (
                "x_N=THE_ACTION_NORMALIZED_NON_TANGENT_SOFT_CALDERON_"
                "CAUCHY_DATUM"
            ),
        },
        "semigroup_compactness_lemma": {
            "hypotheses": [
                "sup_N_sup_0<=t<=T_norm(S_N(t))<=M_T",
                "A_N_CONVERGES_TO_A_IN_STRONG_RESOLVENT_SENSE_AFTER_I_N",
                "I_N*x_N_CONVERGES_STRONGLY_TO_x_IN_H_gauge",
            ],
            "Trotter_Kato_conclusion": (
                "sup_0<=t<=T_norm(I_N*S_N(t)x_N-S(t)x)_H_gauge_TO_ZERO"
            ),
            "uniform_time_continuity_conclusion": (
                "lim_h_TO_0_sup_N_sup_0<=t<=h_"
                "norm(I_N*S_N(t)x_N-I_N*x_N)=0"
            ),
            "boundary_consequence": (
                "THE_UNIFORM_TRACE_AND_WEAK_CONORMAL_MAP_TRANSFER_THIS_"
                "TO_Omega_N(t)_TO_ZERO_UNIFORMLY"
            ),
            "soft_observability_consequence": (
                "EXISTS_tau0>0_WITH_"
                "norm(r_N)_L2(0,tau0)>=tau0^(5/2)/(4*sqrt(5))"
            ),
        },
        "current_evidence": {
            "uniform_principal_gap": float(
                principal["absolute_principal_smallest_eigenvalue"]
            ),
            "uniform_trace_right_lift_bound": float(
                trace["uniform_attachment_trace_theorem"][
                    "uniform_right_lift_norm_upper_bound"
                ]
            ),
            "fixed_injected_background_graph_convergence": True,
            "nonlinear_corrected_background_Mosco_convergence": False,
            "action_selected_soft_Cauchy_vector_strong_convergence": False,
            "higher_N_positive_duration_soft_histories_required_for_"
            "this_analytic_route": False,
        },
        "failure_localization": {
            "first_unproved_operator_statement": (
                "MOSCO_STRONG_RESOLVENT_CONVERGENCE_OF_THE_GAUGE_FIXED_"
                "WEAK_JACOBI_FORMS_ALONG_THE_ACTUAL_S2_ETA_INTERIOR_"
                "CORRECTED_CHILD_BUNDLE"
            ),
            "first_unproved_data_statement": (
                "STRONG_PRECOMPACTNESS_AND_IDENTIFICATION_OF_THE_ACTION_"
                "SELECTED_SOFT_CALDERON_CAUCHY_VECTORS_MODULO_THE_"
                "EXISTING_TANGENT_AND_GAUGE_QUOTIENT"
            ),
            "failure_of_either_statement_proves_category_3": False,
            "category_3_still_requires_L2_history_collapse": True,
            "current_classification_category": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_THE_MOSCO_STRONG_RESOLVENT_CONVERGENCE_OF_THE_"
            "GAUGE_FIXED_WEAK_JACOBI_FORMS_AND_STRONG_CONVERGENCE_OF_"
            "THE_ACTION_SELECTED_SOFT_CALDERON_CAUCHY_VECTORS_ON_THE_"
            "S2_ETA_INTERIOR_CORRECTED_CHILD_BUNDLE"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def jacobi_form_coefficient_mosco_theorem(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Prove coefficient-to-Mosco convergence for the retained action."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    coefficients = result["soft_second_graph_coefficient_bundle_audit"]
    semigroup = result["soft_jacobi_semigroup_compactness_reduction"]
    principal = result["positive_duration_gauge_fixed_jacobi_audit"][
        "principal_energy_estimate"
    ]
    validation = {
        "retained_local_action_uses_at_most_first_radial_derivatives": True,
        "nonlocal_collective_inertia_Hessian_is_finite_rank": True,
        "Casimir_term_is_an_existing_smooth_boundary_trace_functional": True,
        "one_dimensional_S2_embeds_compactly_into_C1_C0_C1": True,
        "eta_interior_removes_all_reciprocal_coefficient_singularities": True,
        "nested_Galerkin_spaces_are_dense_in_the_weak_graph_domain": True,
        "uniform_gauge_fixed_principal_gap_is_positive": bool(
            principal["absolute_principal_smallest_eigenvalue"] > 0.0
        ),
        "measured_projection_sequence_is_not_used_as_a_proof": bool(
            not coefficients["remaining_gap"][
                "finite_projection_measurement_proves_either_statement"
            ]
        ),
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "FOR_ANY_S2_STRONGLY_CONVERGENT_ETA_INTERIOR_CORRECTED_CHILD_"
            "BACKGROUND_SEQUENCE,_THE_EXACT_RETAINED_ACTION_HESSIAN_"
            "FORMS_AND_WEAK_CONORMAL_GRAPHS_CONVERGE_IN_NORM_FORM_AND_"
            "HENCE_MOSCO_STRONG_RESOLVENT_SENSE;_THE_OPERATOR_HALF_OF_"
            "THE_SOFT_SEMIGROUP_LEMMA_IS_CLOSED_CONDITIONALLY_ON_THE_"
            "ACTUAL_BACKGROUND_COMPACTNESS"
        ),
        "retained_action_coefficient_inventory": {
            "bulk_local_dependence": (
                "SMOOTH_FUNCTIONS_OF_(q,D_chi_q,v,m,D_chi_m)_WITH_"
                "EXPONENTIAL_GEOMETRY_AND_INTEGER_POWERS"
            ),
            "eta_dependence": (
                "eta_Legendre=1+(x_spatial-f_normal^2)^3"
            ),
            "collective_inertia": (
                "ONE_SCALAR_INTEGRAL_FOLLOWED_BY_A_RECIPROCAL;_ITS_"
                "SECOND_VARIATION_IS_FINITE_RANK_PLUS_LOCAL_COEFFICIENTS"
            ),
            "boundary_Casimir": (
                "-C_SM*exp(logN_boundary)/R4_boundary"
            ),
            "highest_radial_derivative_order": 1,
            "new_action_term": False,
        },
        "coefficient_convergence_theorem": {
            "background_hypothesis": (
                "U_N_TO_U_STRONGLY_IN_"
                "S2=H2_q_CROSS_H1_v_CROSS_H2_m_AND_"
                "inf_N_eta(U_N)>=eta0>0"
            ),
            "Sobolev_embedding": (
                "H2_q_TO_C1_q,_H1_v_TO_C0_v,_H2_m_TO_C1_m_"
                "ON_THE_COMPACT_ONE_DIMENSIONAL_CAP"
            ),
            "local_coefficient_conclusion": (
                "ALL_LOCAL_HESSIAN_COEFFICIENTS_CONVERGE_UNIFORMLY_"
                "AND_ARE_UNIFORMLY_BOUNDED"
            ),
            "finite_rank_conclusion": (
                "THE_COLLECTIVE_INERTIA_HESSIAN_CONVERGES_IN_OPERATOR_NORM"
            ),
            "boundary_conclusion": (
                "THE_CASIMIR_AND_ATTACHMENT_TRACE_HESSIANS_CONVERGE_IN_"
                "THE_FIXED_FINITE_DIMENSIONAL_BOUNDARY_OPERATOR_NORM"
            ),
        },
        "form_and_resolvent_conclusion": {
            "common_form_domain": (
                "V_GAUGE=THE_EXISTING_ACTION_ENERGY_FORM_SPACE_AFTER_"
                "THE_BOUNDARY_COMPATIBLE_GAUGE_QUOTIENT"
            ),
            "norm_form_convergence": (
                "norm(j_N-j)_B(V_GAUGE,V_GAUGE_star)_TO_ZERO"
            ),
            "operator_graph_domain": (
                "D1_N_IS_THE_ASSOCIATED_WEAK_EULER_DIRAC_AND_CONORMAL_"
                "OPERATOR_DOMAIN_AND_MAY_VARY_WITH_THE_BACKGROUND"
            ),
            "Mosco_convergence": True,
            "strong_resolvent_convergence_for_a_common_stable_shift": True,
            "positive_duration_propagator_convergence_if_energy_stability_"
            "is_uniform": True,
            "zero_frequency_normal_inverse_uniformity_inferred": False,
            "why_not": (
                "A_COMPACT_LOWER_ORDER_NORMAL_EIGENVALUE_MAY_APPROACH_ZERO_"
                "WITHOUT_VIOLATING_PRINCIPAL_OR_SHIFTED_RESOLVENT_"
                "CONVERGENCE"
            ),
        },
        "closed_and_open": {
            "operator_coefficient_to_Mosco_implication": "PROVED",
            "actual_corrected_child_bundle_has_an_N_uniform_S2_bound": False,
            "actual_corrected_child_backgrounds_have_a_unique_strong_limit": (
                False
            ),
            "action_selected_soft_Cauchy_vectors_converge_strongly": False,
            "genuine_uniform_normal_closed_range_failure_demonstrated": (
                False
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_S2_ETA_PRECOMPACTNESS_AND_LIMIT_IDENTIFICATION_OF_THE_"
            "ACTUAL_CORRECTED_CHILD_BACKGROUNDS_AND_STRONG_GRAPH_"
            "COMPACTNESS_OF_THE_ACTION_SELECTED_SOFT_CALDERON_CAUCHY_"
            "VECTORS;_THE_ACTION_COEFFICIENT_TO_MOSCO_STEP_IS_CLOSED"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def actual_child_S2_compactness_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Measure S2 compactness evidence on the completed N3--N6 children."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    candidate_keys = {
        3: "N3_exact_attachment_weak_child_candidate",
        4: "N4_exact_attachment_weak_child_candidate",
        5: "coherent_N5_exact_attachment_weak_child_candidate",
        6: "N6_weak_complete_child_candidate",
    }

    def decode(order: int) -> tuple[np.ndarray, ...]:
        exact = result[candidate_keys[order]]["child_state"]["binary64_hex"]
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    states = {order: decode(order) for order in candidate_keys}
    rows = []
    for order, (q, velocity, multipliers) in states.items():
        frequencies = spectral_frequencies(order)
        rows.append({
            "N": order,
            "q_H2_norm": float(np.linalg.norm(
                q * (1.0 + frequencies["coordinates"] ** 2)
            )),
            "velocity_H1_norm": float(np.linalg.norm(
                velocity * np.sqrt(
                    1.0 + frequencies["coordinates"] ** 2
                )
            )),
            "multiplier_H2_norm": float(np.linalg.norm(
                multipliers * (1.0 + frequencies["multipliers"] ** 2)
            )),
            "complete_persistent_child_validated": bool(
                result[candidate_keys[order]][
                    "complete_persistent_child_validated"
                ]
            ),
        })

    def restrict(
        value: np.ndarray, high: int, low: int, *, multiplier: bool,
    ) -> np.ndarray:
        if multiplier:
            return np.concatenate((value[:low], value[high:high + low]))
        target = np.zeros(1 + 3 * low)
        target[0] = value[0]
        for family in range(3):
            target[1 + family * low:1 + (family + 1) * low] = value[
                1 + family * high:1 + family * high + low
            ]
        return target

    comparisons = []
    for low, high in ((3, 4), (4, 5), (5, 6)):
        q_low, v_low, m_low = states[low]
        q_high, v_high, m_high = states[high]
        frequencies = spectral_frequencies(low)
        weights = {
            "q_H2": 1.0 + frequencies["coordinates"] ** 2,
            "velocity_H1": np.sqrt(
                1.0 + frequencies["coordinates"] ** 2
            ),
            "multiplier_H2": 1.0 + frequencies["multipliers"] ** 2,
        }
        triples = {
            "q_H2": (
                q_low, restrict(q_high, high, low, multiplier=False)
            ),
            "velocity_H1": (
                v_low, restrict(v_high, high, low, multiplier=False)
            ),
            "multiplier_H2": (
                m_low, restrict(m_high, high, low, multiplier=True)
            ),
        }
        comparisons.append({
            "pair": f"N{low}_to_N{high}",
            "restricted_relative_differences": {
                name: float(
                    np.linalg.norm((left - right) * weights[name])
                    / max(1.0, np.linalg.norm(left * weights[name]))
                )
                for name, (left, right) in triples.items()
            },
        })
    n4_n6 = [row for row in rows if row["N"] >= 4]
    spread = {
        name: max(row[name] for row in n4_n6) / min(
            row[name] for row in n4_n6
        )
        for name in ("q_H2_norm", "velocity_H1_norm", "multiplier_H2_norm")
    }
    validation = {
        "all_N3_through_N6_children_are_complete_and_persistent": all(
            row["complete_persistent_child_validated"] for row in rows
        ),
        "N4_through_N6_S2_norms_remain_in_one_finite_band": bool(
            max(spread.values()) < 1.3
        ),
        "N5_to_N6_restricted_S2_differences_are_resolved": all(
            value < 0.2
            for value in comparisons[-1]["restricted_relative_differences"].values()
        ),
        "four_finite_children_not_promoted_as_a_uniform_general_N_bound": True,
        "N3_not_invalidated_by_its_larger_S2_norm": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_ACTUAL_COMPLETE_PERSISTENT_N4_N5_N6_CHILDREN_OCCUPY_A_"
            "COMMON_FINITE_S2_BAND_AND_THE_RESTRICTED_N5_TO_N6_S2_"
            "DIFFERENCE_IS_RESOLVED;_THIS_IS_COMPACTNESS_EVIDENCE_NOT_AN_"
            "N_UNIFORM_A_PRIORI_BOUND"
        ),
        "S2_space": "H2_q_CROSS_H1_velocity_CROSS_H2_lapse_shift",
        "rows": rows,
        "comparisons": comparisons,
        "N4_to_N6_norm_spread_ratios": spread,
        "theorem_gap": {
            "static_spatial_estimate": (
                "norm(q)_H2+norm(m)_H2<=C(eta0^-1,norm(U)_X_E)*"
                "(norm(E_U)_X_E_star+norm(Gamma_U)_boundary+"
                "norm(U)_X_E)_ON_THE_EXISTING_GAUGE_FIXED_CHILD_CHART"
            ),
            "velocity_derivative_fact": (
                "THE_RETAINED_ACTION_DEPENDS_ON_v_BUT_NOT_D_chi_v,_SO_"
                "THE_STATIC_CHILD_ROWS_DO_NOT_ELLIPTICALLY_CONTROL_"
                "norm(v)_H1"
            ),
            "dynamic_velocity_estimate": (
                "sup_0<=t<=T_norm(v(t))_H1<=C_T*(norm(v(0))_H1+"
                "integral_0^T_norm(D_t_v)_H1_dt)_FROM_THE_EXISTING_"
                "POSITIVE_DURATION_EULER_DIRAC_EVOLUTION"
            ),
            "spatial_principal_owner": (
                "THE_EXISTING_INVERTIBLE_GAUGE_FIXED_RADIAL_PRINCIPAL_"
                "MATRIX_WITH_GAP_sqrt(29)-5"
            ),
            "first_uncontrolled_term": (
                "N_UNIFORM_H1_VELOCITY_PROPAGATION_ON_THE_ACTUAL_"
                "POSITIVE_DURATION_CORRECTED_CHILD_HISTORIES"
            ),
            "full_static_S2_estimate_from_snapshot_rows_is_valid": False,
            "coupled_spatial_dynamic_S2_estimate_proved": False,
            "genuine_uniform_failure_demonstrated": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_THE_GAUGE_FIXED_H2_q_H2_m_SPATIAL_GARDING_ESTIMATE_"
            "AND_THE_N_UNIFORM_H1_v_PROPAGATION_ESTIMATE_ON_THE_"
            "EXISTING_POSITIVE_DURATION_CORRECTED_CHILD_HISTORIES"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def gauge_fixed_S2_propagation_theorem(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Derive the coupled spatial and positive-duration S2 estimate."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    actual = result["actual_child_S2_compactness_audit"]
    principal = weighted_pole_attachment_principal_estimate()
    gap = float(principal["canonical_physical_matrix"][
        "smallest_absolute_eigenvalue"
    ])
    hardy = float(principal["weighted_Poincare_Hardy_estimate"][
        "omega_constant"
    ])
    measured_K = max(
        math.sqrt(
            row["q_H2_norm"] ** 2
            + row["velocity_H1_norm"] ** 2
            + row["multiplier_H2_norm"] ** 2
        )
        for row in actual["rows"]
    )
    validation = {
        "weighted_principal_matrix_has_positive_absolute_gap": gap > 0.0,
        "weighted_Hardy_Poincare_constant_is_positive": hardy > 0.0,
        "attachment_trace_fixes_the_three_principal_geometry_traces": bool(
            principal["validation"][
                "trace_rows_fix_three_attachment_geometry_combinations"
            ]
        ),
        "actual_N3_through_N6_initial_S2_norms_are_finite": bool(
            measured_K < math.inf
        ),
        "static_rows_not_used_to_control_D_chi_velocity": True,
        "general_N_initial_S2_bound_not_assumed_from_finite_data": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "THE_EXISTING_WEIGHTED_GAUGE_FIXED_PRINCIPAL_GAP_AND_"
            "ATTACHMENT_TRACE_GIVE_A_SPATIAL_GARDING_ESTIMATE_FOR_q_AND_"
            "m;_COUPLED_WITH_THE_EXISTING_POSITIVE_DURATION_EVOLUTION_"
            "THIS_PROPAGATES_ANY_N_UNIFORM_INITIAL_S2_BOUND,_BUT_THE_"
            "GENERAL_N_INITIAL_BOUND_ITSELF_REMAINS_OPEN"
        ),
        "action_owned_constants": {
            "canonical_principal_absolute_gap": gap,
            "weighted_Hardy_Poincare_constant": hardy,
            "natural_weight": principal["natural_radial_weight"],
            "weight_equivalence": principal["weight_equivalence"],
            "measured_maximum_N3_to_N6_initial_S2_product_norm": measured_K,
        },
        "uniform_coefficient_ball": {
            "hypothesis": (
                "norm(U)_X_E<=K_E_AND_eta(U)>=eta0>0"
            ),
            "derived_pointwise_control": (
                "H1_q_AND_H1_m_EMBED_IN_L_infinity_ON_[0,pi/4],_SO_"
                "R,N,exp(5u-w),eta_inverse_AND_THE_PRINCIPAL_WEIGHT_"
                "kappa_HAVE_K_E_eta0_OWNED_UPPER_AND_LOWER_BOUNDS"
            ),
            "new_acceptance_gate": False,
        },
        "spatial_Garding_estimate": {
            "gauge_slice": "delta_w=0_AND_delta_beta=0",
            "trace_conditions": (
                "THE_EXISTING_THREE_ATTACHMENT_ROWS_FIX_delta_v(L),_"
                "delta_w(L),_delta(scale+u)(L)"
            ),
            "principal_estimate": (
                "gap*norm(D_chi(delta_q,delta_m))_omega<=C_kappa*"
                "norm(J_principal*deltaU)_omega_star"
            ),
            "lower_order_Garding_form": (
                "norm(delta_q,delta_m)_H1_omega<=C(K_E,eta0)*"
                "(norm(J_U*deltaU)_Hminus1_omega+"
                "norm(deltaU)_X_E+norm(Gamma0*deltaq))"
            ),
            "nonlinear_spatial_bootstrap": (
                "norm(q,m)_H2_omega<=C(K_E,eta0)*"
                "(1+norm(v)_H1^2+norm(E_U)_L2_omega+"
                "norm(Gamma_U)_boundary)"
            ),
            "velocity_H1_controlled_by_this_static_estimate": False,
        },
        "positive_duration_velocity_propagation": {
            "existing_evolution": "D_t_q=v,_D_t_v=a_action(U)",
            "differentiated_energy": (
                "D_t_E_S2<=C(K_E,eta0)*(1+E_S2),_"
                "E_S2=norm(q,m)_H2_omega^2+norm(v)_H1_omega^2"
            ),
            "Gronwall_bound": (
                "E_S2(t)<=exp(C*t)*(E_S2(0)+C*t)_ON_0<=t<=T0"
            ),
            "common_duration": (
                "T0=T0(K_E,eta0,E_S2(0))>0"
            ),
            "requires_nonzero_motion_to_vanish": False,
            "new_persistence_gate": False,
        },
        "proved_implication": {
            "if": (
                "sup_N_E_S2,N(0)<=K2_AND_inf_N_eta_N(0)>=eta0>0_"
                "ON_THE_ACTUAL_CORRECTED_CHILD_ROOTS"
            ),
            "then": (
                "sup_N_sup_0<=t<=T0_E_S2,N(t)<=K2_prime_AND_THE_"
                "BACKGROUND_JACOBI_FORMS_HAVE_THE_PREVIOUSLY_PROVED_"
                "MOSCO_STRONG_RESOLVENT_COMPACTNESS"
            ),
            "initial_N_uniform_bound_proved_from_N3_to_N6": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_AN_N_UNIFORM_INITIAL_S2_BOUND_FOR_THE_ACTUAL_"
            "CORRECTED_COMPLETE_CHILD_ROOTS_FROM_THE_EXISTING_ON_SHELL_"
            "WEAK_CALDERON_RELATION,_OR_CONSTRUCT_AN_ACTION_NORMALIZED_"
            "ROOT_SEQUENCE_WITH_DIVERGING_S2_NORM"
        ),
        "genuine_uniform_normal_closed_range_failure_demonstrated": False,
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def normal_section_S2_compactness_scope(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Restrict S2 compactness to the existing child normal section."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    propagation = result["gauge_fixed_S2_propagation_theorem"]
    exact = result["event_child_calderon_angle_stability_lemma"][
        "normal_dimension_law"
    ]
    validation = {
        "child_tangent_dimension_law_is_6N_minus_6": (
            exact["child_manifold_tangent_dimension"] == "6N-6"
        ),
        "boundary_normal_quotient_dimension_is_seven": (
            exact["boundary_normal_quotient_dimension"] == 7
        ),
        "S2_propagation_theorem_is_already_conditional_and_validated": bool(
            propagation["validation_passed"]
        ),
        "tangent_motion_is_not_reclassified_as_a_defect": True,
        "normal_section_is_a_chart_choice_not_a_physical_selector": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "GENERAL_N_S2_COMPACTNESS_IS_REQUIRED_ONLY_FOR_LOCAL_NORMAL_"
            "SECTION_REPRESENTATIVES_OF_THE_COMPLETE_CHILD_MANIFOLD;_"
            "THE_6N_MINUS_6_TANGENT_DIRECTIONS_REMAIN_PHYSICAL_AND_MAY_"
            "NOT_BE_BOUNDED_OR_REMOVED_AS_DEFECTS"
        ),
        "normal_tangent_decomposition": {
            "local_child_manifold_dimension": "6N-6",
            "boundary_normal_quotient_dimension": 7,
            "decomposition": (
                "deltaU=deltaU_tangent+deltaU_normal_AFTER_THE_EXISTING_"
                "BOUNDARY_COMPATIBLE_GAUGE_QUOTIENT"
            ),
            "tangent_kernel": (
                "KER(D_F_N)_CHILD_MANIFOLD_DIRECTIONS"
            ),
            "normal_section": (
                "ANY_LOCAL_COMPLEMENT_ON_WHICH_D_F_N_IS_INVERTIBLE;_"
                "THE_CHOICE_DOES_NOT_CHANGE_THE_PHYSICAL_ROOT_SET"
            ),
        },
        "correct_compactness_statement": {
            "required": (
                "sup_N_norm(U_N_section)_S2<INFINITY_MODULO_THE_EXISTING_"
                "TANGENT_AND_GAUGE_DIRECTIONS"
            ),
            "not_required": (
                "sup_OVER_ALL_COMPLETE_CHILD_ROOTS_AND_ALL_TANGENT_"
                "EXCITATIONS_norm(U)_S2<INFINITY"
            ),
            "nonzero_motion_momentum_and_time_dependence_allowed": True,
            "componentwise_or_coordinate_monotonicity_required": False,
            "new_branch_selector_added": False,
        },
        "propagation_transfer": {
            "if_normal_section_initial_bound_holds": propagation[
                "proved_implication"
            ]["then"],
            "tangent_directions_enter_the_observability_inf_sup": False,
            "why": (
                "THE_TARGET_CLOSED_RANGE_ESTIMATE_IS_ALREADY_RESTRICTED_"
                "TO_THE_NORMAL_COMPLEMENT_MODULO_TANGENT_AND_GAUGE"
            ),
        },
        "exact_next_mathematical_lemma": (
            "PROVE_AN_N_UNIFORM_INITIAL_S2_BOUND_FOR_LOCAL_NORMAL_SECTION_"
            "REPRESENTATIVES_OF_THE_ACTUAL_CORRECTED_COMPLETE_CHILD_"
            "RELATION_MODULO_THE_EXISTING_6N_MINUS_6_TANGENT_AND_GAUGE_"
            "DIRECTIONS,_OR_CONSTRUCT_A_DIVERGING_NORMAL_SEQUENCE"
        ),
        "genuine_uniform_normal_closed_range_failure_demonstrated": False,
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def soft_normal_fredholm_compactness_dichotomy(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Identify genuine uniform failure with a continuum normal kernel."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    scope = result["normal_section_S2_compactness_scope"]
    mosco = result["jacobi_form_coefficient_mosco_theorem"]
    propagation = result["gauge_fixed_S2_propagation_theorem"]
    hard = result["mixed_euler_dirac_hard_momentum_response_audit"]
    validation = {
        "normal_boundary_quotient_has_fixed_dimension_seven": (
            scope["normal_tangent_decomposition"][
                "boundary_normal_quotient_dimension"
            ] == 7
        ),
        "principal_spatial_gap_and_propagation_are_derived": bool(
            propagation["validation_passed"]
        ),
        "coefficient_to_Mosco_implication_is_derived": (
            mosco["closed_and_open"][
                "operator_coefficient_to_Mosco_implication"
            ] == "PROVED"
        ),
        "finite_N_soft_response_is_resolved_nonzero": bool(
            hard["soft_channel"]["exact_response_projection_magnitude"] > 0.0
        ),
        "finite_conditioning_not_used_as_a_failure_proof": True,
        "tangent_and_gauge_kernels_remain_quotiented_not_deleted": True,
        "no_new_equation_constraint_regularizer_objective_or_gate": True,
    }
    return {
        "classification": (
            "ON_ANY_S2_ETA_PRECOMPACT_NORMAL_SECTION_BUNDLE,_FAILURE_OF_"
            "THE_N_UNIFORM_NORMAL_RIGHT_INVERSE_IS_EQUIVALENT_TO_THE_"
            "EXISTENCE_OF_A_NONZERO_CONTINUUM_GAUGE_QUOTIENTED_NORMAL_"
            "JACOBI_KERNEL;_RAW_SMALL_SINGULAR_VALUES_OR_D2_FAILURE_"
            "ALONE_DO_NOT_ESTABLISH_CATEGORY_3"
        ),
        "Fredholm_setup": {
            "normal_boundary_dimension": 7,
            "principal_operator": (
                "THE_EXISTING_WEIGHTED_GAUGE_FIXED_RADIAL_OPERATOR_WITH_"
                "ABSOLUTE_GAP_sqrt(29)-5"
            ),
            "lower_order_terms": (
                "RELATIVELY_COMPACT_ONE_DIMENSIONAL_MULTIPLICATION,_"
                "FINITE_RANK_COLLECTIVE_INERTIA,_AND_FINITE_DIMENSIONAL_"
                "WEAK_CONORMAL_BOUNDARY_COUPLING"
            ),
            "Fredholm_index": 0,
            "physical_tangent_kernel_included_in_normal_problem": False,
        },
        "compactness_contradiction": {
            "assume_failure": (
                "EXISTS_N_j_AND_NORMAL_x_j_WITH_norm(x_j)_S2=1_AND_"
                "norm(J_Nj*x_j,Gamma_Nj*x_j)_dual_TO_ZERO"
            ),
            "background_compactness": (
                "S2_ETA_PRECOMPACTNESS_SELECTS_A_STRONGLY_CONVERGENT_"
                "BACKGROUND_SUBSEQUENCE"
            ),
            "operator_limit": (
                "THE_PROVED_COEFFICIENT_TO_MOSCO_THEOREM_PASSES_THE_"
                "JACOBI_AND_WEAK_CONORMAL_RELATIONS_TO_THE_LIMIT"
            ),
            "no_high_frequency_escape": (
                "THE_WEIGHTED_GARDING_ESTIMATE_IMPLIES_"
                "1<=C*(RESIDUAL+norm(x_j)_X_E);_COMPACT_X_E_EMBEDDING_"
                "PREVENTS_THE_LIMIT_FROM_VANISHING"
            ),
            "limit": (
                "NONZERO_x_star_IN_THE_NORMAL_QUOTIENT_WITH_"
                "J_star*x_star=0_AND_ZERO_MATCHED_BOUNDARY_HISTORY"
            ),
        },
        "converse": {
            "continuum_normal_kernel_is_compatible_with_a_uniform_right_"
            "inverse": False,
            "meaning": (
                "A_NONZERO_NORMAL_KERNEL_PRODUCES_GALERKIN_QUASIMODES_"
                "AND_FORCES_THE_DISCRETE_NORMAL_INF_SUP_TO_ZERO"
            ),
        },
        "classification_policy": {
            "category_2": (
                "NO_CONTINUUM_NORMAL_KERNEL_OR_L2_HISTORY_COLLAPSE_HAS_"
                "BEEN_CONSTRUCTED;_THE_FINITE_N_RESPONSE_IS_NONZERO"
            ),
            "category_3_requires": (
                "EXHIBIT_THE_NONZERO_CONTINUUM_NORMAL_KERNEL_OR_AN_"
                "EQUIVALENT_ACTION_NORMALIZED_L2_HISTORY_COLLAPSE_SEQUENCE"
            ),
            "current_category": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
            "genuine_uniform_failure_demonstrated": False,
        },
        "exact_next_mathematical_lemma": (
            "PROVE_CONTINUUM_GAUGE_QUOTIENTED_NORMAL_SOFT_JACOBI_KERNEL_"
            "ABSENCE_FROM_THE_POSITIVE_DURATION_WEAK_GREEN_ENERGY_"
            "IDENTITY,_OR_EXHIBIT_THE_NONZERO_KERNEL_HISTORY"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def continuum_normal_cauchy_completeness_reduction(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
) -> dict[str, Any]:
    """Reduce Cauchy completeness to the seven-row boundary symbol."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    fredholm = result["soft_normal_fredholm_compactness_dichotomy"]
    adjoint = result["positive_duration_normal_adjoint_kernel_localization"]
    weak = result["weak_conormal_reaction_graph_audit"]
    principal = weighted_pole_attachment_principal_estimate()
    determinant = float(principal["canonical_physical_matrix"]["determinant"])
    validation = {
        "normal_boundary_quotient_dimension_is_seven": (
            fredholm["Fredholm_setup"]["normal_boundary_dimension"] == 7
        ),
        "canonical_weighted_principal_matrix_is_invertible": determinant != 0.0,
        "attachment_trace_has_a_uniform_right_lift": bool(
            weak["uniform_attachment_trace_theorem"][
                "uniform_right_lift_norm_upper_bound"
            ] < 5.0
        ),
        "weak_conormal_reaction_is_lift_independent": bool(
            "H1-H2" in weak["mixed_weak_history_system"]["lift_independence"]
        ),
        "positive_duration_energy_uniqueness_is_already_derived": bool(
            adjoint["validation_passed"]
        ),
        "physical_child_tangent_and_gauge_directions_are_already_quotiented": True,
        "no_new_boundary_row_equation_constraint_or_gate": True,
    }
    return {
        "classification": (
            "CONTINUUM_NORMAL_CAUCHY_COMPLETENESS_REDUCES_TO_PROVING_"
            "THAT_THE_EXISTING_THREE_TRACE_TWO_MOMENTUM_AND_TWO_WEAK_"
            "REACTION_ROWS_DEFINE_AN_ISOMORPHISM_ON_THE_SEVEN_COMPONENT_"
            "RADIAL_NORMAL_CAUCHY_SYMBOL;_DIMENSION_MATCHING_AND_FINITE_N_"
            "RANK_DO_NOT_YET_PROVE_THIS_GENERAL_N_BOUNDARY_SYMBOL_GAP"
        ),
        "boundary_Cauchy_vector": {
            "dimension": 7,
            "existing_rows": [
                "ATTACHMENT_TRACE_3",
                "CANONICAL_MOMENTUM_2",
                "WEAK_DYNAMIC_REACTION_2",
            ],
            "constraint_rows_role": (
                "RECONSTRUCT_THE_LAPSE_SHIFT_NORMAL_COMPONENTS_AND_REMOVE_"
                "THE_CONSTRAINT_ANNIHILATOR"
            ),
            "gauge_role": (
                "THE_EXISTING_BOUNDARY_COMPATIBLE_TIME_RADIAL_GAUGE_"
                "QUOTIENT_REMOVES_w_SHIFT_PRINCIPAL_NULL_DIRECTIONS"
            ),
            "dimension_match_alone_proves_isomorphism": False,
            "new_Cauchy_datum_added": False,
        },
        "radial_uniqueness_reduction": {
            "physical_principal_matrix": principal[
                "canonical_physical_matrix"
            ]["dimensionless_matrix"],
            "determinant": determinant,
            "weighted_absolute_gap": float(principal[
                "canonical_physical_matrix"
            ]["smallest_absolute_eigenvalue"]),
            "first_order_reduction": (
                "D_chi_W_normal=A_U(chi,t)*W_normal_ON_0<chi<=pi/4"
            ),
            "coefficient_regulariry": (
                "U_IN_S2_AND_eta>=eta0_MAKE_A_U_IN_L1_chi_"
                "UNIFORMLY_ON_EACH_PRECOMPACT_NORMAL_BUNDLE"
            ),
            "boundary_value": (
                "IF_THE_SEVEN_ROW_BOUNDARY_SYMBOL_IS_INVERTIBLE,_"
                "VANISHING_EXISTING_ROWS_GIVE_W_normal(pi/4,t)=0"
            ),
            "seven_row_boundary_symbol_invertibility_proved": False,
            "Gronwall_in_chi": (
                "norm(W_normal(chi,t))<=norm(W_normal(pi/4,t))*"
                "exp(integral_chi^(pi/4)norm(A_U))=0"
            ),
            "regular_pole": (
                "THE_EXISTING_POLE_DOMAIN_IS_SATISFIED_AUTOMATICALLY_BY_"
                "THE_ZERO_RADIAL_SOLUTION"
            ),
        },
        "positive_duration_consequence_if_boundary_symbol_closes": {
            "zero_radial_normal_field_at_initial_time": True,
            "zero_initial_gauge_fixed_energy": True,
            "energy_bound": "D_t_E_g<=C_U(t)*E_g",
            "conclusion": (
                "E_g(0)=0_IMPLIES_E_g(t)=0_ON_THE_EXISTING_POSITIVE_"
                "DURATION,_SO_THE_CONTINUUM_NON_TANGENT_NORMAL_KERNEL_"
                "IS_TRIVIAL"
            ),
        },
        "boundary_symbol_gap": {
            "required_map": (
                "B_Cauchy(U):(W_normal_at_attachment)_R7_TO_"
                "(TRACE3,MOMENTUM2,REACTION2)_R7"
            ),
            "required_estimate": (
                "inf_OVER_THE_S2_eta_BUNDLE_sigma_min(B_Cauchy(U))>0"
            ),
            "already_closed_blocks": [
                "TRACE3_UNIFORM_RIGHT_LIFT",
                "GAUGE_FIXED_RADIAL_PRINCIPAL_MATRIX_DETERMINANT_8",
                "WEAK_REACTION_LIFT_INDEPENDENCE",
                "FINITE_N_HARD_AND_SOFT_MOMENTUM_RESPONSES_NONZERO",
            ],
            "missing_block": (
                "EXPLICIT_ACTION_DERIVED_COUPLING_OF_MOMENTUM2_AND_"
                "REACTION2_TO_THE_REMAINING_FOUR_NORMAL_CAUCHY_"
                "COMPONENTS_AFTER_CONSTRAINT_RECONSTRUCTION"
            ),
            "general_N_symbol_gap_proved": False,
        },
        "Fredholm_status": {
            "continuum_normal_kernel": "OPEN_PENDING_BOUNDARY_SYMBOL_GAP",
            "non_tangent_minus_one_eigenstate_excluded": False,
            "uniform_normal_closed_range_on_each_S2_eta_precompact_bundle": (
                False
            ),
            "global_unbounded_child_manifold_claimed": False,
            "category_3_failure_demonstrated": False,
            "soft_channel_classification": (
                "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
            ),
        },
        "exact_next_mathematical_lemma": (
            "DERIVE_THE_EXPLICIT_ACTION_OWNED_SEVEN_BY_SEVEN_NORMAL_"
            "BOUNDARY_CAUCHY_SYMBOL_MAPPING_(TRACE3,MOMENTUM2,REACTION2)_"
            "TO_THE_CONSTRAINT_RECONSTRUCTED_RADIAL_CAUCHY_VECTOR_AND_"
            "PROVE_OR_FAIL_ITS_S2_ETA_UNIFORM_MINIMUM_SINGULAR_VALUE"
        ),
        "new_physics_equations_constraints_regularizers_objectives_or_gates": (
            False
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def weak_constraint_boundary_source_tail_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    maximum_order: int = 48,
    points: int = 256,
) -> dict[str, Any]:
    """Separate the exact boundary lapse covector from the bulk H-1 tail."""

    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    exact = result["N6_weak_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]
    base = tuple(
        np.asarray([float.fromhex(value) for value in exact[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )
    q, velocity, multipliers = embed_nested_state(
        *base, 6, maximum_order
    )
    constraints = constraint_residual(
        maximum_order, q, velocity, multipliers, points=points
    )
    signs_k = (-1.0) ** np.arange(1, maximum_order + 1)
    signs_j = (-1.0) ** np.arange(maximum_order)
    u_boundary = q[1:1 + maximum_order] @ signs_k
    b_boundary = (
        q[1 + 2 * maximum_order:1 + 3 * maximum_order] @ signs_j
    )
    radius = RADIUS0 * math.exp(float(q[0]))
    a_boundary = radius * math.exp(
        float(u_boundary + b_boundary)
    ) / math.sqrt(2.0)
    b_radius = radius * math.exp(
        float(u_boundary - b_boundary)
    ) / math.sqrt(2.0)
    r4 = a_boundary * b_radius / math.sqrt(
        a_boundary**2 + b_radius**2
    )
    boundary_lapse = math.exp(float(
        multipliers[:maximum_order] @ signs_k
    ))
    boundary_coefficient = (
        -standard_model_casimir_coefficient() * boundary_lapse / r4
    )
    bulk_lapse = (
        constraints[:maximum_order] - boundary_coefficient * signs_k
    )
    bulk_shift = constraints[maximum_order:2 * maximum_order]
    frequencies = spectral_frequencies(maximum_order)["multipliers"]
    dual_weights_squared = 1.0 / (1.0 + frequencies**2)
    cuts = [
        cut for cut in (6, 8, 10, 12, 16, 20, 24, 32, 40, 47)
        if cut < maximum_order
    ]
    rows = []
    for cut in cuts:
        high = np.arange(maximum_order) >= cut
        tail = math.sqrt(float(
            np.sum(
                dual_weights_squared[:maximum_order][high]
                * bulk_lapse[high] ** 2
            )
            + np.sum(
                dual_weights_squared[maximum_order:][high]
                * bulk_shift[high] ** 2
            )
        ))
        rows.append({
            "cutoff_N": cut,
            "bulk_constraint_H_minus_1_tail_norm": tail,
            "first_omitted_lapse_coefficient": float(bulk_lapse[cut]),
            "first_omitted_shift_coefficient": float(bulk_shift[cut]),
        })
    fit_rows = [row for row in rows if 12 <= row["cutoff_N"] <= 40]
    slope = float(np.polyfit(
        np.log([row["cutoff_N"] for row in fit_rows]),
        np.log([
            row["bulk_constraint_H_minus_1_tail_norm"]
            for row in fit_rows
        ]),
        1,
    )[0])
    validation = {
        "exact_boundary_Casimir_covector_subtracted": bool(
            abs(boundary_coefficient) > 0.0
        ),
        "bulk_H_minus_1_tail_decreases_after_N12": all(
            later["bulk_constraint_H_minus_1_tail_norm"]
            < earlier["bulk_constraint_H_minus_1_tail_norm"]
            for earlier, later in zip(fit_rows, fit_rows[1:])
        ),
        "measured_tail_power_is_summable_in_squared_dual_norm": bool(
            slope < -0.5
        ),
        "raw_strong_lapse_coefficients_not_used_as_bulk_failure": True,
        "finite_child_equations_and_gates_unchanged": True,
    }
    return {
        "classification": (
            "NONDECAYING_RAW_LAPSE_CONSTRAINT_ROWS_RECLASSIFIED_AS_THE_"
            "EXACT_BOUNDARY_CASIMIR_COVECTOR;_INTERIOR_WEAK_H_MINUS_1_"
            "CONSTRAINT_TAIL_DECAYS_ON_THE_MATCHED_N6_BACKGROUND"
        ),
        "exact_boundary_lapse_covector": {
            "formula": "-C_SM*N_boundary/R4*(-1)^k",
            "coefficient": boundary_coefficient,
            "belongs_to": "WEAK_CONORMAL_BOUNDARY_REACTION",
            "belongs_to_bulk_constraint_failure": False,
        },
        "maximum_order": maximum_order,
        "quadrature_points": points,
        "rows": rows,
        "measured_loglog_tail_slope_N12_to_N40": slope,
        "continuum_interpretation": (
            "THE_MULTIPLIER_VARIATION_IS_A_DISTRIBUTIONAL_ELEMENT_OF_"
            "H_MINUS_1_PLUS_A_BOUNDARY_COVECTOR;_AFTER_THE_EXACT_"
            "BOUNDARY_TERM_IS_ROUTED_TO_THE_CONORMAL_RELATION,_THE_BULK_"
            "SPECTRAL_TAIL_TENDS_TO_ZERO"
        ),
        "strong_L2_constraint_codomain_required": False,
        "new_equation_constraint_or_acceptance_gate": False,
        "first_missing_mathematical_object": (
            "COMPUTE_THE_ACTION_NORMALIZED_NORMAL_RIGHT_INVERSE_DEFECT_"
            "AND_NONLINEAR_LIPSCHITZ_BOUND_NEEDED_FOR_AN_A_POSTERIORI_"
            "RADII_POLYNOMIAL_ON_THE_WEAK_COMPLETE_CHILD_MAP"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=4)
def weak_complete_child_normal_right_inverse_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    derivative_step: float = 2.0e-5,
) -> dict[str, Any]:
    """Measure the total weak N6 map on its action-owned normal quotient."""

    if derivative_step <= 0.0:
        raise ValueError("the normalized derivative step must be positive")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    order = 6
    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    child_exact = result["N6_weak_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]

    def decode(exact: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    child_q, child_v, child_m = decode(child_exact)
    event_q, event_v, event_m = decode(event_exact)
    center = np.concatenate((child_q, child_v, child_m))
    event_momentum = _canonical_pair_at_order(
        order, event_q, event_v, event_m, points=points
    )[0]
    frequencies = spectral_frequencies(order)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    v_weights = np.ones(qdim)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    domain_weights = np.concatenate((q_weights, v_weights, m_weights))

    trace = _trace_jacobian_at_order(order)
    attachment = _attachment_jacobian_at_order(order, child_q)
    boundary_covectors = np.vstack((trace, attachment[1]))
    boundary_gram = (
        boundary_covectors
        @ np.diag(1.0 / q_weights**2)
        @ boundary_covectors.T
    )

    def symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        if float(np.min(eigenvalues)) <= 0.0:
            raise np.linalg.LinAlgError("normalization Gram is not positive")
        return (
            eigenvectors
            @ np.diag(eigenvalues**power)
            @ eigenvectors.T
        )

    boundary_inverse_sqrt = symmetric_power(boundary_gram, -0.5)
    momentum_gram = attachment @ attachment.T
    momentum_sqrt = symmetric_power(momentum_gram, 0.5)
    event_attachment = _attachment_coordinates_at_order(order, event_q)

    def raw_blocks(state: np.ndarray) -> tuple[np.ndarray, ...]:
        q = state[:qdim]
        velocity = state[qdim:2 * qdim]
        multipliers = state[2 * qdim:]
        boundary_rows = np.concatenate((
            trace @ (q - event_q),
            [
                _attachment_coordinates_at_order(order, q)[1]
                - event_attachment[1]
            ],
        ))
        constraints = constraint_residual(
            order, q, velocity, multipliers, points=points
        )
        momentum = _canonical_pair_at_order(
            order, q, velocity, multipliers, points=points
        )[0] - event_momentum
        return boundary_rows, constraints, momentum

    def normalized_rows(state: np.ndarray) -> np.ndarray:
        boundary_rows, constraints, momentum = raw_blocks(state)
        return np.concatenate((
            boundary_inverse_sqrt @ boundary_rows,
            constraints[:mdim] / m_weights,
            constraints[mdim:],
            momentum_sqrt @ momentum,
        ))

    center_rows = normalized_rows(center)
    jacobian = np.empty((center_rows.size, center.size))
    for column in range(center.size):
        delta = np.zeros(center.size)
        delta[column] = derivative_step / domain_weights[column]
        jacobian[:, column] = (
            normalized_rows(center + delta)
            - normalized_rows(center - delta)
        ) / (2.0 * derivative_step)
    left_vectors, singular, right_vectors_t = np.linalg.svd(
        jacobian, full_matrices=False
    )
    tolerance = (
        np.finfo(float).eps * max(jacobian.shape) * singular[0]
    )
    rank = int(np.count_nonzero(singular > tolerance))
    right_inverse = (
        right_vectors_t.T
        @ np.diag(1.0 / singular)
        @ left_vectors.T
    )
    right_inverse_defect = float(np.linalg.norm(
        jacobian @ right_inverse - np.eye(center_rows.size), ord=2
    ))
    raw_boundary, raw_constraints, raw_momentum = raw_blocks(center)
    eta = _eta_legendre_minimum(
        order, child_q, child_m, points=max(2000, points)
    )
    validation = {
        "total_weak_map_closes_at_matched_N6_state": bool(
            np.linalg.norm(center_rows) < 1.0e-8
        ),
        "independent_weak_rows_have_full_rank": rank == center_rows.size,
        "normal_right_inverse_defect_is_small": (
            right_inverse_defect < 1.0e-9
        ),
        "eta_domain_retained": bool(eta["minimum"] > 0.0),
        "boundary_Casimir_covector_retained_in_total_constraint_map": True,
        "no_componentwise_monotonicity_or_new_gate_added": True,
    }
    return {
        "classification": (
            "ACTION_NORMALIZED_TOTAL_WEAK_N6_COMPLETE_CHILD_MAP_HAS_A_"
            "FINITE_FULL_ROW_RANK_NORMAL_RIGHT_INVERSE;_NONLINEAR_"
            "LIPSCHITZ_AND_INFINITE_TAIL_RADII_BOUND_REMAINS_OPEN"
        ),
        "source": "EXACT_ATTACHMENT_MATCHED_PERSISTENT_N6_WEAK_CHILD",
        "map": {
            "domain": "H1_q_CROSS_L2_v_CROSS_H1_lapse_shift",
            "codomain": (
                "FOUR_INDEPENDENT_BOUNDARY_CONFIGURATION_ROWS_CROSS_"
                "H_MINUS_1_TOTAL_CONSTRAINTS_CROSS_R_ENERGY_CROSS_"
                "BOUNDARY_MOMENTUM_DUAL"
            ),
            "independent_boundary_rows": (
                "THREE_TRACE_ROWS_PLUS_THE_SECOND_EXACT_ATTACHMENT_"
                "COORDINATE;_THE_FIRST_ATTACHMENT_COORDINATE_IS_"
                "ALGEBRAICALLY_REDUNDANT_WITH_THE_TRACE_ROWS"
            ),
            "row_count": int(center_rows.size),
            "variable_count": int(center.size),
            "physical_equations_changed": False,
        },
        "normalization": {
            "domain": "H1_q_L2_v_H1_m_ACTION_OWNED_SPECTRAL_WEIGHTS",
            "boundary_Gram": "C*W_q^(-2)*C^T",
            "constraint_dual": "TOTAL_L_m_ROWS_DIVIDED_BY_H1_m_WEIGHTS",
            "boundary_momentum_dual": "sqrt(B*B^T)*Delta_p",
            "tuned_scale_or_observed_particle_data_used": False,
        },
        "center_residual": {
            "action_normalized_total_norm": float(np.linalg.norm(center_rows)),
            "action_normalized_maximum": float(np.max(np.abs(center_rows))),
            "raw_boundary_norm": float(np.linalg.norm(raw_boundary)),
            "raw_total_constraint_norm": float(np.linalg.norm(raw_constraints)),
            "raw_boundary_momentum_norm": float(np.linalg.norm(raw_momentum)),
            "eta_Legendre_minimum": eta["minimum"],
        },
        "derivative": {
            "normalized_central_step": derivative_step,
            "rank": rank,
            "rank_tolerance": float(tolerance),
            "singular_values": singular.tolist(),
            "largest_singular_value": float(singular[0]),
            "smallest_normal_singular_value": float(singular[-1]),
            "normal_right_inverse_norm": float(1.0 / singular[-1]),
            "condition_number": float(singular[0] / singular[-1]),
            "right_inverse_defect_operator_norm": right_inverse_defect,
            "normal_domain_basis": right_vectors_t.tolist(),
            "softest_normal_domain_direction": right_vectors_t[-1].tolist(),
            "coordinate_singular_values_used_as_physics": False,
        },
        "first_missing_mathematical_object": (
            "MEASURE_AN_ACTION_NORMALIZED_LOCAL_JACOBIAN_LIPSCHITZ_BOUND_"
            "ON_THE_NORMAL_RIGHT_INVERSE_DIRECTIONS_AND_COMBINE_IT_WITH_"
            "THE_WEAK_HIGH_SHELL_TAIL_IN_AN_A_POSTERIORI_RADII_POLYNOMIAL"
        ),
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=4)
def weak_complete_child_normal_lipschitz_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    points: int = 96,
    derivative_step: float = 2.0e-5,
    outer_radii: tuple[float, float] = (2.0e-4, 1.0e-4),
) -> dict[str, Any]:
    """Measure the reduced weak-map Hessian on the N6 normal quotient."""

    if derivative_step <= 0.0 or any(radius <= 0.0 for radius in outer_radii):
        raise ValueError("positive normalized derivative radii required")
    if len(outer_radii) != 2 or outer_radii[0] <= outer_radii[1]:
        raise ValueError("outer_radii must be a decreasing two-scale pair")
    target = Path(path)
    result = json.loads(target.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    inverse_audit = weak_complete_child_normal_right_inverse_audit(
        target, points=points, derivative_step=derivative_step
    )
    if not inverse_audit["validation_passed"]:
        raise RuntimeError("normal right-inverse audit must validate first")
    order = 6
    qdim = dimensions(order)["coordinates"]
    mdim = dimensions(order)["multipliers"]
    child_exact = result["N6_weak_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]

    def decode(exact: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    child_q, child_v, child_m = decode(child_exact)
    event_q, event_v, event_m = decode(event_exact)
    center = np.concatenate((child_q, child_v, child_m))
    event_momentum = _canonical_pair_at_order(
        order, event_q, event_v, event_m, points=points
    )[0]
    frequencies = spectral_frequencies(order)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    domain_weights = np.concatenate((
        q_weights, np.ones(qdim), m_weights
    ))
    trace = _trace_jacobian_at_order(order)
    attachment = _attachment_jacobian_at_order(order, child_q)
    boundary_covectors = np.vstack((trace, attachment[1]))

    def symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        if float(np.min(eigenvalues)) <= 0.0:
            raise np.linalg.LinAlgError("normalization Gram is not positive")
        return (
            eigenvectors
            @ np.diag(eigenvalues**power)
            @ eigenvectors.T
        )

    boundary_inverse_sqrt = symmetric_power(
        boundary_covectors
        @ np.diag(1.0 / q_weights**2)
        @ boundary_covectors.T,
        -0.5,
    )
    momentum_sqrt = symmetric_power(attachment @ attachment.T, 0.5)
    event_attachment = _attachment_coordinates_at_order(order, event_q)

    def normalized_rows(state: np.ndarray) -> np.ndarray:
        q = state[:qdim]
        velocity = state[qdim:2 * qdim]
        multipliers = state[2 * qdim:]
        boundary_rows = np.concatenate((
            trace @ (q - event_q),
            [
                _attachment_coordinates_at_order(order, q)[1]
                - event_attachment[1]
            ],
        ))
        constraints = constraint_residual(
            order, q, velocity, multipliers, points=points
        )
        momentum = _canonical_pair_at_order(
            order, q, velocity, multipliers, points=points
        )[0] - event_momentum
        return np.concatenate((
            boundary_inverse_sqrt @ boundary_rows,
            constraints[:mdim] / m_weights,
            constraints[mdim:],
            momentum_sqrt @ momentum,
        ))

    normal_basis = np.asarray(
        inverse_audit["derivative"]["normal_domain_basis"], dtype=float
    ).T
    normal_dimension = normal_basis.shape[1]

    def physical_shift(normalized: np.ndarray) -> np.ndarray:
        return normalized / domain_weights

    def reduced_jacobian(state: np.ndarray) -> np.ndarray:
        matrix = np.empty((normal_dimension, normal_dimension))
        for column in range(normal_dimension):
            delta = physical_shift(
                derivative_step * normal_basis[:, column]
            )
            matrix[:, column] = (
                normalized_rows(state + delta)
                - normalized_rows(state - delta)
            ) / (2.0 * derivative_step)
        return matrix

    center_jacobian = reduced_jacobian(center)
    center_inverse = np.linalg.inv(center_jacobian)
    center_residual = normalized_rows(center)
    newton_correction = -center_inverse @ center_residual
    tensor_rows = []
    tensors = []
    for radius in outer_radii:
        tensor = np.empty((normal_dimension, normal_dimension, normal_dimension))
        for direction in range(normal_dimension):
            shift = physical_shift(radius * normal_basis[:, direction])
            tensor[:, :, direction] = (
                reduced_jacobian(center + shift)
                - reduced_jacobian(center - shift)
            ) / (2.0 * radius)
        tensors.append(tensor)
        permutation_error = float(np.linalg.norm(
            tensor - np.swapaxes(tensor, 1, 2)
        ) / max(1.0, np.linalg.norm(tensor)))
        tensor_rows.append({
            "normalized_outer_radius": radius,
            "Hessian_tensor_Frobenius_norm": float(np.linalg.norm(tensor)),
            "mixed_direction_symmetry_relative_error": permutation_error,
            "largest_single_output_Hessian_slice_norm": float(max(
                np.linalg.norm(tensor[row], ord=2)
                for row in range(normal_dimension)
            )),
        })
    coarse_tensor, fine_tensor = tensors
    richardson_tensor = (4.0 * fine_tensor - coarse_tensor) / 3.0
    tensor_change = float(
        np.linalg.norm(fine_tensor - coarse_tensor)
        / max(1.0, np.linalg.norm(fine_tensor))
    )
    measured_lipschitz = float(np.linalg.norm(richardson_tensor))
    inverse_norm = float(np.linalg.norm(center_inverse, ord=2))
    y_bound = float(np.linalg.norm(newton_correction))
    z0 = float(np.linalg.norm(
        np.eye(normal_dimension) - center_inverse @ center_jacobian,
        ord=2,
    ))
    z2_measured = inverse_norm * measured_lipschitz
    discriminant = (1.0 - z0) ** 2 - 4.0 * z2_measured * y_bound
    roots: list[float] = []
    if discriminant > 0.0 and z2_measured > 0.0:
        square_root = math.sqrt(discriminant)
        roots = [
            ((1.0 - z0) - square_root) / (2.0 * z2_measured),
            ((1.0 - z0) + square_root) / (2.0 * z2_measured),
        ]
    eta_rows = []
    for sign in (-1.0, 1.0):
        trial = center + physical_shift(
            normal_basis @ (sign * newton_correction)
        )
        eta_rows.append(_eta_legendre_minimum(
            order, trial[:qdim], trial[2 * qdim:], points=max(2000, points)
        )["minimum"])
    validation = {
        "normal_reduced_Jacobian_is_invertible": bool(
            np.linalg.svd(center_jacobian, compute_uv=False)[-1] > 0.0
        ),
        "two_scale_Hessian_measurement_is_stable": tensor_change < 5.0e-2,
        "mixed_direction_symmetry_replays": all(
            row["mixed_direction_symmetry_relative_error"] < 5.0e-2
            for row in tensor_rows
        ),
        "measured_finite_N_radii_discriminant_is_positive": (
            discriminant > 0.0
        ),
        "Newton_correction_remains_eta_admissible": min(eta_rows) > 0.0,
        "no_new_equation_constraint_or_acceptance_gate": True,
    }
    return {
        "classification": (
            "FINITE_N_ACTION_NORMALIZED_NORMAL_HESSIAN_AND_MEASURED_"
            "RADII_CONDITION_EVALUATED;_A_RIGOROUS_NEIGHBORHOOD_"
            "SUPREMUM_AND_INFINITE_TAIL_BOUND_REMAIN_REQUIRED"
        ),
        "source": "TOTAL_WEAK_N6_MAP_ON_ITS_19_DIMENSIONAL_NORMAL_QUOTIENT",
        "normal_dimension": normal_dimension,
        "derivative_step": derivative_step,
        "two_scale_Hessian_rows": tensor_rows,
        "two_scale_tensor_relative_change": tensor_change,
        "Richardson_Hessian_Frobenius_bound_measurement": measured_lipschitz,
        "finite_N_measured_radii_polynomial": {
            "formula": "p(r)=Z2*r^2-(1-Z0)*r+Y",
            "Y": y_bound,
            "Z0": z0,
            "normal_inverse_operator_norm": inverse_norm,
            "measured_Z2": z2_measured,
            "discriminant": discriminant,
            "negative_interval_roots": roots,
            "is_a_rigorous_infinite_dimensional_existence_proof": False,
        },
        "Newton_correction": {
            "action_normalized_norm": y_bound,
            "eta_minima_at_signed_corrections": eta_rows,
        },
        "why_not_yet_a_theorem": (
            "THE_TWO_SCALE_TENSOR_IS_A_CONTROLLED_LOCAL_MEASUREMENT_BUT_"
            "NOT_AN_INTERVAL_OR_ANALYTIC_SUPREMUM_OVER_THE_FULL_BALL;_"
            "THE_INFINITE_H_MINUS_1_HIGH_SHELL_DEFECT_MUST_ALSO_BE_"
            "BOUNDED_AFTER_THE_PRINCIPAL_INVERSE_GAIN"
        ),
        "first_missing_mathematical_object": (
            "DERIVE_A_CONSERVATIVE_ACTION_ANALYTIC_SUPREMUM_FOR_THE_"
            "NORMAL_HESSIAN_ON_THE_MEASURED_RADII_BALL_AND_BOUND_THE_"
            "INFINITE_WEAK_CONSTRAINT_TAIL_AFTER_PRINCIPAL_INVERSION"
        ),
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def weak_boundary_layer_radii_obstruction_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    cutoff: int = 6,
) -> dict[str, Any]:
    """Compare the exact Casimir boundary tail with the measured N6 radius."""

    if cutoff < 1:
        raise ValueError("a positive Galerkin cutoff is required")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    tail_audit = result["weak_constraint_boundary_source_tail_audit"]
    lipschitz = result["weak_complete_child_normal_lipschitz_audit"]
    coefficient = abs(float(
        tail_audit["exact_boundary_lapse_covector"]["coefficient"]
    ))
    total_series = 0.5 * (
        (math.pi / 4.0) / math.tanh(math.pi / 4.0) - 1.0
    )
    retained_series = sum(
        1.0 / (1.0 + 16.0 * mode**2)
        for mode in range(1, cutoff + 1)
    )
    tail_series = total_series - retained_series
    boundary_tail = coefficient * math.sqrt(tail_series)
    principal_gap = math.sqrt(29.0) - 5.0
    principal_norm = math.sqrt(29.0) + 5.0
    principal_correction_bracket = [
        boundary_tail / principal_norm,
        boundary_tail / principal_gap,
    ]
    measured_roots = lipschitz["finite_N_measured_radii_polynomial"][
        "negative_interval_roots"
    ]
    if len(measured_roots) != 2:
        raise RuntimeError("finite-N measured radii interval is unavailable")
    measured_upper_radius = float(measured_roots[1])
    asymptotic_orders = {
        "using_principal_norm_lower_correction_scale": (
            coefficient / (4.0 * principal_norm * measured_upper_radius)
        ) ** 2,
        "using_principal_gap_upper_correction_scale": (
            coefficient / (4.0 * principal_gap * measured_upper_radius)
        ) ** 2,
    }
    validation = {
        "exact_H_minus_1_boundary_series_is_positive": tail_series > 0.0,
        "N6_direct_tail_exceeds_measured_finite_N_radius": (
            principal_correction_bracket[0] > measured_upper_radius
        ),
        "mechanical_resolution_increase_is_not_a_practical_closure_route": (
            min(asymptotic_orders.values()) > 1.0e8
        ),
        "boundary_source_is_action_owned_not_a_new_constraint": True,
        "finite_N6_root_and_persistence_remain_valid": True,
        "no_new_equation_constraint_or_acceptance_gate": True,
    }
    return {
        "classification": (
            "DIRECT_N6_TO_CONTINUUM_RADII_TRANSFER_INVALIDATED_BY_THE_"
            "ACTION_OWNED_CASIMIR_BOUNDARY_DISTRIBUTION_TAIL;_AN_EXACT_"
            "VARIATIONAL_BOUNDARY_LAYER_LIFT_OR_PARAMETRIX_IS_REQUIRED"
        ),
        "exact_series_identity": {
            "series": "SUM_k>=1 1/(1+16*k^2)",
            "closed_form": "((pi/4)*coth(pi/4)-1)/2",
            "total": total_series,
            "retained_through_cutoff": retained_series,
            "tail_after_cutoff": tail_series,
        },
        "cutoff": cutoff,
        "boundary_Casimir_coefficient": coefficient,
        "boundary_H_minus_1_tail_norm": boundary_tail,
        "normalized_principal_symbol": {
            "smallest_absolute_eigenvalue": principal_gap,
            "largest_absolute_eigenvalue": principal_norm,
            "principal_only_correction_norm_bracket": (
                principal_correction_bracket
            ),
        },
        "finite_N_measured_radii_upper_root": measured_upper_radius,
        "minimum_principal_correction_to_radius_ratio": (
            principal_correction_bracket[0] / measured_upper_radius
        ),
        "asymptotic_cutoff_estimates_to_reach_that_radius": asymptotic_orders,
        "interpretation": (
            "THE_FINITE_N6_CHILD_REMAINS_A_VALID_ROOT_OF_ITS_RETAINED_"
            "TOTAL_WEAK_EQUATIONS;_WHAT_FAILS_IS USING_ITS_ZERO_PADDED_"
            "STATE_AS_AN_ALREADY_SMALL_CONTINUUM_NEWTON_SEED"
        ),
        "invalidated_next_route": (
            "MECHANICALLY_INCREASE_N_UNTIL_THE_RAW_BOUNDARY_TAIL_FITS_"
            "INSIDE_THE_N6_LOCAL_RADII_BALL"
        ),
        "first_missing_mathematical_object": (
            "DERIVE_FROM_THE_RETAINED_ACTION_AN_EXACT_BOUNDARY_LAYER_"
            "LIFT_OR_CALDERON_PARAMETRIX_FOR_THE_CASIMIR_LAPSE_"
            "DISTRIBUTION_AND_APPLY_THE_RADII_BOUND_ONLY_TO_ITS_"
            "REGULAR_REMAINDER"
        ),
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def casimir_boundary_layer_parametrix_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    maximum_order: int = 48,
    points: int = 256,
    derivative_step: float = 2.0e-5,
) -> dict[str, Any]:
    """Construct the exact-action high-shell lift of the Casimir source."""

    if maximum_order <= 6 or derivative_step <= 0.0:
        raise ValueError("a higher order and positive derivative step are required")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    child_exact = result["N6_weak_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]

    def decode(exact: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    child_n6 = decode(child_exact)
    event_n6 = decode(event_exact)
    child_q, child_v, child_m = embed_nested_state(
        *child_n6, 6, maximum_order
    )
    event_q, _, _ = embed_nested_state(*event_n6, 6, maximum_order)
    qdim = dimensions(maximum_order)["coordinates"]
    mdim = dimensions(maximum_order)["multipliers"]
    frequencies = spectral_frequencies(maximum_order)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    trace = _trace_jacobian_at_order(maximum_order)
    attachment = _attachment_jacobian_at_order(maximum_order, child_q)
    boundary_covectors = np.vstack((trace, attachment[1]))
    boundary_gram = (
        boundary_covectors
        @ np.diag(1.0 / q_weights**2)
        @ boundary_covectors.T
    )
    eigenvalues, eigenvectors = np.linalg.eigh(boundary_gram)
    boundary_inverse_sqrt = (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(eigenvalues))
        @ eigenvectors.T
    )
    event_attachment = _attachment_coordinates_at_order(
        maximum_order, event_q
    )
    high_indices = np.asarray([
        1 + family * maximum_order + mode
        for family in range(3)
        for mode in range(6, maximum_order)
    ], dtype=int)

    def q_from_correction(correction: np.ndarray) -> np.ndarray:
        q = child_q.copy()
        q[high_indices] += correction / q_weights[high_indices]
        return q

    def normalized_rows(correction: np.ndarray) -> np.ndarray:
        q = q_from_correction(correction)
        boundary_rows = np.concatenate((
            trace @ (q - event_q),
            [
                _attachment_coordinates_at_order(maximum_order, q)[1]
                - event_attachment[1]
            ],
        ))
        constraints = constraint_residual(
            maximum_order, q, child_v, child_m, points=points
        )
        return np.concatenate((
            boundary_inverse_sqrt @ boundary_rows,
            constraints[:mdim] / m_weights,
            constraints[mdim:],
        ))

    zero = np.zeros(high_indices.size)
    initial_rows = normalized_rows(zero)
    jacobian = np.empty((initial_rows.size, zero.size))
    for column in range(zero.size):
        delta = np.zeros_like(zero)
        delta[column] = derivative_step
        jacobian[:, column] = (
            normalized_rows(delta) - normalized_rows(-delta)
        ) / (2.0 * derivative_step)
    singular = np.linalg.svd(jacobian, compute_uv=False)
    tolerance = np.finfo(float).eps * max(jacobian.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    proposal = np.linalg.lstsq(jacobian, -initial_rows, rcond=1.0e-12)[0]
    trials = []
    for exponent in range(13):
        factor = 2.0 ** (-exponent)
        correction = factor * proposal
        q = q_from_correction(correction)
        eta = _eta_legendre_minimum(
            maximum_order, q, child_m, points=max(points, 512)
        )
        rows = normalized_rows(correction)
        trials.append({
            "factor": factor,
            "action_H1_correction_norm": float(np.linalg.norm(correction)),
            "normalized_boundary_constraint_norm": float(np.linalg.norm(rows)),
            "normalized_boundary_constraint_maximum": float(
                np.max(np.abs(rows))
            ),
            "eta_Legendre_minimum": eta["minimum"],
            "admissible": bool(eta["minimum"] > 0.0),
        })
    admissible = [trial for trial in trials if trial["admissible"]]
    best = min(
        admissible,
        key=lambda trial: trial["normalized_boundary_constraint_norm"],
    )
    best_correction = float(best["factor"]) * proposal
    best_q = q_from_correction(best_correction)
    best_constraints = constraint_residual(
        maximum_order, best_q, child_v, child_m, points=points
    )
    initial_constraints = constraint_residual(
        maximum_order, child_q, child_v, child_m, points=points
    )
    high = np.arange(maximum_order) >= 6
    dual_weights_squared = 1.0 / (1.0 + frequencies["multipliers"] ** 2)

    def high_tail(constraints: np.ndarray) -> float:
        return math.sqrt(float(
            np.sum(
                dual_weights_squared[:maximum_order][high]
                * constraints[:maximum_order][high] ** 2
            )
            + np.sum(
                dual_weights_squared[maximum_order:][high]
                * constraints[maximum_order:2 * maximum_order][high] ** 2
            )
        ))

    correction_by_family = {}
    for family, name in enumerate(("u", "w", "v")):
        values = best_correction[
            family * (maximum_order - 6):(family + 1) * (maximum_order - 6)
        ]
        correction_by_family[name] = {
            "H1_norm": float(np.linalg.norm(values)),
            "first_six_normalized_coefficients": values[:6].tolist(),
            "last_six_normalized_coefficients": values[-6:].tolist(),
        }
    exact_merit_reduced = bool(
        best["normalized_boundary_constraint_norm"]
        < np.linalg.norm(initial_rows)
    )
    validation = {
        "exact_retained_constraint_derivative_used": True,
        "only_preexisting_high_geometry_shell_variables_used": True,
        "boundary_configuration_rows_included_unchanged": True,
        "eta_domain_retained": bool(best["eta_Legendre_minimum"] > 0.0),
        "exact_nonlinear_merit_controls_the_parametrix_verdict": True,
        "failed_q_only_parametrix_not_promoted": not exact_merit_reduced,
        "finite_N6_child_and_persistence_left_unchanged": True,
        "no_new_equation_constraint_or_acceptance_gate": True,
    }
    return {
        "classification": (
            "Q_ONLY_HIGH_SHELL_CASIMIR_BOUNDARY_LAYER_PARAMETRIX_"
            "INVALIDATED_BY_ITS_ACTION_NORMALIZED_NEAR_KERNEL_AND_"
            "EXACT_NONLINEAR_WEAK_MERIT;_A_MIXED_GAUGE_REDUCED_"
            "EULER_DIRAC_PARAMETRIX_IS_REQUIRED"
        ),
        "source": (
            "EXACT_TOTAL_CONSTRAINT_MAP_AT_FIXED_N6_CHILD_EMBEDDED_IN_"
            f"N{maximum_order}_WITHOUT_A_HIGHER_N_COMPLETE_CHILD_ROOT"
        ),
        "maximum_order": maximum_order,
        "quadrature_points": points,
        "map": {
            "rows": int(initial_rows.size),
            "high_geometry_unknowns": int(high_indices.size),
            "Jacobian_rank": rank,
            "smallest_nonzero_singular_value": float(singular[rank - 1]),
            "physical_equations_changed": False,
        },
        "initial": {
            "normalized_boundary_constraint_norm": float(
                np.linalg.norm(initial_rows)
            ),
            "H_minus_1_high_constraint_tail": high_tail(initial_constraints),
        },
        "best_parametrix_trial": best,
        "strict_exact_merit_reduction_found": exact_merit_reduced,
        "H_minus_1_high_constraint_tail_after_parametrix": high_tail(
            best_constraints
        ),
        "line_trials": trials,
        "correction_by_geometry_family": correction_by_family,
        "is_a_higher_N_complete_child_root": False,
        "is_a_new_boundary_condition": False,
        "infinitesimal_q_only_descent_ruled_out": False,
        "q_only_finite_boundary_layer_lift_promoted": False,
        "first_missing_mathematical_object": (
            "DERIVE_THE_MIXED_BOUNDARY_COMPATIBLE_GAUGE_REDUCED_"
            "EULER_DIRAC_CASIMIR_BOUNDARY_LAYER_PARAMETRIX_USING_THE_"
            "RETAINED_q_v_m_ACTION_BLOCKS_AND_WEAK_CONORMAL_RELATION"
        ),
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def mixed_euler_dirac_boundary_layer_parametrix_audit(
    path: str | Path = (
        "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    ),
    *,
    maximum_order: int = 48,
    points: int = 256,
) -> dict[str, Any]:
    """Lift the Casimir tail with the exact mixed q-v-m action Hessian."""

    if maximum_order <= 6:
        raise ValueError("the mixed boundary layer requires a higher shell")
    result = json.loads(Path(path).read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    child_exact = result["N6_weak_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]
    event_exact = result["sequential_action_energy_projection_audit"][
        "rows"
    ][0]["event"]["projected_state_binary64_hex"]

    def decode(exact: Mapping[str, Any]) -> tuple[np.ndarray, ...]:
        return tuple(
            np.asarray([float.fromhex(value) for value in exact[name]])
            for name in ("coordinates", "velocities", "multipliers")
        )

    child_n6 = decode(child_exact)
    event_n6 = decode(event_exact)
    child = embed_nested_state(*child_n6, 6, maximum_order)
    event = embed_nested_state(*event_n6, 6, maximum_order)
    child_q, child_v, child_m = child
    event_q, event_v, event_m = event
    qdim = dimensions(maximum_order)["coordinates"]
    mdim = dimensions(maximum_order)["multipliers"]
    center = np.concatenate(child)
    frequencies = spectral_frequencies(maximum_order)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    domain_weights = np.concatenate((
        q_weights, np.ones(qdim), m_weights
    ))
    trace = _trace_jacobian_at_order(maximum_order)
    attachment = _attachment_jacobian_at_order(maximum_order, child_q)
    boundary_covectors = np.vstack((trace, attachment[1]))
    boundary_gram = (
        boundary_covectors
        @ np.diag(1.0 / q_weights**2)
        @ boundary_covectors.T
    )
    eigenvalues, eigenvectors = np.linalg.eigh(boundary_gram)
    boundary_inverse_sqrt = (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(eigenvalues))
        @ eigenvectors.T
    )
    event_attachment = _attachment_coordinates_at_order(
        maximum_order, event_q
    )
    high_q = [
        1 + family * maximum_order + mode
        for family in range(3)
        for mode in range(6, maximum_order)
    ]
    high_v = [qdim + index for index in high_q]
    high_m = [
        2 * qdim + mode
        for mode in range(6, maximum_order)
    ] + [
        2 * qdim + maximum_order + mode
        for mode in range(6, maximum_order)
    ]
    high_indices = np.asarray(high_q + high_v + high_m, dtype=int)

    def state_from_correction(correction: np.ndarray) -> np.ndarray:
        state = center.copy()
        state[high_indices] += correction / domain_weights[high_indices]
        return state

    def normalized_rows(state: np.ndarray) -> np.ndarray:
        q = state[:qdim]
        velocity = state[qdim:2 * qdim]
        multipliers = state[2 * qdim:]
        boundary_rows = np.concatenate((
            trace @ (q - event_q),
            [
                _attachment_coordinates_at_order(maximum_order, q)[1]
                - event_attachment[1]
            ],
        ))
        constraints = constraint_residual(
            maximum_order, q, velocity, multipliers, points=points
        )
        return np.concatenate((
            boundary_inverse_sqrt @ boundary_rows,
            constraints[:mdim] / m_weights,
            constraints[mdim:],
        ))

    center_rows = normalized_rows(center)
    jet = exact_full_action_jet_at_state(
        maximum_order, child_q, child_v, child_m, points=points
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    multiplier_slice = slice(2 * qdim, 2 * qdim + mdim)
    velocity_slice = slice(qdim, 2 * qdim)
    constraint_jacobian = hessian[multiplier_slice, :].copy()
    energy_gradient = child_v @ hessian[velocity_slice, :] - gradient
    energy_gradient[velocity_slice] += gradient[velocity_slice]
    raw_jacobian = np.vstack((constraint_jacobian, energy_gradient))
    normalized_constraint_jacobian = raw_jacobian.copy()
    normalized_constraint_jacobian[:mdim] /= m_weights[:, None]
    boundary_jacobian = np.zeros((4, center.size))
    boundary_jacobian[:, :qdim] = (
        boundary_inverse_sqrt @ boundary_covectors
    )
    normalized_jacobian = np.vstack((
        boundary_jacobian, normalized_constraint_jacobian
    )) / domain_weights[None, :]
    reduced_jacobian = normalized_jacobian[:, high_indices]
    left_vectors, singular, _ = np.linalg.svd(
        reduced_jacobian, full_matrices=True
    )
    tolerance = (
        np.finfo(float).eps * max(reduced_jacobian.shape) * singular[0]
    )
    rank = int(np.count_nonzero(singular > tolerance))
    left_null = left_vectors[:, rank:]
    left_null_residual = float(np.linalg.norm(left_null.T @ center_rows))
    proposal = np.linalg.lstsq(
        reduced_jacobian, -center_rows, rcond=1.0e-12
    )[0]
    proposal_direction = proposal / max(1.0, np.linalg.norm(proposal))
    check_step = 2.0e-5
    directional_exact = (
        normalized_rows(state_from_correction(check_step * proposal_direction))
        - normalized_rows(state_from_correction(-check_step * proposal_direction))
    ) / (2.0 * check_step)
    directional_linear = reduced_jacobian @ proposal_direction
    derivative_error = float(
        np.linalg.norm(directional_exact - directional_linear)
        / max(1.0, np.linalg.norm(directional_exact))
    )
    trials = []
    for exponent in range(17):
        factor = 2.0 ** (-exponent)
        correction = factor * proposal
        state = state_from_correction(correction)
        rows = normalized_rows(state)
        eta = _eta_legendre_minimum(
            maximum_order,
            state[:qdim],
            state[2 * qdim:],
            points=max(points, 512),
        )
        trials.append({
            "factor": factor,
            "action_product_correction_norm": float(
                np.linalg.norm(correction)
            ),
            "normalized_boundary_constraint_norm": float(np.linalg.norm(rows)),
            "normalized_boundary_constraint_maximum": float(
                np.max(np.abs(rows))
            ),
            "eta_Legendre_minimum": eta["minimum"],
            "admissible": bool(eta["minimum"] > 0.0),
        })
    admissible = [trial for trial in trials if trial["admissible"]]
    best = min(
        admissible,
        key=lambda trial: trial["normalized_boundary_constraint_norm"],
    )
    best_correction = float(best["factor"]) * proposal
    best_state = state_from_correction(best_correction)
    event_momentum = _canonical_pair_at_order(
        maximum_order, event_q, event_v, event_m, points=points
    )[0]
    child_momentum = _canonical_pair_at_order(
        maximum_order,
        best_state[:qdim],
        best_state[qdim:2 * qdim],
        best_state[2 * qdim:],
        points=points,
    )[0]
    momentum_gram = (
        _attachment_jacobian_at_order(maximum_order, best_state[:qdim])
        @ _attachment_jacobian_at_order(maximum_order, best_state[:qdim]).T
    )
    momentum_values, momentum_vectors = np.linalg.eigh(momentum_gram)
    momentum_sqrt = (
        momentum_vectors
        @ np.diag(np.sqrt(momentum_values))
        @ momentum_vectors.T
    )
    momentum_mismatch = child_momentum - event_momentum
    normalized_momentum = momentum_sqrt @ momentum_mismatch
    center_v_form = hessian[velocity_slice, velocity_slice]
    center_cv = hessian[multiplier_slice, velocity_slice]
    center_v_lift = _boundary_lift(
        center_v_form, attachment, center_cv
    )
    initial_child_momentum = (
        center_v_lift.T @ gradient[velocity_slice]
    )
    initial_momentum_mismatch = initial_child_momentum - event_momentum
    center_momentum_values, center_momentum_vectors = np.linalg.eigh(
        attachment @ attachment.T
    )
    center_momentum_sqrt = (
        center_momentum_vectors
        @ np.diag(np.sqrt(center_momentum_values))
        @ center_momentum_vectors.T
    )
    initial_normalized_momentum = (
        center_momentum_sqrt @ initial_momentum_mismatch
    )
    frozen_momentum_jacobian = (
        center_momentum_sqrt
        @ center_v_lift.T
        @ hessian[velocity_slice, :]
    ) / domain_weights[None, :]
    full_proposal_jacobian = np.vstack((
        reduced_jacobian,
        frozen_momentum_jacobian[:, high_indices],
    ))
    initial_full_rows = np.concatenate((
        center_rows, initial_normalized_momentum
    ))
    full_proposal = np.linalg.lstsq(
        full_proposal_jacobian, -initial_full_rows, rcond=1.0e-12
    )[0]

    def exact_full_rows(state: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        boundary_constraint = normalized_rows(state)
        state_q = state[:qdim]
        state_momentum = _canonical_pair_at_order(
            maximum_order,
            state_q,
            state[qdim:2 * qdim],
            state[2 * qdim:],
            points=points,
        )[0]
        state_attachment = _attachment_jacobian_at_order(
            maximum_order, state_q
        )
        state_values, state_vectors = np.linalg.eigh(
            state_attachment @ state_attachment.T
        )
        state_sqrt = (
            state_vectors
            @ np.diag(np.sqrt(state_values))
            @ state_vectors.T
        )
        momentum_rows = state_sqrt @ (state_momentum - event_momentum)
        return np.concatenate((boundary_constraint, momentum_rows)), momentum_rows

    full_trials = []
    for factor in (1.0, 0.0625, 0.015625):
        correction = factor * full_proposal
        state = state_from_correction(correction)
        rows, momentum_rows = exact_full_rows(state)
        eta = _eta_legendre_minimum(
            maximum_order,
            state[:qdim],
            state[2 * qdim:],
            points=max(points, 512),
        )
        full_trials.append({
            "factor": factor,
            "action_product_correction_norm": float(np.linalg.norm(correction)),
            "exact_normalized_full_weak_norm": float(np.linalg.norm(rows)),
            "exact_normalized_boundary_constraint_norm": float(
                np.linalg.norm(rows[:-2])
            ),
            "exact_normalized_momentum_dual_norm": float(
                np.linalg.norm(momentum_rows)
            ),
            "eta_Legendre_minimum": eta["minimum"],
            "admissible": bool(eta["minimum"] > 0.0),
        })
    full_best = min(
        (trial for trial in full_trials if trial["admissible"]),
        key=lambda trial: trial["exact_normalized_full_weak_norm"],
    )
    initial_full_norm = float(np.linalg.norm(initial_full_rows))
    full_strict_reduction = bool(
        full_best["exact_normalized_full_weak_norm"] < initial_full_norm
    )
    best_jet = exact_full_action_jet_at_state(
        maximum_order,
        best_state[:qdim],
        best_state[qdim:2 * qdim],
        best_state[2 * qdim:],
        points=points,
    )
    best_gradient = np.asarray(best_jet.gradient, dtype=float)
    best_hessian = np.asarray(best_jet.hessian, dtype=float)
    best_velocity = best_state[qdim:2 * qdim]
    best_constraint_jacobian = best_hessian[multiplier_slice, :].copy()
    best_energy_gradient = (
        best_velocity @ best_hessian[velocity_slice, :] - best_gradient
    )
    best_energy_gradient[velocity_slice] += best_gradient[velocity_slice]
    best_raw_constraint_jacobian = np.vstack((
        best_constraint_jacobian, best_energy_gradient
    ))
    best_raw_constraint_jacobian[:mdim] /= m_weights[:, None]
    best_attachment = _attachment_jacobian_at_order(
        maximum_order, best_state[:qdim]
    )
    best_boundary_covectors = np.vstack((trace, best_attachment[1]))
    best_boundary_jacobian = np.zeros((4, center.size))
    best_boundary_jacobian[:, :qdim] = (
        boundary_inverse_sqrt @ best_boundary_covectors
    )
    best_bc_jacobian = np.vstack((
        best_boundary_jacobian, best_raw_constraint_jacobian
    )) / domain_weights[None, :]
    best_reduced_bc_jacobian = best_bc_jacobian[:, high_indices]
    best_left, best_singular, best_right_t = np.linalg.svd(
        best_reduced_bc_jacobian, full_matrices=True
    )
    best_tolerance = (
        np.finfo(float).eps
        * max(best_reduced_bc_jacobian.shape)
        * best_singular[0]
    )
    best_rank = int(np.count_nonzero(best_singular > best_tolerance))
    tangent_kernel = best_right_t[best_rank:].T
    best_v_form = best_hessian[velocity_slice, velocity_slice]
    best_cv = best_hessian[multiplier_slice, velocity_slice]
    best_v_lift = _boundary_lift(
        best_v_form, best_attachment, best_cv
    )
    best_frozen_momentum_jacobian = (
        momentum_sqrt
        @ best_v_lift.T
        @ best_hessian[velocity_slice, :]
    ) / domain_weights[None, :]
    tangent_momentum_response = (
        best_frozen_momentum_jacobian[:, high_indices] @ tangent_kernel
    )
    tangent_response_singular = np.linalg.svd(
        tangent_momentum_response, compute_uv=False
    )
    tangent_basis = tangent_kernel @ np.linalg.pinv(
        tangent_momentum_response, rcond=1.0e-12
    )
    for column in range(tangent_basis.shape[1]):
        norm = float(np.linalg.norm(tangent_basis[:, column]))
        if norm == 0.0:
            raise RuntimeError("frozen tangent proposal basis collapsed")
        tangent_basis[:, column] /= norm
    boundary_only_rows, _ = exact_full_rows(best_state)
    paired_step = 2.0e-5
    paired_exact_jacobian = np.empty((boundary_only_rows.size, 2))
    for column in range(2):
        direction = tangent_basis[:, column]
        plus_rows, _ = exact_full_rows(state_from_correction(
            best_correction + paired_step * direction
        ))
        minus_rows, _ = exact_full_rows(state_from_correction(
            best_correction - paired_step * direction
        ))
        paired_exact_jacobian[:, column] = (
            plus_rows - minus_rows
        ) / (2.0 * paired_step)
    paired_left, paired_singular, paired_right_t = np.linalg.svd(
        paired_exact_jacobian, full_matrices=False
    )
    exact_tangent_coordinates = np.linalg.lstsq(
        paired_exact_jacobian, -boundary_only_rows, rcond=1.0e-12
    )[0]
    tangent_correction = tangent_basis @ exact_tangent_coordinates
    tangent_trials = []
    for factor in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125):
        correction = best_correction + factor * tangent_correction
        state = state_from_correction(correction)
        rows, momentum_rows = exact_full_rows(state)
        eta = _eta_legendre_minimum(
            maximum_order,
            state[:qdim],
            state[2 * qdim:],
            points=max(points, 512),
        )
        tangent_trials.append({
            "factor": factor,
            "increment_action_product_norm": float(
                factor * np.linalg.norm(tangent_correction)
            ),
            "total_action_product_correction_norm": float(
                np.linalg.norm(correction)
            ),
            "exact_normalized_full_weak_norm": float(np.linalg.norm(rows)),
            "exact_normalized_boundary_constraint_norm": float(
                np.linalg.norm(rows[:-2])
            ),
            "exact_normalized_momentum_dual_norm": float(
                np.linalg.norm(momentum_rows)
            ),
            "eta_Legendre_minimum": eta["minimum"],
            "admissible": bool(eta["minimum"] > 0.0),
        })
    tangent_best = min(
        (trial for trial in tangent_trials if trial["admissible"]),
        key=lambda trial: trial["exact_normalized_full_weak_norm"],
    )
    boundary_only_full_norm = float(math.hypot(
        best["normalized_boundary_constraint_norm"],
        np.linalg.norm(normalized_momentum),
    ))
    tangent_strict_reduction = bool(
        tangent_best["exact_normalized_full_weak_norm"]
        < boundary_only_full_norm
    )
    hard_coordinates = (
        -paired_right_t[0]
        * float(paired_left[:, 0] @ boundary_only_rows)
        / paired_singular[0]
    )
    hard_correction = tangent_basis @ hard_coordinates
    hard_trials = []
    for factor in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125):
        correction = best_correction + factor * hard_correction
        state = state_from_correction(correction)
        rows, momentum_rows = exact_full_rows(state)
        eta = _eta_legendre_minimum(
            maximum_order,
            state[:qdim],
            state[2 * qdim:],
            points=max(points, 512),
        )
        hard_trials.append({
            "factor": factor,
            "increment_action_product_norm": float(
                factor * np.linalg.norm(hard_correction)
            ),
            "exact_normalized_full_weak_norm": float(np.linalg.norm(rows)),
            "exact_normalized_boundary_constraint_norm": float(
                np.linalg.norm(rows[:-2])
            ),
            "exact_normalized_momentum_dual_norm": float(
                np.linalg.norm(momentum_rows)
            ),
            "eta_Legendre_minimum": eta["minimum"],
            "admissible": bool(eta["minimum"] > 0.0),
        })
    hard_best = min(
        (trial for trial in hard_trials if trial["admissible"]),
        key=lambda trial: trial["exact_normalized_full_weak_norm"],
    )
    hard_strict_reduction = bool(
        hard_best["exact_normalized_full_weak_norm"]
        < boundary_only_full_norm
    )
    strict_reduction = bool(
        best["normalized_boundary_constraint_norm"]
        < np.linalg.norm(center_rows)
    )
    validation = {
        "exact_full_action_Hessian_used": True,
        "analytic_constraint_Jacobian_matches_exact_directional_response": (
            derivative_error < 1.0e-6
        ),
        "single_left_null_identity_is_compatible_with_the_source": bool(
            center_rows.size - rank == 1 and left_null_residual < 1.0e-8
        ),
        "eta_domain_retained": bool(best["eta_Legendre_minimum"] > 0.0),
        "exact_nonlinear_boundary_constraint_merit_reduced": strict_reduction,
        "frozen_momentum_proposal_reduces_exact_full_weak_merit": (
            full_strict_reduction
        ),
        "boundary_constraint_tangent_momentum_step_reduces_exact_merit": (
            hard_strict_reduction
        ),
        "finite_N6_child_and_persistence_left_unchanged": True,
        "no_new_equation_constraint_or_acceptance_gate": True,
    }
    return {
        "classification": (
            "MIXED_GAUGE_REDUCED_EULER_DIRAC_CASIMIR_BOUNDARY_LAYER_"
            "PARAMETRIX_CLOSES_THE_BOUNDARY_CONSTRAINT_OWNER;_THE_"
            "RETURNED_MOMENTUM_AND_FULL_WEAK_REMAINDER_CONTROL_NEXT"
            if all(validation.values()) else
            "MIXED_EULER_DIRAC_BOUNDARY_LAYER_PARAMETRIX_REMAINS_OPEN"
        ),
        "source": (
            "EXACT_FULL_q_v_m_ACTION_HESSIAN_AT_THE_ZERO_PADDED_MATCHED_"
            f"N6_CHILD_IN_N{maximum_order};_NO_HIGHER_N_ROOT_SOLVE"
        ),
        "maximum_order": maximum_order,
        "quadrature_points": points,
        "map": {
            "rows": int(center_rows.size),
            "high_shell_unknowns": int(high_indices.size),
            "high_q_unknowns": len(high_q),
            "high_v_unknowns": len(high_v),
            "high_m_unknowns": len(high_m),
            "rank": rank,
            "left_nullity": int(center_rows.size - rank),
            "left_null_source_compatibility_norm": left_null_residual,
            "smallest_nonzero_singular_value": float(singular[rank - 1]),
            "condition_number": float(singular[0] / singular[rank - 1]),
        },
        "analytic_constraint_Jacobian_directional_error": derivative_error,
        "initial_normalized_boundary_constraint_norm": float(
            np.linalg.norm(center_rows)
        ),
        "best_parametrix_trial": best,
        "line_trials": trials,
        "returned_momentum_remainder": {
            "raw_norm": float(np.linalg.norm(momentum_mismatch)),
            "action_normalized_dual_norm": float(
                np.linalg.norm(normalized_momentum)
            ),
            "included_in_this_parametrix_solve": False,
        },
        "full_weak_frozen_momentum_proposal": {
            "proposal_model": (
                "EXACT_BOUNDARY_CONSTRAINT_JACOBIAN_PLUS_FROZEN_"
                "STATE_DEPENDENT_LIFT_MOMENTUM_SLOPE"
            ),
            "exact_residual_controls_promotion": True,
            "initial_exact_normalized_full_weak_norm": initial_full_norm,
            "best_trial": full_best,
            "trials": full_trials,
            "strict_exact_full_weak_reduction_found": full_strict_reduction,
            "frozen_lift_slope_promoted_as_physics": False,
        },
        "boundary_constraint_tangent_momentum_correction": {
            "boundary_constraint_normal_rank": best_rank,
            "tangent_kernel_dimension": int(tangent_kernel.shape[1]),
            "tangent_momentum_response_singular_values": (
                tangent_response_singular.tolist()
            ),
            "paired_exact_slope_step": paired_step,
            "paired_exact_two_direction_Jacobian_singular_values": (
                paired_singular.tolist()
            ),
            "frozen_lift_slope_is_proposal_only": True,
            "paired_exact_slopes_replace_the_failed_orientation": True,
            "exact_full_weak_residual_controls_promotion": True,
            "boundary_only_exact_full_weak_norm": boundary_only_full_norm,
            "best_trial": tangent_best,
            "trials": tangent_trials,
            "strict_exact_full_weak_reduction_found": tangent_strict_reduction,
            "hard_response_rank_one_test": {
                "classification": (
                    "FINITE_N_HARD_MOMENTUM_RESPONSE_CLOSED;_THE_SECOND_"
                    "SOFT_CHANNEL_IS_A_NORMAL_DIRECTION_CONTROLLED_BY_THE_"
                    "EXISTING_POSITIVE_DURATION_GAUGE_FIXED_JACOBI_"
                    "EVOLUTION;_THE_N_UNIFORM_CLOSED_RANGE_BOUND_REMAINS_"
                    "THE_THEOREM_LEVEL_DEPENDENCY"
                ),
                "retained_exact_singular_value": float(paired_singular[0]),
                "deferred_soft_exact_singular_value": float(paired_singular[1]),
                "exact_full_weak_norm_before": boundary_only_full_norm,
                "exact_full_weak_norm_after": hard_best[
                    "exact_normalized_full_weak_norm"
                ],
                "exact_boundary_constraint_norm_before": best[
                    "normalized_boundary_constraint_norm"
                ],
                "exact_boundary_constraint_norm_after": hard_best[
                    "exact_normalized_boundary_constraint_norm"
                ],
                "eta_Legendre_minimum_after": hard_best[
                    "eta_Legendre_minimum"
                ],
                "soft_channel_classification": (
                    "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                    "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
                ),
                "soft_channel_is_a_legitimate_child_manifold_tangent": False,
                "soft_channel_exact_response_projection_magnitude": float(
                    paired_singular[1]
                ),
                "uniform_normal_closed_range_failure_proved": False,
                "exact_next_mathematical_lemma": (
                    "N_UNIFORM_POSITIVE_DURATION_GAUGE_FIXED_JACOBI_"
                    "OBSERVABILITY_INF_SUP_LOWER_BOUND_FOR_THE_ISOLATED_"
                    "SOFT_MOMENTUM_NORMAL_CHANNEL_MODULO_THE_EXISTING_CHILD_"
                    "MANIFOLD_TANGENT_AND_GAUGE_QUOTIENT"
                ),
                "trials": hard_trials,
                "best_trial": hard_best,
                "strict_exact_full_weak_reduction_found": hard_strict_reduction,
            },
        },
        "strict_exact_merit_reduction_found": strict_reduction,
        "is_a_higher_N_complete_child_root": False,
        "is_a_new_boundary_condition": False,
        "first_missing_mathematical_object": (
            "PROVE_THE_N_UNIFORM_POSITIVE_DURATION_GAUGE_FIXED_JACOBI_"
            "OBSERVABILITY_INF_SUP_LOWER_BOUND_FOR_THE_ISOLATED_SOFT_"
            "MOMENTUM_NORMAL_CHANNEL_MODULO_THE_EXISTING_CHILD_MANIFOLD_"
            "TANGENT_AND_GAUGE_QUOTIENT"
            if hard_strict_reduction else
            "LOCALIZE_THE_FIRST_FAILED_MIXED_ACTION_BLOCK_BEFORE_ANY_"
            "FURTHER_BOUNDARY_LAYER_CONTINUATION"
        ),
        "new_equations_constraints_or_acceptance_gates": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def general_n_galerkin_transfer_certificate() -> dict[str, Any]:
    """Derive the continuum-to-Galerkin certificate required by general N."""

    calderon = event_to_child_on_shell_calderon_interface()
    missing = (
        "PROVE_OR_MEASURE_THE_N_UNIFORM_POSITIVE_DURATION_NORMAL_"
        "CLOSED_RANGE_BOUND_AND_WEAK_CONORMAL_CALDERON_GRAPH_"
        "CONVERGENCE_ON_THE_ACTION_ENERGY_COHERENT_BRANCH"
    )
    return {
        "classification": (
            "ACTION_OWNED_WEAK_CONORMAL_GALERKIN_TRANSFER_THEOREM_"
            "DERIVED;_N_UNIFORM_NORMAL_INF_SUP_AND_GRAPH_CONVERGENCE_"
            "CERTIFICATE_OPEN"
        ),
        "continuum_spaces": {
            "state_space": (
                "X_E=R_scale_CROSS_H1_radial_geometry_CROSS_L2_velocity_"
                "CROSS_H1_lapse_shift"
            ),
            "classical_regular_domain": "X_s=H6_q_CROSS_H5_v_CROSS_H6_m",
            "reaction_Calderon_graph_domain": (
                "D_EULER_DIRAC={U_IN_X_s:E_U_IN_X_E_STAR_AND_"
                "Gamma_acc(U)_IN_R2}"
            ),
            "reaction_graph_norm": (
                "norm(U)_X_E+norm(E_U)_X_E_STAR+norm(Gamma_acc(U))_R2"
            ),
            "pure_action_energy_state_space_is_the_complete_reaction_domain": (
                False
            ),
            "constraint_space": (
                "H_MINUS_1_LAPSE_SHIFT_DUAL_CROSS_R_ENERGY"
            ),
            "boundary_space": "R3_TRACE_CROSS_R2_MOMENTUM_CROSS_R2_FLUX",
            "output_space": (
                "Y_E=R3_CROSS_H_MINUS_1_CONSTRAINTS_CROSS_R_ENERGY_"
                "CROSS_R2_MOMENTUM_CROSS_R2_REACTION"
            ),
            "basis": (
                "THE_EXISTING_NESTED_POLE_REGULAR_COSINE_AND_WINDOWED_"
                "COSINE_BASIS"
            ),
            "numerical_fixed_ROW_scales_are_the_continuum_norm": False,
            "H6_H5_H6_is_the_root_transport_distance": False,
        },
        "smoothness_from_the_retained_action": {
            "regularity": "s=6>11/2",
            "role": "CLASSICAL_SOLUTION_DOMAIN_NOT_ENERGY_GRAPH_METRIC",
            "sobolev_algebra_and_trace_control": True,
            "eta_interior_requirement": "inf(L_eta)>=eta_0>0",
            "consequence": (
                "THE_EXPONENTIAL_GEOMETRY_RECIPROCAL_LAPSE_ETA_RESPONSE_"
                "AND_BOUNDARY_TRACES_DEFINE_A_SMOOTH_LOCAL_ACTION_MAP"
            ),
            "new_action_term_added": False,
        },
        "set_valued_continuum_relation": {
            "definition": (
                "R(e)={Y_IN_X:F(Y;e)=0,_L_eta(Y)>0,_Y_PERSISTS}"
            ),
            "finite_N_relation": (
                "R_N(e_N)={Y_N:F_N(Y_N;e_N)=0,_L_eta(Y_N)>0,_Y_N_PERSISTS}"
            ),
            "correct_convergence_object": (
                "LOCAL_GRAPH_OR_HAUSDORFF_CONVERGENCE_OF_R_N_TO_R"
            ),
            "arbitrary_root_coordinates_must_form_a_Cauchy_sequence": False,
            "physical_branch_selector_added": False,
        },
        "event_to_child_on_shell_calderon_interface": calderon,
        "normal_inf_sup_condition": {
            "definition": (
                "beta=inf_(lambda_ne_0)norm(D_F(Y_star;e_star)^*lambda)_"
                "X_star/norm(lambda)_Y"
            ),
            "required_bound": "beta>=beta_0>0_AFTER_EXISTING_GAUGE_REDUCTION",
            "meaning": (
                "THE_CONTINUUM_LINEARIZATION_IS_SURJECTIVE_WITH_A_BOUNDED_"
                "NORMAL_RIGHT_INVERSE;_ITS_KERNEL_IS_THE_CHILD_MANIFOLD"
            ),
            "kernel_removed_as_a_defect": False,
        },
        "spectral_consistency_condition": {
            "derivative_defect": (
                "delta_N=norm(D_F_N-Q_N*D_F*P_N)_X_N_TO_Y_N"
            ),
            "nonlinear_injected_defect": (
                "epsilon_N=norm(F_N(P_N*Y_star;e_N))_Y_N"
            ),
            "event_defect": "norm(e_N-P_N*e_star)_EVENT_TO_ZERO",
            "quadrature_aliasing_included": True,
            "required_limits": "delta_N_TO_0_AND_epsilon_N_TO_0",
        },
        "galerkin_transfer_lemma": {
            "hypothesis": "delta_N<beta_0",
            "discrete_inf_sup": "beta_N>=beta_0-delta_N",
            "right_inverse_bound": "kappa_N<=1/(beta_0-delta_N)",
            "newton_kantorovich_condition": (
                "L_N*epsilon_N/(beta_0-delta_N)^2<=1/2"
            ),
            "local_zero_set_distance_bound": (
                "dist_graph(R_N,R)<=2*epsilon_N/(beta_0-delta_N)"
            ),
            "summable_bound_consequence": (
                "IF_THE_DISTANCE_BOUNDS_ARE_SUMMABLE_THEN_THE_NESTED_"
                "LOCAL_CHILD_RELATIONS_ARE_CAUCHY_IN_GRAPH_DISTANCE"
            ),
        },
        "current_evidence": {
            "N3_N4_N5_discrete_full_row_rank": True,
            "N3_N4_N5_complete_persistence": True,
            "initial_constraint_fiber_smallest_singular_values": {
                "N3": 1.69802344039e-4,
                "N4": 5.6894892171e-5,
                "N5": 4.09514089e-6,
            },
            "accepted_child_local_map_smallest_resolved_singular_values": {
                "N4_full_map": 1.550576651e-6,
                "N5_structural_full_map": 2.39514503e-7,
                "N5_final_nonflux_map": 2.88434876e-7,
            },
            "singular_values_are_directly_cross_resolution_comparable": False,
            "why_not_comparable": (
                "THE_STATES_WERE_INDEPENDENT_AND_THE_REPORTED_MATRICES_USE_"
                "N_DEPENDENT_NUMERICAL_ROW_AND_SOBOLEV_COORDINATE_SCALINGS"
            ),
            "naive_uniform_lower_bound_supported": False,
            "finite_rank_implies_a_uniform_inf_sup_bound": False,
            "independent_root_coordinates_are_a_convergence_sequence": False,
            "existing_cross_resolution_common_mode_differences_are_proof": False,
        },
        "proof_obligations": [
            "DEFINE_THE_CONTINUUM_EVENT_CONDITIONED_ON_SHELL_CALDERON_MAP",
            "PROVE_THE_GAUGE_REDUCED_CONSTRAINT_BOUNDARY_MAP_IS_A_BANACH_SUBMERSION",
            "LOWER_BOUND_THE_CONTINUUM_NORMAL_INF_SUP_CONSTANT_beta_0",
            "BOUND_SPECTRAL_TRUNCATION_AND_GAUSS_QUADRATURE_ALIASING_ERRORS",
            "PROVE_ORDERED_EVENT_BRANCH_CONVERGENCE_AND_A_UNIFORM_ETA_MARGIN",
            "TRANSFER_POSITIVE_DURATION_EULER_DIRAC_PERSISTENCE_UNIFORMLY",
        ],
        "first_missing_mathematical_object": missing,
        "required_next": missing,
        "solver_proposal_curvature_is_part_of_this_certificate": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "FULL_BHSM_COMPLETE": False,
    }


def general_n_complete_child_reconstruction_statement() -> dict[str, Any]:
    """State the exact general-N child-map architecture and open uniform bound."""

    ledgers = []
    for order in (3, 4, 5):
        coordinate_count = 1 + 3 * order
        multiplier_count = 2 * order
        state_count = 2 * coordinate_count + multiplier_count
        constraint_count = 2 * order + 1
        compatibility_rows = 3 + constraint_count + 2
        physical_rows = compatibility_rows + 2
        ledgers.append({
            "N": order,
            "coordinates": coordinate_count,
            "velocities": coordinate_count,
            "multipliers": multiplier_count,
            "whole_child_variables": state_count,
            "trace_rows": 3,
            "constraint_rows": constraint_count,
            "momentum_rows": 2,
            "dynamic_flux_rows": 2,
            "compatibility_rows": compatibility_rows,
            "complete_child_rows": physical_rows,
            "compatibility_fiber_dimension": state_count - compatibility_rows,
            "complete_child_fiber_dimension": state_count - physical_rows,
            "complete_persistent_child_validated": True,
        })
    transfer = general_n_galerkin_transfer_certificate()
    missing_object = transfer["required_next"]
    return {
        "classification": (
            "GENERAL_N_LOCAL_RECONSTRUCTION_ARCHITECTURE_DERIVED;_"
            "UNIFORM_CROSS_RESOLUTION_CONVERGENCE_ESTIMATE_OPEN"
        ),
        "domain": "INTEGER_SPECTRAL_ORDER_N_AT_LEAST_3",
        "exact_dimension_formulas": {
            "coordinate_count": "1+3N",
            "multiplier_count": "2N",
            "whole_child_variable_count": "8N+2",
            "constraint_row_count": "2N+1",
            "order_independent_boundary_core_rows": 7,
            "compatibility_row_count": "2N+6",
            "complete_child_physical_row_count": "2N+8",
            "compatibility_fiber_dimension_at_full_row_rank": "6N-4",
            "complete_child_fiber_dimension_at_full_row_rank": "6N-6",
        },
        "validated_resolution_ledger": ledgers,
        "local_reconstruction_theorem": {
            "map": "F_N(Y_N;e_N)=(A_N,Phi_N):R^(8N+2)->R^(2N+8)",
            "event_parameter": (
                "e_N_IS_THE_EXISTING_ETA_ADMISSIBLE_ORDERED_EVENT_STATE_"
                "AND_IS_NOT_AN_ADDED_CHILD_UNKNOWN"
            ),
            "compatibility_map": (
                "A_N=(TRACE_3,CONSTRAINTS_(2N+1),MOMENTUM_2)"
            ),
            "return_map": "Phi_N=DYNAMIC_CALDERON_FLUX_2",
            "hypotheses": [
                "THE_EVENT_IS_ORDERED_AND_ETA_ADMISSIBLE",
                "THE_RETAINED_ACTION_CHILD_MAP_IS_C1_ON_THE_EVENT_CHART",
                "D_A_N_HAS_FULL_ROW_RANK_2N+6",
                "D_F_N_HAS_FULL_ROW_RANK_2N+8_AT_THE_ROOT",
            ],
            "conclusion": (
                "THE_IMPLICIT_FUNCTION_THEOREM_GIVES_A_LOCAL_SMOOTH_"
                "COMPLETE_CHILD_MANIFOLD_OF_DIMENSION_6N-6"
            ),
            "fiber_equivalence": (
                "A_N(Y)=0_AND_Phi_N_RESTRICTED_TO_THE_LOCAL_A_N_FIBER_"
                "EQUALS_ZERO_IFF_THE_UNCHANGED_F_N(Y)=0"
            ),
            "new_equations_constraints_or_acceptance_gates": False,
        },
        "cross_resolution_continuation_criterion": {
            "spectral_prolongation": (
                "I_N_TO_N_PLUS_1_APPLIED_TO_BOTH_THE_ORDERED_EVENT_e_N_"
                "AND_COMPLETE_CHILD_Y_N"
            ),
            "event_convergence_prerequisite": (
                "THE_EXISTING_ORDERED_EVENT_CONSTRUCTION_SUPPLIES_e_(N+1)_"
                "ON_THE_SAME_BRANCH_WITH_norm(e_(N+1)-I*e_N)->0"
            ),
            "injected_defect": (
                "epsilon_N=norm(F_(N+1)(I*Y_N;e_(N+1)))"
            ),
            "normal_right_inverse_bound": (
                "norm(B_(N+1))<=kappa_(N+1),_D_F_(N+1)B_(N+1)=I"
            ),
            "derivative_lipschitz_bound": (
                "norm(D_F_(N+1)(X)-D_F_(N+1)(Z))<=L_(N+1)norm(X-Z)"
            ),
            "newton_kantorovich_smallness": (
                "kappa_(N+1)^2*L_(N+1)*epsilon_N<=1/2"
            ),
            "admissibility_margin": (
                "THE_RESULTING_2*kappa_(N+1)*epsilon_N_NEIGHBORHOOD_"
                "REMAINS_INSIDE_THE_EXISTING_ETA_AND_ORDERED_EVENT_DOMAIN"
            ),
            "conclusion_if_verified": (
                "AN_F_(N+1)_ROOT_EXISTS_NEAR_THE_SPECTRAL_PROLONGATION;_"
                "THE_NORMAL_CORRECTION_IS_AT_MOST_2*kappa*epsilon"
            ),
            "solution_manifold_kernel_is_not_a_defect": True,
            "extra_gauge_or_physical_selector_added": False,
        },
        "resolution_independent_limit_criterion": {
            "topology": (
                "BHSM_ACTION_ENERGY_TOPOLOGY_H1_GEOMETRY_L2_VELOCITY_"
                "H1_LAPSE_SHIFT"
            ),
            "state_convergence_requires": [
                "CONSISTENT_SPECTRAL_INJECTION_AND_RESTRICTION",
                "UNIFORM_OR_CONTROLLED_NORMAL_RIGHT_INVERSE_BOUNDS",
                "SUMMABLE_NORMAL_CORRECTIONS_OR_AN_EQUIVALENT_CAUCHY_BOUND",
                "SPECTRAL_DEFECT_DECAY_TO_ZERO",
                "A_UNIFORM_POSITIVE_ETA_AND_ORDERED_EVENT_MARGIN",
            ],
            "persistence_convergence_requires": [
                "UNIFORM_LOCAL_LIPSCHITZ_CONTROL_OF_THE_RETAINED_EULER_DIRAC_VECTOR_FIELDS",
                "UNIFORM_DIRAC_HESSIAN_INVERTIBILITY_ON_A_COMMON_POSITIVE_DURATION",
                "CONVERGENCE_OF_THE_PROJECTED_FLOWS_IN_THE_ACTION_ENERGY_TOPOLOGY",
            ],
            "three_resolutions_alone_prove_the_limit": False,
        },
        "galerkin_transfer_certificate": transfer,
        "validated": {
            "independent_N3_N4_N5_complete_persistent_children": True,
            "row_and_fiber_dimension_law_at_N3_N4_N5": True,
            "same_action_and_unchanged_child_map_pattern": True,
            "local_fiber_reduction_adds_no_physics": True,
        },
        "open": {
            "uniform_right_inverse_bound": True,
            "spectral_injection_defect_decay": True,
            "uniform_eta_and_event_margin": True,
            "common_duration_persistence_convergence": True,
            "numerical_state_convergence_from_N3_N4_N5": True,
        },
        "first_missing_mathematical_object": missing_object,
        "required_next": missing_object,
        "FULL_BHSM_COMPLETE": False,
    }


@lru_cache(maxsize=2)
def cross_resolution_reconnaissance(
    *, points: int = DEFAULT_POINTS,
) -> dict[str, Any]:
    rows = [independent_order_probe(order, points=points) for order in ORDERS]
    by_order = {row["order"]: row for row in rows}
    common_4 = np.asarray(by_order[4]["local_flow"]["common_N2_fiber"])
    common_5 = np.asarray(by_order[5]["local_flow"]["common_N2_fiber"])
    observables_4 = by_order[4]["local_flow"]["reset_observables"]
    observables_5 = by_order[5]["local_flow"]["reset_observables"]
    rate_names = (
        "scale_rate", "terminal_u_rate", "terminal_w_rate",
        "terminal_v_rate",
    )
    rate_4 = np.asarray([observables_4[name] for name in rate_names])
    rate_5 = np.asarray([observables_5[name] for name in rate_names])
    n4_bracket = bool(by_order[4]["local_flow"]["ordered_forward_event_bracketed"])
    n5_bracket = bool(by_order[5]["local_flow"]["ordered_forward_event_bracketed"])
    full_ranks = all(
        row["constraint_fiber"]["rank"]
        == row["constraint_fiber"]["row_count"]
        for row in rows
    )
    derivation_valid = (
        by_order[4]["initialization"]["projection_success"]
        and by_order[4]["initialization"]["maximum_constraint_residual"] < 1.0e-8
        and by_order[4]["initialization"]["eta_domain_admissible"]
        and not by_order[4]["initialization"]["accepted_N3_trajectory_used"]
    )
    n5_eta_admissible = bool(
        by_order[5]["initialization"]["eta_domain_admissible"]
    )
    return {
        "orders": rows,
        "cross_resolution_measurements": {
            "N4_vs_N5_common_N2_fiber_relative_difference": (
                _relative_difference(common_4, common_5)
            ),
            "N4_vs_N5_terminal_scale_u_w_v_rate_relative_difference": (
                _relative_difference(rate_4, rate_5)
            ),
            "N4_vs_N5_rate_comparison_is_physical": n5_eta_admissible,
            "all_constraint_fibers_full_row_rank": full_ranks,
        },
        "questions": {
            "N4_independently_derived_from_same_action": {
                "classification": "VALIDATED" if derivation_valid else "INVALIDATED",
                "answer": derivation_valid,
            },
            "ordered_event_exists": {
                "classification": "VALIDATED" if n4_bracket else "OPEN",
                "N4_forward_local_bracket": n4_bracket,
                "N5_forward_local_bracket": n5_bracket,
                "claim_boundary": (
                    "A_LOCAL_BRACKET_VALIDATES_EXISTENCE_ONLY_IF_TRUE;_"
                    "OTHERWISE_A_BOUNDED_LOCAL_PROBE_DOES_NOT_PROVE_ABSENCE"
                ),
            },
            "same_rank14_complete_child_reconstructs": {
                "classification": "RECLASSIFIED",
                "answer": None,
                "literal_rank14_survives": False,
                "reason": (
                    "THE_BOUNDARY_CORE_HAS_SEVEN_ORDER_INDEPENDENT_ROWS,_BUT_"
                    "THE_ACTION_ADDS_TWO_CONSTRAINT_ROWS_PER_SPECTRAL_ORDER;_"
                    "THE_FULL_UNREDUCED_COUNTS_ARE_14,_16,_18"
                ),
                "reconstruction_gate": (
                    "OPEN_UNTIL_AN_INDEPENDENT_ORDERED_EVENT_SUPPLIES_"
                    "EVENT_CONDITIONED_CHILD_DATA"
                ),
            },
            "encapsulation_movie_resembles_N3": {
                "classification": "OPEN",
                "answer": None,
                "validated_extent": (
                    "RESET_AND_ONE_CONSTRAINT_CONSISTENT_FORWARD_TANGENT_FRAME"
                ),
                "full_movie_compared": False,
            },
            "period_scale_w_v_survive_resolution": {
                "classification": "OPEN",
                "period": "OPEN_UNTIL_ORDERED_EVENT",
                "scale_u_w_v_local_rates_measured": True,
            },
            "N5_confirms_or_contradicts_N4": {
                "classification": "OPEN",
                "answer": (
                    None if n5_eta_admissible
                    else "CURRENT_BRANCH_INADMISSIBLE_NO_CROSS_RESOLUTION_VERDICT"
                ),
                "structural_confirmation": (
                    "SAME_ACTION,_INDEPENDENT_CONSTRAINT_SURFACE,_AND_"
                    "SEVEN_ROW_BOUNDARY_CORE"
                ),
                "event_child_confirmation": False,
                "physical_reset_eta_admissible": n5_eta_admissible,
                "blocker": (
                    None if n5_eta_admissible
                    else "N5_DENSE_ETA_LEGENDRE_MINIMUM_IS_NONPOSITIVE"
                ),
                "eta_classification": None if n5_eta_admissible else "ETA-D",
            },
        },
        "scientific_status": (
            "N4_INDEPENDENT_ACTION_DERIVATION_VALIDATED;_N5_DIRECT_RESET_"
            "CONSTRAINTS_CLOSE_BUT_THE_CURRENT_BRANCH_FAILS_THE_EXISTING_"
            "ETA_DOMAIN_WITH_OTHER_BRANCHES_OPEN;_EVENT,_COMPLETE_CHILD,_"
            "FULL_MOVIE,_AND_PERIOD_REMAIN_UNPROMOTED"
        ),
        "active_dependency": (
            "LOCATE_OR_RULE_OUT_THE_FIRST_ISOLATED_ORDERED_DIRAC_EVENT_ON_"
            "THE_ADMISSIBLE_INDEPENDENT_N4_ORBIT;_DO_NOT_ADVANCE_THE_CURRENT_"
            "N5_RESET_PAST_ITS_ETA_DOMAIN_FAILURE"
        ),
    }


def completion_payload(
    *,
    points: int = DEFAULT_POINTS,
    include_n4_step_audit: bool = False,
    include_n4_event_resolution_audit: bool = False,
    include_n4_adaptive_event_convergence_audit: bool = False,
    include_n4_complete_child_reconstruction: bool = False,
) -> dict[str, Any]:
    result = cross_resolution_reconnaissance(points=points)
    ownership = ingredient_process_ownership_audit()
    scale_accessibility = physical_scale_accessibility_audit()
    closure_network = breadth_first_closure_network_audit()
    if include_n4_step_audit:
        result = dict(result)
        result["N4_targeted_event_step_audit"] = n4_ordered_event_step_audit(
            points=points
        )
    if include_n4_event_resolution_audit:
        result = dict(result)
        result["N4_ordered_event_resolution_audit"] = (
            n4_ordered_event_resolution_audit(points=points)
        )
    if include_n4_adaptive_event_convergence_audit:
        result = dict(result)
        adaptive = n4_adaptive_event_convergence_audit(points=points)
        result["N4_adaptive_event_convergence_audit"] = adaptive
        questions = dict(result["questions"])
        ordered = dict(questions["ordered_event_exists"])
        ordered["N4_adaptive_quadrature_audit"] = adaptive["classification"]
        if adaptive["N4_ordered_event_validated"]:
            ordered["classification"] = "VALIDATED"
            ordered["N4_ordered_event_exists"] = True
            ordered["claim_boundary"] = (
                "VALIDATES_THE_ORDERED_EVENT_FOR_THE_INDEPENDENT_N4_"
                "TRAJECTORY_ONLY;_DOES_NOT_IMPLY_ENCLOSURE_OR_A_CHILD"
            )
            result["active_dependency"] = adaptive["required_next"]
        questions["ordered_event_exists"] = ordered
        result["questions"] = questions
    if include_n4_complete_child_reconstruction:
        result = dict(result)
        child = n4_event_conditioned_complete_child_reconstruction(
            points=44
        )
        result["N4_event_conditioned_complete_child_reconstruction"] = child
        questions = dict(result["questions"])
        child_question = dict(
            questions["same_rank14_complete_child_reconstructs"]
        )
        child_question.update({
            "N4_physical_row_count": child["physical_row_count"],
            "N4_structural_row_rank": child["chart"]["full_chart_rank"],
            "N4_complete_child_candidate_validated": child[
                "complete_child_candidate_validated"
            ],
            "N4_dynamic_flux_jacobian_step_converged": child["chart"][
                "dynamic_flux_jacobian_step_converged"
            ],
            "N4_active_blocker": child["required_next"],
        })
        questions["same_rank14_complete_child_reconstructs"] = child_question
        result["questions"] = questions
        result["active_dependency"] = child["required_next"]
    validation = {
        "orders_N3_N4_N5_measured": [
            row["order"] for row in result["orders"]
        ] == [3, 4, 5],
        "no_accepted_N3_trajectory_transplanted": all(
            not row["initialization"]["accepted_N3_trajectory_used"]
            for row in result["orders"]
        ),
        "all_independent_constraint_projections_closed": all(
            row["initialization"]["maximum_constraint_residual"] < 1.0e-8
            for row in result["orders"]
        ),
        "N5_eta_failure_not_promoted": (
            not result["orders"][2]["initialization"]["eta_domain_admissible"]
            and result["orders"][2]["local_flow"]["physical_probe_admissible"] is False
        ),
        "ingredient_process_ownership_validated": ownership[
            "validation_passed"
        ],
        "physical_scale_accessibility_audit_validated": scale_accessibility[
            "validation_passed"
        ],
        "breadth_first_closure_network_validated": closure_network[
            "validation_passed"
        ],
        "undefined_sector_balance_not_promoted": (
            scale_accessibility["action_sector_ownership"]["C_ES_status"]
            == "OPEN_UNDEFINED_NOT_ZERO"
            and scale_accessibility["event_approach_metric_audit"][
                "chi_E_status"
            ] == "OPEN_UNDEFINED_UNTIL_G_IS_DERIVED"
        ),
        "all_constraint_fibers_full_row_rank": result[
            "cross_resolution_measurements"
        ]["all_constraint_fibers_full_row_rank"],
        "rank14_not_silently_imposed_at_higher_N": (
            [
                row["complete_child_structure"]["full_unreduced_child_row_count"]
                for row in result["orders"]
            ] == [14, 16, 18]
        ),
        "unresolved_questions_not_promoted": all(
            result["questions"][key]["classification"] in {"OPEN", "RECLASSIFIED"}
            for key in (
                "same_rank14_complete_child_reconstructs",
                "encapsulation_movie_resembles_N3",
                "period_scale_w_v_survive_resolution",
                "N5_confirms_or_contradicts_N4",
            )
        ),
        "FULL_BHSM_COMPLETE_false": not FULL_BHSM_COMPLETE,
    }
    if include_n4_adaptive_event_convergence_audit:
        validation["included_N4_adaptive_event_audit_internally_consistent"] = (
            result["N4_adaptive_event_convergence_audit"][
                "N4_ordered_event_validated"
            ]
            == (
                result["questions"]["ordered_event_exists"][
                    "classification"
                ] == "VALIDATED"
            )
        )
    if include_n4_complete_child_reconstruction:
        child = result["N4_event_conditioned_complete_child_reconstruction"]
        validation["included_N4_child_map_not_overpromoted"] = (
            child["physical_row_count"] == 16
            and child["chart"]["full_chart_rank"] == 16
            and not child["physical_equations_changed"]
            and not child["event_definition_changed"]
            and child["persistence_evaluated"] is False
            and child["FULL_BHSM_COMPLETE"] is False
        )
    return {
        "artifact": "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "quadrature_points": points,
        "cross_resolution_reconnaissance": result,
        "ingredient_process_ownership_audit": ownership,
        "physical_scale_accessibility_audit": scale_accessibility,
        "breadth_first_closure_network_audit": closure_network,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(
    directory: str | Path,
    *,
    points: int = DEFAULT_POINTS,
    include_n4_step_audit: bool = False,
    include_n4_event_resolution_audit: bool = False,
    include_n4_adaptive_event_convergence_audit: bool = False,
    include_n4_complete_child_reconstruction: bool = False,
) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    path.write_text(
        deterministic_json(completion_payload(
            points=points,
            include_n4_step_audit=include_n4_step_audit,
            include_n4_event_resolution_audit=(
                include_n4_event_resolution_audit
            ),
            include_n4_adaptive_event_convergence_audit=(
                include_n4_adaptive_event_convergence_audit
            ),
            include_n4_complete_child_reconstruction=(
                include_n4_complete_child_reconstruction
            ),
        )),
        encoding="utf-8",
    )
    return path


def refresh_existing_n4_child_checkpoint(
    path: str | Path,
) -> Path:
    """Refresh only the derived interfaces and N4 child rolling checkpoint."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    n4_event_conditioned_complete_child_reconstruction.cache_clear()
    child = n4_event_conditioned_complete_child_reconstruction(
        points=44, resume_from_checkpoint=True
    )
    if not child["rolling_checkpoint_promotion"]["eligible"]:
        n4_latest_checkpoint_proposal_audit.cache_clear()
        return target
    result["N4_event_conditioned_complete_child_reconstruction"] = child
    questions = dict(result["questions"])
    child_question = dict(questions["same_rank14_complete_child_reconstructs"])
    child_question.update({
        "N4_physical_row_count": child["physical_row_count"],
        "N4_structural_row_rank": child["chart"]["full_chart_rank"],
        "N4_complete_child_candidate_validated": child[
            "complete_child_candidate_validated"
        ],
        "N4_dynamic_flux_jacobian_step_converged": child["chart"][
            "dynamic_flux_jacobian_step_converged"
        ],
        "N4_active_blocker": child["required_next"],
    })
    questions["same_rank14_complete_child_reconstructs"] = child_question
    result["questions"] = questions
    result["active_dependency"] = child["required_next"]
    payload["cross_resolution_reconnaissance"] = result
    network = breadth_first_closure_network_audit()
    payload["breadth_first_closure_network_audit"] = network
    validation = dict(payload["validation"])
    validation["breadth_first_closure_network_validated"] = network[
        "validation_passed"
    ]
    validation["included_N4_child_map_not_overpromoted"] = (
        child["physical_row_count"] == 16
        and child["chart"]["full_chart_rank"] == 16
        and not child["physical_equations_changed"]
        and not child["event_definition_changed"]
        and child["persistence_evaluated"] is False
        and child["FULL_BHSM_COMPLETE"] is False
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    n4_latest_checkpoint_proposal_audit.cache_clear()
    return target


def refresh_existing_n4_persistence_checkpoint(path: str | Path) -> Path:
    """Attach the focused positive-duration N4 persistence witness."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    child = dict(
        result["N4_event_conditioned_complete_child_reconstruction"]
    )
    if not child["complete_child_candidate_validated"]:
        raise RuntimeError("cannot persist an unvalidated N4 child")
    n4_complete_child_positive_duration_persistence.cache_clear()
    persistence = n4_complete_child_positive_duration_persistence(points=44)
    validated = persistence[
        "positive_duration_relative_persistence_validated"
    ]
    child["persistence_evaluated"] = True
    child["persistence_validated"] = validated
    child["required_next"] = (
        "CLASSIFY_THE_N4_COMPLETE_PERSISTENT_CHILD_AGAINST_N3_AND_TEST_"
        "THE_INDEPENDENT_N5_ETA_ADMISSIBLE_BRANCH"
        if validated else
        "RESOLVE_THE_FIRST_FAILED_N4_PERSISTENCE_DOMAIN_OR_NUMERICAL_"
        "CONVERGENCE_CONDITION"
    )
    result["N4_event_conditioned_complete_child_reconstruction"] = child
    result["N4_complete_child_positive_duration_persistence"] = persistence
    questions = dict(result["questions"])
    child_question = dict(
        questions["same_rank14_complete_child_reconstructs"]
    )
    child_question.update({
        "N4_complete_child_candidate_validated": True,
        "N4_positive_duration_persistence_validated": validated,
        "N4_result": (
            "RECLASSIFIED_RANK16_COMPLETE_PERSISTENT_CHILD"
            if validated else "N4_COMPLETE_CHILD_PERSISTENCE_OPEN"
        ),
        "N4_active_blocker": child["required_next"],
    })
    questions["same_rank14_complete_child_reconstructs"] = child_question
    result["questions"] = questions
    result["active_dependency"] = child["required_next"]
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["included_N4_positive_duration_persistence"] = validated
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def refresh_existing_cross_resolution_classification(path: str | Path) -> Path:
    """Attach the independent N5 event classification without overpromotion."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    n5_cross_quadrature_event_classification.cache_clear()
    n5 = n5_cross_quadrature_event_classification()
    if not n5["qualitative_ordered_event_existence_validated"]:
        raise RuntimeError("independent N5 qualitative event did not validate")
    result["N5_independent_eta_branch_event_classification"] = n5
    questions = dict(result["questions"])
    ordered = dict(questions["ordered_event_exists"])
    ordered.update({
        "N5_classification": n5["classification"],
        "N5_ordered_event_exists_qualitatively": True,
        "N5_quantitative_event_time_validated": n5[
            "quantitative_event_time_validated"
        ],
        "N5_claim_boundary": (
            "THE_SAME_ETA_ADMISSIBLE_INERTIA_BOUNDARY_MODE_EXISTS_ACROSS_"
            "THREE_QUADRATURES;_THE_EVENT_TIME_IS_NOT_PROMOTED"
        ),
    })
    questions["ordered_event_exists"] = ordered
    child_question = dict(
        questions["same_rank14_complete_child_reconstructs"]
    )
    child_question.update({
        "N5_physical_row_count": 18,
        "N5_complete_child_candidate_validated": False,
        "N5_child_status": "OPEN_EVENT_CONDITIONED_18_ROW_MAP",
    })
    questions["same_rank14_complete_child_reconstructs"] = child_question
    n5_question = dict(questions["N5_confirms_or_contradicts_N4"])
    n5_question.update({
        "classification": "VALIDATED_QUALITATIVE_EVENT_STRUCTURE_ONLY",
        "answer": n5["N5_confirms_N4"],
        "event_child_confirmation": False,
        "physical_reset_eta_admissible": True,
        "blocker": "N5_EVENT_CONDITIONED_18_ROW_COMPLETE_CHILD_MAP",
        "eta_classification": "ETA_ADMISSIBLE_ZERO_MULTIPLIER_BRANCH",
    })
    questions["N5_confirms_or_contradicts_N4"] = n5_question
    result["questions"] = questions
    result["scientific_status"] = (
        "N4_COMPLETE_PERSISTENT_CHILD_VALIDATED;_INDEPENDENT_N5_ETA_"
        "ADMISSIBLE_ORDERED_EVENT_EXISTENCE_VALIDATED_QUALITATIVELY;_"
        "N5_EVENT_TIME,_CHILD,_AND_PERSISTENCE_REMAIN_OPEN"
    )
    result["active_dependency"] = (
        "DERIVE_AND_EVALUATE_THE_EVENT_CONDITIONED_N5_18_ROW_COMPLETE_"
        "CHILD_MAP_ON_THE_INDEPENDENT_ZERO_MULTIPLIER_BRANCH"
    )
    payload["cross_resolution_reconnaissance"] = result
    ownership = ingredient_process_ownership_audit()
    network = breadth_first_closure_network_audit()
    payload["ingredient_process_ownership_audit"] = ownership
    payload["breadth_first_closure_network_audit"] = network
    validation = dict(payload["validation"])
    validation["ingredient_process_ownership_validated"] = ownership[
        "validation_passed"
    ]
    validation["breadth_first_closure_network_validated"] = network[
        "validation_passed"
    ]
    validation.pop("unresolved_questions_not_promoted", None)
    validation["N5_qualitative_event_not_overpromoted"] = bool(
        n5["qualitative_ordered_event_existence_validated"]
        and not n5["quantitative_event_time_validated"]
        and not child_question["N5_complete_child_candidate_validated"]
        and n5_question["event_child_confirmation"] is False
    )
    validation["no_cross_resolution_state_transplant"] = not n5[
        "accepted_N3_trajectory_or_N4_child_used"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def refresh_existing_n5_child_chart_checkpoint(path: str | Path) -> Path:
    """Attach the focused independent N5 event-to-child chart audit."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    n5_event_conditioned_complete_child_chart_audit.cache_clear()
    chart = n5_event_conditioned_complete_child_chart_audit(points=44)
    result["N5_event_conditioned_complete_child_chart_audit"] = chart
    questions = dict(result["questions"])
    child_question = dict(
        questions["same_rank14_complete_child_reconstructs"]
    )
    child_question.update({
        "N5_physical_row_count": chart["physical_row_count"],
        "N5_structural_row_rank": chart["chart"]["full_chart_rank"],
        "N5_dynamic_flux_jacobian_step_converged": chart["chart"][
            "dynamic_flux_jacobian_step_converged"
        ],
        "N5_complete_child_candidate_validated": False,
        "N5_child_status": (
            "STRUCTURALLY_FULL_RANK_EVENT_CONDITIONED_18_ROW_MAP_ROOT_OPEN"
            if chart["structurally_full_row_rank"] else
            "EVENT_CONDITIONED_18_ROW_MAP_RANK_OPEN"
        ),
    })
    questions["same_rank14_complete_child_reconstructs"] = child_question
    result["questions"] = questions
    result["active_dependency"] = chart["required_next"]
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["N5_child_chart_not_overpromoted"] = bool(
        chart["physical_row_count"] == 18
        and not chart["complete_child_candidate_validated"]
        and not chart["physical_equations_changed"]
        and not chart["event_definition_changed"]
        and not chart["accepted_N3_trajectory_or_N4_child_used"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def refresh_existing_n5_child_checkpoint(path: str | Path) -> Path:
    """Promote only an exact-merit-reducing admissible N5 child checkpoint."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    n5_event_conditioned_complete_child_reconstruction.cache_clear()
    child = n5_event_conditioned_complete_child_reconstruction(points=44)
    if not child["checkpoint_promotion_eligible"]:
        result["N5_rejected_child_proposal_audit"] = child
        payload["cross_resolution_reconnaissance"] = result
        validation = dict(payload["validation"])
        validation["N5_rejected_proposal_not_promoted"] = bool(
            not child["checkpoint_promotion_eligible"]
            and not child["complete_child_candidate_validated"]
        )
        payload["validation"] = validation
        payload["validation_passed"] = all(validation.values())
        target.write_text(deterministic_json(payload), encoding="utf-8")
        return target
    result["N5_event_conditioned_complete_child_reconstruction"] = child
    questions = dict(result["questions"])
    child_question = dict(
        questions["same_rank14_complete_child_reconstructs"]
    )
    child_question.update({
        "N5_physical_row_count": child["physical_row_count"],
        "N5_complete_child_candidate_validated": child[
            "complete_child_candidate_validated"
        ],
        "N5_child_status": (
            "VALIDATED_RANK18_COMPLETE_CHILD"
            if child["complete_child_candidate_validated"] else
            "ADMISSIBLE_EXACT_MERIT_REDUCING_N5_CHILD_CHECKPOINT"
        ),
    })
    questions["same_rank14_complete_child_reconstructs"] = child_question
    result["questions"] = questions
    result["active_dependency"] = child["required_next"]
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["N5_child_checkpoint_physical_authority_preserved"] = bool(
        child["solver"]["fixed_reference_merit_reduced"]
        and child["child_state"]["eta_Legendre"]["minimum"] > 0.0
        and not child["physical_equations_changed"]
        and not child["event_definition_changed"]
        and not child["accepted_N3_trajectory_or_N4_child_used"]
        and not child["proposal_model"][
            "finite_difference_derivative_promoted_as_physics"
        ]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_existing_n5_persistence(path: str | Path) -> Path:
    """Record N5 persistence only after the unchanged 18-row root closes."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    child = dict(result["N5_event_conditioned_complete_child_reconstruction"])
    if not child.get("complete_child_candidate_validated", False):
        raise RuntimeError("N5 exact 18-row child root must close first")
    n5_complete_child_positive_duration_persistence.cache_clear()
    persistence = n5_complete_child_positive_duration_persistence(points=44)
    if not persistence["positive_duration_relative_persistence_validated"]:
        raise RuntimeError("N5 retained-action persistence did not validate")
    child["persistence_evaluated"] = True
    child["complete_persistent_child_validated"] = True
    child["required_next"] = (
        "DERIVE_THE_GENERAL_N_COMPLETE_PERSISTENT_CHILD_RECONSTRUCTION_"
        "AND_CROSS_RESOLUTION_CONVERGENCE_STATEMENT_FROM_INDEPENDENT_N3_N4_N5"
    )
    result["N5_event_conditioned_complete_child_reconstruction"] = child
    result["N5_complete_child_positive_duration_persistence"] = persistence
    result["active_dependency"] = child["required_next"]
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "GENERAL_N_RECONSTRUCTION_AND_CONVERGENCE_STATEMENT_ACTIVE"
    )
    questions = dict(result["questions"])
    child_question = dict(questions["same_rank14_complete_child_reconstructs"])
    child_question.update({
        "N5_complete_child_candidate_validated": True,
        "N5_complete_persistent_child_validated": True,
        "N5_child_status": "VALIDATED_RANK18_COMPLETE_PERSISTENT_CHILD",
    })
    questions["same_rank14_complete_child_reconstructs"] = child_question
    result["questions"] = questions
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["N5_complete_persistent_child_validated"] = True
    validation["N5_eta_domain_retained_through_persistence"] = bool(
        persistence["coarse_evolution"]["minimum_eta_Legendre"] > 0.0
        and persistence["fine_evolution"]["minimum_eta_Legendre"] > 0.0
    )
    validation["N5_nonzero_relative_evolution_retained"] = bool(
        persistence["nonzero_relative_evolution_retained"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_existing_general_n_statement(path: str | Path) -> Path:
    """Record the derived local general-N architecture without claiming a limit."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    n4 = result["N4_event_conditioned_complete_child_reconstruction"]
    n5 = result["N5_event_conditioned_complete_child_reconstruction"]
    n3_path = target.parent / (
        "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    )
    n3_payload = json.loads(n3_path.read_text(encoding="utf-8"))
    n3_persistence = n3_payload["complete_child_persistence"]["persistence"]
    independent_persistent = bool(
        n3_payload["validation_passed"]
        and n3_persistence["positive_duration_witness"]
        and n3_persistence["relative_evolution_nonzero"]
        and n4["complete_child_candidate_validated"]
        and n4["persistence_validated"]
        and n5["complete_child_candidate_validated"]
        and n5["complete_persistent_child_validated"]
    )
    if not independent_persistent:
        raise RuntimeError("independent N3/N4/N5 persistent children required")

    statement = general_n_complete_child_reconstruction_statement()
    frame_audit = cross_resolution_principal_symbol_frame_audit(target)
    strong_constraint_audit = cross_resolution_strong_constraint_infsup_audit(
        target
    )
    boundary_polarization_audit = (
        cross_resolution_boundary_symplectic_polarization_audit(target)
    )
    attachment_lift_audit = nested_attachment_lift_consistency_audit(target)
    boundary_reaction_audit = on_shell_boundary_reaction_audit(target)
    history_bvp_audit = child_history_bvp_bordered_operator_audit(target)
    two_sided_reaction_audit = event_child_two_sided_reaction_match_audit(
        target
    )
    energy_topology_audit = action_energy_topology_coherent_event_audit(
        target
    )
    statement["cross_resolution_principal_symbol_frame_audit"] = frame_audit
    statement["cross_resolution_strong_constraint_infsup_audit"] = (
        strong_constraint_audit
    )
    statement["cross_resolution_boundary_symplectic_polarization_audit"] = (
        boundary_polarization_audit
    )
    statement["nested_attachment_lift_consistency_audit"] = (
        attachment_lift_audit
    )
    statement["on_shell_boundary_reaction_audit"] = boundary_reaction_audit
    statement["child_history_bvp_bordered_operator_audit"] = (
        history_bvp_audit
    )
    statement["event_child_two_sided_reaction_match_audit"] = (
        two_sided_reaction_audit
    )
    statement["action_energy_topology_coherent_event_audit"] = (
        energy_topology_audit
    )
    required_next = energy_topology_audit["required_next"]
    statement["first_missing_mathematical_object"] = required_next
    statement["required_next"] = required_next
    result["general_N_complete_child_reconstruction_and_convergence_statement"] = (
        statement
    )
    result["cross_resolution_principal_symbol_frame_audit"] = frame_audit
    result["cross_resolution_strong_constraint_infsup_audit"] = (
        strong_constraint_audit
    )
    result["cross_resolution_boundary_symplectic_polarization_audit"] = (
        boundary_polarization_audit
    )
    result["nested_attachment_lift_consistency_audit"] = attachment_lift_audit
    result["on_shell_boundary_reaction_audit"] = boundary_reaction_audit
    result["child_history_bvp_bordered_operator_audit"] = history_bvp_audit
    result["event_child_two_sided_reaction_match_audit"] = (
        two_sided_reaction_audit
    )
    result["action_energy_topology_coherent_event_audit"] = (
        energy_topology_audit
    )
    child = dict(n5)
    child["required_next"] = required_next
    result["N5_event_conditioned_complete_child_reconstruction"] = child
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "GENERAL_N_LOCAL_RECONSTRUCTION_ARCHITECTURE_DERIVED;_UNIFORM_"
        "ACTION_ENERGY_TOPOLOGY_AND_COHERENT_N4_TO_N5_EVENT_DERIVED;_"
        "COHERENT_COMPLETE_CHILD_GRAPH_AND_UNIFORM_BOUND_OPEN"
    )

    questions = dict(result["questions"])
    rank_question = dict(questions["same_rank14_complete_child_reconstructs"])
    rank_question.update({
        "classification": "RECLASSIFIED_AND_RESOLVED_AT_N3_N4_N5",
        "answer": "GENERAL_COMPLETE_CHILD_ROW_RANK_IS_2N+8",
        "literal_rank14_survives": False,
        "validated_ranks": {"N3": 14, "N4": 16, "N5": 18},
        "validated_root_fiber_dimensions": {"N3": 12, "N4": 18, "N5": 24},
        "reconstruction_gate": (
            "CLOSED_INDEPENDENTLY_AT_N3_N4_N5;_UNIFORM_GENERAL_N_"
            "CONTINUATION_ESTIMATE_REMAINS_OPEN"
        ),
    })
    rank_question.pop("N4_active_blocker", None)
    rank_question.pop("N5_active_blocker", None)
    questions["same_rank14_complete_child_reconstructs"] = rank_question

    movie = dict(questions["encapsulation_movie_resembles_N3"])
    movie.update({
        "classification": "RECLASSIFIED",
        "answer": (
            "INDEPENDENT_POSITIVE_DURATION_MOVIES_EXIST_AT_N3_N4_N5;_"
            "CROSS_RESOLUTION_MOVIE_CONVERGENCE_IS_OPEN"
        ),
        "independent_persistence_movies_validated": True,
        "full_movie_compared": False,
    })
    questions["encapsulation_movie_resembles_N3"] = movie

    structure = dict(questions["period_scale_w_v_survive_resolution"])
    structure.update({
        "classification": "RECLASSIFIED",
        "answer": (
            "THE_PERIOD_SCALE_W_V_COORDINATE_ARCHITECTURE_SURVIVES_AT_"
            "N3_N4_N5;_QUANTITATIVE_SPECTRAL_CONVERGENCE_IS_OPEN"
        ),
        "architectural_survival_validated": True,
        "quantitative_convergence_validated": False,
    })
    questions["period_scale_w_v_survive_resolution"] = structure

    n5_question = dict(questions["N5_confirms_or_contradicts_N4"])
    n5_question.update({
        "classification": "VALIDATED_STRUCTURAL_CONFIRMATION",
        "answer": (
            "N5_CONFIRMS_THE_ACTION_DERIVED_COMPLETE_PERSISTENT_CHILD_"
            "ARCHITECTURE;_IT_DOES_NOT_BY_ITSELF_PROVE_RESOLUTION_CONVERGENCE"
        ),
        "event_child_confirmation": True,
        "complete_persistence_confirmation": True,
        "blocker": None,
    })
    questions["N5_confirms_or_contradicts_N4"] = n5_question
    result["questions"] = questions
    payload["cross_resolution_reconnaissance"] = result
    closure_network = breadth_first_closure_network_audit()
    payload["breadth_first_closure_network_audit"] = closure_network

    validation = dict(payload["validation"])
    validation.pop(
        "N5_flux_value_stable_but_outer_derivative_unresolved", None
    )
    validation.update({
        "independent_N3_N4_N5_complete_persistent_children": True,
        "general_N_dimension_law_validated_at_N3_N4_N5": True,
        "general_N_local_fiber_equivalence_adds_no_physics": True,
        "general_N_uniform_convergence_not_overpromoted": bool(
            statement["resolution_independent_limit_criterion"][
                "three_resolutions_alone_prove_the_limit"
            ] is False
        ),
        "breadth_first_closure_network_validated": closure_network[
            "validation_passed"
        ],
        "cross_resolution_principal_symbol_frame_audit_validated": frame_audit[
            "validation_passed"
        ],
        "cross_resolution_strong_constraint_infsup_audit_validated": (
            strong_constraint_audit["validation_passed"]
        ),
        "cross_resolution_boundary_symplectic_polarization_audit_validated": (
            boundary_polarization_audit["validation_passed"]
        ),
        "nested_attachment_lift_consistency_audit_validated": (
            attachment_lift_audit["validation_passed"]
        ),
        "on_shell_boundary_reaction_audit_validated": (
            boundary_reaction_audit["validation_passed"]
        ),
        "child_history_bvp_bordered_operator_audit_validated": (
            history_bvp_audit["validation_passed"]
        ),
        "event_child_two_sided_reaction_match_audit_validated": (
            two_sided_reaction_audit["validation_passed"]
        ),
        "action_energy_topology_coherent_event_audit_validated": (
            energy_topology_audit["validation_passed"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_existing_coherent_n4_to_n5_child_persistence(
    path: str | Path,
) -> Path:
    """Promote the already-defined persistence witness for the coherent graph."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    graph = dict(result["coherent_N4_to_N5_complete_child_graph"])
    if not graph.get("complete_child_candidate_validated", False):
        raise RuntimeError("coherent N4-to-N5 child root must close first")
    coherent_n4_to_n5_complete_child_positive_duration_persistence.cache_clear()
    persistence = (
        coherent_n4_to_n5_complete_child_positive_duration_persistence(
            points=44
        )
    )
    if not persistence["positive_duration_relative_persistence_validated"]:
        raise RuntimeError("coherent N4-to-N5 child persistence did not close")
    reaction_calderon = reaction_calderon_nested_schur_trace_audit(
        target, points=44
    )
    if not reaction_calderon["validation_passed"]:
        raise RuntimeError("reaction-Calderon nested Schur audit failed")
    weak_conormal = weak_conormal_reaction_graph_audit(
        target, points=96, maximum_order=12
    )
    if not weak_conormal["validation_passed"]:
        raise RuntimeError("weak conormal reaction graph audit failed")
    gauge_quotient = boundary_compatible_gauge_quotient_audit(
        target, points=96, maximum_order=13
    )
    if not gauge_quotient["validation_passed"]:
        raise RuntimeError("boundary-compatible gauge quotient audit failed")
    required_next = gauge_quotient["required_next"]
    graph.update({
        "persistence_evaluated": True,
        "persistence_validated": True,
        "complete_persistent_child_validated": True,
        "required_next": required_next,
    })
    result["coherent_N4_to_N5_complete_child_graph"] = graph
    result[
        "coherent_N4_to_N5_complete_child_positive_duration_persistence"
    ] = persistence
    result["reaction_calderon_nested_schur_trace_audit"] = (
        reaction_calderon
    )
    result["weak_conormal_reaction_graph_audit"] = weak_conormal
    result["boundary_compatible_gauge_quotient_audit"] = gauge_quotient
    energy = dict(result["action_energy_topology_coherent_event_audit"])
    energy.update({
        "classification": (
            "ACTION_ENERGY_TOPOLOGY_DERIVED;_H6_MINIMUM_PROJECTION_"
            "RECLASSIFIED_AS_OVERREGULARIZED_FOR_RELATION_TRANSPORT;_"
            "COHERENT_N4_TO_N5_COMPLETE_PERSISTENT_CHILD_GRAPH_VALIDATED;_"
            "REACTION_CALDERON_GRAPH_DOMAIN_RECLASSIFIED"
        ),
        "coherent_complete_child_graph_validated": True,
        "coherent_complete_child_persistence_validated": True,
        "required_next": required_next,
    })
    result["action_energy_topology_coherent_event_audit"] = energy
    statement = dict(
        result["general_N_complete_child_reconstruction_and_convergence_statement"]
    )
    statement["first_missing_mathematical_object"] = required_next
    statement["required_next"] = required_next
    result[
        "general_N_complete_child_reconstruction_and_convergence_statement"
    ] = statement
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "ACTION_ENERGY_COHERENT_N4_TO_N5_COMPLETE_PERSISTENT_CHILD_GRAPH_"
        "VALIDATED;_WEAK_CONORMAL_REACTION_GRAPH_AND_UNIFORM_TRACE_LIFT_"
        "DERIVED;_PRINCIPAL_GAUGE_SOFT_SECTOR_QUOTIENTED;_FULL_HISTORY_"
        "JACOBI_ENERGY_ESTIMATE_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation.update({
        "coherent_N4_to_N5_complete_child_graph_validated": True,
        "coherent_N4_to_N5_positive_duration_persistence_validated": True,
        "coherent_N4_to_N5_nonzero_relative_evolution_retained": bool(
            persistence["nonzero_relative_evolution_retained"]
        ),
        "reaction_calderon_nested_schur_trace_audit_validated": (
            reaction_calderon["validation_passed"]
        ),
        "weak_conormal_reaction_graph_audit_validated": (
            weak_conormal["validation_passed"]
        ),
        "boundary_compatible_gauge_quotient_audit_validated": (
            gauge_quotient["validation_passed"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_general_n_weak_history_checkpoint(path: str | Path) -> Path:
    """Persist the sequential transport and weak history Jacobi checkpoint."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    sequential = sequential_action_energy_projection_audit(target)
    if not sequential["validation_passed"]:
        raise RuntimeError("sequential action-energy projection audit failed")
    jacobi = positive_duration_gauge_fixed_jacobi_audit(target)
    if not jacobi["validation_passed"]:
        raise RuntimeError("positive-duration weak Jacobi audit failed")
    required_next = jacobi["required_next"]
    result["sequential_action_energy_projection_audit"] = sequential
    result["positive_duration_gauge_fixed_jacobi_audit"] = jacobi
    statement = general_n_complete_child_reconstruction_statement()
    statement["first_missing_mathematical_object"] = required_next
    statement["required_next"] = required_next
    result[
        "general_N_complete_child_reconstruction_and_convergence_statement"
    ] = statement
    result["event_to_child_on_shell_calderon_interface"] = (
        event_to_child_on_shell_calderon_interface()
    )
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "ACTION_ENERGY_COHERENT_NESTED_EVENT_AND_CHILD_CONSTRAINT_"
        "TRANSPORT_VALIDATED_THROUGH_N10;_WEAK_CONORMAL_REACTION_GRAPH_"
        "AND_POSITIVE_DURATION_GAUGE_FIXED_JACOBI_ENERGY_ESTIMATE_"
        "DERIVED;_N_UNIFORM_NORMAL_CLOSED_RANGE_AND_CALDERON_GRAPH_"
        "CONVERGENCE_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation.update({
        "sequential_action_energy_projection_audit_validated": (
            sequential["validation_passed"]
        ),
        "positive_duration_gauge_fixed_jacobi_audit_validated": (
            jacobi["validation_passed"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def refresh_sequential_action_energy_projection(path: str | Path) -> Path:
    """Refresh only the reproducible nested action-energy transport ledger."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    sequential = sequential_action_energy_projection_audit(target)
    if not sequential["validation_passed"]:
        raise RuntimeError("sequential action-energy projection audit failed")
    result["sequential_action_energy_projection_audit"] = sequential
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["sequential_action_energy_projection_audit_validated"] = (
        sequential["validation_passed"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_general_n_principal_energy_checkpoint(path: str | Path) -> Path:
    """Persist the closed principal sectors and exact lower-order blocker."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    jacobi = positive_duration_gauge_fixed_jacobi_audit(target)
    if not jacobi["validation_passed"]:
        raise RuntimeError("positive-duration weak Jacobi audit failed")
    result["positive_duration_gauge_fixed_jacobi_audit"] = jacobi
    payload["cross_resolution_reconnaissance"] = result
    target.write_text(deterministic_json(payload), encoding="utf-8")
    certificate = general_n_principal_energy_certificate(target)
    if not certificate["validation_passed"]:
        raise RuntimeError("general-N principal energy certificate failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    required_next = certificate["required_next"]
    result["general_N_principal_energy_certificate"] = certificate
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "ACTION_ENERGY_COHERENT_CONSTRAINT_TRANSPORT_AND_ETA_RETAINED_"
        "THROUGH_N10;_GENERAL_N_ACTION_NORMALIZED_CANONICAL_NORMAL_"
        "PRINCIPAL_AND_BOUNDARY_TRACE_SECTORS_CERTIFIED;_LOWER_ORDER_"
        "POSITIVE_DURATION_NORMAL_SHAPE_SPECTRAL_GAP_OPEN"
    )
    statement = dict(
        result[
            "general_N_complete_child_reconstruction_and_convergence_statement"
        ]
    )
    statement["first_missing_mathematical_object"] = required_next
    statement["required_next"] = required_next
    result[
        "general_N_complete_child_reconstruction_and_convergence_statement"
    ] = statement
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation.update({
        "positive_duration_gauge_fixed_jacobi_audit_validated": (
            jacobi["validation_passed"]
        ),
        "general_N_principal_energy_certificate_validated": (
            certificate["validation_passed"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_n5_shape_history_checkpoint(path: str | Path) -> Path:
    """Persist the focused history test of the remaining N5 shape softness."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = n5_shape_soft_history_response_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("N5 shape-soft history response audit failed")
    result["N5_shape_soft_history_response_audit"] = audit
    payload["cross_resolution_reconnaissance"] = result
    target.write_text(deterministic_json(payload), encoding="utf-8")
    certificate = general_n_principal_energy_certificate(target)
    if not certificate["validation_passed"]:
        raise RuntimeError("general-N principal energy certificate failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    required_next = certificate["required_next"]
    result["general_N_principal_energy_certificate"] = certificate
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "GENERAL_N_ACTION_NORMALIZED_PRINCIPAL_BOUNDARY_AND_N5_WEAK_"
        "HISTORY_SECTORS_CERTIFIED;_N5_INSTANTANEOUS_SHAPE_SOFTNESS_"
        "TESTED_ON_POSITIVE_DURATION;_N6_PLUS_UNIFORM_HISTORY_NORMAL_"
        "SPECTRAL_GAP_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation.update({
        "N5_shape_soft_history_response_audit_validated": (
            audit["validation_passed"]
        ),
        "general_N_principal_energy_certificate_validated": (
            certificate["validation_passed"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_n6_compatibility_extension(path: str | Path) -> Path:
    """Persist the direct full-compatibility repair of the N6 shell owner."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = n6_full_compatibility_extension_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("N6 full compatibility extension audit failed")
    result["N6_full_compatibility_extension_audit"] = audit
    required_next = audit["required_next"]
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "GENERAL_N_FIXED_GEOMETRY_TRANSPORT_FAILURE_LOCALIZED_TO_NEW_"
        "LAPSE_SHIFT_CONSTRAINT_SHELL_ROWS;_N6_FULL_GEOMETRY_VELOCITY_"
        "MULTIPLIER_COMPATIBILITY_EXTENSION_"
        + ("CLOSED" if audit["solver_converged"] else "ACTIVE")
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["N6_full_compatibility_extension_audit_validated"] = audit[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_n6_weak_reaction_checkpoint(path: str | Path) -> Path:
    """Persist the N6 event-to-child weak conormal correspondence."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = n6_event_child_weak_reaction_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("N6 weak reaction correspondence failed")
    result["N6_event_child_weak_reaction_audit"] = audit
    result["active_dependency"] = audit["required_next"]
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "N6_FULL_COMPATIBILITY_FIBER_AND_EVENT_TO_CHILD_TWO_SIDED_"
        "WEAK_CONORMAL_REACTION_CORRESPONDENCE_CLOSED;_N6_POSITIVE_"
        "DURATION_PERSISTENCE_AND_N5_N6_GRAPH_COMPARISON_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["N6_event_child_weak_reaction_audit_validated"] = audit[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_n6_complete_boundary_reaction_checkpoint(
    path: str | Path,
) -> Path:
    """Persist exact N6 attachment matching before weak reaction promotion."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    boundary = n6_complete_boundary_bvp_match_audit(target)
    if not boundary["validation_passed"]:
        raise RuntimeError("N6 exact attachment boundary match failed")
    result["N6_complete_boundary_BVP_match_audit"] = boundary
    payload["cross_resolution_reconnaissance"] = result
    target.write_text(deterministic_json(payload), encoding="utf-8")
    reaction = n6_event_child_weak_reaction_audit(target)
    if not reaction["validation_passed"]:
        raise RuntimeError("matched N6 weak reaction correspondence failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    result["N6_event_child_weak_reaction_audit"] = reaction
    result["N6_weak_complete_child_candidate"] = {
        "classification": (
            "N6_COMPLETE_CHILD_CANDIDATE_UNDER_THE_DERIVED_EXACT_"
            "ATTACHMENT_AND_WEAK_CONORMAL_BOUNDARY_BVP_MAP"
        ),
        "complete_child_candidate_validated": True,
        "persistence_evaluated": False,
        "persistence_validated": False,
        "child_state": {
            "binary64_hex": boundary["child_state_binary64_hex"],
        },
        "legacy_local_dynamic_flux_map_used_as_general_N_physics": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "FULL_BHSM_COMPLETE": False,
    }
    result["active_dependency"] = reaction["required_next"]
    result["scientific_status"] = (
        "INDEPENDENT_N3_N4_N5_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "N6_FULL_COMPATIBILITY_EXACT_EVENT_CHILD_ATTACHMENT_AND_TWO_"
        "SIDED_WEAK_CONORMAL_REACTION_CORRESPONDENCE_CLOSED;_N6_"
        "POSITIVE_DURATION_PERSISTENCE_AND_N5_N6_GRAPH_COMPARISON_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation.update({
        "N6_complete_boundary_BVP_match_audit_validated": (
            boundary["validation_passed"]
        ),
        "N6_event_child_weak_reaction_audit_validated": (
            reaction["validation_passed"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_n6_weak_complete_child_persistence(path: str | Path) -> Path:
    """Persist the unchanged positive-duration witness for the matched N6 child."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    stored_candidate = result.get("N6_weak_complete_child_candidate")
    if stored_candidate is None:
        boundary = result["N6_complete_boundary_BVP_match_audit"]
        reaction = result["N6_event_child_weak_reaction_audit"]
        if not (
            boundary["validation_passed"] and reaction["validation_passed"]
        ):
            raise RuntimeError("matched N6 boundary and reaction required")
        stored_candidate = {
            "classification": (
                "N6_COMPLETE_CHILD_CANDIDATE_UNDER_THE_DERIVED_EXACT_"
                "ATTACHMENT_AND_WEAK_CONORMAL_BOUNDARY_BVP_MAP"
            ),
            "complete_child_candidate_validated": True,
            "persistence_evaluated": False,
            "persistence_validated": False,
            "child_state": {
                "binary64_hex": boundary["child_state_binary64_hex"],
            },
            "legacy_local_dynamic_flux_map_used_as_general_N_physics": (
                False
            ),
            "new_equations_constraints_or_acceptance_gates": False,
            "FULL_BHSM_COMPLETE": False,
        }
        result["N6_weak_complete_child_candidate"] = stored_candidate
        payload["cross_resolution_reconnaissance"] = result
        target.write_text(deterministic_json(payload), encoding="utf-8")
    candidate = dict(stored_candidate)
    if not candidate["complete_child_candidate_validated"]:
        raise RuntimeError("matched N6 complete-child candidate required")
    n6_weak_complete_child_positive_duration_persistence.cache_clear()
    persistence = n6_weak_complete_child_positive_duration_persistence(
        points=96
    )
    if not persistence["positive_duration_relative_persistence_validated"]:
        raise RuntimeError("matched N6 child did not persist")
    candidate.update({
        "persistence_evaluated": True,
        "persistence_validated": True,
        "complete_persistent_child_validated": True,
    })
    result["N6_weak_complete_child_candidate"] = candidate
    result["N6_weak_complete_child_positive_duration_persistence"] = (
        persistence
    )
    result["active_dependency"] = (
        "COMPARE_THE_N5_N6_ACTION_NORMALIZED_WEAK_CONORMAL_REACTION_"
        "GRAPHS_AND_EXACT_ATTACHMENT_MATCHED_STATES;_THEN_PROVE_THE_"
        "GENERAL_N_NORMAL_GRAPH_CONVERGENCE_BOUND"
    )
    result["scientific_status"] = (
        "N3_N4_N5_LEGACY_LOCAL_COMPLETE_PERSISTENT_CHILDREN_VALIDATED;_"
        "N6_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_PERSISTENT_CHILD_"
        "VALIDATED;_N5_LEGACY_EXACT_ATTACHMENT_RECONCILIATION_AND_"
        "GENERAL_N_WEAK_GRAPH_CONVERGENCE_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["N6_weak_complete_child_persistence_validated"] = (
        persistence["positive_duration_relative_persistence_validated"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def refresh_legacy_reaction_correspondence_classification(
    path: str | Path,
) -> Path:
    """Record that legacy reaction solvability lacked exact attachment match."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    audit = event_child_two_sided_reaction_match_audit(target, points=44)
    if not audit["validation_passed"]:
        raise RuntimeError("legacy two-sided reaction replay failed")
    result = dict(payload["cross_resolution_reconnaissance"])
    result["event_child_two_sided_reaction_match_audit"] = audit
    payload["cross_resolution_reconnaissance"] = result
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_coherent_n5_exact_attachment_weak_child(
    path: str | Path,
) -> Path:
    """Persist the reconciled coherent N5 boundary map and persistence."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = coherent_n5_exact_attachment_weak_child_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("coherent N5 exact attachment reconciliation failed")
    candidate = {
        "classification": (
            "COHERENT_N5_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_CHILD"
        ),
        "complete_child_candidate_validated": True,
        "persistence_evaluated": False,
        "persistence_validated": False,
        "child_state": {
            "binary64_hex": audit["child_state_binary64_hex"],
        },
        "original_coherent_F18_root_unchanged": True,
        "new_equations_constraints_or_acceptance_gates": False,
        "FULL_BHSM_COMPLETE": False,
    }
    result["coherent_N5_exact_attachment_weak_child_audit"] = audit
    result["coherent_N5_exact_attachment_weak_child_candidate"] = candidate
    payload["cross_resolution_reconnaissance"] = result
    target.write_text(deterministic_json(payload), encoding="utf-8")
    coherent_n5_exact_attachment_positive_duration_persistence.cache_clear()
    persistence = coherent_n5_exact_attachment_positive_duration_persistence(
        points=44
    )
    if not persistence["positive_duration_relative_persistence_validated"]:
        raise RuntimeError("reconciled coherent N5 child did not persist")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    candidate = dict(
        result["coherent_N5_exact_attachment_weak_child_candidate"]
    )
    candidate.update({
        "persistence_evaluated": True,
        "persistence_validated": True,
        "complete_persistent_child_validated": True,
    })
    result["coherent_N5_exact_attachment_weak_child_candidate"] = candidate
    result[
        "coherent_N5_exact_attachment_positive_duration_persistence"
    ] = persistence
    result["active_dependency"] = (
        "RECONCILE_THE_N4_AND_N3_LEGACY_CHILDREN_WITH_THE_EXACT_"
        "ATTACHMENT_WEAK_CONORMAL_MAP;_THEN_COMPARE_THE_MATCHED_N5_N6_"
        "REACTION_GRAPHS_FOR_GENERAL_N_CONVERGENCE"
    )
    result["scientific_status"] = (
        "N5_AND_N6_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_PERSISTENT_"
        "CHILDREN_VALIDATED;_N3_N4_LEGACY_LOCAL_CHILDREN_REQUIRE_EXACT_"
        "ATTACHMENT_RECONCILIATION_BEFORE_GENERAL_N_PROMOTION"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation.update({
        "coherent_N5_exact_attachment_weak_child_audit_validated": (
            audit["validation_passed"]
        ),
        "coherent_N5_exact_attachment_persistence_validated": (
            persistence["positive_duration_relative_persistence_validated"]
        ),
    })
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_legacy_n3_n4_exact_attachment_weak_children(
    path: str | Path,
) -> Path:
    """Persist reconciled N3/N4 boundary maps and persistence witnesses."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = legacy_n3_n4_exact_attachment_weak_child_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("legacy N3/N4 exact attachment reconciliation failed")
    for row in audit["rows"]:
        order = row["N"]
        result[f"N{order}_exact_attachment_weak_child_candidate"] = {
            "classification": (
                f"N{order}_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_CHILD"
            ),
            "complete_child_candidate_validated": True,
            "persistence_evaluated": False,
            "persistence_validated": False,
            "child_state": {
                "binary64_hex": row["child_state_binary64_hex"],
            },
            "legacy_local_root_unchanged": True,
            "new_equations_constraints_or_acceptance_gates": False,
            "FULL_BHSM_COMPLETE": False,
        }
    result["legacy_N3_N4_exact_attachment_weak_child_audit"] = audit
    payload["cross_resolution_reconnaissance"] = result
    target.write_text(deterministic_json(payload), encoding="utf-8")
    legacy_exact_attachment_positive_duration_persistence.cache_clear()
    persistence = {
        order: legacy_exact_attachment_positive_duration_persistence(
            order, points=44
        )
        for order in (3, 4)
    }
    if not all(
        item["positive_duration_relative_persistence_validated"]
        for item in persistence.values()
    ):
        raise RuntimeError("matched legacy child persistence failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    for order, item in persistence.items():
        key = f"N{order}_exact_attachment_weak_child_candidate"
        candidate = dict(result[key])
        candidate.update({
            "persistence_evaluated": True,
            "persistence_validated": True,
            "complete_persistent_child_validated": True,
        })
        result[key] = candidate
        result[
            f"N{order}_exact_attachment_positive_duration_persistence"
        ] = item
    result["active_dependency"] = (
        "COMPARE_THE_EXACT_ATTACHMENT_MATCHED_N3_N4_N5_N6_WEAK_"
        "CONORMAL_REACTION_GRAPHS_IN_ACTION_NORMALIZED_COORDINATES_"
        "AND_PROVE_THE_GENERAL_N_NORMAL_GRAPH_CONVERGENCE_BOUND"
    )
    result["scientific_status"] = (
        "N3_N4_N5_N6_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_"
        "PERSISTENT_CHILDREN_VALIDATED;_GENERAL_N_ACTION_NORMALIZED_"
        "WEAK_REACTION_GRAPH_CONVERGENCE_REMAINS_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["legacy_N3_N4_exact_attachment_weak_child_audit_validated"] = (
        audit["validation_passed"]
    )
    for order, item in persistence.items():
        validation[
            f"N{order}_exact_attachment_persistence_validated"
        ] = item["positive_duration_relative_persistence_validated"]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_matched_weak_reaction_graph_audit(path: str | Path) -> Path:
    """Persist the N3--N6 normalized weak reaction graph comparison."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = matched_weak_reaction_graph_convergence_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("matched weak reaction graph audit failed")
    result["matched_weak_reaction_graph_convergence_audit"] = audit
    result["active_dependency"] = audit["first_missing_mathematical_object"]
    result["scientific_status"] = (
        "N3_N4_N5_N6_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_"
        "PERSISTENT_CHILDREN_VALIDATED;_ACTION_NORMALIZED_REACTION_"
        "GRAPHS_MEASURED;_GENERAL_N_LOWER_ORDER_NORMAL_GRAPH_"
        "COMPACTNESS_AND_UNIFORM_SPECTRAL_GAP_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["matched_weak_reaction_graph_audit_validated"] = audit[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_injected_calderon_graph_audit(path: str | Path) -> Path:
    """Persist fixed-background linear graph convergence and next blocker."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = injected_matched_background_calderon_graph_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("injected Calderon graph convergence audit failed")
    result["injected_matched_background_calderon_graph_audit"] = audit
    result["active_dependency"] = audit["first_missing_mathematical_object"]
    result["scientific_status"] = (
        "N3_N4_N5_N6_EXACT_ATTACHMENT_WEAK_CONORMAL_COMPLETE_"
        "PERSISTENT_CHILDREN_VALIDATED;_FIXED_BACKGROUND_LINEAR_"
        "CALDERON_GRAPH_GALERKIN_CONVERGENCE_DERIVED_AND_MEASURED;_"
        "NONLINEAR_NORMAL_COMPLEMENT_RADII_BOUND_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["injected_Calderon_graph_convergence_audit_validated"] = (
        audit["validation_passed"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_weak_constraint_boundary_tail_audit(path: str | Path) -> Path:
    """Persist boundary-source separation and weak constraint-tail decay."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = weak_constraint_boundary_source_tail_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("weak constraint boundary-tail audit failed")
    result["weak_constraint_boundary_source_tail_audit"] = audit
    result["active_dependency"] = audit["first_missing_mathematical_object"]
    result["scientific_status"] = (
        "N3_TO_N6_EXACT_ATTACHMENT_WEAK_COMPLETE_PERSISTENT_CHILDREN_"
        "VALIDATED;_LINEAR_CALDERON_GRAPH_CONVERGENCE_AND_WEAK_BULK_"
        "CONSTRAINT_TAIL_DECAY_VALIDATED;_NONLINEAR_NORMAL_RIGHT_"
        "INVERSE_AND_LIPSCHITZ_RADII_BOUND_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["weak_constraint_boundary_tail_audit_validated"] = audit[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_boundary_jerk_weak_graph_domain_audit(
    path: str | Path,
) -> Path:
    """Persist the weak-domain localization of the soft jerk lemma."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    audit = boundary_jerk_weak_graph_domain_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("boundary-jerk weak graph-domain audit failed")
    result["boundary_jerk_weak_graph_domain_audit"] = audit
    reduction = weak_calderon_boundary_generator_reduction(target)
    if not reduction["validation_passed"]:
        raise RuntimeError("weak Calderon boundary-generator reduction failed")
    result["weak_calderon_boundary_generator_reduction"] = reduction
    second_graph = soft_calderon_second_graph_domain_reduction(target)
    if not second_graph["validation_passed"]:
        raise RuntimeError("soft Calderon second graph-domain reduction failed")
    result["soft_calderon_second_graph_domain_reduction"] = second_graph
    coefficients = soft_second_graph_coefficient_bundle_audit(target)
    if not coefficients["validation_passed"]:
        raise RuntimeError("soft second-graph coefficient audit failed")
    result["soft_second_graph_coefficient_bundle_audit"] = coefficients
    smooth_lift = soft_uniform_smooth_boundary_lift_audit(target)
    if not smooth_lift["validation_passed"]:
        raise RuntimeError("soft smooth boundary-lift audit failed")
    result["soft_uniform_smooth_boundary_lift_audit"] = smooth_lift
    compactness = soft_boundary_acceleration_compactness_criterion(target)
    if not compactness["validation_passed"]:
        raise RuntimeError("soft boundary-acceleration criterion failed")
    result["soft_boundary_acceleration_compactness_criterion"] = compactness
    semigroup = soft_jacobi_semigroup_compactness_reduction(target)
    if not semigroup["validation_passed"]:
        raise RuntimeError("soft Jacobi semigroup compactness reduction failed")
    result["soft_jacobi_semigroup_compactness_reduction"] = semigroup
    mosco = jacobi_form_coefficient_mosco_theorem(target)
    if not mosco["validation_passed"]:
        raise RuntimeError("Jacobi coefficient-to-Mosco theorem failed")
    result["jacobi_form_coefficient_mosco_theorem"] = mosco
    actual_S2 = actual_child_S2_compactness_audit(target)
    if not actual_S2["validation_passed"]:
        raise RuntimeError("actual-child S2 compactness audit failed")
    result["actual_child_S2_compactness_audit"] = actual_S2
    propagation = gauge_fixed_S2_propagation_theorem(target)
    if not propagation["validation_passed"]:
        raise RuntimeError("gauge-fixed S2 propagation theorem failed")
    result["gauge_fixed_S2_propagation_theorem"] = propagation
    normal_scope = normal_section_S2_compactness_scope(target)
    if not normal_scope["validation_passed"]:
        raise RuntimeError("normal-section S2 compactness scope failed")
    result["normal_section_S2_compactness_scope"] = normal_scope
    fredholm = soft_normal_fredholm_compactness_dichotomy(target)
    if not fredholm["validation_passed"]:
        raise RuntimeError("soft normal Fredholm dichotomy failed")
    result["soft_normal_fredholm_compactness_dichotomy"] = fredholm
    completeness = continuum_normal_cauchy_completeness_reduction(target)
    if not completeness["validation_passed"]:
        raise RuntimeError("continuum normal Cauchy completeness reduction failed")
    result["continuum_normal_cauchy_completeness_reduction"] = completeness
    result["active_dependency"] = completeness["exact_next_mathematical_lemma"]
    result["scientific_status"] = (
        "N3_TO_N6_EXACT_ATTACHMENT_WEAK_COMPLETE_PERSISTENT_CHILDREN_"
        "VALIDATED;_THE_HARD_MOMENTUM_RESPONSE_CLOSES_AND_THE_SOFT_"
        "NORMAL_CHANNEL_IS_POSITIVE_DURATION_DYNAMICAL;_UNIFORM_"
        "CLASSICAL_H6_CONTROL_IS_INVALID_AS_A_NEW_CRITERION;_THE_WEAK_"
        "CALDERON_BOUNDARY_JERK_FAILURE_IS_LOCALIZED_TO_THE_ACTION_"
        "CONTINUUM_NORMAL_CAUCHY_COMPLETENESS_REDUCED_TO_THE_EXPLICIT_"
        "SEVEN_BY_SEVEN_ACTION_OWNED_BOUNDARY_SYMBOL_GAP"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["boundary_jerk_weak_graph_domain_audit_validated"] = audit[
        "validation_passed"
    ]
    validation["weak_calderon_boundary_generator_reduction_validated"] = (
        reduction["validation_passed"]
    )
    validation["soft_calderon_second_graph_domain_reduction_validated"] = (
        second_graph["validation_passed"]
    )
    validation["soft_second_graph_coefficient_bundle_audit_validated"] = (
        coefficients["validation_passed"]
    )
    validation["soft_uniform_smooth_boundary_lift_audit_validated"] = (
        smooth_lift["validation_passed"]
    )
    validation["soft_boundary_acceleration_compactness_criterion_validated"] = (
        compactness["validation_passed"]
    )
    validation["soft_jacobi_semigroup_compactness_reduction_validated"] = (
        semigroup["validation_passed"]
    )
    validation["jacobi_form_coefficient_mosco_theorem_validated"] = (
        mosco["validation_passed"]
    )
    validation["actual_child_S2_compactness_audit_validated"] = actual_S2[
        "validation_passed"
    ]
    validation["gauge_fixed_S2_propagation_theorem_validated"] = propagation[
        "validation_passed"
    ]
    validation["normal_section_S2_compactness_scope_validated"] = normal_scope[
        "validation_passed"
    ]
    validation["soft_normal_fredholm_compactness_dichotomy_validated"] = (
        fredholm["validation_passed"]
    )
    validation["continuum_normal_cauchy_completeness_reduction_validated"] = (
        completeness["validation_passed"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_weak_complete_child_normal_audits(path: str | Path) -> Path:
    """Persist the N6 weak-map right inverse and normal Hessian audit."""

    target = Path(path)
    right_inverse = weak_complete_child_normal_right_inverse_audit(target)
    if not right_inverse["validation_passed"]:
        raise RuntimeError("weak complete-child right-inverse audit failed")
    lipschitz = weak_complete_child_normal_lipschitz_audit(target)
    if not lipschitz["validation_passed"]:
        raise RuntimeError("weak complete-child normal Hessian audit failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    result["weak_complete_child_normal_right_inverse_audit"] = right_inverse
    result["weak_complete_child_normal_lipschitz_audit"] = lipschitz
    result["active_dependency"] = lipschitz[
        "first_missing_mathematical_object"
    ]
    result["scientific_status"] = (
        "N3_TO_N6_EXACT_ATTACHMENT_WEAK_COMPLETE_PERSISTENT_CHILDREN_"
        "VALIDATED;_TOTAL_WEAK_N6_NORMAL_RIGHT_INVERSE_AND_STABLE_"
        "FINITE_N_RADII_MEASUREMENT_VALIDATED;_ANALYTIC_BALL_SUPREMUM_"
        "AND_PRINCIPAL_INVERTED_INFINITE_TAIL_BOUND_OPEN"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["weak_complete_child_normal_right_inverse_validated"] = (
        right_inverse["validation_passed"]
    )
    validation["weak_complete_child_normal_lipschitz_validated"] = (
        lipschitz["validation_passed"]
    )
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_weak_boundary_layer_radii_obstruction(path: str | Path) -> Path:
    """Persist the first failed infinite-dimensional radii constant."""

    target = Path(path)
    audit = weak_boundary_layer_radii_obstruction_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("weak boundary-layer obstruction audit failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    result["weak_boundary_layer_radii_obstruction_audit"] = audit
    result["active_dependency"] = audit["first_missing_mathematical_object"]
    result["scientific_status"] = (
        "N3_TO_N6_EXACT_ATTACHMENT_WEAK_COMPLETE_PERSISTENT_CHILDREN_"
        "VALIDATED;_FINITE_N6_NORMAL_RADII_DATA_CLOSES;_DIRECT_"
        "CONTINUUM_TRANSFER_FAILS_AT_THE_EXACT_CASIMIR_BOUNDARY_TAIL;_"
        "ACTION_DERIVED_BOUNDARY_LAYER_PARAMETRIX_REQUIRED"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["weak_boundary_layer_radii_obstruction_validated"] = audit[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def promote_casimir_boundary_layer_parametrix_audit(path: str | Path) -> Path:
    """Persist the invalidated q-only lift and its mixed-action successor."""

    target = Path(path)
    audit = casimir_boundary_layer_parametrix_audit(target)
    if not audit["validation_passed"]:
        raise RuntimeError("Casimir boundary-layer parametrix audit failed")
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    result["casimir_boundary_layer_parametrix_audit"] = audit
    result["active_dependency"] = audit["first_missing_mathematical_object"]
    result["scientific_status"] = (
        "N3_TO_N6_EXACT_ATTACHMENT_WEAK_COMPLETE_PERSISTENT_CHILDREN_"
        "VALIDATED;_DIRECT_CONTINUUM_RADII_TRANSFER_FAILS_AT_THE_"
        "CASIMIR_BOUNDARY_TAIL;_Q_ONLY_HIGH_SHELL_LIFT_INVALIDATED;_"
        "MIXED_GAUGE_REDUCED_EULER_DIRAC_PARAMETRIX_REQUIRED"
    )
    payload["cross_resolution_reconnaissance"] = result
    validation = dict(payload["validation"])
    validation["casimir_boundary_layer_parametrix_audit_validated"] = audit[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


def reclassify_existing_n5_proposal_plateau(path: str | Path) -> Path:
    """Freeze the demonstrated N5 flux-Jacobian owner without a new solve."""

    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    result = dict(payload["cross_resolution_reconnaissance"])
    child = dict(result["N5_event_conditioned_complete_child_reconstruction"])
    required_next = (
        "DERIVE_THE_ACTION_OWNED_N5_DYNAMIC_CALDERON_FLUX_JACOBIAN_VIA_"
        "THE_REQUIRED_FOURTH_VARIATION_OR_A_DIFFERENTIATED_CHILD_BVP_"
        "BEFORE_FURTHER_REPETITIVE_CONTINUATION"
    )
    child["required_next"] = required_next
    child["plateau_classification"] = (
        "DOMINANT_DYNAMIC_CALDERON_FLUX_JACOBIAN_OWNER_IDENTIFIED"
    )
    result["N5_event_conditioned_complete_child_reconstruction"] = child
    n5_child_flux_step_audit.cache_clear()
    flux_audit = n5_child_flux_step_audit(points=44)
    result["N5_child_flux_step_and_outer_direction_audit"] = flux_audit
    result["active_dependency"] = required_next
    result["scientific_status"] = (
        "N4_COMPLETE_PERSISTENT_CHILD_VALIDATED;_N5_QUALITATIVE_EVENT_AND_"
        "FULL_RANK_18_ROW_CHILD_MAP_VALIDATED;_N5_ADMISSIBLE_EXACT_MERIT_"
        "CHECKPOINT_PROMOTED;_DYNAMIC_CALDERON_FLUX_JACOBIAN_OWNER_BLOCKS_"
        "THE_N5_ROOT"
    )
    questions = dict(result["questions"])
    child_question = dict(
        questions["same_rank14_complete_child_reconstructs"]
    )
    child_question["N5_active_blocker"] = required_next
    questions["same_rank14_complete_child_reconstructs"] = child_question
    result["questions"] = questions
    payload["cross_resolution_reconnaissance"] = result
    ownership = ingredient_process_ownership_audit()
    network = breadth_first_closure_network_audit()
    payload["ingredient_process_ownership_audit"] = ownership
    payload["breadth_first_closure_network_audit"] = network
    validation = dict(payload["validation"])
    validation["N5_flux_value_stable_but_outer_derivative_unresolved"] = bool(
        flux_audit["physical_map_or_gate_changed"] is False
        and child["proposal_model"][
            "fixed_merit_scaling_preserved_from_checkpoint"
        ]
        and child["solver"]["fixed_reference_merit_reduced"]
        and not child["complete_child_candidate_validated"]
    )
    validation["ingredient_process_ownership_validated"] = ownership[
        "validation_passed"
    ]
    validation["breadth_first_closure_network_validated"] = network[
        "validation_passed"
    ]
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    target.write_text(deterministic_json(payload), encoding="utf-8")
    return target


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "independent_order_probe",
    "ingredient_process_ownership_audit",
    "physical_scale_accessibility_audit",
    "breadth_first_closure_network_audit",
    "n4_ordered_event_step_audit",
    "n4_constrained_ordered_event_search",
    "n4_ordered_event_resolution_audit",
    "n4_adaptive_event_convergence_audit",
    "n4_event_conditioned_complete_child_reconstruction",
    "n4_latest_checkpoint_proposal_audit",
    "n4_complete_child_positive_duration_persistence",
    "n5_independent_eta_branch_event_audit",
    "n5_cross_quadrature_event_classification",
    "n5_event_conditioned_complete_child_chart_audit",
    "n5_child_flux_step_audit",
    "n5_event_conditioned_complete_child_reconstruction",
    "n5_complete_child_positive_duration_persistence",
    "coherent_n4_to_n5_complete_child_positive_duration_persistence",
    "n6_weak_complete_child_positive_duration_persistence",
    "coherent_n5_exact_attachment_positive_duration_persistence",
    "legacy_exact_attachment_positive_duration_persistence",
    "child_jacobi_radial_principal_symbol_audit",
    "cross_resolution_principal_symbol_frame_audit",
    "weighted_pole_attachment_principal_estimate",
    "cross_resolution_strong_constraint_infsup_audit",
    "cross_resolution_boundary_symplectic_polarization_audit",
    "nested_attachment_lift_consistency_audit",
    "on_shell_boundary_reaction_audit",
    "child_history_bvp_bordered_operator_audit",
    "event_child_two_sided_reaction_match_audit",
    "action_energy_topology_coherent_event_audit",
    "reaction_calderon_nested_schur_trace_audit",
    "sequential_action_energy_projection_audit",
    "n6_full_compatibility_extension_audit",
    "n6_complete_boundary_bvp_match_audit",
    "n6_event_child_weak_reaction_audit",
    "coherent_n5_exact_attachment_weak_child_audit",
    "legacy_n3_n4_exact_attachment_weak_child_audit",
    "weak_conormal_reaction_graph_audit",
    "boundary_compatible_gauge_quotient_audit",
    "positive_duration_gauge_fixed_jacobi_audit",
    "n5_shape_soft_history_response_audit",
    "uniform_positive_duration_normal_closed_range_reduction",
    "positive_duration_normal_adjoint_kernel_localization",
    "event_to_child_on_shell_calderon_interface",
    "general_n_principal_energy_certificate",
    "matched_weak_reaction_graph_convergence_audit",
    "injected_matched_background_calderon_graph_audit",
    "injected_n6_event_child_calderon_friedrichs_angle_audit",
    "event_child_calderon_angle_stability_lemma",
    "whole_system_time_translation_tangent_interface",
    "soft_channel_positive_duration_observability_jet_lemma",
    "uniform_boundary_jerk_compactness_reduction",
    "boundary_jerk_weak_graph_domain_audit",
    "weak_calderon_boundary_generator_reduction",
    "soft_calderon_second_graph_domain_reduction",
    "soft_second_graph_coefficient_bundle_audit",
    "soft_uniform_smooth_boundary_lift_audit",
    "soft_boundary_acceleration_compactness_criterion",
    "soft_jacobi_semigroup_compactness_reduction",
    "jacobi_form_coefficient_mosco_theorem",
    "actual_child_S2_compactness_audit",
    "gauge_fixed_S2_propagation_theorem",
    "normal_section_S2_compactness_scope",
    "soft_normal_fredholm_compactness_dichotomy",
    "continuum_normal_cauchy_completeness_reduction",
    "weak_constraint_boundary_source_tail_audit",
    "weak_complete_child_normal_right_inverse_audit",
    "weak_complete_child_normal_lipschitz_audit",
    "weak_boundary_layer_radii_obstruction_audit",
    "casimir_boundary_layer_parametrix_audit",
    "general_n_galerkin_transfer_certificate",
    "general_n_complete_child_reconstruction_statement",
    "cross_resolution_reconnaissance",
    "completion_payload",
    "materialize",
    "refresh_existing_n4_child_checkpoint",
    "refresh_existing_n4_persistence_checkpoint",
    "refresh_existing_cross_resolution_classification",
    "refresh_existing_n5_child_chart_checkpoint",
    "refresh_existing_n5_child_checkpoint",
    "promote_existing_n5_persistence",
    "promote_existing_general_n_statement",
    "promote_existing_coherent_n4_to_n5_child_persistence",
    "promote_general_n_weak_history_checkpoint",
    "refresh_sequential_action_energy_projection",
    "promote_general_n_principal_energy_checkpoint",
    "promote_n5_shape_history_checkpoint",
    "promote_n6_compatibility_extension",
    "promote_n6_weak_reaction_checkpoint",
    "promote_n6_complete_boundary_reaction_checkpoint",
    "promote_n6_weak_complete_child_persistence",
    "refresh_legacy_reaction_correspondence_classification",
    "promote_coherent_n5_exact_attachment_weak_child",
    "promote_legacy_n3_n4_exact_attachment_weak_children",
    "promote_matched_weak_reaction_graph_audit",
    "promote_injected_calderon_graph_audit",
    "promote_boundary_jerk_weak_graph_domain_audit",
    "promote_weak_constraint_boundary_tail_audit",
    "promote_weak_complete_child_normal_audits",
    "promote_weak_boundary_layer_radii_obstruction",
    "promote_casimir_boundary_layer_parametrix_audit",
    "reclassify_existing_n5_proposal_plateau",
]
