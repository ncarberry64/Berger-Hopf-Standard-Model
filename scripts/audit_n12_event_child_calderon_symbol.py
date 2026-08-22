"""Audit the existing N12 event--child Calderon boundary symbol.

The certified N12 event and child are the only physical states in this
calculation.  Their zero-padded higher-order images are diagnostic Galerkin
probes of the retained Hessian and weak reaction relation, never promoted as
complete-child roots.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
    _attachment_chart_curvature_on_velocity,
    _eta_legendre_minimum,
    _metric_radial_flux_covector_at_order,
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


SOURCE_ORDER = 12
POINTS = int(os.environ.get("BHSM_N12_CALDERON_POINTS", "96"))
ORDERS = tuple(int(item) for item in os.environ.get(
    "BHSM_N12_CALDERON_ORDERS", "12,16,20,24,32"
).split(","))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_high_precision_action_center.npz"
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    ".tmp_direct_n12_high_precision_complete_persistent_child_promotion.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_CALDERON_RESULT",
    ".tmp_direct_n12_high_precision_event_child_calderon_symbol.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _split(joint: np.ndarray, side: str) -> tuple[np.ndarray, ...]:
    qdim = dimensions(SOURCE_ORDER)["coordinates"]
    mdim = dimensions(SOURCE_ORDER)["multipliers"]
    state_dimension = 2 * qdim + mdim
    state = joint[:state_dimension] if side == "event" else joint[state_dimension:]
    return (
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
    )


def _symmetric_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    if float(np.min(values)) <= 0.0:
        raise np.linalg.LinAlgError("boundary trace Gram is not positive")
    return vectors @ np.diag(np.sqrt(values)) @ vectors.T


def _reaction_response(
    order: int,
    state: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, float]]]:
    def solve(boundary_acceleration: np.ndarray) -> dict[str, object]:
        q, velocity, multipliers = state
        qdim = dimensions(order)["coordinates"]
        mdim = dimensions(order)["multipliers"]
        boundary = _attachment_jacobian_at_order(order, q)
        curvature = _attachment_chart_curvature_on_velocity(
            order, q, velocity
        )
        jet = exact_full_action_jet_at_state(
            order, q, velocity, multipliers, points=POINTS
        )
        gradient = np.asarray(jet.gradient, dtype=float)
        hessian = np.asarray(jet.hessian, dtype=float)
        matrix = np.block([
            [
                hessian[qdim:2 * qdim, qdim:2 * qdim],
                hessian[qdim:2 * qdim, 2 * qdim:],
                -boundary.T,
            ],
            [
                hessian[2 * qdim:, qdim:2 * qdim],
                hessian[2 * qdim:, 2 * qdim:],
                np.zeros((mdim, 2)),
            ],
            [
                boundary,
                np.zeros((2, mdim)),
                np.zeros((2, 2)),
            ],
        ])
        radial_flux = _metric_radial_flux_covector_at_order(
            order, q, multipliers
        )
        right_hand_side = np.concatenate((
            gradient[:qdim]
            - hessian[qdim:2 * qdim, :qdim] @ velocity
            - radial_flux,
            -hessian[2 * qdim:, :qdim] @ velocity,
            np.asarray(boundary_acceleration, dtype=float) - curvature,
        ))
        # Existing boundary-compatible normal quotient: remove w-velocity
        # and shift-rate gauge-soft directions and retain
        # (scale,u,v,log-lapse,reaction).
        keep = np.concatenate((
            np.arange(0, 1 + order),
            np.arange(1 + 2 * order, 1 + 3 * order),
            qdim + np.arange(order),
            qdim + mdim + np.arange(2),
        ))
        reduced = matrix[np.ix_(keep, keep)]
        reduced_rhs = right_hand_side[keep]
        solved = np.linalg.solve(reduced, reduced_rhs)
        residual = reduced @ solved - reduced_rhs
        singular = np.linalg.svd(reduced, compute_uv=False)
        return {
            "boundary_reaction": solved[-2:],
            "smallest_singular_value": float(singular[-1]),
            "condition_number": float(singular[0] / singular[-1]),
            "maximum_reduced_residual": float(np.max(np.abs(residual))),
        }

    zero = solve(np.zeros(2))
    offset = np.asarray(zero["boundary_reaction"], dtype=float)
    response = np.empty((2, 2))
    solves = []
    for column in range(2):
        unit = np.zeros(2)
        unit[column] = 1.0
        solved = solve(unit)
        response[:, column] = (
            np.asarray(solved["boundary_reaction"], dtype=float) - offset
        )
        solves.append({
            "smallest_bordered_singular_value": float(
                solved["smallest_singular_value"]
            ),
            "condition_number": float(solved["condition_number"]),
            "maximum_reduced_residual": float(
                solved["maximum_reduced_residual"]
            ),
        })
    return offset, response, solves


def main() -> None:
    if not ORDERS or ORDERS[0] != SOURCE_ORDER:
        raise ValueError("the diagnostic order list must start at N12")
    if any(order < SOURCE_ORDER for order in ORDERS):
        raise ValueError("diagnostic orders may not be below N12")
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the certified N12 anchor is required")
    joint = np.asarray(np.load(CHECKPOINT)["state"], dtype=float)
    bases = {side: _split(joint, side) for side in ("event", "child")}
    rows = []
    previous = None
    for order in ORDERS:
        states = {
            side: (
                bases[side] if order == SOURCE_ORDER else
                embed_nested_state(*bases[side], SOURCE_ORDER, order)
            )
            for side in ("event", "child")
        }
        boundaries = {
            side: _attachment_jacobian_at_order(order, states[side][0])
            for side in states
        }
        frequencies = spectral_frequencies(order)["coordinates"]
        inverse_weight = np.diag(1.0 / (1.0 + frequencies**2))
        grams = {
            side: boundaries[side] @ inverse_weight @ boundaries[side].T
            for side in states
        }
        common_sqrt = _symmetric_sqrt(0.5 * (grams["event"] + grams["child"]))
        reactions = {
            side: _reaction_response(order, states[side])
            for side in states
        }
        normalized = {
            side: common_sqrt @ reactions[side][1] @ common_sqrt
            for side in states
        }
        frames = {}
        projectors = {}
        for side, sign in (("event", -1.0), ("child", 1.0)):
            frame, _ = np.linalg.qr(np.vstack((
                np.eye(2), sign * normalized[side],
            )))
            frames[side] = frame
            projectors[side] = frame @ frame.T
        cosines = np.linalg.svd(
            frames["child"].T @ frames["event"], compute_uv=False
        )
        cosines = np.clip(cosines, 0.0, 1.0)
        sines = np.sqrt(np.maximum(0.0, 1.0 - cosines**2))
        symbol = np.column_stack((frames["child"], -frames["event"]))
        symbol_singular = np.linalg.svd(symbol, compute_uv=False)
        pair_projector = np.block([
            [projectors["event"], np.zeros((4, 4))],
            [np.zeros((4, 4)), projectors["child"]],
        ])
        projector_step = (
            None if previous is None else
            float(np.linalg.norm(pair_projector - previous, ord=2))
        )
        previous = pair_projector
        rows.append({
            "N": order,
            "state_status": (
                "CERTIFIED_COMPLETE_PERSISTENT_EVENT_CHILD_PAIR"
                if order == SOURCE_ORDER else
                "ZERO_PADDED_N12_DIAGNOSTIC_PROBE_NOT_A_ROOT"
            ),
            "event_eta_minimum": float(_eta_legendre_minimum(
                order, states["event"][0], states["event"][2],
                points=max(2000, POINTS),
            )["minimum"]),
            "child_eta_minimum": float(_eta_legendre_minimum(
                order, states["child"][0], states["child"][2],
                points=max(2000, POINTS),
            )["minimum"]),
            "event_reaction_offset": reactions["event"][0].tolist(),
            "child_reaction_offset": reactions["child"][0].tolist(),
            "event_action_normalized_response": normalized["event"].tolist(),
            "child_action_normalized_response": normalized["child"].tolist(),
            "principal_cosines": cosines.tolist(),
            "principal_sines": sines.tolist(),
            "Friedrichs_sine": float(np.min(sines)),
            "four_by_four_symbol_singular_values": symbol_singular.tolist(),
            "minimum_graph_symbol_singular_value": float(symbol_singular[-1]),
            "seven_by_seven_symbol_gap": float(min(1.0, symbol_singular[-1])),
            "pair_projector_step_from_previous_probe": projector_step,
            "event_bordered_solves": reactions["event"][2],
            "child_bordered_solves": reactions["child"][2],
        })

    validation = {
        "certified_N12_anchor_consumed": True,
        "existing_action_Hessian_and_weak_reaction_relation_used": True,
        "existing_boundary_compatible_w_shift_gauge_quotient_used": True,
        "N12_boundary_symbol_full_rank": rows[0][
            "minimum_graph_symbol_singular_value"
        ] > 0.0,
        "all_bordered_probe_solves_resolved": all(
            solve["smallest_bordered_singular_value"] > 0.0
            and solve["maximum_reduced_residual"] < 1.0e-7
            for row in rows
            for side in ("event_bordered_solves", "child_bordered_solves")
            for solve in row[side]
        ),
        "all_probes_eta_admissible": all(
            row["event_eta_minimum"] > 0.0
            and row["child_eta_minimum"] > 0.0
            for row in rows
        ),
        "higher_order_injections_not_promoted_as_roots": all(
            row["state_status"] == "ZERO_PADDED_N12_DIAGNOSTIC_PROBE_NOT_A_ROOT"
            for row in rows[1:]
        ),
        "finite_probe_sequence_not_promoted_as_uniform_symbol_theorem": True,
        "no_new_equation_constraint_gate_scale_or_fit": True,
    }
    payload = {
        "classification": (
            "ACTUAL_N12_EVENT_CHILD_CALDERON_BOUNDARY_SYMBOL_MEASURED;_"
            "HIGHER_ORDER_INJECTED_SYMBOL_PROBES_RECORDED;_AN_EXPLICIT_"
            "INFINITE_TAIL_BOUND_IS_STILL_REQUIRED"
        ),
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "source_promotion": str(PROMOTION),
        "source_promotion_SHA256": _sha256(PROMOTION),
        "quadrature_points": POINTS,
        "orders": list(ORDERS),
        "symbol_definition": (
            "B7=I3_TRACE_DIRECT_SUM_[Q_child,-Q_(S_event)]_IN_THE_"
            "EXISTING_COMMON_ACTION_TRACE_GRAM"
        ),
        "rows": rows,
        "N12_minimum_seven_by_seven_symbol_gap": rows[0][
            "seven_by_seven_symbol_gap"
        ],
        "minimum_probe_symbol_gap": min(
            row["seven_by_seven_symbol_gap"] for row in rows
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "BOUND_THE_N12_TO_INFINITY_CHANGE_OF_THE_ACTION_NORMALIZED_"
            "EVENT_AND_CHILD_CALDERON_GRAPH_PROJECTORS_BY_THE_RETAINED_"
            "PRINCIPAL_PLUS_COMPACT_TAIL_AND_PROVE_IT_IS_SMALLER_THAN_"
            "THE_N12_SEVEN_BY_SEVEN_SYMBOL_GAP"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
