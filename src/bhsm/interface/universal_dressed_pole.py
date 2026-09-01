"""Inverse-free complex poles of a renormalized BHSM two-point symbol.

The caller supplies the complete same-action inverse two-point symbol and its
spectral derivative.  A bordered Newton solve tracks one selected simple
mode without evaluating a determinant or forming a propagator inverse.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np
from scipy import linalg


Array = np.ndarray


@dataclass(frozen=True)
class DressedPole:
    spectral_parameter: complex
    pole_mass: float
    pole_width: float
    right_mode: Array
    left_mode: Array
    residue: Array
    relative_symbol_residual: float
    descriptor_derivative_normalization: complex
    bordered_iterations: int
    converged: bool
    simple: bool
    causal_width: bool
    complete_self_energy_ledger: bool
    gate7_closed: bool
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def require_physical_promotion(self, tolerance: float = 1.0e-10) -> None:
        blockers: list[str] = []
        if not self.gate7_closed:
            blockers.append("Gate7_closed_background")
        if not self.complete_self_energy_ledger:
            blockers.append("complete_same_action_self_energy_ledger")
        if not self.converged or self.relative_symbol_residual > tolerance:
            blockers.append("converged_complex_pole")
        if not self.simple:
            blockers.append("simple_isolated_pole")
        if not self.causal_width:
            blockers.append("nonnegative_pole_width")
        if blockers:
            raise RuntimeError("dressed-pole promotion blocked by: " + ", ".join(blockers))


def solve_dressed_pole(
    inverse_symbol: Callable[[complex], Array],
    inverse_symbol_derivative: Callable[[complex], Array],
    initial_spectral_parameter: complex,
    initial_right_mode: Array,
    *,
    anchor_mode: Array | None = None,
    action_version: str,
    background_id: str,
    provenance: tuple[str, ...],
    complete_self_energy_ledger: bool,
    gate7_closed: bool,
    tolerance: float = 1.0e-12,
    maximum_iterations: int = 20,
) -> DressedPole:
    """Track one simple pole with the bordered eigenpair equations.

    The solved equations are ``Gamma(z) r=0`` and ``c^dagger r=1``.  Pole
    mass and width use the convention ``z_p=m_p^2-i m_p Gamma_p``; this is a
    readout of the computed pole, not a fitted line shape.
    """

    if not action_version or not background_id or not provenance:
        raise ValueError("dressed-pole action/background provenance is required")
    if tolerance <= 0.0 or maximum_iterations < 1:
        raise ValueError("pole solver tolerance and iteration count must be positive")
    right = np.asarray(initial_right_mode, dtype=complex)
    if right.ndim != 1 or right.size == 0 or not np.all(np.isfinite(right)):
        raise ValueError("initial right mode must be a finite nonempty vector")
    anchor = np.asarray(right if anchor_mode is None else anchor_mode, dtype=complex)
    if anchor.shape != right.shape or not np.all(np.isfinite(anchor)):
        raise ValueError("anchor mode must match the right mode")
    overlap = complex(np.vdot(anchor, right))
    if abs(overlap) <= np.finfo(float).tiny:
        raise ValueError("anchor mode is orthogonal to the initial right mode")
    right = right / overlap
    spectral = complex(initial_spectral_parameter)
    dimension = right.size
    converged = False
    relative_residual = math.inf
    iterations = 0
    for iterations in range(1, maximum_iterations + 1):
        symbol = np.asarray(inverse_symbol(spectral), dtype=complex)
        derivative = np.asarray(inverse_symbol_derivative(spectral), dtype=complex)
        if symbol.shape != (dimension, dimension) or derivative.shape != symbol.shape:
            raise ValueError("inverse symbol and derivative dimensions must match the mode")
        if not np.all(np.isfinite(symbol)) or not np.all(np.isfinite(derivative)):
            raise ArithmeticError("inverse symbol data must be finite")
        field_residual = symbol @ right
        normalization_residual = complex(np.vdot(anchor, right) - 1.0)
        scale = max(
            float(np.linalg.norm(symbol, ord=2) * np.linalg.norm(right)),
            float(
                np.linalg.norm(derivative, ord=2)
                * max(1.0, abs(spectral))
                * np.linalg.norm(right)
            ),
            np.finfo(float).tiny,
        )
        relative_residual = max(
            float(np.linalg.norm(field_residual) / scale),
            abs(normalization_residual),
        )
        if relative_residual <= tolerance:
            converged = True
            break
        bordered = np.block([
            [symbol, (derivative @ right)[:, None]],
            [anchor.conj()[None, :], np.zeros((1, 1), dtype=complex)],
        ])
        correction = linalg.solve(
            bordered,
            np.concatenate((field_residual, [normalization_residual])),
            assume_a="gen",
            check_finite=True,
        )
        right = right - correction[:dimension]
        spectral = spectral - correction[-1]

    symbol = np.asarray(inverse_symbol(spectral), dtype=complex)
    derivative = np.asarray(inverse_symbol_derivative(spectral), dtype=complex)
    final_field_residual = symbol @ right
    final_normalization_residual = complex(np.vdot(anchor, right) - 1.0)
    final_scale = max(
        float(np.linalg.norm(symbol, ord=2) * np.linalg.norm(right)),
        float(
            np.linalg.norm(derivative, ord=2)
            * max(1.0, abs(spectral))
            * np.linalg.norm(right)
        ),
        np.finfo(float).tiny,
    )
    relative_residual = max(
        float(np.linalg.norm(final_field_residual) / final_scale),
        abs(final_normalization_residual),
    )
    converged = converged or relative_residual <= tolerance
    left_vectors, singular_values, _right_vectors = linalg.svd(
        symbol,
        full_matrices=True,
        check_finite=True,
    )
    left = left_vectors[:, -1]
    left_right = complex(np.vdot(left, right))
    if abs(left_right) <= np.finfo(float).tiny:
        raise ArithmeticError("left and right pole modes have zero pairing")
    left = left / np.conjugate(left_right)
    normalization = complex(np.vdot(left, derivative @ right))
    simple_gap = (
        math.inf
        if dimension == 1
        else float(singular_values[-2] / max(singular_values[0], np.finfo(float).tiny))
    )
    simple = abs(normalization) > tolerance and simple_gap > tolerance
    residue = np.outer(right, left.conj()) / normalization
    real_pole = float(spectral.real)
    mass = math.sqrt(real_pole) if real_pole >= 0.0 else math.nan
    if mass > 0.0:
        width = -float(spectral.imag) / mass
    elif spectral.imag == 0.0 and mass == 0.0:
        width = 0.0
    else:
        width = math.nan
    causal = math.isfinite(width) and width >= -tolerance
    if causal and width < 0.0:
        width = 0.0
    return DressedPole(
        spectral_parameter=spectral,
        pole_mass=mass,
        pole_width=width,
        right_mode=right,
        left_mode=left,
        residue=residue,
        relative_symbol_residual=relative_residual,
        descriptor_derivative_normalization=normalization,
        bordered_iterations=iterations,
        converged=converged,
        simple=simple,
        causal_width=causal,
        complete_self_energy_ledger=bool(complete_self_energy_ledger),
        gate7_closed=bool(gate7_closed),
        action_version=action_version,
        background_id=background_id,
        provenance=provenance,
    )


__all__ = ["DressedPole", "solve_dressed_pole"]
