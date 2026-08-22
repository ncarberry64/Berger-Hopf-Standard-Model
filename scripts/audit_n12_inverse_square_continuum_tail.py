"""Audit the retained weak high-shell tail at the certified N12 anchor.

This script is diagnostic only.  It does not promote sampled higher-order
states as roots and does not replace the analytic inverse-square theorem.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _embedded_weak_bulk_constraint_data,
)


CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    ".tmp_direct_n12_complete_persistent_child_promotion.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_TAIL_AUDIT",
    ".tmp_direct_n12_inverse_square_continuum_tail.json",
))
SOURCE_ORDER = 12
MAXIMUM_ORDER = int(os.environ.get("BHSM_N12_TAIL_MAXIMUM_ORDER", "48"))
POINT_COUNTS = tuple(int(value) for value in os.environ.get(
    "BHSM_N12_TAIL_POINT_COUNTS", "256,512"
).split(","))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _exact_mapping(state: np.ndarray) -> dict[str, list[str]]:
    qdim = 1 + 3 * SOURCE_ORDER
    mdim = 2 * SOURCE_ORDER
    return {
        "coordinates": [float(value).hex() for value in state[:qdim]],
        "velocities": [
            float(value).hex() for value in state[qdim:2 * qdim]
        ],
        "multipliers": [
            float(value).hex() for value in state[2 * qdim:2 * qdim + mdim]
        ],
    }


def _tail_rows(data: dict[str, np.ndarray]) -> list[dict[str, float | int]]:
    lapse = np.asarray(data["bulk_lapse"], dtype=float)
    shift = np.asarray(data["bulk_shift"], dtype=float)
    frequencies = np.asarray(data["frequencies"], dtype=float)
    weights2 = 1.0 / (1.0 + frequencies**2)
    cuts = [
        cut for cut in (12, 16, 20, 24, 32, 40, 47)
        if cut < MAXIMUM_ORDER
    ]
    rows = []
    for cut in cuts:
        high = np.arange(MAXIMUM_ORDER) >= cut
        shell = np.sqrt(
            weights2[:MAXIMUM_ORDER] * lapse**2
            + weights2[MAXIMUM_ORDER:] * shift**2
        )
        tail = math.sqrt(float(np.sum(shell[high] ** 2)))
        rows.append({
            "cutoff_N": cut,
            "bulk_constraint_H_minus_1_tail_norm": tail,
            "first_omitted_shell_weak_norm": float(shell[cut]),
            "N_squared_first_shell_weak_norm": float(cut**2 * shell[cut]),
            "first_omitted_lapse_coefficient": float(lapse[cut]),
            "first_omitted_shift_coefficient": float(shift[cut]),
        })
    return rows


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the direct N12 anchor is not certified")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    sdim = 2 * (1 + 3 * SOURCE_ORDER) + 2 * SOURCE_ORDER
    states = {
        "event": joint[:sdim],
        "child": joint[sdim:],
    }
    evaluations: dict[str, dict[str, object]] = {}
    for points in POINT_COUNTS:
        by_state = {}
        for name, state in states.items():
            data = _embedded_weak_bulk_constraint_data(
                _exact_mapping(state),
                source_order=SOURCE_ORDER,
                maximum_order=MAXIMUM_ORDER,
                points=points,
            )
            by_state[name] = {
                "boundary_coefficient": data["boundary_coefficient"],
                "rows": _tail_rows(data),
            }
        evaluations[str(points)] = by_state

    coarse = evaluations[str(POINT_COUNTS[0])]
    fine = evaluations[str(POINT_COUNTS[-1])]
    comparison = {}
    for name in states:
        coarse_rows = coarse[name]["rows"]
        fine_rows = fine[name]["rows"]
        comparison[name] = [{
            "cutoff_N": left["cutoff_N"],
            "absolute_tail_difference": abs(
                right["bulk_constraint_H_minus_1_tail_norm"]
                - left["bulk_constraint_H_minus_1_tail_norm"]
            ),
            "relative_tail_difference": abs(
                right["bulk_constraint_H_minus_1_tail_norm"]
                - left["bulk_constraint_H_minus_1_tail_norm"]
            ) / max(
                np.finfo(float).tiny,
                right["bulk_constraint_H_minus_1_tail_norm"],
            ),
        } for left, right in zip(coarse_rows, fine_rows)]

    payload = {
        "classification": (
            "N12_CERTIFIED_ANCHOR_INVERSE_SQUARE_WEAK_TAIL_DIAGNOSTIC_"
            "ONLY;_FULL_CONTINUUM_NORMAL_SCHUR_AND_ORDERED_EVENT_"
            "TAIL_ENCLOSURES_REMAIN_REQUIRED"
        ),
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "source_promotion": str(PROMOTION),
        "source_promotion_SHA256": _sha256(PROMOTION),
        "source_order": SOURCE_ORDER,
        "maximum_probe_order": MAXIMUM_ORDER,
        "quadrature_point_counts": POINT_COUNTS,
        "evaluations": evaluations,
        "quadrature_comparison": comparison,
        "interpretation": {
            "higher_order_states_are_complete_child_roots": False,
            "sampled_tail_is_the_analytic_inverse_square_proof": False,
            "boundary_covector_routed_to_existing_weak_reaction": True,
            "unchanged_retained_action_used": True,
            "new_equation_constraint_gate_or_scale": False,
        },
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_missing_certificate": (
            "EXPLICIT_ACTION_NORM_N12_TO_INFINITY_COMPACT_TAIL_MODULUS_"
            "FOR_THE_FULL_GAUGE_REDUCED_EVENT_CHILD_NORMAL_SCHUR_"
            "OPERATOR_AND_THE_ORDERED_EVENT_SPECTRAL_PROJECTOR,_WITH_"
            "GAUSS_QUADRATURE_CONSISTENCY_ENCLOSED"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
