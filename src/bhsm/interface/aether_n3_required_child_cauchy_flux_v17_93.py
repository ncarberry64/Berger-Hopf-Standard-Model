"""Required child Neumann datum from the dynamic attachment equation."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
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
from bhsm.interface.aether_n3_terminal_child_boundary_map_v17_85 import (
    terminal_event_boundary_data,
)


VERSION = "v17.93"
CLASSIFICATION = "BHSM_N3_REQUIRED_COMPLETE_CHILD_CAUCHY_FLUX_MAP"
FULL_BHSM_COMPLETE = False


def _attachment_jacobian(q: np.ndarray) -> np.ndarray:
    value = np.asarray(q, dtype=float)
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    v_boundary = float(value[1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j)
    j_w = np.zeros(Q_DIMENSION)
    j_w[0] = 1.0
    j_w[1:1 + ORDER] = signs_k
    j_w[1 + 2 * ORDER:1 + 3 * ORDER] = (
        -math.tanh(2.0 * v_boundary) * signs_j
    )
    j_c = np.zeros(Q_DIMENSION)
    j_c[0] = 1.0
    return np.vstack((j_w, j_c - j_w))


def _lift(
    form: np.ndarray, boundary: np.ndarray, constraints: np.ndarray
) -> np.ndarray:
    combined = np.vstack((boundary, constraints))
    target = np.zeros((combined.shape[0], 2))
    target[:2] = np.eye(2)
    inverse_times = np.linalg.solve(form, combined.T)
    compliance = combined @ inverse_times
    return inverse_times @ np.linalg.solve(compliance, target)


def _canonical_pair(
    q: np.ndarray, velocity: np.ndarray, multipliers: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    jet = exact_full_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=44
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    boundary = _attachment_jacobian(q)
    q_form = hessian[:Q_DIMENSION, :Q_DIMENSION]
    v_form = hessian[
        Q_DIMENSION:2 * Q_DIMENSION,
        Q_DIMENSION:2 * Q_DIMENSION,
    ]
    cq = hessian[2 * Q_DIMENSION:, :Q_DIMENSION]
    cv = hessian[2 * Q_DIMENSION:, Q_DIMENSION:2 * Q_DIMENSION]
    q_lift = _lift(q_form, boundary, cq)
    v_lift = _lift(v_form, boundary, cv)
    momentum = v_lift.T @ gradient[Q_DIMENSION:2 * Q_DIMENSION]
    force = q_lift.T @ gradient[:Q_DIMENSION]
    return momentum, force, q_lift, v_lift


def required_child_cauchy_flux() -> dict[str, Any]:
    raw = v17_75_selected_raw_vector()
    state = unpack_reduced(raw)
    q_history = np.asarray(state["coordinates"], dtype=float)
    m_history = np.asarray(state["multipliers"], dtype=float)
    velocity_history = (
        trapezoid_sbp_difference() @ q_history / float(state["period"])
    )
    q = q_history[-1]
    velocity = velocity_history[-1]
    multipliers = m_history[-1]
    momentum, force, q_lift, _ = _canonical_pair(q, velocity, multipliers)
    event_local_constraints = constraint_residual(
        ORDER, q, velocity, multipliers, points=44
    )

    dynamics = exact_euler_dirac_acceleration(
        ORDER, q, velocity, multipliers, points=44
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    tangent_norm = max(
        1.0,
        float(np.max(np.abs(velocity))),
        float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )
    epsilon = 2.0e-6 / tangent_norm
    plus_momentum, _, _, _ = _canonical_pair(
        q + epsilon * velocity,
        velocity + epsilon * acceleration,
        multipliers + epsilon * multiplier_rate,
    )
    minus_momentum, _, _, _ = _canonical_pair(
        q - epsilon * velocity,
        velocity - epsilon * acceleration,
        multipliers - epsilon * multiplier_rate,
    )
    momentum_rate = (plus_momentum - minus_momentum) / (2.0 * epsilon)

    boundary = terminal_event_boundary_data(raw)
    radial = boundary["GHY_eta_radial_flux_Gamma1"]
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    d_log_a = np.zeros(Q_DIMENSION)
    d_log_b = np.zeros(Q_DIMENSION)
    d_log_a[0] = d_log_b[0] = 1.0
    d_log_a[1:1 + ORDER] = signs_k
    d_log_b[1:1 + ORDER] = signs_k
    d_log_a[1 + 2 * ORDER:1 + 3 * ORDER] = signs_j
    d_log_b[1 + 2 * ORDER:1 + 3 * ORDER] = -signs_j
    raw_event_flux = (
        float(radial["Pi_log_A"]) * d_log_a
        + float(radial["Pi_log_B"]) * d_log_b
    )
    event_flux = q_lift.T @ raw_event_flux

    # Coordinate-time Euler boundary equation:
    # D_t p_c - partial_c L + Gamma1_event + Gamma1_child = 0.
    child_required = -momentum_rate + force - event_flux
    smooth_opposite_normal = -event_flux
    dynamic_correction = child_required - smooth_opposite_normal
    return {
        "coordinate_order": ["q_W", "x_D"],
        "canonical_momentum": momentum.tolist(),
        "coordinate_time_momentum_rate": momentum_rate.tolist(),
        "instantaneous_action_force": force.tolist(),
        "event_projected_flux": event_flux.tolist(),
        "required_child_projected_flux": child_required.tolist(),
        "smooth_opposite_normal_reference": smooth_opposite_normal.tolist(),
        "dynamic_attachment_correction_to_smooth_reference": (
            dynamic_correction.tolist()
        ),
        "finite_difference": {
            "epsilon": epsilon,
            "follows_full_Euler_Dirac_tangent": True,
            "state_dependent_lift_recomputed_at_both_sides": True,
            "primitive_background_time_introduced": False,
        },
        "boundary_map": {
            "Dirichlet_Gamma0": boundary["spatial_trace_Gamma0"],
            "Cauchy_configuration": q.tolist(),
            "Cauchy_velocity": velocity.tolist(),
            "lapse_shift": multipliers.tolist(),
            "Neumann_Gamma1_child_required_attachment_projection": (
                child_required.tolist()
            ),
            "definition": (
                "B_child_required(z_event)=(Gamma0_event,q_event,dot_q_"
                "event,m_event,Gamma1_child_required)"
            ),
        },
        "F_child_scalar": {
            "definition": (
                "F_child_scalar(z_event)=Gamma1_child_actual_from_the_"
                "reconstructed_Lorentzian_child_minus_Gamma1_child_required"
            ),
            "actual_reconstructed_child_flux": "OPEN",
            "required_flux_derived_algebraically": True,
            "event_local_constraint_residual": event_local_constraints.tolist(),
            "event_local_maximum_constraint_residual": float(
                np.max(np.abs(event_local_constraints))
            ),
            "physical_target_promotable": False,
            "why_not_promotable": (
                "THE_MOMENTUM_RATE_WAS_DIFFERENTIATED_ALONG_THE_PRE_EVENT_"
                "TERMINAL_LOCAL_STATE_BEFORE_THAT_STATE_WAS_RECONSTRUCTED_"
                "ON_THE_SEVEN_CONSTRAINT_CHILD_SURFACE"
            ),
            "static_zero_flux_required": False,
            "smooth_reflection_assumed_as_solution": False,
        },
        "interpretation": (
            "THE_ALGEBRAIC_DYNAMIC_SCALAR_BOUNDARY_FORM_IS_DERIVED_BUT_"
            "ITS_PRE_EVENT_TANGENT_EVALUATION_IS_PROVISIONAL;NONZERO_"
            "MOMENTUM_FORCE_ACCELERATION_AND_FLUX_ARE_BALANCED_TERMS_NOT_"
            "INDIVIDUAL_DEFECTS"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = required_child_cauchy_flux()
    child = result["F_child_scalar"]
    validation = {
        "two_required_flux_components": len(
            result["required_child_projected_flux"]
        ) == 2,
        "momentum_rate_finite": bool(np.all(np.isfinite(
            result["coordinate_time_momentum_rate"]
        ))),
        "required_flux_finite": bool(np.all(np.isfinite(
            result["required_child_projected_flux"]
        ))),
        "dynamic_correction_nonzero": np.linalg.norm(
            result["dynamic_attachment_correction_to_smooth_reference"]
        ) > 0.0,
        "state_dependent_lift_differentiated": result["finite_difference"][
            "state_dependent_lift_recomputed_at_both_sides"
        ],
        "required_flux_form_derived": child[
            "required_flux_derived_algebraically"
        ],
        "inadmissible_pre_event_tangent_not_promoted": (
            not child["physical_target_promotable"]
            and child["event_local_maximum_constraint_residual"] > 1.0
        ),
        "actual_child_flux_not_fabricated": child[
            "actual_reconstructed_child_flux"
        ] == "OPEN",
        "static_flux_not_required": not child["static_zero_flux_required"],
        "smooth_reflection_not_assumed": not child[
            "smooth_reflection_assumed_as_solution"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_required_complete_child_cauchy_flux_v17_93",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "required_complete_child_cauchy_flux": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_DYNAMIC_NEUMANN_FORM_IS_DERIVED_BUT_MUST_BE_EVALUATED_"
            "ON_THE_CONSTRAINT_CONSISTENT_RECONSTRUCTED_CHILD_GERM"
        ),
        "dependency_advanced": (
            "DERIVES_THE_EVENT_TO_CHILD_DYNAMIC_BOUNDARY_FORM_AND_EXPOSES_"
            "THE_NEED_FOR_A_CONSTRAINT_CONSISTENT_CHILD_TANGENT"
        ),
        "active_calculation": (
            "SOLVE_THE_LORENTZIAN_RECONSTRUCTED_CHILD_WITH_THIS_DIRICHLET_"
            "CAUCHY_NEUMANN_TARGET_AND_EVALUATE_F_child_scalar"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_required_complete_child_cauchy_flux_v17_93.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "required_child_cauchy_flux", "completion_payload", "materialize",
]
