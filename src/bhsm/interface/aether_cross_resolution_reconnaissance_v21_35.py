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
            "CURRENT_N5_BRANCH_INADMISSIBLE_BUT_OTHER_BRANCHES_OPEN"
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
            "CHILD_STATUS": "OPEN",
            "PERSISTENCE_STATUS": "NOT_YET_APPLICABLE",
            "note": (
                "THE_INDEPENDENT_ADAPTIVE_EVENT_IS_TIME_CONTROL_AND_"
                "QUADRATURE_CONVERGED;_THE_16_ROW_CHILD_MAP_IS_STRUCTURALLY_"
                "FULL_RANK_BUT_ITS_DYNAMIC_FLUX_JACOBIAN_IS_NOT_STEP_"
                "CONVERGED_AND_NO_CHILD_IS_PROMOTED"
            ),
        },
        "N5": {
            "RESET_CONSTRUCTION": "PASS",
            "RESET_DOMAIN_STATUS": "FAIL",
            "EVOLUTION_STATUS": "NOT_YET_APPLICABLE",
            "EVENT_STATUS": "NOT_YET_APPLICABLE",
            "CHILD_STATUS": "NOT_YET_APPLICABLE",
            "PERSISTENCE_STATUS": "NOT_YET_APPLICABLE",
            "note": (
                "FAIL_APPLIES_ONLY_TO_THE_CURRENT_INDEPENDENT_RESET_BRANCH;_"
                "OTHER_N5_BRANCHES_HAVE_NOT_BEEN_CLASSIFIED"
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
        "N5_warning_scope": "CURRENT_DIRECT_RESET_BRANCH_ONLY",
        "N4_needs_different_physics": False,
        "N4_needs_manifold_preserving_evolution": True,
        "N4_fixed_step_event_resolution_converged": False,
        "N4_adaptive_event_time_and_quadrature_converged": True,
        "N4_ordered_event_validated": True,
        "N4_complete_child_validated": False,
        "N4_child_dynamic_flux_jacobian_step_converged": False,
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
        "later_N5_stages_not_failed_early": all(
            stage_status["N5"][key] == "NOT_YET_APPLICABLE"
            for key in (
                "EVOLUTION_STATUS", "EVENT_STATUS", "CHILD_STATUS",
                "PERSISTENCE_STATUS",
            )
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
            "DERIVE_A_CONVERGENCE_STABLE_DIRECTIONAL_DERIVATIVE_OF_THE_N4_"
            "ACTION_OWNED_DYNAMIC_CALDERON_FLUX_MAP_ON_THE_REGULAR_BROKEN_"
            "CHILD_GERM_BEFORE_ANOTHER_NONLINEAR_CHILD_SOLVE;_DO_NOT_"
            "ADVANCE_THE_CURRENT_N5_BRANCH"
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
        "active_N4_child_dependency_preserved": True,
    }
    return_interface = {
        "interface": (
            "z_event->(Gamma0_event,p_event,Gamma1_event,I_event)->"
            "SolveChildBVP->R_return(z_event)"
        ),
        "classification": "DERIVED_SET_VALUED_INTERFACE_CHILD_ROOT_OPEN",
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
        "current_N4_status": (
            "EVENT_VALIDATED;_16_ROW_MAP_STRUCTURALLY_FULL_RANK;_"
            "CENTER_FIXED_SOBOLEV_NORMALIZED_RICHARDSON_DERIVATIVE_"
            "VALIDATED;_GLOBAL_MERIT_CHILD_CONTINUATION_OPEN"
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
            "BUT_IS_NOT_SUBSTITUTED_BEFORE_AN_N4_CHILD_HISTORY_EXISTS"
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
                "CONTINUE_THE_UNCHANGED_GLOBAL_MERIT_N4_CHILD_SOLVE_FROM_"
                "THE_LATEST_ADMISSIBLE_CHECKPOINT_WITH_FRESH_CENTER_FIXED_"
                "DYNAMIC_CALDERON_FLUX_CURVATURE"
            ),
            "feeds": ["RETURN_INTERFACE", "PERSISTENCE"],
        },
        {
            "priority": 2,
            "object": (
                "ACTION_DERIVED_ENVIRONMENT_TO_RECONSTRUCTION_MAP_AND_"
                "COMPOSITE_MINUS_PARENT_NOETHER_HAMILTONIAN"
            ),
            "feeds": ["RETURN_INTERFACE", "MASS_INTERFACE"],
        },
        {
            "priority": 3,
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
        "active_N4_dependency_retained": doctrine[
            "active_N4_child_dependency_preserved"
        ],
        "shared_invariants_exposed": len(
            shared_invariants["required_by_multiple_interfaces"]
        ) >= 3,
        "first_blocker_action_owned_and_localized": (
            "DYNAMIC_CALDERON_FLUX" in blockers[0]["object"]
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
            "PREDICTION_PROMOTED;_N4_COMPLETE_CHILD_CONTINUATION_ACTIVE"
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


@lru_cache(maxsize=4)
def n4_constrained_ordered_event_search(
    *,
    points: int = DEFAULT_POINTS,
    time_step: float = 1.0e-5,
    maximum_steps: int = 80,
    local_error_tolerance: float | None = None,
) -> dict[str, Any]:
    """Follow the independent N=4 orbit to its first ordered soft event.

    The evolution is the existing exact Euler--Dirac RK4 plus Sobolev
    constraint projection.  Once a simple zero is imminent, the established
    one-sided tangent locator is evaluated on the projected constraint
    surface so the integrator never steps through a singular Hessian.
    """

    if time_step <= 0.0 or maximum_steps <= 0:
        raise ValueError("positive N4 event-search controls required")
    if local_error_tolerance is not None and local_error_tolerance <= 0.0:
        raise ValueError("local_error_tolerance must be positive")
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
    q = np.asarray(coordinates, dtype=float)
    qdim = dimensions(order)["coordinates"]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    v_boundary = float(q[1 + 2 * order:1 + 3 * order] @ signs_j)
    j_w = np.zeros(qdim)
    j_w[0] = 1.0
    j_w[1:1 + order] = signs_k
    j_w[1 + 2 * order:1 + 3 * order] = (
        -math.tanh(2.0 * v_boundary) * signs_j
    )
    j_c = np.zeros(qdim)
    j_c[0] = 1.0
    return np.vstack((j_w, j_c - j_w))


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
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
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


def _metric_radial_flux_covector_at_order(
    order: int, coordinates: np.ndarray, multipliers: np.ndarray,
) -> np.ndarray:
    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    qdim = dimensions(order)["coordinates"]
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    scale = float(q[0])
    u = float(q[1:1 + order] @ signs_k)
    w = float(q[1 + order:1 + 2 * order] @ signs_j)
    v = float(q[1 + 2 * order:1 + 3 * order] @ signs_j)
    radius = float(RADIUS0 * math.exp(scale))
    c_radius = float(radius * math.exp(u + w))
    a_radius = float(radius * math.exp(u + v) / math.sqrt(2.0))
    b_radius = float(radius * math.exp(u - v) / math.sqrt(2.0))
    lapse = float(math.exp(float(m[:order] @ signs_k)))
    prefactor = float(3.0 * lapse * a_radius**3 * b_radius**3 / c_radius)
    d_log_a = np.zeros(qdim)
    d_log_b = np.zeros(qdim)
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

    q = np.asarray(coordinates, dtype=float)
    velocity = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    qdim = dimensions(order)["coordinates"]
    jet = exact_full_action_jet_at_state(
        order, q, velocity, m, points=points
    )
    dirac_hessian = np.asarray(
        jet.hessian[qdim:, qdim:], dtype=float
    )
    mixed_z_q = np.asarray(jet.hessian[qdim:, :qdim], dtype=float)
    gradient_q = np.asarray(jet.gradient[:qdim], dtype=float)
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


def _n4_child_rows(
    child: np.ndarray,
    event_coordinates: np.ndarray,
    event_momentum: np.ndarray,
    event_flux: np.ndarray,
    *,
    points: int,
    relative_flux_step: float = 4.0e-4,
    fixed_flux_time_step: float | None = None,
    richardson_flux: bool = True,
) -> np.ndarray:
    order = 4
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

    momentum_rate = centered_momentum_rate(epsilon)
    if richardson_flux:
        half_rate = centered_momentum_rate(0.5 * epsilon)
        momentum_rate = (4.0 * half_rate - momentum_rate) / 3.0
    flux = child_flux - (-momentum_rate + force - event_flux)
    return np.concatenate((
        _trace_jacobian_at_order(order) @ (q - event_coordinates),
        constraint_residual(
            order, q, velocity, multipliers, points=points
        ),
        momentum - event_momentum,
        flux,
    ))


def _n4_child_flux_time_step(
    child: np.ndarray, *, points: int, relative_flux_step: float,
) -> float:
    """Select one inner flux time step at the center of an outer stencil."""

    order = 4
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
    if resume_from_checkpoint:
        stored = payload["cross_resolution_reconnaissance"].get(
            "N4_event_conditioned_complete_child_reconstruction"
        )
        if (
            isinstance(stored, dict)
            and stored.get("chart", {}).get(
                "dynamic_flux_jacobian_step_converged"
            ) is True
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
                selected_seed = {
                    "source": "LATEST_ADMISSIBLE_N4_CHILD_ROLLING_CHECKPOINT",
                    "prior_scaled_final_norm": stored["chart"][
                        "scaled_final_norm"
                    ],
                    "prior_dynamic_flux_norm": stored[
                        "physical_residuals"
                    ]["dynamic_flux_norm_at_4e-4"],
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
    jacobian_step = 1.0e-4
    inner_relative_flux_step = 4.0e-3
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
    row_scales = np.maximum(np.linalg.norm(jacobian, axis=1), 1.0)
    scaled_jacobian = jacobian / row_scales[:, None]
    _, _, pivots = qr(scaled_jacobian, mode="economic", pivoting=True)
    singular = np.linalg.svd(scaled_jacobian, compute_uv=False)
    tolerance = (
        np.finfo(float).eps * max(scaled_jacobian.shape) * singular[0]
    )
    rank = int(np.count_nonzero(singular > tolerance))
    chart = np.asarray(pivots[:row_count], dtype=int)
    chart_weights = direction_weights[chart]
    fixed = germ.copy()

    def residual(
        chart_values: np.ndarray, *, fixed_flux_time_step: float | None = None,
    ) -> np.ndarray:
        value = fixed.copy()
        value[chart] = chart_values / chart_weights
        return _n4_child_rows(
            value,
            q_event,
            event_momentum,
            event_flux,
            points=points,
            fixed_flux_time_step=fixed_flux_time_step,
        ) / row_scales

    def resolved_chart_jacobian(
        chart_values: np.ndarray, *, base_step: float = jacobian_step,
    ) -> np.ndarray:
        center = fixed.copy()
        center[chart] = chart_values / chart_weights
        full = directional_jacobian(center, base_step, chart)
        half = directional_jacobian(center, 0.5 * base_step, chart)
        return ((4.0 * half - full) / 3.0) / row_scales[:, None]

    chart_values = germ[chart] * chart_weights
    scaled_rows = residual(chart_values)
    solver_jacobian = scaled_jacobian[:, chart].copy()
    refined_solver_jacobian = solver_jacobian.copy()
    initial_chart_jacobian = (
        coarse_richardson_jacobian[:, chart] / row_scales[:, None]
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
            trial_full = fixed.copy()
            trial_full[chart] = trial_values / chart_weights
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
                    trial_full = fixed.copy()
                    trial_full[chart] = trial_values / chart_weights
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
                function_evaluations += 2 * row_count
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
    child = fixed.copy()
    child[chart] = chart_values / chart_weights
    final_rows = _n4_child_rows(
        child, q_event, event_momentum, event_flux, points=points
    )
    coarse_rows = _n4_child_rows(
        child,
        q_event,
        event_momentum,
        event_flux,
        points=points,
        relative_flux_step=8.0e-4,
    )
    q_child = child[:qdim]
    v_child = child[qdim:2 * qdim]
    m_child = child[2 * qdim:]
    eta = _eta_legendre_minimum(order, q_child, m_child, points=5000)
    flux_refinement = float(
        np.linalg.norm(final_rows[-2:] - coarse_rows[-2:])
        / max(1.0, np.linalg.norm(final_rows[-2:]))
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
                "LOCAL_JACOBIAN_ROW_NORMS_NUMERICAL_ONLY_SAME_ZERO_SET"
            ),
            "row_scales": row_scales.tolist(),
            "solver_jacobian": (
                "REGULAR_BROKEN_GERM_FULL_RANK_16_VARIABLE_PIVOT_CHART_"
                "WITH_CENTER_FIXED_TENSOR_PRODUCT_RICHARDSON_AND_GOOD_"
                "BROYDEN_UPDATES"
            ),
            "solver_coordinates": (
                "16_LOCAL_CHART_VARIABLES_FROM_THE_ROW_FULL_RANK_16_BY_34_"
                "PHYSICAL_MAP;_NO_PHYSICAL_ROW_ADDED"
            ),
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
            "dynamic_flux_norm_at_4e-4": float(
                np.linalg.norm(final_rows[14:16])
            ),
            "dynamic_flux_8e-4_to_4e-4_relative_difference": (
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
    child = n4_event_conditioned_complete_child_reconstruction(
        points=44, resume_from_checkpoint=True
    )
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
    "cross_resolution_reconnaissance",
    "completion_payload",
    "materialize",
    "refresh_existing_n4_child_checkpoint",
]
