"""Pull a normalized cancelled-field history back to physical proper time.

For the retained denominator-free field ``G_theta`` the exact incidence is
``d tau / d theta = N_boundary*s``.  A collocation center propagated with
the normalized field ``G_theta/||G_theta||`` therefore has proper-time
density ``q=N_boundary*s/||G_theta||`` with respect to its stored arc
parameter.  This module performs the moving-duration chain rule without
identifying that arc parameter with proper time.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.interpolate import CubicSpline

from bhsm.interface.aether_forward_c2_geometry_incidence import (
    boundary_geometry_action_covectors,
)


def cancelled_arc_proper_time_density_first_jet(
    *,
    log_boundary_lapse: np.ndarray,
    signed_descriptor: np.ndarray,
    cancelled_field_action_norm: np.ndarray,
    log_boundary_lapse_first_jet: np.ndarray,
    signed_descriptor_first_jet: np.ndarray,
    cancelled_field_action_norm_first_jet: np.ndarray,
) -> dict[str, np.ndarray]:
    """Evaluate ``q=N*s/||G||`` and its regular first jet.

    The product rule is used directly, so the terminal ``s=0`` row never
    divides by the signed descriptor.
    """

    log_lapse = np.asarray(log_boundary_lapse, dtype=float)
    descriptor = np.asarray(signed_descriptor, dtype=float)
    norm = np.asarray(cancelled_field_action_norm, dtype=float)
    log_lapse_first = np.asarray(log_boundary_lapse_first_jet, dtype=float)
    descriptor_first = np.asarray(signed_descriptor_first_jet, dtype=float)
    norm_first = np.asarray(cancelled_field_action_norm_first_jet, dtype=float)
    if (
        log_lapse.ndim != 1
        or descriptor.shape != log_lapse.shape
        or norm.shape != log_lapse.shape
        or log_lapse_first.ndim != 2
        or log_lapse_first.shape[0] != log_lapse.size
        or descriptor_first.shape != log_lapse_first.shape
        or norm_first.shape != log_lapse_first.shape
        or not np.all(np.isfinite(log_lapse))
        or not np.all(np.isfinite(descriptor))
        or not np.all(np.isfinite(norm))
        or not np.all(np.isfinite(log_lapse_first))
        or not np.all(np.isfinite(descriptor_first))
        or not np.all(np.isfinite(norm_first))
        or np.any(descriptor < 0.0)
        or np.any(norm <= 0.0)
    ):
        raise ValueError("finite aligned lapse/descriptor/norm values and first jets required")
    lapse_over_norm = np.exp(log_lapse) / norm
    density = lapse_over_norm * descriptor
    first = (
        lapse_over_norm[:, None] * descriptor_first
        + density[:, None] * (
            log_lapse_first - norm_first / norm[:, None]
        )
    )
    return {
        "proper_time_density": density,
        "proper_time_density_first_jet": first,
    }


def pullback_cancelled_arc_history_to_proper_time(
    *,
    arc_nodes: np.ndarray,
    log_radius: np.ndarray,
    log_radius_arc_first_jet: np.ndarray,
    proper_time_density: np.ndarray,
    proper_time_density_first_jet: np.ndarray,
    terminal_log_radius_first_jet: np.ndarray | None = None,
) -> dict[str, Any]:
    """Return the coefficient path and first jet at fixed normalized proper time.

    All first jets are taken at fixed stored arc coordinate on input.  The
    output uses ``u=tau/T``.  The terminal first jet may be supplied
    separately when a first-hit condition moves the terminal arc coordinate.
    """

    arc = np.asarray(arc_nodes, dtype=float)
    x = np.asarray(log_radius, dtype=float)
    x_first = np.asarray(log_radius_arc_first_jet, dtype=float)
    density = np.asarray(proper_time_density, dtype=float)
    density_first = np.asarray(proper_time_density_first_jet, dtype=float)
    if (
        arc.ndim != 1
        or x.shape != arc.shape
        or density.shape != arc.shape
        or x_first.ndim != 2
        or x_first.shape[0] != arc.size
        or density_first.shape != x_first.shape
        or arc.size < 2
        or not np.all(np.isfinite(arc))
        or not np.all(np.isfinite(x))
        or not np.all(np.isfinite(x_first))
        or not np.all(np.isfinite(density))
        or not np.all(np.isfinite(density_first))
        or not np.all(np.diff(arc) > 0.0)
        or np.any(density[:-1] <= 0.0)
        or density[-1] < 0.0
    ):
        raise ValueError(
            "increasing arc nodes, positive preterminal density, and aligned finite first jets required"
        )
    parameter_count = x_first.shape[1]
    if terminal_log_radius_first_jet is None:
        terminal_first = x_first[-1]
    else:
        terminal_first = np.asarray(terminal_log_radius_first_jet, dtype=float)
        if terminal_first.shape != (parameter_count,) or not np.all(np.isfinite(terminal_first)):
            raise ValueError("one finite terminal log-radius derivative per direction required")

    arc_widths = np.diff(arc)
    proper_at_nodes = np.concatenate((
        np.zeros(1),
        np.cumsum(0.5 * arc_widths * (density[:-1] + density[1:])),
    ))
    duration = float(proper_at_nodes[-1])
    if not np.isfinite(duration) or duration <= 0.0 or not np.all(np.diff(proper_at_nodes) > 0.0):
        raise ArithmeticError("proper-time pullback is not strictly increasing")

    if parameter_count:
        proper_first = np.vstack((
            np.zeros((1, parameter_count)),
            np.cumsum(
                0.5 * arc_widths[:, None]
                * (density_first[:-1] + density_first[1:]),
                axis=0,
            ),
        ))
    else:
        proper_first = np.empty((arc.size, 0))
    duration_first = proper_first[-1]
    normalized = proper_at_nodes / duration

    x_spline = CubicSpline(arc, x)
    x_arc_rate = np.asarray(x_spline(arc, 1), dtype=float)
    fixed_normalized_first = np.empty_like(x_first)
    fixed_normalized_first[0] = x_first[0]
    if arc.size > 2:
        arc_motion = (
            normalized[1:-1, None] * duration_first[None, :]
            - proper_first[1:-1]
        ) / density[1:-1, None]
        fixed_normalized_first[1:-1] = (
            x_first[1:-1] + x_arc_rate[1:-1, None] * arc_motion
        )
    fixed_normalized_first[-1] = terminal_first

    return {
        "normalized_proper_times": normalized,
        "proper_times": proper_at_nodes,
        "proper_duration": duration,
        "proper_duration_first_jet": duration_first,
        "log_radius": x,
        "log_radius_normalized_proper_time_first_jet": fixed_normalized_first,
        "proper_time_density": density,
        "proper_time_density_first_jet": density_first,
        "parameter_count": parameter_count,
        "arc_parameter_not_identified_with_proper_time": True,
        "exact_density_identity": (
            "d_tau/d_r=N_boundary*s/||G_theta||_action_for_"
            "dY/dr=G_theta/||G_theta||_action"
        ),
        "density_interpolation": (
            "POSITIVE_PIECEWISE_LINEAR_WITH_EXACT_LINEAR_FIRST_JET"
        ),
    }


def assemble_cancelled_arc_proper_time_coefficient_first_jet(
    *,
    arc_nodes: np.ndarray,
    states: np.ndarray,
    state_action_first_jet: np.ndarray,
    state_weights: np.ndarray,
    signed_descriptor: np.ndarray,
    signed_descriptor_first_jet: np.ndarray,
    cancelled_field_action_norm: np.ndarray,
    cancelled_norm_state_gradient_action: np.ndarray,
    cancelled_norm_descriptor_derivative: np.ndarray,
    terminal_log_radius_first_jet: np.ndarray | None = None,
) -> dict[str, Any]:
    """Compose BHSM geometry incidence with the proper-time pullback."""

    arc = np.asarray(arc_nodes, dtype=float)
    state = np.asarray(states, dtype=float)
    state_first = np.asarray(state_action_first_jet, dtype=float)
    weights = np.asarray(state_weights, dtype=float)
    descriptor = np.asarray(signed_descriptor, dtype=float)
    descriptor_first = np.asarray(signed_descriptor_first_jet, dtype=float)
    norm = np.asarray(cancelled_field_action_norm, dtype=float)
    norm_state = np.asarray(cancelled_norm_state_gradient_action, dtype=float)
    norm_descriptor = np.asarray(cancelled_norm_descriptor_derivative, dtype=float)
    if (
        arc.ndim != 1
        or state.shape != (arc.size, 98)
        or state_first.ndim != 3
        or state_first.shape[:2] != state.shape
        or weights.shape != (98,)
        or descriptor.shape != arc.shape
        or descriptor_first.shape != (arc.size, state_first.shape[2])
        or norm.shape != arc.shape
        or norm_state.shape != state.shape
        or norm_descriptor.shape != arc.shape
        or not np.all(np.isfinite(state))
        or not np.all(np.isfinite(state_first))
        or not np.all(np.isfinite(weights))
        or np.any(weights <= 0.0)
        or not np.all(np.isfinite(norm_state))
        or not np.all(np.isfinite(norm_descriptor))
    ):
        raise ValueError("aligned N12 state-history geometry and norm first jets required")

    log_radius = np.empty(arc.size)
    log_lapse = np.empty(arc.size)
    log_radius_first = np.empty((arc.size, state_first.shape[2]))
    log_lapse_first = np.empty_like(log_radius_first)
    for node in range(arc.size):
        geometry = boundary_geometry_action_covectors(
            state=state[node], weights=weights,
        )
        log_radius[node] = float(geometry["log_R4"])
        log_lapse[node] = float(geometry["log_lapse"])
        log_radius_first[node] = (
            np.asarray(geometry["D_log_R4_action_dual"], dtype=float)
            @ state_first[node]
        )
        log_lapse_first[node] = (
            np.asarray(geometry["D_log_lapse_action_dual"], dtype=float)
            @ state_first[node]
        )
    norm_first = (
        np.einsum("ni,nij->nj", norm_state, state_first)
        + norm_descriptor[:, None] * descriptor_first
    )
    density = cancelled_arc_proper_time_density_first_jet(
        log_boundary_lapse=log_lapse,
        signed_descriptor=descriptor,
        cancelled_field_action_norm=norm,
        log_boundary_lapse_first_jet=log_lapse_first,
        signed_descriptor_first_jet=descriptor_first,
        cancelled_field_action_norm_first_jet=norm_first,
    )
    pulled = pullback_cancelled_arc_history_to_proper_time(
        arc_nodes=arc,
        log_radius=log_radius,
        log_radius_arc_first_jet=log_radius_first,
        proper_time_density=density["proper_time_density"],
        proper_time_density_first_jet=density[
            "proper_time_density_first_jet"
        ],
        terminal_log_radius_first_jet=terminal_log_radius_first_jet,
    )
    return {
        **pulled,
        "log_boundary_lapse": log_lapse,
        "log_boundary_lapse_arc_first_jet": log_lapse_first,
        "log_radius_arc_first_jet": log_radius_first,
        "cancelled_field_action_norm_first_jet": norm_first,
    }


__all__ = [
    "assemble_cancelled_arc_proper_time_coefficient_first_jet",
    "cancelled_arc_proper_time_density_first_jet",
    "pullback_cancelled_arc_history_to_proper_time",
]
