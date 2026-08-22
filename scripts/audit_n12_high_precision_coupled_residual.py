"""Reevaluate the unchanged N12 coupled residual with Decimal lift solves.

The retained action, 57 equations, branch, normalization, and checkpoint are
unchanged.  Only the dense linear algebra used to evaluate the existing
Hessian-minimal boundary lifts is replayed at higher precision.  This audit
tests whether the current binary64 event/momentum floor is evaluation error.
"""

from __future__ import annotations

import hashlib
import json
import os
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
    embed_nested_state,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _attachment_jacobian_at_order,
    _authoritative_n6_event_child_anchor,
    _canonical_pair_at_order,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state as exact_ordered_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
PRECISION = 80
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    ".tmp_direct_n12_exact_identity_constraint_proposal.npz",
))
REFERENCE_RESIDUAL = Path(os.environ.get(
    "BHSM_N12_REFERENCE_RESIDUAL",
    ".tmp_direct_n12_exact_identity_final_residual_2.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_HIGH_PRECISION_RESIDUAL",
    ".tmp_direct_n12_exact_identity_high_precision_residual.json",
))
CROSS_RESOLUTION = Path(
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def d(value: float) -> Decimal:
    return Decimal.from_float(float(value))


def solve_decimal(
    matrix: np.ndarray | list[list[Decimal]],
    right: np.ndarray | list[list[Decimal]],
) -> list[list[Decimal]]:
    """Partial-pivoted Decimal solve with one or more right-hand sides."""

    if isinstance(matrix, np.ndarray):
        a = [[d(value) for value in row] for row in matrix]
    else:
        a = [row[:] for row in matrix]
    if isinstance(right, np.ndarray):
        b = [[d(value) for value in row] for row in right]
    else:
        b = [row[:] for row in right]
    size = len(a)
    columns = len(b[0])
    for pivot_column in range(size):
        pivot = max(
            range(pivot_column, size),
            key=lambda row: abs(a[row][pivot_column]),
        )
        if pivot != pivot_column:
            a[pivot_column], a[pivot] = a[pivot], a[pivot_column]
            b[pivot_column], b[pivot] = b[pivot], b[pivot_column]
        diagonal = a[pivot_column][pivot_column]
        if diagonal == 0:
            raise np.linalg.LinAlgError("singular Decimal system")
        for row in range(pivot_column + 1, size):
            factor = a[row][pivot_column] / diagonal
            if factor == 0:
                continue
            a[row][pivot_column] = Decimal(0)
            for column in range(pivot_column + 1, size):
                a[row][column] -= factor * a[pivot_column][column]
            for rhs_column in range(columns):
                b[row][rhs_column] -= factor * b[pivot_column][rhs_column]
    result = [[Decimal(0) for _ in range(columns)] for _ in range(size)]
    for row in range(size - 1, -1, -1):
        for rhs_column in range(columns):
            remainder = b[row][rhs_column] - sum(
                a[row][column] * result[column][rhs_column]
                for column in range(row + 1, size)
            )
            result[row][rhs_column] = remainder / a[row][row]
    return result


def decimal_matmul(
    left: list[list[Decimal]], right: list[list[Decimal]],
) -> list[list[Decimal]]:
    return [[
        sum(left[row][inner] * right[inner][column]
            for inner in range(len(right)))
        for column in range(len(right[0]))
    ] for row in range(len(left))]


def decimal_boundary_lift(
    form: np.ndarray, boundary: np.ndarray, constraints: np.ndarray,
) -> list[list[Decimal]]:
    combined = np.vstack((boundary, constraints))
    combined_d = [[d(value) for value in row] for row in combined]
    inverse_times = solve_decimal(form, combined.T)
    compliance = decimal_matmul(combined_d, inverse_times)
    target = [[Decimal(0), Decimal(0)] for _ in range(len(compliance))]
    target[0][0] = Decimal(1)
    target[1][1] = Decimal(1)
    compliance_solution = solve_decimal(compliance, target)
    return decimal_matmul(inverse_times, compliance_solution)


def decimal_momentum(state: np.ndarray) -> tuple[list[Decimal], dict[str, float]]:
    qdim = dimensions(ORDER)["coordinates"]
    q = state[:qdim]
    v = state[qdim:2 * qdim]
    m = state[2 * qdim:]
    jet = exact_full_action_jet_at_state(ORDER, q, v, m, points=POINTS)
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    boundary = _attachment_jacobian_at_order(ORDER, q)
    form = hessian[qdim:2 * qdim, qdim:2 * qdim]
    constraints = hessian[2 * qdim:, qdim:2 * qdim]
    lift = decimal_boundary_lift(form, boundary, constraints)
    gradient_d = [d(value) for value in gradient[qdim:2 * qdim]]
    momentum = [
        sum(lift[row][column] * gradient_d[row]
            for row in range(qdim))
        for column in range(2)
    ]
    combined = np.vstack((boundary, constraints))
    inverse_times = np.linalg.solve(form, combined.T)
    compliance = combined @ inverse_times
    return momentum, {
        "velocity_form_condition_number": float(np.linalg.cond(form)),
        "compliance_condition_number": float(np.linalg.cond(compliance)),
        "binary64_lift_norm": float(np.linalg.norm(
            _canonical_pair_at_order(ORDER, q, v, m, points=POINTS)[3]
        )),
    }


def selected_decimal_eigenvalue(
    state: np.ndarray, reference: np.ndarray,
) -> tuple[Decimal, int, float]:
    qdim = dimensions(ORDER)["coordinates"]
    hessian = np.asarray(exact_ordered_action_jet_at_state(
        ORDER,
        state[:qdim], state[qdim:2 * qdim], state[2 * qdim:],
        points=POINTS,
    ).hessian, dtype=float)
    values, vectors = np.linalg.eigh(hessian)
    index = int(np.argmax(np.abs(vectors.T @ reference)))
    vector = vectors[:, index]
    pivot = int(np.argmax(np.abs(vector)))
    retained = [item for item in range(hessian.shape[0]) if item != pivot]
    diagonal = d(hessian[pivot, pivot])
    coupling = [d(hessian[item, pivot]) for item in retained]
    complement = [[d(hessian[row, column]) for column in retained]
                  for row in retained]
    eigenvalue = d(values[index])
    for _ in range(6):
        shifted = [[
            complement[row][column]
            - (eigenvalue if row == column else Decimal(0))
            for column in range(len(retained))
        ] for row in range(len(retained))]
        inverse_coupling_matrix = solve_decimal(
            shifted, [[value] for value in coupling]
        )
        inverse_coupling = [row[0] for row in inverse_coupling_matrix]
        value = diagonal - eigenvalue - sum(
            left * right
            for left, right in zip(coupling, inverse_coupling)
        )
        derivative = -Decimal(1) - sum(
            entry * entry for entry in inverse_coupling
        )
        correction = value / derivative
        eigenvalue -= correction
        if abs(correction) < Decimal("1e-65"):
            break
    neighbor_gap = min(
        values[index] - values[index - 1] if index else np.inf,
        values[index + 1] - values[index]
        if index + 1 < values.size else np.inf,
    )
    return eigenvalue, index, float(neighbor_gap)


def symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    return vectors @ np.diag(values ** power) @ vectors.T


def main() -> None:
    checkpoint = np.load(CHECKPOINT)
    state = np.asarray(checkpoint["state"], dtype=float)
    reference = np.asarray(checkpoint["branch_reference"], dtype=float)
    reference /= np.linalg.norm(reference)
    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    sdim = 2 * qdim + mdim
    event = state[:sdim]
    child = state[sdim:]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)

    payload = json.loads(CROSS_RESOLUTION.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    anchor = _authoritative_n6_event_child_anchor(payload)

    def decode(exact: dict) -> tuple[np.ndarray, ...]:
        return tuple(np.asarray([
            float.fromhex(value) for value in exact[name]
        ]) for name in ("coordinates", "velocities", "multipliers"))

    child6 = decode(anchor["child_exact"])
    embedded_child = embed_nested_state(*child6, 6, ORDER)
    trace = _trace_jacobian_at_order(ORDER)
    attachment = _attachment_jacobian_at_order(ORDER, embedded_child[0])
    boundary = np.vstack((trace, attachment[1]))
    boundary_inverse_sqrt = symmetric_power(
        boundary @ np.diag(1.0 / q_weights ** 2) @ boundary.T, -0.5
    )
    momentum_sqrt = symmetric_power(attachment @ attachment.T, 0.5)
    ordered_scale = float(load_reference["ordered_scale"])

    with localcontext() as context:
        context.prec = PRECISION
        event_momentum, event_audit = decimal_momentum(event)
        child_momentum, child_audit = decimal_momentum(child)
        mismatch_decimal = [
            child_momentum[index] - event_momentum[index]
            for index in range(2)
        ]
        event_eigenvalue, branch, neighbor_gap = selected_decimal_eigenvalue(
            event, reference
        )

    e_constraints = constraint_residual(
        ORDER, event[:qdim], event[qdim:2 * qdim], event[2 * qdim:],
        points=POINTS,
    )
    c_constraints = constraint_residual(
        ORDER, child[:qdim], child[qdim:2 * qdim], child[2 * qdim:],
        points=POINTS,
    )
    boundary_rows = np.concatenate((
        trace @ (child[:qdim] - event[:qdim]),
        [_attachment_coordinates_at_order(ORDER, child[:qdim])[1]
         - _attachment_coordinates_at_order(ORDER, event[:qdim])[1]],
    ))
    mismatch = np.asarray([float(value) for value in mismatch_decimal])
    rows = np.concatenate((
        e_constraints[:mdim] / m_weights,
        e_constraints[mdim:],
        [float(event_eigenvalue / d(ordered_scale))],
        boundary_inverse_sqrt @ boundary_rows,
        c_constraints[:mdim] / m_weights,
        c_constraints[mdim:],
        momentum_sqrt @ mismatch,
    ))
    event_binary = _canonical_pair_at_order(
        ORDER, event[:qdim], event[qdim:2 * qdim], event[2 * qdim:],
        points=POINTS,
    )[0]
    child_binary = _canonical_pair_at_order(
        ORDER, child[:qdim], child[qdim:2 * qdim], child[2 * qdim:],
        points=POINTS,
    )[0]
    reference_rows = np.asarray(load_reference["exact_residual_vector"])
    result = {
        "classification": (
            "N12_BINARY64_COUPLED_RESIDUAL_FLOOR_INVALIDATED"
            if np.linalg.norm(rows) < 0.5 * np.linalg.norm(reference_rows)
            else "N12_HIGH_PRECISION_COUPLED_RESIDUAL_REEVALUATED"
        ),
        "order": ORDER,
        "points": POINTS,
        "decimal_precision": PRECISION,
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": sha256(CHECKPOINT),
        "unchanged_57_row_map": True,
        "ordered_branch_index": branch,
        "ordered_neighbor_gap": neighbor_gap,
        "ordered_event_decimal": str(event_eigenvalue),
        "event_momentum_decimal": [str(value) for value in event_momentum],
        "child_momentum_decimal": [str(value) for value in child_momentum],
        "momentum_mismatch_decimal": [str(value) for value in mismatch_decimal],
        "momentum_mismatch_binary64": (child_binary - event_binary).tolist(),
        "momentum_mismatch_binary64_minus_decimal": (
            child_binary - event_binary - mismatch
        ).tolist(),
        "event_lift_audit": event_audit,
        "child_lift_audit": child_audit,
        "binary64_reference_F12_norm": float(np.linalg.norm(reference_rows)),
        "high_precision_lift_F12_norm": float(np.linalg.norm(rows)),
        "high_precision_lift_event_block_norm": float(np.linalg.norm(
            rows[:26]
        )),
        "high_precision_lift_child_block_norm": float(np.linalg.norm(
            rows[26:]
        )),
        "high_precision_lift_momentum_rows": rows[55:57].tolist(),
        "high_precision_residual_vector": rows.tolist(),
        "binary64_minus_high_precision_residual_norm": float(np.linalg.norm(
            reference_rows - rows
        )),
        "new_physics_equation_constraint_gate_scale_or_selector": False,
        "checkpoint_modified": False,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


load_reference = json.loads(REFERENCE_RESIDUAL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
