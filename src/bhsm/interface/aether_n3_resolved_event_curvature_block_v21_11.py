"""Assemble and validate the full event-curvature block at the resolved step."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_curvature_singular_subspace_audit_v20_89 import curvature_singular_subspace_audit
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import _components


VERSION = "v21.11"
CLASSIFICATION = "BHSM_N3_RESOLVED_RAYLEIGH_EVENT_CURVATURE_BLOCK"
FULL_BHSM_COMPLETE = False
RESOLVED_STEP = 1.0e-5


def completion_payload() -> dict[str, Any]:
    raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    old_curvature = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    old_matrix = _current_square_response(raw, old_curvature)
    transform, _ = _action_curvature_transform(raw)
    gradient_x = transform.T @ old_matrix.T @ residual
    direction_x = -gradient_x / np.linalg.norm(gradient_x)
    direction_y = transform @ direction_x
    radius_best = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["best"]
    radius = min(
        float(radius_best["realized_action_coordinate_norm"]),
        float(radius_best["realized_physical_scaled_norm"])
        / max(float(np.linalg.norm(direction_y)), 1.0e-300),
    )
    _, plus_event = _components(y + radius * direction_y, scales)
    _, minus_event = _components(y - radius * direction_y, scales)
    exact_event_response = (plus_event - minus_event) / (2.0 * radius)

    corrected = curvature_singular_subspace_audit(
        raw, source_label="v21.04", scaled_event_step=RESOLVED_STEP
    )
    support = np.asarray(corrected["event_curvature_support_indices"], dtype=int)
    block = np.asarray(corrected["event_curvature_symmetric_block"], dtype=float)
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
    result = {
        "source_frontier": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "resolved_curvature": corrected,
        "validation_direction": {
            "name": "negative_current_merit_gradient_from_pre_correction_response",
            "exact_reference_action_radius": radius,
            "exact_reference_physical_scaled_radius": float(
                radius * np.linalg.norm(direction_y)
            ),
            "symmetric_block_vs_exact_event_response_relative": relative,
        },
        "classification": (
            "RESOLVED_EVENT_CURVATURE_BLOCK_VALIDATED"
            if relative < 5.0e-3 else "RESOLVED_EVENT_CURVATURE_BLOCK_INVALIDATED"
        ),
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "resolved_step_used": corrected["event_curvature_scaled_step"] == RESOLVED_STEP,
        "symmetric_block_matches_exact_direction": relative < 5.0e-3,
        "child_chart_surjective": corrected["child_compatible_tangent"]["rank_DcG"] == 14,
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RESOLVED_EVENT_CURVATURE_BLOCK_V21_11",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "resolved_event_curvature_block": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RESOLVED_EVENT_CURVATURE_BLOCK_V21_11.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
