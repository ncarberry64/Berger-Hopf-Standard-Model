"""Local proper-time transfer germs from BHSM boundary Cauchy data."""

from __future__ import annotations

import math

import numpy as np

from bhsm.interface.aether_forward_channel_transfer import (
    product_dirac_channel_transfer_generator,
    scalar_channel_transfer_generator,
)


def _finite(*values: float) -> None:
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("finite Cauchy data required")


def _entry(value: float) -> np.ndarray:
    return np.asarray([[0.0, 0.0], [value, 0.0]], dtype=complex)


def _diagonal(value: float) -> np.ndarray:
    return np.asarray([[value, 0.0], [0.0, -value]], dtype=complex)


def scalar_channel_cauchy_generator_jets(
    spatial_eigenvalue_at_unit_radius: float,
    log_radius: float,
    proper_log_radius_rate: float,
    spectral_parameter: complex,
    parameter_log_radius: float,
    parameter_proper_log_radius_rate: float,
) -> dict[str, np.ndarray]:
    """Return ``G, D_tau G, D_xi G, D_xi D_tau G`` at a birth trace."""

    c = float(spatial_eigenvalue_at_unit_radius)
    x = float(log_radius)
    h_rate = float(proper_log_radius_rate)
    h = float(parameter_log_radius)
    h_h_rate = float(parameter_proper_log_radius_rate)
    _finite(c, x, h_rate, h, h_h_rate)
    if c < 0.0:
        raise ValueError("nonnegative scalar channel required")
    potential = c * math.exp(-2.0 * x)
    return {
        "base": scalar_channel_transfer_generator(c, x, spectral_parameter),
        "proper_time_first": _entry(-2.0 * h_rate * potential),
        "parameter_first": _entry(-2.0 * h * potential),
        "mixed_time_parameter": _entry(
            (4.0 * h_rate * h - 2.0 * h_h_rate) * potential
        ),
    }


def product_dirac_channel_cauchy_generator_jets(
    dirac_eigenvalue_at_unit_radius: float,
    log_radius: float,
    proper_log_radius_rate: float,
    spectral_parameter: complex,
    parameter_log_radius: float,
    parameter_proper_log_radius_rate: float,
    *,
    chirality: int = 1,
) -> dict[str, np.ndarray]:
    """Return the corresponding factorized product-Dirac generator jets."""

    eigenvalue = float(dirac_eigenvalue_at_unit_radius)
    x = float(log_radius)
    h_rate = float(proper_log_radius_rate)
    h = float(parameter_log_radius)
    h_h_rate = float(parameter_proper_log_radius_rate)
    sign = int(chirality)
    _finite(eigenvalue, x, h_rate, h, h_h_rate)
    if sign not in (-1, 1):
        raise ValueError("chirality must be +/-1")
    superpotential = sign * eigenvalue * math.exp(-x)
    return {
        "base": product_dirac_channel_transfer_generator(
            eigenvalue, x, spectral_parameter, chirality=sign
        ),
        "proper_time_first": _diagonal(h_rate * superpotential),
        "parameter_first": _diagonal(h * superpotential),
        "mixed_time_parameter": _diagonal(
            (h_h_rate - h_rate * h) * superpotential
        ),
    }


def local_transfer_cauchy_germ(
    generator_jets: dict[str, np.ndarray],
) -> dict[str, np.ndarray | bool]:
    """Return transfer and parameter-jet coefficients through order ``tau^2``.

    If ``T'=G(tau,xi)T`` and ``T(0)=I``, then

    ``T=I+tau*G0+tau^2/2*(G0^2+G_tau)+o(tau^2)``

    and the displayed parameter derivative follows by differentiating this
    identity.  No endpoint load or matrix inverse enters.
    """

    required = (
        "base",
        "proper_time_first",
        "parameter_first",
        "mixed_time_parameter",
    )
    if not all(key in generator_jets for key in required):
        raise KeyError("complete generator Cauchy jet required")
    g, gt, gh, gth = (
        np.asarray(generator_jets[key], dtype=complex) for key in required
    )
    if any(value.shape != (2, 2) for value in (g, gt, gh, gth)) or any(
        not np.all(np.isfinite(value)) for value in (g, gt, gh, gth)
    ):
        raise ValueError("finite 2x2 generator jets required")
    return {
        "transfer_constant": np.eye(2, dtype=complex),
        "transfer_linear": g,
        "transfer_quadratic": 0.5 * (g @ g + gt),
        "parameter_constant": np.zeros((2, 2), dtype=complex),
        "parameter_linear": gh,
        "parameter_quadratic": 0.5 * (gh @ g + g @ gh + gth),
        "explicit_matrix_inverse_formed": False,
        "endpoint_condition_imposed": False,
    }


__all__ = [
    "local_transfer_cauchy_germ",
    "product_dirac_channel_cauchy_generator_jets",
    "scalar_channel_cauchy_generator_jets",
]
