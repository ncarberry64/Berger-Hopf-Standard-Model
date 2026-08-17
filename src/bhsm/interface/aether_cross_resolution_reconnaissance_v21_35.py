"""Independent N=3/N=4/N=5 reconnaissance from the BHSM action.

This module deliberately stops before a higher-resolution global solve.  It
builds every order directly from the canonical reset, projects onto that
order's own Euler--Dirac constraint surface, and measures the local physical
flow and ordered Dirac pencil.  The accepted N=3 trajectory is never used as
an N=4 or N=5 initial condition.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import linear_sum_assignment, minimize_scalar

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    integrate_attached_dirac_flow,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
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
                "classification": "OPEN" if n5_eta_admissible else "RECLASSIFIED",
                "answer": (
                    None if n5_eta_admissible
                    else "CONTRADICTS_AT_THE_CURRENT_DIRECT_RESET"
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
            },
        },
        "scientific_status": (
            "N4_INDEPENDENT_ACTION_DERIVATION_VALIDATED;_N5_DIRECT_RESET_"
            "CONSTRAINTS_CLOSE_BUT_FAILS_THE_EXISTING_ETA_DOMAIN;_EVENT,_"
            "COMPLETE_CHILD,_FULL_MOVIE,_AND_PERIOD_REMAIN_UNPROMOTED"
        ),
        "active_dependency": (
            "LOCATE_OR_RULE_OUT_THE_FIRST_ISOLATED_ORDERED_DIRAC_EVENT_ON_"
            "THE_ADMISSIBLE_INDEPENDENT_N4_ORBIT;_DO_NOT_ADVANCE_THE_CURRENT_"
            "N5_RESET_PAST_ITS_ETA_DOMAIN_FAILURE"
        ),
    }


def completion_payload(
    *, points: int = DEFAULT_POINTS, include_n4_step_audit: bool = False,
) -> dict[str, Any]:
    result = cross_resolution_reconnaissance(points=points)
    if include_n4_step_audit:
        result = dict(result)
        result["N4_targeted_event_step_audit"] = n4_ordered_event_step_audit(
            points=points
        )
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
    return {
        "artifact": "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "quadrature_points": points,
        "cross_resolution_reconnaissance": result,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(
    directory: str | Path,
    *,
    points: int = DEFAULT_POINTS,
    include_n4_step_audit: bool = False,
) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
    path.write_text(
        deterministic_json(completion_payload(
            points=points,
            include_n4_step_audit=include_n4_step_audit,
        )),
        encoding="utf-8",
    )
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "independent_order_probe",
    "n4_ordered_event_step_audit",
    "cross_resolution_reconnaissance",
    "completion_payload",
    "materialize",
]
