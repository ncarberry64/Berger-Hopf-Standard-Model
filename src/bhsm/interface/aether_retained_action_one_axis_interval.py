"""Compact outward-rounded retained-action jets with one signed matrix axis.

The general tensor evaluator retains every matrix leg and is the reference
implementation.  This module is the specialized equivalent needed for row
sweeps: exactly one direction is a fixed matrix and owns the signed output
axis; every other direction is a fixed vector or an interval vector.  Linear
action forms are assembled before nonlinear interval propagation, avoiding
the dense 98 by 98 tensor allocation without replacing the retained action.
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
from bhsm.interface.aether_retained_action_tensor_interval import DirectedInterval
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


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
class OneAxisIntervalJet:
    """Distinct-direction interval jet retaining one signed output vector."""

    d: tuple[DirectedInterval, ...]

    @classmethod
    def constant(cls, value: float, directions: int) -> "OneAxisIntervalJet":
        derivatives = [
            DirectedInterval.constant(0.0) for _ in range(1 << directions)
        ]
        derivatives[0] = DirectedInterval.constant(value)
        return cls(tuple(derivatives))

    @classmethod
    def affine(
        cls,
        value: DirectedInterval,
        directional_derivatives: list[DirectedInterval],
    ) -> "OneAxisIntervalJet":
        derivatives = [
            DirectedInterval.constant(0.0)
            for _ in range(1 << len(directional_derivatives))
        ]
        derivatives[0] = value
        for index, derivative in enumerate(directional_derivatives):
            derivatives[1 << index] = derivative
        return cls(tuple(derivatives))

    @property
    def directions(self) -> int:
        return (len(self.d) - 1).bit_length()

    def _coerce(self, other: object) -> "OneAxisIntervalJet":
        return (
            other if isinstance(other, OneAxisIntervalJet)
            else self.constant(float(other), self.directions)
        )

    def __neg__(self) -> "OneAxisIntervalJet":
        return OneAxisIntervalJet(tuple(-item for item in self.d))

    def __add__(self, other: object) -> "OneAxisIntervalJet":
        other = self._coerce(other)
        return OneAxisIntervalJet(tuple(a + b for a, b in zip(self.d, other.d)))

    __radd__ = __add__

    def __sub__(self, other: object) -> "OneAxisIntervalJet":
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "OneAxisIntervalJet":
        return self._coerce(other) - self

    def __mul__(self, other: object) -> "OneAxisIntervalJet":
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
        return OneAxisIntervalJet(tuple(derivatives))

    __rmul__ = __mul__

    def _unary(
        self,
        value: DirectedInterval,
        outer: list[DirectedInterval],
    ) -> "OneAxisIntervalJet":
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
        return OneAxisIntervalJet(tuple(derivatives))

    def reciprocal(self) -> "OneAxisIntervalJet":
        value = self.d[0]
        outer = [DirectedInterval.constant(0.0)]
        factorial = 1.0
        for order in range(1, self.directions + 1):
            factorial *= order
            outer.append(((-1.0) ** order) * factorial * value ** (-(order + 1)))
        return self._unary(value.reciprocal(), outer)

    def __truediv__(self, other: object) -> "OneAxisIntervalJet":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: object) -> "OneAxisIntervalJet":
        return self._coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "OneAxisIntervalJet":
        if not isinstance(exponent, int):
            raise TypeError("integer powers only")
        if exponent < 0:
            return (self ** (-exponent)).reciprocal()
        result = self.constant(1.0, self.directions)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def exp(self) -> "OneAxisIntervalJet":
        value = self.d[0].exp()
        return self._unary(
            value, [DirectedInterval.constant(0.0)] + [value] * self.directions
        )

    def positive_power(self, exponent: float) -> "OneAxisIntervalJet":
        value = self.d[0]
        outer = [DirectedInterval.constant(0.0)]
        coefficient = 1.0
        for order in range(1, self.directions + 1):
            coefficient *= exponent - (order - 1)
            outer.append(coefficient * value.positive_power(exponent - order))
        return self._unary(value.positive_power(exponent), outer)


def _linear_interval(
    coefficients: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> DirectedInterval:
    coefficients = np.asarray(coefficients, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    columns = coefficients.reshape((-1,) + (1,) * (lower.ndim - 1))
    lo_terms = np.where(columns >= 0.0, columns * lower, columns * upper)
    hi_terms = np.where(columns >= 0.0, columns * upper, columns * lower)

    def faithful_sum(terms: np.ndarray) -> float | np.ndarray:
        if terms.ndim == 1:
            return math.fsum(float(value) for value in terms)
        flat = terms.reshape((terms.shape[0], -1))
        result = np.asarray([
            math.fsum(float(value) for value in flat[:, column])
            for column in range(flat.shape[1])
        ])
        return result.reshape(terms.shape[1:])

    return DirectedInterval(
        DirectedInterval._down(faithful_sum(lo_terms)),
        DirectedInterval._up(faithful_sum(hi_terms)),
    )


def retained_action_one_axis_interval(
    order: int,
    state_lower: np.ndarray,
    state_upper: np.ndarray,
    directions: list[np.ndarray],
    direction_bounds: list[tuple[np.ndarray, np.ndarray] | None],
    *,
    output_index: int,
    points: int = 96,
) -> DirectedInterval:
    """Return a mixed derivative interval with one fixed matrix output leg."""

    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    total = 2 * qdim + mdim
    lower = np.asarray(state_lower, dtype=float)
    upper = np.asarray(state_upper, dtype=float)
    if lower.shape != (total,) or upper.shape != (total,):
        raise ValueError("state interval dimensions do not match order")
    if len(directions) != len(direction_bounds):
        raise ValueError("one bound entry is required for every direction")
    if not 0 <= output_index < len(directions):
        raise ValueError("output index is outside the direction list")
    frequencies = spectral_frequencies(order)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    checked_directions = [np.asarray(direction, dtype=float) for direction in directions]
    for index, (direction, bounds) in enumerate(zip(checked_directions, direction_bounds)):
        if index == output_index:
            if direction.ndim != 2 or direction.shape[0] != total or bounds is not None:
                raise ValueError("the output leg must be one fixed state matrix")
        elif bounds is None:
            if direction.shape != (total,):
                raise ValueError("a fixed non-output leg must be a state vector")
        else:
            blo, bhi = (np.asarray(item, dtype=float) for item in bounds)
            if direction.shape != (total,) or blo.shape != (total,) or bhi.shape != (total,):
                raise ValueError("an interval non-output leg must be a state vector box")

    def affine(coefficients: np.ndarray) -> OneAxisIntervalJet:
        coefficients = np.asarray(coefficients, dtype=float)
        normalized = coefficients / weights
        derivative_intervals = []
        for index, (direction, bounds) in enumerate(zip(
            checked_directions, direction_bounds
        )):
            if index == output_index:
                derivative_intervals.append(
                    _linear_interval(normalized, direction, direction)
                )
            elif bounds is None:
                derivative_intervals.append(DirectedInterval.constant(
                    float(direction @ normalized)
                ))
            else:
                derivative_intervals.append(
                    _linear_interval(normalized, bounds[0], bounds[1])
                )
        return OneAxisIntervalJet.affine(
            _linear_interval(coefficients, lower, upper), derivative_intervals
        )

    nodes, quadrature = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = quadrature * math.pi / 8.0
    ks = np.arange(1, order + 1, dtype=float)
    js = np.arange(order, dtype=float)
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
    bulk = OneAxisIntervalJet.constant(0.0, len(directions))
    inertia = OneAxisIntervalJet.constant(0.0, len(directions))

    for index, coordinate in enumerate(chi):
        window = math.sin(2.0 * coordinate) ** 2
        window_prime = 2.0 * math.sin(4.0 * coordinate)
        q_u = np.zeros(total)
        q_up = np.zeros(total)
        q_w = np.zeros(total)
        q_wp = np.zeros(total)
        q_b = np.zeros(total)
        q_bp = np.zeros(total)
        q_u[1:1 + order] = cos_k[:, index]
        q_up[1:1 + order] = -4.0 * ks * sin_k[:, index]
        q_w[1 + order:1 + 2 * order] = window * cos_j[:, index]
        q_wp[1 + order:1 + 2 * order] = (
            window_prime * cos_j[:, index]
            + window * (-4.0 * js * sin_j[:, index])
        )
        q_b[1 + 2 * order:1 + 3 * order] = window * cos_j[:, index]
        q_bp[1 + 2 * order:1 + 3 * order] = (
            window_prime * cos_j[:, index]
            + window * (-4.0 * js * sin_j[:, index])
        )
        scale = np.zeros(total)
        scale[0] = 1.0
        u, up = affine(q_u), affine(q_up)
        w, wp = affine(q_w), affine(q_wp)
        bshape, bp_shape = affine(q_b), affine(q_bp)
        radius = RADIUS0 * affine(scale).exp()
        C = radius * (u + w).exp()
        A = radius * (u + bshape).exp() * math.cos(coordinate)
        B = radius * (u - bshape).exp() * math.sin(coordinate)
        cp = up + wp
        ap = up + bp_shape - math.tan(coordinate)
        bp = up - bp_shape + 1.0 / math.tan(coordinate)
        volume = C * A**3 * B**3
        spatial_volume = A**3 * B**3

        lc = np.zeros(total)
        la = np.zeros(total)
        lb = np.zeros(total)
        voff = qdim
        lc[voff] = la[voff] = lb[voff] = 1.0
        lc[voff + 1:voff + 1 + order] = cos_k[:, index]
        la[voff + 1:voff + 1 + order] = cos_k[:, index]
        lb[voff + 1:voff + 1 + order] = cos_k[:, index]
        lc[voff + 1 + order:voff + 1 + 2 * order] = window * cos_j[:, index]
        la[voff + 1 + 2 * order:voff + 1 + 3 * order] = window * cos_j[:, index]
        lb[voff + 1 + 2 * order:voff + 1 + 3 * order] = -window * cos_j[:, index]
        moff = 2 * qdim
        lapse = np.zeros(total)
        lapse_prime = np.zeros(total)
        shift = np.zeros(total)
        shift_prime = np.zeros(total)
        lapse[moff:moff + order] = cos_k[:, index]
        lapse_prime[moff:moff + order] = -4.0 * ks * sin_k[:, index]
        shift[moff + order:moff + 2 * order] = (
            math.sin(4.0 * coordinate) * cos_j[:, index]
        )
        shift_prime[moff + order:moff + 2 * order] = (
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
        adm = Hc**2 + 3.0 * Ha**2 + 3.0 * Hb**2 - (Hc + 3.0 * Ha + 3.0 * Hb)**2
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
    signs_k = (-1.0) ** np.arange(1, order + 1)
    signs_j = (-1.0) ** np.arange(order)
    u_boundary_coeff = np.zeros(total)
    b_boundary_coeff = np.zeros(total)
    u_boundary_coeff[1:1 + order] = signs_k
    b_boundary_coeff[1 + 2 * order:1 + 3 * order] = signs_j
    u_boundary = affine(u_boundary_coeff)
    b_boundary = affine(b_boundary_coeff)
    scale = np.zeros(total)
    scale[0] = 1.0
    radius = RADIUS0 * affine(scale).exp()
    A_boundary = radius * (u_boundary + b_boundary).exp() / math.sqrt(2.0)
    B_boundary = radius * (u_boundary - b_boundary).exp() / math.sqrt(2.0)
    R4 = A_boundary * B_boundary / (
        A_boundary**2 + B_boundary**2
    ).positive_power(0.5)
    boundary_lapse = np.zeros(total)
    boundary_lapse[2 * qdim:2 * qdim + order] = signs_k
    result = action - (
        standard_model_casimir_coefficient() / R4
        * affine(boundary_lapse).exp()
    )
    full_mask = (1 << len(directions)) - 1
    return result.d[full_mask]


__all__ = ["OneAxisIntervalJet", "retained_action_one_axis_interval"]
