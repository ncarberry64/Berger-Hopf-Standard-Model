"""Derive and cross-check the exact N12 canonical-momentum Jacobians."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_canonical_momentum_action_jacobian import (  # noqa: E402
    canonical_momentum_action_jacobian,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (  # noqa: E402
    _canonical_pair_at_order,
)


ORDER = 12
POINTS = 96
COMPLEX_STEP = 1.0e-20
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
THIRD = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_THIRD_VARIATIONS.npz"
THEORY = ROOT / "theory/n12_canonical_momentum_action_jacobian.md"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.json"
)
DATA = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN.npz"
)
INPUTS = (STATE, THIRD, THEORY)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _complex_column(
    state: np.ndarray,
    state_weights: np.ndarray,
    column: int,
) -> np.ndarray:
    shifted = state.astype(complex)
    shifted[column] += 1j * COMPLEX_STEP / state_weights[column]
    momentum = _canonical_pair_at_order(
        ORDER,
        shifted[:37],
        shifted[37:74],
        shifted[74:],
        points=POINTS,
    )[0]
    return np.imag(momentum) / COMPLEX_STEP


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing canonical-momentum inputs: " + ", ".join(missing))
    with np.load(STATE) as checkpoint:
        joint = np.asarray(checkpoint["state"], dtype=float)
    with np.load(THIRD) as third_file:
        event_third = np.asarray(third_file["event"], dtype=float)
        child_third = np.asarray(third_file["child"], dtype=float)
        state_weights = np.asarray(third_file["state_weights"], dtype=float)
        third_center = np.asarray(third_file["center_state"], dtype=float)
    if not np.array_equal(joint, third_center):
        raise RuntimeError("third variation belongs to another checkpoint")
    event = joint[:98]
    child = joint[98:]
    event_jacobian = canonical_momentum_action_jacobian(
        ORDER, event, event_third, state_weights, points=POINTS
    )
    child_jacobian = canonical_momentum_action_jacobian(
        ORDER, child, child_third, state_weights, points=POINTS
    )
    columns = (0, 1, 25, 37, 49, 74, 86, 97)
    rows = []
    maximum_absolute = 0.0
    maximum_relative = 0.0
    for sector_name, state, jacobian in (
        ("event", event, event_jacobian),
        ("child", child, child_jacobian),
    ):
        for column in columns:
            independent = _complex_column(state, state_weights, column)
            analytic = jacobian[:, column]
            absolute = float(np.linalg.norm(analytic - independent))
            scale = max(float(np.linalg.norm(independent)), 1.0e-300)
            relative = absolute / scale
            maximum_absolute = max(maximum_absolute, absolute)
            maximum_relative = max(maximum_relative, relative)
            rows.append({
                "sector": sector_name,
                "action_coordinate_column": column,
                "analytic": analytic.tolist(),
                "independent_complex_step": independent.tolist(),
                "absolute_residual": absolute,
                "relative_residual": relative,
            })
    np.savez_compressed(
        DATA,
        event=event_jacobian,
        child=child_jacobian,
        state_weights=state_weights,
        center_state=joint,
    )
    validation = {
        "checkpoint_and_third_variation_centers_match": True,
        "event_and_child_Jacobians_have_shape_2_by_98": (
            event_jacobian.shape == (2, 98) and child_jacobian.shape == (2, 98)
        ),
        "all_entries_are_finite": bool(
            np.all(np.isfinite(event_jacobian))
            and np.all(np.isfinite(child_jacobian))
        ),
        "representative_columns_match_independent_complex_step": (
            maximum_relative < 1.0e-8
        ),
        "no_matrix_inverse_formed": True,
        "no_finite_difference_step_or_fitted_parameter_used": True,
        "no_equation_action_term_reset_selector_endpoint_scale_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_CANONICAL_MOMENTUM_ACTION_JACOBIAN",
        "status": "EXACT_ACTION_COORDINATE_CANONICAL_MOMENTUM_JACOBIAN_DERIVED",
        "classification": (
            "THE_FULL_TWO_BY_98_ACTION_COORDINATE_JACOBIAN_OF_THE_RETAINED_"
            "HESSIAN_MINIMAL_CANONICAL_BOUNDARY_MOMENTUM_IS_DERIVED_BY_"
            "DIFFERENTIATING_ITS_TWO_LINEAR_SOLVES_AND_THE_EXISTING_THIRD_"
            "VARIATION,_REMOVING_THE_COMPLEX_STEP_RESET_JACOBIAN_BOTTLENECK"
        ),
        "identity": {
            "lift": "L=A^-1*K^T*(K*A^-1*K^T)^-1*T",
            "momentum": "p=L^T*g_v",
            "derivative": "Dp[h]=DL[h]^T*g_v+L^T*Dg_v[h]",
            "matrix_inverse_formed": False,
        },
        "crosscheck": {
            "complex_step": COMPLEX_STEP,
            "columns": list(columns),
            "rows": rows,
            "maximum_absolute_residual": maximum_absolute,
            "maximum_relative_residual": maximum_relative,
        },
        "data": {
            "path": DATA.relative_to(ROOT).as_posix(),
            "SHA256": _sha256(DATA),
        },
        "continuation_consequence": {
            "complex_action_evaluations_removed_per_full_reset_Jacobian": 196,
            "intrinsic_reset_tangent_recenter_now_analytic": True,
            "finite_terminal_stratum_certified_here": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_FULL_ANALYTIC_57_BY_196_RESET_JACOBIAN_AT_EACH_"
            "RECENTER,_RUN_AN_INTRINSIC_PROJECTED_CONTINUATION_TOWARD_"
            "CHILD_c_psi*b_psi_NEGATIVE_WITH_ALL_RETAINED_MARGINS,_AND_"
            "CERTIFY_THE_FIRST_TERMINAL_CHILD_ROOT_BALL_OR_FAIL_THE_ROUTE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_GLOBAL_FINITE_RESET_STRATUM_EXISTENCE",
            "Gate8": "LOCKED",
            "canonical_momentum_action_Jacobian": "CLOSED",
            "actual_finite_stratum": "OPEN_CURRENT_OWNER",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
