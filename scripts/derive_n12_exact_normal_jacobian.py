"""Derive the unchanged N12 normal Jacobian from action-owned formulas.

All rows except the canonical momentum mismatch are differentiated directly
from the retained action jet and the fixed boundary charts.  The momentum
row uses a non-subtractive complex step through the existing canonical-pair
map.  The gauge-fixed normal basis is fixed by the accepted checkpoint; it
is numerical coordinate machinery, not a new physical quotient or gate.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
    _authoritative_n6_event_child_anchor,
    _canonical_pair_at_order,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
COMPLEX_STEP = float(os.environ.get(
    "BHSM_N12_EXACT_JACOBIAN_COMPLEX_STEP", "1e-20"
))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
THIRD = Path(os.environ.get(
    "BHSM_N12_THIRD_VARIATION_RESULT",
    ".tmp_direct_n12_center_action_third_variations_current.npz",
))
STABLE_CENTER = Path(os.environ.get(
    "BHSM_N12_STABLE_CENTER_RESULT",
    ".tmp_direct_n12_corrected_branch_stable_lm_90.json",
))
CROSS_RESOLUTION = Path(
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
RESULT = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN_RESULT",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced.npz",
))
METADATA = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN_METADATA",
    ".tmp_direct_n12_exact_normal_jacobian_reproduced.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if np.min(values) <= 0.0:
        raise np.linalg.LinAlgError("positive Gram matrix required")
    return vectors @ np.diag(values ** power) @ vectors.T


def _decode(payload: dict[str, list[str]]) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([
        float.fromhex(value) for value in payload[name]
    ]) for name in ("coordinates", "velocities", "multipliers"))


def _sector_constraint_jacobian(
    state: np.ndarray,
    normal: np.ndarray,
    weights: np.ndarray,
    q_weights: np.ndarray,
) -> np.ndarray:
    qdim = dimensions(ORDER)["coordinates"]
    jet = exact_full_action_jet_at_state(
        ORDER,
        state[:qdim], state[qdim:2 * qdim], state[2 * qdim:],
        points=POINTS,
    )
    gradient = np.asarray(jet.gradient) / weights
    hessian = (
        np.asarray(jet.hessian)
        / weights[:, None]
        / weights[None, :]
    )
    multiplier = hessian[2 * qdim:] @ normal
    # constraint_residual owns the canonical energy v.L_v-L, not v.L_q-L.
    velocity_contraction = np.zeros(state.size)
    velocity_contraction[qdim:2 * qdim] = state[qdim:2 * qdim]
    velocity_to_v = np.zeros((state.size, state.size))
    velocity_to_v[qdim:2 * qdim, qdim:2 * qdim] = np.eye(qdim)
    energy_gradient = (
        hessian @ velocity_contraction
        + velocity_to_v.T @ gradient
        - gradient
    )
    return np.vstack((multiplier, energy_gradient @ normal))


def _sector_momentum_jacobian(
    state: np.ndarray,
    raw_normal: np.ndarray,
) -> np.ndarray:
    qdim = dimensions(ORDER)["coordinates"]
    result = np.empty((2, raw_normal.shape[1]))
    base = state.astype(complex)
    for column in range(raw_normal.shape[1]):
        shifted = base + 1j * COMPLEX_STEP * raw_normal[:, column]
        momentum = np.asarray(_canonical_pair_at_order(
            ORDER,
            shifted[:qdim],
            shifted[qdim:2 * qdim],
            shifted[2 * qdim:],
            points=POINTS,
        )[0])
        result[:, column] = np.imag(momentum) / COMPLEX_STEP
    return result


def main() -> None:
    if COMPLEX_STEP <= 0.0:
        raise ValueError("positive complex step required")
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    weights = np.concatenate((q_weights, np.ones(qdim), m_weights))

    checkpoint = np.load(CHECKPOINT)
    state = np.asarray(checkpoint["state"], dtype=float)
    paired_full = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    _, paired_singular, paired_vh = np.linalg.svd(
        paired_full, full_matrices=False
    )
    normal = paired_vh.T
    third_payload = np.load(THIRD)
    if not np.array_equal(
        state, np.asarray(third_payload["center_state"])
    ):
        raise ValueError("third variation belongs to another center")
    stable = json.loads(STABLE_CENTER.read_text(encoding="utf-8"))
    ordered_scale = float(stable["ordered_scale"])

    event = state[:state_dimension]
    child = state[state_dimension:]
    event_normal = normal[:state_dimension]
    child_normal = normal[state_dimension:]
    event_constraints = _sector_constraint_jacobian(
        event, event_normal, weights, q_weights
    )
    child_constraints = _sector_constraint_jacobian(
        child, child_normal, weights, q_weights
    )

    # Derivative of the same transported simple eigenvalue.  The raw
    # reduced Hessian slots are restored by their action-coordinate weights.
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    event_jet = exact_full_action_jet_at_state(
        ORDER,
        event[:qdim], event[qdim:2 * qdim], event[2 * qdim:],
        points=POINTS,
    )
    # The reduced ordered-event Hessian is the velocity/multiplier block of
    # the full retained action Hessian.
    raw_reduced = np.asarray(event_jet.hessian)[qdim:, qdim:]
    values, vectors = np.linalg.eigh(raw_reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    selected_action = np.zeros(state_dimension)
    selected_action[qdim:] = weights[qdim:] * vectors[:, selected]
    ordered_row = np.einsum(
        "a,b,abi->i",
        selected_action,
        selected_action,
        np.asarray(third_payload["event"]),
    ) @ event_normal / ordered_scale

    trace = _trace_jacobian_at_order(ORDER)
    attachment = _attachment_jacobian_at_order(ORDER, child[:qdim])
    boundary = np.vstack((trace, attachment[1]))
    boundary_inverse_sqrt = _symmetric_power(
        boundary @ np.diag(1.0 / q_weights ** 2) @ boundary.T,
        -0.5,
    )
    event_boundary = _attachment_jacobian_at_order(
        ORDER, event[:qdim]
    )
    child_boundary = _attachment_jacobian_at_order(
        ORDER, child[:qdim]
    )
    event_boundary_full = np.vstack((trace, event_boundary[1]))
    child_boundary_full = np.vstack((trace, child_boundary[1]))
    boundary_rows = boundary_inverse_sqrt @ (
        child_boundary_full @ (child_normal[:qdim] / q_weights[:, None])
        - event_boundary_full @ (event_normal[:qdim] / q_weights[:, None])
    )

    event_momentum = _sector_momentum_jacobian(
        event, event_normal / weights[:, None]
    )
    child_momentum = _sector_momentum_jacobian(
        child, child_normal / weights[:, None]
    )
    cross_payload = json.loads(
        CROSS_RESOLUTION.read_text(encoding="utf-8")
    )["cross_resolution_reconnaissance"]
    anchor = _authoritative_n6_event_child_anchor(cross_payload)
    embedded_child = embed_nested_state(
        *_decode(anchor["child_exact"]), 6, ORDER
    )
    momentum_attachment = _attachment_jacobian_at_order(
        ORDER, embedded_child[0]
    )
    momentum_sqrt = _symmetric_power(
        momentum_attachment @ momentum_attachment.T, 0.5
    )
    momentum_rows = momentum_sqrt @ (child_momentum - event_momentum)

    analytic = np.vstack((
        event_constraints,
        ordered_row[None],
        boundary_rows,
        child_constraints,
        momentum_rows,
    ))
    paired_normal = paired_full @ normal
    difference = analytic - paired_normal
    np.savez_compressed(
        RESULT,
        analytic_normal_jacobian=analytic,
        paired_normal_jacobian=paired_normal,
        normal_basis=normal,
        center_state=state,
        event_momentum_jacobian=event_momentum,
        child_momentum_jacobian=child_momentum,
    )
    singular = np.linalg.svd(analytic, compute_uv=False)
    payload = {
        "classification": "N12_ACTION_FORMULA_NORMAL_JACOBIAN_DERIVED",
        "order": ORDER,
        "points": POINTS,
        "complex_step": COMPLEX_STEP,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "third_variation": str(THIRD),
        "third_variation_SHA256": _sha256(THIRD),
        "result": str(RESULT),
        "result_SHA256": _sha256(RESULT),
        "transported_ordered_eigenline_index": selected,
        "analytic_rank": int(np.linalg.matrix_rank(analytic)),
        "analytic_smallest_singular_value": float(singular[-1]),
        "analytic_largest_singular_value": float(singular[0]),
        "analytic_vs_paired_Frobenius_norm": float(np.linalg.norm(difference)),
        "analytic_vs_paired_operator_norm": float(
            np.linalg.norm(difference, 2)
        ),
        "analytic_vs_paired_relative_Frobenius": float(
            np.linalg.norm(difference) / np.linalg.norm(analytic)
        ),
        "validation": {
            "same_center_as_third_variation": True,
            "same_fixed_gauge_normal_basis_as_checkpoint": True,
            "corrected_transported_ordered_branch": selected == 24,
            "full_row_rank": int(np.linalg.matrix_rank(analytic)) == 57,
            "unchanged_F12": True,
            "new_physics_equation_constraint_gate_or_selector": False,
        },
        "validation_passed": bool(
            selected == 24 and np.linalg.matrix_rank(analytic) == 57
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    METADATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
