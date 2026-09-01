"""Trace-norm control of the compact-source E1 high-energy tail."""

from __future__ import annotations

import math

import numpy as np


def e1_high_energy_trace_norm_bound(
    heat_sandwiched_trace_norm: float,
    spectral_floor: float = 1.0,
) -> float:
    """Bound ``int_[floor,inf] exp(-lambda)/lambda d|nu|``.

    If ``T=exp(-K/2) P exp(-K/2)`` is trace class, the measure
    ``mu(B)=Tr(E_K(B)T)`` equals ``exp(-lambda) dnu(lambda)``.  Hence the
    requested tail is at most ``||T||_1/floor``.
    """

    trace_norm = float(heat_sandwiched_trace_norm)
    floor = float(spectral_floor)
    if not math.isfinite(trace_norm) or trace_norm < 0.0:
        raise ValueError("finite nonnegative trace norm required")
    if not math.isfinite(floor) or floor <= 0.0:
        raise ValueError("finite positive spectral floor required")
    return trace_norm / floor


def factorized_heat_sandwich_trace_norm_bound(
    localized_energy_heat_hilbert_schmidt_norm: float,
    localized_vertex_heat_hilbert_schmidt_norm: float,
) -> float:
    """Bound a factorized first form jet by two Hilbert--Schmidt factors.

    For ``P_h=A*B+B*A`` with compactly supported ``B``, polar decomposition
    of ``B`` localizes both heat factors.  The two adjoint terms give the
    returned factor of two.
    """

    energy = float(localized_energy_heat_hilbert_schmidt_norm)
    vertex = float(localized_vertex_heat_hilbert_schmidt_norm)
    if any(not math.isfinite(value) or value < 0.0 for value in (energy, vertex)):
        raise ValueError("finite nonnegative Hilbert--Schmidt norms required")
    return 2.0 * energy * vertex


def finite_matrix_e1_high_energy_witness(
    operator: np.ndarray,
    source_vertex: np.ndarray,
    spectral_floor: float = 1.0,
) -> dict[str, float]:
    """Evaluate the measure tail and trace-norm theorem in finite dimension."""

    k = np.asarray(operator, dtype=complex)
    p = np.asarray(source_vertex, dtype=complex)
    if k.ndim != 2 or k.shape[0] != k.shape[1] or p.shape != k.shape:
        raise ValueError("matching square matrices required")
    if not np.all(np.isfinite(k)) or not np.all(np.isfinite(p)):
        raise ValueError("finite matrices required")
    if not np.allclose(k, k.conj().T, rtol=0.0, atol=1.0e-12):
        raise ValueError("Hermitian operator required")
    if not np.allclose(p, p.conj().T, rtol=0.0, atol=1.0e-12):
        raise ValueError("Hermitian source vertex required")
    floor = float(spectral_floor)
    if not math.isfinite(floor) or floor <= 0.0:
        raise ValueError("finite positive spectral floor required")

    eigenvalues, basis = np.linalg.eigh(k)
    if float(np.min(eigenvalues)) < -1.0e-12:
        raise ValueError("nonnegative operator required")
    source_in_basis = basis.conj().T @ p @ basis
    diagonal_weights = np.real(np.diag(source_in_basis))
    selected = eigenvalues >= floor
    tail = float(
        np.sum(
            np.exp(-eigenvalues[selected])
            * np.abs(diagonal_weights[selected])
            / eigenvalues[selected]
        )
    )
    heat_half = (basis * np.exp(-0.5 * eigenvalues)) @ basis.conj().T
    sandwich = heat_half @ p @ heat_half
    trace_norm = float(np.sum(np.linalg.svd(sandwich, compute_uv=False)))
    bound = e1_high_energy_trace_norm_bound(trace_norm, floor)
    return {
        "actual_weighted_tail": tail,
        "heat_sandwiched_trace_norm": trace_norm,
        "trace_norm_tail_bound": bound,
        "bound_residual": bound - tail,
    }


__all__ = [
    "e1_high_energy_trace_norm_bound",
    "factorized_heat_sandwich_trace_norm_bound",
    "finite_matrix_e1_high_energy_witness",
]
