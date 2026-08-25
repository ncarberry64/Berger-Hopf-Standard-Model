"""Stable inverse-free Riccati evaluation of finite C2 form-core Weyl data."""

from __future__ import annotations

import math
from typing import Any

import mpmath as mp
import numpy as np


def _map(
    terminal: mp.mpf | None,
    x_mid: mp.mpf,
    duration: mp.mpf,
    *,
    channel: str,
    value: float,
    z: float,
    chirality: int,
) -> mp.mpf:
    if channel == "scalar":
        potential = value * mp.exp(-2 * x_mid)
        k = mp.sqrt(potential - z)
        tangent = mp.tanh(k * duration)
        if terminal is None:
            return k / tangent
        return (k * tangent + terminal) / (1.0 + terminal * tangent / k)
    W = chirality * value * mp.exp(-x_mid)
    k = mp.sqrt(W * W - z)
    tangent = mp.tanh(k * duration)
    a = 1.0 - W * tangent / k
    b = tangent / k
    c = (-z) * tangent / k
    d = 1.0 + W * tangent / k
    if terminal is None:
        return a / b
    return (c + terminal * a) / (d + terminal * b)


def finite_core_weyl_and_coefficient_cotangent(
    *,
    log_radii: np.ndarray,
    proper_durations: np.ndarray,
    channel: str,
    unit_channel_value: float,
    spectral_parameter: float,
    chirality: int = 1,
    decimal_precision: int = 80,
    terminal_load: float | None = None,
) -> dict[str, Any]:
    """Return the birth Weyl scalar and exact reverse coefficient cotangent.

    The terminal `None` value is the far Dirichlet form-core edge.  Each
    Möbius update acts on a scalar conormal impedance and never subtracts the
    two large stiffness terms that make a direct Schur recurrence unstable.
    Local partial derivatives use arbitrary-precision differentiation and are
    then composed by reverse accumulation.  This is necessary because the
    physical coefficient derivative is tens of orders below the short-core
    impedance background.
    """

    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    kind = str(channel)
    value = float(unit_channel_value)
    z = float(spectral_parameter)
    sign = int(chirality)
    load = None if terminal_load is None else float(terminal_load)
    if (
        x.ndim != 1 or h.ndim != 1 or x.size != h.size + 1 or h.size < 1
        or not np.all(np.isfinite(x)) or not np.all(np.isfinite(h))
        or np.any(h <= 0.0) or not math.isfinite(value) or value < 0.0
        or not math.isfinite(z) or z >= 0.0
        or (load is not None and (not math.isfinite(load) or load < 0.0))
    ):
        raise ValueError("finite coefficients, positive durations, and real z<0 required")
    if kind not in {"scalar", "product_Dirac"}:
        raise ValueError("channel must be scalar or product_Dirac")
    if kind == "product_Dirac" and sign not in (-1, 1):
        raise ValueError("product-Dirac chirality must be +/-1")
    if int(decimal_precision) < 50:
        raise ValueError("at least fifty decimal digits required")

    count = h.size
    x_mid = 0.5 * (x[:-1] + x[1:])
    with mp.workdps(int(decimal_precision)):
        starts_mp: list[mp.mpf] = [mp.mpf(0)] * count
        d_x_mp: list[mp.mpf] = [mp.mpf(0)] * count
        d_h_mp: list[mp.mpf] = [mp.mpf(0)] * count
        d_terminal_mp: list[mp.mpf] = [mp.mpf(0)] * count
        terminal: mp.mpf | None = (
            None if load is None else mp.mpf(str(load))
        )
        for index in range(count - 1, -1, -1):
            xi = mp.mpf(str(float(x_mid[index])))
            hi = mp.mpf(str(float(h[index])))
            base = _map(
                terminal, xi, hi, channel=kind, value=value, z=z, chirality=sign
            )
            d_x_mp[index] = mp.diff(
                lambda xx: _map(
                    terminal, xx, hi,
                    channel=kind, value=value, z=z, chirality=sign,
                ),
                xi,
            )
            d_h_mp[index] = mp.diff(
                lambda hh: _map(
                    terminal, xi, hh,
                    channel=kind, value=value, z=z, chirality=sign,
                ),
                hi,
            )
            if terminal is not None:
                d_terminal_mp[index] = mp.diff(
                    lambda zz: _map(
                        zz, xi, hi,
                        channel=kind, value=value, z=z, chirality=sign,
                    ),
                    terminal,
                )
            starts_mp[index] = base
            terminal = base

        gradient_x_mid_mp: list[mp.mpf] = [mp.mpf(0)] * count
        gradient_duration_mp: list[mp.mpf] = [mp.mpf(0)] * count
        adjoint = mp.mpf(1)
        for index in range(count):
            gradient_x_mid_mp[index] = adjoint * d_x_mp[index]
            gradient_duration_mp[index] = adjoint * d_h_mp[index]
            adjoint *= d_terminal_mp[index]
        weyl_decimal = mp.nstr(starts_mp[0], n=int(decimal_precision))
        uniform_log_radius_decimal = mp.nstr(
            mp.fsum(gradient_x_mid_mp), n=int(decimal_precision)
        )
        duration_weighted_decimal = mp.nstr(
            mp.fsum(
                gradient_duration_mp[index] * mp.mpf(str(float(h[index])))
                for index in range(count)
            ),
            n=int(decimal_precision),
        )
        terminal_load_sensitivity_decimal = (
            None if load is None else mp.nstr(adjoint, n=int(decimal_precision))
        )
        starts = np.asarray([float(item) for item in starts_mp])
        gradient_x_mid = np.asarray([float(item) for item in gradient_x_mid_mp])
        gradient_duration = np.asarray([float(item) for item in gradient_duration_mp])
    node_gradient = np.zeros(count + 1)
    node_gradient[:-1] += 0.5 * gradient_x_mid
    node_gradient[1:] += 0.5 * gradient_x_mid
    return {
        "channel": kind,
        "chirality": sign if kind == "product_Dirac" else None,
        "spectral_parameter": z,
        "Weyl_birth_value": float(starts[0]),
        "Weyl_birth_value_decimal": weyl_decimal,
        "backward_impedance_values": starts,
        "D_x_mid_Weyl": gradient_x_mid,
        "D_log_R4_node_Weyl": node_gradient,
        "D_proper_duration_Weyl": gradient_duration,
        "D_log_R4_uniform_shift_decimal": uniform_log_radius_decimal,
        "D_duration_weighted_uniform_scale_decimal": duration_weighted_decimal,
        "terminal_Dirichlet_form_core": load is None,
        "terminal_nonnegative_load": load,
        "D_terminal_load_Weyl_decimal": terminal_load_sensitivity_decimal,
        "explicit_matrix_inverse_formed": False,
        "decimal_precision": int(decimal_precision),
    }


__all__ = ["finite_core_weyl_and_coefficient_cotangent"]
