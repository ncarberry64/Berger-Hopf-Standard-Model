"""Universal inverse-free action expansion on a physical tangent quotient.

The module is deliberately upstream of particle naming and experimental
comparison.  It contracts derivatives of one supplied action at one supplied
background, after applying an explicit physical quotient frame.  Cubic and
quartic entries are evaluated matrix-free, so no dense fourth-order tensor is
formed.

Gate-7 closure is a promotion boundary, not a numerical prerequisite: a
provisional background may be explored, but pole/particle/prediction exports
remain disabled until the caller supplies a Gate-7-closed background.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

import numpy as np


Array = np.ndarray


class DirectionalActionOracle(Protocol):
    """Scalar action and its exact directional derivatives through order four."""

    def value(self, state: Array) -> float: ...

    def derivative(self, state: Array, directions: Sequence[Array]) -> float: ...


@dataclass(frozen=True)
class PhysicalBackground:
    """One action background and its intrinsic physical tangent frame."""

    state: Array
    physical_frame: Array
    action_version: str
    background_id: str
    gate7_closed: bool
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        state = np.asarray(self.state, dtype=float)
        frame = np.asarray(self.physical_frame, dtype=float)
        if state.ndim != 1:
            raise ValueError("state must be one-dimensional")
        if frame.ndim != 2 or frame.shape[0] != state.size:
            raise ValueError("physical_frame must have shape (ambient, physical)")
        gram = frame.T @ frame
        if not np.allclose(gram, np.eye(frame.shape[1]), rtol=1.0e-11, atol=1.0e-12):
            raise ValueError("physical_frame columns must be orthonormal")
        if not np.all(np.isfinite(state)) or not np.all(np.isfinite(frame)):
            raise ValueError("background data must be finite")
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "physical_frame", frame)

    @property
    def physical_dimension(self) -> int:
        return int(self.physical_frame.shape[1])

    @property
    def promotion_status(self) -> str:
        return "PHYSICAL_BACKGROUND_FROZEN" if self.gate7_closed else "PROVISIONAL_BACKGROUND_ONLY"

    def ambient(self, physical_direction: Array) -> Array:
        direction = np.asarray(physical_direction, dtype=float)
        if direction.shape != (self.physical_dimension,):
            raise ValueError("physical direction has the wrong dimension")
        return self.physical_frame @ direction


@dataclass(frozen=True)
class PhysicalActionExpansion:
    """Matrix-free S2/S3/S4 expansion of one action on one quotient."""

    oracle: DirectionalActionOracle
    background: PhysicalBackground

    def _contract(self, *directions: Array) -> float:
        if not 1 <= len(directions) <= 4:
            raise ValueError("only first through fourth action derivatives are supported")
        ambient = tuple(self.background.ambient(direction) for direction in directions)
        value = float(self.oracle.derivative(self.background.state, ambient))
        if not np.isfinite(value):
            raise ArithmeticError("non-finite action derivative")
        return value

    def s1(self, direction: Array) -> float:
        return self._contract(direction)

    def s2(self, first: Array, second: Array) -> float:
        return self._contract(first, second)

    def s3(self, first: Array, second: Array, third: Array) -> float:
        return self._contract(first, second, third)

    def s4(self, first: Array, second: Array, third: Array, fourth: Array) -> float:
        return self._contract(first, second, third, fourth)

    def quadratic_matrix(self) -> Array:
        """Materialize only S2 on the physical quotient."""

        dimension = self.background.physical_dimension
        basis = np.eye(dimension)
        matrix = np.empty((dimension, dimension), dtype=float)
        for row in range(dimension):
            for column in range(row, dimension):
                value = self.s2(basis[row], basis[column])
                matrix[row, column] = value
                matrix[column, row] = value
        return matrix

    def stationarity_covector(self) -> Array:
        dimension = self.background.physical_dimension
        return np.asarray([self.s1(direction) for direction in np.eye(dimension)])

    def vertex(self, order: int, directions: Sequence[Array]) -> float:
        """Return an action-owned amputated bare vertex coefficient.

        Momentum dependence, external-leg normalization, LSZ residues, and
        loop renormalization are separate downstream adapters.  This method
        returns only the multilinear action derivative.
        """

        if order not in (3, 4) or len(directions) != order:
            raise ValueError("vertex order must be three or four")
        return self._contract(*directions)

    def require_physical_promotion(self) -> None:
        if not self.background.gate7_closed:
            raise RuntimeError(
                "Gate 7 is not closed for this background; physical poles, "
                "particle assignments, amplitudes, and predictions may not be promoted"
            )

    def metadata(self) -> dict:
        return {
            "action_version": self.background.action_version,
            "background_id": self.background.background_id,
            "physical_dimension": self.background.physical_dimension,
            "promotion_status": self.background.promotion_status,
            "derivative_orders_available": [1, 2, 3, 4],
            "dense_fourth_tensor_formed": False,
            "particle_or_observable_input_used": False,
            "provenance": list(self.background.provenance),
        }


class CallableDirectionalActionOracle:
    """Adapter for a scalar action plus an exact directional derivative call."""

    def __init__(
        self,
        action: Callable[[Array], float],
        derivative: Callable[[Array, Sequence[Array]], float],
    ) -> None:
        self._action = action
        self._derivative = derivative

    def value(self, state: Array) -> float:
        return float(self._action(np.asarray(state, dtype=float)))

    def derivative(self, state: Array, directions: Sequence[Array]) -> float:
        return float(self._derivative(np.asarray(state, dtype=float), directions))


class JaxDirectionalActionOracle:
    """Matrix-free nested-JVP backend for a scalar JAX action."""

    def __init__(self, action: Callable) -> None:
        import jax

        self._jax = jax
        self._action = action

    def value(self, state: Array) -> float:
        import jax.numpy as jnp

        return float(self._action(jnp.asarray(state)))

    def derivative(self, state: Array, directions: Sequence[Array]) -> float:
        import jax.numpy as jnp

        if not 1 <= len(directions) <= 4:
            raise ValueError("directional derivative order must be between one and four")
        function = self._action
        for direction in directions:
            tangent = jnp.asarray(direction)
            previous = function

            def function(value, previous=previous, tangent=tangent):
                return self._jax.jvp(previous, (value,), (tangent,))[1]

        return float(function(jnp.asarray(state)))


__all__ = [
    "CallableDirectionalActionOracle",
    "DirectionalActionOracle",
    "JaxDirectionalActionOracle",
    "PhysicalActionExpansion",
    "PhysicalBackground",
]
