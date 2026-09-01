"""Prove the stored DOP853 descriptor center has one descending first hit.

Every input binary64 coefficient is converted to an exact rational number.
Bernstein subdivision then certifies positivity of every complete preterminal
segment and negativity of the derivative on the terminal segment.  This is
an exact statement about the stored polynomial center, not yet about the
nearby retained-action orbit supplied by the shadowing theorem.
"""

from __future__ import annotations

from fractions import Fraction
import json
import math
import os
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER_DATA = Path(os.environ.get(
    "BHSM_N12_STOP_CENTER_DATA",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_HALF_STEP_CENTER_RECONNAISSANCE.npz"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_FIRST_HIT_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_DENSE_DESCRIPTOR_FIRST_HIT.json"),
))


def _constant(value: float) -> list[Fraction]:
    return [Fraction.from_float(float(value))]


def _add_constant(poly: list[Fraction], value: float) -> list[Fraction]:
    result = poly.copy()
    result[0] += Fraction.from_float(float(value))
    return result


def _multiply_x(poly: list[Fraction]) -> list[Fraction]:
    return [Fraction(0), *poly]


def _multiply_one_minus_x(poly: list[Fraction]) -> list[Fraction]:
    result = poly + [Fraction(0)]
    for index, coefficient in enumerate(poly):
        result[index + 1] -= coefficient
    return result


def _dense_power(left: float, coefficients: np.ndarray) -> list[Fraction]:
    poly = _constant(0.0)
    for index, coefficient in enumerate(reversed(coefficients)):
        poly = _add_constant(poly, float(coefficient))
        poly = _multiply_x(poly) if index % 2 == 0 else _multiply_one_minus_x(poly)
    return _add_constant(poly, left)


def _derivative(poly: list[Fraction]) -> list[Fraction]:
    return [Fraction(index) * poly[index] for index in range(1, len(poly))]


def _compose_interval(
    poly: list[Fraction], left: Fraction, right: Fraction,
) -> list[Fraction]:
    """Power coefficients of p(left+(right-left)u)."""
    degree = len(poly) - 1
    width = right - left
    result = [Fraction(0) for _ in range(degree + 1)]
    for power, coefficient in enumerate(poly):
        for index in range(power + 1):
            result[index] += (
                coefficient * math.comb(power, index)
                * left ** (power - index) * width ** index
            )
    return result


def _bernstein(poly: list[Fraction]) -> list[Fraction]:
    degree = len(poly) - 1
    return [
        sum(
            poly[j] * Fraction(math.comb(k, j), math.comb(degree, j))
            for j in range(k + 1)
        )
        for k in range(degree + 1)
    ]


def _range_certificate(
    poly: list[Fraction], left: Fraction, right: Fraction, *,
    want_positive: bool, depth: int = 0, max_depth: int = 24,
) -> tuple[bool, Fraction, Fraction, int, int]:
    coefficients = _bernstein(_compose_interval(poly, left, right))
    lower, upper = min(coefficients), max(coefficients)
    success = lower > 0 if want_positive else upper < 0
    if success:
        return True, lower, upper, depth, 1
    if depth >= max_depth:
        return False, lower, upper, depth, 1
    middle = (left + right) / 2
    a = _range_certificate(
        poly, left, middle, want_positive=want_positive,
        depth=depth + 1, max_depth=max_depth,
    )
    b = _range_certificate(
        poly, middle, right, want_positive=want_positive,
        depth=depth + 1, max_depth=max_depth,
    )
    return (
        a[0] and b[0], min(a[1], b[1]), max(a[2], b[2]),
        max(a[3], b[3]), a[4] + b[4],
    )


def _evaluate(poly: list[Fraction], x: Fraction) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(poly):
        value = value * x + coefficient
    return value


def main() -> None:
    with np.load(CENTER_DATA) as source:
        values = np.asarray(source["fine_grid_augmented_action_values"], dtype=float)
        coefficients = np.asarray(source["fine_grid_DOP853_dense_coefficients"], dtype=float)
        bracket = int(source["stop_bracket_fine_grid_index"][0])
        stop_fraction_float = float(source["stop_dense_fraction"][0])
        fixed_step = float(
            source["fine_grid_action_lengths"][1]
            - source["fine_grid_action_lengths"][0]
        )

    preterminal = []
    global_lower: Fraction | None = None
    maximum_depth = 0
    leaves = 0
    for interval in range(bracket):
        poly = _dense_power(values[interval, -1], coefficients[interval, :, -1])
        certificate = _range_certificate(
            poly, Fraction(0), Fraction(1), want_positive=True,
        )
        preterminal.append(certificate[0])
        global_lower = (
            certificate[1] if global_lower is None
            else min(global_lower, certificate[1])
        )
        maximum_depth = max(maximum_depth, certificate[3])
        leaves += certificate[4]

    terminal = _dense_power(
        values[bracket, -1], coefficients[bracket, :, -1],
    )
    terminal_derivative = _derivative(terminal)
    derivative_certificate = _range_certificate(
        terminal_derivative, Fraction(0), Fraction(1), want_positive=False,
    )
    # Re-bracket the polynomial with exact rational arithmetic.  This avoids
    # cancellation in the floating dense evaluator near its 1e-25 zero.
    root_left, root_right = Fraction(0), Fraction(1)
    if not (_evaluate(terminal, root_left) > 0 > _evaluate(terminal, root_right)):
        raise RuntimeError("terminal dense polynomial does not bracket a zero")
    for _ in range(100):
        middle = (root_left + root_right) / 2
        if _evaluate(terminal, middle) > 0:
            root_left = middle
        else:
            root_right = middle
    left_value = _evaluate(terminal, root_left)
    right_value = _evaluate(terminal, root_right)
    terminal_before = _range_certificate(
        terminal, Fraction(0), root_left, want_positive=True,
    )
    terminal_bracketed = left_value > 0 and right_value < 0

    validation = {
        "all_complete_preterminal_polynomials_strictly_positive": all(preterminal),
        "terminal_polynomial_strictly_positive_before_root_bracket": terminal_before[0],
        "terminal_polynomial_derivative_strictly_negative": derivative_certificate[0],
        "terminal_zero_bracket_has_positive_left_and_negative_right": terminal_bracketed,
        "stored_center_only_not_exact_retained_history": True,
        "shadowing_radius_and_domain_margin_transfer_remain_required": True,
    }
    payload = {
        "artifact": "BHSM_N12_C2_STOP_DENSE_DESCRIPTOR_FIRST_HIT",
        "authority": "EXACT_RATIONAL_REPLAY_OF_STORED_BINARY64_CENTER_POLYNOMIALS",
        "center": CENTER_DATA.relative_to(ROOT).as_posix(),
        "summary": {
            "fixed_action_step": fixed_step,
            "complete_preterminal_intervals": bracket,
            "minimum_preterminal_Bernstein_lower": float(global_lower),
            "terminal_stop_fraction": stop_fraction_float,
            "terminal_root_bracket_fraction_width": float(root_right - root_left),
            "exact_rational_root_fraction_midpoint": float((root_left + root_right) / 2),
            "stored_minus_exact_root_fraction": float(
                Fraction.from_float(stop_fraction_float)
                - (root_left + root_right) / 2
            ),
            "terminal_root_bracket_left_value": float(left_value),
            "terminal_root_bracket_right_value": float(right_value),
            "terminal_derivative_Bernstein_upper": float(derivative_certificate[2]),
            "maximum_subdivision_depth": max(maximum_depth, terminal_before[3], derivative_certificate[3]),
            "total_Bernstein_leaves": leaves + terminal_before[4] + derivative_certificate[4],
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "stored_center_first_hit": all(validation.values()),
            "exact_history_first_hit": "OPEN_UNTIL_CORRELATED_SHADOWING_AND_MARGIN_TRANSFER",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
