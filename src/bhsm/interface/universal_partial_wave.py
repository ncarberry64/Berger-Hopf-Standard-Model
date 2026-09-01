"""Coupled-channel partial waves and unitarity diagnostics for BHSM amplitudes.

This module uses the declared scalar/helicity-zero convention

    M(s, cos(theta)) = 16*pi*sum_l (2*l+1) a_l(s) P_l(cos(theta)).

The amplitude, open-channel inventory, and phase-space factors must be
produced upstream by the same BHSM action and spectrum.  The implementation
adds no particle assignments, fitted cutoffs, or experimental inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class CoupledPartialWaveProjection:
    coefficients: Array
    maximum_angular_momentum: int
    quadrature_order: int
    channel_count: int
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        coefficients = np.asarray(self.coefficients, dtype=complex)
        expected = (
            self.maximum_angular_momentum + 1,
            self.channel_count,
            self.channel_count,
        )
        if coefficients.shape != expected or not np.all(np.isfinite(coefficients)):
            raise ValueError("partial-wave coefficient dimensions are inconsistent")
        if not self.action_version or not self.background_id or not self.provenance:
            raise ValueError("partial-wave action/background provenance is required")
        object.__setattr__(self, "coefficients", coefficients)


@dataclass(frozen=True)
class PartialWaveUnitarityRow:
    angular_momentum: int
    s_matrix: Array
    minimum_absorption_margin_eigenvalue: float
    maximum_unitarity_excess_eigenvalue: float
    complete_channel_relative_residual: float
    maximum_perturbative_real_eigenvalue: float
    perturbative_real_bound_satisfied: bool


@dataclass(frozen=True)
class PartialWaveUnitarityReport:
    rows: tuple[PartialWaveUnitarityRow, ...]
    phase_space_factors: Array
    complete_channel_ledger: bool
    maximum_unitarity_excess: float
    maximum_complete_channel_relative_residual: float
    perturbative_real_bound_satisfied: bool

    def require_unitarity(self, tolerance: float = 1.0e-10) -> None:
        if self.complete_channel_ledger:
            if self.maximum_complete_channel_relative_residual > tolerance:
                raise RuntimeError("complete coupled-channel partial waves violate unitarity")
        elif self.maximum_unitarity_excess > tolerance:
            raise RuntimeError("declared channel subspace has unitarity excess")


def project_coupled_partial_waves(
    amplitude: Callable[[float], Array],
    *,
    maximum_angular_momentum: int,
    quadrature_order: int = 48,
    action_version: str,
    background_id: str,
    provenance: tuple[str, ...],
) -> CoupledPartialWaveProjection:
    """Project a square open-channel amplitude matrix onto Legendre modes."""

    if maximum_angular_momentum < 0:
        raise ValueError("maximum angular momentum must be nonnegative")
    if quadrature_order <= maximum_angular_momentum:
        raise ValueError("quadrature order must exceed maximum angular momentum")
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    sampled: list[Array] = []
    channel_count: int | None = None
    for node in nodes:
        value = np.asarray(amplitude(float(node)), dtype=complex)
        if value.ndim != 2 or value.shape[0] != value.shape[1] or value.shape[0] == 0:
            raise ValueError("partial-wave amplitude must be a nonempty square matrix")
        if channel_count is None:
            channel_count = int(value.shape[0])
        if value.shape != (channel_count, channel_count):
            raise ValueError("amplitude channel dimension changed across scattering angle")
        if not np.all(np.isfinite(value)):
            raise ValueError("partial-wave amplitude must be finite")
        sampled.append(value)
    values = np.asarray(sampled)
    coefficients = []
    for angular_momentum in range(maximum_angular_momentum + 1):
        polynomial = np.polynomial.legendre.legval(
            nodes,
            np.eye(maximum_angular_momentum + 1)[angular_momentum],
        )
        coefficients.append(
            np.einsum("q,qij->ij", weights * polynomial, values)
            / (32.0 * math.pi)
        )
    return CoupledPartialWaveProjection(
        coefficients=np.asarray(coefficients),
        maximum_angular_momentum=maximum_angular_momentum,
        quadrature_order=quadrature_order,
        channel_count=int(channel_count),
        action_version=action_version,
        background_id=background_id,
        provenance=provenance,
    )


def analyze_partial_wave_unitarity(
    projection: CoupledPartialWaveProjection,
    phase_space_factors: Array,
    *,
    complete_channel_ledger: bool,
    tolerance: float = 1.0e-10,
) -> PartialWaveUnitarityReport:
    """Evaluate coupled-channel ``S=I+2i sqrt(rho) a sqrt(rho)``.

    A complete open-channel ledger requires ``S^dagger S=I``.  For an
    explicitly incomplete subspace, only positive unitarity excess is a
    contradiction; norm lost to omitted channels is recorded as absorption.
    The conventional perturbative diagnostic is
    ``max |eig(Re(sqrt(rho) a sqrt(rho)))| <= 1/2``.
    """

    rho = np.asarray(phase_space_factors, dtype=float)
    if rho.shape != (projection.channel_count,):
        raise ValueError("one phase-space factor is required per open channel")
    if not np.all(np.isfinite(rho)) or np.min(rho) <= 0.0 or np.max(rho) > 1.0 + tolerance:
        raise ValueError("open-channel phase-space factors must lie in (0, 1]")
    root = np.diag(np.sqrt(rho))
    identity = np.eye(projection.channel_count, dtype=complex)
    rows: list[PartialWaveUnitarityRow] = []
    for angular_momentum, coefficient in enumerate(projection.coefficients):
        reduced = root @ coefficient @ root
        scattering = identity + 2.0j * reduced
        gram = scattering.conj().T @ scattering
        absorption = identity - gram
        absorption = 0.5 * (absorption + absorption.conj().T)
        excess = gram - identity
        excess = 0.5 * (excess + excess.conj().T)
        scale = max(float(np.linalg.norm(gram, ord=2)), 1.0)
        hermitian_real = 0.5 * (reduced + reduced.conj().T)
        maximum_real = float(np.max(np.abs(np.linalg.eigvalsh(hermitian_real))))
        rows.append(PartialWaveUnitarityRow(
            angular_momentum=angular_momentum,
            s_matrix=scattering,
            minimum_absorption_margin_eigenvalue=float(np.min(np.linalg.eigvalsh(absorption))),
            maximum_unitarity_excess_eigenvalue=float(np.max(np.linalg.eigvalsh(excess))),
            complete_channel_relative_residual=float(np.linalg.norm(gram - identity, ord=2) / scale),
            maximum_perturbative_real_eigenvalue=maximum_real,
            perturbative_real_bound_satisfied=maximum_real <= 0.5 + tolerance,
        ))
    return PartialWaveUnitarityReport(
        rows=tuple(rows),
        phase_space_factors=rho,
        complete_channel_ledger=bool(complete_channel_ledger),
        maximum_unitarity_excess=max(row.maximum_unitarity_excess_eigenvalue for row in rows),
        maximum_complete_channel_relative_residual=max(
            row.complete_channel_relative_residual for row in rows
        ),
        perturbative_real_bound_satisfied=all(
            row.perturbative_real_bound_satisfied for row in rows
        ),
    )


__all__ = [
    "CoupledPartialWaveProjection",
    "PartialWaveUnitarityReport",
    "PartialWaveUnitarityRow",
    "analyze_partial_wave_unitarity",
    "project_coupled_partial_waves",
]
