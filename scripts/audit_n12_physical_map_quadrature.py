"""Reevaluate the unchanged raw N12 physical rows across Gauss orders."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _canonical_pair_at_order,
    _eta_legendre_minimum,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


ORDER = 12
POINT_COUNTS = tuple(int(item) for item in os.environ.get(
    "BHSM_N12_QUADRATURE_POINTS", "96,160,192,256,512"
).split(","))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    ".tmp_direct_n12_complete_persistent_child_promotion.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_QUADRATURE_AUDIT",
    ".tmp_direct_n12_physical_map_quadrature.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _ordered(state: np.ndarray, reference: np.ndarray,
             points: int) -> dict[str, float | int]:
    qdim = dimensions(ORDER)["coordinates"]
    jet = exact_action_jet_at_state(
        ORDER,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=points,
    )
    values, vectors = np.linalg.eigh(np.asarray(jet.hessian, dtype=float))
    overlaps = np.abs(vectors.T @ reference)
    selected = int(np.argmax(overlaps))
    lower = (
        float(values[selected] - values[selected - 1])
        if selected > 0 else float("inf")
    )
    upper = (
        float(values[selected + 1] - values[selected])
        if selected + 1 < values.size else float("inf")
    )
    return {
        "selected_index": selected,
        "raw_eigenvalue": float(values[selected]),
        "reference_overlap": float(overlaps[selected]),
        "minimum_neighbor_gap": min(lower, upper),
    }


def _raw_rows(joint: np.ndarray, reference: np.ndarray,
              points: int) -> tuple[np.ndarray, dict[str, object]]:
    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    sdim = 2 * qdim + mdim
    event = joint[:sdim]
    child = joint[sdim:]
    eq, ev, em = event[:qdim], event[qdim:2 * qdim], event[2 * qdim:]
    cq, cv, cm = child[:qdim], child[qdim:2 * qdim], child[2 * qdim:]
    ordered = _ordered(event, reference, points)
    event_constraints = constraint_residual(
        ORDER, eq, ev, em, points=points
    )
    boundary = np.concatenate((
        _trace_jacobian_at_order(ORDER) @ (cq - eq),
        [_attachment_coordinates_at_order(ORDER, cq)[1]
         - _attachment_coordinates_at_order(ORDER, eq)[1]],
    ))
    child_constraints = constraint_residual(
        ORDER, cq, cv, cm, points=points
    )
    event_momentum = _canonical_pair_at_order(
        ORDER, eq, ev, em, points=points
    )[0]
    child_momentum = _canonical_pair_at_order(
        ORDER, cq, cv, cm, points=points
    )[0]
    momentum = child_momentum - event_momentum
    rows = np.concatenate((
        event_constraints,
        [ordered["raw_eigenvalue"]],
        boundary,
        child_constraints,
        momentum,
    ))
    blocks = {
        "event_constraints": event_constraints,
        "ordered_event": np.asarray([ordered["raw_eigenvalue"]]),
        "boundary": boundary,
        "child_constraints": child_constraints,
        "momentum": momentum,
    }
    return rows, {
        "ordered_event": ordered,
        "block_norms": {
            name: float(np.linalg.norm(value))
            for name, value in blocks.items()
        },
        "block_maxima": {
            name: float(np.max(np.abs(value)))
            for name, value in blocks.items()
        },
        "raw_full_norm": float(np.linalg.norm(rows)),
        "raw_full_maximum": float(np.max(np.abs(rows))),
        "event_eta_minimum": _eta_legendre_minimum(
            ORDER, eq, em, points=max(points, 512)
        )["minimum"],
        "child_eta_minimum": _eta_legendre_minimum(
            ORDER, cq, cm, points=max(points, 512)
        )["minimum"],
    }


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the certified N12 anchor is required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    reference /= np.linalg.norm(reference)
    evaluations = {}
    vectors = {}
    for points in POINT_COUNTS:
        rows, record = _raw_rows(joint, reference, points)
        evaluations[str(points)] = record
        vectors[str(points)] = rows
    base = vectors[str(POINT_COUNTS[0])]
    differences = {
        str(points): {
            "raw_row_difference_norm_from_base": float(np.linalg.norm(
                vectors[str(points)] - base
            )),
            "raw_row_difference_maximum_from_base": float(np.max(np.abs(
                vectors[str(points)] - base
            ))),
        }
        for points in POINT_COUNTS[1:]
    }
    final = evaluations[str(POINT_COUNTS[-1])]
    # This is a numerical-certification tolerance, not a physical gate.  A
    # state with a 3e-4 residual is not made a root merely because two high
    # quadrature evaluations agree with one another.
    root_replay_tolerance = max(
        1.0e-10,
        10.0 * float(
            promotion["certified_root_ball"]["center_exact_F12_norm"]
        ),
    )
    quadrature_closed = bool(final["raw_full_norm"] <= root_replay_tolerance)
    validation = {
        "certified_binary64_center_reevaluated_unchanged": True,
        "all_57_raw_physical_rows_included": all(
            vector.size == 57 for vector in vectors.values()
        ),
        "ordered_branch_selected_by_stored_action_owned_reference": True,
        "eta_admissible_at_all_quadratures": all(
            row["event_eta_minimum"] > 0.0
            and row["child_eta_minimum"] > 0.0
            for row in evaluations.values()
        ),
        "higher_quadrature_root_closure_demonstrated": quadrature_closed,
        "new_equation_constraint_gate_scale_or_fit": False,
    }
    payload = {
        "classification": (
            "N12_LOW_ROW_GAUSS_QUADRATURE_CONSISTENCY_CLOSED"
            if quadrature_closed else
            "N12_96_POINT_ROOT_DOES_NOT_TRANSFER_DIRECTLY_TO_THE_"
            "HIGHER_QUADRATURE_RETAINED_MAP"
        ),
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "source_promotion": str(PROMOTION),
        "source_promotion_SHA256": _sha256(PROMOTION),
        "point_counts": POINT_COUNTS,
        "root_replay_numerical_tolerance_not_a_physical_gate": (
            root_replay_tolerance
        ),
        "evaluations": evaluations,
        "differences_from_first_quadrature": differences,
        "scope": {
            "N12_96_point_finite_map_certificate_revoked": False,
            "same_state_is_a_higher_quadrature_root": quadrature_closed,
            "higher_quadrature_state_promoted_as_complete_child": False,
            "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        },
        "exact_next_dependency": (
            "INCLUDE_THE_EXISTING_GAUSS_QUADRATURE_CONSISTENCY_DEFECT_"
            "IN_THE_COUPLED_EVENT_CHILD_SHELL_NEWTON_RADII_MAP"
            if not quadrature_closed else
            "CLOSE_THE_REMAINING_INFINITE_HIGH_SHELL_NORMAL_SCHUR_BLOCKS"
        ),
        "validation": validation,
        "validation_passed": all(
            value for key, value in validation.items()
            if key != "new_equation_constraint_gate_scale_or_fit"
        ) and validation["new_equation_constraint_gate_scale_or_fit"] is False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
