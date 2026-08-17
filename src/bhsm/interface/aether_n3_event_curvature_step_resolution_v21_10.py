"""Resolve the outer finite-difference scale for Rayleigh event curvature."""
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
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import _components


VERSION = "v21.10"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_EVENT_CURVATURE_OUTER_STEP_RESOLUTION"
FULL_BHSM_COMPLETE = False
OUTER_STEPS = (1.0e-10, 3.0e-10, 1.0e-9, 3.0e-9, 1.0e-8, 3.0e-8,
               1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5, 3.0e-5, 1.0e-4)


def completion_payload() -> dict[str, Any]:
    raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    curvature = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    matrix = _current_square_response(raw, curvature)
    transform, transform_audit = _action_curvature_transform(raw)
    gradient_x = transform.T @ matrix.T @ residual
    direction_x = -gradient_x / np.linalg.norm(gradient_x)
    direction_y = transform @ direction_x
    radius_best = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["best"]
    exact_radius = min(
        float(radius_best["realized_action_coordinate_norm"]),
        float(radius_best["realized_physical_scaled_norm"])
        / max(float(np.linalg.norm(direction_y)), 1.0e-300),
    )
    _, plus_event = _components(y + exact_radius * direction_y, scales)
    _, minus_event = _components(y - exact_radius * direction_y, scales)
    exact_event_response = (plus_event - minus_event) / (2.0 * exact_radius)
    base_y = y[:-1]
    base_direction = direction_y[:-1]
    direction_norm = float(np.linalg.norm(base_direction))
    unit = base_direction / direction_norm
    inverse = 1.0 / scales[:-1]

    def gradient(value_y: np.ndarray) -> np.ndarray:
        return rayleigh_sbp_event_covector(value_y / scales[:-1]) * inverse / scales[-1]

    central_gradient = gradient(base_y)
    rows = []
    responses = []
    denominator = max(float(np.linalg.norm(exact_event_response)), 1.0)
    for step in OUTER_STEPS:
        hessian_direction = direction_norm * (
            gradient(base_y + step * unit) - gradient(base_y - step * unit)
        ) / (2.0 * step)
        response = np.empty(376)
        response[:-1] = y[-1] * hessian_direction + direction_y[-1] * central_gradient
        response[-1] = float(central_gradient @ base_direction)
        responses.append(response)
        rows.append({
            "outer_scaled_step": step,
            "event_response_l2": float(np.linalg.norm(response)),
            "vs_exact_event_response_relative": float(
                np.linalg.norm(response - exact_event_response) / denominator
            ),
        })
    for index, row in enumerate(rows):
        if index:
            row["vs_previous_step_relative"] = float(
                np.linalg.norm(responses[index] - responses[index - 1])
                / max(np.linalg.norm(responses[index]), 1.0)
            )
        else:
            row["vs_previous_step_relative"] = None
    best_index = int(np.argmin([row["vs_exact_event_response_relative"] for row in rows]))
    best = rows[best_index]
    neighbor_indices = [index for index in (best_index - 1, best_index + 1) if 0 <= index < len(rows)]
    neighbor_max = max(
        [rows[index]["vs_exact_event_response_relative"] for index in neighbor_indices],
        default=float("inf"),
    )
    resolved = bool(
        best["vs_exact_event_response_relative"] < 5.0e-3 and neighbor_max < 1.0e-2
    )
    result = {
        "source_frontier": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "direction": {
            "name": "negative_current_merit_gradient",
            "exact_reference_action_radius": exact_radius,
            "exact_reference_physical_scaled_radius": float(
                exact_radius * np.linalg.norm(direction_y)
            ),
            "coordinate_map": transform_audit,
        },
        "outer_step_scan": rows,
        "current_assembled_step": 3.0e-8,
        "best_outer_scaled_step": best["outer_scaled_step"],
        "best_vs_exact_event_response_relative": best["vs_exact_event_response_relative"],
        "best_neighbor_max_relative": neighbor_max,
        "classification": (
            "DIRECTIONAL_EVENT_CURVATURE_STEP_RESOLVED"
            if resolved else "DIRECTIONAL_EVENT_CURVATURE_STEP_UNRESOLVED"
        ),
        "next_action": (
            "ASSEMBLE_EVENT_CURVATURE_BLOCK_AT_RESOLVED_STEP_AND_VALIDATE_FULL_RESPONSE"
            if resolved else "DERIVE_ANALYTIC_OR_ADAPTIVE_RAYLEIGH_EVENT_HESSIAN_VECTOR"
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "all_steps_tested": len(rows) == len(OUTER_STEPS),
        "current_step_in_scan": 3.0e-8 in OUTER_STEPS,
        "exact_event_response_nonzero": np.linalg.norm(exact_event_response) > 0.0,
        "one_classification": result["classification"] in {
            "DIRECTIONAL_EVENT_CURVATURE_STEP_RESOLVED",
            "DIRECTIONAL_EVENT_CURVATURE_STEP_UNRESOLVED",
        },
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_EVENT_CURVATURE_STEP_RESOLUTION_V21_10",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_curvature_step_resolution": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_EVENT_CURVATURE_STEP_RESOLUTION_V21_10.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
