"""Shared two-body decay and collision readout for BHSM amplitudes.

The formulas are general relativistic phase-space identities.  Masses,
external residues, degeneracy averages, symmetry factors, and amplitudes must
be supplied by the BHSM spectrum/vertex engine; this module does not fit or
identify them.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable

import numpy as np


def kallen(x: float, y: float, z: float) -> float:
    return x * x + y * y + z * z - 2.0 * (x * y + x * z + y * z)


@dataclass(frozen=True)
class TwoBodyDecayResult:
    open_channel: bool
    momentum: float
    width: float


def two_body_decay_width(
    parent_mass: float,
    first_mass: float,
    second_mass: float,
    amplitude_squared: float,
    *,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> TwoBodyDecayResult:
    values = (
        parent_mass, first_mass, second_mass, amplitude_squared,
        initial_state_average, identical_final_state_factor,
    )
    if any(not math.isfinite(value) for value in values):
        raise ValueError("decay inputs must be finite")
    if parent_mass <= 0.0 or min(first_mass, second_mass, amplitude_squared) < 0.0:
        raise ValueError("masses and amplitude squared must be physical")
    if initial_state_average <= 0.0 or identical_final_state_factor <= 0.0:
        raise ValueError("averaging and symmetry factors must be positive")
    if parent_mass < first_mass + second_mass:
        return TwoBodyDecayResult(False, 0.0, 0.0)
    lam = max(0.0, kallen(parent_mass**2, first_mass**2, second_mass**2))
    momentum = math.sqrt(lam) / (2.0 * parent_mass)
    width = (
        momentum * amplitude_squared
        / (8.0 * math.pi * parent_mass**2)
        / initial_state_average
        / identical_final_state_factor
    )
    return TwoBodyDecayResult(True, momentum, width)


@dataclass(frozen=True)
class TwoToTwoResult:
    open_channel: bool
    incoming_momentum: float
    outgoing_momentum: float
    differential_cross_section_domega: float


def two_to_two_differential_cross_section(
    s: float,
    incoming_masses: tuple[float, float],
    outgoing_masses: tuple[float, float],
    amplitude_squared: float,
    *,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> TwoToTwoResult:
    if not all(math.isfinite(value) for value in (
        s, *incoming_masses, *outgoing_masses, amplitude_squared,
        initial_state_average, identical_final_state_factor,
    )):
        raise ValueError("collision inputs must be finite")
    if s <= 0.0 or min(*incoming_masses, *outgoing_masses, amplitude_squared) < 0.0:
        raise ValueError("collision invariants, masses, and amplitude squared must be physical")
    root_s = math.sqrt(s)
    if root_s < sum(incoming_masses) or root_s < sum(outgoing_masses):
        return TwoToTwoResult(False, 0.0, 0.0, 0.0)
    incoming = math.sqrt(max(0.0, kallen(s, incoming_masses[0] ** 2, incoming_masses[1] ** 2))) / (2.0 * root_s)
    outgoing = math.sqrt(max(0.0, kallen(s, outgoing_masses[0] ** 2, outgoing_masses[1] ** 2))) / (2.0 * root_s)
    if incoming == 0.0:
        return TwoToTwoResult(False, incoming, outgoing, 0.0)
    differential = (
        amplitude_squared
        * outgoing / incoming
        / (64.0 * math.pi**2 * s)
        / initial_state_average
        / identical_final_state_factor
    )
    return TwoToTwoResult(True, incoming, outgoing, differential)


@dataclass(frozen=True)
class DecayLedgerResult:
    total_width: float
    inverse_width_lifetime: float
    branching_fractions: dict[str, float]


def combine_decay_channels(
    channels: Iterable[tuple[str, TwoBodyDecayResult]],
) -> DecayLedgerResult:
    """Combine a complete list of action-derived partial widths.

    The lifetime is returned in inverse units of the supplied width.  A
    seconds conversion belongs after the universal BHSM scale and physical
    unit convention are fixed.
    """

    entries = tuple(channels)
    names = [name for name, _ in entries]
    if len(names) != len(set(names)):
        raise ValueError("duplicate decay-channel id")
    widths = {name: result.width for name, result in entries}
    if any(not math.isfinite(width) or width < 0.0 for width in widths.values()):
        raise ValueError("partial widths must be finite and nonnegative")
    total = math.fsum(widths.values())
    branching = (
        {name: width / total for name, width in widths.items()}
        if total > 0.0
        else {name: 0.0 for name in widths}
    )
    return DecayLedgerResult(
        total_width=total,
        inverse_width_lifetime=math.inf if total == 0.0 else 1.0 / total,
        branching_fractions=branching,
    )


@dataclass(frozen=True)
class IntegratedTwoToTwoResult:
    open_channel: bool
    total_cross_section: float
    quadrature_order: int
    minimum_amplitude_squared: float
    maximum_amplitude_squared: float


def integrate_two_to_two_cross_section(
    s: float,
    incoming_masses: tuple[float, float],
    outgoing_masses: tuple[float, float],
    amplitude_squared: Callable[[float], float],
    *,
    quadrature_order: int = 32,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> IntegratedTwoToTwoResult:
    """Integrate an azimuth-symmetric ``2->2`` BHSM amplitude over angle."""

    if quadrature_order < 2:
        raise ValueError("quadrature order must be at least two")
    root_s = math.sqrt(s) if s > 0.0 else 0.0
    if root_s < sum(incoming_masses) or root_s < sum(outgoing_masses):
        return IntegratedTwoToTwoResult(False, 0.0, quadrature_order, 0.0, 0.0)
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    amplitudes = np.asarray([float(amplitude_squared(float(node))) for node in nodes])
    if not np.all(np.isfinite(amplitudes)) or np.min(amplitudes) < 0.0:
        raise ValueError("amplitude-squared function must be finite and nonnegative")
    differential = np.asarray([
        two_to_two_differential_cross_section(
            s,
            incoming_masses,
            outgoing_masses,
            value,
            initial_state_average=initial_state_average,
            identical_final_state_factor=identical_final_state_factor,
        ).differential_cross_section_domega
        for value in amplitudes
    ])
    # dOmega = dphi d(cos(theta)); azimuth symmetry supplies 2*pi.
    total = float(2.0 * math.pi * np.dot(weights, differential))
    return IntegratedTwoToTwoResult(
        open_channel=True,
        total_cross_section=total,
        quadrature_order=quadrature_order,
        minimum_amplitude_squared=float(np.min(amplitudes)),
        maximum_amplitude_squared=float(np.max(amplitudes)),
    )


__all__ = [
    "DecayLedgerResult",
    "IntegratedTwoToTwoResult",
    "TwoBodyDecayResult",
    "TwoToTwoResult",
    "combine_decay_channels",
    "integrate_two_to_two_cross_section",
    "kallen",
    "two_body_decay_width",
    "two_to_two_differential_cross_section",
]
