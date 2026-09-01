"""Analytic local-block assembly of the N12 weight-five center lift."""

from __future__ import annotations

from functools import lru_cache
from typing import Callable

import mpmath as mp
import sympy as sp


ORDER = 12
PHYSICAL = 25
MULTIPLIERS = 24
DESCRIPTOR = 2 * PHYSICAL + MULTIPLIERS


@lru_cache(maxsize=1)
def _local_weight_seven_hessian() -> list[tuple[int, int, Callable]]:
    rho, cp, ap, bp, lc, la, lb, n, beta, beta_p = sp.symbols(
        "rho cp ap bp lc la lb n beta beta_p"
    )
    h, tangent, cotangent, localization = sp.symbols(
        "h tangent cotangent localization"
    )
    lapse = sp.exp(n)
    hc = (h + lc - beta * cp - beta_p) / lapse
    ha = (h + la - beta * ap) / lapse
    hb = (h + lb - beta * bp) / lapse
    adm = hc**2 + 3 * ha**2 + 3 * hb**2 - (hc + 3 * ha + 3 * hb) ** 2
    # The round zero-energy relation is kappa0=42*h^2.
    integrand = sp.exp(rho + n) * (adm / 2 - 21 * h**2)
    integrand += sp.exp(rho - n) * localization * beta**2 / 2
    variables = (rho, cp, ap, bp, lc, la, lb, n, beta, beta_p)
    base = {
        rho: 0,
        cp: 0,
        ap: -tangent,
        bp: cotangent,
        lc: 0,
        la: 0,
        lb: 0,
        n: 0,
        beta: 0,
        beta_p: 0,
    }
    hessian = sp.hessian(integrand, variables).subs(base)
    result = []
    for row in range(10):
        for column in range(10):
            expression = sp.simplify(hessian[row, column])
            if expression != 0:
                result.append((
                    row,
                    column,
                    sp.lambdify(
                        (h, tangent, cotangent, localization),
                        expression,
                        modules="mpmath",
                    ),
                ))
    return result


@lru_cache(maxsize=1)
def _local_weight_five_gradient() -> list[Callable]:
    c, a, b, cp, ap, bp, n, n_p = sp.symbols(
        "c a b cp ap bp n n_p"
    )
    x, localization = sp.symbols("x localization")
    spatial_gravity = 3 * sp.exp(3 * a + 3 * b - c + n) * (
        n_p * (ap + bp) + ap**2 + bp**2 + 3 * ap * bp
    )
    algebraic = sp.exp(c + 3 * a + 3 * b + n) * (
        3 * sp.sec(x) ** 2 * sp.exp(-2 * a)
        + 3 * sp.csc(x) ** 2 * sp.exp(-2 * b)
        - localization / 2 * (
            sp.exp(-2 * c) + 3 * sp.exp(-2 * a) + 3 * sp.exp(-2 * b)
        )
    )
    variables = (c, a, b, cp, ap, bp, n, n_p)
    base = {
        c: 0,
        a: 0,
        b: 0,
        cp: 0,
        ap: -sp.tan(x),
        bp: sp.cot(x),
        n: 0,
        n_p: 0,
    }
    return [
        sp.lambdify(
            (x, localization),
            sp.simplify(sp.diff(spatial_gravity + algebraic, variable).subs(base)),
            modules="mpmath",
        )
        for variable in variables
    ]


def _localization(x: mp.mpf) -> mp.mpf:
    sigma = -mp.mpf("0.5") + 2 * x / mp.pi - mp.sin(4 * x) / (2 * mp.pi)
    return 1 - 4 * sigma**2


def _sparse_maps(x: mp.mpf) -> tuple[list[dict[int, mp.mpf]], list[dict[int, mp.mpf]]]:
    """Return maps to the 10 weight-seven and 8 weight-five local variables."""

    seven = [dict() for _ in range(10)]
    five = [dict() for _ in range(8)]
    seven[0][0] = mp.mpf(7)  # rho from common scale
    five[0][0] = five[1][0] = five[2][0] = mp.mpf(1)
    seven[4][PHYSICAL] = seven[5][PHYSICAL] = seven[6][PHYSICAL] = mp.mpf(1)
    window = mp.sin(2 * x) ** 2
    window_p = 2 * mp.sin(4 * x)
    for mode in range(ORDER):
        angle = 4 * mode * x
        shape = window * mp.cos(angle)
        derivative = window_p * mp.cos(angle) - 4 * mode * window * mp.sin(angle)
        wq = 1 + mode
        bq = 1 + ORDER + mode
        seven[0][wq] = shape
        seven[1][wq] = derivative
        seven[2][bq] = derivative
        seven[3][bq] = -derivative
        seven[4][PHYSICAL + wq] = shape
        seven[5][PHYSICAL + bq] = shape
        seven[6][PHYSICAL + bq] = -shape
        five[0][wq] = shape
        five[3][wq] = derivative
        five[1][bq] = shape
        five[2][bq] = -shape
        five[4][bq] = derivative
        five[5][bq] = -derivative
        shift = 2 * PHYSICAL + ORDER + mode
        seven[8][shift] = mp.sin(4 * x) * mp.cos(angle)
        seven[9][shift] = (
            4 * mp.cos(4 * x) * mp.cos(angle)
            - 4 * mode * mp.sin(4 * x) * mp.sin(angle)
        )
    for mode in range(1, ORDER + 1):
        angle = 4 * mode * x
        lapse = 2 * PHYSICAL + mode - 1
        seven[7][lapse] = mp.cos(angle)
        five[6][lapse] = mp.cos(angle)
        five[7][lapse] = -4 * mode * mp.sin(angle)
    return seven, five


def _add_outer(
    target: list[list[mp.mpf]], left: dict[int, mp.mpf],
    right: dict[int, mp.mpf], coefficient: mp.mpf,
) -> None:
    for row, left_value in left.items():
        for column, right_value in right.items():
            target[row][column] += coefficient * left_value * right_value


def assemble_weight_five_lift(
    *, points: int = 80, decimal_digits: int = 80
) -> dict[str, object]:
    """Assemble and solve the analytic local-block bordered lift."""

    with mp.workdps(decimal_digits):
        nodes, weights = mp.gauss_quadrature(points, "legendre")
        h = mp.sqrt(mp.mpf(15) * mp.root(5, 3) / (4 * 42))
        hessian = [
            [mp.mpf(0) for _ in range(DESCRIPTOR)]
            for _ in range(DESCRIPTOR)
        ]
        force = [mp.mpf(0) for _ in range(PHYSICAL + MULTIPLIERS)]
        hessian_terms = _local_weight_seven_hessian()
        gradient_terms = _local_weight_five_gradient()
        for node, gauss_weight in zip(nodes, weights):
            x = (node + 1) * mp.pi / 8
            weight = gauss_weight * mp.pi / 8
            density = mp.cos(x) ** 3 * mp.sin(x) ** 3
            localization = _localization(x)
            tangent = mp.tan(x)
            cotangent = 1 / tangent
            seven, five = _sparse_maps(x)
            common = weight * density
            for row, column, function in hessian_terms:
                coefficient = common * function(
                    h, tangent, cotangent, localization
                )
                _add_outer(hessian, seven[row], seven[column], coefficient)
            local_gradient = [
                function(x, localization) for function in gradient_terms
            ]
            for local_row, mapping in enumerate(five):
                coefficient = common * local_gradient[local_row]
                for column, value in mapping.items():
                    # five maps into q25 followed by multiplier24; skip the
                    # absent velocity slot in the seven descriptor ordering.
                    force_column = column if column < PHYSICAL else column - PHYSICAL
                    force[force_column] += coefficient * value

        q = slice(0, PHYSICAL)
        v = slice(PHYSICAL, 2 * PHYSICAL)
        m = slice(2 * PHYSICAL, DESCRIPTOR)
        A = mp.matrix(DESCRIPTOR)
        E = mp.matrix(DESCRIPTOR)
        for index in range(PHYSICAL):
            A[index, PHYSICAL + index] = 1
            E[index, index] = 1
        H = mp.matrix(hessian)
        for i in range(PHYSICAL):
            for j in range(PHYSICAL):
                A[PHYSICAL + i, j] = -(7 * h * H[PHYSICAL + i, j] - H[i, j])
                A[PHYSICAL + i, PHYSICAL + j] = -(
                    7 * h * H[PHYSICAL + i, PHYSICAL + j]
                    + H[PHYSICAL + i, j] - H[i, PHYSICAL + j]
                )
                E[PHYSICAL + i, PHYSICAL + j] = H[PHYSICAL + i, PHYSICAL + j]
            for j in range(MULTIPLIERS):
                A[PHYSICAL + i, 2 * PHYSICAL + j] = -(
                    7 * h * H[PHYSICAL + i, 2 * PHYSICAL + j]
                    - H[i, 2 * PHYSICAL + j]
                )
                E[PHYSICAL + i, 2 * PHYSICAL + j] = H[
                    PHYSICAL + i, 2 * PHYSICAL + j
                ]
        for i in range(MULTIPLIERS):
            for j in range(PHYSICAL):
                A[2 * PHYSICAL + i, j] = H[2 * PHYSICAL + i, j]
                A[2 * PHYSICAL + i, PHYSICAL + j] = H[
                    2 * PHYSICAL + i, PHYSICAL + j
                ]
            for j in range(MULTIPLIERS):
                A[2 * PHYSICAL + i, 2 * PHYSICAL + j] = H[
                    2 * PHYSICAL + i, 2 * PHYSICAL + j
                ]
        matrix = A + 2 * h * E
        rhs = mp.matrix(
            [mp.mpf(0)] * PHYSICAL
            + [-force[i] for i in range(PHYSICAL)]
            + [-force[PHYSICAL + i] for i in range(MULTIPLIERS)]
        )
        solution = mp.lu_solve(matrix, rhs)
        residual = mp.norm(matrix * solution - rhs) / mp.norm(rhs)
        return {
            "expansion_rate": h,
            "matrix": matrix,
            "right_hand_side": rhs,
            "solution": solution,
            "relative_residual": residual,
            "q0_coefficient": solution[0],
            "q0_rate_coefficient": -2 * h * solution[0],
            "solution_norm": mp.norm(solution),
        }


__all__ = ["assemble_weight_five_lift"]
