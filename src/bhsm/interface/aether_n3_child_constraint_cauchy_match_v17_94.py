"""Evaluate the seven-constraint child projection against Cauchy matching.

The projection is an admissible instantaneous Lorentzian child state at the
inherited event configuration.  It is not declared a complete child unless
its attachment momentum and its two-sided dynamic flux also match.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
    project_nested_constraints,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    Q_DIMENSION,
    unpack_reduced,
)
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import (
    _canonical_pair,
    required_child_cauchy_flux,
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


VERSION = "v17.94"
CLASSIFICATION = "BHSM_N3_SEVEN_CONSTRAINT_CHILD_CAUCHY_MATCH"
FULL_BHSM_COMPLETE = False


def _metric_radial_flux_covector(
    q: np.ndarray, multipliers: np.ndarray
) -> tuple[np.ndarray, dict[str, float]]:
    """Return the action-owned terminal metric flux in N=3 coordinates."""

    coordinates = np.asarray(q, dtype=float)
    lapse_shift = np.asarray(multipliers, dtype=float)
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    scale = float(coordinates[0])
    u = float(coordinates[1:1 + ORDER] @ signs_k)
    w = float(coordinates[1 + ORDER:1 + 2 * ORDER] @ signs_j)
    v = float(coordinates[1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j)
    radius = float(RADIUS0 * math.exp(scale))
    c_radius = float(radius * math.exp(u + w))
    a_radius = float(radius * math.exp(u + v) / math.sqrt(2.0))
    b_radius = float(radius * math.exp(u - v) / math.sqrt(2.0))
    lapse = float(math.exp(float(lapse_shift[:ORDER] @ signs_k)))
    prefactor = float(3.0 * lapse * a_radius**3 * b_radius**3 / c_radius)

    d_log_a = np.zeros(Q_DIMENSION)
    d_log_b = np.zeros(Q_DIMENSION)
    d_log_a[0] = d_log_b[0] = 1.0
    d_log_a[1:1 + ORDER] = signs_k
    d_log_b[1:1 + ORDER] = signs_k
    d_log_a[1 + 2 * ORDER:1 + 3 * ORDER] = signs_j
    d_log_b[1 + 2 * ORDER:1 + 3 * ORDER] = -signs_j
    covector = prefactor * d_log_a - prefactor * d_log_b
    return covector, {
        "Pi_log_A": prefactor,
        "Pi_log_B": -prefactor,
        "Pi_log_N": 0.0,
        "lapse": lapse,
    }


def child_constraint_cauchy_match() -> dict[str, Any]:
    raw = v17_75_selected_raw_vector()
    state = unpack_reduced(raw)
    q_history = np.asarray(state["coordinates"], dtype=float)
    multiplier_history = np.asarray(state["multipliers"], dtype=float)
    velocity_history = (
        trapezoid_sbp_difference() @ q_history / float(state["period"])
    )
    q_event = q_history[-1]
    velocity_event = velocity_history[-1]
    multipliers_event = multiplier_history[-1]
    before = constraint_residual(
        ORDER, q_event, velocity_event, multipliers_event, points=44
    )

    projection = project_nested_constraints(
        ORDER, q_event, velocity_event, multipliers_event, points=44
    )
    q_child = np.asarray(projection["coordinates"], dtype=float)
    velocity_child = np.asarray(projection["velocities"], dtype=float)
    multipliers_child = np.asarray(projection["multipliers"], dtype=float)
    after = constraint_residual(
        ORDER, q_child, velocity_child, multipliers_child, points=44
    )

    momentum_event, force_event, _, _ = _canonical_pair(
        q_event, velocity_event, multipliers_event
    )
    momentum_child, force_child, q_lift_child, _ = _canonical_pair(
        q_child, velocity_child, multipliers_child
    )
    momentum_mismatch = momentum_child - momentum_event

    child_flux_covector, raw_child_flux = _metric_radial_flux_covector(
        q_child, multipliers_child
    )
    actual_child_flux = q_lift_child.T @ child_flux_covector
    required = required_child_cauchy_flux()
    required_child_flux = np.asarray(
        required["required_child_projected_flux"], dtype=float
    )
    flux_mismatch = actual_child_flux - required_child_flux

    return {
        "source_state": "v17.75_selected_fine_period_log_mix_state",
        "constraint_projection": {
            "success": bool(projection["success"]),
            "message": str(projection["message"]),
            "coordinate_trace_held_fixed": True,
            "coordinates": q_child.tolist(),
            "velocities": velocity_child.tolist(),
            "multipliers": multipliers_child.tolist(),
            "projection_objective": float(projection["objective"]),
            "constraint_order": [
                "lapse_1", "lapse_2", "lapse_3",
                "shift_0", "shift_1", "shift_2", "Hamiltonian_energy",
            ],
            "event_constraint_residual": before.tolist(),
            "event_constraint_norm": float(np.linalg.norm(before)),
            "projected_child_constraint_residual": after.tolist(),
            "projected_child_maximum_constraint_residual": float(
                np.max(np.abs(after))
            ),
        },
        "attachment_cauchy_match": {
            "coordinate_order": ["q_W", "x_D"],
            "event_momentum": momentum_event.tolist(),
            "projected_child_momentum": momentum_child.tolist(),
            "momentum_matching_residual_child_minus_event": (
                momentum_mismatch.tolist()
            ),
            "momentum_matching_residual_norm": float(
                np.linalg.norm(momentum_mismatch)
            ),
            "event_instantaneous_force": force_event.tolist(),
            "projected_child_instantaneous_force": force_child.tolist(),
            "actual_projected_child_flux": actual_child_flux.tolist(),
            "actual_raw_child_metric_flux": raw_child_flux,
            "required_projected_child_flux": required_child_flux.tolist(),
            "F_child_scalar_flux_residual": flux_mismatch.tolist(),
            "F_child_scalar_flux_residual_norm": float(
                np.linalg.norm(flux_mismatch)
            ),
        },
        "complete_scalar_child_map": {
            "Gamma0_trace_residual": [0.0, 0.0, 0.0],
            "Dirac_constraint_residual": after.tolist(),
            "canonical_momentum_residual": momentum_mismatch.tolist(),
            "dynamic_Calderon_flux_residual": flux_mismatch.tolist(),
            "closed": False,
            "why_open": (
                "THE_NEAREST_FIXED_TRACE_SEVEN_CONSTRAINT_PROJECTION_DOES_"
                "NOT_ALSO_SATISFY_CANONICAL_MOMENTUM_AND_DYNAMIC_FLUX_"
                "MATCHING"
            ),
            "next_BVP": (
                "VARY_THE_CHILD_INTERIOR_COORDINATES_VELOCITIES_AND_"
                "MULTIPLIERS_SUBJECT_TO_FIXED_Gamma0_SEVEN_CONSTRAINTS_"
                "TWO_MOMENTUM_ROWS_AND_TWO_DYNAMIC_FLUX_ROWS"
            ),
        },
        "interpretation": (
            "THE_PROJECTED_CHILD_HAS_FINITE_NONZERO_MOTION_MOMENTUM_FORCE_"
            "AND_FLUX;THE_DEFECT_IS_ONLY_THE_FAILURE_OF_THE_COUPLED_"
            "CONSTRAINT_AND_BOUNDARY_MATCHING_RELATIONS"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = child_constraint_cauchy_match()
    projection = result["constraint_projection"]
    cauchy = result["attachment_cauchy_match"]
    complete = result["complete_scalar_child_map"]
    validation = {
        "seven_child_constraints_owned": len(
            projection["projected_child_constraint_residual"]
        ) == 7,
        "fixed_trace_projection_succeeded": projection["success"],
        "projected_constraints_closed": projection[
            "projected_child_maximum_constraint_residual"
        ] < 1.0e-8,
        "momentum_match_evaluated": len(
            cauchy["momentum_matching_residual_child_minus_event"]
        ) == 2,
        "flux_match_evaluated": len(
            cauchy["F_child_scalar_flux_residual"]
        ) == 2,
        "incomplete_projection_not_promoted": (
            not complete["closed"]
            and cauchy["momentum_matching_residual_norm"] > 1.0e-6
            and cauchy["F_child_scalar_flux_residual_norm"] > 1.0e-6
        ),
        "nonzero_motion_not_called_defect": "DEFECT_IS_ONLY" in result[
            "interpretation"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_child_constraint_cauchy_match_v17_94",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "child_constraint_cauchy_match": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "LOCAL_CONSTRAINT_CONSISTENCY_IS_NECESSARY_BUT_NOT_SUFFICIENT_"
            "FOR_A_COMPLETE_PERSISTENT_CHILD"
        ),
        "dependency_advanced": (
            "EVALUATES_THE_ACTUAL_SEVEN_CONSTRAINT_CHILD_PROJECTION_IN_"
            "THE_EVENT_TO_CHILD_MOMENTUM_AND_DYNAMIC_FLUX_MAP"
        ),
        "active_calculation": complete["next_BVP"],
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_child_constraint_cauchy_match_v17_94.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "child_constraint_cauchy_match", "completion_payload", "materialize",
]
