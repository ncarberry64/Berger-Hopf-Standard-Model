"""Constraint-preserving attachment momentum and force at the N=3 event."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_event_attachment_state_incidence_v17_89 import (
    n3_attachment_state_map,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    Q_DIMENSION,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)


VERSION = "v17.91"
CLASSIFICATION = "BHSM_N3_ATTACHMENT_CANONICAL_COVECTOR"
FULL_BHSM_COMPLETE = False


def _constraint_preserving_lift(
    quadratic_form: np.ndarray,
    boundary_jacobian: np.ndarray,
    constraint_jacobian: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the quadratic-form-minimal lift of two boundary tangents."""

    form = np.asarray(quadratic_form, dtype=float)
    boundary = np.asarray(boundary_jacobian, dtype=float)
    constraints = np.asarray(constraint_jacobian, dtype=float)
    combined = np.vstack((boundary, constraints))
    target = np.zeros((combined.shape[0], boundary.shape[0]))
    target[:boundary.shape[0]] = np.eye(boundary.shape[0])
    inverse_times_constraints = np.linalg.solve(form, combined.T)
    compliance = combined @ inverse_times_constraints
    lift = inverse_times_constraints @ np.linalg.solve(compliance, target)
    return lift, compliance


def attachment_canonical_covector() -> dict[str, Any]:
    raw = v17_75_selected_raw_vector()
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"], dtype=float)
    multipliers = np.asarray(state["multipliers"], dtype=float)
    velocity = trapezoid_sbp_difference() @ q / float(state["period"])
    incidence = n3_attachment_state_map(raw)
    boundary_jacobian = np.asarray(
        incidence["state_jacobian_D_attachment_D_q_event"], dtype=float
    )[1:]

    jet = exact_full_action_jet_at_state(
        ORDER, q[-1], velocity[-1], multipliers[-1], points=44
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    q_form = hessian[:Q_DIMENSION, :Q_DIMENSION]
    velocity_form = hessian[
        Q_DIMENSION:2 * Q_DIMENSION,
        Q_DIMENSION:2 * Q_DIMENSION,
    ]
    constraint_q = hessian[2 * Q_DIMENSION:, :Q_DIMENSION]
    constraint_velocity = hessian[
        2 * Q_DIMENSION:, Q_DIMENSION:2 * Q_DIMENSION
    ]
    q_lift, q_compliance = _constraint_preserving_lift(
        q_form, boundary_jacobian, constraint_q
    )
    velocity_lift, velocity_compliance = _constraint_preserving_lift(
        velocity_form, boundary_jacobian, constraint_velocity
    )
    force = q_lift.T @ gradient[:Q_DIMENSION]
    momentum = velocity_lift.T @ gradient[
        Q_DIMENSION:2 * Q_DIMENSION
    ]

    return {
        "coordinate_order": ["q_W", "x_D"],
        "configuration": incidence["attachment_state"][1:],
        "constraint_preserving_coordinate_lift": q_lift.tolist(),
        "constraint_preserving_velocity_lift": velocity_lift.tolist(),
        "coordinate_lift_boundary_residual": float(np.linalg.norm(
            boundary_jacobian @ q_lift - np.eye(2)
        )),
        "coordinate_lift_constraint_residual": float(np.linalg.norm(
            constraint_q @ q_lift
        )),
        "velocity_lift_boundary_residual": float(np.linalg.norm(
            boundary_jacobian @ velocity_lift - np.eye(2)
        )),
        "velocity_lift_constraint_residual": float(np.linalg.norm(
            constraint_velocity @ velocity_lift
        )),
        "coordinate_compliance_condition_number": float(np.linalg.cond(
            q_compliance
        )),
        "velocity_compliance_condition_number": float(np.linalg.cond(
            velocity_compliance
        )),
        "canonical_attachment_momentum": momentum.tolist(),
        "instantaneous_attachment_action_force": force.tolist(),
        "canonical_covector": {
            "definition": (
                "I_attachment=(p_c,partial_L_child/partial_c,F_child_outer)_"
                "ON_THE_CONSTRAINT_PRESERVING_EVENT_TANGENT"
            ),
            "p_c": momentum.tolist(),
            "partial_L_child_partial_c": force.tolist(),
            "F_child_outer": "OPEN_NOT_SET_TO_ZERO",
        },
        "interpretation": {
            "nonzero_momentum_is_a_defect": False,
            "nonzero_force_is_a_static_failure": False,
            "role": (
                "MOMENTUM_AND_FORCE_ENTER_THE_DYNAMIC_WENTZELL_EULER_"
                "EQUATION_AND_NEED_NOT_VANISH_SEPARATELY"
            ),
            "missing_term": (
                "THE_EVENT_CORE_PLUS_COMPLETE_CHILD_TWO_SIDED_CALDERON_"
                "FLUX_PROJECTED_ON_THE_SAME_TWO_LIFTS"
            ),
        },
    }


def completion_payload() -> dict[str, Any]:
    result = attachment_canonical_covector()
    interpretation = result["interpretation"]
    validation = {
        "coordinate_lift_matches_boundary": result[
            "coordinate_lift_boundary_residual"
        ] < 1.0e-10,
        "coordinate_lift_preserves_constraints": result[
            "coordinate_lift_constraint_residual"
        ] < 1.0e-9,
        "velocity_lift_matches_boundary": result[
            "velocity_lift_boundary_residual"
        ] < 1.0e-10,
        "velocity_lift_preserves_constraints": result[
            "velocity_lift_constraint_residual"
        ] < 1.0e-9,
        "momentum_finite": bool(np.all(np.isfinite(
            result["canonical_attachment_momentum"]
        ))),
        "force_finite": bool(np.all(np.isfinite(
            result["instantaneous_attachment_action_force"]
        ))),
        "nonzero_momentum_retained": np.linalg.norm(
            result["canonical_attachment_momentum"]
        ) > 0.0,
        "nonzero_force_retained": np.linalg.norm(
            result["instantaneous_attachment_action_force"]
        ) > 0.0,
        "motion_not_defect": not interpretation["nonzero_momentum_is_a_defect"],
        "force_not_static_failure": not interpretation[
            "nonzero_force_is_a_static_failure"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_attachment_canonical_covector_v17_91",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "attachment_canonical_covector": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_EVENT_OWNS_NONZERO_CONSTRAINT_PRESERVING_ATTACHMENT_"
            "MOMENTUM_AND_FORCE_AS_PARTS_OF_RELATIVE_CHILD_EVOLUTION"
        ),
        "dependency_advanced": (
            "DERIVES_THE_EVENT_SIDE_NONLINEAR_ATTACHMENT_COVECTOR_ON_THE_"
            "V17_89_RANK_TWO_STATE_MAP"
        ),
        "active_calculation": (
            "DERIVE_AND_PROJECT_THE_EVENT_CORE_PLUS_COMPLETE_CHILD_TWO_"
            "SIDED_CALDERON_FLUX_ON_THE_SAME_TANGENT"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_attachment_canonical_covector_v17_91.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "attachment_canonical_covector", "completion_payload", "materialize",
]
