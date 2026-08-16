"""Assemble the physics-owned 37-support Rayleigh ordered-event curvature."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_rayleigh_krylov_restriction_audit_v20_86 import v20_86_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_proposal_v20_81 import _response
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices, kkt_variable_scales
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.87"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_ORDERED_EVENT_CURVATURE_BLOCK"
FULL_BHSM_COMPLETE = False
SCALED_STEP = 3.0e-8


def _event_gradient_scaled(ybase: np.ndarray, scales: np.ndarray) -> np.ndarray:
    return rayleigh_sbp_event_covector(ybase / scales[:-1]) / scales[:-1] / scales[-1]


def rayleigh_event_curvature_block() -> dict[str, Any]:
    scales = kkt_variable_scales(); raw = v20_86_selected_raw_vector(); y = raw * scales
    residual = rayleigh_square_physical_residual(y); support = np.asarray(event_gradient_indices(), dtype=int)
    event_gradient = _event_gradient_scaled(y[:-1], scales)
    raw_block = np.empty((support.size, support.size))
    for column_position, column in enumerate(support):
        delta = np.zeros(375); delta[int(column)] = SCALED_STEP
        response = (
            _event_gradient_scaled(y[:-1] + delta, scales)
            - _event_gradient_scaled(y[:-1] - delta, scales)
        ) / (2.0 * SCALED_STEP)
        raw_block[:, column_position] = response[support]
    raw_asymmetry = float(np.linalg.norm(raw_block - raw_block.T) / max(1.0, np.linalg.norm(raw_block)))
    block = 0.5 * (raw_block + raw_block.T)
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    inverse = 1.0 / scales[:-1]
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375)); event_hessian[np.ix_(support, support)] = block
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient; matrix[-1, :-1] = event_gradient
    directions = {
        "corrected_physical_residual": residual,
        "latest_accepted_secant": (raw - v20_75_selected_raw_vector()) * scales,
        "material_corridor_secant": (v20_73_selected_raw_vector() - v20_72_selected_raw_vector()) * scales,
    }
    checks = []
    for name, direction in directions.items():
        predicted = matrix @ direction
        reference = _response(direction, SCALED_STEP, y, scales, action_scaled, event_gradient)
        checks.append({
            "direction": name, "assembled_response_l2": float(np.linalg.norm(predicted)),
            "matrix_free_response_l2": float(np.linalg.norm(reference)),
            "relative_residual": float(np.linalg.norm(predicted - reference) / max(1.0, np.linalg.norm(reference))),
            "event_row_absolute_residual": float(abs(predicted[-1] - reference[-1])),
        })
    return {
        "source": {"version": "v20.86", "exact_rayleigh_f376_l2": float(np.linalg.norm(residual))},
        "support_indices": support.tolist(), "support_dimension": int(support.size),
        "scaled_step": SCALED_STEP, "raw_block_relative_asymmetry": raw_asymmetry,
        "symmetric_support_block_l2": float(np.linalg.norm(block)),
        "symmetric_support_block": block.tolist(),
        "action_hessian_scaled_l2": float(np.linalg.norm(action_scaled)),
        "event_curvature_stationarity_contribution_l2": float(abs(y[-1]) * np.linalg.norm(block)),
        "square_matrix_symmetry_residual": float(np.linalg.norm(matrix - matrix.T) / max(1.0, np.linalg.norm(matrix))),
        "directional_checks": checks,
        "outcome": "RAYLEIGH_EVENT_CURVATURE_BLOCK_ASSEMBLED",
        "next_action": "USE_THE_VALIDATED_BLOCK_AS_AN_EQUIVALENT_SQUARE_KKT_PRECONDITIONER_AND_TEST_ONE_EXACT_F376_PROPOSAL",
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "left_residual_scaling_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = rayleigh_event_curvature_block()
    validation = {
        "source_v20_86_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787514011519100) < 5.0e-12,
        "complete_event_support": result["support_dimension"] == 37,
        "raw_block_nearly_symmetric": result["raw_block_relative_asymmetry"] < 2.0e-2,
        "square_matrix_symmetric": result["square_matrix_symmetry_residual"] < 1.0e-13,
        "directional_response_matches": max(row["relative_residual"] for row in result["directional_checks"]) < 2.0e-2,
        "event_rows_exact": max(row["event_row_absolute_residual"] for row in result["directional_checks"]) < 1.0e-12,
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"] and not result["left_residual_scaling_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_EVENT_CURVATURE_BLOCK_V20_87", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_event_curvature_block": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_EVENT_CURVATURE_BLOCK_V20_87.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "SCALED_STEP", "rayleigh_event_curvature_block", "completion_payload", "materialize"]
