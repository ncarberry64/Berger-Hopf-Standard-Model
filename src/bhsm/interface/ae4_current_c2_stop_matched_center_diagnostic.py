"""Stop-matched proper-time center path for the AE4 operator diagnostic."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.aether_cancelled_arc_proper_time_pullback import (
    assemble_cancelled_arc_proper_time_coefficient_first_jet,
)


CLASSIFICATION = "AE4_CURRENT_C2_STOP_MATCHED_CENTER_DIAGNOSTIC"


def stop_matched_center_proper_time_path(
    *,
    arc_nodes: np.ndarray,
    states: np.ndarray,
    signed_descriptor: np.ndarray,
    cancelled_field_action_norm: np.ndarray,
    cancelled_norm_state_gradient_action: np.ndarray,
    cancelled_norm_descriptor_derivative: np.ndarray,
    state_weights: np.ndarray,
    stop_arc_coordinate: float,
) -> dict[str, Any]:
    """Truncate a numerical center at a representative canonical stop.

    The state and norm data are linearly interpolated at the supplied stop
    coordinate and the action-owned stop descriptor is set to zero.  This is
    a center diagnostic, not an outward shadowing or root certificate.
    """

    arc = np.asarray(arc_nodes, dtype=float)
    state = np.asarray(states, dtype=float)
    descriptor = np.asarray(signed_descriptor, dtype=float)
    norm = np.asarray(cancelled_field_action_norm, dtype=float)
    norm_state = np.asarray(cancelled_norm_state_gradient_action, dtype=float)
    norm_descriptor = np.asarray(cancelled_norm_descriptor_derivative, dtype=float)
    weights = np.asarray(state_weights, dtype=float)
    stop = float(stop_arc_coordinate)
    if (
        arc.ndim != 1
        or state.shape != (arc.size, 98)
        or descriptor.shape != arc.shape
        or norm.shape != arc.shape
        or norm_state.shape != state.shape
        or norm_descriptor.shape != arc.shape
        or weights.shape != (98,)
        or arc.size < 2
        or not np.all(np.isfinite(arc))
        or not np.all(np.diff(arc) > 0.0)
        or not np.all(np.isfinite(state))
        or not np.all(np.isfinite(descriptor))
        or not np.all(np.isfinite(norm))
        or np.any(norm <= 0.0)
        or not np.all(np.isfinite(norm_state))
        or not np.all(np.isfinite(norm_descriptor))
        or not np.all(np.isfinite(weights))
        or np.any(weights <= 0.0)
        or not arc[0] < stop < arc[-1]
    ):
        raise ValueError("aligned finite center history and interior stop required")
    right = int(np.searchsorted(arc, stop, side="right"))
    left = right - 1
    fraction = (stop - arc[left]) / (arc[right] - arc[left])

    def interpolate(values: np.ndarray) -> np.ndarray:
        return values[left] + fraction * (values[right] - values[left])

    stopped_arc = np.concatenate((arc[:right], np.asarray((stop,))))
    stopped_states = np.vstack((state[:right], interpolate(state)))
    stopped_descriptor = np.concatenate((descriptor[:right], np.zeros(1)))
    stopped_norm = np.concatenate((norm[:right], np.atleast_1d(interpolate(norm))))
    stopped_norm_state = np.vstack((norm_state[:right], interpolate(norm_state)))
    stopped_norm_descriptor = np.concatenate(
        (norm_descriptor[:right], np.atleast_1d(interpolate(norm_descriptor)))
    )
    count = stopped_arc.size
    pullback = assemble_cancelled_arc_proper_time_coefficient_first_jet(
        arc_nodes=stopped_arc,
        states=stopped_states,
        state_action_first_jet=np.empty((count, 98, 0), dtype=float),
        state_weights=weights,
        signed_descriptor=stopped_descriptor,
        signed_descriptor_first_jet=np.empty((count, 0), dtype=float),
        cancelled_field_action_norm=stopped_norm,
        cancelled_norm_state_gradient_action=stopped_norm_state,
        cancelled_norm_descriptor_derivative=stopped_norm_descriptor,
    )
    return {
        **pullback,
        "classification": CLASSIFICATION,
        "stop_arc_coordinate": stop,
        "source_cell": [left, right],
        "source_cell_fraction": float(fraction),
        "terminal_descriptor": 0.0,
        "representative_center_only": True,
        "outward_interval_shadowing_authority": False,
    }


def refine_piecewise_linear_path(
    log_radius: np.ndarray,
    proper_times: np.ndarray,
    factor: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Subdivide a piecewise-linear coefficient path without changing time."""

    x = np.asarray(log_radius, dtype=float)
    tau = np.asarray(proper_times, dtype=float)
    refinement = int(factor)
    if (
        x.ndim != 1
        or tau.shape != x.shape
        or x.size < 2
        or refinement < 1
        or not np.all(np.isfinite(x))
        or not np.all(np.isfinite(tau))
        or not np.all(np.diff(tau) > 0.0)
    ):
        raise ValueError("finite proper-time path and positive refinement required")
    nodes = [float(x[0])]
    durations: list[float] = []
    for index, duration in enumerate(np.diff(tau)):
        for substep in range(1, refinement + 1):
            fraction = substep / refinement
            nodes.append(float(x[index] + fraction * (x[index + 1] - x[index])))
            durations.append(float(duration / refinement))
    return np.asarray(nodes), np.asarray(durations)


__all__ = [
    "CLASSIFICATION",
    "refine_piecewise_linear_path",
    "stop_matched_center_proper_time_path",
]
