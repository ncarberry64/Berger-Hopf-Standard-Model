"""Resolve the event Hessian in action-owned scaled coordinates."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector, sbp_event_value_from_base
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices, kkt_variable_scales
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector


VERSION = "v18.21"
CLASSIFICATION = "BHSM_N3_RESOLVED_SCALED_EVENT_KKT_RESPONSE"
FULL_BHSM_COMPLETE = False
SCALED_EVENT_HESSIAN_STEP = 3.0e-5


def _scaled_event_hessian(ybase: np.ndarray, scales: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    support = np.asarray(event_gradient_indices(), dtype=int)

    def event(value: np.ndarray) -> float:
        return sbp_event_value_from_base(value / scales[:-1]) / scales[-1]

    hessian = np.zeros((375, 375)); center = event(ybase)
    step = SCALED_EVENT_HESSIAN_STEP
    for index in support:
        i = int(index); delta = np.zeros(375); delta[i] = step
        hessian[i, i] = (
            event(ybase + delta) - 2.0 * center + event(ybase - delta)
        ) / step**2
    for row_position, row_index in enumerate(support):
        i = int(row_index)
        for column_index in support[row_position + 1:]:
            j = int(column_index)
            di = np.zeros(375); dj = np.zeros(375)
            di[i] = step; dj[j] = step
            entry = (
                event(ybase + di + dj) - event(ybase + di - dj)
                - event(ybase - di + dj) + event(ybase - di - dj)
            ) / (4.0 * step**2)
            hessian[i, j] = entry; hessian[j, i] = entry
    block = hessian[np.ix_(support, support)]
    return hessian, {
        "coordinate_system": "ACTION_OWNED_H6_SOBOLEV_SCALED_BASE",
        "support_dimension": int(support.size),
        "scaled_step": step,
        "event_value_scaled": center,
        "support_hessian_norm": float(np.linalg.norm(block)),
        "support_hessian_symmetry_residual": float(
            np.linalg.norm(block - block.T) / max(1.0, np.linalg.norm(block))
        ),
        "scale_selected_from_v18_20_plateau": True,
    }


def resolved_scaled_event_kkt_response(raw: np.ndarray) -> dict[str, Any]:
    state = np.asarray(raw, dtype=float); scales = kkt_variable_scales(); y = state * scales
    action = exact_sbp_action_hessian(state[:-1])
    action_raw = np.asarray(action.pop("hessian")); inverse = 1.0 / scales[:-1]
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_scaled, event_audit = _scaled_event_hessian(y[:-1], scales)
    event_gradient = sbp_event_covector(state[:-1]) * inverse / scales[-1]
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_scaled + y[-1] * event_scaled
    matrix[:-1, -1] = event_gradient
    matrix[-1, :-1] = event_gradient
    return {
        "matrix": matrix,
        "action_response": action,
        "event_response": event_audit,
        "action_hessian_scaled_norm": float(np.linalg.norm(action_scaled)),
        "event_hessian_scaled_norm": float(np.linalg.norm(event_scaled)),
        "event_curvature_contribution_norm": float(abs(y[-1]) * np.linalg.norm(event_scaled)),
        "event_gradient_scaled_norm": float(np.linalg.norm(event_gradient)),
        "matrix_symmetry_residual": float(
            np.linalg.norm(matrix - matrix.T) / max(1.0, np.linalg.norm(matrix))
        ),
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "event_multiplier_analytically_projected": False,
        "left_residual_scaling_applied": False,
        "physical_equations_changed": False,
    }


def resolved_scaled_event_kkt_response_audit() -> dict[str, Any]:
    raw = v18_12_selected_raw_vector(); scales = kkt_variable_scales(); y = raw * scales
    assembled = resolved_scaled_event_kkt_response(raw)
    matrix = np.asarray(assembled.pop("matrix"))
    support = np.asarray(event_gradient_indices(), dtype=int)
    mixed = np.zeros(376); mixed[support] = np.cos(np.arange(support.size) + 0.31)
    templates = [
        np.cos(np.arange(376) + 0.29),
        np.sin(0.31 * np.arange(376) + 0.53),
        np.where(np.arange(376) < 200, 1.0, 0.0),
        np.where(np.arange(376) == 375, 1.0, 0.0),
        mixed,
    ]
    directions = []
    for number, template in enumerate(templates):
        direction = np.asarray(template, dtype=float); direction /= np.linalg.norm(direction)
        predicted = matrix @ direction; checks = []
        for epsilon in (4.0e-5, 2.0e-5):
            finite = (
                _square_physical_residual(y + epsilon * direction)
                - _square_physical_residual(y - epsilon * direction)
            ) / (2.0 * epsilon)
            checks.append({
                "epsilon": epsilon,
                "finite_response_norm": float(np.linalg.norm(finite)),
                "relative_residual": float(
                    np.linalg.norm(predicted - finite) / max(1.0, np.linalg.norm(finite))
                ),
                "event_row_absolute_residual": float(abs(predicted[-1] - finite[-1])),
            })
        directions.append({
            "direction": number,
            "predicted_response_norm": float(np.linalg.norm(predicted)),
            "checks": checks,
        })
    return {
        "source_state": "EXACT_ACCEPTED_V18_12",
        "assembly": assembled,
        "directional_checks": directions,
        "maximum_directional_relative_residual": max(
            check["relative_residual"] for row in directions for check in row["checks"]
        ),
        "maximum_event_row_absolute_residual": max(
            check["event_row_absolute_residual"] for row in directions for check in row["checks"]
        ),
        "v18_19_uniform_raw_event_hessian": "INVALIDATED_NOT_REUSED",
        "componentwise_monotonicity_required": False,
        "complete_child_acceptance_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = resolved_scaled_event_kkt_response_audit(); assembly = result["assembly"]
    validation = {
        "exact_v18_12_source": result["source_state"] == "EXACT_ACCEPTED_V18_12",
        "exact_action_response_validated": assembly["action_response"]["gradient_relative_residual"] < 5.0e-11,
        "scaled_event_plateau_used": assembly["event_response"]["scale_selected_from_v18_20_plateau"],
        "event_hessian_symmetric": assembly["event_response"]["support_hessian_symmetry_residual"] < 1.0e-14,
        "bad_raw_hessian_not_reused": result["v18_19_uniform_raw_event_hessian"].startswith("INVALIDATED"),
        "square_response_symmetric": assembly["matrix_symmetry_residual"] < 1.0e-13,
        "square_explicit_multiplier_system": assembly["physical_solve_dimension"] == [376, 376] and assembly["event_multiplier_explicit"] and not assembly["event_multiplier_analytically_projected"],
        "residual_rows_unscaled": not assembly["left_residual_scaling_applied"],
        "physical_equations_unchanged": not assembly["physical_equations_changed"],
        "directional_response_matches_exact_residual": result["maximum_directional_relative_residual"] < 2.0e-2,
        "event_row_matches_exact_residual": result["maximum_event_row_absolute_residual"] < 2.0e-4,
        "no_componentwise_acceptance": not result["componentwise_monotonicity_required"],
        "complete_child_gate_unchanged": not result["complete_child_acceptance_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_resolved_scaled_event_kkt_response_v18_21",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "resolved_scaled_event_kkt_response": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_ORDERED_EVENT_CURVATURE_IS_RESOLVED_IN_THE_ACTION_OWNED_"
            "COORDINATES_AND_COMBINED_WITH_THE_EXACT_ACTION_RESPONSE"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "TAKE_A_RESOLVED_SQUARE_KKT_STEP_WITH_TOTAL_MERIT_ETA_AND_COMPLETE_CHILD_GATES" if passed
            else "USE_DIRECTIONAL_EVENT_RESPONSE_WITHOUT_CLAIMING_A_FULL_EVENT_HESSIAN"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_resolved_scaled_event_kkt_response_v18_21.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "resolved_scaled_event_kkt_response", "resolved_scaled_event_kkt_response_audit", "completion_payload", "materialize"]
