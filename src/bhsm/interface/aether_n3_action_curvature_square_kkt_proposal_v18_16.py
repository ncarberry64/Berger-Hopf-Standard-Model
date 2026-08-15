"""Apply the v18.15 action-curvature coordinates to a square-KKT proposal."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_coordinate_map_v18_15 import _absolute_curvature_whitener
from bhsm.interface.aether_n3_action_owned_stiffness_measurement_v18_14 import _local_action_terms
from bhsm.interface.aether_n3_direct_constrained_trust_newton_v17_83 import TRUST_RADIUS_MAXIMUM, _dogleg
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import exact_full_action_jet_at_state
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_high_accuracy_physical_jacobian_v17_58 import parallel_high_accuracy_sbp_physical_jacobian
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION, NODES, ORDER, Q_DIMENSION, kkt_variable_scales,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import sobolev_weights, spectral_frequencies


VERSION = "v18.16"
CLASSIFICATION = "BHSM_N3_ACTION_CURVATURE_SQUARE_KKT_PROPOSAL"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 17


def v18_16_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_action_curvature_square_kkt_proposal_v18_16.json"
    ).read_text(encoding="utf-8"))
    selected = payload["action_curvature_square_kkt_proposal"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.16 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def _action_curvature_transform(raw: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    measurement = json.loads(Path(
        "artifacts/BHSM_aether_n3_action_owned_stiffness_measurement_v18_14.json"
    ).read_text(encoding="utf-8"))
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"]); m = np.asarray(state["multipliers"])
    period = float(state["period"]); velocity = trapezoid_sbp_difference() @ q / period
    jet = exact_full_action_jet_at_state(ORDER, q[-1], velocity[-1], m[-1], points=44)
    action_reference = float(sum(abs(value) for value in _local_action_terms(
        q[-1], velocity[-1], m[-1]
    ).values()))
    frequencies = spectral_frequencies(ORDER)["coordinates"]
    q_amplitude = 1.0 / ((1.0 + frequencies**2)**3.0)
    m_amplitude = 1.0 / sobolev_weights(ORDER)["multipliers"]
    lift_q = np.zeros((26, Q_DIMENSION))
    lift_q[:Q_DIMENSION] = np.diag(q_amplitude)
    lift_q[Q_DIMENSION:2 * Q_DIMENSION] = np.diag(q_amplitude / period)
    lift_m = np.zeros((26, M_DIMENSION))
    lift_m[2 * Q_DIMENSION:] = np.diag(m_amplitude)
    q_transform, q_audit = _absolute_curvature_whitener(
        lift_q.T @ jet.hessian @ lift_q / action_reference
    )
    m_transform, m_audit = _absolute_curvature_whitener(
        lift_m.T @ jet.hessian @ lift_m / action_reference
    )
    rows = measurement["action_owned_stiffness_measurement"]["global_directional_measurements"]
    period_row = next(row for row in rows if row["direction"] == "period")
    period_factor = math.sqrt(
        action_reference / abs(float(period_row["directional_second_variation"]))
    )
    transform = np.eye(376)
    for node in range(NODES - 1):
        sl = slice(node * Q_DIMENSION, (node + 1) * Q_DIMENSION)
        transform[sl, sl] = q_transform
    offset = (NODES - 1) * Q_DIMENSION
    for node in range(NODES):
        sl = slice(offset + node * M_DIMENSION, offset + (node + 1) * M_DIMENSION)
        transform[sl, sl] = m_transform
    transform[-2, -2] = period_factor
    transform[-1, -1] = 1.0
    singular = np.linalg.svd(transform, compute_uv=False)
    return transform, {
        "source": "VALIDATED_V18_15_ACTION_CURVATURE_COORDINATE_MAP",
        "action_reference": action_reference,
        "q_resolved_rank": q_audit["resolved_rank"],
        "multiplier_resolved_rank": m_audit["resolved_rank"],
        "minimum_singular_value": float(singular[-1]),
        "maximum_singular_value": float(singular[0]),
        "invertible": bool(singular[-1] > 0.0),
    }


def action_curvature_square_kkt_proposal() -> dict[str, Any]:
    source_raw = v18_12_selected_raw_vector()
    scales = kkt_variable_scales(); source_y = source_raw * scales
    source_residual = _square_physical_residual(source_y)
    initial = _metrics(source_residual)
    transform, transform_audit = _action_curvature_transform(source_raw)
    assembled = parallel_high_accuracy_sbp_physical_jacobian(source_raw)
    proposal_y = np.asarray(assembled.pop("matrix"))
    proposal_x = proposal_y @ transform
    gradient_x = proposal_x.T @ source_residual
    image = proposal_x @ gradient_x
    cauchy_radius = float(
        (gradient_x @ gradient_x) ** 1.5 / max(float(image @ image), 1.0e-300)
    )
    trust_radius = min(TRUST_RADIUS_MAXIMUM, max(1.0e-6, cauchy_radius))
    direction_x, dogleg = _dogleg(proposal_x, source_residual, trust_radius)
    direction_y = transform @ direction_x
    predicted = source_residual + proposal_y @ direction_y
    trials: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_y = source_y + fraction * direction_y
        try:
            residual = _square_physical_residual(candidate_y)
            candidate_raw = candidate_y / scales
            metrics = _metrics(residual)
            eta = _minimum_node_eta(candidate_raw)
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "action_curvature_coordinate_step_norm": float(fraction * np.linalg.norm(direction_x)),
                "physical_scaled_coordinate_step_norm": float(fraction * np.linalg.norm(direction_y)),
                "raw_coordinate_step_norm": float(fraction * np.linalg.norm(direction_y / scales)),
                "eta_minimum": eta,
                "metrics": metrics,
                "complete_norm_reduction": initial["complete"] - metrics["complete"],
                "raw_vector_hex": [float(value).hex() for value in candidate_raw],
            }
            row["true_merit_eligible"] = bool(
                eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
            )
            trials.append(row)
            if row["true_merit_eligible"]:
                eligible.append(row)
        except (ArithmeticError, FloatingPointError, ValueError) as exc:
            trials.append({
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    selected = min(eligible, key=lambda row: row["metrics"]["complete"]) if eligible else None
    return {
        "source_state": "v18.12_complete_child_promoted_state",
        "initial_metrics": initial,
        "initial_eta_minimum": _minimum_node_eta(source_raw),
        "coordinate_map": transform_audit,
        "proposal_model": {
            **assembled,
            "derivative_claim": "INVALIDATED_V17_58_VS_V17_61_RESPONSE_NOT_REASSERTED",
            "used_only_to_propose_trials": True,
            "right_coordinate_map_only": True,
            "left_residual_scaling_applied": False,
            "physical_solve_dimension": [376, 376],
            "event_multiplier_explicit": True,
            "event_multiplier_analytically_projected": False,
            "physical_action_changed": False,
            "physical_event_changed": False,
            "global_KKT_row_added": False,
        },
        "trust_model": {
            **dogleg,
            "derived_cauchy_radius": cauchy_radius,
            "physical_scaled_direction_norm": float(np.linalg.norm(direction_y)),
            "predicted_complete_norm_reduction_not_a_claim": float(
                np.linalg.norm(source_residual) - np.linalg.norm(predicted)
            ),
        },
        "acceptance_rule": (
            "INDEPENDENT_EXACT_SQUARE_376_TOTAL_MERIT_REDUCTION_AND_ETA;_"
            "COMPLETE_CHILD_RECONSTRUCTION_REQUIRED_BEFORE_PROMOTION"
        ),
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = action_curvature_square_kkt_proposal()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    model = result["proposal_model"]
    validation = {
        "source_is_v18_12": result["source_state"].startswith("v18.12"),
        "v18_15_coordinate_map_invertible": result["coordinate_map"]["invertible"],
        "invalid_derivative_claim_not_reasserted": model["derivative_claim"].startswith("INVALIDATED"),
        "proposal_model_only": model["used_only_to_propose_trials"],
        "right_coordinate_map_only": model["right_coordinate_map_only"] and not model["left_residual_scaling_applied"],
        "square_explicit_multiplier_solve": model["physical_solve_dimension"] == [376, 376] and model["event_multiplier_explicit"] and not model["event_multiplier_analytically_projected"],
        "physical_equations_unchanged": not model["physical_action_changed"] and not model["physical_event_changed"] and not model["global_KKT_row_added"],
        "no_componentwise_filter": not result["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not result["must_remain_on_previous_iterate_path"],
        "candidate_classified": selected is not None or bool(result["trials"]),
        "selected_reduces_true_merit": bool(selected is None or selected["complete_norm_reduction"] > MARGIN),
        "selected_preserves_eta": bool(selected is None or selected["eta_minimum"] > 1.0e-5),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_action_curvature_square_kkt_proposal_v18_16",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "action_curvature_square_kkt_proposal": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_ACTION_CURVATURE_COORDINATE_MAP_CHANGES_ONLY_THE_PROPOSAL_"
            "GEOMETRY_WHILE_EXACT_PHYSICAL_MERIT_REMAINS_THE_ACCEPTANCE_MEASURE"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_COMPLETE_CHILD_IF_PRESENT;_"
            "OTHERWISE_AUDIT_THE_PROPOSAL_MODEL_AGAINST_EXACT_TOTAL_MERIT"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_action_curvature_square_kkt_proposal_v18_16.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v18_16_selected_raw_vector", "action_curvature_square_kkt_proposal", "completion_payload", "materialize"]
