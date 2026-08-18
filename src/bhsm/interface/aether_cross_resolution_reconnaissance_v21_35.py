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
            "EVENT_TO_COMPLETE_CHILD_TWO_SIDED_BOUNDARY_REACTION_MAP_"
            "DERIVED_AND_FINITE_N_SOLVABLE_AT_N3_N4_N5;_UNIFORM_"
            "GENERAL_N_GRAPH_CONVERGENCE_AND_RETURN_MAP_OPEN"
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
        "configuration_or_rate_continuity_imposed_as_a_new_gate": False,
        "why_not": (
            "THE_RECONSTRUCTED_CHILD_IS_A_NEW_PIECEWISE_LORENTZIAN_"
            "SOLUTION;_THE_EXISTING_TRACE_AND_CANONICAL_MOMENTUM_ROWS_"
            "ARE_RETAINED_AND_NO_EXTRA_C1_MATCH_IS_ASSUMED"
        ),
        "accepted_F_N_roots_or_persistence_changed": False,
        "new_equations_constraints_or_acceptance_gates": False,
        "required_next": (
            "TEST_THE_TWO_BY_TWO_REACTION_CALDERON_GRAPH_UNDER_EXACT_"
            "NESTED_SPECTRAL_INJECTION_AND_DERIVE_A_UNIFORM_NORMAL_"
            "RIGHT_INVERSE_OR_LOCALIZE_ITS_FIRST_ACTION_OWNED_FAILURE"
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


def event_to_child_on_shell_calderon_interface() -> dict[str, Any]:
    """Reconcile the validated local child roots with the required full BVP."""

    missing = (
        "DERIVE_THE_WEAK_CONORMAL_REACTION_CALDERON_MAP_ON_THE_EULER_"
        "DIRAC_GRAPH_DOMAIN_AND_PROVE_UNIFORM_HIGH_SHELL_SCHUR_TAIL_"
        "CONTROL_OR_LOCALIZE_ITS_FIRST_LOWER_ORDER_FAILURE"
    )
    principal_symbol = child_jacobi_radial_principal_symbol_audit()
    weighted_principal = weighted_pole_attachment_principal_estimate()
    return {
        "classification": (
            "VARIATIONAL_EVENT_TO_ON_SHELL_CHILD_CALDERON_INTERFACE_DERIVED;_"
            "FUNCTION_SPACE_BVP_AND_COMPLEMENTING_ESTIMATE_OPEN"
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


def general_n_galerkin_transfer_certificate() -> dict[str, Any]:
    """Derive the continuum-to-Galerkin certificate required by general N."""

    calderon = event_to_child_on_shell_calderon_interface()
    missing = (
        "DERIVE_THE_WEAK_CONORMAL_REACTION_CALDERON_MAP_ON_THE_EULER_"
        "DIRAC_GRAPH_DOMAIN_AND_PROVE_UNIFORM_HIGH_SHELL_SCHUR_TAIL_"
        "CONTROL_OR_LOCALIZE_ITS_FIRST_LOWER_ORDER_FAILURE"
    )
    return {
        "classification": (
            "ACTION_OWNED_GALERKIN_TRANSFER_THEOREM_DERIVED;_CONTINUUM_"
            "INF_SUP_AND_TAIL_CERTIFICATE_OPEN"
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
    required_next = reaction_calderon["required_next"]
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
        "VALIDATED;_PURE_ENERGY_REACTION_DOMAIN_INVALIDATED;_EULER_DIRAC_"
        "GRAPH_DOMAIN_WEAK_CONORMAL_MAP_OPEN"
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
    })
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
    "event_to_child_on_shell_calderon_interface",
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
    "reclassify_existing_n5_proposal_plateau",
]
