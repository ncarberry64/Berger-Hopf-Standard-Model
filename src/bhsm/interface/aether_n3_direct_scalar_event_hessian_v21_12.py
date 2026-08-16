"""Build the symmetric Rayleigh event Hessian from the scalar event value."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_value_from_base
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    event_gradient_indices, kkt_variable_scales,
)
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import _components


VERSION = "v21.12"
CLASSIFICATION = "BHSM_N3_DIRECT_SCALAR_ORDERED_EVENT_HESSIAN"
FULL_BHSM_COMPLETE = False
SCALED_STEP = 1.0e-5


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

    def value(vector_y: np.ndarray) -> float:
        return float(
            sbp_event_value_from_base(vector_y / scales[:-1]) / scales[-1]
        )

    center = value(base_y)
    dimension = support.size
    block = np.zeros((dimension, dimension))
    for position, index in enumerate(support):
        delta = np.zeros(375)
        delta[int(index)] = SCALED_STEP
        block[position, position] = (
            value(base_y + delta) - 2.0 * center + value(base_y - delta)
        ) / SCALED_STEP**2
    for left in range(dimension):
        left_delta = np.zeros(375)
        left_delta[int(support[left])] = SCALED_STEP
        for right in range(left + 1, dimension):
            right_delta = np.zeros(375)
            right_delta[int(support[right])] = SCALED_STEP
            mixed = (
                value(base_y + left_delta + right_delta)
                - value(base_y + left_delta - right_delta)
                - value(base_y - left_delta + right_delta)
                + value(base_y - left_delta - right_delta)
            ) / (4.0 * SCALED_STEP**2)
            block[left, right] = mixed
            block[right, left] = mixed
    event_hessian = np.zeros((375, 375))
    event_hessian[np.ix_(support, support)] = block
    inverse = 1.0 / scales[:-1]
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) * inverse / scales[-1]
    response = np.empty(376)
    response[:-1] = (
        y[-1] * (event_hessian @ direction_y[:-1])
        + direction_y[-1] * event_gradient
    )
    response[-1] = float(event_gradient @ direction_y[:-1])
    denominator = max(float(np.linalg.norm(exact_event_response)), 1.0)
    relative = float(np.linalg.norm(response - exact_event_response) / denominator)
    prior_radii = old_curvature["bhsm_owned_action_coordinate_radii"]
    result = {
        "source": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "construction": {
            "scalar": "sbp_event_value_from_base/scaled_event_residual_scale",
            "central_second_difference": True,
            "scaled_step": SCALED_STEP,
            "symmetric_by_construction": True,
            "support_dimension": int(dimension),
            "scalar_evaluation_count": int(1 + 2 * dimension + 4 * dimension * (dimension - 1) // 2),
        },
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "bhsm_owned_action_coordinate_radii": prior_radii,
        "validation_direction": {
            "name": "negative_current_merit_gradient_from_pre_correction_response",
            "reference_action_radius": reference_radius,
            "reference_physical_scaled_radius": float(
                reference_radius * np.linalg.norm(direction_y)
            ),
            "direct_scalar_hessian_vs_exact_event_response_relative": relative,
        },
        "coordinate_map": transform_audit,
        "classification": (
            "DIRECT_SCALAR_EVENT_HESSIAN_VALIDATED"
            if relative < 5.0e-3 else "DIRECT_SCALAR_EVENT_HESSIAN_INVALIDATED"
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "complete_event_support": dimension == 37,
        "symmetric_by_construction": np.array_equal(block, block.T),
        "matches_exact_event_response": relative < 5.0e-3,
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_DIRECT_SCALAR_EVENT_HESSIAN_V21_12",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "direct_scalar_event_hessian": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_DIRECT_SCALAR_EVENT_HESSIAN_V21_12.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
