"""Action-coordinate Jacobian of the retained boundary momentum.

The canonical momentum is the pullback of the velocity covector by the
existing Hessian-minimal boundary lift.  This module differentiates its two
linear solves analytically.  It introduces no finite-difference step and does
not alter the retained action or attachment chart.
"""

from __future__ import annotations

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


def _attachment_action_derivatives(
    order: int,
    coordinates: np.ndarray,
    state_weights: np.ndarray,
) -> np.ndarray:
    """Return ``D B`` for every unit action-coordinate direction."""
    qdim = dimensions(order)["coordinates"]
    state_dimension = state_weights.size
    derivatives = np.zeros((state_dimension, 2, qdim))
    signs = (-1.0) ** np.arange(order)
    boundary_slice = slice(1 + 2 * order, 1 + 3 * order)
    boundary_value = float(np.asarray(coordinates)[boundary_slice] @ signs)
    coefficient = -2.0 / np.cosh(2.0 * boundary_value) ** 2
    for column in range(boundary_slice.start, boundary_slice.stop):
        directional_boundary = signs[column - boundary_slice.start] / state_weights[column]
        derivative_first = np.zeros(qdim)
        derivative_first[boundary_slice] = (
            coefficient * directional_boundary * signs
        )
        derivatives[column, 0] = derivative_first
        derivatives[column, 1] = -derivative_first
    return derivatives


def canonical_momentum_action_jacobian(
    order: int,
    state: np.ndarray,
    third_action: np.ndarray,
    state_weights: np.ndarray,
    *,
    points: int = 96,
) -> np.ndarray:
    """Differentiate the retained two-component momentum in action coordinates.

    Parameters
    ----------
    state:
        Raw ``(q,v,m)`` state.
    third_action:
        Third variation normalized in the same action coordinates as
        ``state_weights``.
    state_weights:
        Diagonal action-coordinate weights, so ``x_action=W*x_raw``.
    """
    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    state_dimension = 2 * qdim + mdim
    state = np.asarray(state, dtype=float)
    state_weights = np.asarray(state_weights, dtype=float)
    third_action = np.asarray(third_action, dtype=float)
    if state.shape != (state_dimension,):
        raise ValueError("state has the wrong retained-action dimension")
    if state_weights.shape != (state_dimension,):
        raise ValueError("state weights have the wrong dimension")
    if third_action.shape != (state_dimension,) * 3:
        raise ValueError("third variation has the wrong dimension")
    if np.any(state_weights <= 0.0):
        raise ValueError("positive action-coordinate weights required")

    q = state[:qdim]
    v = state[qdim:2 * qdim]
    m = state[2 * qdim:]
    jet = exact_full_action_jet_at_state(order, q, v, m, points=points)
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    velocity_form = hessian[qdim:2 * qdim, qdim:2 * qdim]
    constraint_velocity = hessian[2 * qdim:, qdim:2 * qdim]
    boundary = _attachment_jacobian_at_order(order, q)
    combined = np.vstack((boundary, constraint_velocity))
    target = np.zeros((combined.shape[0], 2))
    target[:2] = np.eye(2)

    inverse_times = np.linalg.solve(velocity_form, combined.T)
    compliance = combined @ inverse_times
    compliance_solution = np.linalg.solve(compliance, target)
    lift = inverse_times @ compliance_solution
    velocity_gradient = gradient[qdim:2 * qdim]

    attachment_derivatives = _attachment_action_derivatives(
        order, q, state_weights
    )
    jacobian = np.empty((2, state_dimension))
    weight_outer = state_weights[:, None] * state_weights[None, :]
    for column in range(state_dimension):
        derivative_hessian = third_action[:, :, column] * weight_outer
        derivative_velocity_form = derivative_hessian[
            qdim:2 * qdim, qdim:2 * qdim
        ]
        derivative_constraint_velocity = derivative_hessian[
            2 * qdim:, qdim:2 * qdim
        ]
        derivative_combined = np.vstack((
            attachment_derivatives[column],
            derivative_constraint_velocity,
        ))
        derivative_inverse_times = np.linalg.solve(
            velocity_form,
            derivative_combined.T - derivative_velocity_form @ inverse_times,
        )
        derivative_compliance = (
            derivative_combined @ inverse_times
            + combined @ derivative_inverse_times
        )
        derivative_compliance_solution = np.linalg.solve(
            compliance,
            -derivative_compliance @ compliance_solution,
        )
        derivative_lift = (
            derivative_inverse_times @ compliance_solution
            + inverse_times @ derivative_compliance_solution
        )
        derivative_velocity_gradient = (
            hessian[qdim:2 * qdim, column] / state_weights[column]
        )
        jacobian[:, column] = (
            derivative_lift.T @ velocity_gradient
            + lift.T @ derivative_velocity_gradient
        )
    return jacobian

