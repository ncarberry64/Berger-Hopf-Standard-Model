"""Evaluate the N16 source correction with the unchanged complete-child map.

The input is the retained-action minimum-norm correction emitted by
``audit_n12_full_qvm_constraint_tail.py``.  It is a diagnostic proposal, never
an N16 root.  This audit deliberately restores the boundary, ordered-event,
energy, momentum, and eta owners that a constraint-only tail solve omits.
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
    _attachment_jacobian_at_order,
    _boundary_lift,
    _canonical_momentum_at_order_high_precision_real,
    _eta_legendre_minimum,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
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


ORDER = 16
SOURCE_ORDER = 12
POINTS = int(os.environ.get("BHSM_N16_POINTS", "96"))
SOURCE = Path(os.environ.get(
    "BHSM_N16_LINEAR_CANDIDATE",
    "artifacts/n16_coupled_momentum_response/"
    "BHSM_N16_FULL_QVM_LINEAR_SOURCE_CANDIDATE.npz",
))
N12 = Path(
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
RESULT = Path(os.environ.get(
    "BHSM_N16_COMPLETE_CHILD_AUDIT",
    ".tmp_n16_complete_child_candidate_audit.json",
))
COUPLED_CANDIDATE = Path(os.environ.get(
    "BHSM_N16_COUPLED_CANDIDATE",
    ".tmp_n16_coupled_momentum_candidate.npz",
))


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    return vectors @ np.diag(values**power) @ vectors.T


def _embed_qm(vector: np.ndarray) -> np.ndarray:
    old_q = 1 + 3 * SOURCE_ORDER
    new_q = 1 + 3 * ORDER
    result = np.zeros(new_q + 2 * ORDER)
    result[0] = vector[0]
    for family in range(3):
        result[1 + family * ORDER:1 + family * ORDER + SOURCE_ORDER] = (
            vector[
                1 + family * SOURCE_ORDER:
                1 + (family + 1) * SOURCE_ORDER
            ]
        )
    result[new_q:new_q + SOURCE_ORDER] = vector[
        old_q:old_q + SOURCE_ORDER
    ]
    result[new_q + ORDER:new_q + ORDER + SOURCE_ORDER] = vector[
        old_q + SOURCE_ORDER:old_q + 2 * SOURCE_ORDER
    ]
    return result


def _split(state: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    return state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]


def main() -> None:
    source = np.load(SOURCE)
    if int(source["order"]) != ORDER:
        raise ValueError("linear candidate is not N16")
    n12 = np.load(N12)
    reference = _embed_qm(np.asarray(n12["branch_reference"], dtype=float))
    reference /= np.linalg.norm(reference)

    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    trace = _trace_jacobian_at_order(ORDER)

    embedded_child_q = _split(np.asarray(source["child_embedded_state"]))[0]
    attachment = _attachment_jacobian_at_order(ORDER, embedded_child_q)
    boundary = np.vstack((trace, attachment[1]))
    boundary_inverse_sqrt = _symmetric_power(
        boundary @ np.diag(1.0 / q_weights**2) @ boundary.T,
        -0.5,
    )
    momentum_sqrt = _symmetric_power(attachment @ attachment.T, 0.5)

    event_embedded = np.asarray(source["event_embedded_state"], dtype=float)
    event_jet = exact_action_jet_at_state(
        ORDER, *_split(event_embedded), points=POINTS
    )
    event_values, event_vectors = np.linalg.eigh(event_jet.hessian)
    branch = int(np.argmax(np.abs(event_vectors.T @ reference)))
    branch_reference = event_vectors[:, branch]

    def selected_event(state: np.ndarray) -> tuple[float, float, float]:
        values, vectors = np.linalg.eigh(exact_action_jet_at_state(
            ORDER, *_split(state), points=POINTS
        ).hessian)
        index = int(np.argmax(np.abs(vectors.T @ branch_reference)))
        left = (
            float(values[index] - values[index - 1])
            if index else math.inf
        )
        right = (
            float(values[index + 1] - values[index])
            if index + 1 < values.size else math.inf
        )
        return float(values[index]), min(left, right), float(
            abs(vectors[:, index] @ branch_reference)
        )

    def physical_blocks(
        event: np.ndarray, child: np.ndarray,
    ) -> tuple[dict[str, np.ndarray], dict[str, float]]:
        eq, ev, em = _split(event)
        cq, cv, cm = _split(child)
        event_constraints = constraint_residual(
            ORDER, eq, ev, em, points=POINTS
        )
        child_constraints = constraint_residual(
            ORDER, cq, cv, cm, points=POINTS
        )
        boundary_raw = np.concatenate((
            trace @ (cq - eq),
            [
                _attachment_coordinates_at_order(ORDER, cq)[1]
                - _attachment_coordinates_at_order(ORDER, eq)[1]
            ],
        ))
        event_momentum = _canonical_momentum_at_order_high_precision_real(
            ORDER, eq, ev, em, points=POINTS
        )
        child_momentum = _canonical_momentum_at_order_high_precision_real(
            ORDER, cq, cv, cm, points=POINTS
        )
        momentum_raw = child_momentum - event_momentum
        blocks = {
            "event_constraint_weak": np.concatenate((
                event_constraints[:mdim] / m_weights,
                event_constraints[mdim:],
            )),
            "boundary_action": boundary_inverse_sqrt @ boundary_raw,
            "child_constraint_weak": np.concatenate((
                child_constraints[:mdim] / m_weights,
                child_constraints[mdim:],
            )),
            "momentum_action": momentum_sqrt @ momentum_raw,
        }
        concatenated_without_ordered_scaling = np.concatenate(tuple(
            blocks.values()
        ))
        event_eta = _eta_legendre_minimum(
            ORDER, eq, em, points=2000
        )["minimum"]
        child_eta = _eta_legendre_minimum(
            ORDER, cq, cm, points=2000
        )["minimum"]
        return blocks, {
            "event_minimum": float(event_eta),
            "child_minimum": float(child_eta),
            "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
        }

    def evaluate(event: np.ndarray, child: np.ndarray) -> dict[str, object]:
        blocks, eta = physical_blocks(event, child)
        event_value, event_gap, event_overlap = selected_event(event)
        reported_blocks = {
            "event_constraint_weak": blocks["event_constraint_weak"],
            "ordered_event_raw": np.asarray([event_value]),
            "boundary_action": blocks["boundary_action"],
            "child_constraint_weak": blocks["child_constraint_weak"],
            "momentum_action": blocks["momentum_action"],
        }
        concatenated_without_ordered_scaling = np.concatenate(tuple(
            reported_blocks.values()
        ))
        return {
            "block_norms": {
                name: float(np.linalg.norm(value))
                for name, value in reported_blocks.items()
            },
            "combined_action_weak_norm_with_raw_ordered_event": float(
                np.linalg.norm(concatenated_without_ordered_scaling)
            ),
            "maximum_absolute_row_with_raw_ordered_event": float(
                np.max(np.abs(concatenated_without_ordered_scaling))
            ),
            "ordered_event": {
                "raw_selected_eigenvalue": event_value,
                "neighbor_gap": event_gap,
                "overlap_with_injected_N12_eigenline": event_overlap,
            },
            "eta": eta,
        }

    embedded = evaluate(
        event_embedded,
        np.asarray(source["child_embedded_state"], dtype=float),
    )
    candidate = evaluate(
        np.asarray(source["event_candidate_state"], dtype=float),
        np.asarray(source["child_candidate_state"], dtype=float),
    )

    # Existing mixed Euler--Dirac proposal: solve the coupled constraint,
    # boundary, and momentum response in the action-coordinate normal metric.
    # The ordered-event row is independently reevaluated at every trial; its
    # third-action-variation slope is deliberately not approximated here.
    event_center = np.asarray(source["event_candidate_state"], dtype=float)
    child_center = np.asarray(source["child_candidate_state"], dtype=float)
    state_dim = event_center.size
    velocity_slice = slice(qdim, 2 * qdim)
    multiplier_slice = slice(2 * qdim, 2 * qdim + mdim)

    def constraint_jacobian(state: np.ndarray) -> tuple[np.ndarray, object]:
        jet = exact_full_action_jet_at_state(
            ORDER, *_split(state), points=POINTS
        )
        gradient = np.asarray(jet.gradient, dtype=float)
        hessian = np.asarray(jet.hessian, dtype=float)
        velocity = state[velocity_slice]
        energy = velocity @ hessian[velocity_slice, :] - gradient
        energy[velocity_slice] += gradient[velocity_slice]
        matrix = np.vstack((hessian[multiplier_slice, :], energy))
        matrix[:mdim] /= m_weights[:, None]
        return matrix, jet

    event_constraint_jacobian, event_center_jet = constraint_jacobian(
        event_center
    )
    child_constraint_jacobian, child_center_jet = constraint_jacobian(
        child_center
    )
    event_attachment = _attachment_jacobian_at_order(
        ORDER, event_center[:qdim]
    )
    child_attachment = _attachment_jacobian_at_order(
        ORDER, child_center[:qdim]
    )
    event_boundary = np.vstack((trace, event_attachment[1]))
    child_boundary = np.vstack((trace, child_attachment[1]))
    boundary_jacobian = np.zeros((4, 2 * state_dim))
    boundary_jacobian[:, :qdim] = -boundary_inverse_sqrt @ event_boundary
    boundary_jacobian[:, state_dim:state_dim + qdim] = (
        boundary_inverse_sqrt @ child_boundary
    )

    def frozen_momentum_jacobian(
        state: np.ndarray, jet: object, attachment_value: np.ndarray,
    ) -> np.ndarray:
        hessian = np.asarray(jet.hessian, dtype=float)
        lift = _boundary_lift(
            hessian[velocity_slice, velocity_slice],
            attachment_value,
            hessian[multiplier_slice, velocity_slice],
        )
        return momentum_sqrt @ lift.T @ hessian[velocity_slice, :]

    event_momentum_jacobian = frozen_momentum_jacobian(
        event_center, event_center_jet, event_attachment
    )
    child_momentum_jacobian = frozen_momentum_jacobian(
        child_center, child_center_jet, child_attachment
    )
    coupled_jacobian = np.block([
        [event_constraint_jacobian, np.zeros_like(event_constraint_jacobian)],
        [boundary_jacobian],
        [np.zeros_like(child_constraint_jacobian), child_constraint_jacobian],
        [-event_momentum_jacobian, child_momentum_jacobian],
    ])
    state_weights = np.concatenate((q_weights, np.ones(qdim), m_weights))
    joint_weights = np.concatenate((state_weights, state_weights))
    action_jacobian = coupled_jacobian / joint_weights[None, :]
    singular = np.linalg.svd(action_jacobian, compute_uv=False)
    tolerance = (
        np.finfo(float).eps * max(action_jacobian.shape) * singular[0]
    )
    rank = int(np.count_nonzero(singular > tolerance))

    def coupled_rows(event: np.ndarray, child: np.ndarray) -> np.ndarray:
        blocks, _ = physical_blocks(event, child)
        return np.concatenate((
            blocks["event_constraint_weak"],
            blocks["boundary_action"],
            blocks["child_constraint_weak"],
            blocks["momentum_action"],
        ))

    center_rows = coupled_rows(event_center, child_center)
    scaled_proposal = np.linalg.lstsq(
        action_jacobian, -center_rows, rcond=1.0e-12
    )[0]
    physical_proposal = scaled_proposal / joint_weights
    coupled_trials = []
    trial_states: list[tuple[np.ndarray, np.ndarray]] = []
    for exponent in range(13):
        factor = 2.0 ** (-exponent)
        trial = np.concatenate((event_center, child_center)) + (
            factor * physical_proposal
        )
        event_trial = trial[:state_dim]
        child_trial = trial[state_dim:]
        audit = evaluate(event_trial, child_trial)
        exact_rows = coupled_rows(event_trial, child_trial)
        predicted = center_rows + factor * (action_jacobian @ scaled_proposal)
        coupled_trials.append({
            "factor": factor,
            "increment_action_product_norm": float(
                factor * np.linalg.norm(scaled_proposal)
            ),
            "exact_coupled_norm_without_ordered_event": float(
                np.linalg.norm(exact_rows)
            ),
            "predicted_coupled_norm_without_ordered_event": float(
                np.linalg.norm(predicted)
            ),
            "flow_prediction_defect": float(
                np.linalg.norm(exact_rows - predicted)
                / max(np.linalg.norm(center_rows), np.finfo(float).tiny)
            ),
            "block_norms": audit["block_norms"],
            "ordered_event": audit["ordered_event"],
            "eta": audit["eta"],
        })
        trial_states.append((event_trial, child_trial))
    admissible_indices = [
        index for index, trial in enumerate(coupled_trials)
        if trial["eta"]["admissible"]
    ]
    best_index = min(
        admissible_indices,
        key=lambda index: coupled_trials[index][
            "exact_coupled_norm_without_ordered_event"
        ],
    )
    coupled_best = coupled_trials[best_index]
    best_event, best_child = trial_states[best_index]

    # Paired exact rank-one hard momentum response in the kernel of the
    # existing constraint/boundary rows.  This is the retained finite-N test
    # used at lower orders; the frozen lift selects the two-dimensional
    # proposal span, while paired exact full-map slopes determine orientation.
    hard_action_jacobian = action_jacobian[:-2]
    _, hard_singular, hard_right_t = np.linalg.svd(
        hard_action_jacobian, full_matrices=True
    )
    hard_tolerance = (
        np.finfo(float).eps
        * max(hard_action_jacobian.shape)
        * hard_singular[0]
    )
    hard_rank = int(np.count_nonzero(hard_singular > hard_tolerance))
    hard_kernel = hard_right_t[hard_rank:].T
    frozen_tangent_momentum = action_jacobian[-2:] @ hard_kernel
    tangent_basis = hard_kernel @ np.linalg.pinv(
        frozen_tangent_momentum, rcond=1.0e-12
    )
    for column in range(tangent_basis.shape[1]):
        tangent_basis[:, column] /= np.linalg.norm(tangent_basis[:, column])

    def exact_paired_jacobian(step: float) -> np.ndarray:
        matrix = np.empty((center_rows.size, 2))
        center = np.concatenate((event_center, child_center))
        for column in range(2):
            physical_direction = tangent_basis[:, column] / joint_weights
            plus = center + step * physical_direction
            minus = center - step * physical_direction
            matrix[:, column] = (
                coupled_rows(plus[:state_dim], plus[state_dim:])
                - coupled_rows(minus[:state_dim], minus[state_dim:])
            ) / (2.0 * step)
        return matrix

    paired_step = 2.0e-5
    paired_jacobian = exact_paired_jacobian(paired_step)
    paired_half_jacobian = exact_paired_jacobian(0.5 * paired_step)
    paired_richardson = (
        4.0 * paired_half_jacobian - paired_jacobian
    ) / 3.0
    paired_left, paired_singular, paired_right_t = np.linalg.svd(
        paired_jacobian, full_matrices=False
    )
    hard_source_projection = float(abs(paired_left[:, 0] @ center_rows))
    soft_source_projection = float(abs(paired_left[:, 1] @ center_rows))
    hard_coordinates = (
        -paired_right_t[0]
        * float(paired_left[:, 0] @ center_rows)
        / paired_singular[0]
    )
    hard_scaled_correction = tangent_basis @ hard_coordinates
    hard_trials = []
    hard_trial_states: list[tuple[np.ndarray, np.ndarray]] = []
    center_joint = np.concatenate((event_center, child_center))
    center_hard_norm = float(np.linalg.norm(center_rows[:-2]))
    for exponent in range(7):
        factor = 2.0 ** (-exponent)
        trial = center_joint + (
            factor * hard_scaled_correction / joint_weights
        )
        event_trial = trial[:state_dim]
        child_trial = trial[state_dim:]
        audit = evaluate(event_trial, child_trial)
        exact_rows = coupled_rows(event_trial, child_trial)
        hard_trials.append({
            "factor": factor,
            "increment_action_product_norm": float(
                factor * np.linalg.norm(hard_scaled_correction)
            ),
            "exact_full_weak_norm_without_ordered_event": float(
                np.linalg.norm(exact_rows)
            ),
            "exact_hard_constraint_boundary_norm": float(
                np.linalg.norm(exact_rows[:-2])
            ),
            "exact_momentum_norm": float(np.linalg.norm(exact_rows[-2:])),
            "block_norms": audit["block_norms"],
            "ordered_event": audit["ordered_event"],
            "eta": audit["eta"],
        })
        hard_trial_states.append((event_trial, child_trial))
    hard_admissible = [
        index for index, trial in enumerate(hard_trials)
        if trial["eta"]["admissible"]
    ]
    hard_best_index = min(
        hard_admissible,
        key=lambda index: hard_trials[index][
            "exact_full_weak_norm_without_ordered_event"
        ],
    )
    hard_best = hard_trials[hard_best_index]
    hard_best_event, hard_best_child = hard_trial_states[hard_best_index]
    hard_strict_reduction = bool(
        hard_best["exact_full_weak_norm_without_ordered_event"]
        < np.linalg.norm(center_rows)
    )
    if hard_strict_reduction:
        best_event, best_child = hard_best_event, hard_best_child
    COUPLED_CANDIDATE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        COUPLED_CANDIDATE,
        event_state=best_event,
        child_state=best_child,
        order=np.asarray(ORDER),
        factor=np.asarray(coupled_best["factor"]),
    )
    validation = {
        "unchanged_retained_N16_action_used": True,
        "all_existing_complete_child_owners_restored": True,
        "candidate_eta_admissible": candidate["eta"]["admissible"],
        "paired_exact_hard_momentum_response_reduces_full_weak_merit": (
            hard_strict_reduction
        ),
        "soft_channel_retained_as_dynamically_controlled_normal": True,
        "candidate_not_promoted_as_root": True,
        "no_new_equation_constraint_gate_scale_or_event_definition": True,
    }
    payload = {
        "classification": (
            "FINITE_N16_PAIRED_EXACT_HARD_MOMENTUM_RESPONSE_CLOSED;_"
            "SOFT_CHANNEL_REMAINS_A_DYNAMICALLY_CONTROLLED_NORMAL_"
            "DIRECTION;_DIAGNOSTIC_NOT_ROOT"
        ),
        "order": ORDER,
        "points": POINTS,
        "probe_kind": "LINEAR_SOURCE_CORRECTION_NOT_COMPLETE_CHILD_ROOT",
        "embedded_N12": embedded,
        "linear_candidate": candidate,
        "coupled_mixed_euler_dirac_momentum_proposal": {
            "proposal_only": True,
            "ordered_event_reevaluated_but_not_linearized": True,
            "action_coordinate_rows": int(action_jacobian.shape[0]),
            "joint_unknowns": int(action_jacobian.shape[1]),
            "normal_rank": rank,
            "smallest_singular_value": float(singular[rank - 1]),
            "largest_singular_value": float(singular[0]),
            "initial_exact_coupled_norm_without_ordered_event": float(
                np.linalg.norm(center_rows)
            ),
            "best_trial": coupled_best,
            "trials": coupled_trials,
            "strict_exact_merit_reduction": bool(
                coupled_best["exact_coupled_norm_without_ordered_event"]
                < np.linalg.norm(center_rows)
            ),
            "candidate_path": str(COUPLED_CANDIDATE),
        },
        "paired_exact_hard_momentum_response": {
            "classification": (
                "FINITE_N16_HARD_MOMENTUM_RESPONSE_CLOSED_SOFT_CHANNEL_"
                "REMAINS_DYNAMICALLY_CONTROLLED_NORMAL"
                if hard_strict_reduction else
                "FINITE_N16_HARD_MOMENTUM_RESPONSE_NOT_CLOSED"
            ),
            "proposal_only": True,
            "constraint_boundary_kernel_rank": hard_rank,
            "constraint_boundary_kernel_dimension": int(
                hard_kernel.shape[1]
            ),
            "paired_step": paired_step,
            "paired_singular_values": paired_singular.tolist(),
            "paired_half_singular_values": np.linalg.svd(
                paired_half_jacobian, compute_uv=False
            ).tolist(),
            "paired_Richardson_singular_values": np.linalg.svd(
                paired_richardson, compute_uv=False
            ).tolist(),
            "paired_scale_operator_difference": float(np.linalg.norm(
                paired_half_jacobian - paired_jacobian, ord=2
            )),
            "hard_source_projection": hard_source_projection,
            "soft_source_projection": soft_source_projection,
            "exact_full_weak_norm_before": float(np.linalg.norm(center_rows)),
            "exact_full_weak_norm_after": hard_best[
                "exact_full_weak_norm_without_ordered_event"
            ],
            "hard_constraint_boundary_norm_before": center_hard_norm,
            "hard_constraint_boundary_norm_after": hard_best[
                "exact_hard_constraint_boundary_norm"
            ],
            "eta_after": hard_best["eta"],
            "soft_channel": {
                "classification": (
                    "NORMAL_DIRECTION_CONTROLLED_BY_THE_EXISTING_POSITIVE_"
                    "DURATION_GAUGE_FIXED_JACOBI_EVOLUTION"
                ),
                "legitimate_child_manifold_tangent": False,
                "uniform_closed_range_failure_proved": False,
                "exact_response_projection_magnitude": float(
                    paired_singular[1]
                ),
                "source_projection_magnitude": soft_source_projection,
            },
            "best_trial": hard_best,
            "trials": hard_trials,
            "strict_exact_merit_reduction": hard_strict_reduction,
        },
        "interpretation": {
            "constraint_only_descent_is_a_complete_child_certificate": False,
            "raw_ordered_event_is_left_unscaled_to_avoid_a_new_numerical_"
            "normalization": True,
            "first_missing_constant_in_the_existing_continuum_radii_"
            "dependency": (
                "VALIDATED_SOURCE_RESTRICTED_POSITIVE_DURATION_SOFT_"
                "NORMAL_RIGHT_INVERSE_BOUND_K_FOR_THE_N12_TO_INFINITY_"
                "NONLINEAR_EVENT_CHILD_RADII_POLYNOMIAL"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "N16_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
