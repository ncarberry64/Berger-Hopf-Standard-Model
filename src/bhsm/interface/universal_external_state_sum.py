"""External-state sums and density-matrix averages for BHSM amplitudes.

The amplitude callback and every state vector must come from one BHSM
physical quotient.  This module supplies only the finite-dimensional quantum
state contraction.  It does not insert particle multiplicities, Standard
Model polarization rules, symmetry factors, or measured branching data.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Callable, Mapping, Sequence

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class ExternalStateBasis:
    """An orthonormal set of physical quotient modes for one external leg."""

    modes: Array
    state_space_id: str

    def __post_init__(self) -> None:
        modes = np.asarray(self.modes, dtype=complex)
        if modes.ndim != 2 or modes.shape[0] == 0 or modes.shape[1] == 0:
            raise ValueError("external-state modes must have shape (states, quotient dimension)")
        if not np.all(np.isfinite(modes)):
            raise ValueError("external-state modes must be finite")
        gram = modes.conj() @ modes.T
        if not np.allclose(gram, np.eye(modes.shape[0]), rtol=1.0e-11, atol=1.0e-12):
            raise ValueError("external-state modes must be orthonormal")
        if not self.state_space_id:
            raise ValueError("state_space_id must be nonempty")
        object.__setattr__(self, "modes", modes)

    @property
    def state_count(self) -> int:
        return int(self.modes.shape[0])

    @property
    def quotient_dimension(self) -> int:
        return int(self.modes.shape[1])


@dataclass(frozen=True)
class ExternalStateSumResult:
    amplitude_squared: float
    amplitude_evaluations: int
    basis_dimensions: tuple[int, ...]
    incoming_legs: tuple[int, ...]
    coherent_density_matrices_used: bool


def _density_matrix(value: Array, dimension: int) -> Array:
    density = np.asarray(value, dtype=complex)
    if density.shape != (dimension, dimension):
        raise ValueError("incoming density matrix has the wrong dimension")
    if not np.all(np.isfinite(density)):
        raise ValueError("incoming density matrix must be finite")
    if not np.allclose(density, density.conj().T, rtol=1.0e-11, atol=1.0e-12):
        raise ValueError("incoming density matrix must be Hermitian")
    eigenvalues = np.linalg.eigvalsh(density)
    if float(np.min(eigenvalues)) < -1.0e-12:
        raise ValueError("incoming density matrix must be positive semidefinite")
    trace = np.trace(density)
    if abs(trace.imag) > 1.0e-12 or not np.isclose(trace.real, 1.0, rtol=1.0e-11, atol=1.0e-12):
        raise ValueError("incoming density matrix must have unit trace")
    return density


def external_state_amplitude_squared(
    amplitude: Callable[[tuple[Array, ...]], complex],
    bases: Sequence[ExternalStateBasis],
    *,
    incoming_legs: Sequence[int],
    incoming_density_matrices: Mapping[int, Array] | None = None,
) -> ExternalStateSumResult:
    """Sum final states and average or polarize incoming external states.

    Missing incoming density matrices default to the unpolarized state
    ``I/d``.  Outgoing legs use the identity, hence are summed rather than
    averaged.  Off-diagonal incoming density-matrix entries retain coherent
    interference.  Identical-particle factors remain the responsibility of
    the phase-space readout and must not be inserted here.
    """

    spaces = tuple(bases)
    if not spaces:
        raise ValueError("at least one external-state basis is required")
    quotient_dimension = spaces[0].quotient_dimension
    if any(space.quotient_dimension != quotient_dimension for space in spaces):
        raise ValueError("all external states must use the same physical quotient dimension")

    incoming = tuple(sorted(int(index) for index in incoming_legs))
    if len(incoming) != len(set(incoming)) or any(index < 0 or index >= len(spaces) for index in incoming):
        raise ValueError("incoming leg indices must be unique and in range")
    supplied = dict(incoming_density_matrices or {})
    if not set(supplied) <= set(incoming):
        raise ValueError("density matrices may be supplied only for incoming legs")

    contractions: list[Array] = []
    coherent = False
    for leg, space in enumerate(spaces):
        if leg not in incoming:
            contractions.append(np.eye(space.state_count, dtype=complex))
            continue
        if leg in supplied:
            density = _density_matrix(supplied[leg], space.state_count)
            coherent = coherent or bool(np.any(np.abs(density - np.diag(np.diag(density))) > 1.0e-14))
        else:
            density = np.eye(space.state_count, dtype=complex) / space.state_count
        contractions.append(density)

    dimensions = tuple(space.state_count for space in spaces)
    amplitudes = np.empty(dimensions, dtype=complex)
    for indices in itertools.product(*(range(dimension) for dimension in dimensions)):
        modes = tuple(space.modes[index] for space, index in zip(spaces, indices, strict=True))
        value = complex(amplitude(modes))
        if not np.isfinite(value):
            raise ArithmeticError("external-state amplitude must be finite")
        amplitudes[indices] = value

    total = 0.0j
    index_space = tuple(itertools.product(*(range(dimension) for dimension in dimensions)))
    for bra in index_space:
        conjugate = amplitudes[bra].conjugate()
        for ket in index_space:
            coefficient = 1.0 + 0.0j
            for leg, contraction in enumerate(contractions):
                coefficient *= contraction[bra[leg], ket[leg]]
                if coefficient == 0.0:
                    break
            total += conjugate * coefficient * amplitudes[ket]
    tolerance = 1.0e-12 * max(1.0, abs(total.real))
    if abs(total.imag) > tolerance or total.real < -tolerance:
        raise ArithmeticError("external-state contraction did not produce a nonnegative real norm")
    return ExternalStateSumResult(
        amplitude_squared=max(0.0, float(total.real)),
        amplitude_evaluations=int(amplitudes.size),
        basis_dimensions=dimensions,
        incoming_legs=incoming,
        coherent_density_matrices_used=coherent,
    )


__all__ = [
    "ExternalStateBasis",
    "ExternalStateSumResult",
    "external_state_amplitude_squared",
]
