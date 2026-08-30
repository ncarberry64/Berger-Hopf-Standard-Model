"""Shared two-body decay and collision readout for BHSM amplitudes.

The formulas are general relativistic phase-space identities.  Masses,
external residues, degeneracy averages, symmetry factors, and amplitudes must
be supplied by the BHSM spectrum/vertex engine; this module does not fit or
identify them.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


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


__all__ = [
    "TwoBodyDecayResult",
    "TwoToTwoResult",
    "kallen",
    "two_body_decay_width",
    "two_to_two_differential_cross_section",
]
