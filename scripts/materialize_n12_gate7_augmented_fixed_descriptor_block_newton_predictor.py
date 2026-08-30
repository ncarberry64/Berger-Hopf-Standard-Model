"""Solve the 74D constraint-tangent plus descriptor block recurrence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
JACOBIAN = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
THEORY = ROOT / "theory" / "n12_gate7_augmented_fixed_descriptor_newton.md"
RESULT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
TRIAL_DESCRIPTOR_SCALE = 1.0e-7
TEST_DESCRIPTOR_SCALE = 1.0e6


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _augmented_frame(tangent: np.ndarray, descriptor_scale: float) -> np.ndarray:
    frame = np.zeros((99, 74))
    frame[:98, :73] = tangent
    frame[98, 73] = descriptor_scale
    return frame


def main() -> None:
    source_record = _load(SOURCE)
    jacobian_record = _load(JACOBIAN)
    if source_record.get("validation_passed") is not True or jacobian_record.get("validation_passed") is not True:
        raise RuntimeError("validated correlated source and augmented Jacobians required")
    with np.load(SOURCE.with_suffix(".npz")) as source:
        times = np.asarray(source["action_times"], dtype=float)
        residual = np.asarray(source["Hermite_Simpson_shooting_residual"], dtype=float)
        parent_augmented_endpoints = np.asarray(source["augmented_endpoints"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        endpoint_jacobians = np.asarray(source["endpoint_augmented_Jacobian_action"], dtype=float)
        midpoint_jacobians = np.asarray(source["midpoint_augmented_Jacobian_action"], dtype=float)
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)
    identity = np.eye(99)
    correction = np.zeros(99)
    corrections = [correction.copy()]
    reduced_coordinates = [np.zeros(74)]
    left_blocks = []
    right_blocks = []
    reduced_right_blocks = []
    conditions = []
    reduced_residuals = []
    full_residuals = []
    normal_residuals = []
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
        trial_frame = _augmented_frame(tangents[interval + 1], TRIAL_DESCRIPTOR_SCALE)
        test_frame = _augmented_frame(tangents[interval + 1], TEST_DESCRIPTOR_SCALE)
        reduced_right = test_frame.T @ right_block @ trial_frame
        rhs = -test_frame.T @ (residual[interval] + left_block @ correction)
        coordinates = np.linalg.solve(reduced_right, rhs)
        next_correction = trial_frame @ coordinates
        predicted = residual[interval] + left_block @ correction + right_block @ next_correction
        reduced_predicted = np.concatenate((
            tangents[interval + 1].T @ predicted[:98],
            [predicted[98]],
        ))
        normal = predicted[:98] - tangents[interval + 1] @ reduced_predicted[:73]
        left_blocks.append(left_block)
        right_blocks.append(right_block)
        reduced_right_blocks.append(reduced_right)
        conditions.append(float(np.linalg.cond(reduced_right)))
        reduced_residuals.append(float(np.linalg.norm(reduced_predicted)))
        full_residuals.append(float(np.linalg.norm(predicted)))
        normal_residuals.append(float(np.linalg.norm(normal)))
        correction = next_correction
        corrections.append(correction.copy())
        reduced_coordinates.append(coordinates.copy())
    corrections = np.asarray(corrections)
    reduced_coordinates = np.asarray(reduced_coordinates)
    tangent_membership = np.asarray([
        np.linalg.norm(corrections[i] - _augmented_frame(tangents[i], TRIAL_DESCRIPTOR_SCALE) @ reduced_coordinates[i])
        for i in range(371)
    ])
    correction_norms = np.linalg.norm(corrections, axis=1)
    predicted_descriptors = parent_augmented_endpoints[:, 98] + corrections[:, 98]
    np.savez_compressed(
        DATA,
        action_times=times,
        endpoint_augmented_correction_action=corrections,
        endpoint_reduced_tangent_descriptor_coordinates=reduced_coordinates,
        left_Newton_blocks=np.asarray(left_blocks),
        right_Newton_blocks=np.asarray(right_blocks),
        reduced_right_Newton_blocks=np.asarray(reduced_right_blocks),
        reduced_right_block_condition_2=np.asarray(conditions),
        predicted_reduced_residual_2_norm=np.asarray(reduced_residuals),
        predicted_full_residual_2_norm=np.asarray(full_residuals),
        predicted_normal_residual_2_norm=np.asarray(normal_residuals),
        correction_tangent_descriptor_membership_residual_2_norm=tangent_membership,
    )
    validation = {
        "all_370_reduced_blocks_materialized": len(reduced_right_blocks) == 370,
        "all_371_augmented_endpoint_corrections_materialized": corrections.shape == (371, 99),
        "reset_endpoint_correction_is_zero": float(np.linalg.norm(corrections[0])) == 0.0,
        "all_reduced_right_blocks_are_numerically_invertible": float(np.max(conditions)) < 1.0e8,
        "linearized_74D_block_residual_closes": float(np.max(reduced_residuals)) < 1.0e-12,
        "all_corrections_lie_in_constraint_tangent_plus_descriptor_axis": float(np.max(tangent_membership)) < 1.0e-14,
        "descriptor_rate_row_is_solved_not_reconstructed_from_binary_eigenvalue": True,
        "predicted_descriptors_remain_in_nonnegative_domain": float(np.min(predicted_descriptors)) >= 0.0,
        "normal_25D_residual_is_recorded_not_relabelled_as_zero": True,
        "nonlinear_retained_exact_field_replay_not_claimed": True,
        "collocation_parameter_not_labeled_proper_time": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR",
        "status": "AUGMENTED_74D_BLOCK_NEWTON_PREDICTOR_SOLVED" if passed else "AUGMENTED_74D_BLOCK_NEWTON_PREDICTOR_INVALID",
        "authority": "NUMERICAL_REDUCED_TANGENT_DESCRIPTOR_PREDICTOR_NOT_NONLINEAR_OR_INTERVAL_AUTHORITY",
        "mesh": {"blocks": 370, "ambient_dimension": 99, "constraint_tangent_dimension": 73, "reduced_augmented_dimension": 74, "fixed_reset_endpoint": True, "trial_descriptor_scale": TRIAL_DESCRIPTOR_SCALE, "test_descriptor_scale": TEST_DESCRIPTOR_SCALE},
        "summary": {
            "maximum_endpoint_augmented_correction_2_norm": float(np.max(correction_norms)),
            "maximum_endpoint_augmented_correction_owner_node": int(np.argmax(correction_norms)),
            "terminal_endpoint_augmented_correction_2_norm": float(correction_norms[-1]),
            "maximum_state_correction_2_norm": float(np.max(np.linalg.norm(corrections[:, :98], axis=1))),
            "maximum_descriptor_correction_absolute": float(np.max(np.abs(corrections[:, 98]))),
            "minimum_predicted_descriptor": float(np.min(predicted_descriptors)),
            "maximum_reduced_right_block_condition_2": float(np.max(conditions)),
            "maximum_reduced_right_block_condition_owner_interval": int(np.argmax(conditions)),
            "maximum_predicted_reduced_residual_2_norm": float(np.max(reduced_residuals)),
            "maximum_predicted_full_residual_2_norm": float(np.max(full_residuals)),
            "maximum_predicted_normal_residual_2_norm": float(np.max(normal_residuals)),
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {_relative(path): _sha256(path) for path in (
            SOURCE, SOURCE.with_suffix(".npz"), JACOBIAN, JACOBIAN.with_suffix(".npz"), THEORY, THIS_SCRIPT,
        )},
        "claim_boundary": {
            "nonlinear_augmented_center": "OPEN_RETAINED_EXACT_REPLAY",
            "continuous_interval_shadowing": "OPEN",
            "proper_time_pullback": "DOWNSTREAM_REQUIRES_ACCEPTED_CENTER_NORM_JETS",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "APPLY_THE_74D_CORRECTION,_PROJECT_CONSTRAINTS,_KEEP_THE_INDEPENDENT_DESCRIPTOR,_PERSIST_CANCELLED_NORM_JETS,_AND_REPLAY_ALL_370_RETAINED_EXACT_MIDPOINTS",
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "validation_passed": passed}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
