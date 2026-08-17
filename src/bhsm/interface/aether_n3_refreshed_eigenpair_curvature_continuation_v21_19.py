"""Refresh the validated eigenpair event Hessian at v21.18 and continue N=3."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import (
    _action_curvature_transform,
)
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import (
    dual_metric_range_space_proposal,
)
from bhsm.interface.aether_n3_eigenpair_curvature_dual_metric_proposal_v21_18 import (
    v21_18_selected_raw_vector,
)
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import (
    exact_sbp_action_hessian,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_isolated_eigenpair_event_hessian_v21_17 import (
    EXACT_RESPONSE_STEP,
    SECOND_DERIVATIVE_RELATIVE_STEPS,
    _local_eigenpair_hessian,
    _terminal_pullback,
)
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    _terminal_data,
    rayleigh_sbp_event_covector,
    rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import (
    _components,
)


VERSION = "v21.19"
CLASSIFICATION = "BHSM_N3_REFRESHED_EIGENPAIR_CURVATURE_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v21_19_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_REFRESHED_EIGENPAIR_CURVATURE_CONTINUATION_V21_19.json"
    ).read_text(encoding="utf-8"))["refreshed_eigenpair_curvature_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v21.19 has no physically promoted state")
    return np.asarray([
        float.fromhex(value)
        for value in payload["exact_search"]["best"]["raw_vector_hex"]
    ])


def _radius_schedule() -> list[dict[str, float | str]]:
    trials = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]["exact_search"]["trials"]
    unique = {}
    for row in trials:
        unique.setdefault(row["radius_class"], row)
    return [
        {
            "label": label,
            "action_radius": float(row["bhsm_action_coordinate_radius"]),
            "physical_radius": float(row["bhsm_physical_scaled_radius"]),
        }
        for label, row in sorted(unique.items())
    ]


def completion_payload() -> dict[str, Any]:
    raw = v21_18_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    local = _terminal_data(raw[:-1])[-1]
    blocks = []
    gradients = []
    local_audits = []
    support = None
    for relative_step in SECOND_DERIVATIVE_RELATIVE_STEPS:
        gradient, local_hessian, audit = _local_eigenpair_hessian(
            local, second_relative_step=relative_step
        )
        support, support_gradient, raw_block = _terminal_pullback(
            gradient, local_hessian, raw
        )
        support_scales = scales[:-1][support]
        gradients.append(support_gradient / support_scales / scales[-1])
        blocks.append(
            raw_block / support_scales[:, None] / support_scales[None, :] / scales[-1]
        )
        local_audits.append(audit)
    assert support is not None
    block = blocks[1]
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) / scales[:-1] / scales[-1]
    derived_gradient = np.zeros(375)
    derived_gradient[support] = gradients[1]
    gradient_relative = float(
        np.linalg.norm(derived_gradient - event_gradient)
        / max(np.linalg.norm(event_gradient), 1.0)
    )

    inverse = 1.0 / scales[:-1]
    action = exact_sbp_action_hessian(raw[:-1])
    action_raw = np.asarray(action.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375))
    event_hessian[np.ix_(support, support)] = block
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient
    matrix[-1, :-1] = event_gradient
    transform, transform_audit = _action_curvature_transform(raw)
    gradient_x = transform.T @ matrix.T @ residual
    direction = transform @ (-gradient_x / np.linalg.norm(gradient_x))
    direction_norm = float(np.linalg.norm(direction))
    unit = direction / direction_norm
    exact_responses = []
    for factor in (0.5, 1.0, 2.0):
        step = factor * EXACT_RESPONSE_STEP
        _, plus = _components(y + step * unit, scales)
        _, minus = _components(y - step * unit, scales)
        exact_responses.append(direction_norm * (plus - minus) / (2.0 * step))
    exact = exact_responses[1]
    predicted = np.empty(376)
    predicted[:-1] = y[-1] * (event_hessian @ direction[:-1]) + direction[-1] * event_gradient
    predicted[-1] = float(event_gradient @ direction[:-1])
    denominator = max(float(np.linalg.norm(exact)), 1.0)
    directional = {
        "derived_vs_exact_relative": float(np.linalg.norm(predicted - exact) / denominator),
        "exact_half_vs_reference_relative": float(
            np.linalg.norm(exact_responses[0] - exact) / denominator
        ),
        "exact_double_vs_reference_relative": float(
            np.linalg.norm(exact_responses[2] - exact) / denominator
        ),
        "block_action_relative_across_steps": [
            float(np.linalg.norm((candidate - block) @ direction[support]))
            / max(float(np.linalg.norm(block @ direction[support])), 1.0)
            for candidate in blocks
        ],
    }
    curvature_valid = bool(
        gradient_relative < 1.0e-6
        and max(directional["block_action_relative_across_steps"]) < 2.0e-2
        and directional["exact_half_vs_reference_relative"] < 1.0e-2
        and directional["exact_double_vs_reference_relative"] < 1.0e-2
        and directional["derived_vs_exact_relative"] < 1.0e-2
    )
    if not curvature_valid:
        raise ValueError("refreshed v21.19 eigenpair curvature did not validate")

    prior = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    curvature = {
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "bhsm_owned_action_coordinate_radii": prior[
            "bhsm_owned_action_coordinate_radii"
        ],
    }
    schedule = _radius_schedule()
    result = dual_metric_range_space_proposal(
        raw,
        source_label="v21.18",
        curvature_override=curvature,
        radius_schedule_override=schedule,
    )
    result["dual_metric_model"]["curvature_artifact"] = (
        "IN_MEMORY_VALIDATED_V21_19_ISOLATED_EIGENPAIR_REFRESH"
    )
    result["curvature_refresh_validation"] = {
        "gradient_relative": gradient_relative,
        "local_step_audits": local_audits,
        "directional": directional,
        "coordinate_map": transform_audit,
        "validated": curvature_valid,
    }
    best = result["exact_search"]["best"]
    validation = {
        "source_v21_18_reproduced": abs(source_norm - 0.782564196598096) < 5.0e-12,
        "refreshed_curvature_validated": curvature_valid,
        "natural_radius_interval_reused": len(schedule) == 17,
        "both_signs_all_radii": result["exact_search"]["trial_count"] == 34,
        "exact_rows_decide": result["exact_search"][
            "original_unweighted_376_rows_authoritative"
        ],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"]
        or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_REFRESHED_EIGENPAIR_CURVATURE_CONTINUATION_V21_19",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "refreshed_eigenpair_curvature_continuation": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_REFRESHED_EIGENPAIR_CURVATURE_CONTINUATION_V21_19.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v21_19_selected_raw_vector", "completion_payload", "materialize",
]
