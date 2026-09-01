"""Inverse-free quadratic descriptor pencil for BHSM poles and residues.

The input matrices must already be the physical-quotient second variation of
the retained action.  This module supplies the general descriptor algebra; it
does not invent a momentum map, gauge fixing, field normalization, or mass
scale.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy import linalg


Array = np.ndarray

if TYPE_CHECKING:
    from bhsm.interface.universal_brst_quotient import BRSTPhysicalQuotient


@dataclass(frozen=True)
class PoleResidue:
    spectral_parameter: complex
    right_mode: Array
    left_mode: Array
    residue: Array
    normalization: complex
    finite: bool
    simple: bool


@dataclass(frozen=True)
class QuadraticDescriptorPencil:
    """Physical quadratic symbol ``Gamma2(z)=constant+z*linear``."""

    constant: Array
    linear: Array
    action_version: str
    background_id: str
    domain_id: str
    gate7_closed: bool
    quotient_applied: bool
    brst_cancellation_accounted: bool
    scale_map_id: str | None = None

    def __post_init__(self) -> None:
        constant = np.asarray(self.constant, dtype=complex)
        linear = np.asarray(self.linear, dtype=complex)
        if constant.ndim != 2 or constant.shape[0] != constant.shape[1]:
            raise ValueError("constant symbol must be square")
        if linear.shape != constant.shape:
            raise ValueError("constant and linear symbols must have the same shape")
        if not np.all(np.isfinite(constant)) or not np.all(np.isfinite(linear)):
            raise ValueError("quadratic pencil must be finite")
        if not self.quotient_applied:
            raise ValueError("quadratic pencil must be restricted to the physical quotient")
        object.__setattr__(self, "constant", constant)
        object.__setattr__(self, "linear", linear)

    @property
    def dimension(self) -> int:
        return int(self.constant.shape[0])

    def symbol(self, spectral_parameter: complex) -> Array:
        return self.constant + complex(spectral_parameter) * self.linear

    def poles_and_residues(self, simplicity_tolerance: float = 1.0e-9) -> tuple[PoleResidue, ...]:
        """Solve the generalized descriptor problem without forming ``K1^-1``."""

        eigenvalues, left, right = linalg.eig(
            -self.constant,
            self.linear,
            left=True,
            right=True,
            homogeneous_eigvals=False,
            check_finite=True,
        )
        finite_values = eigenvalues[np.isfinite(eigenvalues)]
        result: list[PoleResidue] = []
        for index, value in enumerate(eigenvalues):
            finite = bool(np.isfinite(value))
            right_mode = right[:, index]
            left_mode = left[:, index]
            normalization = complex(left_mode.conj().T @ self.linear @ right_mode)
            if finite:
                separation = np.abs(finite_values - value)
                threshold = simplicity_tolerance * max(1.0, abs(value))
                simple = bool(
                    abs(normalization) > simplicity_tolerance
                    and int(np.count_nonzero(separation <= threshold)) == 1
                )
            else:
                simple = False
            residue = (
                np.outer(right_mode, left_mode.conj()) / normalization
                if finite and abs(normalization) > simplicity_tolerance
                else np.full(self.constant.shape, np.nan + 0.0j)
            )
            result.append(PoleResidue(
                spectral_parameter=complex(value),
                right_mode=right_mode,
                left_mode=left_mode,
                residue=residue,
                normalization=normalization,
                finite=finite,
                simple=simple,
            ))
        return tuple(result)

    def require_physical_promotion(self) -> None:
        missing: list[str] = []
        if not self.gate7_closed:
            missing.append("Gate7_closed_background")
        if not self.brst_cancellation_accounted:
            missing.append("Ward_BRST_cancellation")
        if self.scale_map_id is None:
            missing.append("universal_physical_scale_map")
        if missing:
            raise RuntimeError("physical pole promotion blocked by: " + ", ".join(missing))

    def metadata(self) -> dict:
        return {
            "action_version": self.action_version,
            "background_id": self.background_id,
            "domain_id": self.domain_id,
            "dimension": self.dimension,
            "descriptor_solver": "GENERALIZED_EIGENPROBLEM_NO_EXPLICIT_KINETIC_INVERSE",
            "quotient_applied": self.quotient_applied,
            "brst_cancellation_accounted": self.brst_cancellation_accounted,
            "scale_map_id": self.scale_map_id,
            "physical_promotion_ready": bool(
                self.gate7_closed
                and self.brst_cancellation_accounted
                and self.scale_map_id is not None
            ),
            "empirical_particle_input_used": False,
        }


def quadratic_pencil_from_brst_quotient(
    quotient: "BRSTPhysicalQuotient",
    *,
    domain_id: str,
    gate7_closed: bool,
    scale_map_id: str | None,
    brst_tolerance: float = 1.0e-10,
) -> QuadraticDescriptorPencil:
    """Construct a descriptor pencil only after the explicit BRST checks pass."""

    quotient.require_regular_brst_quotient(tolerance=brst_tolerance)
    return QuadraticDescriptorPencil(
        constant=quotient.quotient_constant,
        linear=quotient.quotient_linear,
        action_version=quotient.action_version,
        background_id=quotient.background_id,
        domain_id=domain_id,
        gate7_closed=gate7_closed,
        quotient_applied=True,
        brst_cancellation_accounted=True,
        scale_map_id=scale_map_id,
    )


__all__ = [
    "PoleResidue",
    "QuadraticDescriptorPencil",
    "quadratic_pencil_from_brst_quotient",
]
