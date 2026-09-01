"""Analytic action-coordinate Jacobian of the retained event/child reset.

The reset residual has 57 rows: 25 event constraints, the selected ordered
event eigenvalue, four boundary-matching rows, 25 child constraints, and two
canonical-momentum rows.  This module differentiates every row from the
retained action jet and its already-materialized third variation.  The four
normalization matrices remain fixed by the existing N6-to-N12 reset chart.
"""

from __future__ import annotations

from decimal import Decimal, localcontext

import numpy as np

from bhsm.interface.aether_canonical_momentum_action_jacobian import (
    canonical_momentum_action_jacobian,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _attachment_jacobian_at_order,
    _canonical_pair_at_order,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_high_precision_velocity_jet import (
    high_precision_canonical_momentum_from_blocks,
    high_precision_constraint_residual_from_blocks,
    high_precision_ordered_eigenpair_from_blocks,
    high_precision_velocity_jet_blocks,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


def _symmetric_power(matrix: np.ndarray, power: float) -> np.ndarray:
    """Return a symmetric spectral power of a positive definite matrix."""
    values, vectors = np.linalg.eigh(np.asarray(matrix, dtype=float))
    if float(np.min(values)) <= 0.0:
        raise np.linalg.LinAlgError("positive normalization Gram required")
    return vectors @ np.diag(values**power) @ vectors.T


def _decimal_linear_solve(
    matrix: list[list[Decimal]],
    right_hand_side: list[Decimal],
) -> list[Decimal]:
    """Solve one small dense Decimal system with partial pivoting."""
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
            raise np.linalg.LinAlgError("singular selected-eigenline complement")
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


def _decimal_solve_multiple(
    matrix: np.ndarray | list[list[Decimal]],
    right: np.ndarray | list[list[Decimal]],
) -> list[list[Decimal]]:
    """Partial-pivoted Decimal solve with one or more right-hand sides."""
    if isinstance(matrix, np.ndarray):
        coefficients = [[
            Decimal.from_float(float(value)) for value in row
        ] for row in matrix]
    else:
        coefficients = [row[:] for row in matrix]
    if isinstance(right, np.ndarray):
        rhs = [[
            Decimal.from_float(float(value)) for value in row
        ] for row in right]
    else:
        rhs = [row[:] for row in right]
    size = len(coefficients)
    columns = len(rhs[0])
    for pivot_column in range(size):
        pivot = max(
            range(pivot_column, size),
            key=lambda row: abs(coefficients[row][pivot_column]),
        )
        if pivot != pivot_column:
            coefficients[pivot_column], coefficients[pivot] = (
                coefficients[pivot], coefficients[pivot_column]
            )
            rhs[pivot_column], rhs[pivot] = rhs[pivot], rhs[pivot_column]
        diagonal = coefficients[pivot_column][pivot_column]
        if diagonal == 0:
            raise np.linalg.LinAlgError("singular Decimal system")
        for row in range(pivot_column + 1, size):
            factor = coefficients[row][pivot_column] / diagonal
            if factor == 0:
                continue
            coefficients[row][pivot_column] = Decimal(0)
            for column in range(pivot_column + 1, size):
                coefficients[row][column] -= (
                    factor * coefficients[pivot_column][column]
                )
            for rhs_column in range(columns):
                rhs[row][rhs_column] -= factor * rhs[pivot_column][rhs_column]
    solution = [[Decimal(0) for _ in range(columns)] for _ in range(size)]
    for row in range(size - 1, -1, -1):
        for rhs_column in range(columns):
            remainder = rhs[row][rhs_column] - sum(
                coefficients[row][column] * solution[column][rhs_column]
                for column in range(row + 1, size)
            )
            solution[row][rhs_column] = (
                remainder / coefficients[row][row]
            )
    return solution


def _decimal_matmul(
    left: list[list[Decimal]],
    right: list[list[Decimal]],
) -> list[list[Decimal]]:
    return [[
        sum(
            left[row][inner] * right[inner][column]
            for inner in range(len(right))
        )
        for column in range(len(right[0]))
    ] for row in range(len(left))]


def _decimal_canonical_momentum(
    order: int,
    state: np.ndarray,
    *,
    points: int,
) -> np.ndarray:
    """Evaluate the retained Hessian-minimal momentum with Decimal solves."""
    qdim = dimensions(order)["coordinates"]
    jet = exact_full_action_jet_at_state(
        order,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=points,
    )
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    boundary = _attachment_jacobian_at_order(order, state[:qdim])
    form = hessian[qdim:2 * qdim, qdim:2 * qdim]
    constraints = hessian[2 * qdim:, qdim:2 * qdim]
    combined = np.vstack((boundary, constraints))
    with localcontext() as context:
        context.prec = 80
        inverse_times = _decimal_solve_multiple(form, combined.T)
        combined_decimal = [[
            Decimal.from_float(float(value)) for value in row
        ] for row in combined]
        compliance = _decimal_matmul(combined_decimal, inverse_times)
        target = [[Decimal(0), Decimal(0)] for _ in range(len(compliance))]
        target[0][0] = Decimal(1)
        target[1][1] = Decimal(1)
        compliance_solution = _decimal_solve_multiple(compliance, target)
        lift = _decimal_matmul(inverse_times, compliance_solution)
        velocity_gradient = [
            Decimal.from_float(float(value))
            for value in gradient[qdim:2 * qdim]
        ]
        momentum = [
            sum(
                lift[row][column] * velocity_gradient[row]
                for row in range(qdim)
            )
            for column in range(2)
        ]
    return np.asarray([float(value) for value in momentum])


def _refined_selected_eigenvalue(
    hessian: np.ndarray,
    estimate: float,
    vector: np.ndarray,
) -> float:
    """Evaluate an already-selected simple eigenvalue by a Decimal Schur root."""
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
            inverse_coupling = _decimal_linear_solve(shifted, coupling)
            value = diagonal - eigenvalue - sum(
                left * right
                for left, right in zip(coupling, inverse_coupling)
            )
            derivative = -Decimal(1) - sum(
                entry * entry for entry in inverse_coupling
            )
            correction = value / derivative
            eigenvalue -= correction
            if abs(correction) < Decimal("1e-60"):
                break
    return float(eigenvalue)


def full_reset_residual(
    order: int,
    joint_state: np.ndarray,
    state_weights: np.ndarray,
    branch_reference: np.ndarray,
    ordered_scale: float,
    normalization_coordinates: np.ndarray,
    *,
    points: int = 96,
    refine_ordered_eigenvalue: bool = True,
    high_precision_momentum: bool = False,
    high_precision_action: bool = False,
) -> tuple[np.ndarray, int]:
    """Evaluate the unchanged normalized 57-row event/child reset residual."""
    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    joint_state = np.asarray(joint_state, dtype=float)
    state_weights = np.asarray(state_weights, dtype=float)
    normalization_coordinates = np.asarray(
        normalization_coordinates, dtype=float
    )
    if joint_state.shape != (2 * state_dimension,):
        raise ValueError("joint state has the wrong event/child dimension")
    event = joint_state[:state_dimension]
    child = joint_state[state_dimension:]
    event_blocks = None
    child_blocks = None
    if high_precision_action:
        event_blocks = high_precision_velocity_jet_blocks(
            order,
            event[:qdim],
            event[qdim:2 * qdim],
            event[2 * qdim:],
            points=points,
            precision=60,
        )
        child_blocks = high_precision_velocity_jet_blocks(
            order,
            child[:qdim],
            child[qdim:2 * qdim],
            child[2 * qdim:],
            points=points,
            precision=60,
        )
        event_constraint = high_precision_constraint_residual_from_blocks(
            event[qdim:2 * qdim], event_blocks
        )
        child_constraint = high_precision_constraint_residual_from_blocks(
            child[qdim:2 * qdim], child_blocks
        )
        ordered = high_precision_ordered_eigenpair_from_blocks(
            event_blocks, branch_reference, precision=60
        )
        selected = int(ordered["index"])
        eigenvalue = float(ordered["eigenvalue"])
    else:
        event_constraint = constraint_residual(
            order,
            event[:qdim],
            event[qdim:2 * qdim],
            event[2 * qdim:],
            points=points,
        )
        child_constraint = constraint_residual(
            order,
            child[:qdim],
            child[qdim:2 * qdim],
            child[2 * qdim:],
            points=points,
        )
        jet = exact_full_action_jet_at_state(
            order,
            event[:qdim],
            event[qdim:2 * qdim],
            event[2 * qdim:],
            points=points,
        )
        reduced_hessian = np.asarray(jet.hessian, dtype=float)[qdim:, qdim:]
        values, vectors = np.linalg.eigh(reduced_hessian)
        selected = int(np.argmax(np.abs(vectors.T @ branch_reference)))
        eigenvalue = float(values[selected])
        if refine_ordered_eigenvalue:
            eigenvalue = _refined_selected_eigenvalue(
                reduced_hessian, eigenvalue, vectors[:, selected]
            )

    q_weights = state_weights[:qdim]
    multiplier_weights = state_weights[2 * qdim:]
    trace = _trace_jacobian_at_order(order)
    normalization_attachment = _attachment_jacobian_at_order(
        order, normalization_coordinates
    )
    normalization_boundary = np.vstack((
        trace,
        normalization_attachment[1],
    ))
    boundary_inverse_sqrt = _symmetric_power(
        normalization_boundary
        @ np.diag(1.0 / q_weights**2)
        @ normalization_boundary.T,
        -0.5,
    )
    boundary_raw = np.concatenate((
        trace @ (child[:qdim] - event[:qdim]),
        [
            _attachment_coordinates_at_order(order, child[:qdim])[1]
            - _attachment_coordinates_at_order(order, event[:qdim])[1]
        ],
    ))
    if high_precision_action:
        if event_blocks is None or child_blocks is None:
            raise RuntimeError("high-precision sector blocks were not built")
        event_momentum = high_precision_canonical_momentum_from_blocks(
            order,
            event[:qdim],
            event_blocks,
            precision=60,
        )
        child_momentum = high_precision_canonical_momentum_from_blocks(
            order,
            child[:qdim],
            child_blocks,
            precision=60,
        )
    elif high_precision_momentum:
        event_momentum = _decimal_canonical_momentum(
            order, event, points=points
        )
        child_momentum = _decimal_canonical_momentum(
            order, child, points=points
        )
    else:
        event_momentum = _canonical_pair_at_order(
            order,
            event[:qdim],
            event[qdim:2 * qdim],
            event[2 * qdim:],
            points=points,
        )[0]
        child_momentum = _canonical_pair_at_order(
            order,
            child[:qdim],
            child[qdim:2 * qdim],
            child[2 * qdim:],
            points=points,
        )[0]
    momentum_sqrt = _symmetric_power(
        normalization_attachment @ normalization_attachment.T,
        0.5,
    )
    rows = np.concatenate((
        event_constraint[:mdim] / multiplier_weights,
        event_constraint[mdim:],
        [eigenvalue / ordered_scale],
        boundary_inverse_sqrt @ boundary_raw,
        child_constraint[:mdim] / multiplier_weights,
        child_constraint[mdim:],
        momentum_sqrt @ (child_momentum - event_momentum),
    ))
    if rows.shape != (57,):
        raise RuntimeError("assembled reset residual has the wrong shape")
    return rows, selected


def sector_constraint_action_jacobian(
    order: int,
    state: np.ndarray,
    state_weights: np.ndarray,
    *,
    points: int = 96,
) -> np.ndarray:
    """Differentiate the 24 multiplier constraints and canonical energy."""
    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    state = np.asarray(state, dtype=float)
    state_weights = np.asarray(state_weights, dtype=float)
    if state.shape != (state_dimension,):
        raise ValueError("state has the wrong retained-action dimension")
    if state_weights.shape != (state_dimension,):
        raise ValueError("state weights have the wrong dimension")

    jet = exact_full_action_jet_at_state(
        order,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=points,
    )
    gradient_action = np.asarray(jet.gradient, dtype=float) / state_weights
    hessian_action = (
        np.asarray(jet.hessian, dtype=float)
        / state_weights[:, None]
        / state_weights[None, :]
    )
    multiplier_rows = hessian_action[2 * qdim:]

    velocity_contraction = np.zeros(state_dimension)
    velocity_contraction[qdim:2 * qdim] = state[qdim:2 * qdim]
    velocity_selector = np.zeros((state_dimension, state_dimension))
    velocity_selector[qdim:2 * qdim, qdim:2 * qdim] = np.eye(qdim)
    energy_row = (
        hessian_action @ velocity_contraction
        + velocity_selector.T @ gradient_action
        - gradient_action
    )
    return np.vstack((multiplier_rows, energy_row))


def selected_ordered_event_action_gradient(
    order: int,
    event_state: np.ndarray,
    event_third_action: np.ndarray,
    state_weights: np.ndarray,
    branch_reference: np.ndarray,
    ordered_scale: float,
    *,
    points: int = 96,
) -> tuple[np.ndarray, int]:
    """Differentiate the transported simple eigenvalue in action coordinates."""
    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    event_state = np.asarray(event_state, dtype=float)
    event_third_action = np.asarray(event_third_action, dtype=float)
    state_weights = np.asarray(state_weights, dtype=float)
    branch_reference = np.asarray(branch_reference, dtype=float)
    if event_state.shape != (state_dimension,):
        raise ValueError("event state has the wrong dimension")
    if event_third_action.shape != (state_dimension,) * 3:
        raise ValueError("event third variation has the wrong dimension")
    if branch_reference.shape != (state_dimension - qdim,):
        raise ValueError("branch reference has the wrong reduced dimension")
    if ordered_scale <= 0.0:
        raise ValueError("positive ordered-event scale required")

    jet = exact_full_action_jet_at_state(
        order,
        event_state[:qdim],
        event_state[qdim:2 * qdim],
        event_state[2 * qdim:],
        points=points,
    )
    reduced_hessian = np.asarray(jet.hessian, dtype=float)[qdim:, qdim:]
    _, vectors = np.linalg.eigh(reduced_hessian)
    selected = int(np.argmax(np.abs(vectors.T @ branch_reference)))
    selected_action = np.zeros(state_dimension)
    selected_action[qdim:] = (
        state_weights[qdim:] * vectors[:, selected]
    )
    gradient = np.einsum(
        "a,b,abi->i",
        selected_action,
        selected_action,
        event_third_action,
    ) / ordered_scale
    return gradient, selected


def full_reset_action_jacobian(
    order: int,
    joint_state: np.ndarray,
    event_third_action: np.ndarray,
    child_third_action: np.ndarray,
    state_weights: np.ndarray,
    branch_reference: np.ndarray,
    ordered_scale: float,
    normalization_coordinates: np.ndarray,
    *,
    points: int = 96,
) -> tuple[np.ndarray, int]:
    """Return the full retained reset Jacobian and selected branch index.

    ``normalization_coordinates`` is the fixed action-owned N6 child embedded
    into the current Galerkin order.  It fixes both the boundary trace and
    momentum row normalizations exactly as in the retained reset residual.
    """
    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    joint_state = np.asarray(joint_state, dtype=float)
    state_weights = np.asarray(state_weights, dtype=float)
    normalization_coordinates = np.asarray(
        normalization_coordinates, dtype=float
    )
    if joint_state.shape != (2 * state_dimension,):
        raise ValueError("joint state has the wrong event/child dimension")
    if state_weights.shape != (state_dimension,):
        raise ValueError("state weights have the wrong dimension")
    if normalization_coordinates.shape != (qdim,):
        raise ValueError("normalization coordinates have the wrong dimension")

    event = joint_state[:state_dimension]
    child = joint_state[state_dimension:]
    event_constraints = sector_constraint_action_jacobian(
        order, event, state_weights, points=points
    )
    child_constraints = sector_constraint_action_jacobian(
        order, child, state_weights, points=points
    )
    ordered_row, selected = selected_ordered_event_action_gradient(
        order,
        event,
        event_third_action,
        state_weights,
        branch_reference,
        ordered_scale,
        points=points,
    )

    q_weights = state_weights[:qdim]
    trace = _trace_jacobian_at_order(order)
    normalization_attachment = _attachment_jacobian_at_order(
        order, normalization_coordinates
    )
    normalization_boundary = np.vstack((
        trace,
        normalization_attachment[1],
    ))
    boundary_inverse_sqrt = _symmetric_power(
        normalization_boundary
        @ np.diag(1.0 / q_weights**2)
        @ normalization_boundary.T,
        -0.5,
    )
    event_boundary = np.vstack((
        trace,
        _attachment_jacobian_at_order(order, event[:qdim])[1],
    ))
    child_boundary = np.vstack((
        trace,
        _attachment_jacobian_at_order(order, child[:qdim])[1],
    ))
    boundary_rows = np.zeros((4, 2 * state_dimension))
    boundary_rows[:, :qdim] = (
        -boundary_inverse_sqrt @ event_boundary / q_weights[None, :]
    )
    boundary_rows[:, state_dimension:state_dimension + qdim] = (
        boundary_inverse_sqrt @ child_boundary / q_weights[None, :]
    )

    event_momentum = canonical_momentum_action_jacobian(
        order,
        event,
        event_third_action,
        state_weights,
        points=points,
    )
    child_momentum = canonical_momentum_action_jacobian(
        order,
        child,
        child_third_action,
        state_weights,
        points=points,
    )
    momentum_sqrt = _symmetric_power(
        normalization_attachment @ normalization_attachment.T,
        0.5,
    )
    momentum_rows = np.hstack((
        -momentum_sqrt @ event_momentum,
        momentum_sqrt @ child_momentum,
    ))

    event_rows = np.hstack((
        event_constraints,
        np.zeros((mdim + 1, state_dimension)),
    ))
    ordered_full = np.concatenate((ordered_row, np.zeros(state_dimension)))
    child_rows = np.hstack((
        np.zeros((mdim + 1, state_dimension)),
        child_constraints,
    ))
    jacobian = np.vstack((
        event_rows,
        ordered_full[None],
        boundary_rows,
        child_rows,
        momentum_rows,
    ))
    expected_rows = 2 * (mdim + 1) + 1 + 4 + 2
    if jacobian.shape != (expected_rows, 2 * state_dimension):
        raise RuntimeError("assembled reset Jacobian has the wrong shape")
    return jacobian, selected
