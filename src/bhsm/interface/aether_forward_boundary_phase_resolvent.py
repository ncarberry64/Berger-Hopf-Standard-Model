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


__all__ = [
    "cayley_phase",
    "half_line_reflection_coefficient",
    "compact_indicator_resolvent_difference",
    "compact_indicator_neumann_to_robin_difference",
    "phase_distance",
    "phase_angle",
]
