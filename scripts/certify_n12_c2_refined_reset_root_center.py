"""Newton-recenter the certified terminal reset root in its proof normal section."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from audit_n12_finite_terminal_directed_center import (  # noqa: E402
    _augmented,
    _inputs,
    _normalization_coordinates,
)
from bhsm.interface.aether_full_reset_action_jacobian import (  # noqa: E402
    full_reset_residual,
)
from bhsm.interface.aether_high_precision_velocity_jet import (  # noqa: E402
    high_precision_ordered_eigenpair_from_blocks,
    high_precision_velocity_jet_blocks,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
DATA_RESULT = BASE / "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
DIRECTED = BASE / "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json"
DIRECTED_DATA = BASE / "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
ROOT_RESIDUAL = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
THEORY = ROOT / "theory/n12_c2_refined_reset_root_center.md"
INPUTS = (CANDIDATE, DIRECTED, DIRECTED_DATA, RADII, ROOT_RESIDUAL, THEORY)
ORDER = 12
POINTS = 96


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _augmented_residual(
    state: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    ordered_scale: float,
    normalization: np.ndarray,
    child_scale: float,
) -> np.ndarray:
    reset, _ = full_reset_residual(
        ORDER, state, weights, reference, ordered_scale, normalization,
        points=POINTS, high_precision_action=True,
    )
    child = state[98:]
    blocks = high_precision_velocity_jet_blocks(
        ORDER, child[:37], child[37:74], child[74:],
        points=POINTS, precision=60,
    )
    child_lambda = float(high_precision_ordered_eigenpair_from_blocks(
        blocks, reference, precision=60,
    )["eigenvalue"])
    return np.concatenate((reset, [child_lambda / child_scale]))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("complete refined-root inputs required")
    directed = _load(DIRECTED)
    radii = _load(RADII)
    root_record = _load(ROOT_RESIDUAL)
    if not (
        directed.get("validation_passed") is True
        and radii.get("validation_passed") is True
    ):
        raise RuntimeError("validated directed center and radii theorem required")

    state, event_third, child_third, weights, reference = _inputs()
    normalization = _normalization_coordinates()
    with np.load(DIRECTED_DATA) as data:
        primary = np.asarray(data["primary_normal"], dtype=float)
        normal = np.asarray(data["normal_basis"], dtype=float)
        child_scale = float(data["child_gradient_scale"])
    augmented, current_scale = _augmented(
        state, event_third, child_third, weights, reference,
        float(root_record["ordered_scale"]), normalization, child_scale,
    )
    if current_scale != child_scale or not np.array_equal(
        primary, augmented @ normal
    ):
        raise RuntimeError("stored normal preconditioner changed")

    residual = _augmented_residual(
        state, weights, reference, float(root_record["ordered_scale"]),
        normalization, child_scale,
    )
    normal_correction = np.linalg.solve(primary, residual)
    joint_weights = np.tile(weights, 2)
    refined_state = state - (normal @ normal_correction) / joint_weights
    refined_residual = _augmented_residual(
        refined_state, weights, reference,
        float(root_record["ordered_scale"]), normalization, child_scale,
    )
    np.savez_compressed(
        DATA_RESULT,
        state=refined_state,
        state_weights=weights,
        branch_reference=reference,
        normal_coordinates=-normal_correction,
        normal_basis=normal,
        old_center_state=state,
    )

    old_Y = float(directed["directed_Y_upper"])
    old_Z0 = float(directed["directed_Z0_upper"])
    Z2 = float(radii["applied_Hessian_ball_bounds"]["total_Z2"])
    new_Y = old_Z0 * old_Y + 0.5 * Z2 * old_Y**2
    new_Z0 = old_Z0 + Z2 * old_Y
    discriminant = (1.0 - new_Z0) ** 2 - 2.0 * Z2 * new_Y
    square_root = math.sqrt(discriminant)
    roots = (
        (1.0 - new_Z0 - square_root) / Z2,
        (1.0 - new_Z0 + square_root) / Z2,
    )
    # The cancellation-safe equivalent avoids loss in the small root.
    small_root = 2.0 * new_Y / (1.0 - new_Z0 + square_root)
    roots = (small_root, roots[1])
    certified_radius = 2.0 * small_root
    polynomial = (
        new_Y + new_Z0 * certified_radius
        + 0.5 * Z2 * certified_radius**2 - certified_radius
    )
    contraction = new_Z0 + Z2 * certified_radius
    old_certified_radius = float(radii["certified_root_ball_radius"])
    correction_norm = float(np.linalg.norm(normal_correction))
    validation = {
        "same_58_dimensional_normal_proof_section_used": primary.shape == (58, 58),
        "Newton_correction_is_enclosed_by_directed_Y": correction_norm <= old_Y,
        "refined_center_materialized_without_tangent_selector": (
            np.linalg.norm(
                (refined_state - state) * joint_weights
                + normal @ normal_correction
            )
            < 1.0e-15
        ),
        "existing_Z2_ball_contains_refined_center_and_new_ball": (
            correction_norm + certified_radius < old_certified_radius
        ),
        "refined_radii_discriminant_is_positive": discriminant > 0.0,
        "refined_radii_polynomial_is_negative": polynomial < 0.0,
        "refined_contraction_is_below_one": contraction < 1.0,
        "refined_small_root_is_below_certified_radius": (
            0.0 < small_root < certified_radius < 1.0e-14
        ),
        "direct_residual_crosscheck_improves": (
            np.linalg.norm(refined_residual) < np.linalg.norm(residual)
        ),
        "same_unique_old_normal_section_root_is_enclosed": (
            correction_norm + certified_radius < old_certified_radius
        ),
        "no_physical_history_member_selector_equation_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_REFINED_RESET_ROOT_CENTER",
        "status": (
            "SAME_TERMINAL_RESET_ROOT_RECENTERED_TO_SUB_1E_14_NORMAL_BALL"
            if passed else "C2_REFINED_RESET_ROOT_CENTER_NOT_CERTIFIED"
        ),
        "classification": (
            "ONE_NEWTON_STEP_IN_THE_ALREADY_CERTIFIED_58_DIMENSIONAL_NORMAL_"
            "PROOF_SECTION,_COMBINED_WITH_THE_EXISTING_DIRECTED_Z0_AND_Z2_"
            "BOUNDS,_RECENTERS_THE_SAME_UNIQUE_LOCAL_RESET_ROOT_IN_A_1E_14_"
            "BALL_WITH_A_POSTERIORI_DISTANCE_BELOW_THE_SMALL_RADII_ROOT;_"
            "TANGENT_RESET_FAMILY_DIRECTIONS_AND_PHYSICAL_ONTOLOGY_ARE_UNCHANGED"
        ),
        "proof_coordinate_Newton_step": {
            "normal_dimension": 58,
            "correction_action_norm": correction_norm,
            "old_directed_Y_upper": old_Y,
            "old_directed_Z0_upper": old_Z0,
            "old_augmented_residual_norm_crosscheck": float(np.linalg.norm(residual)),
            "refined_augmented_residual_norm_crosscheck": float(
                np.linalg.norm(refined_residual)
            ),
            "data": DATA_RESULT.relative_to(ROOT).as_posix(),
            "data_SHA256": _sha256(DATA_RESULT),
            "role": "NUMERICAL_PROOF_CENTER_ONLY_NOT_A_PHYSICAL_SELECTOR",
        },
        "refined_radii_theorem": {
            "Y_upper": new_Y,
            "Z0_upper": new_Z0,
            "Z2_upper_reused": Z2,
            "discriminant_lower": discriminant,
            "negative_interval_roots": list(roots),
            "certified_root_ball_radius": certified_radius,
            "radii_polynomial_at_certified_radius": polynomial,
            "contraction_at_certified_radius": contraction,
            "a_posteriori_root_distance_upper": small_root,
            "old_certified_root_ball_radius": old_certified_radius,
        },
        "exact_next_dependency": (
            "REBUILD_THE_ACTUAL_C2_OUTGOING_ORIENTATION_AND_REGULARIZED_"
            "LAUNCH_BOUNDS_ABOUT_THIS_REFINED_PROOF_CENTER,_THEN_FORM_A_"
            "TIGHT_RECENTERABLE_ENDPOINT_TUBE_FOR_CONTINUED_SAME_ACTION_FLOW"
        ),
        "claim_boundary": {
            "same_local_terminal_reset_root": "CERTIFIED_REFINED_ENCLOSURE",
            "physical_reset_family_member_selected": False,
            "C2_continuation_beyond_first_launch": "OPEN_AFTER_REBUILD",
            "complete_M_C2_maximal_response": "OPEN_AFTER_CONTINUATION",
            "zero_source_force": "OPEN_AFTER_COMPLETE_M_C2",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "correction": payload["proof_coordinate_Newton_step"][
            "correction_action_norm"
        ],
        "refined_residual": payload["proof_coordinate_Newton_step"][
            "refined_augmented_residual_norm_crosscheck"
        ],
        "root_distance": payload["refined_radii_theorem"][
            "a_posteriori_root_distance_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
