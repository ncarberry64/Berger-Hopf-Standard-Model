"""Fixed-channel transfer systems for the maximal-forward source operator.

The retained round spatial blocks are homogeneous in the physical boundary
radius.  Their eigenspaces are therefore fixed along a history; only
``x(tau)=log(R4(tau))`` changes.  This module exposes the exact two-dimensional
channel generators and their log-radius jets without selecting a history,
endpoint, spectral-to-momentum map, or source profile.
"""

from __future__ import annotations

import math

import numpy as np


def scalar_channel_transfer_generator(
    spatial_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
) -> np.ndarray:
    """Return the first-order transfer generator for ``-u''+c/R4^2 u=z u``."""

    c = float(spatial_eigenvalue_at_unit_radius)
    x = float(log_radius)
    z = complex(spectral_parameter)
    if not math.isfinite(c) or c < 0.0 or not math.isfinite(x):
        raise ValueError("finite nonnegative channel and finite log radius required")
    potential = c * math.exp(-2.0 * x)
    return np.asarray([[0.0, 1.0], [potential - z, 0.0]], dtype=complex)


def scalar_channel_log_radius_jets(
    spatial_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
    left_direction: float,
    right_direction: float,
) -> dict[str, np.ndarray]:
    """Return base, first-left, first-right, and mixed log-radius jets."""

    base = scalar_channel_transfer_generator(
        spatial_eigenvalue_at_unit_radius, log_radius, spectral_parameter
    )
    c = float(spatial_eigenvalue_at_unit_radius)
    potential = c * math.exp(-2.0 * float(log_radius))
    h = float(left_direction)
    k = float(right_direction)
    if not math.isfinite(h) or not math.isfinite(k):
        raise ValueError("finite log-radius directions required")

    def lower_left(value: float) -> np.ndarray:
        return np.asarray([[0.0, 0.0], [value, 0.0]], dtype=complex)

    return {
        "base": base,
        "first_left": lower_left(-2.0 * h * potential),
        "first_right": lower_left(-2.0 * k * potential),
        "mixed_second": lower_left(4.0 * h * k * potential),
    }


def product_dirac_channel_transfer_generator(
    dirac_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
    *,
    chirality: int = 1,
) -> np.ndarray:
    """Return the transfer generator for one product-Dirac squared channel.

    With ``A=d/dtau+s`` and ``v=A u``, the equation ``A^* A u=z u`` is
    ``(u,v)'=[[-s,1],[-z,s]](u,v)``.  The other squared block is obtained by
    changing the chirality sign.
    """

    eigenvalue = float(dirac_eigenvalue_at_unit_radius)
    x = float(log_radius)
    z = complex(spectral_parameter)
    sign = int(chirality)
    if (
        not math.isfinite(eigenvalue)
        or not math.isfinite(x)
        or sign not in (-1, 1)
    ):
        raise ValueError("finite Dirac channel and chirality +/-1 required")
    s = sign * eigenvalue * math.exp(-x)
    return np.asarray([[-s, 1.0], [-z, s]], dtype=complex)


def product_dirac_channel_log_radius_jets(
    dirac_eigenvalue_at_unit_radius: float,
    log_radius: float,
    spectral_parameter: complex,
    left_direction: float,
    right_direction: float,
    *,
    chirality: int = 1,
) -> dict[str, np.ndarray]:
    """Return exact log-radius jets of a product-Dirac channel generator."""

    base = product_dirac_channel_transfer_generator(
        dirac_eigenvalue_at_unit_radius,
        log_radius,
        spectral_parameter,
        chirality=chirality,
    )
    s = (
        int(chirality)
        * float(dirac_eigenvalue_at_unit_radius)
        * math.exp(-float(log_radius))
    )
    h = float(left_direction)
    k = float(right_direction)
    if not math.isfinite(h) or not math.isfinite(k):
        raise ValueError("finite log-radius directions required")

    def diagonal(value: float) -> np.ndarray:
        return np.asarray([[value, 0.0], [0.0, -value]], dtype=complex)

    return {
        "base": base,
        "first_left": diagonal(h * s),
        "first_right": diagonal(k * s),
        "mixed_second": diagonal(-h * k * s),
    }


def backward_weyl_mobius(
    transfer_birth_to_terminal: np.ndarray,
    terminal_admittance: complex,
) -> complex:
    """Pull a scalar terminal Weyl admittance back to the birth trace."""

    transfer = np.asarray(transfer_birth_to_terminal, dtype=complex)
    if transfer.shape != (2, 2) or not np.all(np.isfinite(transfer)):
        raise ValueError("finite 2x2 transfer matrix required")
    terminal = complex(terminal_admittance)
    numerator = transfer[1, 0] - terminal * transfer[0, 0]
    denominator = terminal * transfer[0, 1] - transfer[1, 1]
    if abs(denominator) == 0.0:
        raise ZeroDivisionError("terminal graph is singular under transfer")
    return numerator / denominator


__all__ = [
    "scalar_channel_transfer_generator",
    "scalar_channel_log_radius_jets",
    "product_dirac_channel_transfer_generator",
    "product_dirac_channel_log_radius_jets",
    "backward_weyl_mobius",
]
