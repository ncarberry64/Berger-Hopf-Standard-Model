"""Outward-rounded mixed tensor jets for the retained local BHSM action.

The evaluator in this module uses the same 96-point retained action expression
as :func:`exact_full_action_jet_at_state`, but carries a state interval and any
number of distinct vector or matrix direction legs.  Matrix legs retain their
own tensor axes, so signed rows and bilinear maps are assembled before norms.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    HOPF_ORBIT_VOLUME,
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


@dataclass(frozen=True)
class DirectedInterval:
    """Binary64 interval with scalar or ndarray endpoints."""

    lo: float | np.ndarray
    hi: float | np.ndarray

    @classmethod
    def constant(cls, value: float | np.ndarray) -> "DirectedInterval":
        array = np.asarray(value, dtype=float)
        if array.ndim == 0:
            scalar = float(array)
            return cls(scalar, scalar)
        return cls(array.copy(), array.copy())

    @classmethod
    def hull(
        cls, lower: float | np.ndarray, upper: float | np.ndarray,
    ) -> "DirectedInterval":
        return cls(cls._down(lower), cls._up(upper))

    @staticmethod
    def _down(value: float | np.ndarray) -> float | np.ndarray:
        result = np.nextafter(np.asarray(value, dtype=float), -np.inf)
        return float(result) if result.ndim == 0 else result

    @staticmethod
    def _up(value: float | np.ndarray) -> float | np.ndarray:
        result = np.nextafter(np.asarray(value, dtype=float), np.inf)
        return float(result) if result.ndim == 0 else result

    def __neg__(self) -> "DirectedInterval":
        return DirectedInterval(self._down(-np.asarray(self.hi)), self._up(-np.asarray(self.lo)))

    def __add__(self, other: object) -> "DirectedInterval":
        if not isinstance(other, DirectedInterval):
            other = DirectedInterval.constant(other)
        return DirectedInterval(
            self._down(np.asarray(self.lo) + np.asarray(other.lo)),
            self._up(np.asarray(self.hi) + np.asarray(other.hi)),
        )

    __radd__ = __add__

    def __sub__(self, other: object) -> "DirectedInterval":
        return self + (-(other if isinstance(other, DirectedInterval) else DirectedInterval.constant(other)))

    def __rsub__(self, other: object) -> "DirectedInterval":
        return (other if isinstance(other, DirectedInterval) else DirectedInterval.constant(other)) - self

    def __mul__(self, other: object) -> "DirectedInterval":
        if not isinstance(other, DirectedInterval):
            other = DirectedInterval.constant(other)
        products = np.stack((
            np.asarray(self.lo) * np.asarray(other.lo),
            np.asarray(self.lo) * np.asarray(other.hi),
            np.asarray(self.hi) * np.asarray(other.lo),
            np.asarray(self.hi) * np.asarray(other.hi),
        ))
        return DirectedInterval(
            self._down(np.min(products, axis=0)),
            self._up(np.max(products, axis=0)),
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "DirectedInterval":
        lo = np.asarray(self.lo)
        hi = np.asarray(self.hi)
        if np.any((lo <= 0.0) & (hi >= 0.0)):
            raise ArithmeticError("interval reciprocal crosses zero")
        endpoints = np.stack((1.0 / lo, 1.0 / hi))
        return DirectedInterval(
            self._down(np.min(endpoints, axis=0)),
            self._up(np.max(endpoints, axis=0)),
        )

    def __truediv__(self, other: object) -> "DirectedInterval":
        return self * (
            other.reciprocal() if isinstance(other, DirectedInterval)
            else DirectedInterval.constant(other).reciprocal()
        )

    def __rtruediv__(self, other: object) -> "DirectedInterval":
        return (other if isinstance(other, DirectedInterval) else DirectedInterval.constant(other)) * self.reciprocal()

    def __pow__(self, exponent: int) -> "DirectedInterval":
        if not isinstance(exponent, int):
            raise TypeError("integer powers only")
        if exponent < 0:
            return (self ** (-exponent)).reciprocal()
        result = DirectedInterval.constant(1.0)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "DirectedInterval":
        return DirectedInterval(
            self._down(np.exp(np.asarray(self.lo))),
            self._up(np.exp(np.asarray(self.hi))),
        )

    def positive_power(self, exponent: float) -> "DirectedInterval":
        lo = np.asarray(self.lo)
        hi = np.asarray(self.hi)
        if np.any(lo <= 0.0):
            raise ArithmeticError("positive power needs a positive interval")
        endpoints = np.stack((lo**exponent, hi**exponent))
        return DirectedInterval(
            self._down(np.min(endpoints, axis=0)),
            self._up(np.max(endpoints, axis=0)),
        )

    def magnitude(self) -> float:
        return float(max(np.max(np.abs(self.lo)), np.max(np.abs(self.hi))))


@lru_cache(maxsize=None)
def _partitions(mask: int) -> tuple[tuple[int, ...], ...]:
    if mask == 0:
        return ((),)
    first = mask & -mask
    remainder = mask ^ first
    result: list[tuple[int, ...]] = []
    for partition in _partitions(remainder):
        result.append((first,) + partition)
        for index in range(len(partition)):
            merged = list(partition)
            merged[index] |= first
            result.append(tuple(sorted(merged)))
    return tuple(sorted(set(result)))


@dataclass(frozen=True)
class TensorIntervalJet:
    """Distinct-direction interval jet retaining every matrix-leg axis."""

    d: tuple[DirectedInterval, ...]
    axis_sizes: tuple[int, ...]

    @classmethod
    def constant(
        cls, value: object, axis_sizes: tuple[int, ...],
    ) -> "TensorIntervalJet":
        shape = (1,) * len(axis_sizes)
        zero = DirectedInterval.constant(np.zeros(shape))
        derivatives = [zero for _ in range(1 << len(axis_sizes))]
        interval = value if isinstance(value, DirectedInterval) else DirectedInterval.constant(value)
        derivatives[0] = DirectedInterval(
            np.asarray(interval.lo).reshape(shape),
            np.asarray(interval.hi).reshape(shape),
        )
        return cls(tuple(derivatives), axis_sizes)

    @classmethod
    def affine(
        cls,
        value: DirectedInterval,
        derivatives: list[DirectedInterval],
        axis_sizes: tuple[int, ...],
    ) -> "TensorIntervalJet":
        result = list(cls.constant(value, axis_sizes).d)
        directions = len(axis_sizes)
        for index, derivative in enumerate(derivatives):
            shape = [1] * directions
            shape[index] = axis_sizes[index]
            result[1 << index] = DirectedInterval(
                np.asarray(derivative.lo).reshape(shape),
                np.asarray(derivative.hi).reshape(shape),
            )
        return cls(tuple(result), axis_sizes)

    @property
    def directions(self) -> int:
        return len(self.axis_sizes)

    def _coerce(self, other: object) -> "TensorIntervalJet":
        return other if isinstance(other, TensorIntervalJet) else self.constant(other, self.axis_sizes)

    def __neg__(self) -> "TensorIntervalJet":
        return TensorIntervalJet(tuple(-item for item in self.d), self.axis_sizes)

    def __add__(self, other: object) -> "TensorIntervalJet":
        other = self._coerce(other)
        return TensorIntervalJet(tuple(a + b for a, b in zip(self.d, other.d)), self.axis_sizes)

    __radd__ = __add__

    def __sub__(self, other: object) -> "TensorIntervalJet":
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "TensorIntervalJet":
        return self._coerce(other) - self

    def __mul__(self, other: object) -> "TensorIntervalJet":
        other = self._coerce(other)
        derivatives = []
        for mask in range(len(self.d)):
            total = DirectedInterval.constant(0.0)
            subset = mask
            while True:
                total = total + self.d[subset] * other.d[mask ^ subset]
                if subset == 0:
                    break
                subset = (subset - 1) & mask
            derivatives.append(total)
        return TensorIntervalJet(tuple(derivatives), self.axis_sizes)

    __rmul__ = __mul__

    def _unary(
        self, value: DirectedInterval, outer: list[DirectedInterval],
    ) -> "TensorIntervalJet":
        derivatives = [DirectedInterval.constant(0.0) for _ in self.d]
        derivatives[0] = value
        for mask in range(1, len(self.d)):
            total = DirectedInterval.constant(0.0)
            for partition in _partitions(mask):
                term = outer[len(partition)]
                for block in partition:
                    term = term * self.d[block]
                total = total + term
            derivatives[mask] = total
        return TensorIntervalJet(tuple(derivatives), self.axis_sizes)

    def reciprocal(self) -> "TensorIntervalJet":
        value = self.d[0]
        outer = [DirectedInterval.constant(0.0)]
        factorial = 1.0
        for order in range(1, self.directions + 1):
            factorial *= order
            outer.append(((-1.0) ** order) * factorial * value ** (-(order + 1)))
        return self._unary(value.reciprocal(), outer)

    def __truediv__(self, other: object) -> "TensorIntervalJet":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: object) -> "TensorIntervalJet":
        return self._coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "TensorIntervalJet":
        if not isinstance(exponent, int):
            raise TypeError("integer powers only")
        if exponent < 0:
            return (self ** (-exponent)).reciprocal()
        result = self.constant(1.0, self.axis_sizes)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "TensorIntervalJet":
        value = self.d[0].exp()
        return self._unary(value, [DirectedInterval.constant(0.0)] + [value] * self.directions)

    def positive_power(self, exponent: float) -> "TensorIntervalJet":
        value = self.d[0]
        outer = [DirectedInterval.constant(0.0)]
        coefficient = 1.0
        for order in range(1, self.directions + 1):
            coefficient *= exponent - (order - 1)
            outer.append(coefficient * value.positive_power(exponent - order))
        return self._unary(value.positive_power(exponent), outer)


def _linear(variables: list[TensorIntervalJet], coefficients: np.ndarray) -> TensorIntervalJet:
    result = TensorIntervalJet.constant(0.0, variables[0].axis_sizes)
    for variable, coefficient in zip(variables, coefficients):
        result = result + float(coefficient) * variable
    return result


def retained_action_tensor_interval(
    order: int,
    state_lower: np.ndarray,
    state_upper: np.ndarray,
    directions: list[np.ndarray | tuple[np.ndarray, np.ndarray]],
    *,
    points: int = 96,
) -> DirectedInterval:
    """Return the full mixed derivative interval for distinct action legs.

    A direction is either one fixed action-coordinate vector/matrix or a pair
    of lower/upper action-coordinate arrays.  Every matrix direction owns one
    output tensor axis.  Vector directions own a singleton axis.
    """

    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    total = 2 * qdim + mdim
    lower = np.asarray(state_lower, dtype=float)
    upper = np.asarray(state_upper, dtype=float)
    if lower.shape != (total,) or upper.shape != (total,):
        raise ValueError("state interval dimensions do not match order")
    frequencies = spectral_frequencies(order)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    direction_intervals: list[tuple[np.ndarray, np.ndarray]] = []
    axis_sizes = []
    for direction in directions:
        if isinstance(direction, tuple):
            dlo, dhi = (np.asarray(item, dtype=float) for item in direction)
        else:
            dlo = dhi = np.asarray(direction, dtype=float)
        if dlo.shape != dhi.shape or dlo.shape[0] != total or dlo.ndim not in (1, 2):
            raise ValueError("direction must be a state vector/matrix or endpoint pair")
        direction_intervals.append((dlo, dhi))
        axis_sizes.append(1 if dlo.ndim == 1 else dlo.shape[1])
    axes = tuple(axis_sizes)
    variables = []
    for state_index in range(total):
        derivative_intervals = []
        for dlo, dhi in direction_intervals:
            derivative_intervals.append(DirectedInterval.hull(
                dlo[state_index] / weights[state_index],
                dhi[state_index] / weights[state_index],
            ))
        variables.append(TensorIntervalJet.affine(
            DirectedInterval.hull(lower[state_index], upper[state_index]),
            derivative_intervals,
            axes,
        ))
    qj = variables[:qdim]
    vj = variables[qdim:2 * qdim]
    mj = variables[2 * qdim:]
    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
    cos_k = np.cos(4.0 * np.outer(ks, chi))
    sin_k = np.sin(4.0 * np.outer(ks, chi))
    cos_j = np.cos(4.0 * np.outer(js, chi))
    sin_j = np.sin(4.0 * np.outer(js, chi))
    u_coeff = qj[1:1 + order]
    w_coeff = qj[1 + order:1 + 2 * order]
    b_coeff = qj[1 + 2 * order:1 + 3 * order]
    radius = RADIUS0 * qj[0].exp()
    response_sigma = -0.5 + 2.0 * chi / math.pi - np.sin(4.0 * chi) / (2.0 * math.pi)
    localization = 1.0 - 4.0 * response_sigma**2
    kappa0 = 15.0 * 5.0 ** (1.0 / 3.0) / 4.0
    bulk = TensorIntervalJet.constant(0.0, axes)
    inertia = TensorIntervalJet.constant(0.0, axes)
    for index, coordinate in enumerate(chi):
        window = math.sin(2.0 * coordinate) ** 2
        window_prime = 2.0 * math.sin(4.0 * coordinate)
        u = _linear(u_coeff, cos_k[:, index])
        up = _linear(u_coeff, -4.0 * ks * sin_k[:, index])
        w = window * _linear(w_coeff, cos_j[:, index])
        bshape = window * _linear(b_coeff, cos_j[:, index])
        wp = _linear(w_coeff, window_prime * cos_j[:, index] + window * (-4.0 * js * sin_j[:, index]))
        bp_shape = _linear(b_coeff, window_prime * cos_j[:, index] + window * (-4.0 * js * sin_j[:, index]))
        C = radius * (u + w).exp()
        A = radius * (u + bshape).exp() * math.cos(coordinate)
        B = radius * (u - bshape).exp() * math.sin(coordinate)
        cp = up + wp
        ap = up + bp_shape - math.tan(coordinate)
        bp = up - bp_shape + 1.0 / math.tan(coordinate)
        volume = C * A**3 * B**3
        spatial_volume = A**3 * B**3
        lc_coeff = np.zeros(qdim)
        la_coeff = np.zeros(qdim)
        lb_coeff = np.zeros(qdim)
        lc_coeff[0] = la_coeff[0] = lb_coeff[0] = 1.0
        lc_coeff[1:1 + order] = la_coeff[1:1 + order] = lb_coeff[1:1 + order] = cos_k[:, index]
        lc_coeff[1 + order:1 + 2 * order] = window * cos_j[:, index]
        la_coeff[1 + 2 * order:1 + 3 * order] = window * cos_j[:, index]
        lb_coeff[1 + 2 * order:1 + 3 * order] = -window * cos_j[:, index]
        lapse_coeff = np.zeros(mdim)
        lapse_coeff[:order] = cos_k[:, index]
        lapse_prime_coeff = np.zeros(mdim)
        lapse_prime_coeff[:order] = -4.0 * ks * sin_k[:, index]
        shift_coeff = np.zeros(mdim)
        shift_coeff[order:2 * order] = math.sin(4.0 * coordinate) * cos_j[:, index]
        shift_prime_coeff = np.zeros(mdim)
        shift_prime_coeff[order:2 * order] = 4.0 * math.cos(4.0 * coordinate) * cos_j[:, index] + math.sin(4.0 * coordinate) * (-4.0 * js * sin_j[:, index])
        lc = _linear(vj, lc_coeff)
        la = _linear(vj, la_coeff)
        lb = _linear(vj, lb_coeff)
        log_n = _linear(mj, lapse_coeff)
        n_prime = _linear(mj, lapse_prime_coeff)
        beta = _linear(mj, shift_coeff)
        beta_prime = _linear(mj, shift_prime_coeff)
        lapse = log_n.exp()
        Hc = (lc - beta * cp - beta_prime) / lapse
        Ha = (la - beta * ap) / lapse
        Hb = (lb - beta * bp) / lapse
        adm = Hc**2 + 3.0 * Ha**2 + 3.0 * Hb**2 - (Hc + 3.0 * Ha + 3.0 * Hb)**2
        f_normal = -beta / lapse
        x_spatial = 1.0 / C**2 + 3.0 * math.cos(coordinate)**2 / A**2 + 3.0 * math.sin(coordinate)**2 / B**2
        x_eta = x_spatial - f_normal**2
        eta_legendre = 1.0 + x_eta**3
        fixed_gravity = ap**2 + bp**2 + 3.0 * ap * bp
        spatial_gravity = 3.0 * spatial_volume / C * lapse * (n_prime * (ap + bp) + fixed_gravity)
        algebraic = lapse * volume * (
            3.0 / A**2 + 3.0 / B**2 - 0.5 * kappa0
            - localization[index] * (0.5 * x_eta + 0.125 * x_eta**4)
            + 0.5 * adm
        )
        bulk = bulk + quadrature[index] * (spatial_gravity + algebraic)
        inertia = inertia + quadrature[index] * (volume * localization[index] * eta_legendre / lapse)
    action = bulk - 0.25 / (2.0 * HOPF_ORBIT_VOLUME**2 * inertia)
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary = _linear(u_coeff, signs_k)
    b_boundary = _linear(b_coeff, signs_j)
    A_boundary = radius * (u_boundary + b_boundary).exp() / math.sqrt(2.0)
    B_boundary = radius * (u_boundary - b_boundary).exp() / math.sqrt(2.0)
    R4 = A_boundary * B_boundary / (A_boundary**2 + B_boundary**2).positive_power(0.5)
    boundary_lapse_coeff = np.zeros(mdim)
    boundary_lapse_coeff[:order] = signs_k
    boundary_log_n = _linear(mj, boundary_lapse_coeff)
    result = action - standard_model_casimir_coefficient() / R4 * boundary_log_n.exp()
    full_mask = (1 << len(directions)) - 1
    value = result.d[full_mask]
    return DirectedInterval(np.squeeze(value.lo), np.squeeze(value.hi))


def interval_tensor_norm_upper(value: DirectedInterval) -> float:
    """Frobenius upper bound, also valid for every induced tensor norm."""

    lower = np.asarray(value.lo, dtype=float)
    upper = np.asarray(value.hi, dtype=float)
    midpoint = (lower + upper) / 2.0
    radius = (upper - lower) / 2.0
    return math.nextafter(
        float(np.linalg.norm(midpoint.ravel()) + np.linalg.norm(radius.ravel())),
        math.inf,
    )


__all__ = [
    "DirectedInterval",
    "TensorIntervalJet",
    "interval_tensor_norm_upper",
    "retained_action_tensor_interval",
]
