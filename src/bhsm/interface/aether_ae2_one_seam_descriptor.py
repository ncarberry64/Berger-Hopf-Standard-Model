"""Direct inverse-free descriptor assembly on the AE2 one-seam domain.

The external birth trace and the far Friedrichs-core trace are Dirichlet.
The E1/C2 trace is a single internal degree of freedom.  Consequently the
assembled quadratic form contains the retained contact exactly once and has
no pre-E0 response arm.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


_S = np.asarray(((1.0, -1.0), (-1.0, 1.0)))
_A = np.asarray(((2.0, 1.0), (1.0, 2.0)))
_C = np.asarray(((-1.0, 0.0), (0.0, 1.0)))


def _element(
    x_left: float,
    x_right: float,
    duration: float,
    *,
    channel: str,
    unit_channel_value: float,
    chirality: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return one action form element and its coefficient derivatives."""

    h = float(duration)
    x_mid = 0.5 * (float(x_left) + float(x_right))
    value = float(unit_channel_value)
    mass = h * _A / 6.0
    if channel == "scalar":
        potential = value * math.exp(-2.0 * x_mid)
        stiffness = _S / h + potential * mass
        d_x_mid = -2.0 * potential * mass
        d_h = -_S / h**2 + potential * _A / 6.0
    elif channel == "product_Dirac":
        superpotential = int(chirality) * value * math.exp(-x_mid)
        potential = superpotential * superpotential
        stiffness = _S / h + potential * mass + superpotential * _C
        d_x_mid = -2.0 * potential * mass - superpotential * _C
        d_h = -_S / h**2 + potential * _A / 6.0
    else:
        raise ValueError("channel must be scalar or product_Dirac")
    return stiffness, mass, d_x_mid, d_h, _A / 6.0


def assemble_ae2_one_seam_descriptor(
    *,
    formation_log_radii: np.ndarray,
    formation_proper_durations: np.ndarray,
    child_log_radii: np.ndarray,
    child_proper_durations: np.ndarray,
    channel: str,
    unit_channel_value: float,
    chirality: int = 1,
    seam_contact: float = 0.0,
    seam_match_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Assemble the E0--E1--C2 form with E1 represented only once.

    No response map and no kinetic/Dirac block is inverted.  The returned
    matrices act on all nodes except the external E0 Dirichlet node and the
    far C2 Friedrichs-core Dirichlet node.  ``seam_reduced_index`` identifies
    the common E1/C2 trace in that physical finite-core vector.
    """

    xf = np.asarray(formation_log_radii, dtype=float)
    hf = np.asarray(formation_proper_durations, dtype=float)
    xc = np.asarray(child_log_radii, dtype=float)
    hc = np.asarray(child_proper_durations, dtype=float)
    value = float(unit_channel_value)
    contact = float(seam_contact)
    tolerance = float(seam_match_tolerance)
    sign = int(chirality)
    if (
        xf.ndim != 1
        or xc.ndim != 1
        or hf.ndim != 1
        or hc.ndim != 1
        or xf.size != hf.size + 1
        or xc.size != hc.size + 1
        or hf.size < 1
        or hc.size < 1
        or not np.all(np.isfinite(xf))
        or not np.all(np.isfinite(xc))
        or not np.all(np.isfinite(hf))
        or not np.all(np.isfinite(hc))
        or np.any(hf <= 0.0)
        or np.any(hc <= 0.0)
        or not math.isfinite(value)
        or value < 0.0
        or not math.isfinite(contact)
        or contact < 0.0
        or not math.isfinite(tolerance)
        or tolerance < 0.0
    ):
        raise ValueError("finite matched paths, positive durations, and nonnegative form data required")
    if channel == "product_Dirac" and sign not in (-1, 1):
        raise ValueError("product-Dirac chirality must be +/-1")
    if abs(float(xf[-1] - xc[0])) > tolerance:
        raise ValueError("formation and child log radii must match at the AE2 seam")

    log_radii = np.concatenate((xf, xc[1:]))
    durations = np.concatenate((hf, hc))
    segment_count = durations.size
    full_node_count = segment_count + 1
    # Both exterior nodes are Dirichlet; all interior nodes are retained.
    dimension = full_node_count - 2
    K = np.zeros((dimension, dimension))
    M = np.zeros((dimension, dimension))
    dK_dx_mid = np.zeros((segment_count, 2, 2))
    dK_dh = np.zeros((segment_count, 2, 2))
    dM_dh = np.zeros((segment_count, 2, 2))

    for element_index, duration in enumerate(durations):
        local_K, local_M, local_dx, local_dh, local_dM = _element(
            log_radii[element_index],
            log_radii[element_index + 1],
            duration,
            channel=channel,
            unit_channel_value=value,
            chirality=sign,
        )
        dK_dx_mid[element_index] = local_dx
        dK_dh[element_index] = local_dh
        dM_dh[element_index] = local_dM
        for local_i, global_i in enumerate((element_index, element_index + 1)):
            if global_i in (0, full_node_count - 1):
                continue
            reduced_i = global_i - 1
            for local_j, global_j in enumerate((element_index, element_index + 1)):
                if global_j in (0, full_node_count - 1):
                    continue
                reduced_j = global_j - 1
                K[reduced_i, reduced_j] += local_K[local_i, local_j]
                M[reduced_i, reduced_j] += local_M[local_i, local_j]

    seam_global_node = hf.size
    seam_reduced_index = seam_global_node - 1
    K[seam_reduced_index, seam_reduced_index] += contact
    return {
        "channel": str(channel),
        "chirality": sign if channel == "product_Dirac" else None,
        "formation_segment_count": int(hf.size),
        "child_segment_count": int(hc.size),
        "segment_count": int(segment_count),
        "dimension": int(dimension),
        "seam_global_node": int(seam_global_node),
        "seam_reduced_index": int(seam_reduced_index),
        "seam_contact": contact,
        "K": K,
        "M": M,
        "D_x_mid_K_elements": dK_dx_mid,
        "D_h_K_elements": dK_dh,
        "D_h_M_elements": dM_dh,
        "external_birth_Dirichlet": True,
        "far_child_Friedrichs_core_Dirichlet": True,
        "internal_seam_trace_count": 1,
        "explicit_matrix_inverse_formed": False,
    }


def scalar_seam_schur_value(
    matrix: np.ndarray, seam_index: int
) -> float:
    """Return a scalar seam Schur value using a linear solve, not an inverse.

    This helper is for finite reproducibility witnesses.  The production
    descriptor assembly above never requires this elimination.
    """

    operator = np.asarray(matrix, dtype=float)
    seam = int(seam_index)
    if operator.ndim != 2 or operator.shape[0] != operator.shape[1]:
        raise ValueError("square matrix required")
    if seam < 0 or seam >= operator.shape[0]:
        raise ValueError("valid seam index required")
    rest = [index for index in range(operator.shape[0]) if index != seam]
    diagonal = float(operator[seam, seam])
    if not rest:
        return diagonal
    coupling = operator[np.ix_(rest, [seam])].reshape(-1)
    interior = operator[np.ix_(rest, rest)]
    return diagonal - float(coupling @ np.linalg.solve(interior, coupling))


__all__ = ["assemble_ae2_one_seam_descriptor", "scalar_seam_schur_value"]
