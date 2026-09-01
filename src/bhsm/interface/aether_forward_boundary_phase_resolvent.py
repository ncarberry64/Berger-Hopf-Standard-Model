"""Exact resolvent separation for an unselected boundary phase.

The formulas give a local scalar representative of the maximal-isotropic
Cayley family retained by the BHSM matter-boundary audit.  They are used only
to prove that self-adjointness and nonnegativity do not make the resolvent
independent of the missing normal boundary generator.
"""

from __future__ import annotations

import cmath
import math


def _nonnegative(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"finite nonnegative {name} required")
    return number


def _positive(value: float, name: str) -> float:
    number = _nonnegative(value, name)
    if number == 0.0:
        raise ValueError(f"positive {name} required")
    return number


def cayley_phase(robin_parameter: float) -> complex:
    """Return the scalar maximal-isotropic Cayley phase.

    The convention agrees with the retained v15.12/v15.13 trace family,
    ``U_h=(1-i*h)/(1+i*h)``.
    """

    h = _nonnegative(robin_parameter, "Robin parameter")
    return (1.0 - 1.0j * h) / (1.0 + 1.0j * h)


def half_line_reflection_coefficient(
    decay_rate: float,
    robin_parameter: float,
) -> float:
    """Return the negative-energy reflection coefficient.

    For ``K_h=-d2/dx2+m2`` on the half-line with ``u'(0)=h*u(0)`` and
    ``kappa=sqrt(m2-z)>0``, the resolvent kernel is

    ``G_h=(exp(-kappa*|x-y|)+r_h*exp(-kappa*(x+y)))/(2*kappa)``.
    """

    kappa = _positive(decay_rate, "decay rate")
    h = _nonnegative(robin_parameter, "Robin parameter")
    return (kappa - h) / (kappa + h)


def compact_indicator_resolvent_difference(
    decay_rate: float,
    support_length: float,
    reference_robin: float,
    comparison_robin: float,
) -> float:
    """Return the exact compact-source resolvent contraction difference.

    The supplied source is ``f=1_[0,L]``.  The result is

    ``<f,(R_h1-R_h0)f>``
    ``=(r_h1-r_h0)*(1-exp(-kappa*L))**2/(2*kappa**3)``.
    """

    kappa = _positive(decay_rate, "decay rate")
    length = _positive(support_length, "support length")
    r0 = half_line_reflection_coefficient(kappa, reference_robin)
    r1 = half_line_reflection_coefficient(kappa, comparison_robin)
    integral = -math.expm1(-kappa * length) / kappa
    return (r1 - r0) * integral * integral / (2.0 * kappa)


def compact_indicator_neumann_to_robin_difference(
    decay_rate: float,
    support_length: float,
    robin_parameter: float,
) -> float:
    """Specialize the compact-source difference from Neumann to Robin."""

    kappa = _positive(decay_rate, "decay rate")
    length = _positive(support_length, "support length")
    h = _positive(robin_parameter, "Robin parameter")
    numerator = h * (-math.expm1(-kappa * length)) ** 2
    return -numerator / (kappa**3 * (kappa + h))


def phase_distance(first_robin: float, second_robin: float) -> float:
    """Return the chordal distance between two retained Cayley phases."""

    first = cayley_phase(first_robin)
    second = cayley_phase(second_robin)
    return abs(first - second)


def phase_angle(robin_parameter: float) -> float:
    """Return the principal argument of the retained Cayley phase."""

    return cmath.phase(cayley_phase(robin_parameter))


def robin_neumann_relative_heat_trace(
    heat_time: float,
    robin_parameter: float,
) -> float:
    """Return the half-line Robin-minus-Neumann relative heat trace.

    For finite ``x=h*sqrt(t)`` the exact value is
    ``(exp(x**2)*erfc(x)-1)/2``.  The audit uses ``x=1``; the conservative
    range guard avoids an overflow-prone representation at very large ``x``.
    """

    time = _positive(heat_time, "heat time")
    h = _nonnegative(robin_parameter, "Robin parameter")
    x = h * math.sqrt(time)
    if x > 25.0:
        raise ValueError("scaled Robin heat argument exceeds stable range")
    return 0.5 * (math.exp(x * x) * math.erfc(x) - 1.0)


def _gaussian_second_moment_tail(lower: float, scale: float) -> float:
    """Return ``integral_lower^infinity x^2 exp(-scale*x^2) dx``."""

    point = _positive(lower, "Gaussian tail lower endpoint")
    a = _positive(scale, "Gaussian scale")
    return (
        point * math.exp(-a * point * point) / (2.0 * a)
        + math.sqrt(math.pi) * math.erfc(math.sqrt(a) * point)
        / (4.0 * a**1.5)
    )


def hs_weyl_spatial_supertrace_enclosure(
    dimensionless_heat_time: float,
    cutoff: int = 20,
) -> dict[str, float]:
    """Enclose the retained four-HS minus 48-Weyl spatial heat trace.

    The exact series is
    ``4 sum_(m>=1)m^2 exp(-a*m^2)``
    ``-48 sum_(n>=0)(n+1)(n+2) exp(-a*(n+3/2)^2)``.
    For a decreasing tail, the integral test gives the stated absolute
    remainder bound.  ``cutoff>=max(2,ceil(1/sqrt(a)))`` enforces that regime.
    """

    a = _positive(dimensionless_heat_time, "dimensionless heat time")
    if not isinstance(cutoff, int) or cutoff < max(2, math.ceil(1.0 / math.sqrt(a))):
        raise ValueError("cutoff must reach the decreasing Gaussian tail")
    hs_partial = 4.0 * sum(
        m * m * math.exp(-a * m * m) for m in range(1, cutoff + 1)
    )
    weyl_partial = -48.0 * sum(
        (n + 1) * (n + 2) * math.exp(-a * (n + 1.5) ** 2)
        for n in range(cutoff + 1)
    )
    hs_tail = 4.0 * _gaussian_second_moment_tail(float(cutoff), a)
    # (n+1)(n+2)=(n+3/2)^2-1/4 <= (n+3/2)^2.
    weyl_tail = 48.0 * _gaussian_second_moment_tail(cutoff + 1.5, a)
    partial = hs_partial + weyl_partial
    remainder = hs_tail + weyl_tail
    return {
        "HS_partial": hs_partial,
        "Weyl_partial": weyl_partial,
        "graded_partial": partial,
        "absolute_tail_upper": remainder,
        "graded_lower": partial - remainder,
        "graded_upper": partial + remainder,
    }


__all__ = [
    "cayley_phase",
    "half_line_reflection_coefficient",
    "compact_indicator_resolvent_difference",
    "compact_indicator_neumann_to_robin_difference",
    "phase_distance",
    "phase_angle",
    "robin_neumann_relative_heat_trace",
    "hs_weyl_spatial_supertrace_enclosure",
]
