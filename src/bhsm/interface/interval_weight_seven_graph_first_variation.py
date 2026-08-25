"""Directed first variation of the N12 asymptotic bordered graph operator.

The implementation differentiates the exact local weight-seven action three
times, projects its sparse cubic tensor to the 74-dimensional physical
quotient, and solves the fixed bordered recurrence for every normalized
product-coordinate direction.  It never forms the bordered or Euler--Dirac
inverse.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import permutations
from math import factorial

import sympy as sp

from bhsm.interface.interval_weight_five_center_lift import (
    DESCRIPTOR,
    MULTIPLIERS,
    ORDER,
    PHYSICAL,
    _sparse_maps,
    assemble_interval_weight_five_lift,
)


THIRD_FOURIER_FREQUENCY_BOUND = 256
THIRD_COEFFICIENT_L1_BOUND = 10**18
THIRD_POLYNOMIAL_DEGREE_BOUND = 3


@lru_cache(maxsize=1)
def _local_ordered_third_terms() -> list[tuple[int, int, int, object]]:
    """Return all nonzero ordered local D3L coefficient callables."""

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
    terms: list[tuple[int, int, int, object]] = []
    for first in range(10):
        for second in range(first, 10):
            for third in range(second, 10):
                expression = sp.simplify(
                    sp.diff(
                        integrand,
                        variables[first],
                        variables[second],
                        variables[third],
                    ).subs(base)
                )
                if expression == 0:
                    continue
                function = sp.lambdify(
                    (h, tangent, cotangent, localization),
                    expression,
                    modules="math",
                )
                for ordered in sorted(set(permutations((first, second, third)))):
                    terms.append((*ordered, function))
    return terms


def third_gauss_remainder_bound(points: int) -> Fraction:
    """Exact inflated Gauss error radius for each projected D3L entry."""

    derivative_order = 2 * points
    derivative_bound = (
        THIRD_COEFFICIENT_L1_BOUND
        * (derivative_order + 1) ** THIRD_POLYNOMIAL_DEGREE_BOUND
        * THIRD_FOURIER_FREQUENCY_BOUND**derivative_order
    )
    return Fraction(
        factorial(points) ** 4 * derivative_bound,
        (2 * points + 1) * factorial(2 * points) ** 3,
    )


def squared_product_weights() -> list[int]:
    """Exact H6/H5/H6 squared weights in descriptor order."""

    windowed = list(range(0, 48, 4))
    lapse = list(range(4, 52, 4))
    coordinates = [0] + windowed + windowed
    multipliers = lapse + windowed
    return (
        [(1 + omega * omega) ** 6 for omega in coordinates]
        + [(1 + omega * omega) ** 5 for omega in coordinates]
        + [(1 + omega * omega) ** 6 for omega in multipliers]
    )


def descriptor_labels() -> list[str]:
    coordinates = ["q0"] + [f"w_{j}" for j in range(ORDER)] + [
        f"b_{j}" for j in range(ORDER)
    ]
    velocities = ["dot_q0"] + [f"dot_w_{j}" for j in range(ORDER)] + [
        f"dot_b_{j}" for j in range(ORDER)
    ]
    multipliers = [f"log_lapse_{j}" for j in range(1, ORDER + 1)] + [
        f"shift_{j}" for j in range(ORDER)
    ]
    return coordinates + velocities + multipliers


def _zero_matrix(arb_mat: type) -> object:
    return arb_mat(DESCRIPTOR, DESCRIPTOR)


def _linearized_recurrence(
    derivative_hessian: object,
    center_hessian: object,
    expansion_rate: object,
    expansion_rate_derivative: object,
    arb: type,
    arb_mat: type,
) -> object:
    """Differentiate B(H,K) exactly, including explicit H coefficients."""

    result = _zero_matrix(arb_mat)
    for index in range(PHYSICAL):
        result[index, index] = 2 * expansion_rate_derivative
    for row in range(PHYSICAL):
        velocity_row = PHYSICAL + row
        for column in range(PHYSICAL):
            result[velocity_row, column] = -(
                7
                * expansion_rate_derivative
                * center_hessian[velocity_row, column]
                + 7
                * expansion_rate
                * derivative_hessian[velocity_row, column]
                - derivative_hessian[row, column]
            )
            velocity_column = PHYSICAL + column
            result[velocity_row, velocity_column] = -(
                5
                * expansion_rate_derivative
                * center_hessian[velocity_row, velocity_column]
                + 5
                * expansion_rate
                * derivative_hessian[velocity_row, velocity_column]
                + derivative_hessian[velocity_row, column]
                - derivative_hessian[row, velocity_column]
            )
        for column in range(MULTIPLIERS):
            multiplier_column = 2 * PHYSICAL + column
            result[velocity_row, multiplier_column] = -(
                5
                * expansion_rate_derivative
                * center_hessian[velocity_row, multiplier_column]
                + 5
                * expansion_rate
                * derivative_hessian[velocity_row, multiplier_column]
                - derivative_hessian[row, multiplier_column]
            )
    for row in range(MULTIPLIERS):
        multiplier_row = 2 * PHYSICAL + row
        for column in range(DESCRIPTOR):
            result[multiplier_row, column] = derivative_hessian[
                multiplier_row, column
            ]
    return result


def assemble_interval_graph_first_variation(
    *, points: int = 96, decimal_digits: int = 120
) -> dict[str, object]:
    """Certify the complete first graph-defect jet by repeated solves."""

    try:
        from flint import arb, arb_mat, ctx
    except ImportError as error:  # pragma: no cover - optional proof backend
        raise RuntimeError(
            "python-flint==0.9.0 is required for directed certification"
        ) from error

    prior_digits = ctx.dps
    ctx.dps = decimal_digits
    try:
        center = assemble_interval_weight_five_lift(
            points=points, decimal_digits=decimal_digits
        )
        center_matrix = center["matrix"]
        center_hessian = center["action_hessian"]
        expansion_rate = center["expansion_rate"]
        weights = [arb(value).sqrt() for value in squared_product_weights()]
        scaled_center = arb_mat(DESCRIPTOR, DESCRIPTOR, [
            center_matrix[row, column] / (weights[row] * weights[column])
            for row in range(DESCRIPTOR)
            for column in range(DESCRIPTOR)
        ])
        derivative_hessians = [
            _zero_matrix(arb_mat) for _ in range(DESCRIPTOR)
        ]
        pi = arb.pi()
        terms = _local_ordered_third_terms()
        for node_index in range(points):
            node, gauss_weight = arb.legendre_p_root(
                points, node_index, weight=True
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
            sparse, _ = _sparse_maps(x, arb)
            mapping = arb_mat(10, DESCRIPTOR)
            for local_row, entries in enumerate(sparse):
                for column, value in entries.items():
                    mapping[local_row, column] = value
            local_slices = [arb_mat(10, 10) for _ in range(10)]
            for first, second, third, function in terms:
                local_slices[third][first, second] = function(
                    expansion_rate, tangent, cotangent, localization
                )
            mapping_transpose = mapping.transpose()
            common = weight * density
            for direction in range(DESCRIPTOR):
                local_derivative = arb_mat(10, 10)
                for local_direction in range(10):
                    coefficient = (
                        mapping[local_direction, direction]
                        / weights[direction]
                    )
                    if coefficient != 0:
                        local_derivative += coefficient * local_slices[
                            local_direction
                        ]
                derivative_hessians[direction] += common * (
                    mapping_transpose * local_derivative * mapping
                )

        remainder = third_gauss_remainder_bound(points)
        remainder_ball = arb(
            0, f"{remainder.numerator}/{remainder.denominator}"
        )
        for direction in range(DESCRIPTOR):
            for row in range(DESCRIPTOR):
                for column in range(DESCRIPTOR):
                    derivative_hessians[direction][row, column] += (
                        remainder_ball
                    )

        direction_records = []
        stack_frobenius_squared_upper = arb(0)
        all_residuals_contain_zero = True
        labels = descriptor_labels()
        for direction, derivative_hessian in enumerate(derivative_hessians):
            expansion_derivative = (
                1 / weights[direction] if direction == PHYSICAL else arb(0)
            )
            derivative_matrix = _linearized_recurrence(
                derivative_hessian,
                center_hessian,
                expansion_rate,
                expansion_derivative,
                arb,
                arb_mat,
            )
            scaled_derivative = arb_mat(DESCRIPTOR, DESCRIPTOR, [
                derivative_matrix[row, column]
                / (weights[row] * weights[column])
                for row in range(DESCRIPTOR)
                for column in range(DESCRIPTOR)
            ])
            solution = scaled_center.solve(
                scaled_derivative, algorithm="precond"
            )
            residual = scaled_center * solution - scaled_derivative
            residual_ok = all(
                residual[row, column].contains(0)
                for row in range(DESCRIPTOR)
                for column in range(DESCRIPTOR)
            )
            all_residuals_contain_zero &= residual_ok
            frobenius_squared = arb(0)
            for row in range(DESCRIPTOR):
                for column in range(DESCRIPTOR):
                    absolute = abs(solution[row, column])
                    frobenius_squared += absolute * absolute
            frobenius = frobenius_squared.sqrt()
            upper = frobenius.upper()
            stack_frobenius_squared_upper += upper * upper
            direction_records.append({
                "index": direction,
                "label": labels[direction],
                "frobenius_ball": frobenius,
                "frobenius_upper": upper,
                "residual_contains_zero": residual_ok,
            })
        stack_upper = stack_frobenius_squared_upper.sqrt().upper()
        return {
            "points": points,
            "decimal_digits": decimal_digits,
            "nonzero_ordered_local_third_terms": len(terms),
            "nonzero_symmetric_local_third_terms": len({
                tuple(sorted((first, second, third)))
                for first, second, third, _ in terms
            }),
            "third_quadrature_remainder": remainder_ball.rad(),
            "direction_records": direction_records,
            "stack_frobenius_upper": stack_upper,
            "linear_half_contraction_radius_lower": (1 / (2 * stack_upper)).lower(),
            "all_repeated_solve_residuals_contain_zero": (
                all_residuals_contain_zero
            ),
            "explicit_bordered_inverse_formed": False,
            "combined_Euler_Dirac_inverse_used": False,
            "explicit_expansion_rate_coefficient_variation_included": True,
        }
    finally:
        ctx.dps = prior_digits


__all__ = [
    "assemble_interval_graph_first_variation",
    "descriptor_labels",
    "squared_product_weights",
    "third_gauss_remainder_bound",
]
