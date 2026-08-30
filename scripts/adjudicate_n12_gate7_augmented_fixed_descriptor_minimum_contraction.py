"""Adjudicate the minimum one-ball contraction after the one-shot replay.

This script does not rebuild a center, derivative, response, or cone.  It
checks whether the already-certified exact-affine nonlinear cone can be
transferred to the accepted augmented fixed-descriptor replay center and
records the smallest contraction data still required there.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
JACOBIAN = BASE / "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.json"
PREDICTOR = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.json"
ENDPOINT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
REPLAY = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.json"
OLD_Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
RESULT = BASE / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_MINIMUM_CONTRACTION_ADJUDICATION.json"
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


def _up(value: float) -> float:
    return math.nextafter(float(value), math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value), -math.inf)


def _augmented_frame(tangent: np.ndarray, descriptor_scale: float) -> np.ndarray:
    frame = np.zeros((99, 74))
    frame[:98, :73] = tangent
    frame[98, 73] = descriptor_scale
    return frame


def _numerical_old_preconditioner_image(
    residual: np.ndarray,
    left_blocks: np.ndarray,
    right_blocks: np.ndarray,
    tangents: np.ndarray,
) -> tuple[np.ndarray, float, float]:
    """Apply the stored causal reduced inverse as a diagnostic only."""

    correction = np.zeros(99)
    corrections = [correction.copy()]
    reduced_residuals: list[float] = []
    for interval in range(370):
        trial = _augmented_frame(tangents[interval + 1], TRIAL_DESCRIPTOR_SCALE)
        test = _augmented_frame(tangents[interval + 1], TEST_DESCRIPTOR_SCALE)
        reduced_right = test.T @ right_blocks[interval] @ trial
        rhs = -test.T @ (
            residual[interval] + left_blocks[interval] @ correction
        )
        coordinates = np.linalg.solve(reduced_right, rhs)
        next_correction = trial @ coordinates
        predicted = (
            residual[interval]
            + left_blocks[interval] @ correction
            + right_blocks[interval] @ next_correction
        )
        reduced = np.concatenate((
            tangents[interval + 1].T @ predicted[:98],
            [predicted[98]],
        ))
        reduced_residuals.append(float(np.linalg.norm(reduced)))
        correction = next_correction
        corrections.append(correction.copy())
    array = np.asarray(corrections)
    return (
        array,
        float(np.max(np.linalg.norm(array, axis=1))),
        float(np.max(reduced_residuals)),
    )


def main() -> None:
    records = {
        path: _load(path)
        for path in (PARENT, JACOBIAN, PREDICTOR, ENDPOINT, REPLAY, OLD_Z2)
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all one-shot replay and retained-Z2 inputs must validate")

    with np.load(PARENT.with_suffix(".npz")) as source:
        parent_endpoints = np.asarray(source["augmented_endpoints"], dtype=float)
    with np.load(ENDPOINT.with_suffix(".npz")) as source:
        replay_states = np.asarray(source["projected_states"], dtype=float)
        replay_descriptors = np.asarray(
            source["independent_signed_descriptors"], dtype=float,
        )
        weights = np.asarray(source["state_weights"], dtype=float)
    replay_endpoints = np.column_stack((
        replay_states * weights[None, :], replay_descriptors,
    ))
    with np.load(REPLAY.with_suffix(".npz")) as source:
        replay_residual = np.asarray(
            source["Hermite_Simpson_shooting_residual"], dtype=float,
        )
    with np.load(PREDICTOR.with_suffix(".npz")) as source:
        left_blocks = np.asarray(source["left_Newton_blocks"], dtype=float)
        right_blocks = np.asarray(source["right_Newton_blocks"], dtype=float)
    with np.load(JACOBIAN.with_suffix(".npz")) as source:
        tangents = np.asarray(source["endpoint_physical_tangent_action"], dtype=float)

    center_shift = np.linalg.norm(replay_endpoints - parent_endpoints, axis=1)
    center_shift_upper = _up(float(np.max(center_shift)))
    old_radius = float(records[OLD_Z2]["domain"]["candidate_nonlinear_action_radius"])
    old_radius_lower = _down(old_radius)
    shift_to_radius_lower = _down(center_shift_upper / old_radius)

    diagnostic_correction, diagnostic_y, diagnostic_linear_residual = (
        _numerical_old_preconditioner_image(
            replay_residual, left_blocks, right_blocks, tangents,
        )
    )
    diagnostic_y_lower = _down(diagnostic_y)
    diagnostic_y_to_radius_lower = _down(diagnostic_y_lower / old_radius)

    # The existing Z2 theorem is explicitly local to its own exact-affine
    # center.  A different center outside that ball cannot inherit it.  This
    # is a domain/provenance adjudication, not a floating-point no-root claim.
    old_z2_contains_replay_center = center_shift_upper <= old_radius_lower
    old_ball_can_contain_diagnostic_newton_image = diagnostic_y <= old_radius_lower
    current_center_outward_y_available = False
    current_center_outward_z1_available = False
    current_center_outward_z2_available = False
    minimum_interval_contraction_available = all((
        old_z2_contains_replay_center,
        current_center_outward_y_available,
        current_center_outward_z1_available,
        current_center_outward_z2_available,
    ))

    validation = {
        "all_one_shot_replay_inputs_validated": True,
        "one_corrected_nonlinear_replay_only": True,
        "no_second_741_node_derivative_rebuild_started": True,
        "no_second_Newton_or_alternative_numerical_campaign_started": True,
        "old_Z2_center_domain_tested_before_transfer": True,
        "old_Z2_does_not_contain_the_replay_center": not old_z2_contains_replay_center,
        "old_cone_cannot_be_promoted_as_current_center_interval_authority": True,
        "diagnostic_old_preconditioner_image_not_promoted_to_outward_Y": True,
        "missing_outward_Y_Z1_Z2_not_relabelled_as_contraction": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values()) and not minimum_interval_contraction_available

    payload = {
        "artifact": "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_MINIMUM_CONTRACTION_ADJUDICATION",
        "status": (
            "MINIMUM_INTERVAL_CONTRACTION_BLOCKED_BY_CURRENT_CENTER_Y_Z1_Z2"
            if passed else "MINIMUM_INTERVAL_CONTRACTION_ADJUDICATION_INVALID"
        ),
        "authority": "CENTER_DOMAIN_AND_PROVENANCE_ADJUDICATION_WITH_NUMERICAL_PRECONDITIONER_DIAGNOSTIC",
        "minimum_required_theorem": {
            "self_map": "Y+Z1*r+Z2*r^2<r",
            "contraction": "Z1+2*Z2*r<1",
            "same_ball_requirement": "Y_Z1_Z2_AND_DOMAIN_MARGINS_MUST_SHARE_THE_ACCEPTED_REPLAY_CENTER_AND_NORM",
        },
        "summary": {
            "maximum_parent_to_replay_center_displacement_action_2_norm_upper": center_shift_upper,
            "old_exact_affine_Z2_candidate_radius_lower": old_radius_lower,
            "center_displacement_to_old_Z2_radius_lower": shift_to_radius_lower,
            "old_Z2_contains_replay_center": old_z2_contains_replay_center,
            "diagnostic_old_preconditioner_Y_2_norm": diagnostic_y,
            "diagnostic_Y_to_old_Z2_radius_lower": diagnostic_y_to_radius_lower,
            "diagnostic_old_preconditioner_linear_residual_2_norm": diagnostic_linear_residual,
            "old_ball_can_contain_diagnostic_newton_image": old_ball_can_contain_diagnostic_newton_image,
            "maximum_diagnostic_correction_owner_node": int(np.argmax(
                np.linalg.norm(diagnostic_correction, axis=1)
            )),
        },
        "adjudication": {
            "existing_exact_affine_Z2_transfer": "REJECTED_BY_CENTER_DOMAIN_MISMATCH",
            "current_replay_center_outward_Y": "MISSING",
            "current_replay_center_outward_Z1": "MISSING",
            "current_replay_center_outward_Z2": "MISSING",
            "minimum_interval_contraction_certificate": "NOT_AVAILABLE",
            "Gate7": "NOT_CLOSED_PRECISE_EQUATION_LEVEL_BLOCKER_LOCALIZED",
            "next_Gate7_numerical_campaign_authorized": False,
            "background_freeze_for_universal_physics_engine": "NOT_YET_AUTHORIZED_BY_GATE7",
        },
        "exact_blocker": (
            "ON_THE_ACCEPTED_ONE_SHOT_REPLAY_CENTER,_PRODUCE_OUTWARD_Y=||A*F||,_"
            "Z1=||I-A*DF||,_AND_A_SAME_CENTER_Z2_LIPSCHITZ_BOUND_IN_ONE_COMMON_"
            "CAUSAL_74D_NORM;_THEN_EXHIBIT_R_WITH_Y+Z1*R+Z2*R^2<R_AND_"
            "Z1+2*Z2*R<1._THE_OLD_EXACT_AFFINE_Z2_CONE_CANNOT_BE_TRANSFERRED."
        ),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                PARENT, PARENT.with_suffix(".npz"), JACOBIAN,
                JACOBIAN.with_suffix(".npz"), PREDICTOR,
                PREDICTOR.with_suffix(".npz"), ENDPOINT,
                ENDPOINT.with_suffix(".npz"), REPLAY,
                REPLAY.with_suffix(".npz"), OLD_Z2, THIS_SCRIPT,
            )
        },
        "claim_boundary": {
            "actual_root_nonexistence": "NOT_CLAIMED",
            "current_center_interval_contraction": "OPEN_PRECISELY_LOCALIZED",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "exact_blocker": payload["exact_blocker"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
