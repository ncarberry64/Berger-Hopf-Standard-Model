"""Evaluate the N48 source-tail linear correction in the unchanged map.

The candidate is proposal evidence only.  It is not a complete-child root and
cannot be promoted without the full joint event, boundary, momentum, ordered
event, nonlinear radius, eta, and persistence certificates.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _eta_legendre_minimum,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


SOURCE_ORDER = 12
POINTS = int(os.environ.get("BHSM_N48_CANDIDATE_POINTS", "96"))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N48_LINEAR_CANDIDATE_CHECKPOINT",
    ".tmp_n12_full_qvm_linear_correction_candidates.npz",
))
N12_CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N48_LINEAR_CANDIDATE_RESULT",
    ".tmp_n48_linear_correction_candidate_audit.json",
))


def _split(state: np.ndarray, order: int) -> tuple[np.ndarray, ...]:
    qdim = dimensions(order)["coordinates"]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def _boundary_coefficient(
    order: int, q: np.ndarray, multipliers: np.ndarray,
) -> float:
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary = float(q[1:1 + order] @ signs_k)
    b_boundary = float(q[1 + 2 * order:1 + 3 * order] @ signs_j)
    radius = RADIUS0 * math.exp(float(q[0]))
    a = radius * math.exp(u_boundary + b_boundary) / math.sqrt(2.0)
    b = radius * math.exp(u_boundary - b_boundary) / math.sqrt(2.0)
    r4 = a * b / math.sqrt(a * a + b * b)
    lapse = math.exp(float(multipliers[:order] @ signs_k))
    return -standard_model_casimir_coefficient() * lapse / r4


def _constraint_blocks(state: np.ndarray, order: int) -> dict[str, float]:
    q, velocity, multipliers = _split(state, order)
    residual = constraint_residual(
        order, q, velocity, multipliers, points=POINTS
    )
    frequencies = spectral_frequencies(order)["multipliers"]
    weights = np.sqrt(1.0 + frequencies ** 2)
    coefficient = _boundary_coefficient(order, q, multipliers)
    signs = (-1.0) ** np.arange(1, order + 1)
    bulk = residual[:2 * order].copy()
    bulk[:order] -= coefficient * signs
    weak_total = residual[:2 * order] / weights
    weak_bulk = bulk / weights
    high = np.concatenate((
        np.arange(SOURCE_ORDER, order),
        order + np.arange(SOURCE_ORDER, order),
    ))
    low = np.concatenate((
        np.arange(SOURCE_ORDER),
        order + np.arange(SOURCE_ORDER),
    ))
    return {
        "total_constraint_weak_norm": float(np.linalg.norm(weak_total)),
        "routed_bulk_constraint_weak_norm": float(np.linalg.norm(weak_bulk)),
        "high_routed_bulk_constraint_weak_norm": float(
            np.linalg.norm(weak_bulk[high])
        ),
        "low_routed_bulk_constraint_weak_norm": float(
            np.linalg.norm(weak_bulk[low])
        ),
        "energy_residual": float(residual[-1]),
        "boundary_reaction_coefficient": coefficient,
    }


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
    return result / np.linalg.norm(result)


def _ordered_event(state: np.ndarray, order: int, reference: np.ndarray) -> dict[str, float | int]:
    q, velocity, multipliers = _split(state, order)
    hessian = np.asarray(exact_action_jet_at_state(
        order, q, velocity, multipliers, points=POINTS
    ).hessian, dtype=float)
    values, vectors = np.linalg.eigh(hessian)
    index = int(np.argmax(np.abs(vectors.T @ reference)))
    overlap = float(abs(vectors[:, index] @ reference))
    gap = min(
        abs(values[index] - values[index - 1]) if index else math.inf,
        abs(values[index + 1] - values[index])
        if index + 1 < values.size else math.inf,
    )
    return {
        "selected_index": index,
        "selected_eigenvalue": float(values[index]),
        "reference_overlap": overlap,
        "neighbor_gap": float(gap),
    }


def _evaluate(state: np.ndarray, order: int) -> dict[str, object]:
    q, _, multipliers = _split(state, order)
    return {
        "constraints": _constraint_blocks(state, order),
        "eta_minimum": float(_eta_legendre_minimum(
            order, q, multipliers, points=4000
        )["minimum"]),
        "finite": bool(np.all(np.isfinite(state))),
    }


def main() -> None:
    payload = np.load(CHECKPOINT)
    order = int(payload["order"])
    if order <= SOURCE_ORDER:
        raise RuntimeError("a higher-order correction candidate is required")
    n12 = np.load(N12_CHECKPOINT)
    reference = _embed_reference(
        np.asarray(n12["branch_reference"], dtype=float), order
    )
    states = {}
    for name in ("event", "child"):
        base = np.asarray(payload[f"{name}_embedded_state"], dtype=float)
        candidate = np.asarray(payload[f"{name}_candidate_state"], dtype=float)
        states[name] = {
            "embedded": _evaluate(base, order),
            "linear_candidate": _evaluate(candidate, order),
            "raw_correction_norm": float(np.linalg.norm(
                payload[f"{name}_raw_correction"]
            )),
        }
    states["event"]["embedded"]["ordered_event"] = _ordered_event(
        np.asarray(payload["event_embedded_state"], dtype=float),
        order,
        reference,
    )
    states["event"]["linear_candidate"]["ordered_event"] = _ordered_event(
        np.asarray(payload["event_candidate_state"], dtype=float),
        order,
        reference,
    )
    trace = _trace_jacobian_at_order(order)
    boundary = {}
    for label in ("embedded", "linear_candidate"):
        event_q = _split(
            np.asarray(payload[f"event_{'embedded_state' if label == 'embedded' else 'candidate_state'}"]),
            order,
        )[0]
        child_q = _split(
            np.asarray(payload[f"child_{'embedded_state' if label == 'embedded' else 'candidate_state'}"]),
            order,
        )[0]
        boundary[label] = {
            "trace_jump_norm": float(np.linalg.norm(trace @ (child_q - event_q))),
            "attachment_second_jump": float(
                _attachment_coordinates_at_order(order, child_q)[1]
                - _attachment_coordinates_at_order(order, event_q)[1]
            ),
        }
    output = {
        "artifact": "BHSM_N48_LINEAR_SOURCE_CORRECTION_NONLINEAR_AUDIT",
        "order": order,
        "states": states,
        "event_child_boundary": boundary,
        "classification": (
            "PROPOSAL_ONLY_NONLINEAR_EVALUATION_OF_THE_SOURCE_RESTRICTED_"
            "LINEAR_CORRECTION;_NOT_A_COMPLETE_CHILD_ROOT_OR_CERTIFICATE"
        ),
        "unchanged_physical_map": True,
        "zero_padded_or_linear_state_promoted_as_root": False,
        "validation": {
            "event_high_bulk_weak_residual_reduced": bool(
                states["event"]["linear_candidate"]["constraints"][
                    "high_routed_bulk_constraint_weak_norm"
                ] < states["event"]["embedded"]["constraints"][
                    "high_routed_bulk_constraint_weak_norm"
                ]
            ),
            "child_high_bulk_weak_residual_reduced": bool(
                states["child"]["linear_candidate"]["constraints"][
                    "high_routed_bulk_constraint_weak_norm"
                ] < states["child"]["embedded"]["constraints"][
                    "high_routed_bulk_constraint_weak_norm"
                ]
            ),
            "eta_admissible": bool(
                states["event"]["linear_candidate"]["eta_minimum"] > 0.0
                and states["child"]["linear_candidate"]["eta_minimum"] > 0.0
            ),
            "candidate_not_promoted": True,
        },
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    output["validation_passed"] = all(output["validation"].values())
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
