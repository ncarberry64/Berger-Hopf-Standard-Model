"""Refresh the eigenpair curvature at v21.28 after predictive contraction."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import dual_metric_range_space_proposal
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fourth_expanded_predictive_continuation_v21_28 import v21_28_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_isolated_eigenpair_event_hessian_v21_17 import EXACT_RESPONSE_STEP, _local_eigenpair_hessian, _terminal_pullback
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import _terminal_data, rayleigh_sbp_event_covector, rayleigh_square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import _components


VERSION = "v21.29"
CLASSIFICATION = "BHSM_N3_FIFTH_EXPANDED_RADIUS_REFRESHED_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v21_29_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_FIFTH_EXPANDED_RADIUS_REFRESHED_CONTINUATION_V21_29.json"
    ).read_text(encoding="utf-8"))["fifth_expanded_radius_refreshed_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v21.29 has no physically promoted state")
    return np.asarray([float.fromhex(v) for v in payload["exact_search"]["best"]["raw_vector_hex"]])


def completion_payload() -> dict[str, Any]:
    raw = v21_28_selected_raw_vector(); scales = kkt_variable_scales(); y = raw * scales
    residual = rayleigh_square_physical_residual(y); source_norm = float(np.linalg.norm(residual))
    local = _terminal_data(raw[:-1])[-1]
    local_gradient, local_hessian, local_audit = _local_eigenpair_hessian(local, second_relative_step=1.0e-3)
    support, support_gradient, raw_block = _terminal_pullback(local_gradient, local_hessian, raw)
    support_scales = scales[:-1][support]
    block = raw_block / support_scales[:, None] / support_scales[None, :] / scales[-1]
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) / scales[:-1] / scales[-1]
    derived_gradient = np.zeros(375); derived_gradient[support] = support_gradient / support_scales / scales[-1]
    gradient_relative = float(np.linalg.norm(derived_gradient - event_gradient) / max(np.linalg.norm(event_gradient), 1.0))

    inverse = 1.0 / scales[:-1]
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375)); event_hessian[np.ix_(support, support)] = block
    matrix = np.zeros((376, 376)); matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient; matrix[-1, :-1] = event_gradient
    transform, transform_audit = _action_curvature_transform(raw)
    gradient_x = transform.T @ matrix.T @ residual
    direction = transform @ (-gradient_x / np.linalg.norm(gradient_x))
    norm = float(np.linalg.norm(direction)); unit = direction / norm; exact = []
    for factor in (0.5, 1.0, 2.0):
        step = factor * EXACT_RESPONSE_STEP
        _, plus = _components(y + step * unit, scales); _, minus = _components(y - step * unit, scales)
        exact.append(norm * (plus - minus) / (2.0 * step))
    predicted = np.empty(376)
    predicted[:-1] = y[-1] * (event_hessian @ direction[:-1]) + direction[-1] * event_gradient
    predicted[-1] = float(event_gradient @ direction[:-1])
    denominator = max(float(np.linalg.norm(exact[1])), 1.0)
    directional = {
        "derived_vs_exact_relative": float(np.linalg.norm(predicted - exact[1]) / denominator),
        "exact_half_vs_reference_relative": float(np.linalg.norm(exact[0] - exact[1]) / denominator),
        "exact_double_vs_reference_relative": float(np.linalg.norm(exact[2] - exact[1]) / denominator),
    }
    curvature_valid = bool(gradient_relative < 1.0e-6 and max(directional.values()) < 1.0e-2 and local_audit["eigenpair_residual_l2"] < 1.0e-9)
    if not curvature_valid:
        raise ValueError("v21.29 refreshed curvature did not validate")
    previous = json.loads(Path(
        "artifacts/BHSM_N3_EIGENPAIR_CURVATURE_EXPANDED_RADIUS_V21_21.json"
    ).read_text(encoding="utf-8"))["eigenpair_curvature_expanded_radius"]
    schedule = previous["dual_metric_model"]["radius_schedule"]
    prior = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    curvature = {
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "bhsm_owned_action_coordinate_radii": prior["bhsm_owned_action_coordinate_radii"],
    }
    result = dual_metric_range_space_proposal(
        raw, source_label="v21.28", curvature_override=curvature,
        radius_schedule_override=schedule,
    )
    result["dual_metric_model"]["curvature_artifact"] = "IN_MEMORY_VALIDATED_V21_29_EIGENPAIR_REFRESH"
    result["curvature_refresh_validation"] = {
        "gradient_relative": gradient_relative, "directional": directional,
        "local_audit": local_audit, "coordinate_map": transform_audit,
        "validated": curvature_valid,
    }
    best = result["exact_search"]["best"]
    validation = {
        "source_v21_28_reproduced": abs(source_norm - 0.780582944226373) < 5.0e-12,
        "curvature_validated": curvature_valid,
        "same_history_owned_interval": len(schedule) == 25,
        "both_signs_all_points": result["exact_search"]["trial_count"] == 50,
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_FIFTH_EXPANDED_RADIUS_REFRESHED_CONTINUATION_V21_29", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "fifth_expanded_radius_refreshed_continuation": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_FIFTH_EXPANDED_RADIUS_REFRESHED_CONTINUATION_V21_29.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8"); return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v21_29_selected_raw_vector", "completion_payload", "materialize"]


