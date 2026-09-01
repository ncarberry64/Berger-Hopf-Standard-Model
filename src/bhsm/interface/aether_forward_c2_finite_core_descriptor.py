"""Inverse-free nonuniform finite-core descriptor pencils for C2 channels."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


_S = np.asarray(((1.0, -1.0), (-1.0, 1.0)))
_A = np.asarray(((2.0, 1.0), (1.0, 2.0)))
_C = np.asarray(((-1.0, 0.0), (0.0, 1.0)))


def assemble_finite_core_descriptor(
    *,
    log_radii: np.ndarray,
    proper_durations: np.ndarray,
    channel: str,
    unit_channel_value: float,
    chirality: int = 1,
) -> dict[str, Any]:
    """Assemble a birth-retained, far-core-Dirichlet form pencil.

    The far Dirichlet node is the nested Friedrichs form-core truncation and is
    not a physical endpoint condition.  Only tridiagonal coefficients and
    elementwise form derivatives are returned; no kinetic or Dirac block is
    inverted.
    """

    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    value = float(unit_channel_value)
    kind = str(channel)
    if (
        x.ndim != 1
        or h.ndim != 1
        or x.size != h.size + 1
        or h.size < 1
        or not np.all(np.isfinite(x))
        or not np.all(np.isfinite(h))
        or np.any(h <= 0.0)
        or not math.isfinite(value)
        or value < 0.0
    ):
        raise ValueError("finite node radii, positive durations, and nonnegative channel required")
    sign = int(chirality)
    if kind == "product_Dirac" and sign not in (-1, 1):
        raise ValueError("product-Dirac chirality must be +/-1")
    if kind not in {"scalar", "product_Dirac"}:
        raise ValueError("channel must be scalar or product_Dirac")

    segments = h.size
    dimension = segments  # retain node 0, eliminate the far node N
    K_diag = np.zeros(dimension)
    K_off = np.zeros(max(dimension - 1, 0))
    M_diag = np.zeros(dimension)
    M_off = np.zeros(max(dimension - 1, 0))
    dK_dx = np.zeros((segments, 2, 2))
    dK_dh = np.zeros((segments, 2, 2))
    dM_dh = np.broadcast_to(_A / 6.0, (segments, 2, 2)).copy()
    coefficient = np.zeros(segments)

    for index in range(segments):
        duration = h[index]
        x_mid = 0.5 * (x[index] + x[index + 1])
        mass = duration * _A / 6.0
        if kind == "scalar":
            potential = value * math.exp(-2.0 * x_mid)
            local = _S / duration + potential * mass
            local_dx = -2.0 * potential * mass
            local_dh = -_S / duration**2 + potential * _A / 6.0
            coefficient[index] = potential
        else:
            W = sign * value * math.exp(-x_mid)
            potential = W * W
            local = _S / duration + potential * mass + W * _C
            local_dx = -2.0 * potential * mass - W * _C
            local_dh = -_S / duration**2 + potential * _A / 6.0
            coefficient[index] = W
        dK_dx[index] = local_dx
        dK_dh[index] = local_dh

        left = index
        right = index + 1
        if left < dimension:
            K_diag[left] += local[0, 0]
            M_diag[left] += mass[0, 0]
        if right < dimension:
            K_diag[right] += local[1, 1]
            M_diag[right] += mass[1, 1]
            K_off[left] += local[0, 1]
            M_off[left] += mass[0, 1]

    total_duration = float(np.sum(h))
    if kind == "scalar":
        generalized_gap_lower = float(np.min(coefficient))
    else:
        W_upper = float(np.max(np.abs(coefficient)))
        first_order_gap = math.pi / (2.0 * total_duration) - W_upper
        generalized_gap_lower = max(0.0, first_order_gap) ** 2
    return {
        "channel": kind,
        "chirality": sign if kind == "product_Dirac" else None,
        "dimension": dimension,
        "segment_count": segments,
        "far_core_Dirichlet_node_eliminated": True,
        "birth_node_retained": True,
        "K_diagonal": K_diag,
        "K_off_diagonal": K_off,
        "M_diagonal": M_diag,
        "M_off_diagonal": M_off,
        "element_coefficient": coefficient,
        "D_x_mid_K_elements": dK_dx,
        "D_h_K_elements": dK_dh,
        "D_h_M_elements": dM_dh,
        "proper_duration": total_duration,
        "generalized_gap_lower": generalized_gap_lower,
        "explicit_matrix_inverse_formed": False,
    }


__all__ = ["assemble_finite_core_descriptor"]
