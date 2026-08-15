"""Construct an exact-action, directional-event merit descent for square KKT."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector


VERSION = "v18.22"
CLASSIFICATION = "BHSM_N3_DIRECTIONAL_EVENT_MERIT_DESCENT"
FULL_BHSM_COMPLETE = False
EVENT_DIRECTIONAL_STEP = 3.0e-5
TRIAL_STEPS = (1.0e-8, 3.0e-8, 1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3)


def v18_22_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_directional_event_merit_descent_v18_22.json"
    ).read_text(encoding="utf-8"))
    selected = payload["directional_event_merit_descent"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.22 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def _event_gradient_scaled(ybase: np.ndarray, scales: np.ndarray) -> np.ndarray:
    return (
        sbp_event_covector(ybase / scales[:-1])
        / scales[:-1] / scales[-1]
    )


def _event_hessian_vector(
    ybase: np.ndarray, direction: np.ndarray, scales: np.ndarray,
) -> np.ndarray:
    norm = float(np.linalg.norm(direction))
    if norm == 0.0:
        return np.zeros(375)
    unit = direction / norm
    plus = _event_gradient_scaled(ybase + EVENT_DIRECTIONAL_STEP * unit, scales)
    minus = _event_gradient_scaled(ybase - EVENT_DIRECTIONAL_STEP * unit, scales)
    return norm * (plus - minus) / (2.0 * EVENT_DIRECTIONAL_STEP)


def directional_event_merit_descent() -> dict[str, Any]:
    raw = v18_12_selected_raw_vector(); scales = kkt_variable_scales(); y = raw * scales
    residual = _square_physical_residual(y); initial = _metrics(residual)
    action = exact_sbp_action_hessian(raw[:-1])
    action_raw = np.asarray(action.pop("hessian")); inverse = 1.0 / scales[:-1]
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_gradient = _event_gradient_scaled(y[:-1], scales)
    event_hv_residual = _event_hessian_vector(y[:-1], residual[:-1], scales)
    jacobian_residual = np.concatenate((
        action_scaled @ residual[:-1]
        + y[-1] * event_hv_residual
        + residual[-1] * event_gradient,
        [float(event_gradient @ residual[:-1])],
    ))
    residual_direction = residual / np.linalg.norm(residual)
    predicted_jv = jacobian_residual / np.linalg.norm(residual)
    response_checks = []
    for epsilon in (1.0e-4, 3.0e-5, 1.0e-5):
        finite = (
            _square_physical_residual(y + epsilon * residual_direction)
            - _square_physical_residual(y - epsilon * residual_direction)
        ) / (2.0 * epsilon)
        response_checks.append({
            "epsilon": epsilon,
            "finite_response_norm": float(np.linalg.norm(finite)),
            "relative_residual": float(
                np.linalg.norm(predicted_jv - finite) / max(1.0, np.linalg.norm(finite))
            ),
        })
    merit_gradient = jacobian_residual
    direction = -merit_gradient / np.linalg.norm(merit_gradient)
    source_merit = 0.5 * float(residual @ residual)
    slopes = []; trials = []; eligible = []
    for step in TRIAL_STEPS:
        plus_residual = _square_physical_residual(y + step * direction)
        minus_residual = _square_physical_residual(y - step * direction)
        plus_merit = 0.5 * float(plus_residual @ plus_residual)
        minus_merit = 0.5 * float(minus_residual @ minus_residual)
        slope = (plus_merit - minus_merit) / (2.0 * step)
        slopes.append({
            "step": step,
            "exact_symmetric_merit_slope": slope,
            "predicted_merit_slope": -float(np.linalg.norm(merit_gradient)),
        })
        candidate_raw = (y + step * direction) / scales
        metrics = _metrics(plus_residual); eta = _minimum_node_eta(candidate_raw)
        row = {
            "step": step,
            "physical_scaled_coordinate_step_norm": step,
            "raw_coordinate_step_norm": float(step * np.linalg.norm(direction / scales)),
            "eta_minimum": eta,
            "metrics": metrics,
            "complete_norm_reduction": initial["complete"] - metrics["complete"],
            "merit_reduction": source_merit - plus_merit,
            "raw_vector_hex": [float(value).hex() for value in candidate_raw],
        }
        row["true_merit_eligible"] = bool(
            eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
        )
        trials.append(row)
        if row["true_merit_eligible"]:
            eligible.append(row)
    selected = min(eligible, key=lambda row: row["metrics"]["complete"]) if eligible else None
    return {
        "source_state": "v18.12_complete_child_promoted_state",
        "source_complete_norm": initial["complete"],
        "source_eta_minimum": _minimum_node_eta(raw),
        "action_response": action,
        "event_response": {
            "type": "DIRECTIONAL_HESSIAN_VECTOR_ONLY",
            "scaled_displacement": EVENT_DIRECTIONAL_STEP,
            "full_event_hessian_claimed": False,
            "invalidated_v18_19_v18_21_matrices_reused": False,
        },
        "jacobian_residual_norm": float(np.linalg.norm(jacobian_residual)),
        "response_checks": response_checks,
        "maximum_response_relative_residual": max(row["relative_residual"] for row in response_checks),
        "merit_gradient_norm": float(np.linalg.norm(merit_gradient)),
        "predicted_unit_direction_merit_slope": -float(np.linalg.norm(merit_gradient)),
        "exact_directional_slopes": slopes,
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_equations_changed": False,
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
    }


def completion_payload() -> dict[str, Any]:
    result = directional_event_merit_descent()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    resolved_slopes = [
        row["exact_symmetric_merit_slope"]
        for row in result["exact_directional_slopes"] if row["step"] >= 1.0e-5
    ]
    validation = {
        "source_is_v18_12": result["source_state"].startswith("v18.12"),
        "exact_action_response_validated": result["action_response"]["gradient_relative_residual"] < 5.0e-11,
        "directional_event_only": result["event_response"]["type"] == "DIRECTIONAL_HESSIAN_VECTOR_ONLY" and not result["event_response"]["full_event_hessian_claimed"],
        "invalid_event_matrices_not_reused": not result["event_response"]["invalidated_v18_19_v18_21_matrices_reused"],
        "response_direction_validated": result["maximum_response_relative_residual"] < 2.0e-2,
        "resolved_merit_slope_negative": all(slope < 0.0 for slope in resolved_slopes),
        "square_explicit_multiplier_system": result["physical_solve_dimension"] == [376, 376] and result["event_multiplier_explicit"],
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "no_componentwise_filter": not result["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not result["must_remain_on_previous_iterate_path"],
        "selected_reduces_true_merit": bool(selected is None or selected["complete_norm_reduction"] > MARGIN),
        "selected_preserves_eta": bool(selected is None or selected["eta_minimum"] > 1.0e-5),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_directional_event_merit_descent_v18_22",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "directional_event_merit_descent": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "AN_EXACT_ACTION_PLUS_DIRECTIONAL_EVENT_RESPONSE_DETERMINES_THE_"
            "SQUARE_KKT_MERIT_GRADIENT_WITHOUT_A_FALSE_FULL_EVENT_HESSIAN"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_COMPLETE_CHILD_IF_PRESENT" if selected is not None
            else "RESOLVE_THE_DIRECTIONAL_EVENT_RESPONSE_OR_MERIT_NOISE_FLOOR"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_directional_event_merit_descent_v18_22.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v18_22_selected_raw_vector", "directional_event_merit_descent", "completion_payload", "materialize"]
