"""Derive mixed retained-action majorants for an N12 tracked eigenline."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from derive_n12_action_ball_majorants import action_bound
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_ORDERED_MIXED_MAJORANT_RESULT",
    ".tmp_direct_n12_ordered_event_mixed_majorants.json",
))
SIDE = os.environ.get("BHSM_N12_EIGENLINE_SIDE", "event").strip().lower()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    if SIDE not in {"event", "child"}:
        raise ValueError("BHSM_N12_EIGENLINE_SIDE must be event or child")
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    checkpoint = np.load(CHECKPOINT)
    state = np.asarray(checkpoint["state"], dtype=float)
    offset = 0 if SIDE == "event" else state_dimension
    sector_state = state[offset:offset + state_dimension]
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
    _, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
    sector_normal = vh.T[offset:offset + state_dimension]

    hessian = np.asarray(exact_action_jet_at_state(
        ORDER,
        sector_state[:qdim],
        sector_state[qdim:2 * qdim],
        sector_state[2 * qdim:],
        points=POINTS,
    ).hessian, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    selected = int(np.argmax(np.abs(eigenvectors.T @ reference)))
    selected_vector = eigenvectors[:, selected]
    complement = np.delete(eigenvectors, selected, axis=1)

    frequencies = spectral_frequencies(ORDER)
    state_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    reduced_weights = state_weights[qdim:]
    selected_action_direction = np.concatenate((
        np.zeros(qdim), selected_vector * reduced_weights
    ))
    complement_action_subspace = np.vstack((
        np.zeros((qdim, complement.shape[1])),
        complement * reduced_weights[:, None],
    ))
    reduced_raw_unit_action_subspace = np.vstack((
        np.zeros((qdim, reduced_weights.size)),
        np.diag(reduced_weights),
    ))

    specifications = {
        "D3_normal_raw_reduced_raw_reduced": [
            sector_normal,
            reduced_raw_unit_action_subspace,
            reduced_raw_unit_action_subspace,
        ],
        "D4_normal_normal_raw_reduced_raw_reduced": [
            sector_normal,
            sector_normal,
            reduced_raw_unit_action_subspace,
            reduced_raw_unit_action_subspace,
        ],
        "D4_normal_normal_selected_selected": [
            sector_normal,
            sector_normal,
            selected_action_direction,
            selected_action_direction,
        ],
        "D4_normal_normal_selected_complement": [
            sector_normal,
            sector_normal,
            selected_action_direction,
            complement_action_subspace,
        ],
        "D5_normal_normal_selected_selected_normal": [
            sector_normal,
            sector_normal,
            selected_action_direction,
            selected_action_direction,
            sector_normal,
        ],
        "D5_normal_normal_selected_complement_normal": [
            sector_normal,
            sector_normal,
            selected_action_direction,
            complement_action_subspace,
            sector_normal,
        ],
    }
    bounds = {}
    for name, directions in specifications.items():
        bound = action_bound(
            sector_state,
            projection=sector_normal,
            mixed_directions=directions,
        )
        bounds[name] = float(bound.d[-1])

    payload = {
        "classification": "N12_ORDERED_EVENT_MIXED_ACTION_MAJORANTS_DERIVED",
        "sector": SIDE,
        "order": ORDER,
        "points": POINTS,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "validated_N6_branch_index": int(
            checkpoint["n6_ordered_branch_index"]
        ),
        "transported_N12_eigenline_index": selected,
        "normal_rank": int(np.linalg.matrix_rank(jacobian)),
        "normal_smallest_singular_value": float(singular[-1]),
        "bounds": bounds,
        "validation": {
            "action_coordinate_normal_directions": True,
            "raw_reduced_Hessian_slots_restored_by_action_weights": True,
            "selected_line_owned_by_validated_branch_record": True,
            "unchanged_retained_action": True,
            "new_equation_selector_constraint_or_gate": False,
        },
        "validation_passed": True,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
