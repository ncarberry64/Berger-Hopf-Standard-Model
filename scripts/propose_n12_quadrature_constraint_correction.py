"""Propose a quadrature-consistent N12 correction in the existing v/m fiber."""

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
    _attachment_jacobian_at_order,
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
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = int(os.environ.get("BHSM_N12_CORRECTION_POINTS", "1024"))
ITERATIONS = int(os.environ.get("BHSM_N12_CORRECTION_ITERATIONS", "12"))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_CORRECTION_RESULT",
    ".tmp_direct_n12_quadrature_constraint_correction.json",
))
PROPOSAL = Path(os.environ.get(
    "BHSM_N12_CORRECTION_PROPOSAL",
    ".tmp_direct_n12_quadrature_corrected_proposal.npz",
))
ORDERED_SCALE = float(os.environ.get(
    "BHSM_N12_ORDERED_SCALE", "0.0004960628322343664"
))


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    return vectors @ np.diag(values**power) @ vectors.T


def _ordered(state: np.ndarray, reference: np.ndarray) -> float:
    qdim = dimensions(ORDER)["coordinates"]
    hessian = exact_action_jet_at_state(
        ORDER,
        state[:qdim], state[qdim:2 * qdim], state[2 * qdim:],
        points=POINTS,
    ).hessian
    values, vectors = np.linalg.eigh(np.asarray(hessian, dtype=float))
    return float(values[int(np.argmax(np.abs(vectors.T @ reference)))])


def _constraint_rows_and_jacobian(
    q: np.ndarray, velocity: np.ndarray, multipliers: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    jet = exact_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=POINTS
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    rows = np.concatenate((
        gradient[qdim:],
        [float(gradient[:qdim] @ velocity - jet.value)],
    ))
    energy_gradient = np.concatenate((
        velocity @ hessian[:qdim, :qdim],
        velocity @ hessian[:qdim, qdim:] - gradient[qdim:],
    ))
    jacobian = np.vstack((hessian[qdim:, :], energy_gradient))
    return rows, jacobian


def _project(state: np.ndarray) -> tuple[np.ndarray, list[dict[str, float]]]:
    qdim = dimensions(ORDER)["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    weights = np.concatenate((
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    q = state[:qdim].copy()
    z = state[qdim:].copy()
    history = []
    for iteration in range(ITERATIONS):
        rows, raw_jacobian = _constraint_rows_and_jacobian(
            q, z[:qdim], z[qdim:]
        )
        jacobian = raw_jacobian / weights[None, :]
        singular = np.linalg.svd(jacobian, compute_uv=False)
        correction_action = -jacobian.T @ np.linalg.solve(
            jacobian @ jacobian.T, rows
        )
        accepted = False
        factor = 1.0
        old_norm = float(np.linalg.norm(rows))
        for _ in range(20):
            candidate = z + factor * correction_action / weights
            candidate_rows = constraint_residual(
                ORDER, q, candidate[:qdim], candidate[qdim:], points=POINTS
            )
            if np.linalg.norm(candidate_rows) < old_norm:
                z = candidate
                accepted = True
                break
            factor *= 0.5
        history.append({
            "iteration": iteration,
            "constraint_norm_before": old_norm,
            "constraint_maximum_before": float(np.max(np.abs(rows))),
            "normal_sigma_min": float(singular[-1]),
            "action_correction_norm": float(np.linalg.norm(
                factor * correction_action
            )),
            "accepted_factor": factor if accepted else 0.0,
        })
        if not accepted or old_norm < 1.0e-12:
            break
    return np.concatenate((q, z)), history


def _normalized_rows(joint: np.ndarray, reference: np.ndarray) -> np.ndarray:
    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    sdim = 2 * qdim + mdim
    event = joint[:sdim]
    child = joint[sdim:]
    eq, ev, em = event[:qdim], event[qdim:2 * qdim], event[2 * qdim:]
    cq, cv, cm = child[:qdim], child[qdim:2 * qdim], child[2 * qdim:]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    trace = _trace_jacobian_at_order(ORDER)
    attachment = _attachment_jacobian_at_order(ORDER, cq)
    boundary = np.vstack((trace, attachment[1]))
    boundary_inverse_sqrt = _symmetric_power(
        boundary @ np.diag(1.0 / q_weights**2) @ boundary.T, -0.5
    )
    momentum_sqrt = _symmetric_power(attachment @ attachment.T, 0.5)
    event_constraints = constraint_residual(
        ORDER, eq, ev, em, points=POINTS
    )
    child_constraints = constraint_residual(
        ORDER, cq, cv, cm, points=POINTS
    )
    boundary_rows = np.concatenate((
        trace @ (cq - eq),
        [_attachment_coordinates_at_order(ORDER, cq)[1]
         - _attachment_coordinates_at_order(ORDER, eq)[1]],
    ))
    momentum = (
        _canonical_pair_at_order(ORDER, cq, cv, cm, points=POINTS)[0]
        - _canonical_pair_at_order(ORDER, eq, ev, em, points=POINTS)[0]
    )
    return np.concatenate((
        event_constraints[:mdim] / m_weights,
        event_constraints[mdim:],
        [_ordered(event, reference) / ORDERED_SCALE],
        boundary_inverse_sqrt @ boundary_rows,
        child_constraints[:mdim] / m_weights,
        child_constraints[mdim:],
        momentum_sqrt @ momentum,
    ))


def main() -> None:
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    reference /= np.linalg.norm(reference)
    qdim = dimensions(ORDER)["coordinates"]
    sdim = 2 * qdim + dimensions(ORDER)["multipliers"]
    before = _normalized_rows(joint, reference)
    event, event_history = _project(joint[:sdim])
    child, child_history = _project(joint[sdim:])
    proposed = np.concatenate((event, child))
    after = _normalized_rows(proposed, reference)
    event_eta = _eta_legendre_minimum(
        ORDER, event[:qdim], event[2 * qdim:], points=max(POINTS, 2000)
    )["minimum"]
    child_eta = _eta_legendre_minimum(
        ORDER, child[:qdim], child[2 * qdim:], points=max(POINTS, 2000)
    )["minimum"]
    accepted = bool(
        np.linalg.norm(after) < np.linalg.norm(before)
        and event_eta > 0.0 and child_eta > 0.0
    )
    if accepted:
        np.savez(
            PROPOSAL,
            state=proposed,
            n6_ordered_branch_index=checkpoint["n6_ordered_branch_index"],
            branch_reference=reference,
            soft_right_direction=checkpoint["soft_right_direction"],
            paired_j_full=checkpoint["paired_j_full"],
            paired_j_half=checkpoint["paired_j_half"],
            paired_jacobian=checkpoint["paired_jacobian"],
            recent_accepted_states=np.asarray([proposed]),
        )
    payload = {
        "classification": (
            "N12_QUADRATURE_CONSISTENT_CONSTRAINT_FIBER_PROPOSAL_ACCEPTED"
            if accepted else "N12_QUADRATURE_CONSTRAINT_PROPOSAL_REJECTED"
        ),
        "points": POINTS,
        "source_checkpoint": str(CHECKPOINT),
        "proposal_checkpoint": str(PROPOSAL) if accepted else None,
        "exact_normalized_full_residual_before": float(np.linalg.norm(before)),
        "exact_normalized_full_residual_after": float(np.linalg.norm(after)),
        "exact_normalized_full_maximum_after": float(np.max(np.abs(after))),
        "event_eta_minimum": event_eta,
        "child_eta_minimum": child_eta,
        "event_projection_history": event_history,
        "child_projection_history": child_history,
        "unchanged_57_row_map": True,
        "proposal_only": True,
        "new_physics_equation_constraint_gate_scale_or_fit": False,
        "accepted": accepted,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
