"""Exact local radius, lapse, and proper-duration incidence for C2 flow."""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.aether_forward_boundary_radius import (
    boundary_log_lapse,
    boundary_log_radius,
    boundary_log_radius_jets,
)


ORDER = 12
QDIM = 3 * ORDER + 1
STATE_DIMENSION = QDIM + QDIM + 2 * ORDER


def boundary_geometry_action_covectors(
    *, state: np.ndarray, weights: np.ndarray
) -> dict[str, Any]:
    """Return exact action-dual covectors of ``log R4`` and ``log N``."""

    y = np.asarray(state, dtype=float)
    w = np.asarray(weights, dtype=float)
    if (
        y.shape != (STATE_DIMENSION,)
        or w.shape != (STATE_DIMENSION,)
        or not np.all(np.isfinite(y))
        or not np.all(np.isfinite(w))
        or np.any(w <= 0.0)
    ):
        raise ValueError("finite C2 state and positive action weights required")
    radius_raw = np.zeros(STATE_DIMENSION)
    radius_raw[:QDIM] = np.asarray(
        boundary_log_radius_jets(
            ORDER, y[:QDIM], np.zeros(QDIM), np.zeros(QDIM)
        )["gradient"],
        dtype=float,
    )
    lapse_raw = np.zeros(STATE_DIMENSION)
    lapse_raw[2 * QDIM : 2 * QDIM + ORDER] = (
        (-1.0) ** np.arange(1, ORDER + 1)
    )
    return {
        "log_R4": boundary_log_radius(ORDER, y[:QDIM]),
        "log_lapse": boundary_log_lapse(ORDER, y[2 * QDIM :]),
        "D_log_R4_action_dual": radius_raw / w,
        "D_log_lapse_action_dual": lapse_raw / w,
    }


def proper_duration_density_and_action_covector(
    *,
    state: np.ndarray,
    weights: np.ndarray,
    signed_descriptor: float,
    Delta: float,
    D_Delta_action_dual: np.ndarray,
) -> dict[str, Any]:
    """Return ``q_tau=N*s/Delta`` and its exact signed local covector.

    The caller supplies the signed action-dual derivative of the action-owned
    desingularizing denominator.  This keeps the geometry incidence separate
    from the selected-line/Euler--Dirac derivative oracle that owns ``DDelta``.
    """

    geometry = boundary_geometry_action_covectors(state=state, weights=weights)
    s = float(signed_descriptor)
    delta = float(Delta)
    d_delta = np.asarray(D_Delta_action_dual, dtype=float)
    if (
        not np.isfinite(s)
        or s < 0.0
        or not np.isfinite(delta)
        or delta <= 0.0
        or d_delta.shape != (STATE_DIMENSION,)
        or not np.all(np.isfinite(d_delta))
    ):
        raise ValueError("nonnegative descriptor, positive Delta, and signed DDelta required")
    density = float(np.exp(float(geometry["log_lapse"])) * s / delta)
    covector = density * (
        np.asarray(geometry["D_log_lapse_action_dual"])
        - d_delta / delta
    )
    return {
        **geometry,
        "proper_duration_density": density,
        "D_proper_duration_density_action_dual": covector,
        "D_Delta_action_dual_consumed": True,
    }


__all__ = [
    "boundary_geometry_action_covectors",
    "proper_duration_density_and_action_covector",
]
