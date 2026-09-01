"""Source-contracted retarded spectral density for BHSM two-point symbols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy import linalg


Array = np.ndarray


@dataclass(frozen=True)
class SpectralDensityResult:
    spectral_points: Array
    density_matrices: Array
    minimum_density_eigenvalue: float
    maximum_linear_solve_relative_residual: float
    maximum_symbol_condition_number: float
    positive_semidefinite: bool
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
        if self.maximum_linear_solve_relative_residual > tolerance:
            blockers.append("retarded_symbol_solve")
        if self.minimum_density_eigenvalue < -tolerance or not self.positive_semidefinite:
            blockers.append("positive_spectral_measure")
        if blockers:
            raise RuntimeError("spectral-density promotion blocked by: " + ", ".join(blockers))


def source_contracted_spectral_density(
    inverse_retarded_symbol: Callable[[float], Array],
    spectral_points: Sequence[float],
    source_frame: Array,
    *,
    action_version: str,
    background_id: str,
    provenance: tuple[str, ...],
    complete_self_energy_ledger: bool,
    gate7_closed: bool,
    positivity_tolerance: float = 1.0e-10,
) -> SpectralDensityResult:
    """Evaluate ``rho=-(1/pi) Im(B^dagger Gamma_R^-1 B)`` by solves.

    ``B`` is an action-owned physical source frame.  The source contraction
    may be rectangular and therefore avoids assigning a basis to unobserved
    ambient directions.  A retarded sign convention is required upstream.
    """

    points = np.asarray(tuple(spectral_points), dtype=float)
    frame = np.asarray(source_frame, dtype=complex)
    if points.ndim != 1 or points.size == 0 or not np.all(np.isfinite(points)):
        raise ValueError("spectral points must be a finite nonempty sequence")
    if np.any(np.diff(points) <= 0.0):
        raise ValueError("spectral points must be strictly increasing")
    if frame.ndim != 2 or frame.shape[0] == 0 or frame.shape[1] == 0:
        raise ValueError("source frame must have shape (field, source)")
    if not np.all(np.isfinite(frame)):
        raise ValueError("source frame must be finite")
    if not action_version or not background_id or not provenance:
        raise ValueError("spectral-density action/background provenance is required")

    densities: list[Array] = []
    residuals: list[float] = []
    conditions: list[float] = []
    minimum_eigenvalue = np.inf
    for point in points:
        symbol = np.asarray(inverse_retarded_symbol(float(point)), dtype=complex)
        if symbol.shape != (frame.shape[0], frame.shape[0]):
            raise ValueError("retarded symbol and source-frame dimensions differ")
        if not np.all(np.isfinite(symbol)):
            raise ArithmeticError("retarded symbol must be finite")
        response = linalg.solve(symbol, frame, assume_a="gen", check_finite=True)
        solve_residual = symbol @ response - frame
        denominator = max(
            float(np.linalg.norm(symbol, ord=2) * np.linalg.norm(response, ord=2)),
            float(np.linalg.norm(frame, ord=2)),
            np.finfo(float).tiny,
        )
        residuals.append(float(np.linalg.norm(solve_residual, ord=2) / denominator))
        conditions.append(float(np.linalg.cond(symbol)))
        contracted = frame.conj().T @ response
        density = -(contracted - contracted.conj().T) / (2.0j * np.pi)
        density = 0.5 * (density + density.conj().T)
        eigenvalue = float(np.min(np.linalg.eigvalsh(density)))
        minimum_eigenvalue = min(minimum_eigenvalue, eigenvalue)
        densities.append(density)
    return SpectralDensityResult(
        spectral_points=points,
        density_matrices=np.asarray(densities),
        minimum_density_eigenvalue=minimum_eigenvalue,
        maximum_linear_solve_relative_residual=max(residuals),
        maximum_symbol_condition_number=max(conditions),
        positive_semidefinite=minimum_eigenvalue >= -positivity_tolerance,
        complete_self_energy_ledger=bool(complete_self_energy_ledger),
        gate7_closed=bool(gate7_closed),
        action_version=action_version,
        background_id=background_id,
        provenance=provenance,
    )


__all__ = ["SpectralDensityResult", "source_contracted_spectral_density"]
