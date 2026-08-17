"""Deterministic rolling checkpoint for unchanged fresh N=3 curvature steps.

The driver removes only the manual one-module-per-accepted-step cadence.  It
replays v21.32 -> v21.33 bit-for-bit before advancing and retains the same
exact F376 merit, curvature validation, radius search, and complete-child
promotion gate used by v21.33.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import dual_metric_range_space_proposal
from bhsm.interface.aether_n3_eighth_expanded_radius_refreshed_continuation_v21_33 import v21_33_selected_raw_vector
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_isolated_eigenpair_event_hessian_v21_17 import (
    EXACT_RESPONSE_STEP,
    _local_eigenpair_hessian,
    _terminal_pullback,
)
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    _terminal_data,
    rayleigh_sbp_event_covector,
    rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_seventh_expanded_radius_refreshed_continuation_v21_32 import v21_32_selected_raw_vector
from bhsm.interface.aether_n3_terminal_derivative_owner_audit_v21_09 import _components


VERSION = "v21.34"
CLASSIFICATION = "BHSM_N3_FRESH_EIGENPAIR_CURVATURE_CONTINUATION_CHECKPOINT"
FULL_BHSM_COMPLETE = False
CHECKPOINT_NAME = "BHSM_N3_FRESH_EIGENPAIR_CURVATURE_CONTINUATION_CHECKPOINT.json"


def _owned_search_data() -> tuple[list[float], dict[str, Any]]:
    expanded = json.loads(Path(
        "artifacts/BHSM_N3_EIGENPAIR_CURVATURE_EXPANDED_RADIUS_V21_21.json"
    ).read_text(encoding="utf-8"))["eigenpair_curvature_expanded_radius"]
    prior = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    return expanded["dual_metric_model"]["radius_schedule"], prior["bhsm_owned_action_coordinate_radii"]


def _validated_curvature(raw: np.ndarray, scales: np.ndarray, action_radii: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    local = _terminal_data(raw[:-1])[-1]
    local_gradient, local_hessian, local_audit = _local_eigenpair_hessian(
        local, second_relative_step=1.0e-3
    )
    support, support_gradient, raw_block = _terminal_pullback(
        local_gradient, local_hessian, raw
    )
    support_scales = scales[:-1][support]
    block = raw_block / support_scales[:, None] / support_scales[None, :] / scales[-1]
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) / scales[:-1] / scales[-1]
    derived_gradient = np.zeros(375)
    derived_gradient[support] = support_gradient / support_scales / scales[-1]
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
    norm = float(np.linalg.norm(direction))
    unit = direction / norm
    exact = []
    for factor in (0.5, 1.0, 2.0):
        step = factor * EXACT_RESPONSE_STEP
        _, plus = _components(y + step * unit, scales)
        _, minus = _components(y - step * unit, scales)
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
    validated = bool(
        gradient_relative < 1.0e-6
        and max(directional.values()) < 1.0e-2
        and local_audit["eigenpair_residual_l2"] < 1.0e-9
    )
    audit = {
        "gradient_relative": gradient_relative,
        "directional": directional,
        "eigenpair_residual_l2": local_audit["eigenpair_residual_l2"],
        "coordinate_map": transform_audit,
        "validated": validated,
    }
    if not validated:
        raise ValueError("fresh isolated-eigenpair curvature did not validate")
    curvature = {
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "bhsm_owned_action_coordinate_radii": action_radii,
    }
    return curvature, audit


def _compact_step(result: dict[str, Any], source_label: str, curvature_audit: dict[str, Any]) -> dict[str, Any]:
    best = result["exact_search"]["best"]
    promotion = result["promotion"]
    child = promotion.get("child")
    return {
        "source": source_label,
        "source_exact_f376_l2": result["source"]["exact_rayleigh_f376_l2"],
        "trial_count": result["exact_search"]["trial_count"],
        "best": best,
        "promotion": {
            "attempted": promotion["attempted"],
            "promoted": promotion["promoted"],
            "child": child,
        },
        "curvature_validation": curvature_audit,
        "same_physics": bool(
            not result["physical_equations_changed"]
            and not result["event_definition_changed"]
            and not result["acceptance_gate_changed"]
        ),
    }


def _fresh_step(
    raw: np.ndarray,
    source_label: str,
    scales: np.ndarray,
    radius_schedule: list[float],
    action_radii: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray | None]:
    curvature, audit = _validated_curvature(raw, scales, action_radii)
    result = dual_metric_range_space_proposal(
        raw,
        source_label=source_label,
        curvature_override=curvature,
        radius_schedule_override=radius_schedule,
    )
    result["dual_metric_model"]["curvature_artifact"] = "IN_MEMORY_VALIDATED_FRESH_ISOLATED_EIGENPAIR"
    compact = _compact_step(result, source_label, audit)
    if not compact["same_physics"]:
        raise ValueError("fresh continuation changed physical equations or gates")
    if not result["promotion"]["promoted"]:
        return compact, None
    return compact, np.asarray([float.fromhex(value) for value in result["exact_search"]["best"]["raw_vector_hex"]])


def continuation_payload(accepted_steps: int = 1) -> dict[str, Any]:
    if accepted_steps < 1:
        raise ValueError("accepted_steps must be positive")
    scales = kkt_variable_scales()
    radius_schedule, action_radii = _owned_search_data()

    replay, replay_raw = _fresh_step(
        v21_32_selected_raw_vector(), "v21.32 equivalence replay", scales, radius_schedule, action_radii
    )
    expected = v21_33_selected_raw_vector()
    replay_equivalent = bool(
        replay_raw is not None
        and np.array_equal(replay_raw, expected)
        and replay["promotion"]["promoted"]
        and replay["promotion"]["child"]["all_pass"]
    )
    if not replay_equivalent:
        raise ValueError("rolling driver did not reproduce v21.33 exactly")

    accepted = []
    raw = expected
    source_label = "v21.33"
    stop_reason = "REQUESTED_ACCEPTED_STEPS_REACHED"
    for index in range(accepted_steps):
        step, candidate = _fresh_step(raw, source_label, scales, radius_schedule, action_radii)
        step["checkpoint_index"] = index + 1
        accepted.append(step)
        if candidate is None:
            stop_reason = "NO_PHYSICALLY_PROMOTED_DESCENT_CANDIDATE"
            break
        raw = candidate
        source_label = f"checkpoint-{index + 1}"

    promoted = [step for step in accepted if step["promotion"]["promoted"]]
    final_raw = raw
    final_norm = float(np.linalg.norm(rayleigh_square_physical_residual(final_raw * scales)))
    validation = {
        "v21_32_to_v21_33_exact_replay": replay_equivalent,
        "unchanged_25_radius_both_sign_search": bool(
            len(radius_schedule) == 25 and all(step["trial_count"] == 50 for step in accepted)
        ),
        "fresh_curvature_validated_every_step": all(
            step["curvature_validation"]["validated"] for step in accepted
        ),
        "same_physics_every_step": all(step["same_physics"] for step in accepted),
        "every_promoted_child_passes": all(
            step["promotion"]["child"]["all_pass"] for step in promoted
        ),
        "strict_exact_merit_descent": all(
            step["best"] is not None and step["best"]["exact_reduction"] > 0.0
            for step in promoted
        ),
    }
    return {
        "artifact": "BHSM_N3_FRESH_EIGENPAIR_CURVATURE_CONTINUATION_CHECKPOINT",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "equivalence_replay": replay,
        "requested_accepted_steps": accepted_steps,
        "promoted_step_count": len(promoted),
        "steps": accepted,
        "authoritative_checkpoint": {
            "source": source_label,
            "exact_rayleigh_f376_l2": final_norm,
            "raw_vector_hex": [float(value).hex() for value in final_raw],
        },
        "stop_reason": stop_reason,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "acceptance_gate_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def resume_payload(checkpoint_path: str | Path, additional_steps: int) -> dict[str, Any]:
    """Advance a validated checkpoint without recomputing accepted steps."""
    if additional_steps < 1:
        raise ValueError("additional_steps must be positive")
    path = Path(checkpoint_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not payload.get("validation_passed"):
        raise ValueError("cannot resume an unvalidated checkpoint")
    if not payload["validation"]["v21_32_to_v21_33_exact_replay"]:
        raise ValueError("checkpoint lacks the exact v21.33 equivalence replay")

    scales = kkt_variable_scales()
    radius_schedule, action_radii = _owned_search_data()
    raw = np.asarray([
        float.fromhex(value)
        for value in payload["authoritative_checkpoint"]["raw_vector_hex"]
    ])
    steps = list(payload["steps"])
    source_label = f"checkpoint-{len(steps)}"
    stop_reason = "REQUESTED_ACCEPTED_STEPS_REACHED"
    for _ in range(additional_steps):
        step, candidate = _fresh_step(
            raw, source_label, scales, radius_schedule, action_radii
        )
        step["checkpoint_index"] = len(steps) + 1
        steps.append(step)
        if candidate is None:
            stop_reason = "NO_PHYSICALLY_PROMOTED_DESCENT_CANDIDATE"
            break
        raw = candidate
        source_label = f"checkpoint-{len(steps)}"

    promoted = [step for step in steps if step["promotion"]["promoted"]]
    validation = {
        "v21_32_to_v21_33_exact_replay": True,
        "unchanged_25_radius_both_sign_search": bool(
            len(radius_schedule) == 25 and all(step["trial_count"] == 50 for step in steps)
        ),
        "fresh_curvature_validated_every_step": all(
            step["curvature_validation"]["validated"] for step in steps
        ),
        "same_physics_every_step": all(step["same_physics"] for step in steps),
        "every_promoted_child_passes": all(
            step["promotion"]["child"]["all_pass"] for step in promoted
        ),
        "strict_exact_merit_descent": all(
            step["best"] is not None and step["best"]["exact_reduction"] > 0.0
            for step in promoted
        ),
    }
    payload.update({
        "requested_accepted_steps": len(steps),
        "promoted_step_count": len(promoted),
        "steps": steps,
        "authoritative_checkpoint": {
            "source": source_label,
            "exact_rayleigh_f376_l2": float(
                np.linalg.norm(rayleigh_square_physical_residual(raw * scales))
            ),
            "raw_vector_hex": [float(value).hex() for value in raw],
        },
        "stop_reason": stop_reason,
        "validation": validation,
        "validation_passed": all(validation.values()),
    })
    return payload


def selected_raw_vector(path: str | Path = Path("artifacts") / CHECKPOINT_NAME) -> np.ndarray:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    checkpoint = payload["authoritative_checkpoint"]
    return np.asarray([float.fromhex(value) for value in checkpoint["raw_vector_hex"]])


def materialize(directory: str | Path, accepted_steps: int = 1, resume: bool = False) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / CHECKPOINT_NAME
    payload = (
        resume_payload(path, accepted_steps)
        if resume
        else continuation_payload(accepted_steps)
    )
    path.write_text(deterministic_json(payload), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", default="artifacts")
    parser.add_argument("--accepted-steps", type=int, default=1)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="append accepted steps to the validated rolling checkpoint",
    )
    args = parser.parse_args()
    print(materialize(args.artifact_dir, args.accepted_steps, resume=args.resume))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "CHECKPOINT_NAME",
    "continuation_payload",
    "resume_payload",
    "selected_raw_vector",
    "materialize",
]
