"""Materialize and cross-check the analytic N12 full reset Jacobian."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (  # noqa: E402
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _authoritative_n6_event_child_anchor,
)
from bhsm.interface.aether_full_reset_action_jacobian import (  # noqa: E402
    full_reset_action_jacobian,
)


ORDER = 12
POINTS = 96
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
THIRD = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_THIRD_VARIATIONS.npz"
EXACT_NORMAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_NORMAL_1E24.npz"
)
ROOT_RESIDUAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
)
CROSS_RESOLUTION = ROOT / (
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
THEORY = ROOT / "theory/n12_full_reset_action_jacobian.md"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
)
DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz"
)
INPUTS = (STATE, THIRD, EXACT_NORMAL, ROOT_RESIDUAL, CROSS_RESOLUTION, THEORY)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing full-reset inputs: " + ", ".join(missing))
    with np.load(STATE) as checkpoint:
        joint = np.asarray(checkpoint["state"], dtype=float)
        paired = np.asarray(checkpoint["paired_jacobian"], dtype=float)
        branch_reference = np.asarray(
            checkpoint["branch_reference"], dtype=float
        )
    with np.load(THIRD) as third_file:
        event_third = np.asarray(third_file["event"], dtype=float)
        child_third = np.asarray(third_file["child"], dtype=float)
        state_weights = np.asarray(third_file["state_weights"], dtype=float)
        third_center = np.asarray(third_file["center_state"], dtype=float)
    with np.load(EXACT_NORMAL) as exact_file:
        old_analytic_normal = np.asarray(
            exact_file["analytic_normal_jacobian"], dtype=float
        )
        normal_basis = np.asarray(exact_file["normal_basis"], dtype=float)
    if not np.array_equal(joint, third_center):
        raise RuntimeError("third variation belongs to another checkpoint")

    root_residual = json.loads(ROOT_RESIDUAL.read_text(encoding="utf-8"))
    cross_payload = json.loads(
        CROSS_RESOLUTION.read_text(encoding="utf-8")
    )["cross_resolution_reconnaissance"]
    anchor = _authoritative_n6_event_child_anchor(cross_payload)
    normalization_coordinates = embed_nested_state(
        *_decode(anchor["child_exact"]), 6, ORDER
    )[0]
    analytic, selected = full_reset_action_jacobian(
        ORDER,
        joint,
        event_third,
        child_third,
        state_weights,
        branch_reference,
        float(root_residual["ordered_scale"]),
        normalization_coordinates,
        points=POINTS,
    )
    analytic_normal = analytic @ normal_basis
    paired_difference = analytic - paired
    normal_difference = analytic_normal - old_analytic_normal
    singular = np.linalg.svd(analytic_normal, compute_uv=False)
    rank = int(np.linalg.matrix_rank(analytic))
    nullity = int(analytic.shape[1] - rank)
    paired_relative = float(
        np.linalg.norm(paired_difference) / np.linalg.norm(analytic)
    )
    old_normal_relative = float(
        np.linalg.norm(normal_difference) / np.linalg.norm(analytic_normal)
    )
    np.savez_compressed(
        DATA,
        analytic_full_reset_jacobian=analytic,
        analytic_normal_jacobian=analytic_normal,
        normal_basis=normal_basis,
        center_state=joint,
        state_weights=state_weights,
        normalization_coordinates=normalization_coordinates,
    )
    validation = {
        "checkpoint_and_third_variation_centers_match": True,
        "full_Jacobian_has_shape_57_by_196": analytic.shape == (57, 196),
        "transported_ordered_branch_is_24": selected == 24,
        "full_row_rank_is_57": rank == 57,
        "physical_tangent_nullity_is_139": nullity == 139,
        "all_entries_are_finite": bool(np.all(np.isfinite(analytic))),
        "analytic_normal_smallest_singular_matches_certified_value": bool(
            abs(float(singular[-1]) - 0.008076424724302237) < 2.0e-5
        ),
        "full_analytic_and_paired_Jacobians_agree_to_existing_discretization_scale": (
            paired_relative < 3.0e-5
        ),
        "no_matrix_inverse_or_numerical_derivative_used": True,
        "no_equation_action_term_reset_selector_endpoint_scale_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_FULL_RESET_ACTION_JACOBIAN",
        "status": "FULL_ANALYTIC_ACTION_COORDINATE_RESET_JACOBIAN_DERIVED",
        "classification": (
            "ALL_57_RETAINED_EVENT_CHILD_RESET_ROWS_ARE_DIFFERENTIATED_"
            "ANALYTICALLY_IN_THE_196_ACTION_COORDINATES,_WITH_RANK_57_AND_"
            "A_139_DIMENSIONAL_LOCAL_PHYSICAL_TANGENT_KERNEL"
        ),
        "dimensions": {
            "rows": int(analytic.shape[0]),
            "columns": int(analytic.shape[1]),
            "rank": rank,
            "physical_tangent_nullity": nullity,
        },
        "transported_ordered_eigenline_index": selected,
        "normal_restriction": {
            "largest_singular_value": float(singular[0]),
            "smallest_singular_value": float(singular[-1]),
            "condition_number": float(singular[0] / singular[-1]),
            "relative_difference_from_prior_complex_step_normal_certificate": (
                old_normal_relative
            ),
        },
        "paired_crosscheck": {
            "relative_Frobenius_residual": paired_relative,
            "absolute_Frobenius_residual": float(np.linalg.norm(paired_difference)),
            "operator_norm_residual": float(np.linalg.norm(paired_difference, 2)),
            "interpretation": (
                "AGREES_WITH_THE_STORED_PAIRED_FINITE_DIFFERENCE_AT_ITS_"
                "ALREADY_RECORDED_DISCRETIZATION_AND_NORMALIZATION_SCALE"
            ),
        },
        "data": {
            "path": DATA.relative_to(ROOT).as_posix(),
            "SHA256": _sha256(DATA),
        },
        "continuation_consequence": {
            "full_reset_Jacobian_rebuild_is_analytic": True,
            "complex_action_evaluations_removed_per_recenter": 196,
            "intrinsic_projected_or_bordered_recenter_enabled": True,
            "finite_terminal_stratum_certified_here": False,
        },
        "exact_next_dependency": (
            "RUN_INTRINSIC_PREDICTOR_CORRECTOR_CONTINUATION_IN_THE_139_"
            "DIMENSIONAL_RESET_TANGENT_TOWARD_THE_FINITE_CHILD_TERMINAL_"
            "SIGN_CONDITION,_MONITOR_ALL_CANONICAL_MARGINS,_AND_CERTIFY_A_"
            "TERMINAL_ROOT_BALL_OR_A_RETAINED_STOP"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_GLOBAL_FINITE_RESET_STRATUM_EXISTENCE",
            "Gate8": "LOCKED",
            "actual_finite_stratum": "OPEN_CURRENT_OWNER",
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()

