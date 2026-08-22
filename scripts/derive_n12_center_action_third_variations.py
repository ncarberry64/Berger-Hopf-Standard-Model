"""Derive the action-normalized N12 third variation at one checkpoint.

This is local certificate machinery for the unchanged retained action.  It
does not alter the N12 residual, event selector, physical gates, or state.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
COMPLEX_STEP = 1.0e-20
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_THIRD_VARIATION_RESULT",
    ".tmp_direct_n12_center_action_third_variations_current.npz",
))
METADATA = Path(os.environ.get(
    "BHSM_N12_THIRD_VARIATION_METADATA",
    ".tmp_direct_n12_center_action_third_variations_current.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _third_variation(state: np.ndarray, weights: np.ndarray) -> np.ndarray:
    qdim = dimensions(ORDER)["coordinates"]
    tensor = np.empty((state.size, state.size, state.size))
    for column in range(state.size):
        shifted = state.astype(complex)
        shifted[column] += 1j * COMPLEX_STEP / weights[column]
        hessian = exact_full_action_jet_at_state(
            ORDER,
            shifted[:qdim],
            shifted[qdim:2 * qdim],
            shifted[2 * qdim:],
            points=POINTS,
        ).hessian
        tensor[:, :, column] = (
            np.imag(hessian)
            / COMPLEX_STEP
            / weights[:, None]
            / weights[None, :]
        )
    return tensor


def _symmetry_audit(tensor: np.ndarray) -> dict[str, float]:
    permutations = (
        tensor,
        tensor.transpose(0, 2, 1),
        tensor.transpose(1, 0, 2),
        tensor.transpose(1, 2, 0),
        tensor.transpose(2, 0, 1),
        tensor.transpose(2, 1, 0),
    )
    reference_norm = max(float(np.linalg.norm(tensor)), 1.0e-300)
    maximum = max(
        float(np.linalg.norm(candidate - tensor))
        for candidate in permutations
    )
    return {
        "Frobenius_norm": reference_norm,
        "maximum_permutation_defect": maximum,
        "maximum_relative_permutation_defect": maximum / reference_norm,
    }


def main() -> None:
    if COMPLEX_STEP <= 0.0:
        raise ValueError("positive complex step required")
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    frequencies = spectral_frequencies(ORDER)
    state_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    checkpoint = np.load(CHECKPOINT)
    joint_state = np.asarray(checkpoint["state"], dtype=float)
    if joint_state.shape != (2 * state_dimension,):
        raise ValueError("checkpoint is not the N12 joint event-child state")
    event = _third_variation(
        joint_state[:state_dimension], state_weights
    )
    child = _third_variation(
        joint_state[state_dimension:], state_weights
    )
    np.savez_compressed(
        RESULT,
        event=event,
        child=child,
        center_state=joint_state,
        state_weights=state_weights,
    )
    payload = {
        "classification": "N12_CENTER_ACTION_THIRD_VARIATION_DERIVED",
        "order": ORDER,
        "points": POINTS,
        "complex_step": COMPLEX_STEP,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "result": str(RESULT),
        "result_SHA256": _sha256(RESULT),
        "action_coordinates": True,
        "event": _symmetry_audit(event),
        "child": _symmetry_audit(child),
        "unchanged_retained_action": True,
        "checkpoint_modified": False,
        "new_physics_equation_constraint_or_gate": False,
        "FULL_BHSM_COMPLETE": False,
    }
    METADATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
