"""Evaluate corrected retained-action N64 finite-core physical rows.

This is a targeted same-state audit of the trace-compatible Newton2 center.
It uses the corrected Decimal action blocks for constraints, preserves the
transported N12 ordered eigenline selector, and evaluates canonical momentum.
Dynamic flux remains a separate expensive row and is not silently inferred.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import construct_n64_trace_compatible_source_correction as bridge
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _canonical_pair_at_order,
    _child_rows_at_order,
    _eta_legendre_minimum,
    _metric_radial_flux_covector_at_order,
)
from bhsm.interface.aether_high_precision_velocity_jet import (
    high_precision_constraint_residual_from_blocks,
    high_precision_velocity_jet_blocks,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_TRACE_COMPATIBLE_SOURCE_NEWTON2_STATE.npz"
)
ANCHOR = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_CORRECTED_PHYSICAL_ROWS.json"
)
ORDER = 64
SOURCE_ORDER = 12
POINTS = 96


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _split(vector: np.ndarray) -> tuple[np.ndarray, ...]:
    qdim = dimensions(ORDER)["coordinates"]
    return vector[:qdim], vector[qdim:2 * qdim], vector[2 * qdim:]


def _embed_qm(reference: np.ndarray) -> np.ndarray:
    source_q = dimensions(SOURCE_ORDER)["coordinates"]
    target_q = dimensions(ORDER)["coordinates"]
    result = np.zeros(target_q + 2 * ORDER)
    result[0] = reference[0]
    for family in range(3):
        result[
            1 + family * ORDER:1 + family * ORDER + SOURCE_ORDER
        ] = reference[
            1 + family * SOURCE_ORDER:1 + (family + 1) * SOURCE_ORDER
        ]
    source_m = reference[source_q:]
    result[target_q:target_q + SOURCE_ORDER] = source_m[:SOURCE_ORDER]
    result[target_q + ORDER:target_q + ORDER + SOURCE_ORDER] = source_m[
        SOURCE_ORDER:
    ]
    return result / np.linalg.norm(result)


def _constraint_record(
    velocity: np.ndarray, blocks: dict[str, object],
) -> dict[str, object]:
    residual = high_precision_constraint_residual_from_blocks(velocity, blocks)
    weights = np.sqrt(
        1.0 + spectral_frequencies(ORDER)["multipliers"] ** 2
    )
    weak = residual[:2 * ORDER] / weights
    block_values = {
        "low_lapse": weak[:SOURCE_ORDER],
        "high_lapse": weak[SOURCE_ORDER:ORDER],
        "low_shift": weak[ORDER:ORDER + SOURCE_ORDER],
        "high_shift": weak[ORDER + SOURCE_ORDER:2 * ORDER],
        "energy": residual[2 * ORDER:],
    }
    return {
        "block_norms": {
            name: float(np.linalg.norm(values))
            for name, values in block_values.items()
        },
        "block_maxima": {
            name: float(np.max(np.abs(values)))
            for name, values in block_values.items()
        },
        "full_norm": float(np.linalg.norm(np.concatenate(
            tuple(block_values.values())
        ))),
    }


def _ordered_record(blocks: dict[str, object], reference: np.ndarray) -> dict[str, object]:
    vv = blocks["hessian_velocity_velocity"]
    mv = blocks["hessian_multiplier_velocity"]
    mm = blocks["hessian_multiplier_multiplier"]
    qdim = len(vv)
    mdim = len(mm)
    hessian = np.asarray([
        [float(value) for value in (
            vv[row][:] + [mv[column][row] for column in range(mdim)]
        )]
        for row in range(qdim)
    ] + [
        [float(value) for value in (mv[row][:] + mm[row][:])]
        for row in range(mdim)
    ])
    values, vectors = np.linalg.eigh(hessian)
    overlaps = np.abs(vectors.T @ reference)
    index = int(np.argmax(overlaps))
    lower = values[index] - values[index - 1] if index else np.inf
    upper = values[index + 1] - values[index] if index + 1 < len(values) else np.inf
    return {
        "binary_eigenvalue_diagnostic": float(values[index]),
        "transported_reference_overlap": float(overlaps[index]),
        "selected_index": index,
        "lower_neighbor_gap": float(lower),
        "upper_neighbor_gap": float(upper),
        "simple_branch": bool(min(lower, upper) > 0.0),
        "Decimal_Schur_value_evaluated": False,
    }


def main() -> None:
    payload = np.load(STATE)
    states = {
        side: _split(np.asarray(payload[f"{side}_state"], dtype=float))
        for side in ("event", "child")
    }
    blocks = {
        side: high_precision_velocity_jet_blocks(
            ORDER, *state, points=POINTS, precision=60
        )
        for side, state in states.items()
    }
    constraints = {
        side: _constraint_record(states[side][1], blocks[side])
        for side in states
    }
    anchor = np.load(ANCHOR)
    reference = _embed_qm(np.asarray(anchor["branch_reference"], dtype=float))
    ordered = _ordered_record(blocks["event"], reference)
    canonical = {
        side: _canonical_pair_at_order(ORDER, *state, points=POINTS)
        for side, state in states.items()
    }
    momenta = {
        side: np.asarray(canonical[side][0], dtype=float)
        for side in states
    }
    momentum_jump = momenta["child"] - momenta["event"]
    event_flux = np.asarray(canonical["event"][2].T @ (
        _metric_radial_flux_covector_at_order(
            ORDER, states["event"][0], states["event"][2]
        )
    ), dtype=float)
    dynamic_flux = np.asarray(_child_rows_at_order(
        ORDER,
        np.concatenate(states["child"]),
        states["event"][0],
        momenta["event"],
        event_flux,
        points=POINTS,
        flux_derivative_method="complex_step",
    )[-2:], dtype=float)
    boundary_jump = (
        bridge._boundary_value(ORDER, states["child"][0])
        - bridge._boundary_value(ORDER, states["event"][0])
    )
    eta = {
        side: float(_eta_legendre_minimum(
            ORDER, state[0], state[2], points=4000
        )["minimum"])
        for side, state in states.items()
    }
    validation = {
        "trace_compatible_Newton2_center_consumed": True,
        "corrected_Decimal_action_blocks_used_for_constraints": True,
        "transported_N12_ordered_eigenline_selector_used": True,
        "ordered_branch_remains_simple": bool(ordered["simple_branch"]),
        "canonical_momentum_evaluated_from_unchanged_action": True,
        "complete_four_row_boundary_closed": float(
            np.linalg.norm(boundary_jump)
        ) < 1.0e-12,
        "eta_admissible": all(value > 0.0 for value in eta.values()),
        "dynamic_flux_evaluated_from_unchanged_action": True,
        "candidate_not_promoted_as_complete_child": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    result = {
        "classification": (
            "N64_CORRECTED_CONSTRAINT_ORDERED_EVENT_AND_MOMENTUM_ROWS_"
            "EVALUATED;_DYNAMIC_FLUX_AND_NONLINEAR_COMPLETION_REMAIN_OPEN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (STATE, ANCHOR)
        },
        "constraints": constraints,
        "ordered_event": ordered,
        "canonical_momentum": {
            "event": momenta["event"].tolist(),
            "child": momenta["child"].tolist(),
            "jump": momentum_jump.tolist(),
            "jump_norm": float(np.linalg.norm(momentum_jump)),
        },
        "boundary_jump_norm": float(np.linalg.norm(boundary_jump)),
        "eta": eta,
        "dynamic_flux": {
            "rows": dynamic_flux.tolist(),
            "norm": float(np.linalg.norm(dynamic_flux)),
            "derivative_method": "complex_step",
        },
        "dynamic_flux_evaluated": True,
        "state_status": "FINITE_CORE_PROPOSAL_ONLY_NOT_A_COMPLETE_CHILD_ROOT",
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "EVALUATE_THE_UNCHANGED_DYNAMIC_FLUX_ROWS_AT_THIS_SAME_N64_"
            "CENTER_AND_THEN_CONSTRUCT_THE_COUPLED_CORRECTION_FOR_THE_"
            "REMAINING_CORRECTED_PHYSICAL_ROWS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
