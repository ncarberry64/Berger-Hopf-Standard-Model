"""Derive the exact N12-to-infinity trace/attachment tail modulus.

Only the existing nested cosine basis and action-coordinate H1 weights enter.
No sampled higher-order state, fit, equation, or acceptance gate is used.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    ".tmp_direct_n12_complete_persistent_child_promotion.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_BOUNDARY_TAIL_MODULUS",
    ".tmp_direct_n12_exact_boundary_tail_modulus.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _positive_mode_series() -> float:
    """Return sum_{n>=1} (1+16 n^2)^-1 by its exact coth identity."""

    return 0.5 * ((math.pi / 4.0) / math.tanh(math.pi / 4.0) - 1.0)


def _tail_sums(order: int) -> tuple[float, float]:
    total = _positive_mode_series()
    # u modes are indexed n=1,...,N; their omitted tail starts at N+1.
    u_retained = sum(1.0 / (1.0 + 16.0 * n * n)
                     for n in range(1, order + 1))
    # windowed w,v modes are indexed j=0,...,N-1; their tail starts at N.
    j_retained_positive = sum(1.0 / (1.0 + 16.0 * j * j)
                              for j in range(1, order))
    return total - u_retained, total - j_retained_positive


def _single_state_boundary_gram(tanh_two_v: float,
                                u_tail: float,
                                j_tail: float) -> np.ndarray:
    # Rows are the unchanged three trace coordinates followed by the second
    # attachment coordinate q_c-q_w used by the N12 child map.
    u_rows = np.asarray([1.0, 1.0, 1.0, -1.0])
    w_rows = np.asarray([1.0, 0.0, 0.0, 0.0])
    v_rows = np.asarray([0.0, 1.0, -1.0, tanh_two_v])
    return (
        u_tail * np.outer(u_rows, u_rows)
        + j_tail * np.outer(w_rows, w_rows)
        + j_tail * np.outer(v_rows, v_rows)
    )


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the certified N12 anchor is required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    qdim = 1 + 3 * ORDER
    mdim = 2 * ORDER
    sdim = 2 * qdim + mdim
    event_q = joint[:qdim]
    child_q = joint[sdim:sdim + qdim]
    u_tail, j_tail = _tail_sums(ORDER)

    def tanh_boundary(q: np.ndarray) -> float:
        signs = (-1.0) ** np.arange(ORDER)
        v_boundary = float(q[1 + 2 * ORDER:1 + 3 * ORDER] @ signs)
        return math.tanh(2.0 * v_boundary)

    event_tanh = tanh_boundary(event_q)
    child_tanh = tanh_boundary(child_q)
    event_gram = _single_state_boundary_gram(event_tanh, u_tail, j_tail)
    child_gram = _single_state_boundary_gram(child_tanh, u_tail, j_tail)

    frequencies = spectral_frequencies(ORDER)["coordinates"]
    q_weights = np.sqrt(1.0 + frequencies**2)
    trace = _trace_jacobian_at_order(ORDER)
    attachment = _attachment_jacobian_at_order(ORDER, child_q)
    retained_boundary = np.vstack((trace, attachment[1]))
    retained_gram = (
        retained_boundary
        @ np.diag(1.0 / q_weights**2)
        @ retained_boundary.T
    )
    values, vectors = np.linalg.eigh(retained_gram)
    inverse_sqrt = (
        vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.T
    )
    # The physical boundary row is child minus event.  Independent action
    # coordinates therefore add their exact high-shell row Grams.
    joint_raw_gram = child_gram + event_gram
    normalized_gram = inverse_sqrt @ joint_raw_gram @ inverse_sqrt.T
    raw_modulus = math.sqrt(float(np.linalg.eigvalsh(joint_raw_gram)[-1]))
    normalized_modulus = math.sqrt(float(
        np.linalg.eigvalsh(normalized_gram)[-1]
    ))

    # Cross-check the closed form against a long finite partial sum plus a
    # positive integral remainder bracket.  This is an identity check, not
    # the source of the theorem.
    cutoff = 1_000_000
    u_partial = sum(1.0 / (1.0 + 16.0 * n * n)
                    for n in range(ORDER + 1, cutoff + 1))
    j_partial = sum(1.0 / (1.0 + 16.0 * n * n)
                    for n in range(ORDER, cutoff + 1))
    remainder_upper = 1.0 / (16.0 * cutoff)
    identity_check = {
        "u_closed_minus_partial": u_tail - u_partial,
        "j_closed_minus_partial": j_tail - j_partial,
        "positive_integral_remainder_upper": remainder_upper,
        "both_differences_inside_positive_remainder_bracket": bool(
            0.0 < u_tail - u_partial < remainder_upper
            and 0.0 < j_tail - j_partial < remainder_upper
        ),
    }
    validation = {
        "certified_N12_anchor_consumed": True,
        "exact_coth_series_identity_used": True,
        "existing_action_coordinate_weights_used": True,
        "event_and_child_boundary_derivatives_included": True,
        "retained_boundary_row_normalization_included": True,
        "series_identity_cross_check_passed": identity_check[
            "both_differences_inside_positive_remainder_bracket"
        ],
        "no_higher_order_probe_promoted_as_root": True,
        "no_new_equation_constraint_gate_scale_or_fit": True,
    }
    payload = {
        "classification": "N12_EXACT_TRACE_ATTACHMENT_HIGH_SHELL_MODULUS_DERIVED",
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "source_promotion": str(PROMOTION),
        "source_promotion_SHA256": _sha256(PROMOTION),
        "basis_series": {
            "positive_mode_identity": (
                "sum_(n>=1)(1+16*n^2)^-1="
                "((pi/4)*coth(pi/4)-1)/2"
            ),
            "u_tail_starts_at_mode": ORDER + 1,
            "windowed_w_v_tail_starts_at_mode": ORDER,
            "u_tail_sum": u_tail,
            "windowed_tail_sum": j_tail,
        },
        "boundary_state_data": {
            "event_tanh_two_v_boundary": event_tanh,
            "child_tanh_two_v_boundary": child_tanh,
        },
        "joint_child_minus_event_tail": {
            "raw_action_H1_to_boundary_operator_norm": raw_modulus,
            "existing_normalized_boundary_operator_norm": normalized_modulus,
            "raw_row_gram": joint_raw_gram.tolist(),
            "normalized_row_gram": normalized_gram.tolist(),
        },
        "identity_cross_check": identity_check,
        "scope": {
            "trace_attachment_compact_tail_closed": True,
            "bulk_Euler_Dirac_normal_tail_closed_here": False,
            "ordered_event_spectral_projector_tail_closed_here": False,
            "canonical_momentum_flux_tail_closed_here": False,
            "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        },
        "exact_next_dependency": (
            "BOUND_THE_REMAINING_INTERIOR_EULER_DIRAC_ORDERED_EVENT_"
            "AND_CANONICAL_MOMENTUM_FLUX_COMPACT_TAIL_BLOCKS_IN_THE_"
            "SAME_ACTION_GRAPH_NORM_AND_CLOSE_THE_FULL_NORMAL_SCHUR_"
            "COMPLEMENT"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
