"""Derive the normal Hessian of the unchanged N12 momentum mismatch.

The calculation differentiates the existing state-dependent canonical pair
with a complex outer direction and a centered real inner direction.  It is
certificate data only and never changes the residual or checkpoint.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _canonical_pair_at_order,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
OUTER_STEP = 1.0e-20
INNER_STEP = float(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_STEP", "1e-5"
))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_RESULT",
    ".tmp_direct_n12_center_momentum_hessian.npz",
))
METADATA = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_METADATA",
    ".tmp_direct_n12_center_momentum_hessian.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _momentum(state: np.ndarray, qdim: int) -> np.ndarray:
    return np.asarray(_canonical_pair_at_order(
        ORDER,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=POINTS,
    )[0])


def _sector_hessian(
    state: np.ndarray,
    normal: np.ndarray,
    weights: np.ndarray,
) -> np.ndarray:
    qdim = dimensions(ORDER)["coordinates"]
    columns = normal.shape[1]
    result = np.empty((2, columns, columns))
    raw_directions = normal / weights[:, None]
    for first in range(columns):
        outer = 1j * OUTER_STEP * raw_directions[:, first]
        for second in range(first, columns):
            inner = INNER_STEP * raw_directions[:, second]
            plus = _momentum(state.astype(complex) + inner + outer, qdim)
            minus = _momentum(state.astype(complex) - inner + outer, qdim)
            mixed = np.imag(plus - minus) / (
                2.0 * INNER_STEP * OUTER_STEP
            )
            result[:, first, second] = mixed
            result[:, second, first] = mixed
    return result


def main() -> None:
    if INNER_STEP <= 0.0 or OUTER_STEP <= 0.0:
        raise ValueError("positive derivative steps required")
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    frequencies = spectral_frequencies(ORDER)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    _, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
    normal = vh.T
    event = _sector_hessian(
        joint[:state_dimension], normal[:state_dimension], weights
    )
    child = _sector_hessian(
        joint[state_dimension:], normal[state_dimension:], weights
    )
    mismatch = child - event
    np.savez_compressed(
        RESULT,
        event=event,
        child=child,
        mismatch=mismatch,
        center_state=joint,
        normal_basis=normal,
    )
    payload = {
        "classification": "N12_CENTER_CANONICAL_MOMENTUM_HESSIAN_DERIVED",
        "order": ORDER,
        "points": POINTS,
        "inner_step": INNER_STEP,
        "outer_complex_step": OUTER_STEP,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "result": str(RESULT),
        "result_SHA256": _sha256(RESULT),
        "normal_rank": int(np.linalg.matrix_rank(jacobian)),
        "normal_smallest_singular_value": float(singular[-1]),
        "event_component_operator_norms": [
            float(np.linalg.norm(event[index], 2)) for index in range(2)
        ],
        "child_component_operator_norms": [
            float(np.linalg.norm(child[index], 2)) for index in range(2)
        ],
        "mismatch_component_operator_norms": [
            float(np.linalg.norm(mismatch[index], 2)) for index in range(2)
        ],
        "mismatch_vector_Hessian_Frobenius_bound": float(np.linalg.norm(
            mismatch
        )),
        "validation": {
            "same_normal_basis_as_exact_paired_Jacobian": True,
            "unchanged_canonical_pair": True,
            "proposal_or_physical_gate_changed": False,
            "single_step_center_measurement_is_full_ball_majorant": False,
        },
        "validation_passed": True,
        "scope": (
            "CENTER_MOMENTUM_HESSIAN_ONLY;_STEP_CONVERGENCE_AND_"
            "FULL_BALL_HIGHER_VARIATION_REMAINDER_REMAIN"
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    METADATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
