"""Action-owned bare vertices and tree exchange amplitudes.

This is general diagram algebra applied to BHSM objects.  Every external mode,
quadratic symbol, cubic vertex, and quartic contact must come from the same
physical action expansion.  The module performs no empirical matching and no
explicit matrix inversion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy import linalg

from bhsm.interface.universal_physical_action_expansion import PhysicalActionExpansion
from bhsm.interface.universal_quadratic_spectrum import QuadraticDescriptorPencil


Array = np.ndarray


@dataclass(frozen=True)
class BareVertexGenerator:
    expansion: PhysicalActionExpansion

    def cubic(self, first: Array, second: Array, third: Array) -> complex:
        return complex(self.expansion.s3(first, second, third))

    def quartic(self, first: Array, second: Array, third: Array, fourth: Array) -> complex:
        return complex(self.expansion.s4(first, second, third, fourth))

    def cubic_internal_covector(self, first: Array, second: Array) -> Array:
        """Return ``S3(first,second,e_i)`` in the quotient basis."""

        basis = np.eye(self.expansion.background.physical_dimension)
        return np.asarray([self.cubic(first, second, mode) for mode in basis])


@dataclass(frozen=True)
class TreeAmplitude:
    contact: complex
    exchange: complex
    total: complex
    spectral_parameter: complex
    channel: str
    linear_solve_relative_residual: float


@dataclass(frozen=True)
class FullTreeAmplitude:
    contact: complex
    exchanges: dict[str, complex]
    total: complex
    spectral_parameters: dict[str, complex]
    maximum_linear_solve_relative_residual: float


@dataclass(frozen=True)
class TreeAmplitudeAssembler:
    quadratic: QuadraticDescriptorPencil
    vertices: BareVertexGenerator

    def __post_init__(self) -> None:
        background = self.vertices.expansion.background
        if self.quadratic.dimension != background.physical_dimension:
            raise ValueError("quadratic symbol and vertex quotient dimensions differ")
        if self.quadratic.action_version != background.action_version:
            raise ValueError("quadratic and vertices must come from the same action version")
        if self.quadratic.background_id != background.background_id:
            raise ValueError("quadratic and vertices must come from the same background")

    def four_point_channel(
        self,
        external_modes: Sequence[Array],
        spectral_parameter: complex,
        *,
        channel: str,
    ) -> TreeAmplitude:
        """Assemble one cubic-exchange channel plus the quartic contact.

        The ordered external tuple is ``(a,b,c,d)``.  Crossing is represented
        by passing the corresponding ordering and channel spectral parameter.
        Tensor, spin, gauge, color, flavor, and momentum indices remain inside
        the physical mode vectors and action derivatives supplied upstream.
        """

        if len(external_modes) != 4:
            raise ValueError("a four-point channel needs four external modes")
        if channel not in {"s", "t", "u", "direct"}:
            raise ValueError("channel must be s, t, u, or direct")
        modes = tuple(np.asarray(mode, dtype=complex) for mode in external_modes)
        expected = (self.quadratic.dimension,)
        if any(mode.shape != expected for mode in modes):
            raise ValueError("external mode has the wrong quotient dimension")

        left = self.vertices.cubic_internal_covector(modes[0], modes[1])
        right = self.vertices.cubic_internal_covector(modes[2], modes[3])
        symbol = self.quadratic.symbol(spectral_parameter)
        internal = linalg.solve(symbol, right, assume_a="gen", check_finite=True)
        residual = symbol @ internal - right
        denominator = max(
            np.linalg.norm(symbol, ord=2) * np.linalg.norm(internal),
            np.linalg.norm(right),
            np.finfo(float).tiny,
        )
        relative_residual = float(np.linalg.norm(residual) / denominator)
        exchange = complex(left @ internal)
        contact = self.vertices.quartic(*modes)
        return TreeAmplitude(
            contact=contact,
            exchange=exchange,
            total=contact + exchange,
            spectral_parameter=complex(spectral_parameter),
            channel=channel,
            linear_solve_relative_residual=relative_residual,
        )

    def four_point_total(
        self,
        external_modes: Sequence[Array],
        spectral_parameters: dict[str, complex],
    ) -> FullTreeAmplitude:
        """Assemble contact plus requested ``s/t/u`` exchanges exactly once.

        External modes already carry the caller's all-incoming/crossing sign
        convention.  This method supplies only the three canonical pairings
        and prevents accidental triple counting of the quartic contact.
        """

        if len(external_modes) != 4:
            raise ValueError("a four-point amplitude needs four external modes")
        if not spectral_parameters or not set(spectral_parameters) <= {"s", "t", "u"}:
            raise ValueError("spectral parameters must select one or more of s, t, u")
        modes = tuple(np.asarray(mode, dtype=complex) for mode in external_modes)
        expected = (self.quadratic.dimension,)
        if any(mode.shape != expected for mode in modes):
            raise ValueError("external mode has the wrong quotient dimension")
        pairings = {
            "s": ((0, 1), (2, 3)),
            "t": ((0, 2), (1, 3)),
            "u": ((0, 3), (1, 2)),
        }
        exchanges: dict[str, complex] = {}
        residuals: list[float] = []
        for channel, spectral_parameter in spectral_parameters.items():
            left_pair, right_pair = pairings[channel]
            left = self.vertices.cubic_internal_covector(
                modes[left_pair[0]], modes[left_pair[1]],
            )
            right = self.vertices.cubic_internal_covector(
                modes[right_pair[0]], modes[right_pair[1]],
            )
            symbol = self.quadratic.symbol(spectral_parameter)
            internal = linalg.solve(symbol, right, assume_a="gen", check_finite=True)
            residual = symbol @ internal - right
            denominator = max(
                np.linalg.norm(symbol, ord=2) * np.linalg.norm(internal),
                np.linalg.norm(right),
                np.finfo(float).tiny,
            )
            residuals.append(float(np.linalg.norm(residual) / denominator))
            exchanges[channel] = complex(left @ internal)
        contact = self.vertices.quartic(*modes)
        return FullTreeAmplitude(
            contact=contact,
            exchanges=exchanges,
            total=contact + sum(exchanges.values()),
            spectral_parameters={
                channel: complex(value) for channel, value in spectral_parameters.items()
            },
            maximum_linear_solve_relative_residual=max(residuals, default=0.0),
        )

    def require_physical_promotion(self) -> None:
        self.vertices.expansion.require_physical_promotion()
        self.quadratic.require_physical_promotion()

    def metadata(self) -> dict:
        return {
            "action_version": self.quadratic.action_version,
            "background_id": self.quadratic.background_id,
            "domain_id": self.quadratic.domain_id,
            "assembly_identity": "M4=V4+V3_left*Gamma2(z)^(-1)*V3_right",
            "explicit_matrix_inverse_formed": False,
            "external_physics_vertex_inserted": False,
            "lsz_and_phase_space": "DOWNSTREAM",
            "loop_completion": "DOWNSTREAM",
        }


__all__ = [
    "BareVertexGenerator",
    "FullTreeAmplitude",
    "TreeAmplitude",
    "TreeAmplitudeAssembler",
]
