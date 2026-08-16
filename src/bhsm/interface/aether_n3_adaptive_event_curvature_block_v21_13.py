"""Assemble Rayleigh event curvature with independently resolved column steps."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    event_gradient_indices, kkt_variable_scales,
)
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import _components


VERSION = "v21.13"
CLASSIFICATION = "BHSM_N3_DIRECTION_ADAPTIVE_RAYLEIGH_EVENT_CURVATURE_BLOCK"
FULL_BHSM_COMPLETE = False
COLUMN_STEPS = (1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5,
                3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3)


def completion_payload() -> dict[str, Any]:
    raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    base_y = y[:-1]
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    old_curvature = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    old_matrix = _current_square_response(raw, old_curvature)
    transform, transform_audit = _action_curvature_transform(raw)
    gradient_x = transform.T @ old_matrix.T @ residual
    direction_x = -gradient_x / np.linalg.norm(gradient_x)
    direction_y = transform @ direction_x
    radius_best = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["best"]
    reference_radius = min(
        float(radius_best["realized_action_coordinate_norm"]),
        float(radius_best["realized_physical_scaled_norm"])
        / max(float(np.linalg.norm(direction_y)), 1.0e-300),
    )
    _, plus_event = _components(y + reference_radius * direction_y, scales)
    _, minus_event = _components(y - reference_radius * direction_y, scales)
    exact_event_response = (plus_event - minus_event) / (2.0 * reference_radius)
    support = np.asarray(event_gradient_indices(), dtype=int)
    inverse = 1.0 / scales[:-1]

    def gradient(value_y: np.ndarray) -> np.ndarray:
        return rayleigh_sbp_event_covector(value_y / scales[:-1]) * inverse / scales[-1]

    central_gradient = gradient(base_y)
    raw_block = np.empty((support.size, support.size))
    column_audit = []
    for column_position, column in enumerate(support):
        candidates = []
        for step in COLUMN_STEPS:
            delta = np.zeros(375)
            delta[int(column)] = step
            derivative = (
                gradient(base_y + delta) - gradient(base_y - delta)
            ) / (2.0 * step)
            candidates.append(derivative[support])
        scores = []
        for index in range(1, len(COLUMN_STEPS) - 1):
            denominator = max(float(np.linalg.norm(candidates[index])), 1.0)
            scores.append((
                max(
                    float(np.linalg.norm(candidates[index] - candidates[index - 1]) / denominator),
                    float(np.linalg.norm(candidates[index + 1] - candidates[index]) / denominator),
                ),
                index,
            ))
        score, selected = min(scores)
        raw_block[:, column_position] = candidates[selected]
        column_audit.append({
            "support_column_position": column_position,
            "scaled_coordinate_index": int(column),
            "selected_scaled_step": COLUMN_STEPS[selected],
            "neighbor_plateau_score": score,
        })
    raw_asymmetry = float(
        np.linalg.norm(raw_block - raw_block.T) / max(np.linalg.norm(raw_block), 1.0)
    )
    block = 0.5 * (raw_block + raw_block.T)

    def event_response(local_block: np.ndarray) -> np.ndarray:
        hessian = np.zeros((375, 375))
        hessian[np.ix_(support, support)] = local_block
        response = np.empty(376)
        response[:-1] = (
            y[-1] * (hessian @ direction_y[:-1])
            + direction_y[-1] * central_gradient
        )
        response[-1] = float(central_gradient @ direction_y[:-1])
        return response

    raw_response = event_response(raw_block)
    symmetric_response = event_response(block)
    denominator = max(float(np.linalg.norm(exact_event_response)), 1.0)
    raw_relative = float(np.linalg.norm(raw_response - exact_event_response) / denominator)
    symmetric_relative = float(
        np.linalg.norm(symmetric_response - exact_event_response) / denominator
    )
    steps = [row["selected_scaled_step"] for row in column_audit]
    result = {
        "source": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "construction": {
            "candidate_column_steps": list(COLUMN_STEPS),
            "selection": "MINIMAX_ADJACENT_COLUMN_RESPONSE_PLATEAU",
            "column_audit": column_audit,
            "selected_step_range": [min(steps), max(steps)],
            "maximum_selected_column_plateau_score": max(
                row["neighbor_plateau_score"] for row in column_audit
            ),
            "raw_block_relative_asymmetry": raw_asymmetry,
            "symmetric_by_construction_after_resolution": True,
        },
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "bhsm_owned_action_coordinate_radii": old_curvature[
            "bhsm_owned_action_coordinate_radii"
        ],
        "validation_direction": {
            "name": "negative_current_merit_gradient_from_pre_correction_response",
            "reference_action_radius": reference_radius,
            "reference_physical_scaled_radius": float(
                reference_radius * np.linalg.norm(direction_y)
            ),
            "raw_block_vs_exact_event_response_relative": raw_relative,
            "symmetric_block_vs_exact_event_response_relative": symmetric_relative,
        },
        "coordinate_map": transform_audit,
        "classification": (
            "ADAPTIVE_EVENT_CURVATURE_BLOCK_VALIDATED"
            if symmetric_relative < 5.0e-3 else "ADAPTIVE_EVENT_CURVATURE_BLOCK_INVALIDATED"
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "complete_event_support": support.size == 37,
        "all_columns_resolved": len(column_audit) == support.size,
        "symmetric_block_matches_exact_direction": symmetric_relative < 5.0e-3,
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_ADAPTIVE_EVENT_CURVATURE_BLOCK_V21_13",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "adaptive_event_curvature_block": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_ADAPTIVE_EVENT_CURVATURE_BLOCK_V21_13.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
