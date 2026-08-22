"""Measure the unchanged N6-to-N12 joint weak Schur/chord bridge.

The paired slopes and chord/Broyden updates are proposal machinery only.
Promotion remains controlled by the exact retained joint weak residual, and
the emitted artifact stays fail-closed unless every nonlinear radii and
existing physical-neighborhood certificate is actually present.
"""

import hashlib
import json
import os
import time
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np


START_WALL_CLOCK = time.perf_counter()

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _attachment_jacobian_at_order,
    _authoritative_n6_event_child_anchor,
    _canonical_momentum_at_order_high_precision_real,
    _canonical_pair_at_order,
    _exact_full_jet_euler_dirac_acceleration,
    _eta_legendre_minimum,
    _project_constraints_action_energy,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_high_precision_velocity_jet import (
    high_precision_canonical_momentum_from_blocks,
    high_precision_constraint_residual_from_blocks,
    high_precision_ordered_eigenpair_from_blocks,
    high_precision_velocity_jet_blocks,
)


PATH = Path("artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json")
SEED_ARTIFACT = Path(
    "artifacts/BHSM_N6_N12_JOINT_SCHUR_CHORD_COVER.json"
)
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_joint_schur_n12_state.npz"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_RESULT", ".tmp_joint_schur_result.json"
))
ARTIFACT = Path(os.environ.get(
    "BHSM_N12_ARTIFACT", str(SEED_ARTIFACT)
))
CURVED_PATH_LEDGER = Path(os.environ.get(
    "BHSM_N12_CURVED_PATH_LEDGER",
    ".tmp_direct_n12_curved_path.json",
))
ORDER = 12
LOW = 6
POINTS = int(os.environ.get("BHSM_N12_POINTS", "96"))
STEPS = (2.0e-5, 1.0e-5)
PROPOSAL_STEPS = int(os.environ.get("BHSM_CHORD_PROPOSAL_STEPS", "0"))
if not 0 <= PROPOSAL_STEPS <= 96:
    raise ValueError("BHSM_CHORD_PROPOSAL_STEPS must lie in [0,96]")
PROPOSAL_MODE = os.environ.get("BHSM_N12_PROPOSAL_MODE", "chord")
if PROPOSAL_MODE not in {"chord", "normal_lm"}:
    raise ValueError("BHSM_N12_PROPOSAL_MODE must be chord or normal_lm")
PROFILE_JACOBIAN_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_PROFILE_JACOBIAN_DIAGNOSTIC", "0"
) == "1"
CURVED_SOFT_2D_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_CURVED_SOFT_2D_DIAGNOSTIC", "0"
) == "1"
SOFT_SUBSPACE_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_SOFT_SUBSPACE_DIAGNOSTIC", "0"
) == "1"
CONTINUOUS_NEWTON_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_CONTINUOUS_NEWTON_DIAGNOSTIC", "0"
) == "1"
CENTER_ONLY_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_CENTER_ONLY_DIAGNOSTIC", "0"
) == "1"
REFRESH_CENTER_CHECKPOINT = os.environ.get(
    "BHSM_N12_REFRESH_CENTER_CHECKPOINT", "0"
) == "1"
RESIDUAL_ONLY_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_RESIDUAL_ONLY_DIAGNOSTIC", "0"
) == "1"
SHELL_DECOMPOSITION_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_SHELL_DECOMPOSITION_DIAGNOSTIC", "0"
) == "1"
EVENT_FIBER_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_EVENT_FIBER_DIAGNOSTIC", "0"
) == "1"
ORDERED_EVENT_PROFILE_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_ORDERED_EVENT_PROFILE_DIAGNOSTIC", "0"
) == "1"
STRUCTURED_SHAKE_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_STRUCTURED_SHAKE_DIAGNOSTIC", "0"
) == "1"
CONSTRAINT_OWNER_KERNEL_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_CONSTRAINT_OWNER_KERNEL_DIAGNOSTIC", "0"
) == "1"
RADII_GATE_DIAGNOSTIC = os.environ.get(
    "BHSM_N12_RADII_GATE_DIAGNOSTIC", "0"
) == "1"
STABLE_ORDERED_EVENT_EIGENVALUE = os.environ.get(
    "BHSM_N12_STABLE_ORDERED_EVENT_EIGENVALUE", "0"
) == "1"
STABLE_CANONICAL_MOMENTUM = os.environ.get(
    "BHSM_N12_STABLE_CANONICAL_MOMENTUM", "1"
) == "1"
HIGH_PRECISION_ACTION_JET = os.environ.get(
    "BHSM_N12_HIGH_PRECISION_ACTION_JET", "1"
) == "1"
IGNORE_CACHED_JACOBIAN = os.environ.get(
    "BHSM_N12_IGNORE_CACHED_JACOBIAN", "0"
) == "1"
ORDERED_EVENT_EIGENVALUE_EVALUATION = (
    "SELECTED_EIGENLINE_DECIMAL_SCHUR_OF_DECIMAL_RETAINED_ACTION_HESSIAN"
    if HIGH_PRECISION_ACTION_JET else
    "SELECTED_EIGENLINE_DECIMAL_SCHUR_REFINEMENT_OF_BINARY64_HESSIAN"
    if STABLE_ORDERED_EVENT_EIGENVALUE else
    "BINARY64_SYMMETRIC_EIGENSOLVER"
)
CANONICAL_MOMENTUM_EVALUATION = (
    "DECIMAL_RETAINED_ACTION_JET_AND_HESSIAN_MINIMAL_REAL_LIFT"
    if HIGH_PRECISION_ACTION_JET else
    "DECIMAL80_HESSIAN_MINIMAL_REAL_LIFT_SOLVES"
    if STABLE_CANONICAL_MOMENTUM else
    "BINARY64_HESSIAN_MINIMAL_REAL_LIFT_SOLVES"
)
EVENT_FIBER_PROPOSAL_CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_EVENT_FIBER_PROPOSAL_CHECKPOINT",
    ".tmp_direct_n12_corrected_event_fiber_proposal.npz",
))
PROFILE_PROPOSAL_CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_PROFILE_PROPOSAL_CHECKPOINT",
    ".tmp_direct_n12_soft_profile_proposal.npz",
))
SHAKE_HISTORICAL_CENTER = Path(os.environ.get(
    "BHSM_N12_SHAKE_HISTORICAL_CENTER",
    ".tmp_direct_n12_exact_identity_normal_jacobian_1e20.npz",
))


def decode(exact):
    return tuple(
        np.asarray([float.fromhex(value) for value in exact[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )


def embed_q(value, source, target):
    result = np.zeros(1 + 3 * target)
    result[0] = value[0]
    for family in range(3):
        result[1 + family * target:1 + family * target + source] = value[
            1 + family * source:1 + (family + 1) * source
        ]
    return result


def embed_qm(value, source, target):
    q_source = 1 + 3 * source
    q_target = 1 + 3 * target
    result = np.zeros(q_target + 2 * target)
    result[:q_target] = embed_q(value[:q_source], source, target)
    result[q_target:q_target + source] = value[q_source:q_source + source]
    result[q_target + target:q_target + target + source] = value[
        q_source + source:q_source + 2 * source
    ]
    return result


payload = json.loads(PATH.read_text(encoding="utf-8"))["cross_resolution_reconnaissance"]
anchor = _authoritative_n6_event_child_anchor(payload)
event6 = decode(anchor["event_exact"])
child6 = decode(anchor["child_exact"])
event = embed_nested_state(*event6, 6, ORDER)
child = embed_nested_state(*child6, 6, ORDER)
qdim = dimensions(ORDER)["coordinates"]
mdim = dimensions(ORDER)["multipliers"]
sdim = 2 * qdim + mdim
freq = spectral_frequencies(ORDER)
q_weights = np.sqrt(1.0 + freq["coordinates"] ** 2)
m_weights = np.sqrt(1.0 + freq["multipliers"] ** 2)
state_weights = np.concatenate((q_weights, np.ones(qdim), m_weights))
joint_weights = np.concatenate((state_weights, state_weights))
trace = _trace_jacobian_at_order(ORDER)
attachment = _attachment_jacobian_at_order(ORDER, child[0])
boundary = np.vstack((trace, attachment[1]))


def symmetric_power(matrix, power):
    values, vectors = np.linalg.eigh(matrix)
    return vectors @ np.diag(values**power) @ vectors.T


boundary_inverse_sqrt = symmetric_power(
    boundary @ np.diag(1.0 / q_weights**2) @ boundary.T, -0.5
)
momentum_sqrt = symmetric_power(attachment @ attachment.T, 0.5)

n6_jet = exact_action_jet_at_state(6, *event6, points=POINTS)
n6_values, n6_vectors = np.linalg.eigh(n6_jet.hessian)
# The repaired event record owns the continued ordered eigenline.  At the
# root its eigenvalue is zero up to quadrature/roundoff, so recomputing the
# index from ``count(values < 0)`` can jump to the adjacent eigenline when the
# last bit changes sign.  Preserve the already-validated branch selector.
n6_event_record = payload.get("N6_coherent_ordered_event_repair_audit")
if not (
    anchor.get("ordered_event_validated") is True
    and isinstance(n6_event_record, dict)
    and n6_event_record.get("validation_passed") is True
    and "branch_index" in n6_event_record
):
    raise RuntimeError(
        "direct N12 continuation requires the validated repaired N6 "
        "ordered-event branch record"
    )
n6_branch = int(n6_event_record["branch_index"])
if not 0 <= n6_branch < n6_values.size:
    raise RuntimeError("stored N6 ordered-event branch index is out of range")
embedded_reference = embed_qm(n6_vectors[:, n6_branch], 6, ORDER)
embedded_reference /= np.linalg.norm(embedded_reference)
center_event_jet = exact_action_jet_at_state(ORDER, *event, points=POINTS)
center_values, center_vectors = np.linalg.eigh(center_event_jet.hessian)
center_branch = int(np.argmax(np.abs(center_vectors.T @ embedded_reference)))
branch_reference = center_vectors[:, center_branch]


def _selected_ordered_eigenpair(state):
    q, v, m = state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]
    hessian = np.asarray(
        exact_action_jet_at_state(
            ORDER, q, v, m, points=POINTS
        ).hessian,
        dtype=float,
    )
    values, vectors = np.linalg.eigh(hessian)
    index = int(np.argmax(np.abs(vectors.T @ branch_reference)))
    return hessian, float(values[index]), vectors[:, index]


def _decimal_linear_solve(matrix, right_hand_side):
    """Solve one small dense system in Decimal arithmetic with pivoting."""

    coefficients = [row[:] for row in matrix]
    rhs = right_hand_side[:]
    size = len(rhs)
    for column in range(size):
        pivot = max(
            range(column, size),
            key=lambda row: abs(coefficients[row][column]),
        )
        if pivot != column:
            coefficients[column], coefficients[pivot] = (
                coefficients[pivot], coefficients[column]
            )
            rhs[column], rhs[pivot] = rhs[pivot], rhs[column]
        diagonal = coefficients[column][column]
        if diagonal == 0:
            raise np.linalg.LinAlgError(
                "singular complement in ordered-event eigenvalue refinement"
            )
        for row in range(column + 1, size):
            factor = coefficients[row][column] / diagonal
            if factor == 0:
                continue
            coefficients[row][column] = Decimal(0)
            for inner in range(column + 1, size):
                coefficients[row][inner] -= (
                    factor * coefficients[column][inner]
                )
            rhs[row] -= factor * rhs[column]
    solution = [Decimal(0)] * size
    for row in range(size - 1, -1, -1):
        remainder = rhs[row] - sum(
            coefficients[row][column] * solution[column]
            for column in range(row + 1, size)
        )
        solution[row] = remainder / coefficients[row][row]
    return solution


def _refined_selected_ordered_eigenvalue(hessian, estimate, vector):
    """Refine the same simple eigenline without changing its selector.

    Near the N12 root the selected eigenvalue is far below
    ``eps * ||H||`` even though its neighboring spectral gap stays open.
    The eigensolver still owns the branch/eigenline; a high-precision scalar
    Schur complement only evaluates that already-selected eigenvalue.
    """

    pivot = int(np.argmax(np.abs(vector)))
    retained = [index for index in range(hessian.shape[0]) if index != pivot]
    with localcontext() as context:
        context.prec = 80
        diagonal = Decimal.from_float(float(hessian[pivot, pivot]))
        coupling = [
            Decimal.from_float(float(hessian[index, pivot]))
            for index in retained
        ]
        complement = [[
            Decimal.from_float(float(hessian[row, column]))
            for column in retained
        ] for row in retained]
        eigenvalue = Decimal.from_float(float(estimate))
        for _ in range(4):
            shifted = [[
                complement[row][column]
                - (eigenvalue if row == column else Decimal(0))
                for column in range(len(retained))
            ] for row in range(len(retained))]
            inverse_coupling = _decimal_linear_solve(
                shifted, coupling
            )
            value = (
                diagonal
                - eigenvalue
                - sum(
                    left * right
                    for left, right in zip(coupling, inverse_coupling)
                )
            )
            derivative = -Decimal(1) - sum(
                entry * entry for entry in inverse_coupling
            )
            correction = value / derivative
            eigenvalue -= correction
            if abs(correction) < Decimal("1e-60"):
                break
        return float(eigenvalue)


def ordered_lambda(state, blocks=None):
    if HIGH_PRECISION_ACTION_JET:
        if blocks is None:
            q, v, m = (
                state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]
            )
            blocks = high_precision_velocity_jet_blocks(
                ORDER, q, v, m, points=POINTS, precision=60,
            )
        return float(high_precision_ordered_eigenpair_from_blocks(
            blocks, branch_reference, precision=60,
        )["eigenvalue"])
    hessian, estimate, vector = _selected_ordered_eigenpair(state)
    if not STABLE_ORDERED_EVENT_EIGENVALUE:
        return estimate
    return _refined_selected_ordered_eigenvalue(
        hessian, estimate, vector
    )


base_center = np.concatenate((*event, *child))

# Normalize the retained ordered-event scalar by its own action-coordinate dual norm.
ordered_gradient = np.empty(sdim)
ordered_step = STEPS[1]
for column in range(sdim):
    delta = np.zeros(sdim)
    delta[column] = ordered_step / state_weights[column]
    ordered_gradient[column] = (
        _selected_ordered_eigenpair(base_center[:sdim] + delta)[1]
        - _selected_ordered_eigenpair(base_center[:sdim] - delta)[1]
    ) / (2.0 * ordered_step)
ordered_scale = float(np.linalg.norm(ordered_gradient))


def rows(joint):
    event_state = joint[:sdim]
    child_state = joint[sdim:]
    eq, ev, em = event_state[:qdim], event_state[qdim:2 * qdim], event_state[2 * qdim:]
    cq, cv, cm = child_state[:qdim], child_state[qdim:2 * qdim], child_state[2 * qdim:]
    event_blocks = None
    child_blocks = None
    if HIGH_PRECISION_ACTION_JET:
        event_blocks = high_precision_velocity_jet_blocks(
            ORDER, eq, ev, em, points=POINTS, precision=60,
        )
        child_blocks = high_precision_velocity_jet_blocks(
            ORDER, cq, cv, cm, points=POINTS, precision=60,
        )
        e_constraints = high_precision_constraint_residual_from_blocks(
            ev, event_blocks,
        )
        c_constraints = high_precision_constraint_residual_from_blocks(
            cv, child_blocks,
        )
    else:
        e_constraints = constraint_residual(
            ORDER, eq, ev, em, points=POINTS,
        )
        c_constraints = constraint_residual(
            ORDER, cq, cv, cm, points=POINTS,
        )
    e_rows = np.concatenate((
        e_constraints[:mdim] / m_weights,
        e_constraints[mdim:],
        [ordered_lambda(event_state, event_blocks) / ordered_scale],
    ))
    boundary_rows = np.concatenate((
        trace @ (cq - eq),
        [_attachment_coordinates_at_order(ORDER, cq)[1]
         - _attachment_coordinates_at_order(ORDER, eq)[1]],
    ))
    if HIGH_PRECISION_ACTION_JET:
        momentum = (
            high_precision_canonical_momentum_from_blocks(
                ORDER, cq, child_blocks, precision=60,
            )
            - high_precision_canonical_momentum_from_blocks(
                ORDER, eq, event_blocks, precision=60,
            )
        )
    elif STABLE_CANONICAL_MOMENTUM:
        momentum = (
            _canonical_momentum_at_order_high_precision_real(
                ORDER, cq, cv, cm, points=POINTS
            )
            - _canonical_momentum_at_order_high_precision_real(
                ORDER, eq, ev, em, points=POINTS
            )
        )
    else:
        momentum = (
            _canonical_pair_at_order(ORDER, cq, cv, cm, points=POINTS)[0]
            - _canonical_pair_at_order(ORDER, eq, ev, em, points=POINTS)[0]
        )
    c_rows = np.concatenate((
        boundary_inverse_sqrt @ boundary_rows,
        c_constraints[:mdim] / m_weights,
        c_constraints[mdim:],
        momentum_sqrt @ momentum,
    ))
    return np.concatenate((e_rows, c_rows))


previous_soft_right = None
curved_previous_soft_right = None
cached_j_full = None
cached_j_half = None
cached_j = None
recent_accepted_states = None
continuous_newton_solver_time = 0.0
continuous_newton_dt = float(os.environ.get(
    "BHSM_N12_CONTINUOUS_NEWTON_INITIAL_DT", str(1.0 / 1024.0)
))
if CHECKPOINT.exists():
    checkpoint_payload = np.load(CHECKPOINT)
    center = np.asarray(checkpoint_payload["state"], dtype=float)
    if "branch_reference" in checkpoint_payload.files:
        if "n6_ordered_branch_index" not in checkpoint_payload.files:
            raise RuntimeError(
                "checkpoint branch provenance predates the corrected "
                "action-owned N6 ordered-event selector"
            )
        if int(checkpoint_payload["n6_ordered_branch_index"]) != n6_branch:
            raise RuntimeError(
                "checkpoint transports a different N6 ordered-event branch"
            )
        branch_reference = np.asarray(
            checkpoint_payload["branch_reference"], dtype=float
        )
    if "soft_right_direction" in checkpoint_payload.files:
        previous_soft_right = np.asarray(
            checkpoint_payload["soft_right_direction"], dtype=float
        )
    if "curved_previous_soft_right_direction" in checkpoint_payload.files:
        curved_previous_soft_right = np.asarray(
            checkpoint_payload["curved_previous_soft_right_direction"],
            dtype=float,
        )
    if not IGNORE_CACHED_JACOBIAN and all(
        name in checkpoint_payload.files
        for name in ("paired_j_full", "paired_j_half", "paired_jacobian")
    ):
        cached_j_full = np.asarray(checkpoint_payload["paired_j_full"])
        cached_j_half = np.asarray(checkpoint_payload["paired_j_half"])
        cached_j = np.asarray(checkpoint_payload["paired_jacobian"])
    if "recent_accepted_states" in checkpoint_payload.files:
        recent_accepted_states = np.asarray(
            checkpoint_payload["recent_accepted_states"], dtype=float
        )
    if "continuous_newton_solver_time" in checkpoint_payload.files:
        continuous_newton_solver_time = float(
            checkpoint_payload["continuous_newton_solver_time"]
        )
    if "continuous_newton_dt" in checkpoint_payload.files:
        continuous_newton_dt = float(checkpoint_payload["continuous_newton_dt"])
    center_source = "REFRESHED_FROM_PREVIOUS_EXACT_DESCENT_CHECKPOINT"
elif SEED_ARTIFACT.exists():
    durable = json.loads(SEED_ARTIFACT.read_text(encoding="utf-8"))
    exact_center = durable["latest_checkpoint_binary64_hex"]
    center = np.concatenate((
        np.asarray([float.fromhex(value) for value in exact_center["event"]]),
        np.asarray([float.fromhex(value) for value in exact_center["child"]]),
    ))
    branch_reference = np.asarray([
        float.fromhex(value)
        for value in exact_center["transported_ordered_event_eigenline"]
    ])
    center_source = "RESTORED_FROM_DURABLE_BINARY64_ARTIFACT"
else:
    center = base_center.copy()
    center_source = "ZERO_PADDED_REPAIRED_N6_ANCHOR"
if recent_accepted_states is None:
    recent_accepted_states = center[None, :]

# Transport the already-selected ordered event eigenline to the accepted
# chord center before taking its local paired slopes.  Comparing every local
# perturbation directly with the original zero-padded N6 vector can swap two
# nearby eigenlines after a long accepted chord even though the continued
# physical branch itself remains simple.
center_event_state = center[:sdim]
center_eq = center_event_state[:qdim]
center_ev = center_event_state[qdim:2 * qdim]
center_em = center_event_state[2 * qdim:]
transport_values, transport_vectors = np.linalg.eigh(
    exact_action_jet_at_state(
        ORDER, center_eq, center_ev, center_em, points=POINTS
    ).hessian
)
transport_branch = int(np.argmax(np.abs(
    transport_vectors.T @ branch_reference
)))
branch_reference = transport_vectors[:, transport_branch]
transport_neighbor_gap = min(
    float(transport_values[transport_branch] - transport_values[transport_branch - 1])
    if transport_branch > 0 else np.inf,
    float(transport_values[transport_branch + 1] - transport_values[transport_branch])
    if transport_branch + 1 < transport_values.size else np.inf,
)
center_rows = rows(center)

if RESIDUAL_ONLY_DIAGNOSTIC:
    event_eta = _eta_legendre_minimum(
        ORDER, center[:qdim], center[2 * qdim:sdim], points=2000
    )["minimum"]
    child_eta = _eta_legendre_minimum(
        ORDER,
        center[sdim:sdim + qdim],
        center[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    residual_payload = {
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
        "ordered_event_eigenvalue_evaluation": (
            ORDERED_EVENT_EIGENVALUE_EVALUATION
        ),
        "canonical_momentum_evaluation": CANONICAL_MOMENTUM_EVALUATION,
        "ordered_scale": ordered_scale,
        "method": "UNCHANGED_EXACT_F12_RESIDUAL_ONLY",
        "exact_full_residual": float(np.linalg.norm(center_rows)),
        "exact_residual_vector": center_rows.tolist(),
        "event_block_norm": float(np.linalg.norm(center_rows[:2 * ORDER + 2])),
        "child_block_norm": float(np.linalg.norm(center_rows[2 * ORDER + 2:])),
        "event_eta": float(event_eta),
        "child_eta": float(child_eta),
        "checkpoint_modified": False,
        "unchanged_exact_F12": True,
        "new_physics_or_gate": False,
    }
    RESULT.write_text(
        json.dumps(residual_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(residual_payload, indent=2))
    raise SystemExit(0)

if EVENT_FIBER_DIAGNOSTIC:
    event_state = center[:sdim]
    eq0 = event_state[:qdim]
    ev0 = event_state[qdim:2 * qdim]
    em0 = event_state[2 * qdim:]
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        ORDER, eq0, ev0, em0, points=POINTS
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    candidate_cache = {}

    def event_fiber_candidate(offset):
        key = float(offset)
        if key in candidate_cache:
            return candidate_cache[key]
        q = eq0 + key * ev0
        projection = _project_constraints_action_energy(
            ORDER,
            q,
            ev0 + key * acceleration,
            em0 + key * multiplier_rate,
            points=POINTS,
        )
        record = {
            "offset": key,
            "projection_success": bool(projection["success"]),
            "projection_message": projection["message"],
            "projection_iterations": int(projection["iterations"]),
            "projection_action_energy_correction_norm": float(
                projection["action_energy_correction_norm"]
            ),
            "maximum_constraint_residual": float(
                projection["maximum_constraint_residual"]
            ),
        }
        if projection["success"]:
            proposed = center.copy()
            proposed[:qdim] = projection["coordinates"]
            proposed[qdim:2 * qdim] = projection["velocities"]
            proposed[2 * qdim:sdim] = projection["multipliers"]
            exact = rows(proposed)
            raw_lambda = ordered_lambda(proposed[:sdim])
            event_eta = _eta_legendre_minimum(
                ORDER,
                proposed[:qdim],
                proposed[2 * qdim:sdim],
                points=2000,
            )["minimum"]
            child_eta = _eta_legendre_minimum(
                ORDER,
                proposed[sdim:sdim + qdim],
                proposed[sdim + 2 * qdim:],
                points=2000,
            )["minimum"]
            record.update({
                "raw_ordered_event_eigenvalue": float(raw_lambda),
                "scaled_ordered_event_row": float(raw_lambda / ordered_scale),
                "exact_full_residual": float(np.linalg.norm(exact)),
                "exact_event_block_norm": float(np.linalg.norm(
                    exact[:2 * ORDER + 2]
                )),
                "exact_child_block_norm": float(np.linalg.norm(
                    exact[2 * ORDER + 2:]
                )),
                "event_eta": float(event_eta),
                "child_eta": float(child_eta),
                "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
            })
            record["state"] = proposed
        candidate_cache[key] = record
        return record

    derivative_step = float(os.environ.get(
        "BHSM_N12_EVENT_FIBER_DERIVATIVE_STEP", "1.0e-7"
    ))
    minus = event_fiber_candidate(-derivative_step)
    zero = event_fiber_candidate(0.0)
    plus = event_fiber_candidate(derivative_step)
    derivative = None
    estimated_root_offset = None
    if minus["projection_success"] and plus["projection_success"]:
        derivative = float(
            (plus["raw_ordered_event_eigenvalue"]
             - minus["raw_ordered_event_eigenvalue"])
            / (2.0 * derivative_step)
        )
        if abs(derivative) > 1.0e-300:
            estimated_root_offset = float(np.clip(
                -zero["raw_ordered_event_eigenvalue"] / derivative,
                -2.0e-2,
                2.0e-2,
            ))
            for factor in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
                event_fiber_candidate(factor * estimated_root_offset)
    successful = sorted(
        (record for record in candidate_cache.values()
         if record["projection_success"]),
        key=lambda record: record["offset"],
    )
    sign_brackets = []
    for left, right in zip(successful[:-1], successful[1:]):
        if (
            left["raw_ordered_event_eigenvalue"]
            * right["raw_ordered_event_eigenvalue"] <= 0.0
        ):
            sign_brackets.append({
                "left_offset": left["offset"],
                "right_offset": right["offset"],
                "left_raw_event": left["raw_ordered_event_eigenvalue"],
                "right_raw_event": right["raw_ordered_event_eigenvalue"],
            })
    admissible = [
        record for record in successful if record.get("admissible") is True
    ]
    best = min(
        admissible,
        key=lambda record: record["exact_full_residual"],
    ) if admissible else None
    proposal_saved = bool(
        best is not None
        and best["exact_full_residual"] < float(np.linalg.norm(center_rows))
    )
    if proposal_saved:
        np.savez(
            EVENT_FIBER_PROPOSAL_CHECKPOINT,
            state=best["state"],
            n6_ordered_branch_index=n6_branch,
            branch_reference=branch_reference,
        )
    serial_candidates = []
    for record in successful:
        serial_candidates.append({
            key: value for key, value in record.items() if key != "state"
        })
    event_fiber_payload = {
        "classification": (
            "ACTION_OWNED_EVENT_FIBER_EXACT_MERIT_PROPOSAL_AVAILABLE"
            if proposal_saved else
            "ACTION_OWNED_EVENT_FIBER_NO_EXACT_MERIT_PROPOSAL"
        ),
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "ordered_event_eigenvalue_evaluation": (
            ORDERED_EVENT_EIGENVALUE_EVALUATION
        ),
        "canonical_momentum_evaluation": CANONICAL_MOMENTUM_EVALUATION,
        "center_exact_full_residual": float(np.linalg.norm(center_rows)),
        "center_raw_ordered_event_eigenvalue": float(ordered_lambda(
            center[:sdim]
        )),
        "ordered_scale": ordered_scale,
        "derivative_step": derivative_step,
        "projected_event_directional_derivative": derivative,
        "linearized_root_offset": estimated_root_offset,
        "candidates": serial_candidates,
        "ordered_event_sign_brackets": sign_brackets,
        "best_candidate": (
            {key: value for key, value in best.items() if key != "state"}
            if best is not None else None
        ),
        "proposal_checkpoint": (
            str(EVENT_FIBER_PROPOSAL_CHECKPOINT) if proposal_saved else None
        ),
        "proposal_only": True,
        "unchanged_exact_F12": True,
        "physical_equation_or_gate_changed": False,
        "checkpoint_promoted": False,
    }
    RESULT.write_text(
        json.dumps(event_fiber_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(event_fiber_payload, indent=2))
    raise SystemExit(0)


def jacobian_at(state, step):
    matrix = np.empty((center_rows.size, center.size))
    for column in range(center.size):
        delta = np.zeros(center.size)
        delta[column] = step / joint_weights[column]
        matrix[:, column] = (
            rows(state + delta) - rows(state - delta)
        ) / (2.0 * step)
    return matrix


paired_jacobian_reused_from_same_state_checkpoint = cached_j is not None
if paired_jacobian_reused_from_same_state_checkpoint:
    j_full = cached_j_full
    j_half = cached_j_half
    j = cached_j
else:
    j_full = jacobian_at(center, STEPS[0])
    j_half = jacobian_at(center, STEPS[1])
    j = (4.0 * j_half - j_full) / 3.0
normal_u, normal_singular, normal_vh = np.linalg.svd(j, full_matrices=False)
normal_basis = normal_vh.T
soft_right_direction = normal_basis[:, -1]
soft_left_direction = normal_u[:, -1]
if previous_soft_right is not None:
    previous_soft_right = previous_soft_right / np.linalg.norm(
        previous_soft_right
    )
    if float(soft_right_direction @ previous_soft_right) < 0.0:
        soft_right_direction = -soft_right_direction
        soft_left_direction = -soft_left_direction
    soft_rotation_from_previous = float(np.degrees(np.arccos(np.clip(
        abs(float(soft_right_direction @ previous_soft_right)), 0.0, 1.0
    ))))
else:
    soft_rotation_from_previous = None
normal_newton = normal_basis @ (
    (normal_u.T @ (-center_rows)) / normal_singular
)
normal_newton_norm = float(np.linalg.norm(normal_newton))
normal_inverse_bound = float(1.0 / normal_singular[-1])
normal_newton_direction = normal_newton / max(normal_newton_norm, 1.0e-300)

if STRUCTURED_SHAKE_DIAGNOSTIC:
    historical_payload = np.load(SHAKE_HISTORICAL_CENTER)
    historical_state = np.asarray(
        historical_payload["center_state"], dtype=float
    )
    if historical_state.shape != center.shape:
        raise ValueError("structured-shake historical center has wrong shape")
    shake_action = (center - historical_state) * joint_weights
    shake_amplitude = float(np.linalg.norm(shake_action))
    if not shake_amplitude > 0.0:
        raise ValueError("structured-shake historical secant is zero")

    # The two temporary excitations are used only to measure nonlinear
    # residual response.  Every prospective candidate below starts at the
    # unshaken accepted center.  The same-state paired normal right inverse is
    # proposal machinery and has no physical authority.
    raw_shake = shake_action / joint_weights
    shake_records = []
    transported = []
    normal_jacobian = j @ normal_basis
    for sign in (-1.0, 1.0):
        temporary_state = center + sign * raw_shake
        temporary_rows = rows(temporary_state)
        response = normal_basis @ np.linalg.solve(
            normal_jacobian, -temporary_rows
        )
        transported.append(response)
        shake_records.append({
            "sign": sign,
            "temporary_action_coordinate_amplitude": shake_amplitude,
            "temporary_exact_F12_norm": float(np.linalg.norm(
                temporary_rows
            )),
            "temporary_excitation_removed_before_candidate_evaluation": True,
        })
    directions = (
        ("response_from_negative_shake", transported[0]),
        ("response_from_positive_shake", transported[1]),
        ("symmetric_transport", 0.5 * (transported[0] + transported[1])),
        ("curvature_transport", 0.5 * (transported[1] - transported[0])),
    )
    trials = []
    best = None
    center_norm = float(np.linalg.norm(center_rows))
    for name, direction in directions:
        for orientation in (-1.0, 1.0):
            for backtrack in range(15):
                factor = orientation * 0.5 ** backtrack
                candidate_state = center + factor * direction / joint_weights
                try:
                    candidate_rows = rows(candidate_state)
                except (ArithmeticError, FloatingPointError, ValueError):
                    continue
                norm = float(np.linalg.norm(candidate_rows))
                row = {
                    "direction": name,
                    "orientation": orientation,
                    "backtrack": backtrack,
                    "factor": factor,
                    "action_coordinate_step_norm": float(
                        abs(factor) * np.linalg.norm(direction)
                    ),
                    "exact_F12_norm": norm,
                    "exact_reduction": center_norm - norm,
                }
                trials.append(row)
                if norm >= center_norm:
                    continue
                event_eta = _eta_legendre_minimum(
                    ORDER,
                    candidate_state[:qdim],
                    candidate_state[2 * qdim:sdim],
                    points=2000,
                )["minimum"]
                child_eta = _eta_legendre_minimum(
                    ORDER,
                    candidate_state[sdim:sdim + qdim],
                    candidate_state[sdim + 2 * qdim:],
                    points=2000,
                )["minimum"]
                row.update({
                    "event_eta": float(event_eta),
                    "child_eta": float(child_eta),
                    "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
                })
                if row["admissible"] and (
                    best is None or norm < best["exact_F12_norm"]
                ):
                    best = {**row, "state": candidate_state}
    accepted = best is not None
    if accepted:
        np.savez_compressed(
            CHECKPOINT,
            state=best["state"],
            n6_ordered_branch_index=n6_branch,
            branch_reference=branch_reference,
            soft_right_direction=soft_right_direction,
            recent_accepted_states=np.vstack((
                historical_state, center, best["state"]
            )),
            continuous_newton_solver_time=continuous_newton_solver_time,
            continuous_newton_dt=continuous_newton_dt,
        )
    best_serial = (
        {key: value for key, value in best.items() if key != "state"}
        if best is not None else None
    )
    shake_payload = {
        "classification": (
            "N12_STRUCTURED_SHAKE_EXACT_MERIT_PROPOSAL_ACCEPTED"
            if accepted else
            "N12_STRUCTURED_SHAKE_NO_EXACT_MERIT_RECOVERY"
        ),
        "order": ORDER,
        "points": POINTS,
        "source_checkpoint": str(CHECKPOINT),
        "historical_center": str(SHAKE_HISTORICAL_CENTER),
        "center_exact_F12_norm": center_norm,
        "shake_amplitude_owner": (
            "LAST_ACCEPTED_EXACT_N12_ACTION_COORDINATE_SECANT"
        ),
        "shake_action_coordinate_amplitude": shake_amplitude,
        "temporary_shakes": shake_records,
        "transported_directions": [name for name, _ in directions],
        "trial_count": len(trials),
        "best_trials": sorted(
            trials, key=lambda row: row["exact_F12_norm"]
        )[:16],
        "best_admissible_proposal": best_serial,
        "accepted": accepted,
        "candidate_origin_is_unshaken_accepted_center": True,
        "temporary_excitation_removed_before_all_candidate_evaluations": True,
        "unchanged_exact_F12_authoritative": True,
        "same_existing_eta_gate": True,
        "paired_normal_inverse_is_proposal_only": True,
        "physical_equation_event_definition_constraint_or_gate_changed": False,
        "componentwise_monotonicity_added": False,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(shake_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(shake_payload, indent=2))
    raise SystemExit(0)

if CONSTRAINT_OWNER_KERNEL_DIAGNOSTIC:
    # Rows 0:25 and 30:55 are the existing event/child constraint rows.
    # Construct one proposal in the paired-normal kernel of the existing
    # ordered-event, boundary, and momentum rows.  This is a targeted
    # residual-owner proposal, not a new equation or acceptance objective.
    target_rows = list(range(0, 25)) + list(range(30, 55))
    protected_rows = [25] + list(range(26, 30)) + [55, 56]
    protected_normal = j[protected_rows] @ normal_basis
    _, protected_singular, protected_vh = np.linalg.svd(
        protected_normal, full_matrices=True
    )
    protected_tolerance = (
        np.finfo(float).eps
        * max(protected_normal.shape)
        * protected_singular[0]
    )
    protected_rank = int(np.count_nonzero(
        protected_singular > protected_tolerance
    ))
    protected_kernel = protected_vh.T[:, protected_rank:]
    target_on_kernel = (
        j[target_rows] @ normal_basis @ protected_kernel
    )
    target_singular = np.linalg.svd(
        target_on_kernel, compute_uv=False
    )
    coefficients = np.linalg.lstsq(
        target_on_kernel,
        -center_rows[target_rows],
        rcond=1.0e-12,
    )[0]
    correction = normal_basis @ protected_kernel @ coefficients
    predicted = center_rows + j @ correction
    candidates = []
    best = None
    center_norm = float(np.linalg.norm(center_rows))
    for orientation in (1.0, -1.0):
        for backtrack in range(15):
            factor = orientation * 0.5 ** backtrack
            candidate_state = center + factor * correction / joint_weights
            exact = rows(candidate_state)
            norm = float(np.linalg.norm(exact))
            row = {
                "orientation": orientation,
                "backtrack": backtrack,
                "factor": factor,
                "action_coordinate_step_norm": float(
                    abs(factor) * np.linalg.norm(correction)
                ),
                "exact_F12_norm": norm,
                "exact_constraint_owner_norm": float(np.linalg.norm(
                    exact[target_rows]
                )),
                "exact_protected_rows_norm": float(np.linalg.norm(
                    exact[protected_rows]
                )),
                "exact_ordered_event_row": float(exact[25]),
                "exact_boundary_rows_norm": float(np.linalg.norm(
                    exact[26:30]
                )),
                "exact_momentum_rows": exact[55:57].tolist(),
                "exact_momentum_rows_norm": float(np.linalg.norm(
                    exact[55:57]
                )),
                "exact_reduction": center_norm - norm,
            }
            candidates.append(row)
            if norm >= center_norm:
                continue
            event_eta = _eta_legendre_minimum(
                ORDER,
                candidate_state[:qdim],
                candidate_state[2 * qdim:sdim],
                points=2000,
            )["minimum"]
            child_eta = _eta_legendre_minimum(
                ORDER,
                candidate_state[sdim:sdim + qdim],
                candidate_state[sdim + 2 * qdim:],
                points=2000,
            )["minimum"]
            row.update({
                "event_eta": float(event_eta),
                "child_eta": float(child_eta),
                "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
            })
            if row["admissible"] and (
                best is None or norm < best["exact_F12_norm"]
            ):
                best = {**row, "state": candidate_state}
    accepted = best is not None
    if accepted:
        np.savez_compressed(
            CHECKPOINT,
            state=best["state"],
            n6_ordered_branch_index=n6_branch,
            branch_reference=branch_reference,
            soft_right_direction=soft_right_direction,
            recent_accepted_states=np.vstack((center, best["state"])),
            continuous_newton_solver_time=continuous_newton_solver_time,
            continuous_newton_dt=continuous_newton_dt,
        )
    best_serial = (
        {key: value for key, value in best.items() if key != "state"}
        if best is not None else None
    )
    owner_payload = {
        "classification": (
            "N12_CONSTRAINT_OWNER_KERNEL_PROPOSAL_ACCEPTED"
            if accepted else
            "N12_CONSTRAINT_OWNER_KERNEL_NO_EXACT_MERIT_RECOVERY"
        ),
        "order": ORDER,
        "points": POINTS,
        "center_exact_F12_norm": center_norm,
        "center_constraint_owner_norm": float(np.linalg.norm(
            center_rows[target_rows]
        )),
        "center_protected_rows_norm": float(np.linalg.norm(
            center_rows[protected_rows]
        )),
        "protected_rows": protected_rows,
        "constraint_owner_rows": target_rows,
        "protected_normal_rank": protected_rank,
        "protected_kernel_dimension": int(protected_kernel.shape[1]),
        "target_on_kernel_rank": int(np.linalg.matrix_rank(
            target_on_kernel
        )),
        "target_on_kernel_smallest_singular_value": float(
            target_singular[-1]
        ),
        "linear_correction_action_norm": float(np.linalg.norm(correction)),
        "linear_predicted_F12_norm": float(np.linalg.norm(predicted)),
        "linear_predicted_constraint_owner_norm": float(np.linalg.norm(
            predicted[target_rows]
        )),
        "linear_predicted_protected_rows_norm": float(np.linalg.norm(
            predicted[protected_rows]
        )),
        "best_trials": sorted(
            candidates, key=lambda row: row["exact_F12_norm"]
        )[:16],
        "best_admissible_proposal": best_serial,
        "accepted": accepted,
        "proposal_only": True,
        "unchanged_exact_F12_authoritative": True,
        "same_existing_eta_gate": True,
        "new_equation_constraint_gate_scale_or_objective": False,
        "componentwise_monotonicity_added": False,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(owner_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(owner_payload, indent=2))
    raise SystemExit(0)

normal_newton_curvature = []
for radius in (1.0e-4, 5.0e-5):
    plus = rows(center + radius * normal_newton_direction / joint_weights)
    minus = rows(center - radius * normal_newton_direction / joint_weights)
    curvature = float(np.linalg.norm(
        plus - 2.0 * center_rows + minus
    ) / radius**2)
    normal_newton_curvature.append({
        "radius": radius,
        "full_F12_second_difference_norm": curvature,
    })
local_nonlinear_majorant_measurement = max(
    row["full_F12_second_difference_norm"]
    for row in normal_newton_curvature
)
nk_product_measurement = float(
    2.0
    * normal_inverse_bound
    * local_nonlinear_majorant_measurement
    * normal_newton_norm
)

e_len = 2 * ORDER + 2
c0 = e_len

if RADII_GATE_DIAGNOSTIC:
    event_eta = _eta_legendre_minimum(
        ORDER, center[:qdim], center[2 * qdim:sdim], points=2000
    )["minimum"]
    child_eta = _eta_legendre_minimum(
        ORDER,
        center[sdim:sdim + qdim],
        center[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    km_product = normal_inverse_bound * local_nonlinear_majorant_measurement
    discriminant = 1.0 - nk_product_measurement
    measured_roots = []
    if discriminant > 0.0 and km_product > 0.0:
        square_root = np.sqrt(discriminant)
        measured_roots = [
            float((1.0 - square_root) / km_product),
            float((1.0 + square_root) / km_product),
        ]
    payload = {
        "classification": "DIRECT_N12_NUMERICAL_CERTIFICATE_NOT_YET_OBTAINED",
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "ordered_event_eigenvalue_evaluation": (
            ORDERED_EVENT_EIGENVALUE_EVALUATION
        ),
        "candidate": {
            "exact_full_F12_norm": float(np.linalg.norm(center_rows)),
            "exact_event_block_norm": float(np.linalg.norm(
                center_rows[:e_len]
            )),
            "exact_child_block_norm": float(np.linalg.norm(
                center_rows[e_len:]
            )),
            "event_eta_minimum": float(event_eta),
            "child_eta_minimum": float(child_eta),
            "normal_rank": int(np.linalg.matrix_rank(j)),
            "smallest_normal_singular_value": float(normal_singular[-1]),
            "normal_inverse_bound": normal_inverse_bound,
            "normal_Newton_correction_norm": normal_newton_norm,
            "ordered_event_neighbor_gap": transport_neighbor_gap,
        },
        "measured_action_norm_radii_polynomial": {
            "formula": "p(r)=Y+(K*M2/2)*r^2-r",
            "Y": normal_newton_norm,
            "K": normal_inverse_bound,
            "measured_M2": local_nonlinear_majorant_measurement,
            "measured_2_K_M2_Y": nk_product_measurement,
            "discriminant": discriminant,
            "negative_interval_roots": measured_roots,
            "measured_local_basin_entered": bool(discriminant > 0.0),
        },
        "rigorous_certificate_gate": {
            "M2_is_a_rigorous_full_action_ball_supremum": False,
            "bordered_lift_and_ordered_eigenprojector_inverse_majorants": (
                False
            ),
            "eta_event_Dirac_persistence_ball_transfer_enclosed": False,
            "direct_N12_root_certified": False,
            "reason": (
                "THE_NEGATIVE_MEASURED_RADII_INTERVAL_USES_ONLY_THE_"
                "TWO_RADIUS_DIRECTIONAL_CURVATURE_MEASUREMENT;_THE_"
                "RETAINED_ACTION_FOURTH_VARIATION,_STATE_DEPENDENT_"
                "BORDERED_CANONICAL_LIFT,_ORDERED_EIGENPROJECTOR,_AND_"
                "PHYSICAL_NEIGHBORHOOD_SUPREMA_ARE_NOT_YET_ENCLOSED_"
                "ON_THE_FULL_ACTION_BALL"
            ),
        },
        "exact_next_mathematical_lemma": (
            "BOUND_THE_RETAINED_ACTION_FOURTH_VARIATION_AND_ALL_"
            "STATE_DEPENDENT_BORDERED_LIFT_AND_ORDERED_EIGENPROJECTOR_"
            "INVERSES_UNIFORMLY_ON_THE_MEASURED_N12_ACTION_BALL,_THEN_"
            "TRANSFER_THAT_BALL_INSIDE_THE_EXISTING_ETA_EVENT_DIRAC_"
            "AND_POSITIVE_DURATION_PERSISTENCE_NEIGHBORHOODS"
        ),
        "unchanged_exact_F12": True,
        "proposal_regularization_promoted_as_physics": False,
        "new_equation_constraint_or_gate": False,
        "checkpoint_modified": False,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

if ORDERED_EVENT_PROFILE_DIAGNOSTIC:
    ordered_event_row = e_len - 1
    other_rows = np.delete(j, ordered_event_row, axis=0) @ normal_basis
    _, _, other_vh = np.linalg.svd(other_rows, full_matrices=True)
    coupled_event_normal = other_vh.T[:, -1]
    coupled_event_direction = normal_basis @ coupled_event_normal
    coupled_event_derivative = float(
        j[ordered_event_row] @ coupled_event_direction
    )
    if abs(coupled_event_derivative) <= 1.0e-300:
        raise RuntimeError(
            "coupled ordered-event normal derivative is numerically zero"
        )
    coupled_event_newton = (
        -center_rows[ordered_event_row] / coupled_event_derivative
    ) * coupled_event_direction
    profile = []
    for factor in (
        -0.5, -0.25, -0.125, 0.0, 0.015625, 0.03125, 0.046875,
        0.05, 0.0625, 0.078125, 0.09375, 0.125, 0.25, 0.5, 1.0,
    ):
        state = center + factor * coupled_event_newton / joint_weights
        exact = rows(state)
        event_eta = _eta_legendre_minimum(
            ORDER, state[:qdim], state[2 * qdim:sdim], points=2000
        )["minimum"]
        child_eta = _eta_legendre_minimum(
            ORDER,
            state[sdim:sdim + qdim],
            state[sdim + 2 * qdim:],
            points=2000,
        )["minimum"]
        profile.append({
            "factor_of_linear_ordered_event_Newton_step": factor,
            "action_coordinate_step_norm": float(
                abs(factor) * np.linalg.norm(coupled_event_newton)
            ),
            "exact_full_residual": float(np.linalg.norm(exact)),
            "signed_scaled_ordered_event_residual": float(
                exact[ordered_event_row]
            ),
            "other_56_rows_norm": float(np.linalg.norm(
                np.delete(exact, ordered_event_row)
            )),
            "exact_event_block_norm": float(np.linalg.norm(exact[:e_len])),
            "exact_child_block_norm": float(np.linalg.norm(exact[e_len:])),
            "event_eta": float(event_eta),
            "child_eta": float(child_eta),
            "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
        })
    admissible = [row for row in profile if row["admissible"]]
    best = min(admissible, key=lambda row: row["exact_full_residual"])
    sign_brackets = []
    ordered = sorted(admissible, key=lambda row: row[
        "factor_of_linear_ordered_event_Newton_step"
    ])
    for left, right in zip(ordered[:-1], ordered[1:]):
        if (
            left["signed_scaled_ordered_event_residual"]
            * right["signed_scaled_ordered_event_residual"] <= 0.0
        ):
            sign_brackets.append({
                "left_factor": left[
                    "factor_of_linear_ordered_event_Newton_step"
                ],
                "right_factor": right[
                    "factor_of_linear_ordered_event_Newton_step"
                ],
                "left_residual": left[
                    "signed_scaled_ordered_event_residual"
                ],
                "right_residual": right[
                    "signed_scaled_ordered_event_residual"
                ],
            })
    payload = {
        "classification": "COUPLED_ORDERED_EVENT_SAME_STATE_PROFILE",
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "ordered_event_eigenvalue_evaluation": (
            ORDERED_EVENT_EIGENVALUE_EVALUATION
        ),
        "center_exact_full_residual": float(np.linalg.norm(center_rows)),
        "center_exact_residual_vector": center_rows.tolist(),
        "center_signed_scaled_ordered_event_residual": float(
            center_rows[ordered_event_row]
        ),
        "center_other_56_rows_norm": float(np.linalg.norm(
            np.delete(center_rows, ordered_event_row)
        )),
        "paired_normal_rank": int(np.linalg.matrix_rank(j)),
        "paired_smallest_normal_singular_value": float(normal_singular[-1]),
        "coupled_ordered_event_derivative": coupled_event_derivative,
        "linear_ordered_event_Newton_action_norm": float(
            np.linalg.norm(coupled_event_newton)
        ),
        "profile": profile,
        "best_admissible_sample": best,
        "ordered_event_sign_brackets": sign_brackets,
        "proposal_only": True,
        "unchanged_exact_F12": True,
        "checkpoint_modified": False,
        "new_physics_or_gate": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    raise SystemExit(0)

low_rows = (
    list(range(LOW))
    + list(range(ORDER, ORDER + LOW))
    + [2 * ORDER, 2 * ORDER + 1]
    + list(range(c0, c0 + 4))
    + list(range(c0 + 4, c0 + 4 + LOW))
    + list(range(c0 + 4 + ORDER, c0 + 4 + ORDER + LOW))
    + [c0 + 4 + 2 * ORDER]
    + list(range(c0 + 4 + 2 * ORDER + 1, c0 + 4 + 2 * ORDER + 3))
)
high_rows = [index for index in range(center_rows.size) if index not in set(low_rows)]

if CENTER_ONLY_DIAGNOSTIC:
    event_eta = _eta_legendre_minimum(
        ORDER, center[:qdim], center[2 * qdim:sdim], points=2000
    )["minimum"]
    child_eta = _eta_legendre_minimum(
        ORDER,
        center[sdim:sdim + qdim],
        center[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    signed_soft = float(soft_left_direction @ center_rows)
    hard = center_rows - soft_left_direction * signed_soft
    if REFRESH_CENTER_CHECKPOINT:
        np.savez(
            CHECKPOINT,
            state=center,
            n6_ordered_branch_index=n6_branch,
            branch_reference=branch_reference,
            soft_right_direction=soft_right_direction,
            paired_j_full=j_full,
            paired_j_half=j_half,
            paired_jacobian=j,
            recent_accepted_states=center[None, :],
        )
    center_payload = {
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
        "ordered_event_eigenvalue_evaluation": (
            ORDERED_EVENT_EIGENVALUE_EVALUATION
        ),
        "ordered_scale": ordered_scale,
        "method": "EXACT_ACCEPTED_CENTER_DIAGNOSTIC_ONLY",
        "exact_full_residual": float(np.linalg.norm(center_rows)),
        "signed_soft_residual": signed_soft,
        "hard_complement_norm": float(np.linalg.norm(hard)),
        "event_eta": float(event_eta),
        "child_eta": float(child_eta),
        "normal_rank": int(np.linalg.matrix_rank(j)),
        "smallest_normal_singular_value": float(normal_singular[-1]),
        "normal_Newton_correction_norm": normal_newton_norm,
        "normal_inverse_bound": normal_inverse_bound,
        "local_nonlinear_majorant_measurement": (
            local_nonlinear_majorant_measurement
        ),
        "Newton_Kantorovich_product": nk_product_measurement,
        "paired_jacobian_reused_from_same_state_checkpoint": (
            paired_jacobian_reused_from_same_state_checkpoint
        ),
        "wall_clock_seconds": float(time.perf_counter() - START_WALL_CLOCK),
        "unchanged_exact_F12": True,
        "checkpoint_modified": REFRESH_CENTER_CHECKPOINT,
        "new_physics_or_gate": False,
        "radii_certification_started": False,
    }
    RESULT.write_text(
        json.dumps(center_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(center_payload, indent=2))
    raise SystemExit(0)

if CONTINUOUS_NEWTON_DIAGNOSTIC:
    # In action coordinates the Euclidean metric is the authorized action
    # metric M.  Hence ``normal_newton`` is exactly -R_M F: the minimum-M-norm
    # right-inverse direction on the gauge-fixed normal complement.
    dt_values = sorted(set(
        float(np.clip(continuous_newton_dt * factor, 1.0e-6, 0.125))
        for factor in (0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
    ))
    center_norm = float(np.linalg.norm(center_rows))
    candidate_records = []
    candidate_states = []
    candidate_rows_list = []
    for solver_dt in dt_values:
        ideal_ratio = float(np.exp(-solver_dt))
        # Exponential integration of the locally frozen right inverse gives
        # the exact ideal linear residual law without another stage Jacobian.
        action_step = (1.0 - ideal_ratio) * normal_newton
        candidate_state = center + action_step / joint_weights
        exact_candidate_rows = rows(candidate_state)
        exact_norm = float(np.linalg.norm(exact_candidate_rows))
        ideal_rows = ideal_ratio * center_rows
        flow_prediction_defect = float(
            np.linalg.norm(exact_candidate_rows - ideal_rows)
            / max(center_norm, 1.0e-300)
        )
        event_eta = _eta_legendre_minimum(
            ORDER,
            candidate_state[:qdim],
            candidate_state[2 * qdim:sdim],
            points=2000,
        )["minimum"]
        child_eta = _eta_legendre_minimum(
            ORDER,
            candidate_state[sdim:sdim + qdim],
            candidate_state[sdim + 2 * qdim:],
            points=2000,
        )["minimum"]
        signed_soft = float(soft_left_direction @ exact_candidate_rows)
        signed_soft_event = float(
            soft_left_direction[:e_len] @ exact_candidate_rows[:e_len]
        )
        hard = exact_candidate_rows - soft_left_direction * signed_soft
        candidate_records.append({
            "solver_dt": solver_dt,
            "action_norm_step": float(np.linalg.norm(action_step)),
            "exact_full_residual": exact_norm,
            "signed_center_soft_residual": signed_soft,
            "signed_center_soft_event_residual": signed_soft_event,
            "hard_complement_norm": float(np.linalg.norm(hard)),
            "event_eta": float(event_eta),
            "child_eta": float(child_eta),
            "center_normal_rank": int(np.linalg.matrix_rank(j)),
            "center_sigma_minimum": float(normal_singular[-1]),
            "right_inverse_direction_action_norm": normal_newton_norm,
            "ideal_exp_residual_ratio": ideal_ratio,
            "actual_residual_ratio": float(exact_norm / center_norm),
            "flow_prediction_defect": flow_prediction_defect,
            "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
            "exact_merit_improved": bool(exact_norm < center_norm),
        })
        candidate_states.append(candidate_state)
        candidate_rows_list.append(exact_candidate_rows)
    eligible = [
        index for index, record in enumerate(candidate_records)
        if record["admissible"] and record["exact_merit_improved"]
    ]
    selected_index = (
        min(eligible, key=lambda index: candidate_records[index][
            "exact_full_residual"
        ])
        if eligible else None
    )
    accepted_refresh = None
    endpoint_paired_jacobian_evaluations = 0
    if selected_index is not None:
        accepted_state = candidate_states[selected_index]
        accepted_rows = candidate_rows_list[selected_index]
        accepted_full = jacobian_at(accepted_state, STEPS[0])
        accepted_half = jacobian_at(accepted_state, STEPS[1])
        endpoint_paired_jacobian_evaluations = 1
        accepted_jacobian = (4.0 * accepted_half - accepted_full) / 3.0
        accepted_u, accepted_singular, accepted_vh = np.linalg.svd(
            accepted_jacobian, full_matrices=False
        )
        accepted_rank = int(np.linalg.matrix_rank(accepted_jacobian))
        accepted_soft_right = accepted_vh[-1]
        accepted_soft_left = accepted_u[:, -1]
        if float(accepted_soft_right @ soft_right_direction) < 0.0:
            accepted_soft_right = -accepted_soft_right
            accepted_soft_left = -accepted_soft_left
        selected = candidate_records[selected_index]
        if accepted_rank == center_rows.size:
            accepted_action_step = joint_weights * (accepted_state - center)
            exact_secant = accepted_rows - center_rows
            predicted_secant = j @ accepted_action_step
            secant_defect = float(
                np.linalg.norm(exact_secant - predicted_secant)
                / max(
                    np.linalg.norm(exact_secant),
                    np.linalg.norm(predicted_secant),
                    1.0e-300,
                )
            )
            accepted_signed_soft = float(accepted_soft_left @ accepted_rows)
            accepted_hard = (
                accepted_rows - accepted_soft_left * accepted_signed_soft
            )
            accepted_normal_newton = accepted_vh.T @ (
                (accepted_u.T @ (-accepted_rows)) / accepted_singular
            )
            accepted_inverse_bound = float(1.0 / accepted_singular[-1])
            defect_to_ideal_drop = float(
                selected["flow_prediction_defect"]
                / max(1.0 - selected["ideal_exp_residual_ratio"], 1.0e-300)
            )
            if defect_to_ideal_drop < 0.1:
                next_dt = min(0.125, 2.0 * selected["solver_dt"])
            elif defect_to_ideal_drop < 0.5:
                next_dt = selected["solver_dt"]
            else:
                next_dt = max(1.0e-6, 0.5 * selected["solver_dt"])
            path_ledger = (
                json.loads(CURVED_PATH_LEDGER.read_text(encoding="utf-8"))
                if CURVED_PATH_LEDGER.exists() else []
            )
            path_increment = float(np.linalg.norm(accepted_action_step))
            cumulative_path = float(
                (path_ledger[-1]["cumulative_action_norm_path_length"]
                 if path_ledger else 0.0) + path_increment
            )
            solver_time_after = float(
                continuous_newton_solver_time + selected["solver_dt"]
            )
            residual_decrease = float(
                center_norm - selected["exact_full_residual"]
            )
            path_ledger.append({
                "proposal": "minimum_action_norm_continuous_newton",
                "continuous_newton_solver_time": solver_time_after,
                "solver_dt": selected["solver_dt"],
                "cumulative_action_norm_path_length": cumulative_path,
                "action_norm_path_increment": path_increment,
                "exact_full_residual": selected["exact_full_residual"],
                "signed_local_soft_full_residual": accepted_signed_soft,
                "signed_local_soft_event_residual": selected[
                    "signed_center_soft_event_residual"
                ],
                "hard_complement_norm": float(np.linalg.norm(accepted_hard)),
                "exact_residual_decrease_per_unit_path_length": float(
                    residual_decrease / max(path_increment, 1.0e-300)
                ),
                "event_eta": selected["event_eta"],
                "child_eta": selected["child_eta"],
                "normal_rank": accepted_rank,
                "smallest_normal_singular_value": float(
                    accepted_singular[-1]
                ),
                "soft_right_rotation_degrees": float(np.degrees(np.arccos(
                    np.clip(abs(float(
                        accepted_soft_right @ soft_right_direction
                    )), 0.0, 1.0)
                ))),
                "ideal_exp_residual_ratio": selected[
                    "ideal_exp_residual_ratio"
                ],
                "actual_residual_ratio": selected["actual_residual_ratio"],
                "flow_prediction_defect": selected[
                    "flow_prediction_defect"
                ],
            })
            CURVED_PATH_LEDGER.write_text(
                json.dumps(path_ledger, indent=2) + "\n", encoding="utf-8"
            )
            next_recent_accepted_states = np.vstack((
                recent_accepted_states, accepted_state
            ))[-3:]
            np.savez(
                CHECKPOINT,
                state=accepted_state,
                n6_ordered_branch_index=n6_branch,
                branch_reference=branch_reference,
                soft_right_direction=accepted_soft_right,
                curved_previous_soft_right_direction=soft_right_direction,
                paired_j_full=accepted_full,
                paired_j_half=accepted_half,
                paired_jacobian=accepted_jacobian,
                recent_accepted_states=next_recent_accepted_states,
                continuous_newton_solver_time=solver_time_after,
                continuous_newton_dt=next_dt,
            )
            accepted_refresh = {
                "candidate_index": selected_index,
                "solver_time_before": continuous_newton_solver_time,
                "solver_time_after": solver_time_after,
                "solver_dt": selected["solver_dt"],
                "next_solver_dt": next_dt,
                "exact_full_residual": selected["exact_full_residual"],
                "signed_refreshed_soft_residual": accepted_signed_soft,
                "refreshed_hard_complement_norm": float(np.linalg.norm(
                    accepted_hard
                )),
                "event_eta": selected["event_eta"],
                "child_eta": selected["child_eta"],
                "normal_rank": accepted_rank,
                "smallest_normal_singular_value": float(
                    accepted_singular[-1]
                ),
                "normal_Newton_correction_norm": float(np.linalg.norm(
                    accepted_normal_newton
                )),
                "normal_inverse_bound": accepted_inverse_bound,
                "soft_right_rotation_from_center_degrees": path_ledger[-1][
                    "soft_right_rotation_degrees"
                ],
                "normalized_Broyden_secant_defect": secant_defect,
                "action_norm_path_increment": path_increment,
                "cumulative_action_norm_path_length": cumulative_path,
                "exact_residual_decrease": residual_decrease,
                "exact_residual_decrease_per_unit_path_length": float(
                    residual_decrease / max(path_increment, 1.0e-300)
                ),
                "ideal_exp_residual_ratio": selected[
                    "ideal_exp_residual_ratio"
                ],
                "actual_residual_ratio": selected["actual_residual_ratio"],
                "flow_prediction_defect": selected[
                    "flow_prediction_defect"
                ],
                "flow_defect_to_ideal_drop_ratio": defect_to_ideal_drop,
            }
    wall_clock_seconds = float(time.perf_counter() - START_WALL_CLOCK)
    continuous_payload = {
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
        "method": "MINIMUM_ACTION_NORM_CONTINUOUS_NEWTON",
        "integration_proposal": "FROZEN_RIGHT_INVERSE_EXPONENTIAL_STEP",
        "higher_order_stage_not_used_because_it_requires_an_extra_exact_J": True,
        "center_exact_full_residual": center_norm,
        "center_signed_soft_residual": float(
            soft_left_direction @ center_rows
        ),
        "center_hard_complement_norm": float(np.linalg.norm(
            center_rows - soft_left_direction * float(
                soft_left_direction @ center_rows
            )
        )),
        "center_normal_rank": int(np.linalg.matrix_rank(j)),
        "center_sigma_minimum": float(normal_singular[-1]),
        "right_inverse_direction_action_norm": normal_newton_norm,
        "normal_inverse_bound": normal_inverse_bound,
        "Newton_Kantorovich_product_at_center": nk_product_measurement,
        "candidates": candidate_records,
        "accepted_refresh": accepted_refresh,
        "endpoint_paired_exact_J_evaluations": (
            endpoint_paired_jacobian_evaluations
        ),
        "wall_clock_seconds": wall_clock_seconds,
        "exact_residual_reduction_per_endpoint_paired_J": (
            center_norm - accepted_refresh["exact_full_residual"]
            if accepted_refresh is not None else 0.0
        ),
        "wall_clock_seconds_per_exact_residual_reduction": (
            wall_clock_seconds
            / max(
                center_norm - accepted_refresh["exact_full_residual"],
                1.0e-300,
            )
            if accepted_refresh is not None else None
        ),
        "classification": (
            "CONTINUOUS_NEWTON_EXACT_ADMISSIBLE_STEP_ACCEPTED"
            if accepted_refresh is not None else
            "CONTINUOUS_NEWTON_NO_EXACT_ADMISSIBLE_FULL_RANK_STEP"
        ),
        "unchanged_exact_F12": True,
        "solver_time_is_physical": False,
        "action_metric_is_physical_gate": False,
        "proposal_only_transport": True,
        "new_physics_or_gate": False,
        "radii_certification_started": False,
    }
    RESULT.write_text(
        json.dumps(continuous_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(continuous_payload, indent=2))
    raise SystemExit(0)

if SOFT_SUBSPACE_DIAGNOSTIC:
    probe_amplitude = float(os.environ.get(
        "BHSM_N12_SUBSPACE_PROBE_AMPLITUDE", "2.5e-5"
    ))
    probe_state = (
        center + probe_amplitude * soft_right_direction / joint_weights
    )
    probe_rows = rows(probe_state)
    probe_event_eta = _eta_legendre_minimum(
        ORDER,
        probe_state[:qdim],
        probe_state[2 * qdim:sdim],
        points=2000,
    )["minimum"]
    probe_child_eta = _eta_legendre_minimum(
        ORDER,
        probe_state[sdim:sdim + qdim],
        probe_state[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    probe_full = jacobian_at(probe_state, STEPS[0])
    probe_half = jacobian_at(probe_state, STEPS[1])
    probe_jacobian = (4.0 * probe_half - probe_full) / 3.0
    probe_u, probe_singular, probe_vh = np.linalg.svd(
        probe_jacobian, full_matrices=False
    )
    subspace_comparisons = []
    for dimension in (1, 2, 3):
        center_subspace = normal_vh[-dimension:].T
        probe_subspace = probe_vh[-dimension:].T
        cosines = np.linalg.svd(
            center_subspace.T @ probe_subspace,
            compute_uv=False,
        )
        cosines = np.clip(cosines, 0.0, 1.0)
        principal_angles = np.degrees(np.arccos(cosines))
        projector_gap = float(np.sqrt(max(
            0.0, 1.0 - float(np.min(cosines)) ** 2
        )))
        low_index = dimension - 1
        center_ascending = normal_singular[::-1]
        probe_ascending = probe_singular[::-1]
        center_gap_ratio = float(
            center_ascending[dimension] / center_ascending[low_index]
        )
        probe_gap_ratio = float(
            probe_ascending[dimension] / probe_ascending[low_index]
        )
        subspace_comparisons.append({
            "dimension": dimension,
            "principal_angles_degrees": principal_angles.tolist(),
            "maximum_principal_angle_degrees": float(np.max(
                principal_angles
            )),
            "projector_operator_gap": projector_gap,
            "center_gap_above_subspace_ratio": center_gap_ratio,
            "probe_gap_above_subspace_ratio": probe_gap_ratio,
            "numerically_stable_below_15_degrees": bool(
                float(np.max(principal_angles)) < 15.0
            ),
            "numerically_separated_by_ratio_two": bool(
                min(center_gap_ratio, probe_gap_ratio) >= 2.0
            ),
        })
    stable_dimensions = [
        record["dimension"] for record in subspace_comparisons
        if record["numerically_stable_below_15_degrees"]
        and record["numerically_separated_by_ratio_two"]
    ]
    selected_dimension = min(stable_dimensions) if stable_dimensions else None
    center_soft_left = normal_u[:, -1]
    if float(normal_vh[-1] @ probe_vh[-1]) < 0.0:
        probe_soft_left = -probe_u[:, -1]
    else:
        probe_soft_left = probe_u[:, -1]
    signed_probe_soft = float(probe_soft_left @ probe_rows)
    probe_hard = probe_rows - probe_soft_left * signed_probe_soft
    diagnostic_payload = {
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
        "center_exact_full_residual": float(np.linalg.norm(center_rows)),
        "probe_action_coordinate_amplitude": probe_amplitude,
        "probe_exact_full_residual": float(np.linalg.norm(probe_rows)),
        "probe_signed_local_soft_residual": signed_probe_soft,
        "probe_hard_complement_norm": float(np.linalg.norm(probe_hard)),
        "probe_event_eta": probe_event_eta,
        "probe_child_eta": probe_child_eta,
        "center_normal_rank": int(np.linalg.matrix_rank(j)),
        "probe_normal_rank": int(np.linalg.matrix_rank(probe_jacobian)),
        "center_four_smallest_singular_values": normal_singular[-4:][::-1].tolist(),
        "probe_four_smallest_singular_values": probe_singular[-4:][::-1].tolist(),
        "center_adjacent_low_singular_ratios": (
            normal_singular[-4:][::-1][1:]
            / normal_singular[-4:][::-1][:-1]
        ).tolist(),
        "probe_adjacent_low_singular_ratios": (
            probe_singular[-4:][::-1][1:]
            / probe_singular[-4:][::-1][:-1]
        ).tolist(),
        "subspace_comparisons": subspace_comparisons,
        "selected_smallest_stable_separated_dimension": selected_dimension,
        "classification": (
            f"STABLE_SEPARATED_{selected_dimension}D_SOFT_BUNDLE"
            if selected_dimension is not None else
            "SOFT_PROFILE_CURVED_NO_STABLE_SEPARATED_K_LE_3"
        ),
        "stability_and_separation_thresholds_are_proposal_controls_only": True,
        "unchanged_exact_F12": True,
        "new_physics_or_gate": False,
        "radii_certification_started": False,
        "Newton_Kantorovich_product_at_center": nk_product_measurement,
    }
    checkpoint_fields = {
        "state": center,
        "n6_ordered_branch_index": n6_branch,
        "branch_reference": branch_reference,
        "soft_right_direction": soft_right_direction,
        "normal_soft_subspace_3": normal_vh[-3:].T,
        "four_smallest_singular_values": normal_singular[-4:][::-1],
    }
    if curved_previous_soft_right is not None:
        checkpoint_fields["curved_previous_soft_right_direction"] = (
            curved_previous_soft_right
        )
    np.savez(CHECKPOINT, **checkpoint_fields)
    RESULT.write_text(
        json.dumps(diagnostic_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(diagnostic_payload, indent=2))
    raise SystemExit(0)

if CURVED_SOFT_2D_DIAGNOSTIC:
    if previous_soft_right is None:
        raise RuntimeError(
            "the curved-soft plane requires the previous paired soft vector"
        )
    history_soft_right = (
        curved_previous_soft_right
        if curved_previous_soft_right is not None else previous_soft_right
    )
    curved_direction = history_soft_right - float(
        history_soft_right @ soft_right_direction
    ) * soft_right_direction
    curved_direction_norm = float(np.linalg.norm(curved_direction))
    if curved_direction_norm <= 1.0e-10:
        history_checkpoint_name = os.environ.get(
            "BHSM_N12_CURVED_HISTORY_CHECKPOINT"
        )
        if history_checkpoint_name:
            history_checkpoint = np.load(history_checkpoint_name)
            history_soft_right = np.asarray(
                history_checkpoint["soft_right_direction"], dtype=float
            )
            history_soft_right /= np.linalg.norm(history_soft_right)
            if float(history_soft_right @ soft_right_direction) < 0.0:
                history_soft_right = -history_soft_right
            curved_direction = history_soft_right - float(
                history_soft_right @ soft_right_direction
            ) * soft_right_direction
            curved_direction_norm = float(np.linalg.norm(curved_direction))
    if curved_direction_norm <= 1.0e-10:
        raise RuntimeError(
            "the previous soft vector has no resolved orthogonal component"
        )
    curved_direction /= curved_direction_norm
    plane_basis = np.column_stack((soft_right_direction, curved_direction))
    proposal_planes = [{
        "name": "consecutive_soft_singular_vectors",
        "basis": plane_basis,
    }]
    if recent_accepted_states.shape[0] >= 3:
        previous_chord = joint_weights * (
            recent_accepted_states[-2] - recent_accepted_states[-3]
        )
        current_chord = joint_weights * (
            recent_accepted_states[-1] - recent_accepted_states[-2]
        )
        current_chord_norm = float(np.linalg.norm(current_chord))
        if current_chord_norm > 1.0e-12:
            osculating_tangent = current_chord / current_chord_norm
            osculating_curvature = previous_chord - float(
                previous_chord @ osculating_tangent
            ) * osculating_tangent
            osculating_curvature_norm = float(np.linalg.norm(
                osculating_curvature
            ))
            if osculating_curvature_norm > 1.0e-12:
                osculating_curvature /= osculating_curvature_norm
                proposal_planes.append({
                    "name": "last_three_state_osculating_plane",
                    "basis": np.column_stack((
                        osculating_tangent, osculating_curvature
                    )),
                    "previous_chord_action_norm": float(np.linalg.norm(
                        previous_chord
                    )),
                    "current_chord_action_norm": current_chord_norm,
                })
    candidate_records = []
    candidate_states = []
    candidate_rows_list = []
    proposal_plane_summaries = []
    for proposal_plane in proposal_planes:
        proposal_basis = proposal_plane["basis"]
        proposal_jacobian = j @ proposal_basis
        predicted_coefficients = np.linalg.lstsq(
            proposal_jacobian, -center_rows, rcond=1.0e-12
        )[0]
        predicted_norm = float(np.linalg.norm(predicted_coefficients))
        if predicted_norm <= 1.0e-300:
            predicted_unit = np.asarray([1.0, 0.0])
        else:
            predicted_unit = predicted_coefficients / predicted_norm
        perpendicular_unit = np.asarray([
            -predicted_unit[1], predicted_unit[0]
        ])
        trust_radius = float(min(
            5.0e-4, max(5.0e-5, 0.01 * predicted_norm)
        ))
        proposal_plane_summaries.append({
            key: value for key, value in proposal_plane.items()
            if key != "basis"
        } | {
            "predicted_coefficients": predicted_coefficients.tolist(),
            "trust_radius": trust_radius,
        })
        radius_factors = (
            1.0 / 32.0, 1.0 / 16.0, 1.0 / 8.0, 3.0 / 16.0,
            0.25, 3.0 / 8.0, 0.5, 0.75, 1.0
        )
        if (
            proposal_plane["name"] == "last_three_state_osculating_plane"
            and trust_radius <= 1.0e-4
        ):
            radius_factors += (2.0,)
        for radius_factor in radius_factors:
            for angle_degrees in (
                -90.0, -60.0, -45.0, -30.0, -15.0, 0.0,
                15.0, 30.0, 45.0, 60.0, 90.0
            ):
                angle = np.radians(angle_degrees)
                unit = (
                    np.cos(angle) * predicted_unit
                    + np.sin(angle) * perpendicular_unit
                )
                coefficients = radius_factor * trust_radius * unit
                action_step = proposal_basis @ coefficients
                candidate_state = center + action_step / joint_weights
                exact_candidate_rows = rows(candidate_state)
                predicted_candidate_rows = center_rows + j @ action_step
                event_eta = _eta_legendre_minimum(
                    ORDER,
                    candidate_state[:qdim],
                    candidate_state[2 * qdim:sdim],
                    points=2000,
                )["minimum"]
                child_eta = _eta_legendre_minimum(
                    ORDER,
                    candidate_state[sdim:sdim + qdim],
                    candidate_state[sdim + 2 * qdim:],
                    points=2000,
                )["minimum"]
                signed_soft_full = float(
                    soft_left_direction @ exact_candidate_rows
                )
                signed_soft_event = float(
                    soft_left_direction[:e_len]
                    @ exact_candidate_rows[:e_len]
                )
                hard_complement = exact_candidate_rows - (
                    soft_left_direction * signed_soft_full
                )
                predicted_reduction = float(
                    np.linalg.norm(center_rows)
                    - np.linalg.norm(predicted_candidate_rows)
                )
                actual_reduction = float(
                    np.linalg.norm(center_rows)
                    - np.linalg.norm(exact_candidate_rows)
                )
                candidate_records.append({
                    "proposal_plane": proposal_plane["name"],
                    "coefficient_1": float(coefficients[0]),
                    "coefficient_2": float(coefficients[1]),
                    "action_coordinate_norm": float(np.linalg.norm(
                        coefficients
                    )),
                    "exact_full_residual": float(np.linalg.norm(
                        exact_candidate_rows
                    )),
                    "signed_local_soft_full_residual": signed_soft_full,
                    "signed_local_soft_event_residual": signed_soft_event,
                    "hard_complement_norm": float(np.linalg.norm(
                        hard_complement
                    )),
                    "event_eta": event_eta,
                    "child_eta": child_eta,
                    "paired_center_normal_rank": int(np.linalg.matrix_rank(j)),
                    "paired_center_smallest_singular_value": float(
                        normal_singular[-1]
                    ),
                    "predicted_exact_merit_reduction": predicted_reduction,
                    "actual_exact_merit_reduction": actual_reduction,
                    "actual_to_predicted_reduction_ratio": (
                        actual_reduction / predicted_reduction
                        if predicted_reduction > 0.0 else None
                    ),
                    "admissible": bool(event_eta > 0.0 and child_eta > 0.0),
                    "exact_merit_improved": bool(actual_reduction > 0.0),
                })
                candidate_states.append(candidate_state)
                candidate_rows_list.append(exact_candidate_rows)
    accepted_indices = [
        index for index, record in enumerate(candidate_records)
        if record["admissible"] and record["exact_merit_improved"]
    ]
    accepted_index = (
        min(
            accepted_indices,
            key=lambda index: candidate_records[index]["exact_full_residual"],
        )
        if accepted_indices else None
    )
    accepted_refresh = None
    path_ledger = (
        json.loads(CURVED_PATH_LEDGER.read_text(encoding="utf-8"))
        if CURVED_PATH_LEDGER.exists() else []
    )
    if accepted_index is not None:
        accepted_state = candidate_states[accepted_index]
        accepted_rows = candidate_rows_list[accepted_index]
        accepted_full = jacobian_at(accepted_state, STEPS[0])
        accepted_half = jacobian_at(accepted_state, STEPS[1])
        accepted_jacobian = (4.0 * accepted_half - accepted_full) / 3.0
        accepted_u, accepted_singular, accepted_vh = np.linalg.svd(
            accepted_jacobian, full_matrices=False
        )
        accepted_soft_right = accepted_vh[-1]
        accepted_soft_left = accepted_u[:, -1]
        if float(accepted_soft_right @ soft_right_direction) < 0.0:
            accepted_soft_right = -accepted_soft_right
            accepted_soft_left = -accepted_soft_left
        accepted_action_step = joint_weights * (accepted_state - center)
        exact_secant = accepted_rows - center_rows
        predicted_secant = j @ accepted_action_step
        secant_defect = float(
            np.linalg.norm(exact_secant - predicted_secant)
            / max(
                np.linalg.norm(exact_secant),
                np.linalg.norm(predicted_secant),
                1.0e-300,
            )
        )
        accepted_signed_soft = float(accepted_soft_left @ accepted_rows)
        accepted_hard = accepted_rows - accepted_soft_left * accepted_signed_soft
        accepted_refresh = {
            "candidate_index": accepted_index,
            "exact_full_residual": float(np.linalg.norm(accepted_rows)),
            "signed_refreshed_soft_residual": accepted_signed_soft,
            "refreshed_hard_complement_norm": float(np.linalg.norm(accepted_hard)),
            "normal_rank": int(np.linalg.matrix_rank(accepted_jacobian)),
            "smallest_normal_singular_value": float(accepted_singular[-1]),
            "soft_right_rotation_from_center_degrees": float(np.degrees(
                np.arccos(np.clip(abs(float(
                    accepted_soft_right @ soft_right_direction
                )), 0.0, 1.0))
            )),
            "normalized_Broyden_secant_defect": secant_defect,
        }
        accepted_path_increment = float(np.linalg.norm(accepted_action_step))
        cumulative_path_length = float(
            (path_ledger[-1]["cumulative_action_norm_path_length"]
             if path_ledger else 0.0)
            + accepted_path_increment
        )
        exact_residual_decrease = float(
            np.linalg.norm(center_rows) - np.linalg.norm(accepted_rows)
        )
        accepted_refresh.update({
            "action_norm_path_increment": accepted_path_increment,
            "cumulative_action_norm_path_length": cumulative_path_length,
            "exact_residual_decrease_per_unit_path_length": float(
                exact_residual_decrease / accepted_path_increment
            ),
        })
        path_ledger.append({
            "cumulative_action_norm_path_length": cumulative_path_length,
            "action_norm_path_increment": accepted_path_increment,
            "exact_full_residual": float(np.linalg.norm(accepted_rows)),
            "signed_local_soft_full_residual": accepted_signed_soft,
            "signed_local_soft_event_residual": candidate_records[
                accepted_index
            ]["signed_local_soft_event_residual"],
            "hard_complement_norm": float(np.linalg.norm(accepted_hard)),
            "exact_residual_decrease_per_unit_path_length": float(
                exact_residual_decrease / accepted_path_increment
            ),
            "event_eta": candidate_records[accepted_index]["event_eta"],
            "child_eta": candidate_records[accepted_index]["child_eta"],
            "normal_rank": int(np.linalg.matrix_rank(accepted_jacobian)),
            "smallest_normal_singular_value": float(accepted_singular[-1]),
            "soft_right_rotation_degrees": accepted_refresh[
                "soft_right_rotation_from_center_degrees"
            ],
        })
        CURVED_PATH_LEDGER.write_text(
            json.dumps(path_ledger, indent=2) + "\n", encoding="utf-8"
        )
        next_recent_accepted_states = np.vstack((
            recent_accepted_states, accepted_state
        ))[-3:]
        np.savez(
            CHECKPOINT,
            state=accepted_state,
            n6_ordered_branch_index=n6_branch,
            branch_reference=branch_reference,
            soft_right_direction=accepted_soft_right,
            curved_previous_soft_right_direction=soft_right_direction,
            paired_j_full=accepted_full,
            paired_j_half=accepted_half,
            paired_jacobian=accepted_jacobian,
            recent_accepted_states=next_recent_accepted_states,
        )
    curved_payload = {
        "order": ORDER,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
        "center_exact_full_residual": float(np.linalg.norm(center_rows)),
        "center_normal_rank": int(np.linalg.matrix_rank(j)),
        "center_smallest_normal_singular_value": float(normal_singular[-1]),
        "previous_to_current_soft_rotation_degrees": soft_rotation_from_previous,
        "previous_soft_orthogonal_component_norm": curved_direction_norm,
        "proposal_planes": proposal_plane_summaries,
        "candidates": candidate_records,
        "accepted_refresh": accepted_refresh,
        "classification": (
            "CURVED_SOFT_2D_EXACT_MERIT_STEP_ACCEPTED"
            if accepted_refresh is not None else
            "CURVED_SOFT_2D_NO_EXACT_MERIT_STEP_AT_THIS_TRUST_RADIUS"
        ),
        "unchanged_exact_F12": True,
        "proposal_only_geometry": True,
        "paired_jacobian_reused_from_same_state_checkpoint": (
            paired_jacobian_reused_from_same_state_checkpoint
        ),
        "new_physics_or_gate": False,
        "radii_certification_started": False,
        "Newton_Kantorovich_product_at_center": nk_product_measurement,
        "endpoint_paired_exact_J_evaluations": (
            1 if accepted_refresh is not None else 0
        ),
        "wall_clock_seconds": float(time.perf_counter() - START_WALL_CLOCK),
        "exact_residual_reduction_per_endpoint_paired_J": (
            float(np.linalg.norm(center_rows))
            - accepted_refresh["exact_full_residual"]
            if accepted_refresh is not None else 0.0
        ),
    }
    if accepted_refresh is not None:
        curved_payload["wall_clock_seconds_per_exact_residual_reduction"] = (
            curved_payload["wall_clock_seconds"]
            / max(
                curved_payload[
                    "exact_residual_reduction_per_endpoint_paired_J"
                ],
                1.0e-300,
            )
        )
    RESULT.write_text(
        json.dumps(curved_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(curved_payload, indent=2))
    raise SystemExit(0)

soft_newton_amplitude = float(
    -(soft_left_direction @ center_rows) / normal_singular[-1]
)
soft_scalar_profile = []
profile_state_vectors = {}
profile_soft_right_vectors = {}
profile_amplitudes_override = os.environ.get(
    "BHSM_N12_PROFILE_AMPLITUDES"
)
profile_amplitudes = (
    tuple(float(value) for value in profile_amplitudes_override.split(","))
    if PROFILE_JACOBIAN_DIAGNOSTIC and profile_amplitudes_override else
    (-1.0 / 512.0, 0.0, 1.0 / 1024.0, 1.0 / 512.0,
     1.0 / 256.0, 1.0 / 128.0)
    if PROFILE_JACOBIAN_DIAGNOSTIC else
    (-1.0 / 32.0, -1.0 / 64.0, -1.0 / 128.0,
     -1.0 / 256.0, -1.0 / 512.0, -1.0 / 1024.0,
     0.0,
     1.0 / 1024.0, 1.0 / 512.0, 1.0 / 256.0,
     1.0 / 128.0, 1.0 / 64.0, 1.0 / 32.0)
)
for relative_amplitude in profile_amplitudes:
    action_amplitude = relative_amplitude * soft_newton_amplitude
    profile_state = (
        center + action_amplitude * soft_right_direction / joint_weights
    )
    profile_rows = rows(profile_state)
    profile_event_eta = _eta_legendre_minimum(
        ORDER,
        profile_state[:qdim],
        profile_state[2 * qdim:sdim],
        points=2000,
    )["minimum"]
    profile_child_eta = _eta_legendre_minimum(
        ORDER,
        profile_state[sdim:sdim + qdim],
        profile_state[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    profile_record = {
        "relative_to_linear_soft_Newton_amplitude": relative_amplitude,
        "action_coordinate_amplitude": action_amplitude,
        "exact_norm": float(np.linalg.norm(profile_rows)),
        "exact_event_block_norm": float(np.linalg.norm(
            profile_rows[:e_len]
        )),
        "exact_non_event_block_norm": float(np.linalg.norm(
            profile_rows[e_len:]
        )),
        "event_eta": profile_event_eta,
        "child_eta": profile_child_eta,
        "exact_F12_changed": False,
    }
    if PROFILE_JACOBIAN_DIAGNOSTIC:
        if relative_amplitude == 0.0:
            profile_jacobian = j
        else:
            profile_full = jacobian_at(profile_state, STEPS[0])
            profile_half = jacobian_at(profile_state, STEPS[1])
            profile_jacobian = (4.0 * profile_half - profile_full) / 3.0
        profile_u, profile_singular, profile_vh = np.linalg.svd(
            profile_jacobian, full_matrices=False
        )
        profile_soft_right = profile_vh[-1]
        profile_soft_left = profile_u[:, -1]
        if float(profile_soft_right @ soft_right_direction) < 0.0:
            profile_soft_right = -profile_soft_right
            profile_soft_left = -profile_soft_left
        signed_soft_full = float(profile_soft_left @ profile_rows)
        signed_soft_event = float(
            profile_soft_left[:e_len] @ profile_rows[:e_len]
        )
        hard_rows = profile_rows - profile_soft_left * signed_soft_full
        profile_record.update({
            "signed_soft_full_residual": signed_soft_full,
            "signed_soft_event_residual": signed_soft_event,
            "exact_hard_residual_norm": float(np.linalg.norm(hard_rows)),
            "normal_rank": int(np.linalg.matrix_rank(profile_jacobian)),
            "normal_row_count": int(profile_jacobian.shape[0]),
            "smallest_normal_singular_value": float(profile_singular[-1]),
            "soft_right_rotation_from_center_degrees": float(np.degrees(
                np.arccos(np.clip(abs(float(
                    profile_soft_right @ soft_right_direction
                )), 0.0, 1.0))
            )),
        })
        profile_state_vectors[action_amplitude] = profile_state
        profile_soft_right_vectors[action_amplitude] = profile_soft_right
    soft_scalar_profile.append(profile_record)

if PROFILE_JACOBIAN_DIAGNOSTIC:
    admissible = [
        row for row in soft_scalar_profile
        if row["event_eta"] > 0.0 and row["child_eta"] > 0.0
    ]
    ordered_profile = sorted(
        admissible, key=lambda row: row["action_coordinate_amplitude"]
    )
    sign_change_brackets = []
    for left, right in zip(ordered_profile, ordered_profile[1:]):
        left_value = left["signed_soft_event_residual"]
        right_value = right["signed_soft_event_residual"]
        if left_value == 0.0 or left_value * right_value < 0.0:
            sign_change_brackets.append({
                "left_action_coordinate_amplitude": left[
                    "action_coordinate_amplitude"
                ],
                "right_action_coordinate_amplitude": right[
                    "action_coordinate_amplitude"
                ],
                "left_signed_soft_event_residual": left_value,
                "right_signed_soft_event_residual": right_value,
            })
    best_profile = min(admissible, key=lambda row: row["exact_norm"])
    maximum_rotation = max(
        row["soft_right_rotation_from_center_degrees"]
        for row in admissible
    )
    if sign_change_brackets:
        profile_classification = "ADMISSIBLE_SOFT_EVENT_CROSSING_BRACKETED"
    elif maximum_rotation > 15.0:
        profile_classification = "CURVED_SOFT_NORMAL_GEOMETRY"
    else:
        profile_classification = (
            "ADMISSIBLE_ONE_DIMENSIONAL_LOCAL_MINIMUM_NO_OBSTRUCTION_CLAIM"
        )
    diagnostic_payload = {
        "order": ORDER,
        "points": POINTS,
        "center_exact_norm": float(np.linalg.norm(center_rows)),
        "soft_linear_Newton_amplitude": soft_newton_amplitude,
        "profile": soft_scalar_profile,
        "admissible_sign_change_brackets": sign_change_brackets,
        "best_admissible_profile_state": best_profile,
        "maximum_soft_right_rotation_degrees": maximum_rotation,
        "material_rotation_threshold_degrees": 15.0,
        "classification": profile_classification,
        "unchanged_exact_F12": True,
        "profile_is_proposal_diagnostic_only": True,
        "positive_profile_minimum_promoted_as_obstruction": False,
        "radii_certification_started": False,
        "Newton_Kantorovich_product_at_center": nk_product_measurement,
    }
    best_amplitude = best_profile["action_coordinate_amplitude"]
    np.savez(
        PROFILE_PROPOSAL_CHECKPOINT,
        state=profile_state_vectors[best_amplitude],
        n6_ordered_branch_index=n6_branch,
        branch_reference=branch_reference,
        soft_right_direction=profile_soft_right_vectors[best_amplitude],
    )
    diagnostic_payload["best_profile_proposal_checkpoint"] = str(
        PROFILE_PROPOSAL_CHECKPOINT
    )
    RESULT.write_text(
        json.dumps(diagnostic_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(diagnostic_payload, indent=2))
    raise SystemExit(0)


def low_state_indices(order, low):
    q = [0]
    for family in range(3):
        q.extend(range(1 + family * order, 1 + family * order + low))
    v = [qdim + index for index in q]
    m = list(range(2 * qdim, 2 * qdim + low))
    m += list(range(2 * qdim + order, 2 * qdim + order + low))
    return q + v + m


low_one = low_state_indices(ORDER, LOW)
low_columns = low_one + [sdim + index for index in low_one]
high_columns = [index for index in range(center.size) if index not in set(low_columns)]

jll = j[np.ix_(low_rows, low_columns)]
jlh = j[np.ix_(low_rows, high_columns)]
jhl = j[np.ix_(high_rows, low_columns)]
jhh = j[np.ix_(high_rows, high_columns)]
r_low = center_rows[low_rows]
r_high = center_rows[high_rows]

if SHELL_DECOMPOSITION_DIAGNOSTIC:
    blocks = {
        "A_inherited_core": jll,
        "B_inherited_shell": jlh,
        "C_new_core": jhl,
        "D_new_shell": jhh,
    }
    paired_half_blocks = {
        "A_inherited_core": j_half[np.ix_(low_rows, low_columns)],
        "B_inherited_shell": j_half[np.ix_(low_rows, high_columns)],
        "C_new_core": j_half[np.ix_(high_rows, low_columns)],
        "D_new_shell": j_half[np.ix_(high_rows, high_columns)],
    }
    block_payload = {}
    for name, matrix in blocks.items():
        singular = np.linalg.svd(matrix, compute_uv=False)
        block_payload[name] = {
            "shape": list(matrix.shape),
            "numerical_rank": int(np.linalg.matrix_rank(matrix)),
            "smallest_singular_value": float(singular[-1]),
            "largest_singular_value": float(singular[0]),
            "Richardson_minus_half_spectral_norm": float(np.linalg.norm(
                matrix - paired_half_blocks[name], ord=2
            )),
        }
    d_right = jhh.T @ np.linalg.inv(jhh @ jhh.T)
    event_new_rows = list(range(LOW, ORDER)) + list(range(
        ORDER + LOW, 2 * ORDER
    ))
    child_new_rows = list(range(c0 + 4 + LOW, c0 + 4 + ORDER)) + list(range(
        c0 + 4 + ORDER + LOW, c0 + 4 + 2 * ORDER
    ))
    shell_one = [
        index for index in range(sdim) if index not in set(low_one)
    ]
    event_shell_columns = shell_one
    child_shell_columns = [sdim + index for index in shell_one]
    event_diagonal = j[np.ix_(event_new_rows, event_shell_columns)]
    child_diagonal = j[np.ix_(child_new_rows, child_shell_columns)]
    event_cross = j[np.ix_(event_new_rows, child_shell_columns)]
    child_cross = j[np.ix_(child_new_rows, event_shell_columns)]
    shell_payload = {
        "classification": "N12_RANK_DEFICIT_RESOLVED_BY_SHELL_DIRECTIONS",
        "order": ORDER,
        "low_order": LOW,
        "points": POINTS,
        "n6_ordered_branch_index": n6_branch,
        "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
        "state_dimension_split": {
            "joint_total": int(center.size),
            "joint_core": len(low_columns),
            "joint_shell": len(high_columns),
        },
        "residual_dimension_split": {
            "total": int(center_rows.size),
            "inherited": len(low_rows),
            "new_shell": len(high_rows),
            "inherited_row_indices": low_rows,
            "new_shell_row_indices": high_rows,
        },
        "exact_full_residual": float(np.linalg.norm(center_rows)),
        "inherited_residual_norm": float(np.linalg.norm(r_low)),
        "new_shell_residual_norm": float(np.linalg.norm(r_high)),
        "blocks": block_payload,
        "D_range_test": {
            "right_inverse_spectral_norm": float(np.linalg.norm(
                d_right, ord=2
            )),
            "D_Dright_minus_identity_spectral_norm": float(np.linalg.norm(
                jhh @ d_right - np.eye(len(high_rows)), ord=2
            )),
            "augmented_D_identity_numerical_rank": int(np.linalg.matrix_rank(
                np.column_stack((jhh, np.eye(len(high_rows))))
            )),
        },
        "separated_event_child_shell_blocks": {
            "event_diagonal_rank": int(np.linalg.matrix_rank(event_diagonal)),
            "event_diagonal_sigma_min": float(np.linalg.svd(
                event_diagonal, compute_uv=False
            )[-1]),
            "child_diagonal_rank": int(np.linalg.matrix_rank(child_diagonal)),
            "child_diagonal_sigma_min": float(np.linalg.svd(
                child_diagonal, compute_uv=False
            )[-1]),
            "event_rows_child_shell_spectral_norm": float(np.linalg.norm(
                event_cross, ord=2
            )),
            "child_rows_event_shell_spectral_norm": float(np.linalg.norm(
                child_cross, ord=2
            )),
        },
        "scope": (
            "POINTWISE_CORRECTED_PAIRED_JACOBIAN_EVIDENCE_ONLY;_NO_"
            "NONLINEAR_SHELL_NEIGHBORHOOD_OR_CONTINUUM_PROMOTION"
        ),
        "unchanged_exact_F12": True,
        "checkpoint_modified": False,
        "new_physics_or_gate": False,
    }
    RESULT.write_text(
        json.dumps(shell_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(shell_payload, indent=2))
    raise SystemExit(0)

uh, sh, vht = np.linalg.svd(jhh, full_matrices=False)
jhh_right = vht.T @ np.diag(1.0 / sh) @ uh.T
feedback = jlh @ jhh_right @ jhl
source_feedback = jlh @ jhh_right @ r_high

u0, s0, vh0 = np.linalg.svd(jll, full_matrices=False)
v0 = vh0.T
hard_u = u0[:, :-1]
soft_u = u0[:, -1:]
hard_v = v0[:, :-1]
soft_v = v0[:, -1:]


def scalar_data(t):
    schur = jll - t * feedback
    reduced_schur = u0.T @ schur @ v0
    source = r_low - t * source_feedback
    a = hard_u.T @ schur @ hard_v
    b = hard_u.T @ schur @ soft_v
    c = soft_u.T @ schur @ hard_v
    d = float((soft_u.T @ schur @ soft_v).item())
    rh = hard_u.T @ source
    rs = float((soft_u.T @ source).item())
    a_inverse_b = np.linalg.solve(a, b)
    a_inverse_r = np.linalg.solve(a, rh)
    denominator = float(d - (c @ a_inverse_b).item())
    compatibility = float(rs - (c @ a_inverse_r).item())
    return (
        denominator,
        compatibility,
        float(np.linalg.svd(a, compute_uv=False)[-1]),
        float(np.linalg.svd(schur, compute_uv=False)[-1]),
        float(np.linalg.svd(reduced_schur, compute_uv=False)[-1]),
    )


grid = np.linspace(0.0, 1.0, 2001)
data = np.asarray([scalar_data(float(t)) for t in grid])
imin = int(np.argmin(np.abs(data[:, 0])))
ismin = int(np.argmin(data[:, 3]))
irsmin = int(np.argmin(data[:, 4]))


def enclose_affine_schur_interval(left, right):
    """Norm-enclose the fixed-frame affine Schur reduction on [left,right]."""

    midpoint = 0.5 * (left + right)
    radius = 0.5 * (right - left)
    schur = jll - midpoint * feedback
    reduced_schur = u0.T @ schur @ v0
    a = hard_u.T @ schur @ hard_v
    b = hard_u.T @ schur @ soft_v
    c = soft_u.T @ schur @ hard_v
    d = float((soft_u.T @ schur @ soft_v).item())
    a_prime = -(hard_u.T @ feedback @ hard_v)
    b_prime = -(hard_u.T @ feedback @ soft_v)
    c_prime = -(soft_u.T @ feedback @ hard_v)
    d_prime = -float((soft_u.T @ feedback @ soft_v).item())
    a_inverse = np.linalg.inv(a)
    hard_inverse_norm = float(np.linalg.norm(a_inverse, ord=2))
    hard_neumann = radius * float(np.linalg.norm(
        a_prime @ a_inverse, ord=2
    ))
    hard_gap = (1.0 - hard_neumann) / hard_inverse_norm
    reduced_inverse = np.linalg.inv(reduced_schur)
    reduced_inverse_norm = float(np.linalg.norm(reduced_inverse, ord=2))
    reduced_prime = -(u0.T @ feedback @ v0)
    reduced_neumann = radius * float(np.linalg.norm(
        reduced_prime @ reduced_inverse, ord=2
    ))
    full_gap = (1.0 - reduced_neumann) / reduced_inverse_norm
    if hard_gap <= 0.0:
        return {
            "left": left, "right": right, "hard_gap_lower": hard_gap,
            "reduced_full_gap_lower": full_gap,
            "soft_denominator_lower": -np.inf,
        }
    a_inverse_b = np.linalg.solve(a, b)
    denominator = float(d - (c @ a_inverse_b).item())
    b_bound = float(np.linalg.norm(b) + radius * np.linalg.norm(b_prime))
    c_bound = float(np.linalg.norm(c) + radius * np.linalg.norm(c_prime))
    derivative_bound = (
        abs(d_prime)
        + float(np.linalg.norm(c_prime)) * b_bound / hard_gap
        + c_bound * float(np.linalg.norm(a_prime, ord=2)) * b_bound / hard_gap**2
        + c_bound * float(np.linalg.norm(b_prime)) / hard_gap
    )
    derivative_denominator_lower = (
        abs(denominator) - derivative_bound * radius
    )
    # In the orthonormal 33-dimensional normal section, the bottom-right
    # block of reduced_schur^{-1} is denominator^{-1}.  Hence its minimum
    # singular value is also a rigorous (and much sharper) denominator bound.
    denominator_lower = max(
        derivative_denominator_lower, full_gap
    )
    # Round all asserted lower bounds outward by one binary64 ulp.
    return {
        "left": left,
        "right": right,
        "hard_gap_lower": float(np.nextafter(hard_gap, -np.inf)),
        "reduced_full_gap_lower": float(np.nextafter(full_gap, -np.inf)),
        "hard_Neumann_factor_upper": float(np.nextafter(
            hard_neumann, np.inf
        )),
        "reduced_full_Neumann_factor_upper": float(np.nextafter(
            reduced_neumann, np.inf
        )),
        "soft_denominator_midpoint": denominator,
        "soft_derivative_upper": float(np.nextafter(derivative_bound, np.inf)),
        "soft_derivative_route_lower": float(np.nextafter(
            derivative_denominator_lower, -np.inf
        )),
        "soft_denominator_lower": float(np.nextafter(denominator_lower, -np.inf)),
        "soft_lower_bound_uses_full_schur_inverse_identity": bool(
            full_gap >= derivative_denominator_lower
        ),
    }


def affine_schur_interval_cover(max_depth=18):
    pending = [(0.0, 1.0, 0)]
    accepted = []
    rejected = []
    while pending:
        left, right, depth = pending.pop()
        enclosure = enclose_affine_schur_interval(left, right)
        if (
            enclosure["hard_gap_lower"] > 0.0
            and enclosure["reduced_full_gap_lower"] > 0.0
            and enclosure["soft_denominator_lower"] > 0.0
        ):
            accepted.append(enclosure)
        elif depth < max_depth:
            midpoint = 0.5 * (left + right)
            pending.append((midpoint, right, depth + 1))
            pending.append((left, midpoint, depth + 1))
        else:
            rejected.append(enclosure)
    accepted.sort(key=lambda row: row["left"])
    return accepted, rejected


affine_cover, affine_rejected = affine_schur_interval_cover()
affine_cover_digest = hashlib.sha256(
    json.dumps(affine_cover, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

# One full minimum-norm Schur correction at t=1, evaluated by the unchanged rows.
schur1 = jll - feedback
effective1 = r_low - source_feedback
delta_low = -np.linalg.pinv(schur1, rcond=1.0e-12) @ effective1
delta_high = -jhh_right @ (r_high + jhl @ delta_low)
delta = np.zeros(center.size)
delta[low_columns] = delta_low
delta[high_columns] = delta_high
trial = center + delta / joint_weights
trial_rows = rows(trial)
eq = trial[:qdim]
em = trial[2 * qdim:sdim]
cq = trial[sdim:sdim + qdim]
cm = trial[sdim + 2 * qdim:]
line_trials = []
for factor in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625):
    line_state = center + factor * delta / joint_weights
    line_rows = rows(line_state)
    line_trials.append({
        "factor": factor,
        "action_norm": float(factor * np.linalg.norm(delta)),
        "exact_norm": float(np.linalg.norm(line_rows)),
        "exact_low_norm": float(np.linalg.norm(line_rows[low_rows])),
        "exact_high_norm": float(np.linalg.norm(line_rows[high_rows])),
    })
direction = delta / np.linalg.norm(delta)
directional_curvature = []
for radius in (1.0e-3, 5.0e-4):
    plus = rows(center + radius * direction / joint_weights)
    minus = rows(center - radius * direction / joint_weights)
    value = (plus - 2.0 * center_rows + minus) / radius**2
    directional_curvature.append({
        "radius": radius,
        "second_difference_norm": float(np.linalg.norm(value)),
    })

# Continue only the unchanged exact joint residual.  The paired Richardson
# matrix seeds a chord/Broyden proposal; exact total merit and eta decide every
# accepted state.
x = np.zeros(center.size)
current_rows = center_rows.copy()
proposal_jacobian = j.copy()
continuation = []
current_state = center.copy()
lambda_diagnostics = []
last_relative_lambda = None
for iteration in range(PROPOSAL_STEPS):
    singular = np.linalg.svd(proposal_jacobian, compute_uv=False)
    proposal_directions = [(
        "minimum_action_norm_chord",
        0.0,
        np.linalg.lstsq(
            proposal_jacobian, -current_rows, rcond=1.0e-12
        )[0],
    )]
    if PROPOSAL_MODE == "normal_lm":
        row_gram = proposal_jacobian @ proposal_jacobian.T
        identity_rows = np.eye(current_rows.size)
        sigma_min = float(singular[-1])
        if iteration == 0 or last_relative_lambda is None:
            relative_lambdas = (
                0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0,
                7.0, 8.0, 9.0, 10.0, 12.0, 16.0, 24.0, 32.0,
                64.0, 128.0, 256.0,
            )
        else:
            relative_lambdas = tuple(sorted({
                min(256.0, max(0.25, last_relative_lambda * multiplier))
                for multiplier in (0.25, 0.5, 1.0, 2.0, 4.0)
            }))
        for relative_lambda in relative_lambdas:
            regularization = relative_lambda * sigma_min
            correction = proposal_jacobian.T @ np.linalg.solve(
                row_gram + regularization**2 * identity_rows,
                -current_rows,
            )
            proposal_directions.append((
                "normal_levenberg",
                relative_lambda,
                correction,
            ))
        if iteration == 0:
            non_event_normal = proposal_jacobian[e_len:] @ normal_basis
            _, non_event_singular, non_event_vh = np.linalg.svd(
                non_event_normal, full_matrices=True
            )
            non_event_tolerance = (
                np.finfo(float).eps
                * max(non_event_normal.shape)
                * non_event_singular[0]
            )
            non_event_rank = int(np.count_nonzero(
                non_event_singular > non_event_tolerance
            ))
            non_event_kernel = non_event_vh.T[:, non_event_rank:]
            event_on_kernel = (
                proposal_jacobian[:e_len]
                @ normal_basis
                @ non_event_kernel
            )
            kernel_coefficients = np.linalg.lstsq(
                event_on_kernel,
                -current_rows[:e_len],
                rcond=1.0e-12,
            )[0]
            proposal_directions.append((
                "non_event_kernel_event_newton",
                0.0,
                normal_basis @ non_event_kernel @ kernel_coefficients,
            ))
            # The ordered scalar is the final event row.  Within the existing
            # 57-dimensional gauge-fixed normal space, the other 56 rows have
            # a one-dimensional nullspace.  Its lift is the coupled
            # event-to-complete-child tangent: it changes the ordered row while
            # preserving every other physical row to first order.
            ordered_event_row = e_len - 1
            other_rows = np.delete(
                proposal_jacobian, ordered_event_row, axis=0
            ) @ normal_basis
            _, _, other_vh = np.linalg.svd(
                other_rows, full_matrices=True
            )
            coupled_event_normal = other_vh.T[:, -1]
            coupled_event_direction = normal_basis @ coupled_event_normal
            coupled_event_derivative = float(
                proposal_jacobian[ordered_event_row]
                @ coupled_event_direction
            )
            if abs(coupled_event_derivative) > 1.0e-300:
                proposal_directions.append((
                    "coupled_ordered_event_kernel_newton",
                    0.0,
                    (
                        -current_rows[ordered_event_row]
                        / coupled_event_derivative
                    ) * coupled_event_direction,
                ))
            proposal_directions.append((
                "soft_right_scalar_newton",
                0.0,
                soft_newton_amplitude * soft_right_direction,
            ))
    candidates = []
    if iteration == 0:
        line_factors = (
            1.0, 0.5, 0.25, 0.125, 0.1, 0.09375, 0.078125,
            0.0625, 0.05, 0.046875, 0.03125,
            0.015625, 0.0078125, 0.00390625, 0.001953125,
            0.0009765625,
        )
    else:
        line_factors = (1.0, 0.5, 0.25, 0.125, 0.0625)
    for proposal_type, relative_lambda, correction in proposal_directions:
        for factor in line_factors:
            trial_x = x + factor * correction
            trial_state = center + trial_x / joint_weights
            exact = rows(trial_state)
            candidates.append((
                float(np.linalg.norm(exact)),
                factor,
                proposal_type,
                relative_lambda,
                trial_x,
                exact,
            ))
    if iteration == 0:
        for proposal_type, relative_lambda, _ in proposal_directions:
            family = [
                candidate for candidate in candidates
                if candidate[2] == proposal_type
                and candidate[3] == relative_lambda
            ]
            candidate = min(family, key=lambda item: item[0])
            candidate_state = center + candidate[4] / joint_weights
            candidate_event_eta = _eta_legendre_minimum(
                ORDER,
                candidate_state[:qdim],
                candidate_state[2 * qdim:sdim],
                points=2000,
            )["minimum"]
            candidate_child_eta = _eta_legendre_minimum(
                ORDER,
                candidate_state[sdim:sdim + qdim],
                candidate_state[sdim + 2 * qdim:],
                points=2000,
            )["minimum"]
            candidate_low = candidate[5][low_rows]
            lambda_diagnostics.append({
                "proposal_type": proposal_type,
                "relative_lambda": relative_lambda,
                "best_factor": candidate[1],
                "exact_norm": candidate[0],
                "exact_hard_residual_norm": float(np.linalg.norm(
                    hard_u.T @ candidate_low
                )),
                "exact_soft_residual_magnitude": float(abs(
                    (soft_u.T @ candidate_low).item()
                )),
                "exact_high_residual_norm": float(np.linalg.norm(
                    candidate[5][high_rows]
                )),
                "event_eta": candidate_event_eta,
                "child_eta": candidate_child_eta,
                "paired_exact_normal_gap_at_center": float(singular[-1]),
                "regularized_proposal_gap": float(
                    singular[-1] * np.sqrt(1.0 + relative_lambda**2)
                ) if proposal_type == "normal_levenberg" else float(
                    singular[-1]
                ),
                "regularized_gap_promoted_as_physics": False,
                "exact_F12_changed": False,
            })
    (
        best_norm,
        factor,
        proposal_type,
        relative_lambda,
        next_x,
        next_rows,
    ) = min(candidates, key=lambda item: item[0])
    current_norm = float(np.linalg.norm(current_rows))
    best_state = center + next_x / joint_weights
    best_event_eta = _eta_legendre_minimum(
        ORDER,
        best_state[:qdim],
        best_state[2 * qdim:sdim],
        points=2000,
    )["minimum"]
    best_child_eta = _eta_legendre_minimum(
        ORDER,
        best_state[sdim:sdim + qdim],
        best_state[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    if not (
        best_norm < current_norm
        and best_event_eta > 0.0
        and best_child_eta > 0.0
    ):
        continuation.append({
            "iteration": iteration,
            "accepted": False,
            "current_norm": current_norm,
            "best_trial_norm": best_norm,
            "best_proposal_type": proposal_type,
            "best_relative_lambda": relative_lambda,
            "best_trial_event_eta": best_event_eta,
            "best_trial_child_eta": best_child_eta,
            "rejection_reason": (
                "EXACT_MERIT_NOT_IMPROVED"
                if not best_norm < current_norm else
                "EXISTING_ETA_DOMAIN_NOT_PRESERVED"
            ),
        })
        break
    step = next_x - x
    row_step = next_rows - current_rows
    predicted_row_step = proposal_jacobian @ step
    predicted_rows = current_rows + predicted_row_step
    predicted_reduction = current_norm - float(np.linalg.norm(predicted_rows))
    actual_reduction = current_norm - best_norm
    reduction_ratio = (
        actual_reduction / predicted_reduction
        if predicted_reduction > 0.0 else None
    )
    defect = row_step - predicted_row_step
    normalized_secant_defect = float(
        np.linalg.norm(defect)
        / max(np.linalg.norm(row_step), np.linalg.norm(predicted_row_step), 1.0e-300)
    )
    proposal_jacobian += np.outer(defect, step) / float(step @ step)
    _, _, updated_vh = np.linalg.svd(proposal_jacobian, full_matrices=False)
    updated_soft = updated_vh.T[:, -1]
    soft_rotation_from_fresh = float(np.degrees(np.arccos(np.clip(
        abs(float(updated_soft @ soft_right_direction)), 0.0, 1.0
    ))))
    x = next_x
    current_rows = next_rows
    current_state = best_state
    last_relative_lambda = (
        relative_lambda if proposal_type == "normal_levenberg" else None
    )
    event_eta = best_event_eta
    child_eta = best_child_eta
    continuation.append({
        "iteration": iteration,
        "accepted": True,
        "factor": factor,
        "proposal_type": proposal_type,
        "relative_lambda": relative_lambda,
        "exact_norm_before": current_norm,
        "exact_norm_after": best_norm,
        "exact_event_block_norm": float(np.linalg.norm(next_rows[:e_len])),
        "exact_attachment_trace_norm": float(np.linalg.norm(
            next_rows[c0:c0 + 4]
        )),
        "exact_child_constraint_norm": float(np.linalg.norm(
            next_rows[c0 + 4:c0 + 4 + 2 * ORDER + 1]
        )),
        "exact_attachment_momentum_reaction_norm": float(np.linalg.norm(
            next_rows[c0 + 4 + 2 * ORDER + 1:]
        )),
        "exact_hard_residual_norm": float(np.linalg.norm(
            hard_u.T @ next_rows[low_rows]
        )),
        "exact_soft_residual_magnitude": float(abs(
            (soft_u.T @ next_rows[low_rows]).item()
        )),
        "exact_high_residual_norm": float(np.linalg.norm(
            next_rows[high_rows]
        )),
        "cumulative_action_norm": float(np.linalg.norm(x)),
        "event_eta": event_eta,
        "child_eta": child_eta,
        "proposal_smallest_singular": float(
            np.linalg.svd(proposal_jacobian, compute_uv=False)[-1]
        ),
        "paired_exact_derivative_current": iteration == 0,
        "proposal_regularization_promoted_as_physics": False,
        "normalized_Broyden_secant_defect": normalized_secant_defect,
        "predicted_exact_merit_reduction": predicted_reduction,
        "actual_exact_merit_reduction": actual_reduction,
        "actual_to_predicted_reduction_ratio": reduction_ratio,
        "soft_right_rotation_from_fresh_degrees": soft_rotation_from_fresh,
    })
    if best_norm < 1.0e-9:
        break
    if proposal_type == "non_event_kernel_event_newton":
        break
    if proposal_type == "soft_right_scalar_newton":
        break
    if (
        normalized_secant_defect > 0.5
        or reduction_ratio is None
        or reduction_ratio < 0.1
        or soft_rotation_from_fresh > 15.0
    ):
        break
checkpoint_fields = {
    "state": current_state,
    "n6_ordered_branch_index": n6_branch,
    "branch_reference": branch_reference,
    "soft_right_direction": soft_right_direction,
}
accepted_continuation_step = any(
    record.get("accepted") is True for record in continuation
)
if not accepted_continuation_step:
    # A rejected proposal leaves the exact center unchanged.  Retain its
    # same-state paired slopes instead of forcing an unnecessary expensive
    # refresh or silently replacing them with proposal/Broyden curvature.
    checkpoint_fields.update({
        "paired_j_full": j_full,
        "paired_j_half": j_half,
        "paired_jacobian": j,
        "recent_accepted_states": recent_accepted_states,
        "continuous_newton_solver_time": continuous_newton_solver_time,
        "continuous_newton_dt": continuous_newton_dt,
    })
np.savez_compressed(CHECKPOINT, **checkpoint_fields)

out = {
    "order": ORDER,
    "points": POINTS,
    "n6_ordered_branch_index": n6_branch,
    "n6_ordered_branch_selector": "VALIDATED_REPAIRED_EVENT_RECORD",
    "ordered_event_eigenvalue_evaluation": (
        ORDERED_EVENT_EIGENVALUE_EVALUATION
    ),
    "center_source": center_source,
    "proposal_steps_requested": PROPOSAL_STEPS,
    "proposal_mode": PROPOSAL_MODE,
    "lambda_diagnostics_at_fresh_paired_center": lambda_diagnostics,
    "soft_scalar_profile_at_fresh_paired_center": soft_scalar_profile,
    "soft_right_rotation_from_previous_fresh_degrees": (
        soft_rotation_from_previous
    ),
    "Broyden_refresh_controls": {
        "normalized_secant_defect_maximum": 0.5,
        "actual_to_predicted_reduction_ratio_minimum": 0.1,
        "soft_right_rotation_maximum_degrees": 15.0,
        "controls_are_proposal_reliability_only": True,
        "physical_acceptance_gate_changed": False,
    },
    "fresh_paired_normal_certificate_diagnostic": {
        "row_rank": int(np.count_nonzero(
            normal_singular
            > np.finfo(float).eps * max(j.shape) * normal_singular[0]
        )),
        "row_count": int(j.shape[0]),
        "smallest_normal_singular_value": float(normal_singular[-1]),
        "normal_right_inverse_bound": normal_inverse_bound,
        "normal_Newton_correction_norm": normal_newton_norm,
        "full_F12_directional_nonlinear_majorant_measurements": (
            normal_newton_curvature
        ),
        "local_nonlinear_majorant_measurement": (
            local_nonlinear_majorant_measurement
        ),
        "Newton_Kantorovich_product_measurement": nk_product_measurement,
        "measured_discriminant_positive": nk_product_measurement < 1.0,
        "measurement_is_rigorous_full_ball_majorant": False,
        "radii_certificate_promoted": False,
    },
    "center_rows": int(center_rows.size),
    "center_norm": float(np.linalg.norm(center_rows)),
    "center_low_norm": float(np.linalg.norm(r_low)),
    "center_high_norm": float(np.linalg.norm(r_high)),
    "ordered_center_lambda": ordered_lambda(center[:sdim]),
    "ordered_center_neighbor_gap": transport_neighbor_gap,
    "ordered_scale": ordered_scale,
    "jacobian_full_to_half_norm": float(np.linalg.norm(j_half - j_full, ord=2)),
    "jacobian_richardson_to_half_norm": float(np.linalg.norm(j - j_half, ord=2)),
    "jhh_singular_values": sh.tolist(),
    "jhh_right_inverse_defect": float(np.linalg.norm(jhh @ jhh_right - np.eye(len(high_rows)), ord=2)),
    "jll_singular_values": s0.tolist(),
    "minimum_abs_soft_denominator": float(abs(data[imin, 0])),
    "minimum_abs_soft_denominator_t": float(grid[imin]),
    "soft_source_at_minimum": float(data[imin, 1]),
    "minimum_hard_singular": float(np.min(data[:, 2])),
    "minimum_full_schur_singular": float(data[ismin, 3]),
    "minimum_full_schur_singular_t": float(grid[ismin]),
    "minimum_reduced_normal_section_singular": float(data[irsmin, 4]),
    "minimum_reduced_normal_section_singular_t": float(grid[irsmin]),
    "affine_schur_interval_cover": {
        "accepted_interval_count": len(affine_cover),
        "rejected_interval_count": len(affine_rejected),
        "minimum_certified_hard_gap": min(
            row["hard_gap_lower"] for row in affine_cover
        ) if affine_cover else None,
        "minimum_certified_full_gap": min(
            row["reduced_full_gap_lower"] for row in affine_cover
        ) if affine_cover else None,
        "minimum_certified_soft_denominator": min(
            row["soft_denominator_lower"] for row in affine_cover
        ) if affine_cover else None,
        "maximum_interval_width": max(
            row["right"] - row["left"] for row in affine_cover
        ) if affine_cover else None,
        "first_interval": affine_cover[0] if affine_cover else None,
        "last_interval": affine_cover[-1] if affine_cover else None,
        "cover_sha256": affine_cover_digest,
        "scope": "FIXED_PAIRED_RICHARDSON_LINEARIZATION_ONLY",
    },
    "endpoint_data": {"t0": data[0].tolist(), "t1": data[-1].tolist()},
    "correction_action_norm": float(np.linalg.norm(delta)),
    "trial_exact_norm": float(np.linalg.norm(trial_rows)),
    "trial_exact_high_norm": float(np.linalg.norm(trial_rows[high_rows])),
    "trial_event_eta": _eta_legendre_minimum(ORDER, eq, em, points=2000)["minimum"],
    "trial_child_eta": _eta_legendre_minimum(ORDER, cq, cm, points=2000)["minimum"],
    "line_trials": line_trials,
    "directional_curvature": directional_curvature,
    "exact_merit_continuation": continuation,
    "continuation_final_norm": float(np.linalg.norm(current_rows)),
    "continuation_checkpoint": str(CHECKPOINT),
    "certification_status": {
        "exact_joint_weak_root_landed": bool(
            np.linalg.norm(current_rows) < 1.0e-9
        ),
        "fixed_paired_linear_schur_homotopy_enclosed": bool(
            affine_cover and not affine_rejected
        ),
        "nonlinear_segment_radii_polynomials_certified": False,
        "eta_event_Dirac_persistence_ball_transfer_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "first_rigorous_certification_obstruction": (
            "ACTION_ANALYTIC_FOURTH_VARIATION_AND_BORDERED_LIFT_"
            "INVERSE_MAJORANT_ON_EACH_FINITE_CHORD_BALL,_INCLUDING_"
            "THE_ORDERED_EVENT_EIGENPROJECTOR,_STATE_DEPENDENT_"
            "CANONICAL_MOMENTUM_LIFT,_EXISTING_QUADRATURE_"
            "CONSISTENCY_DEFECT,_AND_ETA_DIRAC_EVENT_PERSISTENCE_"
            "NEIGHBORHOOD_LIPSCHITZ_RADII"
        ),
        "paired_slopes_are_proposal_curvature_only": True,
        "new_physics_equation_gate_constraint_or_selector": False,
    },
}
RESULT.write_text(json.dumps(out, indent=2), encoding="utf-8")
checkpoint_payload = np.load(CHECKPOINT)
checkpoint_state = np.asarray(checkpoint_payload["state"], dtype=float)
checkpoint_branch = np.asarray(
    checkpoint_payload["branch_reference"], dtype=float
)
artifact_payload = {
    "artifact": "BHSM_N6_N12_JOINT_SCHUR_CHORD_COVER",
    "classification": (
        "UNCHANGED_JOINT_WEAK_RESIDUAL_CHORD_CONTINUATION_AND_"
        "FIXED_LINEAR_SCHUR_INTERVAL_COVER;_NONLINEAR_ACTION_NORM_"
        "RADII_CERTIFICATE_REMAINS_FAIL_CLOSED"
    ),
    "finite_anchor_history": {
        "zero_padded_repaired_N6_in_N12_exact_joint_norm": (
            0.3322528867427651
        ),
        "first_refreshed_center_exact_joint_norm": 0.04485300994713792,
        "second_refreshed_center_exact_joint_norm": 3.325651595441319e-5,
        "linear_bridge_lower_bounds_at_zero_padded_anchor": {
            "hard_gap": 0.00994932347,
            "full_Schur_gap": 0.00371468430,
            "soft_denominator": 0.00559736955,
        },
        "one_N6_centered_ball_classified_as_retained_action_obstruction": (
            False
        ),
        "one_N6_centered_ball_classification": "LOCAL_BASIN_FAILURE_ONLY",
    },
    "latest_probe": out,
    "latest_checkpoint_binary64_hex": {
        "event": [float(value).hex() for value in checkpoint_state[:sdim]],
        "child": [float(value).hex() for value in checkpoint_state[sdim:]],
        "transported_ordered_event_eigenline": [
            float(value).hex() for value in checkpoint_branch
        ],
    },
    "measurement_center_binary64_hex": {
        "event": [float(value).hex() for value in center[:sdim]],
        "child": [float(value).hex() for value in center[sdim:]],
        "transported_ordered_event_eigenline": [
            float(value).hex() for value in branch_reference
        ],
    },
    "unchanged_joint_weak_residual_used": True,
    "paired_slopes_promoted_as_physics": False,
    "higher_N_complete_child_promoted": False,
    "frozen_predictions_touched": False,
    "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
    "FULL_BHSM_COMPLETE": False,
}
ARTIFACT.write_text(
    json.dumps(artifact_payload, sort_keys=True, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
print(json.dumps(out, indent=2))
