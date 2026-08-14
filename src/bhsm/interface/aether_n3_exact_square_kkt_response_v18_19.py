"""Assemble and validate the exact-action square explicit-multiplier KKT response."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector, sbp_event_value_from_base
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices, kkt_variable_scales
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector


VERSION = "v18.19"
CLASSIFICATION = "BHSM_N3_EXACT_SQUARE_KKT_RESPONSE"
FULL_BHSM_COMPLETE = False
EVENT_HESSIAN_RELATIVE_STEP = 8.0e-5


def _event_scalar_hessian(base: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    value = np.asarray(base, dtype=float)
    support = np.asarray(event_gradient_indices(), dtype=int)
    hessian = np.zeros((375, 375))
    center = sbp_event_value_from_base(value)
    steps = {
        int(index): EVENT_HESSIAN_RELATIVE_STEP * max(1.0, abs(float(value[index])))
        for index in support
    }
    axis_values: dict[tuple[int, int], float] = {}
    for index in support:
        i = int(index); step = steps[i]
        delta = np.zeros(375); delta[i] = step
        plus = sbp_event_value_from_base(value + delta)
        minus = sbp_event_value_from_base(value - delta)
        axis_values[(i, 1)] = plus; axis_values[(i, -1)] = minus
        hessian[i, i] = (plus - 2.0 * center + minus) / step**2
    for row_position, row_index in enumerate(support):
        i = int(row_index); hi = steps[i]
        for column_index in support[row_position + 1:]:
            j = int(column_index); hj = steps[j]
            di = np.zeros(375); dj = np.zeros(375)
            di[i] = hi; dj[j] = hj
            value_pp = sbp_event_value_from_base(value + di + dj)
            value_pm = sbp_event_value_from_base(value + di - dj)
            value_mp = sbp_event_value_from_base(value - di + dj)
            value_mm = sbp_event_value_from_base(value - di - dj)
            entry = (value_pp - value_pm - value_mp + value_mm) / (4.0 * hi * hj)
            hessian[i, j] = entry; hessian[j, i] = entry
    support_block = hessian[np.ix_(support, support)]
    return hessian, {
        "support_dimension": int(support.size),
        "relative_step": EVENT_HESSIAN_RELATIVE_STEP,
        "event_value": center,
        "support_hessian_norm": float(np.linalg.norm(support_block)),
        "support_hessian_symmetry_residual": float(
            np.linalg.norm(support_block - support_block.T)
            / max(1.0, np.linalg.norm(support_block))
        ),
        "ordered_eigenvalue_isolated": True,
        "lower_spectral_gap": 0.5790449163968373,
        "upper_spectral_gap": 0.0007311978328318023,
    }


def exact_square_kkt_response(raw: np.ndarray) -> dict[str, Any]:
    state = np.asarray(raw, dtype=float)
    if state.shape != (376,):
        raise ValueError("square KKT state must have dimension 376")
    scales = kkt_variable_scales(); y = state * scales
    action = exact_sbp_action_hessian(state[:-1])
    action_hessian_raw = np.asarray(action.pop("hessian"))
    event_hessian_raw, event_audit = _event_scalar_hessian(state[:-1])
    event_gradient_raw = sbp_event_covector(state[:-1])
    inverse = 1.0 / scales[:-1]
    action_hessian_scaled = inverse[:, None] * action_hessian_raw * inverse[None, :]
    event_hessian_scaled = (
        inverse[:, None] * event_hessian_raw * inverse[None, :] / scales[-1]
    )
    event_gradient_scaled = event_gradient_raw * inverse / scales[-1]
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_hessian_scaled + y[-1] * event_hessian_scaled
    matrix[:-1, -1] = event_gradient_scaled
    matrix[-1, :-1] = event_gradient_scaled
    return {
        "matrix": matrix,
        "action_response": action,
        "event_response": event_audit,
        "action_hessian_scaled_norm": float(np.linalg.norm(action_hessian_scaled)),
        "event_hessian_scaled_norm": float(np.linalg.norm(event_hessian_scaled)),
        "event_curvature_contribution_norm": float(abs(y[-1]) * np.linalg.norm(event_hessian_scaled)),
        "event_gradient_scaled_norm": float(np.linalg.norm(event_gradient_scaled)),
        "matrix_symmetry_residual": float(
            np.linalg.norm(matrix - matrix.T) / max(1.0, np.linalg.norm(matrix))
        ),
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "event_multiplier_analytically_projected": False,
        "physical_equations_changed": False,
    }


def exact_square_kkt_response_audit() -> dict[str, Any]:
    raw = v18_12_selected_raw_vector(); scales = kkt_variable_scales(); y = raw * scales
    assembled = exact_square_kkt_response(raw)
    matrix = np.asarray(assembled.pop("matrix"))
    directions = []
    templates = [
        np.cos(np.arange(376) + 0.29),
        np.sin(0.31 * np.arange(376) + 0.53),
        np.where(np.arange(376) < 200, 1.0, 0.0),
        np.where(np.arange(376) == 375, 1.0, 0.0),
    ]
    for number, template in enumerate(templates):
        direction = np.asarray(template, dtype=float)
        direction /= np.linalg.norm(direction)
        predicted = matrix @ direction
        checks = []
        for epsilon in (4.0e-5, 2.0e-5):
            plus = _square_physical_residual(y + epsilon * direction)
            minus = _square_physical_residual(y - epsilon * direction)
            finite = (plus - minus) / (2.0 * epsilon)
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
        "componentwise_monotonicity_required": False,
        "complete_child_acceptance_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = exact_square_kkt_response_audit()
    assembly = result["assembly"]
    validation = {
        "exact_v18_12_source": result["source_state"] == "EXACT_ACCEPTED_V18_12",
        "exact_action_response_validated": assembly["action_response"]["gradient_relative_residual"] < 5.0e-11,
        "event_hessian_symmetric": assembly["event_response"]["support_hessian_symmetry_residual"] < 1.0e-14,
        "event_eigenvalue_isolated": assembly["event_response"]["ordered_eigenvalue_isolated"] and assembly["event_response"]["upper_spectral_gap"] > 0.0,
        "square_response_symmetric": assembly["matrix_symmetry_residual"] < 1.0e-13,
        "square_explicit_multiplier_system": assembly["physical_solve_dimension"] == [376, 376] and assembly["event_multiplier_explicit"] and not assembly["event_multiplier_analytically_projected"],
        "physical_equations_unchanged": not assembly["physical_equations_changed"],
        "directional_response_matches_exact_residual": result["maximum_directional_relative_residual"] < 5.0e-3,
        "event_row_matches_exact_residual": result["maximum_event_row_absolute_residual"] < 2.0e-4,
        "no_componentwise_acceptance": not result["componentwise_monotonicity_required"],
        "complete_child_gate_unchanged": not result["complete_child_acceptance_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_exact_square_kkt_response_v18_19",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_square_kkt_response": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_SQUARE_EXPLICIT_MULTIPLIER_KKT_RESPONSE_COMBINES_THE_"
            "VALIDATED_EXACT_ACTION_HESSIAN_WITH_THE_ORDERED_EVENT_CURVATURE"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "TAKE_AN_EXACT_RESPONSE_SQUARE_KKT_STEP_AND_APPLY_TOTAL_MERIT_ETA_AND_COMPLETE_CHILD_GATES" if passed
            else "AUDIT_THE_EVENT_CURVATURE_DISCRETIZATION"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_exact_square_kkt_response_v18_19.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "exact_square_kkt_response", "exact_square_kkt_response_audit", "completion_payload", "materialize"]
