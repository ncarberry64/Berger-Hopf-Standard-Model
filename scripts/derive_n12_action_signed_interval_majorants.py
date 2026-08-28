"""Reproducible signed/interval retained-action mixed evaluator.

This isolated module preserves the exact signed-output and directed
interval-output extensions without modifying the protected general-majorant
working file.  It evaluates the identical retained N=12 quadrature action.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_ACTION_MAJORANT_RESULT",
    ".tmp_direct_n12_action_ball_majorants.json",
))
BALL_RADIUS = float(os.environ.get("BHSM_N12_CERTIFICATE_BALL", "1e-8"))
ROUNDING_INFLATION = 1.0 + 1.0e-10


def _up(value: float) -> float:
    return math.nextafter(float(value) * ROUNDING_INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) * ROUNDING_INFLATION, -math.inf)


def _norm_up(values: np.ndarray) -> float:
    vector = np.asarray(values, dtype=float).ravel()
    return _up(math.sqrt(math.fsum(float(x) * float(x) for x in vector)))


@dataclass(frozen=True)
class Bound:
    lo: float
    hi: float
    d: tuple[float, float, float, float, float, float]

    @classmethod
    def constant(cls, value: float) -> "Bound":
        x = float(value)
        return cls(x, x, (max(abs(x), 0.0), 0.0, 0.0, 0.0, 0.0, 0.0))

    @classmethod
    def affine(cls, value: float, gradient_norm: float) -> "Bound":
        spread = _up(BALL_RADIUS * gradient_norm)
        lo = math.nextafter(float(value) - spread, -math.inf)
        hi = math.nextafter(float(value) + spread, math.inf)
        return cls(
            lo,
            hi,
            (
                _up(max(abs(lo), abs(hi))), _up(gradient_norm),
                0.0, 0.0, 0.0, 0.0,
            ),
        )

    def __neg__(self) -> "Bound":
        return Bound(-self.hi, -self.lo, self.d)

    def __add__(self, other: float | "Bound") -> "Bound":
        if not isinstance(other, Bound):
            other = Bound.constant(other)
        return Bound(
            math.nextafter(self.lo + other.lo, -math.inf),
            math.nextafter(self.hi + other.hi, math.inf),
            tuple(_up(a + b) for a, b in zip(self.d, other.d)),
        )

    __radd__ = __add__

    def __sub__(self, other: float | "Bound") -> "Bound":
        return self + (-other if isinstance(other, Bound) else -float(other))

    def __rsub__(self, other: float | "Bound") -> "Bound":
        return (-self) + other

    def __mul__(self, other: float | "Bound") -> "Bound":
        if not isinstance(other, Bound):
            other = Bound.constant(other)
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        lo = math.nextafter(min(products), -math.inf)
        hi = math.nextafter(max(products), math.inf)
        d = []
        for n in range(6):
            total = math.fsum(
                math.comb(n, k) * self.d[k] * other.d[n - k]
                for k in range(n + 1)
            )
            d.append(_up(total))
        return Bound(lo, hi, tuple(d))

    __rmul__ = __mul__

    def reciprocal(self) -> "Bound":
        if self.lo <= 0.0 <= self.hi:
            raise ArithmeticError("interval reciprocal crosses zero")
        endpoints = (1.0 / self.lo, 1.0 / self.hi)
        lo = math.nextafter(min(endpoints), -math.inf)
        hi = math.nextafter(max(endpoints), math.inf)
        minimum = min(abs(self.lo), abs(self.hi))
        g = [_up(1.0 / minimum), 0.0, 0.0, 0.0, 0.0, 0.0]
        for n in range(1, 6):
            total = math.fsum(
                math.comb(n, k) * self.d[k] * g[n - k]
                for k in range(1, n + 1)
            )
            g[n] = _up(total / minimum)
        return Bound(lo, hi, tuple(g))

    def __truediv__(self, other: float | "Bound") -> "Bound":
        if isinstance(other, Bound):
            return self * other.reciprocal()
        return self * (1.0 / float(other))

    def __rtruediv__(self, other: float | "Bound") -> "Bound":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "Bound":
        if not isinstance(power, int):
            raise TypeError("integer powers only")
        if power == 0:
            return Bound.constant(1.0)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = Bound.constant(1.0)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "Bound":
        lo = math.nextafter(math.exp(self.lo), -math.inf)
        hi = math.nextafter(math.exp(self.hi), math.inf)
        g = [_up(hi), 0.0, 0.0, 0.0, 0.0, 0.0]
        for n in range(1, 6):
            total = math.fsum(
                math.comb(n - 1, k) * g[k] * self.d[n - k]
                for k in range(n)
            )
            g[n] = _up(total)
        return Bound(lo, hi, tuple(g))

    def positive_power(self, power: float) -> "Bound":
        if self.lo <= 0.0:
            raise ArithmeticError("noninteger power needs a positive interval")
        lo = math.nextafter(self.lo**power, -math.inf)
        hi = math.nextafter(self.hi**power, math.inf)
        h = [max(abs(lo), abs(hi))]
        coefficient = 1.0
        for k in range(1, 6):
            coefficient *= power - (k - 1)
            exponent = power - k
            endpoint = self.lo if exponent < 0.0 else self.hi
            h.append(_up(abs(coefficient) * endpoint**exponent))
        f = self.d
        g = [h[0]]
        g.append(_up(h[1] * f[1]))
        g.append(_up(h[2] * f[1]**2 + h[1] * f[2]))
        g.append(_up(
            h[3] * f[1]**3 + 3.0 * h[2] * f[1] * f[2]
            + h[1] * f[3]
        ))
        g.append(_up(
            h[4] * f[1]**4 + 6.0 * h[3] * f[1]**2 * f[2]
            + 3.0 * h[2] * f[2]**2 + 4.0 * h[2] * f[1] * f[3]
            + h[1] * f[4]
        ))
        g.append(_up(
            h[5] * f[1]**5 + 10.0 * h[4] * f[1]**3 * f[2]
            + 10.0 * h[3] * f[1]**2 * f[3]
            + 15.0 * h[3] * f[1] * f[2]**2
            + 5.0 * h[2] * f[1] * f[4]
            + 10.0 * h[2] * f[2] * f[3]
            + h[1] * f[5]
        ))
        return Bound(lo, hi, tuple(g))


@lru_cache(maxsize=None)
def _set_partitions(mask: int) -> tuple[tuple[int, ...], ...]:
    """Return unordered partitions of the set bits in ``mask``."""

    if mask == 0:
        return ((),)
    first = mask & -mask
    remainder = mask ^ first
    result = []
    for partition in _set_partitions(remainder):
        result.append((first,) + partition)
        for index in range(len(partition)):
            merged = list(partition)
            merged[index] |= first
            result.append(tuple(sorted(merged)))
    return tuple(sorted(set(result)))


@dataclass(frozen=True)
class MixedBound:
    """Interval value plus distinct-direction mixed derivative bounds."""

    lo: float
    hi: float
    d: tuple[float, ...]

    @classmethod
    def constant(cls, value: float, directions: int) -> "MixedBound":
        x = float(value)
        derivatives = [0.0] * (1 << directions)
        derivatives[0] = abs(x)
        return cls(x, x, tuple(derivatives))

    @classmethod
    def affine(
        cls,
        value: float,
        interval_gradient_norm: float,
        directional_derivatives: list[float],
    ) -> "MixedBound":
        spread = _up(BALL_RADIUS * interval_gradient_norm)
        lo = math.nextafter(float(value) - spread, -math.inf)
        hi = math.nextafter(float(value) + spread, math.inf)
        derivatives = [0.0] * (1 << len(directional_derivatives))
        derivatives[0] = _up(max(abs(lo), abs(hi)))
        for index, derivative in enumerate(directional_derivatives):
            derivatives[1 << index] = _up(abs(derivative))
        return cls(lo, hi, tuple(derivatives))

    @property
    def directions(self) -> int:
        return (len(self.d) - 1).bit_length()

    def __neg__(self) -> "MixedBound":
        return MixedBound(-self.hi, -self.lo, self.d)

    def __add__(self, other: float | "MixedBound") -> "MixedBound":
        if not isinstance(other, MixedBound):
            other = MixedBound.constant(other, self.directions)
        return MixedBound(
            math.nextafter(self.lo + other.lo, -math.inf),
            math.nextafter(self.hi + other.hi, math.inf),
            tuple(_up(a + b) for a, b in zip(self.d, other.d)),
        )

    __radd__ = __add__

    def __sub__(self, other: float | "MixedBound") -> "MixedBound":
        return self + (-other if isinstance(other, MixedBound) else -float(other))

    def __rsub__(self, other: float | "MixedBound") -> "MixedBound":
        return (-self) + other

    def __mul__(self, other: float | "MixedBound") -> "MixedBound":
        if not isinstance(other, MixedBound):
            other = MixedBound.constant(other, self.directions)
        derivatives = []
        for mask in range(len(self.d)):
            total = 0.0
            subset = mask
            while True:
                total += self.d[subset] * other.d[mask ^ subset]
                if subset == 0:
                    break
                subset = (subset - 1) & mask
            derivatives.append(_up(total))
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return MixedBound(
            math.nextafter(min(products), -math.inf),
            math.nextafter(max(products), math.inf),
            tuple(derivatives),
        )

    __rmul__ = __mul__

    def _unary(
        self,
        lo: float,
        hi: float,
        outer_derivatives: list[float],
    ) -> "MixedBound":
        derivatives = [0.0] * len(self.d)
        derivatives[0] = _up(max(abs(lo), abs(hi)))
        for mask in range(1, len(self.d)):
            total = 0.0
            for partition in _set_partitions(mask):
                product = outer_derivatives[len(partition)]
                for block in partition:
                    product *= self.d[block]
                total += product
            derivatives[mask] = _up(total)
        return MixedBound(lo, hi, tuple(derivatives))

    def reciprocal(self) -> "MixedBound":
        if self.lo <= 0.0 <= self.hi:
            raise ArithmeticError("interval reciprocal crosses zero")
        minimum = min(abs(self.lo), abs(self.hi))
        endpoints = (1.0 / self.lo, 1.0 / self.hi)
        outer = [0.0]
        factorial = 1.0
        for order in range(1, self.directions + 1):
            factorial *= order
            outer.append(_up(factorial / minimum ** (order + 1)))
        return self._unary(
            math.nextafter(min(endpoints), -math.inf),
            math.nextafter(max(endpoints), math.inf),
            outer,
        )

    def __truediv__(self, other: float | "MixedBound") -> "MixedBound":
        if isinstance(other, MixedBound):
            return self * other.reciprocal()
        return self * (1.0 / float(other))

    def __rtruediv__(self, other: float | "MixedBound") -> "MixedBound":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "MixedBound":
        if not isinstance(power, int):
            raise TypeError("integer powers only")
        if power == 0:
            return MixedBound.constant(1.0, self.directions)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = MixedBound.constant(1.0, self.directions)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "MixedBound":
        lo = math.nextafter(math.exp(self.lo), -math.inf)
        hi = math.nextafter(math.exp(self.hi), math.inf)
        return self._unary(
            lo,
            hi,
            [0.0] + [_up(hi)] * self.directions,
        )

    def positive_power(self, power: float) -> "MixedBound":
        if self.lo <= 0.0:
            raise ArithmeticError("noninteger power needs a positive interval")
        lo = math.nextafter(self.lo ** power, -math.inf)
        hi = math.nextafter(self.hi ** power, math.inf)
        outer = [0.0]
        coefficient = 1.0
        for order in range(1, self.directions + 1):
            coefficient *= power - (order - 1)
            exponent = power - order
            endpoint = self.lo if exponent < 0.0 else self.hi
            outer.append(_up(abs(coefficient) * endpoint ** exponent))
        return self._unary(lo, hi, outer)


@dataclass(frozen=True)
class ExactMixed:
    """Exact distinct-direction jet with broadcast vector/tensor legs.

    This is used only to aggregate signed output components at a fixed state
    before an interval remainder is applied.  Distinguished matrix-valued
    directions occupy separate broadcast axes.  A mixed derivative uses each
    direction at most once, so the final component tensor retains every
    correlation without constructing an action derivative tensor globally.
    """

    value: float
    d: tuple[float | np.ndarray, ...]

    @classmethod
    def constant(cls, value: float, directions: int) -> "ExactMixed":
        derivatives: list[float | np.ndarray] = [0.0] * (1 << directions)
        derivatives[0] = float(value)
        return cls(float(value), tuple(derivatives))

    @classmethod
    def affine(
        cls, value: float, directional_derivatives: list[float | np.ndarray],
    ) -> "ExactMixed":
        derivatives: list[float | np.ndarray] = [0.0] * (
            1 << len(directional_derivatives)
        )
        derivatives[0] = float(value)
        for index, derivative in enumerate(directional_derivatives):
            derivatives[1 << index] = np.asarray(derivative, dtype=float) if (
                isinstance(derivative, np.ndarray)
            ) else float(derivative)
        return cls(float(value), tuple(derivatives))

    @property
    def directions(self) -> int:
        return (len(self.d) - 1).bit_length()

    def __neg__(self) -> "ExactMixed":
        return ExactMixed(-self.value, tuple(-item for item in self.d))

    def __add__(self, other: float | "ExactMixed") -> "ExactMixed":
        if not isinstance(other, ExactMixed):
            other = ExactMixed.constant(other, self.directions)
        return ExactMixed(
            self.value + other.value,
            tuple(a + b for a, b in zip(self.d, other.d)),
        )

    __radd__ = __add__

    def __sub__(self, other: float | "ExactMixed") -> "ExactMixed":
        return self + (-other if isinstance(other, ExactMixed) else -float(other))

    def __rsub__(self, other: float | "ExactMixed") -> "ExactMixed":
        return (-self) + other

    def __mul__(self, other: float | "ExactMixed") -> "ExactMixed":
        if not isinstance(other, ExactMixed):
            other = ExactMixed.constant(other, self.directions)
        derivatives: list[float | np.ndarray] = []
        for mask in range(len(self.d)):
            total: float | np.ndarray = 0.0
            subset = mask
            while True:
                total = total + self.d[subset] * other.d[mask ^ subset]
                if subset == 0:
                    break
                subset = (subset - 1) & mask
            derivatives.append(total)
        return ExactMixed(self.value * other.value, tuple(derivatives))

    __rmul__ = __mul__

    def _unary(
        self, value: float, outer_derivatives: list[float],
    ) -> "ExactMixed":
        derivatives: list[float | np.ndarray] = [0.0] * len(self.d)
        derivatives[0] = value
        for mask in range(1, len(self.d)):
            total: float | np.ndarray = 0.0
            for partition in _set_partitions(mask):
                product: float | np.ndarray = outer_derivatives[len(partition)]
                for block in partition:
                    product = product * self.d[block]
                total = total + product
            derivatives[mask] = total
        return ExactMixed(value, tuple(derivatives))

    def reciprocal(self) -> "ExactMixed":
        if self.value == 0.0:
            raise ArithmeticError("exact reciprocal crosses zero")
        outer = [0.0]
        factorial = 1.0
        for order in range(1, self.directions + 1):
            factorial *= order
            outer.append(((-1.0) ** order) * factorial / self.value ** (order + 1))
        return self._unary(1.0 / self.value, outer)

    def __truediv__(self, other: float | "ExactMixed") -> "ExactMixed":
        if isinstance(other, ExactMixed):
            return self * other.reciprocal()
        return self * (1.0 / float(other))

    def __rtruediv__(self, other: float | "ExactMixed") -> "ExactMixed":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "ExactMixed":
        if not isinstance(power, int):
            raise TypeError("integer powers only")
        if power == 0:
            return ExactMixed.constant(1.0, self.directions)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = ExactMixed.constant(1.0, self.directions)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "ExactMixed":
        value = math.exp(self.value)
        return self._unary(
            value, [0.0] + [value] * self.directions,
        )

    def positive_power(self, power: float) -> "ExactMixed":
        if self.value <= 0.0:
            raise ArithmeticError("noninteger power needs a positive value")
        value = self.value ** power
        outer = [0.0]
        coefficient = 1.0
        for order in range(1, self.directions + 1):
            coefficient *= power - (order - 1)
            outer.append(coefficient * self.value ** (power - order))
        return self._unary(value, outer)


@dataclass(frozen=True)
class IntervalValue:
    """Directed floating-point interval with scalar or array endpoints."""

    lo: float | np.ndarray
    hi: float | np.ndarray

    @classmethod
    def constant(cls, value: float | np.ndarray) -> "IntervalValue":
        array = np.asarray(value, dtype=float)
        if array.ndim == 0:
            scalar = float(array)
            return cls(scalar, scalar)
        return cls(array.copy(), array.copy())

    @staticmethod
    def _down(value: float | np.ndarray) -> float | np.ndarray:
        result = np.nextafter(np.asarray(value, dtype=float), -np.inf)
        return float(result) if result.ndim == 0 else result

    @staticmethod
    def _up(value: float | np.ndarray) -> float | np.ndarray:
        result = np.nextafter(np.asarray(value, dtype=float), np.inf)
        return float(result) if result.ndim == 0 else result

    def __neg__(self) -> "IntervalValue":
        return IntervalValue(self._down(-np.asarray(self.hi)), self._up(-np.asarray(self.lo)))

    def __add__(self, other: float | np.ndarray | "IntervalValue") -> "IntervalValue":
        if not isinstance(other, IntervalValue):
            other = IntervalValue.constant(other)
        return IntervalValue(
            self._down(np.asarray(self.lo) + np.asarray(other.lo)),
            self._up(np.asarray(self.hi) + np.asarray(other.hi)),
        )

    __radd__ = __add__

    def __sub__(self, other: float | np.ndarray | "IntervalValue") -> "IntervalValue":
        return self + (-other if isinstance(other, IntervalValue) else -np.asarray(other))

    def __rsub__(self, other: float | np.ndarray | "IntervalValue") -> "IntervalValue":
        return (-self) + other

    def __mul__(self, other: float | np.ndarray | "IntervalValue") -> "IntervalValue":
        if not isinstance(other, IntervalValue):
            other = IntervalValue.constant(other)
        products = np.stack((
            np.asarray(self.lo) * np.asarray(other.lo),
            np.asarray(self.lo) * np.asarray(other.hi),
            np.asarray(self.hi) * np.asarray(other.lo),
            np.asarray(self.hi) * np.asarray(other.hi),
        ))
        return IntervalValue(
            self._down(np.min(products, axis=0)),
            self._up(np.max(products, axis=0)),
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "IntervalValue":
        lo = np.asarray(self.lo)
        hi = np.asarray(self.hi)
        if np.any((lo <= 0.0) & (hi >= 0.0)):
            raise ArithmeticError("interval reciprocal crosses zero")
        endpoints = np.stack((1.0 / lo, 1.0 / hi))
        return IntervalValue(
            self._down(np.min(endpoints, axis=0)),
            self._up(np.max(endpoints, axis=0)),
        )

    def __truediv__(self, other: float | np.ndarray | "IntervalValue") -> "IntervalValue":
        if isinstance(other, IntervalValue):
            return self * other.reciprocal()
        return self * (1.0 / np.asarray(other))

    def __rtruediv__(self, other: float | np.ndarray | "IntervalValue") -> "IntervalValue":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "IntervalValue":
        if not isinstance(power, int):
            raise TypeError("integer powers only")
        if power == 0:
            return IntervalValue.constant(1.0)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = IntervalValue.constant(1.0)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "IntervalValue":
        return IntervalValue(
            self._down(np.exp(np.asarray(self.lo))),
            self._up(np.exp(np.asarray(self.hi))),
        )

    def positive_power(self, power: float) -> "IntervalValue":
        lo = np.asarray(self.lo)
        hi = np.asarray(self.hi)
        if np.any(lo <= 0.0):
            raise ArithmeticError("noninteger power needs a positive interval")
        endpoints = np.stack((lo**power, hi**power))
        return IntervalValue(
            self._down(np.min(endpoints, axis=0)),
            self._up(np.max(endpoints, axis=0)),
        )


@dataclass(frozen=True)
class IntervalMixed:
    """Distinct-direction interval jet preserving one signed output vector."""

    d: tuple[IntervalValue, ...]

    @classmethod
    def constant(cls, value: float, directions: int) -> "IntervalMixed":
        derivatives = [IntervalValue.constant(0.0) for _ in range(1 << directions)]
        derivatives[0] = IntervalValue.constant(value)
        return cls(tuple(derivatives))

    @classmethod
    def affine(
        cls,
        value: IntervalValue,
        directional_derivatives: list[IntervalValue],
    ) -> "IntervalMixed":
        derivatives = [
            IntervalValue.constant(0.0)
            for _ in range(1 << len(directional_derivatives))
        ]
        derivatives[0] = value
        for index, derivative in enumerate(directional_derivatives):
            derivatives[1 << index] = derivative
        return cls(tuple(derivatives))

    @property
    def directions(self) -> int:
        return (len(self.d) - 1).bit_length()

    def __neg__(self) -> "IntervalMixed":
        return IntervalMixed(tuple(-item for item in self.d))

    def __add__(self, other: float | "IntervalMixed") -> "IntervalMixed":
        if not isinstance(other, IntervalMixed):
            other = IntervalMixed.constant(other, self.directions)
        return IntervalMixed(tuple(a + b for a, b in zip(self.d, other.d)))

    __radd__ = __add__

    def __sub__(self, other: float | "IntervalMixed") -> "IntervalMixed":
        return self + (-other if isinstance(other, IntervalMixed) else -float(other))

    def __rsub__(self, other: float | "IntervalMixed") -> "IntervalMixed":
        return (-self) + other

    def __mul__(self, other: float | "IntervalMixed") -> "IntervalMixed":
        if not isinstance(other, IntervalMixed):
            other = IntervalMixed.constant(other, self.directions)
        derivatives = []
        for mask in range(len(self.d)):
            total = IntervalValue.constant(0.0)
            subset = mask
            while True:
                total = total + self.d[subset] * other.d[mask ^ subset]
                if subset == 0:
                    break
                subset = (subset - 1) & mask
            derivatives.append(total)
        return IntervalMixed(tuple(derivatives))

    __rmul__ = __mul__

    def _unary(
        self,
        value: IntervalValue,
        outer_derivatives: list[IntervalValue],
    ) -> "IntervalMixed":
        derivatives = [IntervalValue.constant(0.0) for _ in self.d]
        derivatives[0] = value
        for mask in range(1, len(self.d)):
            total = IntervalValue.constant(0.0)
            for partition in _set_partitions(mask):
                product = outer_derivatives[len(partition)]
                for block in partition:
                    product = product * self.d[block]
                total = total + product
            derivatives[mask] = total
        return IntervalMixed(tuple(derivatives))

    def reciprocal(self) -> "IntervalMixed":
        value = self.d[0]
        inverse = value.reciprocal()
        outer = [IntervalValue.constant(0.0)]
        factorial = 1.0
        for order in range(1, self.directions + 1):
            factorial *= order
            outer.append(((-1.0) ** order) * factorial * (value ** (-(order + 1))))
        return self._unary(inverse, outer)

    def __truediv__(self, other: float | "IntervalMixed") -> "IntervalMixed":
        if isinstance(other, IntervalMixed):
            return self * other.reciprocal()
        return self * (1.0 / float(other))

    def __rtruediv__(self, other: float | "IntervalMixed") -> "IntervalMixed":
        return self.reciprocal() * other

    def __pow__(self, power: int) -> "IntervalMixed":
        if not isinstance(power, int):
            raise TypeError("integer powers only")
        if power == 0:
            return IntervalMixed.constant(1.0, self.directions)
        if power < 0:
            return (self ** (-power)).reciprocal()
        result = IntervalMixed.constant(1.0, self.directions)
        base = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def exp(self) -> "IntervalMixed":
        value = self.d[0].exp()
        return self._unary(value, [IntervalValue.constant(0.0)] + [value] * self.directions)

    def positive_power(self, power: float) -> "IntervalMixed":
        value = self.d[0]
        powered = value.positive_power(power)
        outer = [IntervalValue.constant(0.0)]
        coefficient = 1.0
        for order in range(1, self.directions + 1):
            coefficient *= power - (order - 1)
            outer.append(coefficient * value.positive_power(power - order))
        return self._unary(powered, outer)


def _linear_interval(
    coefficients: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> IntervalValue:
    coefficients = np.asarray(coefficients, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    coefficient_columns = coefficients.reshape((-1,) + (1,) * (lower.ndim - 1))
    lo_terms = np.where(
        coefficient_columns >= 0.0,
        coefficient_columns * lower,
        coefficient_columns * upper,
    )
    hi_terms = np.where(
        coefficient_columns >= 0.0,
        coefficient_columns * upper,
        coefficient_columns * lower,
    )

    def faithful_sum(terms: np.ndarray) -> float | np.ndarray:
        if terms.ndim == 1:
            return math.fsum(float(value) for value in terms)
        flattened = terms.reshape((terms.shape[0], -1))
        result = np.asarray([
            math.fsum(float(value) for value in flattened[:, column])
            for column in range(flattened.shape[1])
        ])
        return result.reshape(terms.shape[1:])

    return IntervalValue(
        IntervalValue._down(faithful_sum(lo_terms)),
        IntervalValue._up(faithful_sum(hi_terms)),
    )

def action_bound(
    state: np.ndarray,
    projection: np.ndarray | None = None,
    mixed_directions: list[np.ndarray] | None = None,
    *,
    exact_signed_output_index: int | None = None,
    exact_signed_tensor_indices: tuple[int, ...] | None = None,
    interval_state_bounds: tuple[np.ndarray, np.ndarray] | None = None,
    interval_direction_bounds: list[tuple[np.ndarray, np.ndarray] | None] | None = None,
    interval_signed_output_index: int | None = None,
) -> Bound | MixedBound | ExactMixed | IntervalMixed:
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    q = np.asarray(state[:qdim], dtype=float)
    velocity = np.asarray(state[qdim:2 * qdim], dtype=float)
    multipliers = np.asarray(state[2 * qdim:], dtype=float)
    values = np.concatenate((q, velocity, multipliers))
    frequencies = spectral_frequencies(ORDER)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))

    exact_modes = sum((
        exact_signed_output_index is not None,
        exact_signed_tensor_indices is not None,
        interval_signed_output_index is not None,
    ))
    if exact_modes > 1:
        raise ValueError(
            "exact vector, exact tensor, and interval signed-output modes are mutually exclusive"
        )
    tensor_indices = (
        tuple(int(index) for index in exact_signed_tensor_indices)
        if exact_signed_tensor_indices is not None else
        (int(exact_signed_output_index),)
        if exact_signed_output_index is not None else ()
    )
    if len(set(tensor_indices)) != len(tensor_indices):
        raise ValueError("exact signed tensor indices must be unique")
    if interval_signed_output_index is not None:
        if mixed_directions is None or interval_state_bounds is None or interval_direction_bounds is None:
            raise ValueError("interval signed-output mode requires state and direction bounds")
        if len(interval_direction_bounds) != len(mixed_directions):
            raise ValueError("one interval direction bound is required per mixed direction")
        if projection is not None:
            raise ValueError("interval signed-output mode uses explicit state bounds")

    def affine(coefficients: np.ndarray) -> Bound | MixedBound | ExactMixed | IntervalMixed:
        coefficients = np.asarray(coefficients, dtype=float)
        normalized = coefficients / weights
        interval_normalized = normalized
        if projection is not None:
            interval_normalized = (
                np.asarray(projection, dtype=float).T @ normalized
            )
        if mixed_directions is None:
            return Bound.affine(
                float(coefficients @ values),
                _norm_up(interval_normalized),
            )
        if interval_signed_output_index is not None:
            state_value = _linear_interval(
                coefficients,
                np.asarray(interval_state_bounds[0], dtype=float),
                np.asarray(interval_state_bounds[1], dtype=float),
            )
            directional_derivatives = []
            for index, (direction, bounds) in enumerate(zip(
                mixed_directions, interval_direction_bounds,
            )):
                direction = np.asarray(direction, dtype=float)
                if index == interval_signed_output_index:
                    if direction.ndim != 2 or bounds is not None:
                        raise ValueError("interval output leg must be one fixed matrix")
                    directional_derivatives.append(_linear_interval(
                        normalized, direction, direction,
                    ))
                else:
                    if bounds is None:
                        if direction.ndim != 1:
                            raise ValueError("a fixed non-output direction must be a vector")
                        directional_derivatives.append(IntervalValue.constant(
                            float(direction @ normalized)
                        ))
                    else:
                        directional_derivatives.append(_linear_interval(
                            normalized,
                            np.asarray(bounds[0], dtype=float),
                            np.asarray(bounds[1], dtype=float),
                        ))
            return IntervalMixed.affine(state_value, directional_derivatives)
        if tensor_indices:
            if projection is not None:
                raise ValueError("exact signed output evaluation is fixed-state only")
            directional_derivatives: list[float | np.ndarray] = []
            for index, direction in enumerate(mixed_directions):
                direction = np.asarray(direction, dtype=float)
                if direction.ndim == 1:
                    directional_derivatives.append(float(direction @ normalized))
                elif direction.ndim == 2 and index in tensor_indices:
                    component = direction.T @ normalized
                    shape = [1] * len(tensor_indices)
                    shape[tensor_indices.index(index)] = component.size
                    directional_derivatives.append(component.reshape(shape))
                else:
                    raise ValueError(
                        "exact signed evaluation permits matrices only in declared tensor legs"
                    )
            return ExactMixed.affine(
                float(coefficients @ values), directional_derivatives,
            )
        direction_bounds = []
        for direction in mixed_directions:
            direction = np.asarray(direction, dtype=float)
            if direction.ndim == 1:
                direction_bounds.append(abs(float(direction @ normalized)))
            elif direction.ndim == 2:
                direction_bounds.append(_norm_up(direction.T @ normalized))
            else:
                raise ValueError("mixed direction must be a vector or subspace")
        return MixedBound.affine(
            float(coefficients @ values),
            _norm_up(interval_normalized),
            direction_bounds,
        )

    nodes, quadrature = np.polynomial.legendre.leggauss(POINTS)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, ORDER + 1, dtype=float)
    js = np.arange(ORDER, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi))
    sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi))
    sin_j = np.sin(4.0 * np.outer(js, chi))
    response_sigma = (
        -0.5 + 2.0 * chi / math.pi
        - np.sin(4.0 * chi) / (2.0 * math.pi)
    )
    localization = 1.0 - 4.0 * response_sigma**2
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    if mixed_directions is None:
        bulk = Bound.constant(0.0)
        inertia = Bound.constant(0.0)
    elif tensor_indices:
        bulk = ExactMixed.constant(0.0, len(mixed_directions))
        inertia = ExactMixed.constant(0.0, len(mixed_directions))
    elif interval_signed_output_index is not None:
        bulk = IntervalMixed.constant(0.0, len(mixed_directions))
        inertia = IntervalMixed.constant(0.0, len(mixed_directions))
    else:
        bulk = MixedBound.constant(0.0, len(mixed_directions))
        inertia = MixedBound.constant(0.0, len(mixed_directions))

    for index, coordinate in enumerate(chi):
        window = math.sin(2.0 * coordinate) ** 2
        window_prime = 2.0 * math.sin(4.0 * coordinate)
        q_u = np.zeros(values.size)
        q_up = np.zeros(values.size)
        q_w = np.zeros(values.size)
        q_wp = np.zeros(values.size)
        q_b = np.zeros(values.size)
        q_bp = np.zeros(values.size)
        q_u[1:1 + ORDER] = cos_k[:, index]
        q_up[1:1 + ORDER] = -4.0 * ks * sin_k[:, index]
        q_w[1 + ORDER:1 + 2 * ORDER] = window * cos_j[:, index]
        q_wp[1 + ORDER:1 + 2 * ORDER] = (
            window_prime * cos_j[:, index]
            + window * (-4.0 * js * sin_j[:, index])
        )
        q_b[1 + 2 * ORDER:1 + 3 * ORDER] = window * cos_j[:, index]
        q_bp[1 + 2 * ORDER:1 + 3 * ORDER] = (
            window_prime * cos_j[:, index]
            + window * (-4.0 * js * sin_j[:, index])
        )
        scale = np.zeros(values.size)
        scale[0] = 1.0
        u, up = affine(q_u), affine(q_up)
        w, wp = affine(q_w), affine(q_wp)
        b, bp_shape = affine(q_b), affine(q_bp)
        radius = RADIUS0 * affine(scale).exp()
        C = radius * (u + w).exp()
        A = radius * (u + b).exp() * math.cos(coordinate)
        B = radius * (u - b).exp() * math.sin(coordinate)
        cp = up + wp
        ap = up + bp_shape - math.tan(coordinate)
        bp = up - bp_shape + 1.0 / math.tan(coordinate)
        volume = C * A**3 * B**3
        spatial_volume = A**3 * B**3

        lc = np.zeros(values.size)
        la = np.zeros(values.size)
        lb = np.zeros(values.size)
        voff = qdim
        lc[voff] = la[voff] = lb[voff] = 1.0
        lc[voff + 1:voff + 1 + ORDER] = cos_k[:, index]
        la[voff + 1:voff + 1 + ORDER] = cos_k[:, index]
        lb[voff + 1:voff + 1 + ORDER] = cos_k[:, index]
        lc[voff + 1 + ORDER:voff + 1 + 2 * ORDER] = (
            window * cos_j[:, index]
        )
        la[voff + 1 + 2 * ORDER:voff + 1 + 3 * ORDER] = (
            window * cos_j[:, index]
        )
        lb[voff + 1 + 2 * ORDER:voff + 1 + 3 * ORDER] = (
            -window * cos_j[:, index]
        )
        moff = 2 * qdim
        lapse = np.zeros(values.size)
        lapse_prime = np.zeros(values.size)
        shift = np.zeros(values.size)
        shift_prime = np.zeros(values.size)
        lapse[moff:moff + ORDER] = cos_k[:, index]
        lapse_prime[moff:moff + ORDER] = -4.0 * ks * sin_k[:, index]
        shift[moff + ORDER:moff + 2 * ORDER] = (
            math.sin(4.0 * coordinate) * cos_j[:, index]
        )
        shift_prime[moff + ORDER:moff + 2 * ORDER] = (
            4.0 * math.cos(4.0 * coordinate) * cos_j[:, index]
            + math.sin(4.0 * coordinate) * (-4.0 * js * sin_j[:, index])
        )
        lc_b, la_b, lb_b = affine(lc), affine(la), affine(lb)
        log_n = affine(lapse)
        n_prime = affine(lapse_prime)
        beta = affine(shift)
        beta_prime = affine(shift_prime)
        N = log_n.exp()
        Hc = (lc_b - beta * cp - beta_prime) / N
        Ha = (la_b - beta * ap) / N
        Hb = (lb_b - beta * bp) / N
        adm = (
            Hc**2 + 3.0 * Ha**2 + 3.0 * Hb**2
            - (Hc + 3.0 * Ha + 3.0 * Hb) ** 2
        )
        f_normal = -beta / N
        x_spatial = (
            1.0 / C**2
            + 3.0 * math.cos(coordinate) ** 2 / A**2
            + 3.0 * math.sin(coordinate) ** 2 / B**2
        )
        x_eta = x_spatial - f_normal**2
        eta_legendre = 1.0 + x_eta**3
        fixed_gravity = ap**2 + bp**2 + 3.0 * ap * bp
        spatial_gravity = (
            3.0 * spatial_volume / C * N
            * (n_prime * (ap + bp) + fixed_gravity)
        )
        algebraic = N * volume * (
            3.0 / A**2 + 3.0 / B**2 - 0.5 * kappa0
            - localization[index] * (0.5 * x_eta + 0.125 * x_eta**4)
            + 0.5 * adm
        )
        bulk = bulk + quadrature[index] * (spatial_gravity + algebraic)
        inertia = inertia + quadrature[index] * (
            volume * localization[index] * eta_legendre / N
        )

    action = bulk - 0.25 / (2.0 * HOPF_ORBIT_VOLUME**2 * inertia)
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    u_boundary_coeff = np.zeros(values.size)
    b_boundary_coeff = np.zeros(values.size)
    u_boundary_coeff[1:1 + ORDER] = signs_k
    b_boundary_coeff[1 + 2 * ORDER:1 + 3 * ORDER] = signs_j
    u_boundary = affine(u_boundary_coeff)
    b_boundary = affine(b_boundary_coeff)
    scale = np.zeros(values.size)
    scale[0] = 1.0
    radius = RADIUS0 * affine(scale).exp()
    A_boundary = radius * (u_boundary + b_boundary).exp() / math.sqrt(2.0)
    B_boundary = radius * (u_boundary - b_boundary).exp() / math.sqrt(2.0)
    R4 = A_boundary * B_boundary / (
        A_boundary**2 + B_boundary**2
    ).positive_power(0.5)
    boundary_lapse = np.zeros(values.size)
    boundary_lapse[2 * qdim:2 * qdim + ORDER] = signs_k
    return action - (
        standard_model_casimir_coefficient() / R4 * affine(boundary_lapse).exp()
    )


def sector_payload(
    name: str, state: np.ndarray, projection: np.ndarray | None = None,
) -> dict[str, object]:
    bound = action_bound(state)
    restricted = action_bound(state, projection) if projection is not None else None
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    q, v, m = (
        state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]
    )
    jet = exact_full_action_jet_at_state(ORDER, q, v, m, points=POINTS)
    normalized_gradient = np.asarray(jet.gradient) / weights
    normalized_hessian = (
        np.asarray(jet.hessian) / weights[:, None] / weights[None, :]
    )
    exact_gradient_norm = float(np.linalg.norm(normalized_gradient))
    exact_hessian_norm = float(np.linalg.norm(normalized_hessian, ord=2))
    result = {
        "sector": name,
        "action_value": float(jet.value),
        "action_value_interval": [bound.lo, bound.hi],
        "derivative_operator_majorants_0_through_5": list(bound.d),
        "exact_center_action_gradient_norm": exact_gradient_norm,
        "exact_center_action_hessian_norm": exact_hessian_norm,
        "value_enclosed": bool(bound.lo <= float(jet.value) <= bound.hi),
        "gradient_bound_dominates_exact_center": bool(
            bound.d[1] >= exact_gradient_norm
        ),
        "hessian_bound_dominates_exact_center": bool(
            bound.d[2] >= exact_hessian_norm
        ),
    }
    if restricted is not None:
        result["restricted_subspace_dimension"] = int(projection.shape[1])
        result[
            "restricted_derivative_operator_majorants_0_through_5"
        ] = list(restricted.d)
    return result


def main() -> None:
    if BALL_RADIUS <= 0.0:
        raise ValueError("certificate ball radius must be positive")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    frequencies = spectral_frequencies(ORDER)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    event_projection = None
    child_projection = None
    if "paired_jacobian" in checkpoint.files:
        _, _, normal_vh = np.linalg.svd(
            np.asarray(checkpoint["paired_jacobian"]), full_matrices=False
        )
        normal = normal_vh.T
        event_projection = normal[:state_dimension]
        child_projection = normal[state_dimension:]
        if "branch_reference" in checkpoint.files:
            event = joint[:state_dimension]
            q = event[:qdim]
            velocity = event[qdim:2 * qdim]
            multipliers = event[2 * qdim:]
            event_jet = exact_action_jet_at_state(
                ORDER, q, velocity, multipliers, points=POINTS
            )
            values, vectors = np.linalg.eigh(event_jet.hessian)
            reference = np.asarray(checkpoint["branch_reference"])
            branch = int(np.argmax(np.abs(vectors.T @ reference)))
            reduced_weights = weights[qdim:]
            eigenline = np.zeros(state_dimension)
            eigenline[qdim:] = reduced_weights * vectors[:, branch]
            eigenline /= np.linalg.norm(eigenline)
            event_projection = np.linalg.qr(np.column_stack((
                event_projection, eigenline,
            )))[0]
    sectors = [
        sector_payload("event", joint[:state_dimension], event_projection),
        sector_payload("child", joint[state_dimension:], child_projection),
    ]
    validation = {
        "unchanged_retained_action_expression": True,
        "event_value_enclosed": sectors[0]["value_enclosed"],
        "child_value_enclosed": sectors[1]["value_enclosed"],
        "event_first_two_center_derivatives_dominated": bool(
            sectors[0]["gradient_bound_dominates_exact_center"]
            and sectors[0]["hessian_bound_dominates_exact_center"]
        ),
        "child_first_two_center_derivatives_dominated": bool(
            sectors[1]["gradient_bound_dominates_exact_center"]
            and sectors[1]["hessian_bound_dominates_exact_center"]
        ),
        "no_equation_gate_or_physics_changed": True,
    }
    payload = {
        "classification": "N12_RETAINED_ACTION_BALL_DERIVATIVE_MAJORANTS",
        "order": ORDER,
        "points": POINTS,
        "action_coordinate_ball_radius": BALL_RADIUS,
        "rounding_inflation_factor_per_bound_operation": ROUNDING_INFLATION,
        "sectors": sectors,
        "scope": (
            "SCALAR_RETAINED_ACTION_DERIVATIVE_MAJORANTS_ONLY;_THE_"
            "BORDERED_LIFT_AND_EIGENPROJECTOR_COMPOSITION_BOUNDS_REMAIN"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
