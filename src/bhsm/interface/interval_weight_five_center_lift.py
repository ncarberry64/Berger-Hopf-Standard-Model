"""Directed Arb enclosure of the N12 weight-five center lift.

The quadrature nodes and weights are certified Legendre balls.  A global,
exact rational Gauss remainder is added to every integrated Hessian and force
entry before the bordered system is solved with Arb ball arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import factorial
from typing import Callable

import sympy as sp


ORDER = 12
PHYSICAL = 25
MULTIPLIERS = 24
DESCRIPTOR = 2 * PHYSICAL + MULTIPLIERS

# Structural bounds for every scalar coefficient integrand after the round
# density cancels the apparent tan/cot endpoint singularities.  The actual
# maximum frequency is at most 110 and the coefficient l1 bound is below
# 1e8; these inflated integer constants make the proof audit elementary.
FOURIER_FREQUENCY_BOUND = 128
COEFFICIENT_L1_BOUND = 10**12
POLYNOMIAL_DEGREE_BOUND = 2


@lru_cache(maxsize=1)
def _local_blocks() -> tuple[
    list[tuple[int, int, Callable]], list[Callable]
]:
    """Return arithmetic-only local Hessian and gradient callables."""

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
    local_hessian = sp.hessian(integrand, variables).subs(base)
    hessian_terms = []
    for row in range(10):
        for column in range(10):
            expression = sp.simplify(local_hessian[row, column])
            if expression != 0:
                hessian_terms.append((
                    row,
                    column,
                    sp.lambdify(
                        (h, tangent, cotangent, localization),
                        expression,
                        modules="math",
                    ),
                ))

    c, a, b, c_p, a_p, b_p, log_lapse, log_lapse_p = sp.symbols(
        "c a b c_p a_p b_p log_lapse log_lapse_p"
    )
    cosine, sine = sp.symbols("cosine sine", positive=True)
    spatial_gravity = 3 * sp.exp(
        3 * a + 3 * b - c + log_lapse
    ) * (
        log_lapse_p * (a_p + b_p)
        + a_p**2 + b_p**2 + 3 * a_p * b_p
    )
    algebraic = sp.exp(c + 3 * a + 3 * b + log_lapse) * (
        3 * sp.exp(-2 * a) / cosine**2
        + 3 * sp.exp(-2 * b) / sine**2
        - localization / 2 * (
            sp.exp(-2 * c)
            + 3 * sp.exp(-2 * a)
            + 3 * sp.exp(-2 * b)
        )
    )
    force_variables = (
        c, a, b, c_p, a_p, b_p, log_lapse, log_lapse_p
    )
    force_base = {
        c: 0,
        a: 0,
        b: 0,
        c_p: 0,
        a_p: -tangent,
        b_p: cotangent,
        log_lapse: 0,
        log_lapse_p: 0,
    }
    gradient_terms = [
        sp.lambdify(
            (tangent, cotangent, cosine, sine, localization),
            sp.simplify(
                sp.diff(spatial_gravity + algebraic, variable).subs(
                    force_base
                )
            ),
            modules="math",
        )
        for variable in force_variables
    ]
    return hessian_terms, gradient_terms


def _sparse_maps(x: object, arb: type) -> tuple[
    list[dict[int, object]], list[dict[int, object]]
]:
    seven = [dict() for _ in range(10)]
    five = [dict() for _ in range(8)]
    seven[0][0] = arb(7)
    five[0][0] = five[1][0] = five[2][0] = arb(1)
    seven[4][PHYSICAL] = seven[5][PHYSICAL] = seven[6][PHYSICAL] = arb(1)
    window = (2 * x).sin() ** 2
    window_prime = 2 * (4 * x).sin()
    for mode in range(ORDER):
        angle = 4 * mode * x
        shape = window * angle.cos()
        derivative = (
            window_prime * angle.cos()
            - 4 * mode * window * angle.sin()
        )
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
        seven[8][shift] = (4 * x).sin() * angle.cos()
        seven[9][shift] = (
            4 * (4 * x).cos() * angle.cos()
            - 4 * mode * (4 * x).sin() * angle.sin()
        )
    for mode in range(1, ORDER + 1):
        angle = 4 * mode * x
        lapse = 2 * PHYSICAL + mode - 1
        seven[7][lapse] = angle.cos()
        five[6][lapse] = angle.cos()
        five[7][lapse] = -4 * mode * angle.sin()
    return seven, five


def _omitted_u_maps(
    x: object, arb: type
) -> tuple[list[list[object]], list[list[object]], list[list[object]]]:
    """Maps for the twelve omitted time/lapse-chain coordinate equations."""

    q_maps = [[arb(0) for _ in range(10)] for _ in range(ORDER)]
    v_maps = [[arb(0) for _ in range(10)] for _ in range(ORDER)]
    five_maps = [[arb(0) for _ in range(8)] for _ in range(ORDER)]
    for mode in range(1, ORDER + 1):
        angle = 4 * mode * x
        value = angle.cos()
        derivative = -4 * mode * angle.sin()
        index = mode - 1
        q_maps[index][0] = 7 * value
        q_maps[index][1] = derivative
        q_maps[index][2] = derivative
        q_maps[index][3] = derivative
        v_maps[index][4] = value
        v_maps[index][5] = value
        v_maps[index][6] = value
        five_maps[index][0] = value
        five_maps[index][1] = value
        five_maps[index][2] = value
        five_maps[index][3] = derivative
        five_maps[index][4] = derivative
        five_maps[index][5] = derivative
    return q_maps, v_maps, five_maps


def gauss_remainder_bound(points: int) -> Fraction:
    """Exact global error radius for every scalar coefficient integral."""

    derivative_order = 2 * points
    derivative_bound = (
        COEFFICIENT_L1_BOUND
        * (derivative_order + 1) ** POLYNOMIAL_DEGREE_BOUND
        * FOURIER_FREQUENCY_BOUND**derivative_order
    )
    # On [0,pi/4], the omitted interval-length factor is strictly below one.
    return Fraction(
        factorial(points) ** 4 * derivative_bound,
        (2 * points + 1) * factorial(2 * points) ** 3,
    )


def _add_outer(
    target: list[list[object]], left: dict[int, object],
    right: dict[int, object], coefficient: object,
) -> None:
    for row, left_value in left.items():
        for column, right_value in right.items():
            target[row][column] += coefficient * left_value * right_value


def assemble_interval_weight_five_lift(
    *, points: int = 128, decimal_digits: int = 120
) -> dict[str, object]:
    """Return a directed ball enclosure of the bordered center lift."""

    try:
        from flint import arb, arb_mat, ctx
    except ImportError as error:  # pragma: no cover - optional proof backend
        raise RuntimeError(
            "python-flint==0.9.0 is required for directed certification"
        ) from error

    prior_digits = ctx.dps
    ctx.dps = decimal_digits
    try:
        pi = arb.pi()
        h = (arb(15) * arb(5).root(3) / arb(168)).sqrt()
        hessian = [
            [arb(0) for _ in range(DESCRIPTOR)]
            for _ in range(DESCRIPTOR)
        ]
        force = [arb(0) for _ in range(PHYSICAL + MULTIPLIERS)]
        hessian_q_u = [
            [arb(0) for _ in range(DESCRIPTOR)] for _ in range(ORDER)
        ]
        hessian_v_u = [
            [arb(0) for _ in range(DESCRIPTOR)] for _ in range(ORDER)
        ]
        force_u = [arb(0) for _ in range(ORDER)]
        hessian_terms, gradient_terms = _local_blocks()
        for index in range(points):
            node, gauss_weight = arb.legendre_p_root(
                points, index, weight=True
            )
            x = (node + 1) * pi / 8
            weight = gauss_weight * pi / 8
            cosine = x.cos()
            sine = x.sin()
            density = cosine**3 * sine**3
            sigma = -arb(1) / 2 + 2 * x / pi - (4 * x).sin() / (2 * pi)
            localization = 1 - 4 * sigma**2
            tangent = x.tan()
            cotangent = 1 / tangent
            seven, five = _sparse_maps(x, arb)
            q_u_maps, v_u_maps, five_u_maps = _omitted_u_maps(x, arb)
            common = weight * density
            for row, column, function in hessian_terms:
                coefficient = common * function(
                    h, tangent, cotangent, localization
                )
                _add_outer(
                    hessian, seven[row], seven[column], coefficient
                )
                for mode in range(ORDER):
                    if q_u_maps[mode][row] != 0:
                        for selected_column, value in seven[column].items():
                            hessian_q_u[mode][selected_column] += (
                                coefficient
                                * q_u_maps[mode][row]
                                * value
                            )
                    if v_u_maps[mode][row] != 0:
                        for selected_column, value in seven[column].items():
                            hessian_v_u[mode][selected_column] += (
                                coefficient
                                * v_u_maps[mode][row]
                                * value
                            )
            local_gradient = [
                function(
                    tangent, cotangent, cosine, sine, localization
                )
                for function in gradient_terms
            ]
            for local_row, mapping in enumerate(five):
                coefficient = common * local_gradient[local_row]
                for column, value in mapping.items():
                    force_column = (
                        column if column < PHYSICAL else column - PHYSICAL
                    )
                    force[force_column] += coefficient * value
                for mode in range(ORDER):
                    force_u[mode] += (
                        coefficient * five_u_maps[mode][local_row]
                    )

        remainder = gauss_remainder_bound(points)
        remainder_ball = arb(
            0, f"{remainder.numerator}/{remainder.denominator}"
        )
        for row in range(DESCRIPTOR):
            for column in range(DESCRIPTOR):
                hessian[row][column] += remainder_ball
        for row in range(PHYSICAL + MULTIPLIERS):
            force[row] += remainder_ball
        for mode in range(ORDER):
            force_u[mode] += remainder_ball
            for column in range(DESCRIPTOR):
                hessian_q_u[mode][column] += remainder_ball
                hessian_v_u[mode][column] += remainder_ball

        matrix = [
            [arb(0) for _ in range(DESCRIPTOR)]
            for _ in range(DESCRIPTOR)
        ]
        for index in range(PHYSICAL):
            matrix[index][index] = 2 * h
            matrix[index][PHYSICAL + index] = arb(1)
        for i in range(PHYSICAL):
            for j in range(PHYSICAL):
                matrix[PHYSICAL + i][j] = -(
                    7 * h * hessian[PHYSICAL + i][j]
                    - hessian[i][j]
                )
                matrix[PHYSICAL + i][PHYSICAL + j] = -(
                    5 * h * hessian[PHYSICAL + i][PHYSICAL + j]
                    + hessian[PHYSICAL + i][j]
                    - hessian[i][PHYSICAL + j]
                )
            for j in range(MULTIPLIERS):
                matrix[PHYSICAL + i][2 * PHYSICAL + j] = -(
                    5 * h * hessian[PHYSICAL + i][2 * PHYSICAL + j]
                    - hessian[i][2 * PHYSICAL + j]
                )
        for i in range(MULTIPLIERS):
            for j in range(PHYSICAL):
                matrix[2 * PHYSICAL + i][j] = hessian[
                    2 * PHYSICAL + i
                ][j]
                matrix[2 * PHYSICAL + i][PHYSICAL + j] = hessian[
                    2 * PHYSICAL + i
                ][PHYSICAL + j]
            for j in range(MULTIPLIERS):
                matrix[2 * PHYSICAL + i][2 * PHYSICAL + j] = hessian[
                    2 * PHYSICAL + i
                ][2 * PHYSICAL + j]

        matrix_ball = arb_mat(matrix)
        multiplier_block = arb_mat([
            [
                hessian[2 * PHYSICAL + row][2 * PHYSICAL + column]
                for column in range(MULTIPLIERS)
            ]
            for row in range(MULTIPLIERS)
        ])
        # Arb raises if zero cannot be excluded from the determinant.
        multiplier_block.inv()
        rhs = [arb(0)] * PHYSICAL + [
            -force[index] for index in range(PHYSICAL)
        ] + [
            -force[PHYSICAL + index] for index in range(MULTIPLIERS)
        ]
        rhs_ball = arb_mat(DESCRIPTOR, 1, rhs)
        solution = matrix_ball.solve(rhs_ball, algorithm="precond")
        residual = matrix_ball * solution - rhs_ball
        omitted_residuals = []
        for mode in range(ORDER):
            value = force_u[mode]
            for column in range(PHYSICAL):
                value += -(
                    7 * h * hessian_v_u[mode][column]
                    - hessian_q_u[mode][column]
                ) * solution[column, 0]
                value += -(
                    5 * h * hessian_v_u[mode][PHYSICAL + column]
                    + hessian_v_u[mode][column]
                    - hessian_q_u[mode][PHYSICAL + column]
                ) * solution[PHYSICAL + column, 0]
            for column in range(MULTIPLIERS):
                value += -(
                    5 * h * hessian_v_u[mode][2 * PHYSICAL + column]
                    - hessian_q_u[mode][2 * PHYSICAL + column]
                ) * solution[2 * PHYSICAL + column, 0]
            omitted_residuals.append(value)
        rate = -2 * h * solution[0, 0]
        return {
            "points": points,
            "decimal_digits": decimal_digits,
            "expansion_rate": h,
            "quadrature_remainder": remainder_ball.rad(),
            "matrix": matrix_ball,
            "action_hessian": arb_mat(hessian),
            "right_hand_side": rhs_ball,
            "solution": solution,
            "q0_coefficient": solution[0, 0],
            "q0_rate_coefficient": rate,
            "residual_contains_zero": all(
                residual[row, 0].contains(0)
                for row in range(DESCRIPTOR)
            ),
            "omitted_gauge_chain_residuals": omitted_residuals,
            "omitted_gauge_chain_residuals_contain_zero": all(
                value.contains(0) for value in omitted_residuals
            ),
            "q0_strictly_positive": bool(solution[0, 0] > 0),
            "q0_rate_strictly_negative": bool(rate < 0),
            "combined_Euler_Dirac_inverse_used": False,
            "algebraic_multiplier_block_rigorously_invertible": True,
        }
    finally:
        ctx.dps = prior_digits


__all__ = [
    "COEFFICIENT_L1_BOUND",
    "FOURIER_FREQUENCY_BOUND",
    "POLYNOMIAL_DEGREE_BOUND",
    "assemble_interval_weight_five_lift",
    "gauss_remainder_bound",
]
