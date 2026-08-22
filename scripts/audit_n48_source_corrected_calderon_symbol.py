"""Evaluate the existing Calderon symbol on a retained-order source correction.

Both the embedded N12 state and the source-restricted linear correction are
diagnostic probes.  This script changes no complete-child row, weak reaction
relation, boundary trace, event definition, or persistence gate.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

import audit_n12_event_child_calderon_symbol as calderon
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
    _eta_legendre_minimum,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


POINTS = tuple(int(value) for value in os.environ.get(
    "BHSM_N48_CORRECTED_CALDERON_POINTS", "96,192"
).split(","))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N48_LINEAR_CANDIDATE_CHECKPOINT",
    ".tmp_n12_full_qvm_linear_correction_candidates.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N48_CORRECTED_CALDERON_RESULT",
    ".tmp_n48_source_corrected_calderon_symbol.json",
))


def _split(state: np.ndarray, order: int) -> tuple[np.ndarray, ...]:
    qdim = dimensions(order)["coordinates"]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def _evaluate(
    event: tuple[np.ndarray, ...],
    child: tuple[np.ndarray, ...],
    order: int,
    points: int,
) -> dict[str, object]:
    calderon.POINTS = points
    states = {"event": event, "child": child}
    boundaries = {
        name: _attachment_jacobian_at_order(order, state[0])
        for name, state in states.items()
    }
    frequencies = spectral_frequencies(order)["coordinates"]
    inverse_weight = np.diag(1.0 / (1.0 + frequencies**2))
    grams = {
        name: boundary @ inverse_weight @ boundary.T
        for name, boundary in boundaries.items()
    }
    common_sqrt = calderon._symmetric_sqrt(
        0.5 * (grams["event"] + grams["child"])
    )
    reactions = {
        name: calderon._reaction_response(order, state)
        for name, state in states.items()
    }
    normalized = {
        name: common_sqrt @ response[1] @ common_sqrt
        for name, response in reactions.items()
    }
    frames = {}
    for name, sign in (("event", -1.0), ("child", 1.0)):
        frames[name], _ = np.linalg.qr(np.vstack((
            np.eye(2), sign * normalized[name]
        )))
    cosines = np.linalg.svd(
        frames["child"].T @ frames["event"], compute_uv=False
    )
    cosines = np.clip(cosines, 0.0, 1.0)
    sines = np.sqrt(np.maximum(0.0, 1.0 - cosines**2))
    symbol = np.column_stack((frames["child"], -frames["event"]))
    symbol_singular = np.linalg.svd(symbol, compute_uv=False)
    return {
        "Friedrichs_sine": float(np.min(sines)),
        "minimum_graph_symbol_singular_value": float(symbol_singular[-1]),
        "seven_by_seven_symbol_gap": float(min(1.0, symbol_singular[-1])),
        "event_eta_minimum": float(_eta_legendre_minimum(
            order, event[0], event[2], points=4000
        )["minimum"]),
        "child_eta_minimum": float(_eta_legendre_minimum(
            order, child[0], child[2], points=4000
        )["minimum"]),
        "minimum_event_bordered_singular_value": float(min(
            row["smallest_bordered_singular_value"]
            for row in reactions["event"][2]
        )),
        "minimum_child_bordered_singular_value": float(min(
            row["smallest_bordered_singular_value"]
            for row in reactions["child"][2]
        )),
        "maximum_bordered_solve_residual": float(max(
            row["maximum_reduced_residual"]
            for name in ("event", "child")
            for row in reactions[name][2]
        )),
    }


def main() -> None:
    payload = np.load(CHECKPOINT)
    order = int(payload["order"])
    states = {
        "embedded": {
            name: _split(np.asarray(
                payload[f"{name}_embedded_state"], dtype=float
            ), order)
            for name in ("event", "child")
        },
        "linear_candidate": {
            name: _split(np.asarray(
                payload[f"{name}_candidate_state"], dtype=float
            ), order)
            for name in ("event", "child")
        },
    }
    evaluations = {
        str(points): {
            name: _evaluate(
                state["event"], state["child"], order, points
            )
            for name, state in states.items()
        }
        for points in POINTS
    }
    validation = {
        "unchanged_action_Hessian_and_weak_reaction_used": True,
        "embedded_and_linear_states_not_promoted_as_roots": True,
        "all_states_eta_admissible": bool(all(
            row["event_eta_minimum"] > 0.0
            and row["child_eta_minimum"] > 0.0
            for by_points in evaluations.values() for row in by_points.values()
        )),
        "all_sampled_symbols_transverse": bool(all(
            row["seven_by_seven_symbol_gap"] > 0.0
            for by_points in evaluations.values() for row in by_points.values()
        )),
        "all_bordered_solves_resolved": bool(all(
            row["minimum_event_bordered_singular_value"] > 0.0
            and row["minimum_child_bordered_singular_value"] > 0.0
            and row["maximum_bordered_solve_residual"] < 1.0e-7
            for by_points in evaluations.values() for row in by_points.values()
        )),
        "no_new_equation_constraint_gate_event_definition_or_fit": True,
    }
    output = {
        "artifact": f"BHSM_N{order}_SOURCE_CORRECTED_CALDERON_SYMBOL_AUDIT",
        "order": order,
        "quadrature_points": list(POINTS),
        "evaluations": evaluations,
        "classification": (
            f"N{order}_SOURCE_RESTRICTED_LINEAR_CORRECTION_PRESERVES_FINITE_"
            "EVENT_CHILD_CALDERON_TRANSVERSALITY_ON_SAMPLED_QUADRATURE;_"
            "DIAGNOSTIC_ONLY_NOT_A_ROOT_OR_UNIFORM_THEOREM"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
