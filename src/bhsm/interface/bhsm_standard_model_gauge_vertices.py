"""BHSM-owned Standard-Model representation and gauge-vertex tensors.

The chiral multiplets and hypercharges come from the retained BHSM bundle.
Pauli/Gell-Mann matrices and Lie brackets are representation mathematics.
Only an action-derived local form-factor normalization may be attached as a
physical coupling; no measured coupling or hand-written particle vertex is
accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from bhsm.interface.particle_chirality_anomaly_normalization import (
    Multiplet,
    one_family_multiplets,
)


Array = np.ndarray


def su2_fundamental_generators() -> tuple[Array, ...]:
    i = 1j
    return (
        np.asarray([[0, 1], [1, 0]], dtype=complex) / 2.0,
        np.asarray([[0, -i], [i, 0]], dtype=complex) / 2.0,
        np.asarray([[1, 0], [0, -1]], dtype=complex) / 2.0,
    )


def su3_fundamental_generators() -> tuple[Array, ...]:
    i = 1j
    matrices = (
        [[0, 1, 0], [1, 0, 0], [0, 0, 0]],
        [[0, -i, 0], [i, 0, 0], [0, 0, 0]],
        [[1, 0, 0], [0, -1, 0], [0, 0, 0]],
        [[0, 0, 1], [0, 0, 0], [1, 0, 0]],
        [[0, 0, -i], [0, 0, 0], [i, 0, 0]],
        [[0, 0, 0], [0, 0, 1], [0, 1, 0]],
        [[0, 0, 0], [0, 0, -i], [0, i, 0]],
        [[1 / np.sqrt(3), 0, 0], [0, 1 / np.sqrt(3), 0], [0, 0, -2 / np.sqrt(3)]],
    )
    return tuple(np.asarray(matrix, dtype=complex) / 2.0 for matrix in matrices)


def _multiplet(name: str) -> Multiplet:
    lookup = {row.name: row for row in one_family_multiplets(include_neutral_singlet=True)}
    if name not in lookup:
        raise KeyError(name)
    return lookup[name]


def multiplet_generators(name: str, group: str) -> tuple[Array, ...]:
    row = _multiplet(name)
    color_identity = np.eye(row.su3_dimension, dtype=complex)
    weak_identity = np.eye(row.sp1_dimension, dtype=complex)
    if group == "SU3":
        if row.su3 == "1":
            base = (np.zeros((1, 1), dtype=complex),) * 8
        elif row.su3 == "3":
            base = su3_fundamental_generators()
        elif row.su3 == "conjugate(3)":
            base = tuple(-generator.conj() for generator in su3_fundamental_generators())
        else:
            raise ValueError("unsupported retained SU3 representation")
        return tuple(np.kron(generator, weak_identity) for generator in base)
    if group == "SU2":
        base = (
            su2_fundamental_generators()
            if row.sp1 == "2"
            else (np.zeros((1, 1), dtype=complex),) * 3
        )
        return tuple(np.kron(color_identity, generator) for generator in base)
    if group == "U1":
        return (float(row.Y) * np.eye(row.complex_dimension, dtype=complex),)
    raise ValueError("group must be SU3, SU2, or U1")


def structure_constants(generators: tuple[Array, ...]) -> Array:
    """Compute ``f_abc`` from ``[T_a,T_b]=i f_abc T_c``."""

    count = len(generators)
    result = np.zeros((count, count, count), dtype=float)
    for a, first in enumerate(generators):
        for b, second in enumerate(generators):
            commutator = first @ second - second @ first
            for c, third in enumerate(generators):
                result[a, b, c] = float(np.real(-2j * np.trace(commutator @ third)))
    return result


@dataclass(frozen=True)
class ActionGaugeCoupling:
    group: str
    value: float
    action_version: str
    background_id: str
    local_form_factor_id: str
    provenance: tuple[str, ...]
    derived_from_retained_local_form_factor: bool

    def __post_init__(self) -> None:
        if self.group not in {"SU3", "SU2", "U1"}:
            raise ValueError("unknown gauge group")
        if not np.isfinite(self.value) or self.value <= 0.0:
            raise ValueError("gauge coupling must be finite and positive")
        if not self.derived_from_retained_local_form_factor:
            raise ValueError("gauge coupling must come from the retained local form factor")
        if not self.local_form_factor_id or not self.provenance:
            raise ValueError("gauge-coupling provenance is required")


def fermion_gauge_vertex(
    multiplet_name: str,
    coupling: ActionGaugeCoupling,
) -> tuple[Array, ...]:
    """Return the internal ``g T_a`` tensors of the covariant derivative."""

    return tuple(coupling.value * generator for generator in multiplet_generators(
        multiplet_name, coupling.group,
    ))


def three_gauge_vertex_color_tensor(coupling: ActionGaugeCoupling) -> Array:
    if coupling.group == "U1":
        return np.zeros((1, 1, 1), dtype=float)
    generators = (
        su3_fundamental_generators()
        if coupling.group == "SU3"
        else su2_fundamental_generators()
    )
    return coupling.value * structure_constants(generators)


__all__ = [
    "ActionGaugeCoupling",
    "fermion_gauge_vertex",
    "multiplet_generators",
    "structure_constants",
    "su2_fundamental_generators",
    "su3_fundamental_generators",
    "three_gauge_vertex_color_tensor",
]
