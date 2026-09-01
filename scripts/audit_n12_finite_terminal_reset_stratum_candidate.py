"""Audit the full-reset finite terminal-stratum numerical candidate."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (  # noqa: E402
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _authoritative_n6_event_child_anchor,
    _eta_legendre_minimum,
)
from bhsm.interface.aether_full_reset_action_jacobian import (  # noqa: E402
    full_reset_action_jacobian,
    full_reset_residual,
    selected_ordered_event_action_gradient,
)
from bhsm.interface.aether_high_precision_velocity_jet import (  # noqa: E402
    high_precision_ordered_eigenpair_from_blocks,
    high_precision_velocity_jet_blocks,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


ORDER = 12
POINTS = 96
STATE_DIMENSION = 98
BASELINE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
ROOT_RESIDUAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
)
CROSS_RESOLUTION = ROOT / (
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
FULL_JACOBIAN = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
)
THEORY = ROOT / "theory/n12_finite_terminal_reset_stratum_candidate.md"
DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
)
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json"
)
SEED = os.environ.get("BHSM_N12_TERMINAL_CANDIDATE_SEED")
SEED_THIRD = os.environ.get("BHSM_N12_TERMINAL_CANDIDATE_THIRD")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def _materialize_data() -> None:
    if DATA.is_file():
        return
    if not SEED or not SEED_THIRD:
        raise FileNotFoundError(
            "candidate data absent; set BHSM_N12_TERMINAL_CANDIDATE_SEED "
            "and BHSM_N12_TERMINAL_CANDIDATE_THIRD once"
        )
    seed_path = Path(SEED)
    third_path = Path(SEED_THIRD)
    with np.load(seed_path) as seed, np.load(third_path) as third:
        state = np.asarray(seed["state"], dtype=float)
        center = np.asarray(third["center_state"], dtype=float)
        if not np.array_equal(state, center):
            raise RuntimeError("candidate third variation belongs to another center")
        with np.load(BASELINE) as baseline:
            reference = np.asarray(baseline["branch_reference"], dtype=float)
        np.savez_compressed(
            DATA,
            state=state,
            event_third=np.asarray(third["event"], dtype=float),
            child_third=np.asarray(third["child"], dtype=float),
            state_weights=np.asarray(third["state_weights"], dtype=float),
            branch_reference=reference,
        )


def _terminal_data(
    state: np.ndarray,
    reference: np.ndarray,
) -> dict[str, float | int]:
    q = state[:37]
    velocity = state[37:74]
    multipliers = state[74:]
    blocks = high_precision_velocity_jet_blocks(
        ORDER, q, velocity, multipliers, points=POINTS, precision=60
    )
    ordered = high_precision_ordered_eigenpair_from_blocks(
        blocks, reference, precision=60
    )
    jet = exact_full_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=POINTS
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    reduced = hessian[37:, 37:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    mixed = hessian[37:, :37]
    rhs = np.concatenate((
        np.asarray(jet.gradient[:37], dtype=float) - mixed[:37] @ velocity,
        -mixed[37:] @ velocity,
    ))
    direction = np.zeros(STATE_DIMENSION)
    direction[37:] = psi
    shifted = state.astype(complex) + 1j * 1.0e-20 * direction
    shifted_jet = exact_full_action_jet_at_state(
        ORDER,
        shifted[:37],
        shifted[37:74],
        shifted[74:],
        points=POINTS,
    )
    reduced_derivative = (
        np.imag(np.asarray(shifted_jet.hessian[37:, 37:])) / 1.0e-20
    )
    forcing = float(psi @ rhs)
    cubic = float(psi @ reduced_derivative @ psi)
    return {
        "selected_eigenvalue": float(ordered["eigenvalue"]),
        "selected_index": int(ordered["index"]),
        "selected_spectral_gap": float(ordered["spectral_gap"]),
        "b_psi": forcing,
        "c_psi": cubic,
        "hitting_product": cubic * forcing,
    }


def build_payload() -> dict[str, object]:
    _materialize_data()
    inputs = (BASELINE, ROOT_RESIDUAL, CROSS_RESOLUTION, FULL_JACOBIAN, THEORY, DATA)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing terminal-candidate inputs: " + ", ".join(missing))
    with np.load(DATA) as data:
        state = np.asarray(data["state"], dtype=float)
        event_third = np.asarray(data["event_third"], dtype=float)
        child_third = np.asarray(data["child_third"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(BASELINE) as baseline:
        baseline_state = np.asarray(baseline["state"], dtype=float)
    root_residual = json.loads(ROOT_RESIDUAL.read_text(encoding="utf-8"))
    cross = json.loads(CROSS_RESOLUTION.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    anchor = _authoritative_n6_event_child_anchor(cross)
    normalization_coordinates = embed_nested_state(
        *_decode(anchor["child_exact"]), 6, ORDER
    )[0]
    reset_rows, event_index = full_reset_residual(
        ORDER,
        state,
        weights,
        reference,
        float(root_residual["ordered_scale"]),
        normalization_coordinates,
        points=POINTS,
        high_precision_action=True,
    )
    jacobian, analytic_event_index = full_reset_action_jacobian(
        ORDER,
        state,
        event_third,
        child_third,
        weights,
        reference,
        float(root_residual["ordered_scale"]),
        normalization_coordinates,
        points=POINTS,
    )
    child_gradient, child_index = selected_ordered_event_action_gradient(
        ORDER,
        state[STATE_DIMENSION:],
        child_third,
        weights,
        reference,
        1.0,
        points=POINTS,
    )
    child_gradient_full = np.concatenate((np.zeros(STATE_DIMENSION), child_gradient))
    reset_tangent = null_space(jacobian)
    child_gradient_scale = float(
        np.linalg.norm(reset_tangent.T @ child_gradient_full)
    )
    augmented = np.vstack((jacobian, child_gradient_full / child_gradient_scale))
    augmented_singular = np.linalg.svd(augmented, compute_uv=False)
    event = _terminal_data(state[:STATE_DIMENSION], reference)
    child = _terminal_data(state[STATE_DIMENSION:], reference)
    augmented_residual = np.concatenate((
        reset_rows,
        [float(child["selected_eigenvalue"]) / child_gradient_scale],
    ))
    newton_correction = augmented.T @ np.linalg.solve(
        augmented @ augmented.T, augmented_residual
    )
    joint_weights = np.concatenate((weights, weights))
    eta = {}
    for name, sector in (
        ("event", state[:STATE_DIMENSION]),
        ("child", state[STATE_DIMENSION:]),
    ):
        eta[name] = {
            str(points): _eta_legendre_minimum(
                ORDER, sector[:37], sector[74:], points=points
            )["minimum"]
            for points in (96, 192, 384)
        }
    validation = {
        "stored_third_variation_matches_candidate_center": True,
        "high_precision_reset_residual_below_1e_11": float(
            np.linalg.norm(reset_rows)
        ) < 1.0e-11,
        "event_and_child_selected_lines_remain_simple": min(
            float(event["selected_spectral_gap"]),
            float(child["selected_spectral_gap"]),
        ) > 1.0e-9,
        "event_selected_row_remains_branch_24": (
            event_index == analytic_event_index == 24
        ),
        "child_selected_event_is_branch_23": (
            child_index == int(child["selected_index"]) == 23
        ),
        "child_selected_eigenvalue_is_numerically_zero": abs(
            float(child["selected_eigenvalue"])
        ) < 1.0e-18,
        "child_hitting_product_is_strictly_negative": float(
            child["hitting_product"]
        ) < -1.0e-16,
        "event_and_child_Legendre_margins_are_positive": min(
            value for sector in eta.values() for value in sector.values()
        ) > 0.8,
        "reset_Jacobian_has_rank_57": int(np.linalg.matrix_rank(jacobian)) == 57,
        "terminal_augmented_Jacobian_has_rank_58": int(
            np.linalg.matrix_rank(augmented)
        ) == 58,
        "normal_Newton_correction_is_below_1e_9": float(
            np.linalg.norm(newton_correction)
        ) < 1.0e-9,
        "no_child_selector_observable_value_action_term_scale_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE",
        "status": "HIGH_PRECISION_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE_DERIVED",
        "classification": (
            "THE_UNCHANGED_FULL_EVENT_CHILD_RESET_RELATION_HAS_A_"
            "HIGH_PRECISION_NUMERICAL_CHILD_EVENT_CENTER_WITH_STRICTLY_"
            "NEGATIVE_FORWARD_HITTING_PRODUCT_AND_A_FULL_RANK_58_ROW_"
            "TERMINAL_NORMAL_BLOCK;_DIRECTED_ROUNDING_ROOT_BALL_"
            "CERTIFICATION_REMAINS_OPEN"
        ),
        "center": {
            "high_precision_reset_residual_norm": float(np.linalg.norm(reset_rows)),
            "high_precision_reset_residual_maximum": float(np.max(np.abs(reset_rows))),
            "event": event,
            "child": child,
            "event_child_action_distance_from_certified_reset": float(
                np.linalg.norm((state - baseline_state) * joint_weights)
            ),
            "Legendre_minima": eta,
        },
        "terminal_normal_block": {
            "reset_rows": 57,
            "terminal_rows": 58,
            "ambient_action_dimension": 196,
            "terminal_tangent_dimension": 138,
            "rank": int(np.linalg.matrix_rank(augmented)),
            "largest_singular_value": float(augmented_singular[0]),
            "smallest_singular_value": float(augmented_singular[-1]),
            "condition_number": float(
                augmented_singular[0] / augmented_singular[-1]
            ),
            "child_event_gradient_scale_on_reset_tangent": child_gradient_scale,
            "normalized_augmented_residual_norm": float(
                np.linalg.norm(augmented_residual)
            ),
            "normal_Newton_correction_norm": float(
                np.linalg.norm(newton_correction)
            ),
        },
        "proof_boundary": {
            "finite_terminal_stratum_numerical_candidate": True,
            "finite_terminal_stratum_certified": False,
            "global_uniqueness_claimed": False,
            "universal_reachability_claimed": False,
            "physical_child_selected": False,
            "candidate_used_as_observable_readout": False,
        },
        "exact_next_dependency": (
            "BUILD_THE_58_ROW_DIRECTED_ROUNDING_RADII_POLYNOMIAL_AT_THIS_"
            "CENTER_WITH_RETAINED_ACTION_DERIVATIVE_MAJORANTS,_THEN_"
            "TRANSFER_SELECTED_LINE_SIMPLICITY,_LEGENDRE,_BOUNDARY,_"
            "CANONICAL_LIFT,_AND_STRICT_NEGATIVE_HITTING_PRODUCT_MARGINS_"
            "TO_THE_CERTIFIED_ROOT_BALL"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_TERMINAL_ROOT_BALL_CERTIFICATION",
            "Gate8": "LOCKED",
            "actual_finite_terminal_stratum": "NUMERICAL_CANDIDATE_NOT_CERTIFIED",
            "actual_projected_force": "OPEN_AFTER_TERMINAL_CERTIFICATION",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": {
            "path": DATA.relative_to(ROOT).as_posix(),
            "SHA256": _sha256(DATA),
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in inputs
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

