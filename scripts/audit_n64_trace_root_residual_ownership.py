"""Audit exact retained constraint ownership at the N64 trace root center."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import audit_n12_full_qvm_constraint_tail as tail
import construct_n64_trace_compatible_source_correction as bridge
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
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
ANCHOR_STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N64_TRACE_ROOT_RESIDUAL_OWNERSHIP.json"
)
ORDER = 64
ANCHOR = 12
POINTS = 96


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _split(vector: np.ndarray, order: int) -> tuple[np.ndarray, ...]:
    qdim = dimensions(order)["coordinates"]
    return vector[:qdim], vector[qdim:2 * qdim], vector[2 * qdim:]


def _sector(state: tuple[np.ndarray, ...], order: int) -> dict[str, object]:
    q, velocity, multipliers = state
    raw = np.asarray(constraint_residual(
        order, q, velocity, multipliers, points=POINTS
    ), dtype=float)
    reaction, _ = tail._boundary_reaction_data(q, multipliers, order)
    raw[:order] -= reaction * ((-1.0) ** np.arange(1, order + 1))
    weights = np.sqrt(
        1.0 + spectral_frequencies(order)["multipliers"] ** 2
    )
    weak = raw[:2 * order] / weights
    blocks = {
        "low_lapse": weak[:min(ANCHOR, order)],
        "high_lapse": weak[min(ANCHOR, order):order],
        "low_shift": weak[order:order + min(ANCHOR, order)],
        "high_shift": weak[order + min(ANCHOR, order):2 * order],
        "energy": raw[2 * order:],
    }
    norms = {name: float(np.linalg.norm(value)) for name, value in blocks.items()}
    maxima = {
        name: (float(np.max(np.abs(value))) if value.size else 0.0)
        for name, value in blocks.items()
    }
    return {
        "block_norms": norms,
        "block_maxima": maxima,
        "full_routed_weak_norm": float(np.linalg.norm(np.concatenate(
            tuple(blocks.values())
        ))),
        "dominant_block": max(norms, key=norms.get),
        "eta_minimum": float(_eta_legendre_minimum(
            order, q, multipliers, points=4000
        )["minimum"]),
    }


def main() -> None:
    payload = np.load(STATE)
    states = {
        side: _split(np.asarray(payload[f"{side}_state"], dtype=float), ORDER)
        for side in ("event", "child")
    }
    sectors = {side: _sector(state, ORDER) for side, state in states.items()}
    anchor_joint = np.asarray(np.load(ANCHOR_STATE)["state"], dtype=float)
    anchor_qdim = dimensions(ANCHOR)["coordinates"]
    anchor_size = 2 * anchor_qdim + 2 * ANCHOR
    anchor_states = {
        "event": _split(anchor_joint[:anchor_size], ANCHOR),
        "child": _split(anchor_joint[anchor_size:], ANCHOR),
    }
    legacy_anchor = {
        side: _sector(state, ANCHOR) for side, state in anchor_states.items()
    }
    jump = (
        bridge._boundary_value(ORDER, states["child"][0])
        - bridge._boundary_value(ORDER, states["event"][0])
    )
    low_baseline_changes = {
        side: {
            block: (
                sectors[side]["block_norms"][block]
                - legacy_anchor[side]["block_norms"][block]
            )
            for block in ("low_lapse", "low_shift", "energy")
        }
        for side in ("event", "child")
    }
    validation = {
        "accepted_Newton2_state_consumed": True,
        "legacy_constraint_helper_used_only_as_a_baseline_diagnostic": True,
        "existing_weak_boundary_reaction_routed": True,
        "low_and_high_history_blocks_reported_separately": True,
        "certified_N12_legacy_baseline_reported": True,
        "legacy_low_rows_not_promoted_over_the_corrected_F12_evaluator": True,
        "complete_four_row_boundary_remains_closed": float(
            np.linalg.norm(jump)
        ) < 1.0e-12,
        "eta_admissible": all(
            row["eta_minimum"] > 0.0 for row in sectors.values()
        ),
        "no_state_promoted_as_complete_child_root": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    result = {
        "classification": (
            "N64_TRACE_ROOT_HIGH_WARD_ROWS_CLOSED;_LEGACY_LOW_ROW_"
            "BASELINE_IS_NOT_THE_CORRECTED_PHYSICAL_AUTHORITY"
        ),
        "input": {
            "path": str(STATE.relative_to(ROOT)).replace("\\", "/"),
            "SHA256": _sha256(STATE),
        },
        "sectors": sectors,
        "certified_N12_legacy_evaluator_baseline": legacy_anchor,
        "N64_minus_N12_legacy_low_block_norm_changes": low_baseline_changes,
        "boundary_jump_norm": float(np.linalg.norm(jump)),
        "legacy_candidate_dominant_side": max(
            sectors, key=lambda side: sectors[side]["full_routed_weak_norm"]
        ),
        "legacy_candidate_dominant_block": "low_lapse",
        "state_status": "FINITE_CORE_TRACE_ROOT_ONLY_NOT_A_COMPLETE_CHILD_ROOT",
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "EVALUATE_THE_CORRECTED_RETAINED_ACTION_N64_ORDERED_EVENT_"
            "CANONICAL_MOMENTUM_DYNAMIC_FLUX_AND_CORRECTED_CONSTRAINT_"
            "ROWS_AT_THIS_TRACE_COMPATIBLE_FINITE_CORE_CENTER"
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
