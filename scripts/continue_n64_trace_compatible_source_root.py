"""Take one exact paired Newton step on the N64 joint finite-core map.

The map is unchanged: event and child high Ward constraints plus the complete
four-row nonlinear event-to-child boundary match.  The minimum-action solve is
proposal machinery only.  Exact reevaluation and eta are the authorities.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

import construct_n64_trace_compatible_source_correction as bridge
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT_STATE = Path(os.environ.get(
    "BHSM_N64_TRACE_INPUT_STATE",
    ROOT / (
        "artifacts/n12_continuum_majorant_effectiveness/"
        "BHSM_N64_TRACE_COMPATIBLE_SOURCE_CORRECTION_STATE.npz"
    ),
))
RESULT_STATE = Path(os.environ.get(
    "BHSM_N64_TRACE_RESULT_STATE",
    ROOT / (
        "artifacts/n12_continuum_majorant_effectiveness/"
        "BHSM_N64_TRACE_COMPATIBLE_SOURCE_NEWTON1_STATE.npz"
    ),
))
RESULT = Path(os.environ.get(
    "BHSM_N64_TRACE_RESULT",
    ROOT / (
        "artifacts/n12_continuum_majorant_effectiveness/"
        "BHSM_N64_TRACE_COMPATIBLE_SOURCE_NEWTON1.json"
    ),
))
ORDER = 64


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _split(vector: np.ndarray) -> tuple[np.ndarray, ...]:
    qdim = dimensions(ORDER)["coordinates"]
    return vector[:qdim], vector[qdim:2 * qdim], vector[2 * qdim:]


def _assemble(states: dict[str, tuple[np.ndarray, ...]]) -> dict[str, object]:
    data = {
        side: bridge._sector_linear_data(state)
        for side, state in states.items()
    }
    ae = np.asarray(data["event"]["matrix"])
    ac = np.asarray(data["child"]["matrix"])
    constraints = np.block([
        [ae, np.zeros((ae.shape[0], ac.shape[1]))],
        [np.zeros((ac.shape[0], ae.shape[1])), ac],
    ])
    boundary_blocks = []
    for side in ("event", "child"):
        q = np.asarray(data[side]["q"])
        full = np.zeros((4, int(data[side]["state_dimension"])))
        full[:, :len(q)] = bridge._boundary_jacobian(ORDER, q)
        columns = np.asarray(data[side]["columns"])
        weights = np.asarray(data[side]["column_weights"])
        boundary_blocks.append(full[:, columns] / weights[None, :])
    boundary_matrix = np.column_stack((-boundary_blocks[0], boundary_blocks[1]))
    jump = (
        bridge._boundary_value(ORDER, states["child"][0])
        - bridge._boundary_value(ORDER, states["event"][0])
    )
    residual = np.concatenate((
        np.asarray(data["event"]["source"]),
        np.asarray(data["child"]["source"]),
        jump,
    ))
    return {
        "data": data,
        "matrix": np.vstack((constraints, boundary_matrix)),
        "residual": residual,
        "boundary_jump": jump,
    }


def _eta(states: dict[str, tuple[np.ndarray, ...]]) -> dict[str, float]:
    return {
        side: float(_eta_legendre_minimum(
            ORDER, state[0], state[2], points=4000
        )["minimum"])
        for side, state in states.items()
    }


def main() -> None:
    source = np.load(INPUT_STATE)
    states = {
        side: _split(np.asarray(source[f"{side}_state"], dtype=float))
        for side in ("event", "child")
    }
    before = _assemble(states)
    matrix = np.asarray(before["matrix"])
    residual = np.asarray(before["residual"])
    correction, _, rank, singular = np.linalg.lstsq(
        matrix, -residual, rcond=None
    )
    candidates = {}
    cursor = 0
    for side in ("event", "child"):
        data = before["data"][side]
        count = len(data["columns"])
        action = correction[cursor:cursor + count]
        cursor += count
        raw = np.zeros(int(data["state_dimension"]))
        raw[np.asarray(data["columns"])] = (
            action / np.asarray(data["column_weights"])
        )
        candidates[side] = _split(np.concatenate(states[side]) + raw)

    after = _assemble(candidates)
    eta_before = _eta(states)
    eta_after = _eta(candidates)
    before_norm = float(np.linalg.norm(residual))
    after_norm = float(np.linalg.norm(after["residual"]))
    accepted = bool(
        after_norm < before_norm
        and all(value > 0.0 for value in eta_after.values())
        and int(rank) == matrix.shape[0]
    )
    retained = candidates if accepted else states
    validation = {
        "input_trace_compatible_candidate_consumed": True,
        "unchanged_exact_joint_map_reevaluated_before_and_after": True,
        "paired_normal_Jacobian_full_row_rank": int(rank) == matrix.shape[0],
        "exact_joint_merit_reduced": after_norm < before_norm,
        "eta_admissible_after_proposal": all(
            value > 0.0 for value in eta_after.values()
        ),
        "candidate_acceptance_uses_exact_map_not_linear_prediction": True,
        "state_not_promoted_as_complete_child_root": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "N64_TRACE_COMPATIBLE_SOURCE_NEWTON_ACCEPTED_AS_FINITE_CORE_"
            "PROPOSAL" if accepted else
            "N64_TRACE_COMPATIBLE_SOURCE_NEWTON_REJECTED_EXACT_STATE_RETAINED"
        ),
        "input": {
            "path": str(INPUT_STATE.relative_to(ROOT)).replace("\\", "/"),
            "SHA256": _sha256(INPUT_STATE),
        },
        "order": ORDER,
        "paired_linear_solve": {
            "shape": list(matrix.shape),
            "rank": int(rank),
            "smallest_singular_value": float(singular[-1]),
            "condition_number": float(singular[0] / singular[-1]),
            "action_norm_step": float(np.linalg.norm(correction)),
            "linear_prediction_defect": float(np.linalg.norm(
                matrix @ correction + residual
            )),
        },
        "exact_merit": {
            "before_norm": before_norm,
            "after_norm": after_norm,
            "ratio": after_norm / before_norm,
            "boundary_before_norm": float(np.linalg.norm(before["boundary_jump"])),
            "boundary_after_norm": float(np.linalg.norm(after["boundary_jump"])),
            "eta_before": eta_before,
            "eta_after": eta_after,
        },
        "accepted": accepted,
        "state_status": "FINITE_CORE_PROPOSAL_ONLY_NOT_A_COMPLETE_CHILD_ROOT",
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "REFRESH_THE_EXACT_PAIRED_FINITE_CORE_JACOBIAN_AT_THE_ACCEPTED_"
            "STATE_AND_CONTINUE_ONLY_IF_EXACT_MERIT_DESCENDS;_THEN_BUILD_"
            "THE_LOCAL_FINITE_CORE_RADIUS_BEFORE_APPENDING_THE_ANALYTIC_TAIL"
            if accepted else
            "LOCALIZE_THE_FIRST_DOMINANT_EXACT_ROW_BLOCK_BEFORE_ANY_FURTHER_"
            "FINITE_CORE_PROPOSAL"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        RESULT_STATE,
        order=np.asarray(ORDER),
        event_state=np.concatenate(retained["event"]),
        child_state=np.concatenate(retained["child"]),
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
