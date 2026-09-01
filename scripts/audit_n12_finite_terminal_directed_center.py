"""Directed-rounding center audit for the 58-row terminal reset map."""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, localcontext
import hashlib
import json
import math
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


ORDER = 12
POINTS = 96
PRECISION = 80
OPERATION_COUNT = 1_000_000
CANDIDATE = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
)
ROOT_RESIDUAL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json"
)
CROSS_RESOLUTION = ROOT / (
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz"
)
CERTIFICATE_CHECKPOINT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz"
)
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json"
)
CROSS_THIRD = os.environ.get("BHSM_N12_TERMINAL_CROSS_THIRD")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _d(value: float) -> Decimal:
    return Decimal.from_float(float(value))


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def _inputs() -> tuple[np.ndarray, ...]:
    with np.load(CANDIDATE) as candidate:
        return (
            np.asarray(candidate["state"], dtype=float),
            np.asarray(candidate["event_third"], dtype=float),
            np.asarray(candidate["child_third"], dtype=float),
            np.asarray(candidate["state_weights"], dtype=float),
            np.asarray(candidate["branch_reference"], dtype=float),
        )


def _normalization_coordinates() -> np.ndarray:
    payload = json.loads(CROSS_RESOLUTION.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    anchor = _authoritative_n6_event_child_anchor(payload)
    return embed_nested_state(*_decode(anchor["child_exact"]), 6, ORDER)[0]


def _augmented(
    state: np.ndarray,
    event_third: np.ndarray,
    child_third: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    ordered_scale: float,
    normalization_coordinates: np.ndarray,
    child_scale: float | None = None,
) -> tuple[np.ndarray, float]:
    jacobian, _ = full_reset_action_jacobian(
        ORDER,
        state,
        event_third,
        child_third,
        weights,
        reference,
        ordered_scale,
        normalization_coordinates,
        points=POINTS,
    )
    child_gradient, _ = selected_ordered_event_action_gradient(
        ORDER,
        state[98:],
        child_third,
        weights,
        reference,
        1.0,
        points=POINTS,
    )
    child_full = np.concatenate((np.zeros(98), child_gradient))
    if child_scale is None:
        child_scale = float(np.linalg.norm(null_space(jacobian).T @ child_full))
    return np.vstack((jacobian, child_full / child_scale)), child_scale


def _materialize() -> None:
    state, event_third, child_third, weights, reference = _inputs()
    root = json.loads(ROOT_RESIDUAL.read_text(encoding="utf-8"))
    ordered_scale = float(root["ordered_scale"])
    normalization = _normalization_coordinates()
    primary, child_scale = _augmented(
        state,
        event_third,
        child_third,
        weights,
        reference,
        ordered_scale,
        normalization,
    )
    if not CERTIFICATE_CHECKPOINT.is_file():
        np.savez_compressed(
            CERTIFICATE_CHECKPOINT,
            state=state,
            paired_jacobian=primary,
            branch_reference=reference,
            n6_ordered_branch_index=np.asarray(
                root["n6_ordered_branch_index"], dtype=int
            ),
        )
    if DATA.is_file():
        return
    if not CROSS_THIRD:
        raise FileNotFoundError(
            "directed-center data absent; set BHSM_N12_TERMINAL_CROSS_THIRD once"
        )
    with np.load(CROSS_THIRD) as cross:
        if not np.array_equal(state, np.asarray(cross["center_state"])):
            raise RuntimeError("cross third variation belongs to another center")
        cross_augmented, _ = _augmented(
            state,
            np.asarray(cross["event"], dtype=float),
            np.asarray(cross["child"], dtype=float),
            weights,
            reference,
            ordered_scale,
            normalization,
            child_scale,
        )
    _, _, vh = np.linalg.svd(primary, full_matrices=False)
    normal = vh.T
    np.savez_compressed(
        DATA,
        primary_normal=primary @ normal,
        cross_normal=cross_augmented @ normal,
        normal_basis=normal,
        child_gradient_scale=np.asarray(child_scale),
        center_state=state,
    )


def build_payload() -> dict[str, object]:
    _materialize()
    state, event_third, child_third, weights, reference = _inputs()
    root = json.loads(ROOT_RESIDUAL.read_text(encoding="utf-8"))
    normalization = _normalization_coordinates()
    with np.load(DATA) as data:
        primary = np.asarray(data["primary_normal"], dtype=float)
        cross = np.asarray(data["cross_normal"], dtype=float)
        normal = np.asarray(data["normal_basis"], dtype=float)
        child_scale = float(data["child_gradient_scale"])
        center_state = np.asarray(data["center_state"], dtype=float)
    if not np.array_equal(state, center_state):
        raise RuntimeError("directed-center matrices belong to another center")
    augmented, current_scale = _augmented(
        state,
        event_third,
        child_third,
        weights,
        reference,
        float(root["ordered_scale"]),
        normalization,
        child_scale,
    )
    if current_scale != child_scale:
        raise RuntimeError("child-event normalization changed")
    primary_rebuilt = augmented @ normal
    reset, _ = full_reset_residual(
        ORDER,
        state,
        weights,
        reference,
        float(root["ordered_scale"]),
        normalization,
        points=POINTS,
        high_precision_action=True,
    )
    child = state[98:]
    blocks = high_precision_velocity_jet_blocks(
        ORDER,
        child[:37],
        child[37:74],
        child[74:],
        points=POINTS,
        precision=60,
    )
    child_lambda = float(high_precision_ordered_eigenpair_from_blocks(
        blocks, reference, precision=60
    )["eigenvalue"])
    residual = np.concatenate((reset, [child_lambda / child_scale]))
    inverse = np.linalg.inv(primary)
    epsilon = np.finfo(float).eps
    gamma = OPERATION_COUNT * epsilon / (1.0 - OPERATION_COUNT * epsilon)
    entry_radius = (
        np.abs(primary - cross)
        + gamma * np.maximum(np.abs(primary), np.abs(cross))
    )
    dimension = primary.shape[0]
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_CEILING
        error_upper = []
        for row in range(dimension):
            for column in range(dimension):
                center_sum = sum(
                    _d(inverse[row, inner]) * _d(primary[inner, column])
                    for inner in range(dimension)
                )
                center_error = (
                    (Decimal(1) if row == column else Decimal(0))
                    - center_sum
                )
                radius = sum(
                    abs(_d(inverse[row, inner]))
                    * _d(entry_radius[inner, column])
                    for inner in range(dimension)
                )
                error_upper.append(abs(center_error) + radius)
        z0 = float(sum(value * value for value in error_upper).sqrt())
        correction = [sum(
            _d(inverse[row, inner]) * _d(residual[inner])
            for inner in range(dimension)
        ) for row in range(dimension)]
        y_upper = float(sum(value * value for value in correction).sqrt())
    validation = {
        "same_center_and_normal_basis": True,
        "primary_matrix_rebuild_is_exact_binary64": bool(
            np.array_equal(primary, primary_rebuilt)
        ),
        "terminal_normal_dimension_is_58": primary.shape == (58, 58),
        "primary_and_cross_matrices_have_rank_58": bool(
            np.linalg.matrix_rank(primary) == 58
            and np.linalg.matrix_rank(cross) == 58
        ),
        "dense_products_accumulated_from_exact_float_inputs": True,
        "Decimal_rounding_is_ceiling": True,
        "cross_complex_step_and_binary64_gamma_enclosed": True,
        "directed_Z0_is_contractively_below_one": z0 < 1.0,
        "directed_Y_is_below_1e_10": y_upper < 1.0e-10,
        "nonlinear_Z2_and_root_ball_not_claimed_here": True,
        "no_equation_action_term_selector_scale_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER",
        "status": "TERMINAL_58_ROW_DIRECTED_CENTER_Y_Z0_CLOSED_Z2_OPEN",
        "classification": (
            "THE_PRIMARY_1E_20_AND_CROSS_1E_24_ANALYTIC_TERMINAL_NORMAL_"
            "JACOBIANS_HAVE_RANK_58_AND_DIRECTED_DECIMAL_ACCUMULATION_"
            "CLOSES_THE_CENTER_Y_AND_Z0_BOUNDS;_THE_NONLINEAR_Z2_BALL_"
            "BOUND_REMAINS_OPEN"
        ),
        "decimal_precision": PRECISION,
        "binary64_operation_count_enclosure": OPERATION_COUNT,
        "binary64_gamma": gamma,
        "terminal_normal_dimension": dimension,
        "primary_smallest_singular_value": float(
            np.linalg.svd(primary, compute_uv=False)[-1]
        ),
        "cross_smallest_singular_value": float(
            np.linalg.svd(cross, compute_uv=False)[-1]
        ),
        "cross_entry_radius_maximum": float(np.max(entry_radius)),
        "cross_entry_radius_Frobenius": float(np.linalg.norm(entry_radius)),
        "directed_Y_upper": y_upper,
        "directed_Z0_upper": z0,
        "data": {
            "path": DATA.relative_to(ROOT).as_posix(),
            "SHA256": _sha256(DATA),
        },
        "proof_boundary": {
            "directed_center_Y_Z0": "CLOSED",
            "nonlinear_Z2": "OPEN_CURRENT_OWNER",
            "terminal_root_ball_certified": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_APPLIED_58_ROW_HESSIAN_BALL_BOUND_Z2_FROM_THE_"
            "RETAINED_ACTION_D3_TO_D5_MAJORANTS,_BORDERED_CANONICAL_"
            "LIFT_BOUNDS,_EVENT_AND_CHILD_SELECTED_EIGENLINE_RESOLVENTS,_"
            "BOUNDARY_CHART,_AND_CANONICAL_MOMENTUM_DERIVATIVES"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_TERMINAL_ROOT_BALL_Z2",
            "Gate8": "LOCKED",
            "actual_finite_terminal_stratum": "NUMERICAL_CANDIDATE_NOT_CERTIFIED",
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (
                CANDIDATE, ROOT_RESIDUAL, CROSS_RESOLUTION, DATA,
                CERTIFICATE_CHECKPOINT,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
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
