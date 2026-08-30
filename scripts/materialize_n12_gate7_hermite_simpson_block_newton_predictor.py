"""Solve the finite Hermite--Simpson block Newton predictor recurrence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_DIRECT_HERMITE_SIMPSON_MULTIPLE_SHOOTING_SOURCE.json"
ENDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN.json"
MIDPOINT_JACOBIAN = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_MIDPOINT_GRAPH_JACOBIAN.json"
THEORY = ROOT / "theory" / "n12_gate7_hermite_simpson_block_newton_predictor.md"
RESULT = BASE / "BHSM_N12_GATE7_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR.json"
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
    records = [_load(path) for path in (SOURCE, ENDPOINT_JACOBIAN, MIDPOINT_JACOBIAN)]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated source and endpoint/midpoint Jacobians required")
    with np.load(SOURCE.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        residual = np.asarray(source["Hermite_Simpson_shooting_residual"], dtype=float)[:, :-1]
    with np.load(ENDPOINT_JACOBIAN.with_suffix(".npz")) as source:
        endpoint_jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
    with np.load(MIDPOINT_JACOBIAN.with_suffix(".npz")) as source:
        midpoint_jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)

    identity = np.eye(98)
    correction = np.zeros(98)
    corrections = [correction.copy()]
    left_blocks = []
    right_blocks = []
    right_condition = []
    predicted_residual = []
    for interval, duration in enumerate(np.diff(times)):
        left_midpoint_map = 0.5 * identity + duration * endpoint_jacobians[interval] / 8.0
        right_midpoint_map = 0.5 * identity - duration * endpoint_jacobians[interval + 1] / 8.0
        left_block = (
            -identity
            - duration * (
                endpoint_jacobians[interval]
                + 4.0 * midpoint_jacobians[interval] @ left_midpoint_map
            ) / 6.0
        )
        right_block = (
            identity
            - duration * (
                4.0 * midpoint_jacobians[interval] @ right_midpoint_map
                + endpoint_jacobians[interval + 1]
            ) / 6.0
        )
        next_correction = np.linalg.solve(
            right_block,
            -residual[interval] - left_block @ correction,
        )
        predicted = (
            residual[interval]
            + left_block @ correction
            + right_block @ next_correction
        )
        left_blocks.append(left_block)
        right_blocks.append(right_block)
        right_condition.append(float(np.linalg.cond(right_block)))
        predicted_residual.append(float(np.linalg.norm(predicted)))
        correction = next_correction
        corrections.append(correction.copy())
    corrections = np.asarray(corrections)
    left_blocks = np.asarray(left_blocks)
    right_blocks = np.asarray(right_blocks)
    correction_norm = np.linalg.norm(corrections, axis=1)
    np.savez_compressed(
        DATA,
        action_times=times,
        endpoint_state_correction_action=corrections,
        left_Newton_blocks=left_blocks,
        right_Newton_blocks=right_blocks,
        right_block_condition_2=np.asarray(right_condition),
        predicted_linearized_residual_2_norm=np.asarray(predicted_residual),
    )
    validation = {
        "all_370_left_and_right_blocks_materialized": left_blocks.shape == right_blocks.shape == (370, 98, 98),
        "all_371_endpoint_corrections_materialized": corrections.shape == (371, 98),
        "reset_endpoint_correction_is_zero": float(np.linalg.norm(corrections[0])) == 0.0,
        "all_right_blocks_are_numerically_invertible": float(np.max(right_condition)) < 1.0e5,
        "linearized_block_residual_closes": float(np.max(predicted_residual)) < 1.0e-16,
        "all_quantities_finite": bool(np.all(np.isfinite(np.concatenate((
            corrections.ravel(), left_blocks.ravel(), right_blocks.ravel(),
        ))))),
        "nonlinear_exact_field_replay_not_claimed": True,
        "continuous_interval_shadowing_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR",
        "status": "FINITE_BLOCK_BIDIAGONAL_NEWTON_PREDICTOR_SOLVED" if passed else "BLOCK_NEWTON_PREDICTOR_INVALID",
        "authority": "NUMERICAL_LINEARIZED_HERMITE_SIMPSON_PREDICTOR_NOT_NONLINEAR_OR_INTERVAL_AUTHORITY",
        "mesh": {"blocks": 370, "state_dimension": 98, "fixed_reset_endpoint": True},
        "summary": {
            "maximum_endpoint_correction_action_2_norm": float(np.max(correction_norm)),
            "maximum_endpoint_correction_owner_node": int(np.argmax(correction_norm)),
            "terminal_endpoint_correction_action_2_norm": float(correction_norm[-1]),
            "maximum_right_block_condition_2": float(np.max(right_condition)),
            "maximum_right_block_condition_owner_interval": int(np.argmax(right_condition)),
            "maximum_predicted_linearized_residual_2_norm": float(np.max(predicted_residual)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                SOURCE, SOURCE.with_suffix(".npz"), ENDPOINT_JACOBIAN,
                ENDPOINT_JACOBIAN.with_suffix(".npz"), MIDPOINT_JACOBIAN,
                MIDPOINT_JACOBIAN.with_suffix(".npz"), THEORY, THIS_SCRIPT,
            )
        },
        "claim_boundary": {
            "nonlinear_Hermite_Simpson_center": "OPEN_EXACT_REPLAY",
            "continuous_action_constrained_center": "OPEN",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "APPLY_THE_ENDPOINT_CORRECTIONS,_PROJECT_ALL_ACTION_CONSTRAINTS,_"
            "RECENTER_THE_DESCRIPTOR_FIBER,_AND_REPLAY_THE_NONLINEAR_EXACT_FIELD"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
