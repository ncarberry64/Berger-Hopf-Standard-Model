"""Exact shared-parameter cells of a stored native DOP853 action curve.

Every stored binary64 operand is imported as its exact rational value.
The same theta in [-1,1] parametrizes every coordinate and every jet.
Bernstein hulls are containing boxes, never a replacement polynomial.
"""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from math import comb
from pathlib import Path

import numpy as np


def rational(value):
    if isinstance(value, Fraction):
        return value
    if isinstance(value, (int, np.integer)):
        return Fraction(int(value))
    return Fraction.from_float(float(value))


def dense_power(left, coefficients):
    """Native alternating DOP853 basis, as powers of the native fraction."""
    poly = [Fraction(0)]
    for index, value in enumerate(reversed(coefficients)):
        poly[0] += rational(value)
        if index % 2 == 0:
            poly = [Fraction(0), *poly]
        else:
            shifted = poly + [Fraction(0)]
            for j, coefficient in enumerate(poly):
                shifted[j + 1] -= coefficient
            poly = shifted
    poly[0] += rational(left)
    return tuple(poly)


def compose(poly, origin, scale):
    """Exact coefficients of p(origin+scale*theta)."""
    return tuple(sum((value * comb(k, j) * origin ** (k-j) * scale ** j
                      for k, value in enumerate(poly) if k >= j), Fraction(0))
                 for j in range(len(poly)))


def derivative(poly):
    return tuple(j * poly[j] for j in range(1, len(poly))) or (Fraction(0),)


def evaluate(poly, theta):
    result = Fraction(0)
    for value in reversed(poly):
        result = result * theta + value
    return result


def bernstein_range(poly):
    """Containing exact range on theta in [-1,1], from Bernstein controls."""
    power = compose(poly, Fraction(-1), Fraction(2))
    degree = len(power) - 1
    controls = tuple(sum((power[j] * Fraction(comb(k, j), comb(degree, j))
                          for j in range(k + 1)), Fraction(0))
                     for k in range(degree + 1))
    return min(controls), max(controls)


@dataclass(frozen=True)
class NativeCurveCell:
    interval: int
    fraction_left: Fraction
    fraction_right: Fraction
    native_arc_left: Fraction
    native_width: Fraction
    powers: tuple
    state_weights: tuple = ()
    branch_reference: tuple = ()
    source_path: str = ""
    source_sha256: str = ""

    @property
    def arc_midpoint(self):
        return self.native_arc_left + self.native_width * (self.fraction_left + self.fraction_right) / 2

    @property
    def arc_radius(self):
        return self.native_width * (self.fraction_right - self.fraction_left) / 2

    def jet_coefficients(self, order=0):
        """Rows are theta powers, columns are coordinates; derivatives use arc."""
        if order not in (0, 1, 2, 3):
            raise ValueError("native jet order must be between zero and three")
        origin = (self.fraction_left + self.fraction_right) / 2
        scale = (self.fraction_right - self.fraction_left) / 2
        polynomials = []
        for value in self.powers:
            for _ in range(order):
                value = derivative(value)
            polynomials.append(tuple(c / self.native_width ** order
                                     for c in compose(value, origin, scale)))
        return np.asarray(polynomials, dtype=object).T

    def jet_value(self, order=0, theta=Fraction(0)):
        theta = rational(theta)
        if not -1 <= theta <= 1:
            raise ValueError("theta must belong to the native cell")
        return tuple(evaluate(poly, theta) for poly in self.jet_coefficients(order).T)

    def jet_bounds(self, order=0):
        return tuple(bernstein_range(poly) for poly in self.jet_coefficients(order).T)


def native_cell(left, coefficients, native_arc_left, native_width,
                fraction_left=Fraction(0), fraction_right=Fraction(1), interval=0):
    native_width, lo, hi = map(rational, (native_width, fraction_left, fraction_right))
    coefficients = np.asarray(coefficients)
    if native_width <= 0 or not 0 <= lo < hi <= 1:
        raise ValueError("positive native width and an ordered native fraction cell required")
    if coefficients.ndim != 2 or coefficients.shape[1] != len(left):
        raise ValueError("complete native coefficient rows and coordinate columns required")
    powers = tuple(dense_power(value, coefficients[:, j]) for j, value in enumerate(left))
    return NativeCurveCell(interval, lo, hi, rational(native_arc_left), native_width, powers)


def load_native_cell(path, interval=0, fraction_left=Fraction(0), fraction_right=None):
    """Load a current stored cell, clipped by the actual retained stop fraction."""
    path = Path(path).resolve()
    with np.load(path, allow_pickle=False) as data:
        terminal = int(data["stop_bracket_fine_grid_index"][0])
        if not 0 <= interval <= terminal:
            raise ValueError("native interval lies beyond the retained stop")
        cap = rational(data["stop_dense_fraction"][0]) if interval == terminal else Fraction(1)
        hi = cap if fraction_right is None else rational(fraction_right)
        if hi > cap:
            raise ValueError("native cell extends beyond the retained stop fraction")
        grid = data["fine_grid_action_lengths"]
        cell = native_cell(data["fine_grid_augmented_action_values"][interval],
                           data["fine_grid_DOP853_dense_coefficients"][interval],
                           rational(grid[interval]), rational(grid[interval+1])-rational(grid[interval]),
                           fraction_left, hi, interval)
        weights = tuple(rational(v) for v in data["state_weights"])
        reference = tuple(float(v) for v in data["branch_reference"])
    return NativeCurveCell(**{**cell.__dict__, "state_weights": weights,
                             "branch_reference": reference, "source_path": str(path),
                             "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()})
