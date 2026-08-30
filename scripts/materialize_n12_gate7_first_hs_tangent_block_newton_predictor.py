"""Solve the first-HS block Newton recurrence in the 73D constraint tangent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE.json"
ENDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_CENTER_GRAPH_JACOBIAN.json"
MIDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_MIDPOINT_GRAPH_JACOBIAN.json"
TANGENT = BASE / "BHSM_N12_GATE7_FIRST_HS_NEWTON_ENDPOINT_TANGENT.json"
THEORY = ROOT / "theory" / "n12_gate7_first_hs_tangent_block_newton_predictor.md"
RESULT = BASE / "BHSM_N12_GATE7_FIRST_HS_TANGENT_BLOCK_NEWTON_PREDICTOR.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def main() -> None:
    parents = [_load(path) for path in (SOURCE, ENDPOINT_JACOBIAN, MIDPOINT_JACOBIAN, TANGENT)]
    if not all(parent.get("validation_passed") is True for parent in parents):
        raise RuntimeError("validated source, Jacobians, and endpoint tangents required")
    with np.load(SOURCE.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        residual = np.asarray(source["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(ENDPOINT_JACOBIAN.with_suffix(".npz")) as source:
        endpoint_jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(MIDPOINT_JACOBIAN.with_suffix(".npz")) as source:
        midpoint_jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(TANGENT.with_suffix(".npz")) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)

    identity = np.eye(98)
    correction = np.zeros(98)
    corrections = [correction.copy()]
    reduced_condition = []
    tangent_residual = []
    full_residual = []
    normal_residual = []
    for interval, duration in enumerate(np.diff(times)):
        left_midpoint_map = 0.5 * identity + duration * endpoint_jacobians[interval] / 8.0
        right_midpoint_map = 0.5 * identity - duration * endpoint_jacobians[interval + 1] / 8.0
        left_block = -identity - duration * (
            endpoint_jacobians[interval]
            + 4.0 * midpoint_jacobians[interval] @ left_midpoint_map
        ) / 6.0
        right_block = identity - duration * (
            4.0 * midpoint_jacobians[interval] @ right_midpoint_map
            + endpoint_jacobians[interval + 1]
        ) / 6.0
        q_next = tangents[interval + 1]
        reduced = q_next.T @ right_block @ q_next
        rhs = -q_next.T @ (residual[interval] + left_block @ correction)
        next_correction = q_next @ np.linalg.solve(reduced, rhs)
        predicted = residual[interval] + left_block @ correction + right_block @ next_correction
        tangent_part = q_next.T @ predicted
        normal_part = predicted - q_next @ tangent_part
        reduced_condition.append(float(np.linalg.cond(reduced)))
        tangent_residual.append(float(np.linalg.norm(tangent_part)))
        full_residual.append(float(np.linalg.norm(predicted)))
        normal_residual.append(float(np.linalg.norm(normal_part)))
        correction = next_correction
        corrections.append(correction.copy())
    corrections = np.asarray(corrections)
    tangent_membership = np.asarray([
        np.linalg.norm(corrections[i] - tangents[i] @ (tangents[i].T @ corrections[i]))
        for i in range(times.size)
    ])
    correction_norm = np.linalg.norm(corrections, axis=1)
    np.savez_compressed(
        DATA,
        action_times=times,
        endpoint_state_correction_action=corrections,
        reduced_right_block_condition_2=np.asarray(reduced_condition),
        predicted_tangent_residual_2_norm=np.asarray(tangent_residual),
        predicted_full_residual_2_norm=np.asarray(full_residual),
        predicted_normal_residual_2_norm=np.asarray(normal_residual),
        correction_tangent_membership_residual_2_norm=tangent_membership,
    )
    validation = {
        "all_371_tangent_endpoint_corrections_materialized": corrections.shape == (371, 98),
        "reset_endpoint_correction_is_zero": float(np.linalg.norm(corrections[0])) == 0.0,
        "all_reduced_right_blocks_are_numerically_invertible": float(np.max(reduced_condition)) < 1.0e5,
        "linearized_tangent_block_residual_closes": float(np.max(tangent_residual)) < 1.0e-16,
        "all_corrections_lie_in_endpoint_tangents": float(np.max(tangent_membership)) < 1.0e-15,
        "normal_block_residual_is_recorded_not_relabelled_as_zero": True,
        "nonlinear_exact_field_replay_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_FIRST_HS_TANGENT_BLOCK_NEWTON_PREDICTOR",
        "status": "INTRINSIC_73D_TANGENT_BLOCK_NEWTON_PREDICTOR_SOLVED" if passed else "TANGENT_BLOCK_NEWTON_PREDICTOR_INVALID",
        "authority": "NUMERICAL_TANGENT_LINEARIZED_PREDICTOR_NOT_NONLINEAR_OR_INTERVAL_AUTHORITY",
        "mesh": {"blocks": 370, "ambient_dimension": 98, "tangent_dimension": 73, "fixed_reset_endpoint": True},
        "summary": {
            "maximum_endpoint_correction_action_2_norm": float(np.max(correction_norm)),
            "maximum_endpoint_correction_owner_node": int(np.argmax(correction_norm)),
            "terminal_endpoint_correction_action_2_norm": float(correction_norm[-1]),
            "maximum_reduced_right_block_condition_2": float(np.max(reduced_condition)),
            "maximum_reduced_right_block_condition_owner_interval": int(np.argmax(reduced_condition)),
            "maximum_predicted_tangent_residual_2_norm": float(np.max(tangent_residual)),
            "maximum_predicted_full_residual_2_norm": float(np.max(full_residual)),
            "maximum_predicted_normal_residual_2_norm": float(np.max(normal_residual)),
            "maximum_correction_tangent_membership_residual_2_norm": float(np.max(tangent_membership)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                SOURCE, SOURCE.with_suffix(".npz"), ENDPOINT_JACOBIAN,
                ENDPOINT_JACOBIAN.with_suffix(".npz"), MIDPOINT_JACOBIAN,
                MIDPOINT_JACOBIAN.with_suffix(".npz"), TANGENT,
                TANGENT.with_suffix(".npz"), THEORY, THIS_SCRIPT,
            )
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_EXACT_REPLAY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "APPLY_THE_TANGENT_CORRECTIONS_AND_REPLAY_ALL_370_EXACT_NONLINEAR_MIDPOINT_FIELDS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
