"""Threshold identities for compactly supported forward source variations."""

from __future__ import annotations

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


def scalar_core_zero_energy_impedance_lower(
    proper_duration_lower: float,
    radius_upper: float,
    unit_radius_eigenvalue: float,
) -> float:
    """Return the certified child-side zero-energy impedance margin.

    On the known core, ``V=c/R4**2 >= c/Rmax**2``.  Sturm comparison with
    the constant lower potential and a nonnegative inward graph at the far
    end gives ``M_child(0) >= a*tanh(a*T)``, where ``a=sqrt(c)/Rmax``.
    The constant channel has margin zero.
    """

    duration = _positive(proper_duration_lower, "proper duration")
    maximum_radius = _positive(radius_upper, "radius upper bound")
    eigenvalue = _nonnegative(unit_radius_eigenvalue, "spatial eigenvalue")
    if eigenvalue == 0.0:
        return 0.0
    rate = math.sqrt(eigenvalue) / maximum_radius
    return rate * math.tanh(rate * duration)


def free_robin_compact_counting_bound(
    robin_margin: float,
    support_length: float,
    source_l1_norm: float,
    spectral_ceiling: float,
) -> dict[str, float]:
    """Bound a compact multiplication source in the free Robin model.

    For ``-d2/dx2`` on the half-line with ``u'(0)=h*u(0)``, ``h>0``, the
    normalized generalized eigenfunction is

    ``sqrt(2/pi)*(k*cos(kx)+h*sin(kx))/sqrt(k**2+h**2)``.

    If the absolute source is supported in ``[0,L]``, its spectral counting
    contraction through ``Lambda`` is at most ``C*Lambda**(3/2)``.  This is
    a comparison theorem for the regular free threshold class, not an
    assertion that the unknown N12 exterior is free.
    """

    h = _positive(robin_margin, "Robin margin")
    length = _nonnegative(support_length, "support length")
    source = _nonnegative(source_l1_norm, "source L1 norm")
    ceiling = _nonnegative(spectral_ceiling, "spectral ceiling")
    coefficient = (
        2.0
        * source
        * ((1.0 + h * length) / h) ** 2
        / (3.0 * math.pi)
    )
    return {
        "excess_exponent": 0.5,
        "counting_coefficient": coefficient,
        "counting_upper": coefficient * ceiling**1.5,
    }


def free_neumann_compact_counting_leading_coefficient(
    support_length: float,
    constant_source_density: float = 1.0,
) -> float:
    """Return the exact leading ``sqrt(Lambda)`` coefficient for Neumann.

    The source is the constant density ``q`` on ``[0,L]``.  Since the
    generalized eigenfunctions are ``sqrt(2/pi)*cos(kx)``, the localized
    counting contraction is asymptotic to ``(2*q*L/pi)*sqrt(Lambda)``.
    """

    length = _nonnegative(support_length, "support length")
    density = _nonnegative(constant_source_density, "source density")
    return 2.0 * density * length / math.pi


def factorized_first_form_bound(
    factor_image_norm: float,
    varied_factor_image_norm: float,
) -> float:
    """Bound the first form jet of ``P=A* A`` on one state.

    ``D q[u]=2 Re <A u,A_h u>``.  In particular every exact kernel vector
    has exactly zero first geometry weight on a fixed form domain.
    """

    factor = _nonnegative(factor_image_norm, "factor image norm")
    varied = _nonnegative(
        varied_factor_image_norm, "varied factor image norm"
    )
    return 2.0 * factor * varied


def constant_superpotential_zero_mode_witness(
    superpotential: float,
) -> dict[str, float]:
    """Return the normalized half-line kernel witness for ``A=d/dx+s``."""

    value = _positive(superpotential, "superpotential")
    amplitude = math.sqrt(2.0 * value)
    return {
        "normalization_amplitude": amplitude,
        "L2_norm_squared": 1.0,
        "factor_image_norm": 0.0,
        "birth_conormal": 0.0,
        "first_form_weight": factorized_first_form_bound(0.0, amplitude),
    }


__all__ = [
    "scalar_core_zero_energy_impedance_lower",
    "free_robin_compact_counting_bound",
    "free_neumann_compact_counting_leading_coefficient",
    "factorized_first_form_bound",
    "constant_superpotential_zero_mode_witness",
]
