"""Signed reverse pullback for a finite C2 coefficient-history functional."""

from __future__ import annotations

from typing import Any

import numpy as np


def signed_coefficient_history_adjoint(
    *,
    transition_jacobians_action: np.ndarray,
    node_log_radius_covectors_action_dual: np.ndarray,
    segment_duration_covectors_action_dual: np.ndarray,
    D_log_radius_functional: np.ndarray,
    D_proper_duration_functional: np.ndarray,
    terminal_state_covector_action_dual: np.ndarray | None = None,
) -> dict[str, Any]:
    """Pull a signed coefficient cotangent to the first history state.

    Let ``Y[j+1]=Phi[j](Y[j])``.  The caller supplies the exact first
    derivatives of the segment maps, node log radii, and segment proper
    durations in the stored action coordinates.  If ``C(x,h)`` is any scalar
    finite-core response, the recurrence is

    ``p[N]=C_x[N] x_Y[N] + g_T`` and

    ``p[j]=C_x[j] x_Y[j] + C_h[j] h_Y[j] + Phi_Y[j]^T p[j+1]``.

    No full Euler--Dirac inverse, forward Jacobi column family, or physical
    reset representative is selected by this algebraic pullback.
    """

    transitions = np.asarray(transition_jacobians_action, dtype=float)
    x_covectors = np.asarray(
        node_log_radius_covectors_action_dual, dtype=float
    )
    h_covectors = np.asarray(
        segment_duration_covectors_action_dual, dtype=float
    )
    d_x = np.asarray(D_log_radius_functional, dtype=float)
    d_h = np.asarray(D_proper_duration_functional, dtype=float)
    if transitions.ndim != 3 or transitions.shape[1] != transitions.shape[2]:
        raise ValueError("transition Jacobians must have shape (segments,n,n)")
    segments, state_dimension, _ = transitions.shape
    if x_covectors.shape != (segments + 1, state_dimension):
        raise ValueError("node log-radius covectors have the wrong shape")
    if h_covectors.shape != (segments, state_dimension):
        raise ValueError("segment-duration covectors have the wrong shape")
    if d_x.shape != (segments + 1,) or d_h.shape != (segments,):
        raise ValueError("coefficient cotangents have the wrong shape")
    terminal = (
        np.zeros(state_dimension)
        if terminal_state_covector_action_dual is None
        else np.asarray(terminal_state_covector_action_dual, dtype=float)
    )
    if terminal.shape != (state_dimension,):
        raise ValueError("terminal covector has the wrong shape")
    if not all(
        np.all(np.isfinite(value))
        for value in (transitions, x_covectors, h_covectors, d_x, d_h, terminal)
    ):
        raise ValueError("finite signed-adjoint inputs required")

    local_covectors = d_x[:, None] * x_covectors
    local_covectors[:-1] += d_h[:, None] * h_covectors
    adjoint_nodes = np.empty_like(local_covectors)
    adjoint_nodes[-1] = local_covectors[-1] + terminal
    for index in range(segments - 1, -1, -1):
        adjoint_nodes[index] = (
            local_covectors[index]
            + transitions[index].T @ adjoint_nodes[index + 1]
        )
    return {
        "initial_state_covector_action_dual": adjoint_nodes[0],
        "adjoint_node_covectors_action_dual": adjoint_nodes,
        "local_node_covectors_action_dual": local_covectors,
        "state_dimension": state_dimension,
        "segment_count": segments,
        "explicit_matrix_inverse_formed": False,
        "forward_Jacobi_columns_formed": False,
    }


__all__ = ["signed_coefficient_history_adjoint"]
