"""Derive an independently enclosed N12 canonical-momentum Hessian.

The retained canonical pair is differentiated by complex step in the first
normal direction.  A short forward difference in the second direction is
used only for the center Hessian enclosure; its truncation is bounded later
by the retained-action third-variation majorant of the composed momentum.
Nothing in this script changes F12 or a physical gate.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _canonical_pair_at_order,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
OUTER_STEP = 1.0e-20
FORWARD_STEP = float(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_FORWARD_STEP", "1e-10"
))
WORKERS = int(os.environ.get("BHSM_N12_MOMENTUM_HESSIAN_WORKERS", "1"))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
EXACT_NORMAL = Path(os.environ.get(
    "BHSM_N12_EXACT_NORMAL_JACOBIAN",
    ".tmp_direct_n12_exact_normal_jacobian.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_ONE_SIDED_RESULT",
    ".tmp_direct_n12_center_momentum_hessian_one_sided.npz",
))
METADATA = Path(os.environ.get(
    "BHSM_N12_MOMENTUM_HESSIAN_ONE_SIDED_METADATA",
    ".tmp_direct_n12_center_momentum_hessian_one_sided.json",
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


def _momentum_jacobian(
    state: np.ndarray,
    raw_directions: np.ndarray,
    qdim: int,
) -> np.ndarray:
    result = np.empty((2, raw_directions.shape[1]))
    complex_state = state.astype(complex)
    for column in range(raw_directions.shape[1]):
        value = _momentum(
            complex_state + 1j * OUTER_STEP * raw_directions[:, column],
            qdim,
        )
        result[:, column] = np.imag(value) / OUTER_STEP
    return result


def _sector_hessian(
    state: np.ndarray,
    normal: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    raw_directions = normal / weights[:, None]
    center_jacobian = _momentum_jacobian(state, raw_directions, qdim)
    columns = normal.shape[1]
    result = np.empty((2, columns, columns))
    arguments = [(
        state,
        raw_directions,
        qdim,
        center_jacobian,
        second,
    ) for second in range(columns)]
    if WORKERS == 1:
        derived = map(_sector_hessian_column, arguments)
    else:
        executor = ProcessPoolExecutor(max_workers=WORKERS)
        derived = executor.map(_sector_hessian_column, arguments)
    try:
        for second, column in derived:
            result[:, :, second] = column
    finally:
        if WORKERS != 1:
            executor.shutdown()
    return result, center_jacobian


def _sector_hessian_column(
    argument: tuple[np.ndarray, np.ndarray, int, np.ndarray, int],
) -> tuple[int, np.ndarray]:
    state, raw_directions, qdim, center_jacobian, second = argument
    shifted = state + FORWARD_STEP * raw_directions[:, second]
    shifted_jacobian = _momentum_jacobian(shifted, raw_directions, qdim)
    return second, (shifted_jacobian - center_jacobian) / FORWARD_STEP


def main() -> None:
    if FORWARD_STEP <= 0.0 or OUTER_STEP <= 0.0:
        raise ValueError("positive differentiation steps required")
    if WORKERS <= 0:
        raise ValueError("positive worker count required")
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
    exact = np.load(EXACT_NORMAL)
    normal = np.asarray(exact["normal_basis"], dtype=float)
    if not np.array_equal(joint, np.asarray(exact["center_state"])):
        raise ValueError("exact normal Jacobian belongs to another center")
    event, event_jacobian = _sector_hessian(
        joint[:state_dimension], normal[:state_dimension], weights
    )
    child, child_jacobian = _sector_hessian(
        joint[state_dimension:], normal[state_dimension:], weights
    )
    mismatch = child - event
    np.savez_compressed(
        RESULT,
        event=event,
        child=child,
        mismatch=mismatch,
        event_momentum_jacobian=event_jacobian,
        child_momentum_jacobian=child_jacobian,
        center_state=joint,
        normal_basis=normal,
    )
    payload = {
        "classification": (
            "N12_CENTER_MOMENTUM_HESSIAN_ONE_SIDED_PROOF_APPROXIMATION"
        ),
        "order": ORDER,
        "points": POINTS,
        "forward_action_coordinate_step": FORWARD_STEP,
        "parallel_workers": WORKERS,
        "outer_complex_step": OUTER_STEP,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "exact_normal_jacobian": str(EXACT_NORMAL),
        "exact_normal_jacobian_SHA256": _sha256(EXACT_NORMAL),
        "result": str(RESULT),
        "result_SHA256": _sha256(RESULT),
        "mismatch_Frobenius_norm": float(np.linalg.norm(mismatch)),
        "mismatch_component_operator_norms": [
            float(np.linalg.norm(mismatch[index], 2)) for index in range(2)
        ],
        "validation": {
            "same_center_as_exact_normal_jacobian": True,
            "unchanged_canonical_pair": True,
            "truncation_promoted_without_majorant": False,
            "physical_equation_gate_or_selector_changed": False,
        },
        "validation_passed": True,
        "scope": (
            "CENTER_APPROXIMATION_ONLY;_THE_COMPOSED_THIRD_VARIATION_"
            "MUST_ENCLOSE_THE_FORWARD_TRUNCATION_BEFORE_CERTIFICATION"
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    METADATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
