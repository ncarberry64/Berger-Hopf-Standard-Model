"""Classify the N48 ordered-event near-zero Hessian cluster.

Raw, action-coordinate, and already-existing boundary-compatible gauge-quotient
spectra are compared at the zero-padded N12 state and the source-restricted
linear correction candidate.  No event equation or branch selector changes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


SOURCE_ORDER = 12
POINTS = tuple(int(value) for value in os.environ.get(
    "BHSM_N48_ORDERED_CLUSTER_POINTS", "96,192"
).split(","))
LINEAR = Path(os.environ.get(
    "BHSM_N48_LINEAR_CANDIDATE_CHECKPOINT",
    ".tmp_n12_full_qvm_linear_correction_candidates.npz",
))
N12 = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N48_ORDERED_CLUSTER_RESULT",
    ".tmp_n48_ordered_event_projector_cluster.json",
))


def _split(state: np.ndarray, order: int) -> tuple[np.ndarray, ...]:
    qdim = dimensions(order)["coordinates"]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def _embed_reference(reference: np.ndarray, target: int) -> np.ndarray:
    q_source = dimensions(SOURCE_ORDER)["coordinates"]
    q_target = dimensions(target)["coordinates"]
    result = np.zeros(q_target + 2 * target)
    result[0] = reference[0]
    for family in range(3):
        result[
            1 + family * target:1 + family * target + SOURCE_ORDER
        ] = reference[
            1 + family * SOURCE_ORDER:1 + (family + 1) * SOURCE_ORDER
        ]
    result[q_target:q_target + SOURCE_ORDER] = reference[
        q_source:q_source + SOURCE_ORDER
    ]
    result[
        q_target + target:q_target + target + SOURCE_ORDER
    ] = reference[q_source + SOURCE_ORDER:q_source + 2 * SOURCE_ORDER]
    return result


def _selected(matrix: np.ndarray, reference: np.ndarray) -> dict[str, object]:
    values, vectors = np.linalg.eigh(matrix)
    normalized_reference = reference / np.linalg.norm(reference)
    overlaps = np.abs(vectors.T @ normalized_reference)
    index = int(np.argmax(overlaps))
    order = np.argsort(np.abs(values))
    position = int(np.where(order == index)[0][0])
    neighbor = min(
        abs(values[index] - values[index - 1]) if index else np.inf,
        abs(values[index + 1] - values[index])
        if index + 1 < values.size else np.inf,
    )
    return {
        "dimension": int(matrix.shape[0]),
        "operator_norm": float(np.max(np.abs(values))),
        "selected_index_by_value": index,
        "selected_absolute_order": position,
        "selected_eigenvalue": float(values[index]),
        "selected_reference_overlap": float(overlaps[index]),
        "selected_neighbor_gap": float(neighbor),
        "eight_smallest_absolute_eigenvalues": values[order[:8]].tolist(),
        "counts_within_absolute_thresholds": {
            str(threshold): int(np.count_nonzero(np.abs(values) < threshold))
            for threshold in (1.0e-12, 1.0e-10, 1.0e-8, 1.0e-6)
        },
    }


def _gauge_indices(order: int) -> np.ndarray:
    qdim = dimensions(order)["coordinates"]
    indices = [0]
    indices.extend(range(1, 1 + order))
    indices.extend(range(1 + 2 * order, 1 + 3 * order))
    indices.extend(qdim + np.arange(order))
    return np.asarray(indices, dtype=int)


def _evaluate(
    state: np.ndarray, order: int, reference: np.ndarray, points: int,
) -> dict[str, object]:
    q, velocity, multipliers = _split(state, order)
    hessian = np.asarray(exact_action_jet_at_state(
        order, q, velocity, multipliers, points=points
    ).hessian, dtype=float)
    qdim = dimensions(order)["coordinates"]
    frequencies = spectral_frequencies(order)
    weights = np.concatenate((
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    normalized = hessian / weights[:, None] / weights[None, :]
    action_reference = weights * reference
    gauge = _gauge_indices(order)
    reference_norm = np.linalg.norm(reference)
    gauge_fraction = float(
        np.linalg.norm(reference[gauge]) / max(1.0e-300, reference_norm)
    )
    gauge_action_reference = action_reference[gauge]
    return {
        "raw_coordinate_Hessian": _selected(hessian, reference),
        "action_coordinate_congruence": _selected(
            normalized, action_reference
        ),
        "existing_principal_gauge_quotient": _selected(
            normalized[np.ix_(gauge, gauge)], gauge_action_reference
        ),
        "embedded_N12_reference_gauge_quotient_fraction": gauge_fraction,
        "raw_Hessian_symmetry_defect": float(np.linalg.norm(
            hessian - hessian.T
        )),
    }


def main() -> None:
    linear = np.load(LINEAR)
    order = int(linear["order"])
    n12 = np.load(N12)
    reference = _embed_reference(
        np.asarray(n12["branch_reference"], dtype=float), order
    )
    states = {
        "embedded": np.asarray(linear["event_embedded_state"], dtype=float),
        "linear_candidate": np.asarray(
            linear["event_candidate_state"], dtype=float
        ),
    }
    evaluations = {
        str(points): {
            name: _evaluate(state, order, reference, points)
            for name, state in states.items()
        }
        for points in POINTS
    }
    payload = {
        "artifact": "BHSM_N48_ORDERED_EVENT_PROJECTOR_CLUSTER_AUDIT",
        "order": order,
        "quadrature_points": list(POINTS),
        "evaluations": evaluations,
        "classification": (
            "ORDERED_EVENT_NEAR_ZERO_CLUSTER_CLASSIFIED_ACROSS_RAW_ACTION_"
            "AND_EXISTING_GAUGE_QUOTIENT_COORDINATES;_DIAGNOSTIC_ONLY"
        ),
        "event_definition_changed": False,
        "linear_candidate_promoted_as_root": False,
        "validation": {
            "quadrature_orders_agree_on_gauge_quotient_gap": bool(all(
                abs(
                    evaluations["96"][state][
                        "existing_principal_gauge_quotient"
                    ]["selected_neighbor_gap"]
                    - evaluations["192"][state][
                        "existing_principal_gauge_quotient"
                    ]["selected_neighbor_gap"]
                ) < 2.0e-11
                for state in states
            )),
            "gauge_quotient_branch_isolated_on_both_states": bool(all(
                evaluations[str(points)][state][
                    "existing_principal_gauge_quotient"
                ]["selected_neighbor_gap"] > 1.0e-8
                for points in POINTS for state in states
            )),
            "zero_padded_and_linear_states_not_promoted": True,
            "event_definition_unchanged": True,
        },
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    payload["validation_passed"] = all(payload["validation"].values())
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
