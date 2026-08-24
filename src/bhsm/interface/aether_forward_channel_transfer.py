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
    mixed_second_direction: float = 0.0,
) -> dict[str, np.ndarray]:
    """Return base, first-left, first-right, and mixed log-radius jets."""

    base = scalar_channel_transfer_generator(
        spatial_eigenvalue_at_unit_radius, log_radius, spectral_parameter
    )
    c = float(spatial_eigenvalue_at_unit_radius)
    potential = c * math.exp(-2.0 * float(log_radius))
    h = float(left_direction)
    k = float(right_direction)
    ell = float(mixed_second_direction)
    if not math.isfinite(h) or not math.isfinite(k) or not math.isfinite(ell):
        raise ValueError("finite log-radius directions required")

    def lower_left(value: float) -> np.ndarray:
        return np.asarray([[0.0, 0.0], [value, 0.0]], dtype=complex)

    return {
        "base": base,
        "first_left": lower_left(-2.0 * h * potential),
        "first_right": lower_left(-2.0 * k * potential),
        "mixed_second": lower_left((4.0 * h * k - 2.0 * ell) * potential),
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
    mixed_second_direction: float = 0.0,
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
    ell = float(mixed_second_direction)
    if not math.isfinite(h) or not math.isfinite(k) or not math.isfinite(ell):
        raise ValueError("finite log-radius directions required")

    def diagonal(value: float) -> np.ndarray:
        return np.asarray([[value, 0.0], [0.0, -value]], dtype=complex)

    return {
        "base": base,
        "first_left": diagonal(h * s),
        "first_right": diagonal(k * s),
        "mixed_second": diagonal((ell - h * k) * s),
    }


def transfer_variation_rhs(
    generator_jets: dict[str, np.ndarray],
    transfer_jets: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Return the base, tangent, and mixed-second transfer derivatives.

    For ``T'=G T`` and two action directions ``h,k``, this is the exact
    triangular variational system

    ``T_h'=G T_h+G_h T`` and
    ``T_hk'=G T_hk+G_h T_k+G_k T_h+G_hk T``.

    The birth frame is action independent when the initial data are
    ``T=I`` and all three variation matrices are zero.  Endpoint/domain
    variations are instead carried by the terminal-admittance jets below.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")

    def checked(record: dict[str, np.ndarray], key: str) -> np.ndarray:
        value = np.asarray(record[key], dtype=complex)
        if value.shape != (2, 2) or not np.all(np.isfinite(value)):
            raise ValueError(f"finite 2x2 matrix required for {key}")
        return value

    if not all(key in generator_jets and key in transfer_jets for key in keys):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    g, gh, gk, ghk = (checked(generator_jets, key) for key in keys)
    t, th, tk, thk = (checked(transfer_jets, key) for key in keys)
    return {
        "base": g @ t,
        "first_left": g @ th + gh @ t,
        "first_right": g @ tk + gk @ t,
        "mixed_second": g @ thk + gh @ tk + gk @ th + ghk @ t,
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


def backward_weyl_mobius_jets(
    transfer_jets: dict[str, np.ndarray],
    terminal_admittance_jets: dict[str, complex],
) -> dict[str, complex]:
    """Pull back base, tangent, and mixed-second terminal Weyl jets.

    This includes terminal/Friedrichs graph variation and therefore separates
    bulk transfer variation from endpoint/domain variation without assuming a
    terminal return.  A zero denominator is precisely the singular graph
    chart already excluded from a regular Weyl interval.
    """

    keys = ("base", "first_left", "first_right", "mixed_second")
    if not all(key in transfer_jets for key in keys) or not all(
        key in terminal_admittance_jets for key in keys
    ):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    matrices = [np.asarray(transfer_jets[key], dtype=complex) for key in keys]
    if any(matrix.shape != (2, 2) for matrix in matrices) or any(
        not np.all(np.isfinite(matrix)) for matrix in matrices
    ):
        raise ValueError("finite 2x2 transfer jets required")
    mu, muh, muk, muhk = (
        complex(terminal_admittance_jets[key]) for key in keys
    )
    if not all(
        math.isfinite(value.real) and math.isfinite(value.imag)
        for value in (mu, muh, muk, muhk)
    ):
        raise ValueError("finite terminal admittance jets required")
    t, th, tk, thk = matrices

    def numerator(matrix: np.ndarray, terminal: complex) -> complex:
        return matrix[1, 0] - terminal * matrix[0, 0]

    def denominator(matrix: np.ndarray, terminal: complex) -> complex:
        return terminal * matrix[0, 1] - matrix[1, 1]

    n = numerator(t, mu)
    d = denominator(t, mu)
    if abs(d) == 0.0:
        raise ZeroDivisionError("terminal graph is singular under transfer")
    nh = numerator(th, mu) - muh * t[0, 0]
    nk = numerator(tk, mu) - muk * t[0, 0]
    nhk = (
        numerator(thk, mu)
        - muhk * t[0, 0]
        - muh * tk[0, 0]
        - muk * th[0, 0]
    )
    dh = denominator(th, mu) + muh * t[0, 1]
    dk = denominator(tk, mu) + muk * t[0, 1]
    dhk = (
        denominator(thk, mu)
        + muhk * t[0, 1]
        + muh * tk[0, 1]
        + muk * th[0, 1]
    )
    m = n / d
    mh = (nh - m * dh) / d
    mk = (nk - m * dk) / d
    mhk = (nhk - mh * dk - mk * dh - m * dhk) / d
    return {
        "base": m,
        "first_left": mh,
        "first_right": mk,
        "mixed_second": mhk,
    }


__all__ = [
    "scalar_channel_transfer_generator",
    "scalar_channel_log_radius_jets",
    "product_dirac_channel_transfer_generator",
    "product_dirac_channel_log_radius_jets",
    "transfer_variation_rhs",
    "backward_weyl_mobius",
    "backward_weyl_mobius_jets",
]
