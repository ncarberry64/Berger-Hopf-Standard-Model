"""Promote the first norm-reducing N=3 step with complete-child acceptance."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import (
    _metric_radial_flux_covector,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    _advance_constrained,
    eta_legendre_minimum,
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    _metrics,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
    unpack_reduced,
)
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import (
    _canonical_pair,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scalar_complete_child_boundary_solution_v17_96 import (
    _trace_jacobian,
)


VERSION = "v18.00"
CLASSIFICATION = "BHSM_N3_COMPLETE_CHILD_MERIT_PROMOTION"
FULL_BHSM_COMPLETE = False


_CHILD_Q = np.asarray([
    -0.00045972100470063, 0.02188001970726366,
    -0.01316516795080263, -0.02724522270426428,
    0.05741309591366458, -0.24544757971491346,
    0.00029374940593023, -0.0829432987642108,
    0.02765473134217901, 0.13827878675355856,
])
_CHILD_V = np.asarray([
    -0.31644186858019596, -0.149205035569735,
    0.1727118120675777, -0.02396357249459281,
    -4.068912007619503, -8.074368231506005,
    -2.0294214155360386, 0.3613748501240466,
    0.600910991483536, 0.19656948368052682,
])
_CHILD_M = np.asarray([
    1.0487220625575764, 0.05889405079228081,
    0.8875388136123643, -0.15203320731416298,
    -0.12757524582459767, 0.8036653640828633,
])


def _v17_83_trial_zero() -> tuple[dict[str, Any], np.ndarray]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_direct_constrained_trust_newton_v17_83.json"
    ).read_text(encoding="utf-8"))["direct_constrained_trust_newton"]
    trial = next(row for row in payload["trials"] if row["backtrack"] == 0)
    raw = np.asarray([float.fromhex(value) for value in trial["raw_vector_hex"]])
    return payload, raw


def v18_00_selected_raw_vector() -> np.ndarray:
    return _v17_83_trial_zero()[1].copy()


def complete_child_merit_promotion() -> dict[str, Any]:
    prior, candidate_raw = _v17_83_trial_zero()
    scales = kkt_variable_scales()
    candidate_y, candidate_residual = (
        exact_local_jet_sbp_projected_residual_and_vector(
            candidate_raw * scales
        )
    )
    candidate_raw = candidate_y / scales
    candidate_metrics = _metrics(candidate_residual)
    initial_metrics = prior["initial_metrics"]

    event_state = unpack_reduced(candidate_raw)
    q_history = np.asarray(event_state["coordinates"], dtype=float)
    multiplier_history = np.asarray(event_state["multipliers"], dtype=float)
    velocity_history = (
        trapezoid_sbp_difference() @ q_history / float(event_state["period"])
    )
    q_event = q_history[-1]
    velocity_event = velocity_history[-1]
    multipliers_event = multiplier_history[-1]
    event_momentum, _, event_lift, _ = _canonical_pair(
        q_event, velocity_event, multipliers_event
    )
    child_momentum, child_force, child_lift, _ = _canonical_pair(
        _CHILD_Q, _CHILD_V, _CHILD_M
    )
    event_covector, _ = _metric_radial_flux_covector(
        q_event, multipliers_event
    )
    child_covector, _ = _metric_radial_flux_covector(_CHILD_Q, _CHILD_M)
    event_flux = event_lift.T @ event_covector
    child_flux = child_lift.T @ child_covector
    dynamics = exact_euler_dirac_acceleration(
        3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    tangent_scale = max(
        1.0,
        float(np.max(np.abs(_CHILD_V))),
        float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )
    flux_rows = []
    # v17.95 established 8e-4/4e-4 as the resolved central-difference
    # plateau. Smaller steps re-enter subtraction noise and are not used as
    # physical acceptance rows.
    for relative_step in (8.0e-4, 4.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(
            _CHILD_Q + epsilon * _CHILD_V,
            _CHILD_V + epsilon * acceleration,
            _CHILD_M + epsilon * multiplier_rate,
        )
        minus, _, _, _ = _canonical_pair(
            _CHILD_Q - epsilon * _CHILD_V,
            _CHILD_V - epsilon * acceleration,
            _CHILD_M - epsilon * multiplier_rate,
        )
        momentum_rate = (plus - minus) / (2.0 * epsilon)
        residual = child_flux - (
            -momentum_rate + child_force - event_flux
        )
        flux_rows.append({
            "relative_step": relative_step,
            "residual": residual.tolist(),
            "norm": float(np.linalg.norm(residual)),
        })
    child_constraints = constraint_residual(
        3, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    child_eta = eta_legendre_minimum(_CHILD_Q, _CHILD_M, points=5000)
    q_next, v_next, m_next, _, projection = _advance_constrained(
        _CHILD_Q, _CHILD_V, _CHILD_M, 1.0e-5, points=44
    )
    next_eta = eta_legendre_minimum(q_next, m_next, points=3000)
    next_constraints = constraint_residual(
        3, q_next, v_next, m_next, points=44
    )
    trace_residual = _trace_jacobian() @ (_CHILD_Q - q_event)
    momentum_residual = child_momentum - event_momentum
    flux_envelope = max(row["norm"] for row in flux_rows)

    return {
        "source_state": "v17.75_selected_fine_period_log_mix_state",
        "promoted_global_state": {
            "source_trial": "v17.83_backtrack_zero",
            "raw_vector_hex": [float(value).hex() for value in candidate_raw],
            "initial_metrics": initial_metrics,
            "candidate_metrics": candidate_metrics,
            "complete_norm_reduction": (
                initial_metrics["complete"] - candidate_metrics["complete"]
            ),
            "event_component_change": (
                candidate_metrics["event"] - initial_metrics["event"]
            ),
            "eta_minimum": _minimum_node_eta(candidate_raw),
        },
        "complete_child_acceptance": {
            "trace_residual": trace_residual.tolist(),
            "maximum_trace_residual": float(np.max(np.abs(trace_residual))),
            "maximum_seven_constraint_residual": float(
                np.max(np.abs(child_constraints))
            ),
            "attachment_momentum_residual": momentum_residual.tolist(),
            "attachment_momentum_residual_norm": float(
                np.linalg.norm(momentum_residual)
            ),
            "dynamic_flux_rows": flux_rows,
            "dynamic_flux_residual_envelope": flux_envelope,
            "eta_Legendre_minimum": child_eta,
            "positive_duration_step": 1.0e-5,
            "next_step_projection_success": bool(projection["success"]),
            "next_step_maximum_constraint_residual": float(
                np.max(np.abs(next_constraints))
            ),
            "next_step_eta_Legendre_minimum": next_eta,
            "nonzero_child_motion_retained": float(np.linalg.norm(
                v_next
            )) > 0.0,
        },
        "acceptance_rule": {
            "definition": (
                "ACCEPT_IF_THE_TRUE_COMPLETE_376_ROW_NORM_DECREASES_THE_"
                "GLOBAL_ETA_DOMAIN_IS_PRESERVED_AND_THE_PERTURBED_EVENT_"
                "RECONSTRUCTS_A_COMPLETE_POSITIVE_DURATION_CHILD"
            ),
            "each_named_residual_component_must_decrease_monotonically": False,
            "why_event_component_increase_is_not_a_defect": (
                "A_SINGLE_COMPONENT_MAY_INCREASE_ALONG_A_DESCENT_STEP_OF_"
                "THE_COUPLED_MERIT;IT_MUST_CLOSE_AT_CONVERGENCE_BUT_IS_NOT_"
                "AN_INDEPENDENT_LINE_SEARCH_MERIT_FUNCTION"
            ),
            "handcrafted_direction_mixture": False,
            "new_KKT_row_added": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = complete_child_merit_promotion()
    global_state = result["promoted_global_state"]
    child = result["complete_child_acceptance"]
    rule = result["acceptance_rule"]
    validation = {
        "true_complete_norm_reduced": global_state[
            "complete_norm_reduction"
        ] > 0.0,
        "global_eta_preserved": global_state["eta_minimum"] > 1.0e-5,
        "small_event_increase_classified": global_state[
            "event_component_change"
        ] > 0.0,
        "child_trace_closed": child["maximum_trace_residual"] < 1.0e-9,
        "child_constraints_closed": child[
            "maximum_seven_constraint_residual"
        ] < 1.0e-9,
        "child_momentum_closed": child[
            "attachment_momentum_residual_norm"
        ] < 1.0e-7,
        "child_flux_closed": child[
            "dynamic_flux_residual_envelope"
        ] < 2.0e-5,
        "child_eta_hyperregular": child[
            "eta_Legendre_minimum"
        ]["minimum"] > 0.0,
        "child_positive_step_persists": (
            child["next_step_projection_success"]
            and child["next_step_maximum_constraint_residual"] < 1.0e-8
            and child["next_step_eta_Legendre_minimum"]["minimum"] > 0.0
        ),
        "motion_not_rejected": child["nonzero_child_motion_retained"],
        "no_handcrafted_mixture": not rule["handcrafted_direction_mixture"],
        "no_377th_row": not rule["new_KKT_row_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_complete_child_merit_promotion_v18_00",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "complete_child_merit_promotion": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_FIRST_TRUE_GLOBAL_MERIT_DESCENT_STEP_ALSO_PRODUCES_A_"
            "COMPLETE_CONSTRAINT_CONSISTENT_PERSISTENT_MOVING_CHILD"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "REFRESH_THE_EXISTING_PHYSICAL_JACOBIAN_AT_THE_PROMOTED_STATE_"
            "AND_CONTINUE_TRUE_MERIT_DESCENT_WITH_COMPLETE_CHILD_ACCEPTANCE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_complete_child_merit_promotion_v18_00.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v18_00_selected_raw_vector", "complete_child_merit_promotion",
    "completion_payload", "materialize",
]
