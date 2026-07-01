"""Numerically guarded four-vector transformations used by invariant audits."""

from __future__ import annotations

import numpy as np


def _states(values: np.ndarray) -> np.ndarray:
    states = np.asarray(values, dtype=np.float64)
    if states.ndim != 2 or states.shape[1] != 4:
        raise ValueError("four-vectors must have shape (n, 4) as E,px,py,pz")
    if not np.all(np.isfinite(states)):
        raise ValueError("four-vectors must be finite")
    return states


def minkowski_norm_sq(values: np.ndarray) -> np.ndarray:
    """Return E^2-|p|^2 using the (+---) convention."""

    states = _states(values)
    return states[:, 0] ** 2 - np.einsum("ij,ij->i", states[:, 1:4], states[:, 1:4])


def boundary_chart_forward(values: np.ndarray) -> np.ndarray:
    """Map E,px,py,pz to E,r,ux,uy,uz without angular singularities."""

    states = _states(values)
    xyz = states[:, 1:4]
    radius = np.linalg.norm(xyz, axis=1)
    safe = np.where(radius == 0.0, 1.0, radius)
    unit = xyz / safe[:, None]
    unit[radius == 0.0] = 0.0
    return np.column_stack((states[:, 0], radius, unit))


def boundary_chart_inverse(chart: np.ndarray) -> np.ndarray:
    """Invert E,r,ux,uy,uz after validating the finite chart representation."""

    values = np.asarray(chart, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 5 or not np.all(np.isfinite(values)):
        raise ValueError("boundary chart must contain finite E,r,ux,uy,uz rows")
    if np.any(values[:, 1] < 0.0):
        raise ValueError("boundary chart radius must be nonnegative")
    return np.column_stack((values[:, 0], values[:, 1, None] * values[:, 2:5]))


def lorentz_boost_x(values: np.ndarray, beta: float) -> np.ndarray:
    """Apply a stable x-directed Lorentz boost for |beta|<1."""

    states = _states(values)
    beta = float(beta)
    if not np.isfinite(beta) or abs(beta) >= 1.0:
        raise ValueError("beta must be finite with abs(beta) < 1")
    gamma = 1.0 / np.sqrt(1.0 - beta * beta)
    result = states.copy()
    result[:, 0] = gamma * (states[:, 0] - beta * states[:, 1])
    result[:, 1] = gamma * (states[:, 1] - beta * states[:, 0])
    return result
