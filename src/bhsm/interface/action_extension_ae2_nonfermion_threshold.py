"""AE2 zero-threshold margins for the retained nonfermionic source blocks."""

from __future__ import annotations

import math


def _nonnegative(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"finite nonnegative {name} required")
    return number


def seam_wronskian_lower(
    event_dtn_lower: float,
    child_dtn_lower: float,
    wentzell_lower: float = 0.0,
) -> float:
    """Return the quadratic-form lower bound for a two-sided AE2 seam.

    With outward conormals, the zero-energy seam operator is
    ``M_event + U_R^* M_child U_R + W``.  Unitary conjugation preserves the
    child lower bound, so nonnegative arm forms and a nonnegative Wentzell
    block add without a sign loss.
    """

    return sum(
        (
            _nonnegative(event_dtn_lower, "event DtN lower"),
            _nonnegative(child_dtn_lower, "child DtN lower"),
            _nonnegative(wentzell_lower, "Wentzell lower"),
        )
    )


def transverse_gauge_wentzell_lower(
    five_dimensional_coefficient: float,
    group_ray_coefficient: float,
    coexact_unit_eigenvalue: float,
    radius_upper: float,
) -> float:
    """Return the retained transverse-gauge Wentzell eigenvalue lower.

    ``W=K_F*c_group*sqrt(Delta_1^coexact)`` and spatial eigenvalues scale as
    ``R4^-2``.  Hence the square-root block scales as ``R4^-1``.
    """

    coefficient = _nonnegative(
        five_dimensional_coefficient, "five-dimensional coefficient"
    )
    group = _nonnegative(group_ray_coefficient, "group-ray coefficient")
    eigenvalue = _nonnegative(coexact_unit_eigenvalue, "coexact eigenvalue")
    radius = _nonnegative(radius_upper, "radius upper")
    if coefficient == 0.0 or group == 0.0 or eigenvalue == 0.0 or radius == 0.0:
        raise ValueError("strictly positive gauge Wentzell inputs required")
    return coefficient * group * math.sqrt(eigenvalue) / radius


__all__ = ["seam_wronskian_lower", "transverse_gauge_wentzell_lower"]
