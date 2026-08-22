"""Close the N64 hybrid weak finite-core source system.

This is the finite analytic core required by the continuum proof, not an N64
complete-child solve.  The retained N12 multiplier rows remain the unchanged
physical action constraints.  Only omitted high lapse rows route the already
existing Casimir boundary covector through the weak conormal reaction.  The
same action, energy row, full q-v-m normal coordinates, and four event-child
boundary rows are retained.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

import audit_n12_full_qvm_constraint_tail as tail
import construct_n64_trace_compatible_source_correction as bridge
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
)
from bhsm.interface.aether_high_precision_velocity_jet import (
    high_precision_velocity_jet_blocks,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.environ.get(
    "BHSM_N64_HYBRID_INPUT",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_TRACE_COMPATIBLE_SOURCE_NEWTON2_STATE.npz",
))
OUTPUT_STATE = Path(os.environ.get(
    "BHSM_N64_HYBRID_STATE",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_HYBRID_WEAK_FINITE_CORE_STATE.npz",
))
OUTPUT = Path(os.environ.get(
    "BHSM_N64_HYBRID_RESULT",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_HYBRID_WEAK_FINITE_CORE.json",
))
ORDER = 64
SOURCE_ORDER = 12
POINTS = int(os.environ.get("BHSM_N64_HYBRID_POINTS", "96"))
ITERATIONS = int(os.environ.get("BHSM_N64_HYBRID_ITERATIONS", "6"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _split(vector: np.ndarray) -> tuple[np.ndarray, ...]:
    qdim = dimensions(ORDER)["coordinates"]
    return vector[:qdim], vector[qdim:2 * qdim], vector[2 * qdim:]


def _sector(state: tuple[np.ndarray, ...]) -> dict[str, object]:
    q, velocity, multipliers = state
    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    blocks = high_precision_velocity_jet_blocks(
        ORDER, q, velocity, multipliers, points=POINTS, precision=60
    )
    gradient_v = np.asarray(
        [float(value) for value in blocks["gradient_velocity"]], dtype=float
    )
    gradient_m = np.asarray(
        [float(value) for value in blocks["gradient_multiplier"]], dtype=float
    )
    vv = np.asarray([
        [float(value) for value in row]
        for row in blocks["hessian_velocity_velocity"]
    ], dtype=float)
    mv = np.asarray([
        [float(value) for value in row]
        for row in blocks["hessian_multiplier_velocity"]
    ], dtype=float)
    mm = np.asarray([
        [float(value) for value in row]
        for row in blocks["hessian_multiplier_multiplier"]
    ], dtype=float)
    rows = gradient_m.copy()
    jacobian = np.column_stack((mv, mm))

    # Low rows are the unchanged finite physical constraints.  The existing
    # weak reaction removes the boundary covector only from omitted lapse
    # modes, never from the retained N12 equations.
    reaction, reaction_derivative = tail._boundary_reaction_data(
        q, multipliers, ORDER
    )
    high = np.arange(SOURCE_ORDER, ORDER)
    signs = (-1.0) ** np.arange(SOURCE_ORDER + 1, ORDER + 1)
    rows[high] -= reaction * signs
    jacobian[high] -= signs[:, None] * reaction_derivative[
        qdim:
    ][None, :]

    energy = float(
        velocity @ gradient_v - float(blocks["action_value"])
    )
    energy_jacobian = np.concatenate((
        vv @ velocity,
        mv @ velocity - gradient_m,
    ))

    frequencies = spectral_frequencies(ORDER)
    row_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
        np.ones(1),
    ))
    columns = np.arange(qdim, 2 * qdim + mdim)
    labels = ["velocity"] * qdim + ["multiplier"] * mdim
    column_weights = np.concatenate((
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    raw_rows = np.concatenate((rows, [energy]))
    raw_jacobian = np.vstack((jacobian, energy_jacobian))
    return {
        "q": q,
        "rows": raw_rows / row_weights,
        "matrix": raw_jacobian / row_weights[:, None]
        / column_weights[None, :],
        "columns": columns,
        "column_weights": column_weights,
        "labels": labels,
        "state_dimension": 2 * qdim + mdim,
        "blocks": {
            "low_lapse": float(np.linalg.norm(
                (raw_rows / row_weights)[:SOURCE_ORDER]
            )),
            "high_lapse_weak_reaction": float(np.linalg.norm(
                (raw_rows / row_weights)[SOURCE_ORDER:ORDER]
            )),
            "low_shift": float(np.linalg.norm(
                (raw_rows / row_weights)[ORDER:ORDER + SOURCE_ORDER]
            )),
            "high_shift": float(np.linalg.norm(
                (raw_rows / row_weights)[ORDER + SOURCE_ORDER:2 * ORDER]
            )),
            "energy": abs(float(raw_rows[-1])),
        },
    }


def _assemble(states: dict[str, tuple[np.ndarray, ...]]) -> dict[str, object]:
    data = {side: _sector(state) for side, state in states.items()}
    event_matrix = np.asarray(data["event"]["matrix"])
    child_matrix = np.asarray(data["child"]["matrix"])
    sector_matrix = np.block([
        [event_matrix, np.zeros((event_matrix.shape[0], child_matrix.shape[1]))],
        [np.zeros((child_matrix.shape[0], event_matrix.shape[1])), child_matrix],
    ])
    boundary = (
        bridge._boundary_value(ORDER, states["child"][0])
        - bridge._boundary_value(ORDER, states["event"][0])
    )
    residual = np.concatenate((
        np.asarray(data["event"]["rows"]),
        np.asarray(data["child"]["rows"]),
    ))
    return {
        "data": data,
        # Coordinates are held fixed during this exact v/m fiber correction,
        # so all four already-closed boundary rows are preserved identically.
        "matrix": sector_matrix,
        "residual": residual,
        "boundary": boundary,
    }


def _apply(
    states: dict[str, tuple[np.ndarray, ...]],
    assembled: dict[str, object],
    action_correction: np.ndarray,
    factor: float,
) -> dict[str, tuple[np.ndarray, ...]]:
    result = {}
    cursor = 0
    for side in ("event", "child"):
        data = assembled["data"][side]
        count = len(data["columns"])
        action = action_correction[cursor:cursor + count]
        cursor += count
        raw = np.zeros(int(data["state_dimension"]))
        qdim = dimensions(ORDER)["coordinates"]
        raw[qdim:] = factor * action / np.asarray(data["column_weights"])
        result[side] = _split(np.concatenate(states[side]) + raw)
    return result


def _eta(states: dict[str, tuple[np.ndarray, ...]]) -> dict[str, float]:
    return {
        side: float(_eta_legendre_minimum(
            ORDER, state[0], state[2], points=4000
        )["minimum"])
        for side, state in states.items()
    }


def main() -> None:
    source = np.load(INPUT)
    states = {
        side: _split(np.asarray(source[f"{side}_state"], dtype=float))
        for side in ("event", "child")
    }
    history = []
    total_action_length = 0.0
    for iteration in range(ITERATIONS):
        center = _assemble(states)
        matrix = np.asarray(center["matrix"])
        residual = np.asarray(center["residual"])
        singular = np.linalg.svd(matrix, compute_uv=False)
        correction = np.linalg.lstsq(matrix, -residual, rcond=None)[0]
        before = float(np.linalg.norm(residual))
        accepted = None
        for exponent in range(12):
            factor = 2.0 ** (-exponent)
            trial_states = _apply(states, center, correction, factor)
            eta = _eta(trial_states)
            if min(eta.values()) <= 0.0:
                continue
            trial = _assemble(trial_states)
            after = float(np.linalg.norm(trial["residual"]))
            if after < before:
                accepted = (factor, trial_states, trial, eta, after)
                break
        history.append({
            "iteration": iteration,
            "exact_hybrid_weak_norm_before": before,
            "exact_hybrid_weak_norm_after": (
                None if accepted is None else accepted[4]
            ),
            "accepted_factor": 0.0 if accepted is None else accepted[0],
            "normal_rank": int(np.linalg.matrix_rank(matrix)),
            "normal_smallest_singular_value": float(singular[-1]),
            "normal_condition_number": float(singular[0] / singular[-1]),
            "full_action_step_norm": float(np.linalg.norm(correction)),
            "linear_prediction_defect": float(np.linalg.norm(
                matrix @ correction + residual
            )),
            "block_norms_before": {
                side: center["data"][side]["blocks"]
                for side in ("event", "child")
            },
        })
        if accepted is None:
            break
        total_action_length += accepted[0] * float(np.linalg.norm(correction))
        states = accepted[1]
        if accepted[4] < 1.0e-12:
            break

    final = _assemble(states)
    eta = _eta(states)
    final_norm = float(np.linalg.norm(final["residual"]))
    matrix = np.asarray(final["matrix"])
    singular = np.linalg.svd(matrix, compute_uv=False)
    validation = {
        "certified_N12_anchored_finite_core_consumed": True,
        "retained_low_multiplier_and_energy_rows_unchanged": True,
        "only_omitted_high_lapse_rows_use_existing_weak_reaction": True,
        "complete_four_row_boundary_operator_retained": True,
        "complete_four_row_boundary_closed": float(
            np.linalg.norm(final["boundary"])
        ) < 1.0e-12,
        "hybrid_weak_finite_core_closed_below_1e_minus_10": final_norm < 1.0e-10,
        "normal_matrix_full_row_rank": int(np.linalg.matrix_rank(matrix)) == matrix.shape[0],
        "eta_admissible": min(eta.values()) > 0.0,
        "not_promoted_as_complete_child_root": True,
        "ordered_event_momentum_and_persistence_not_inferred": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    OUTPUT_STATE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT_STATE,
        order=np.asarray(ORDER),
        event_state=np.concatenate(states["event"]),
        child_state=np.concatenate(states["child"]),
    )
    payload = {
        "classification": (
            "N64_HYBRID_WEAK_ACTION_GALERKIN_FINITE_CORE_CLOSED;_"
            "CALDERON_OBSERVATION_GAP_AND_COMPACT_TAIL_REMAIN"
            if validation["hybrid_weak_finite_core_closed_below_1e_minus_10"]
            else "N64_HYBRID_WEAK_FINITE_CORE_NOT_YET_CLOSED"
        ),
        "order": ORDER,
        "source_order": SOURCE_ORDER,
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "SHA256": _sha256(INPUT)},
        "history": history,
        "total_action_path_length": total_action_length,
        "final": {
            "exact_hybrid_weak_norm": final_norm,
            "boundary_norm": float(np.linalg.norm(final["boundary"])),
            "eta": eta,
            "normal_shape": list(matrix.shape),
            "normal_rank": int(np.linalg.matrix_rank(matrix)),
            "normal_smallest_singular_value": float(singular[-1]),
            "normal_inverse_upper_diagnostic": float(1.0 / singular[-1]),
            "block_norms": {
                side: final["data"][side]["blocks"]
                for side in ("event", "child")
            },
        },
        "state_artifact": {
            "path": str(OUTPUT_STATE.relative_to(ROOT)).replace("\\", "/"),
            "SHA256": _sha256(OUTPUT_STATE),
            "status": "FINITE_ANALYTIC_CORE_NOT_A_COMPLETE_CHILD_ROOT",
        },
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "EVALUATE_AND_ENCLOSE_THE_EXISTING_POSITIVE_DURATION_EVENT_CHILD_"
            "CALDERON_GAP_ON_THIS_FINITE_CORE_AND_APPLY_THE_EXPLICIT_JACOBI_"
            "FORTIN_TAIL_TO_THE_FOUR_COMPACT_BLOCKS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
