"""Exact jets and norm majorants for the retained Euler--Dirac solve."""

from __future__ import annotations

import math

import numpy as np


_KEYS = ("base", "first_left", "first_right", "mixed_second")


def _checked_matrix(value: np.ndarray, shape: tuple[int, int], name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if matrix.shape != shape or not np.all(np.isfinite(matrix)):
        raise ValueError(f"finite {name} matrix of shape {shape} required")
    return matrix


def _checked_vector(value: np.ndarray, size: int, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=complex)
    if vector.shape != (size,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"finite {name} vector of length {size} required")
    return vector


def implicit_linear_solve_jets(
    operator_jets: dict[str, np.ndarray],
    right_hand_side_jets: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Differentiate ``D(e,d) s(e,d)=b(e,d)`` through mixed order.

    The returned equations use the same base factorization for every jet and
    never differentiate an explicitly formed inverse.
    """

    if not all(key in operator_jets and key in right_hand_side_jets for key in _KEYS):
        raise KeyError("base, first_left, first_right, and mixed_second required")
    base = np.asarray(operator_jets["base"], dtype=complex)
    if base.ndim != 2 or base.shape[0] != base.shape[1]:
        raise ValueError("square base Euler--Dirac operator required")
    size = base.shape[0]
    operators = {
        key: _checked_matrix(operator_jets[key], (size, size), key)
        for key in _KEYS
    }
    rhs = {
        key: _checked_vector(right_hand_side_jets[key], size, key)
        for key in _KEYS
    }
    d = operators["base"]
    s = np.linalg.solve(d, rhs["base"])
    sh = np.linalg.solve(
        d, rhs["first_left"] - operators["first_left"] @ s
    )
    sk = np.linalg.solve(
        d, rhs["first_right"] - operators["first_right"] @ s
    )
    shk = np.linalg.solve(
        d,
        rhs["mixed_second"]
        - operators["mixed_second"] @ s
        - operators["first_left"] @ sk
        - operators["first_right"] @ sh,
    )
    return {
        "base": s,
        "first_left": sh,
        "first_right": sk,
        "mixed_second": shk,
    }


def implicit_linear_solve_jet_bounds(
    inverse_bound: float,
    rhs_bound: float,
    rhs_first_left_bound: float,
    rhs_first_right_bound: float,
    rhs_mixed_second_bound: float,
    operator_first_left_bound: float,
    operator_first_right_bound: float,
    operator_mixed_second_bound: float,
) -> dict[str, float]:
    """Return the direct submultiplicative norm bounds for the solve jets."""

    values = tuple(
        float(value)
        for value in (
            inverse_bound,
            rhs_bound,
            rhs_first_left_bound,
            rhs_first_right_bound,
            rhs_mixed_second_bound,
            operator_first_left_bound,
            operator_first_right_bound,
            operator_mixed_second_bound,
        )
    )
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("finite nonnegative solve-jet bounds required")
    alpha, b, bh, bk, bhk, dh, dk, dhk = values
    s = alpha * b
    sh = alpha * (bh + dh * s)
    sk = alpha * (bk + dk * s)
    shk = alpha * (bhk + dhk * s + dh * sk + dk * sh)
    return {
        "base": s,
        "first_left": sh,
        "first_right": sk,
        "mixed_second": shk,
    }


def jacobi_cocycle_bounds(
    first_generator_bound: float,
    second_generator_bound: float,
    duration: float,
) -> dict[str, float]:
    """Bound unit first and zero-initial-mixed second state Jacobi fields."""

    a = float(first_generator_bound)
    b = float(second_generator_bound)
    time = float(duration)
    if any(not math.isfinite(value) or value < 0.0 for value in (a, b, time)):
        raise ValueError("finite nonnegative cocycle data required")
    first = math.exp(a * time)
    mixed = b * time if a == 0.0 else (b / a) * first * math.expm1(a * time)
    return {"first": first, "mixed_second": mixed}


__all__ = [
    "implicit_linear_solve_jets",
    "implicit_linear_solve_jet_bounds",
    "jacobi_cocycle_bounds",
]
