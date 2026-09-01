"""Jacobi and moving-endpoint jets for an action-owned maximal history."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class MovingEndpointJets:
    """First and mixed second jets of a transverse hitting endpoint."""

    time_left: float
    time_right: float
    time_mixed: float
    state_left: Array
    state_right: Array
    state_mixed: Array


def state_jacobi_rhs(
    vector_field: Array,
    vector_jacobian: Array,
    vector_hessian: Array,
    state_left: Array,
    state_right: Array,
    state_mixed: Array,
) -> tuple[Array, Array, Array]:
    """Return the triangular first/mixed state-Jacobi right-hand sides.

    For ``Y'=V(Y)``, the fixed-time jets obey

    ``J_h'=DV J_h`` and
    ``K_hk'=DV K_hk + D2V[J_h,J_k]``.

    ``vector_field`` is accepted to enforce a common state dimension and to
    keep the call contract aligned with the endpoint formula.
    """

    v = np.asarray(vector_field, dtype=float)
    dv = np.asarray(vector_jacobian, dtype=float)
    d2v = np.asarray(vector_hessian, dtype=float)
    jh = np.asarray(state_left, dtype=float)
    jk = np.asarray(state_right, dtype=float)
    khk = np.asarray(state_mixed, dtype=float)
    n = v.size
    if (
        v.shape != (n,)
        or dv.shape != (n, n)
        or d2v.shape != (n, n, n)
        or jh.shape != (n,)
        or jk.shape != (n,)
        or khk.shape != (n,)
    ):
        raise ValueError("incompatible state-Jacobi dimensions")
    if not all(np.all(np.isfinite(value)) for value in (v, dv, d2v, jh, jk, khk)):
        raise ValueError("finite state-Jacobi data required")
    first_left = dv @ jh
    first_right = dv @ jk
    mixed = dv @ khk + np.einsum("ijk,j,k->i", d2v, jh, jk)
    return first_left, first_right, mixed


def moving_endpoint_jets(
    vector_field: Array,
    vector_jacobian: Array,
    event_gradient: Array,
    event_hessian: Array,
    fixed_time_left: Array,
    fixed_time_right: Array,
    fixed_time_mixed: Array,
    *,
    transversality_tolerance: float = 1.0e-14,
) -> MovingEndpointJets:
    """Convert fixed-time flow jets to jets at ``e(Y(T(xi),xi))=0``.

    The event function has no separately inserted parameter dependence.  Any
    retained geometric dependence is represented through the state and its
    reset-stratum Jacobi data.
    """

    v = np.asarray(vector_field, dtype=float)
    dv = np.asarray(vector_jacobian, dtype=float)
    normal = np.asarray(event_gradient, dtype=float)
    d2e = np.asarray(event_hessian, dtype=float)
    jh = np.asarray(fixed_time_left, dtype=float)
    jk = np.asarray(fixed_time_right, dtype=float)
    khk = np.asarray(fixed_time_mixed, dtype=float)
    n = v.size
    if (
        v.shape != (n,)
        or dv.shape != (n, n)
        or normal.shape != (n,)
        or d2e.shape != (n, n)
        or jh.shape != (n,)
        or jk.shape != (n,)
        or khk.shape != (n,)
    ):
        raise ValueError("incompatible moving-endpoint dimensions")
    if not all(np.all(np.isfinite(value)) for value in (v, dv, normal, d2e, jh, jk, khk)):
        raise ValueError("finite moving-endpoint data required")
    alpha = float(normal @ v)
    if abs(alpha) <= transversality_tolerance:
        raise ValueError("transverse event margin required")

    time_left = -float(normal @ jh) / alpha
    time_right = -float(normal @ jk) / alpha
    endpoint_left = jh + v * time_left
    endpoint_right = jk + v * time_right

    fixed_chain = (
        khk
        + (dv @ jh) * time_right
        + (dv @ jk) * time_left
        + (dv @ v) * time_left * time_right
    )
    event_curvature = float(endpoint_left @ d2e @ endpoint_right)
    time_mixed = -(float(normal @ fixed_chain) + event_curvature) / alpha
    endpoint_mixed = fixed_chain + v * time_mixed
    return MovingEndpointJets(
        time_left=time_left,
        time_right=time_right,
        time_mixed=time_mixed,
        state_left=endpoint_left,
        state_right=endpoint_right,
        state_mixed=endpoint_mixed,
    )


def endpoint_observable_jets(
    observable_gradient: Array,
    observable_hessian: Array,
    endpoint: MovingEndpointJets,
) -> tuple[float, float, float]:
    """Compose a scalar endpoint graph/observable with endpoint state jets."""

    gradient = np.asarray(observable_gradient, dtype=float)
    hessian = np.asarray(observable_hessian, dtype=float)
    n = endpoint.state_left.size
    if gradient.shape != (n,) or hessian.shape != (n, n):
        raise ValueError("incompatible endpoint observable dimensions")
    first_left = float(gradient @ endpoint.state_left)
    first_right = float(gradient @ endpoint.state_right)
    mixed = float(
        gradient @ endpoint.state_mixed
        + endpoint.state_left @ hessian @ endpoint.state_right
    )
    return first_left, first_right, mixed


__all__ = [
    "MovingEndpointJets",
    "endpoint_observable_jets",
    "moving_endpoint_jets",
    "state_jacobi_rhs",
]
