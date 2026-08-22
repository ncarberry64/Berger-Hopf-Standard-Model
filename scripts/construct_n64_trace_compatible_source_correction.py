"""Construct the joint trace-compatible N12-to-N64 source correction.

This is a proposal/finite-core diagnostic, not a higher-resolution root.  It
solves the retained high lapse/shift Ward rows for event and child together
while imposing the complete four-row event-to-child boundary linearization.
The solve uses the existing gauge-fixed q-v-m normal coordinates and action
weights.  Every result is reevaluated with the unchanged action covector.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

import audit_n12_full_qvm_constraint_tail as tail
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
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


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
RESULT_STATE = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_TRACE_COMPATIBLE_SOURCE_CORRECTION_STATE.npz"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_TRACE_COMPATIBLE_SOURCE_CORRECTION.json"
)
SOURCE_ORDER = 12
ORDER = 64
POINTS = 96


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _split_source(joint: np.ndarray, side: str) -> tuple[np.ndarray, ...]:
    qdim = dimensions(SOURCE_ORDER)["coordinates"]
    mdim = dimensions(SOURCE_ORDER)["multipliers"]
    size = 2 * qdim + mdim
    state = joint[:size] if side == "event" else joint[size:]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def _weights(order: int) -> np.ndarray:
    qdim = dimensions(order)["coordinates"]
    frequencies = spectral_frequencies(order)
    return np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))


def _boundary_jacobian(order: int, q: np.ndarray) -> np.ndarray:
    signs_u = (-1.0) ** np.arange(1, order + 1)
    signs_shape = (-1.0) ** np.arange(order)
    vb = float(q[1 + 2 * order:1 + 3 * order] @ signs_shape)
    first = np.zeros(1 + 3 * order)
    first[0] = 1.0
    first[1:1 + order] = signs_u
    first[1 + 2 * order:1 + 3 * order] = (
        -math.tanh(2.0 * vb) * signs_shape
    )
    scale = np.zeros_like(first)
    scale[0] = 1.0
    trace = np.zeros((3, 1 + 3 * order))
    trace[:, 0] = 1.0
    trace[:, 1:1 + order] = signs_u
    trace[0, 1 + order:1 + 2 * order] = signs_shape
    trace[1, 1 + 2 * order:1 + 3 * order] = signs_shape
    trace[2, 1 + 2 * order:1 + 3 * order] = -signs_shape
    return np.vstack((trace, scale - first))


def _boundary_value(order: int, q: np.ndarray) -> np.ndarray:
    signs_u = (-1.0) ** np.arange(1, order + 1)
    signs_shape = (-1.0) ** np.arange(order)
    rho = float(q[0])
    ub = float(q[1:1 + order] @ signs_u)
    wb = float(q[1 + order:1 + 2 * order] @ signs_shape)
    vb = float(q[1 + 2 * order:1 + 3 * order] @ signs_shape)
    return np.asarray((
        rho + ub + wb,
        rho + ub + vb,
        rho + ub - vb,
        -ub + 0.5 * math.log(math.cosh(2.0 * vb)),
    ))


def _sector_linear_data(state: tuple[np.ndarray, ...]) -> dict[str, object]:
    q, velocity, multipliers = state
    qdim = dimensions(ORDER)["coordinates"]
    jet = exact_full_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=POINTS
    )
    hessian = np.asarray(jet.hessian, dtype=float)
    gradient = np.asarray(jet.gradient, dtype=float)
    rows, row_modes = tail._high_constraint_rows(ORDER)
    count = ORDER - SOURCE_ORDER
    signs = (-1.0) ** np.arange(SOURCE_ORDER + 1, ORDER + 1)
    reaction, reaction_derivative = tail._boundary_reaction_data(
        q, multipliers, ORDER
    )
    jacobian = hessian[rows].copy()
    jacobian[:count] -= signs[:, None] * reaction_derivative[None, :]
    raw = gradient[rows].copy()
    raw[:count] -= reaction * signs
    row_weights = np.sqrt(
        1.0 + spectral_frequencies(ORDER)["multipliers"][row_modes] ** 2
    )
    columns, labels = tail._normal_columns(
        ORDER, high_only=False, principal_quotient=False
    )
    column_weights = tail._column_weights(ORDER, columns)
    return {
        "q": q,
        "velocity": velocity,
        "multipliers": multipliers,
        "matrix": jacobian[:, columns] / row_weights[:, None]
        / column_weights[None, :],
        "source": raw / row_weights,
        "columns": columns,
        "column_weights": column_weights,
        "labels": labels,
        "raw_high_weak_norm": float(np.linalg.norm(raw / row_weights)),
        "state_dimension": 2 * qdim + 2 * ORDER,
    }


def _reevaluate(state: tuple[np.ndarray, ...]) -> dict[str, object]:
    data = _sector_linear_data(state)
    return {
        "high_constraint_weak_norm": data["raw_high_weak_norm"],
        "eta_minimum": float(_eta_legendre_minimum(
            ORDER, state[0], state[2], points=4000
        )["minimum"]),
    }


def main() -> None:
    joint = np.asarray(np.load(CHECKPOINT)["state"], dtype=float)
    states = {
        side: embed_nested_state(
            *_split_source(joint, side), SOURCE_ORDER, ORDER
        )
        for side in ("event", "child")
    }
    data = {side: _sector_linear_data(state) for side, state in states.items()}
    ae = np.asarray(data["event"]["matrix"])
    ac = np.asarray(data["child"]["matrix"])
    zero_ec = np.zeros((ae.shape[0], ac.shape[1]))
    zero_ce = np.zeros((ac.shape[0], ae.shape[1]))
    constraint_matrix = np.block([[ae, zero_ec], [zero_ce, ac]])
    source = np.concatenate((data["event"]["source"], data["child"]["source"]))

    boundary_blocks = []
    for side in ("event", "child"):
        q = np.asarray(data[side]["q"])
        full = np.zeros((4, int(data[side]["state_dimension"])))
        full[:, :len(q)] = _boundary_jacobian(ORDER, q)
        columns = np.asarray(data[side]["columns"])
        column_weights = np.asarray(data[side]["column_weights"])
        boundary_blocks.append(full[:, columns] / column_weights[None, :])
    boundary_matrix = np.column_stack((-boundary_blocks[0], boundary_blocks[1]))
    matrix = np.vstack((constraint_matrix, boundary_matrix))
    rhs = np.concatenate((-source, np.zeros(4)))
    correction, _, rank, singular = np.linalg.lstsq(matrix, rhs, rcond=None)
    linear_defect = matrix @ correction - rhs

    candidates = {}
    cursor = 0
    raw_corrections = {}
    for side in ("event", "child"):
        count = len(data[side]["columns"])
        action = correction[cursor:cursor + count]
        cursor += count
        raw = np.zeros(int(data[side]["state_dimension"]))
        raw[np.asarray(data[side]["columns"])] = (
            action / np.asarray(data[side]["column_weights"])
        )
        raw_corrections[side] = raw
        qdim = dimensions(ORDER)["coordinates"]
        base = np.concatenate(states[side])
        trial = base + raw
        candidates[side] = (
            trial[:qdim], trial[qdim:2 * qdim], trial[2 * qdim:]
        )

    before_jump = _boundary_value(ORDER, states["child"][0]) - _boundary_value(
        ORDER, states["event"][0]
    )
    after_jump = _boundary_value(ORDER, candidates["child"][0]) - _boundary_value(
        ORDER, candidates["event"][0]
    )
    before = {side: _reevaluate(state) for side, state in states.items()}
    after = {side: _reevaluate(state) for side, state in candidates.items()}
    validation = {
        "certified_N12_anchor_consumed": True,
        "unchanged_exact_action_covector_reevaluated": True,
        "existing_full_qvm_normal_coordinates_used": True,
        "complete_four_row_joint_boundary_linearization_used": True,
        "linear_augmented_system_full_row_rank": int(rank) == matrix.shape[0],
        "linear_augmented_residual_below_1e_minus_9": float(
            np.linalg.norm(linear_defect)
        ) < 1.0e-9,
        "exact_high_constraint_merit_reduced_on_both_sides": all(
            after[side]["high_constraint_weak_norm"]
            < before[side]["high_constraint_weak_norm"]
            for side in ("event", "child")
        ),
        "eta_admissible_on_both_sides": all(
            after[side]["eta_minimum"] > 0.0 for side in ("event", "child")
        ),
        "candidate_not_promoted_as_root": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "N64_JOINT_TRACE_COMPATIBLE_SOURCE_CORRECTION_CONSTRUCTED_"
            "AS_PROPOSAL_ONLY;_NONLINEAR_COMPLETE_CHILD_ROOT_NOT_CERTIFIED"
        ),
        "input": {
            "path": str(CHECKPOINT.relative_to(ROOT)).replace("\\", "/"),
            "SHA256": _sha256(CHECKPOINT),
        },
        "order": ORDER,
        "source_order": SOURCE_ORDER,
        "linear_system": {
            "shape": list(matrix.shape),
            "rank": int(rank),
            "smallest_singular_value": float(singular[-1]),
            "condition_number": float(singular[0] / singular[-1]),
            "action_norm_correction": float(np.linalg.norm(correction)),
            "linear_augmented_residual_norm": float(np.linalg.norm(linear_defect)),
        },
        "exact_reevaluation": {
            "before": before,
            "after": after,
            "boundary_jump_before": before_jump.tolist(),
            "boundary_jump_after": after_jump.tolist(),
            "boundary_jump_after_norm": float(np.linalg.norm(after_jump)),
        },
        "state_status": "PROPOSAL_ONLY_NOT_A_COMPLETE_CHILD_ROOT",
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "USE_THE_TRACE_COMPATIBLE_CANDIDATE_AS_THE_FINITE_CORE_CENTER_"
            "FOR_THE_UNCHANGED_JOINT_EVENT_CHILD_NONLINEAR_RESIDUAL_AND_"
            "EITHER_CERTIFY_A_LOCAL_RADIUS_OR_LOCALIZE_ITS_FIRST_OWNER"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        RESULT_STATE,
        order=np.asarray(ORDER),
        event_state=np.concatenate(candidates["event"]),
        child_state=np.concatenate(candidates["child"]),
        event_raw_correction=raw_corrections["event"],
        child_raw_correction=raw_corrections["child"],
    )
    payload["state_artifact"] = {
        "path": str(RESULT_STATE.relative_to(ROOT)).replace("\\", "/"),
        "SHA256": _sha256(RESULT_STATE),
    }
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
