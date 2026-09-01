"""Event-normal Riccati evolution of the finite-endpoint Weyl map."""

from __future__ import annotations

import numpy as np


def weyl_riccati_rhs(
    weyl: np.ndarray, spatial_operator: np.ndarray, spectral_parameter: float,
) -> np.ndarray:
    """Return ``dM/ds=(L-zI)-M^2`` from the terminal event inward."""

    m = np.asarray(weyl, dtype=complex)
    potential = np.asarray(spatial_operator, dtype=complex)
    if (
        m.ndim != 2
        or m.shape[0] != m.shape[1]
        or potential.shape != m.shape
        or not np.all(np.isfinite(m))
        or not np.all(np.isfinite(potential))
    ):
        raise ValueError("finite same-size square Weyl and spatial matrices required")
    if not np.allclose(m, m.conj().T, rtol=0.0, atol=1.0e-11):
        raise ValueError("Weyl matrix must be Hermitian on the real resolvent axis")
    if not np.allclose(potential, potential.conj().T, rtol=0.0, atol=1.0e-11):
        raise ValueError("spatial operator must be Hermitian")
    return potential - float(spectral_parameter) * np.eye(m.shape[0]) - m @ m


def weyl_geometry_jet_rhs(
    weyl: np.ndarray,
    geometry_jet: np.ndarray,
    spatial_geometry_jet: np.ndarray,
) -> np.ndarray:
    """Return the exact linearized Riccati equation for ``D_Phi M``."""

    m = np.asarray(weyl, dtype=complex)
    dm = np.asarray(geometry_jet, dtype=complex)
    dv = np.asarray(spatial_geometry_jet, dtype=complex)
    if m.ndim != 2 or m.shape[0] != m.shape[1] or dm.shape != m.shape or dv.shape != m.shape:
        raise ValueError("Weyl value and geometry jets must have one square shape")
    if not all(np.all(np.isfinite(value)) for value in (m, dm, dv)):
        raise ValueError("finite Weyl geometry-jet data required")
    return dv - m @ dm - dm @ m


def scalar_constant_weyl(
    length: float, spatial_value: float, spectral_parameter: float, terminal_wentzell: float,
) -> float:
    """Closed scalar solution used to verify the event-normal orientation."""

    if length < 0.0:
        raise ValueError("length must be nonnegative")
    k2 = float(spatial_value) - float(spectral_parameter)
    if k2 <= 0.0:
        raise ValueError("positive coercive scalar pencil required")
    k = k2**0.5
    tangent = np.tanh(k * float(length))
    denominator = k + float(terminal_wentzell) * tangent
    if denominator == 0.0:
        raise ValueError("scalar Riccati chart reached a pole")
    return float(
        k * (float(terminal_wentzell) + k * tangent) / denominator
    )


__all__ = [
    "weyl_riccati_rhs",
    "weyl_geometry_jet_rhs",
    "scalar_constant_weyl",
]
