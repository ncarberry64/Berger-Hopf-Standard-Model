"""Certified mode, decay-channel, and stability classification.

The records contain only action-derived intervals and labels.  Experimental
particle names and measured masses are comparison-layer data and are not
accepted by this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, order=True)
class CertifiedInterval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    def contains_zero(self) -> bool:
        return self.lower <= 0.0 <= self.upper

    def is_exact_zero(self) -> bool:
        return self.lower == 0.0 and self.upper == 0.0


@dataclass(frozen=True)
class SpectralMode:
    mode_id: str
    mass: CertifiedInterval
    spin_twice: int
    electric_charge: CertifiedInterval
    color_representation: str
    weak_representation: str
    action_version: str
    domain_id: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.mass.lower < 0.0:
            raise ValueError("mass interval must be nonnegative")
        if self.spin_twice < 0:
            raise ValueError("twice-spin must be nonnegative")


@dataclass(frozen=True)
class DecayChannelInterval:
    parent_mode_id: str
    daughter_mode_ids: tuple[str, ...]
    amplitude_squared: CertifiedInterval
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.amplitude_squared.lower < 0.0:
            raise ValueError("amplitude-squared interval must be nonnegative")


def decay_channel_status(
    channel: DecayChannelInterval,
    modes: dict[str, SpectralMode],
) -> str:
    parent = modes[channel.parent_mode_id]
    daughters = [modes[mode_id] for mode_id in channel.daughter_mode_ids]
    threshold_lower = sum(mode.mass.lower for mode in daughters)
    threshold_upper = sum(mode.mass.upper for mode in daughters)
    if parent.mass.upper < threshold_lower:
        kinematics = "CLOSED"
    elif parent.mass.lower > threshold_upper:
        kinematics = "OPEN"
    else:
        kinematics = "UNRESOLVED"
    if channel.amplitude_squared.is_exact_zero():
        coupling = "FORBIDDEN_EXACT_ZERO"
    elif channel.amplitude_squared.lower > 0.0:
        coupling = "NONZERO"
    else:
        coupling = "UNRESOLVED"
    return f"{kinematics}_{coupling}"


def classify_mode_stability(
    parent_mode_id: str,
    modes: Iterable[SpectralMode],
    channels: Iterable[DecayChannelInterval],
    *,
    complete_channel_ledger: bool,
) -> dict:
    mode_map = {mode.mode_id: mode for mode in modes}
    if parent_mode_id not in mode_map:
        raise KeyError(parent_mode_id)
    relevant = [channel for channel in channels if channel.parent_mode_id == parent_mode_id]
    statuses = [decay_channel_status(channel, mode_map) for channel in relevant]
    if any(status == "OPEN_NONZERO" for status in statuses):
        verdict = "CERTIFIED_UNSTABLE_HAS_OPEN_NONZERO_CHANNEL"
    elif complete_channel_ledger and all(
        status.startswith("CLOSED_") or status.endswith("FORBIDDEN_EXACT_ZERO")
        for status in statuses
    ):
        verdict = "CERTIFIED_STABLE_ON_COMPLETE_CHANNEL_LEDGER"
    else:
        verdict = "STABILITY_UNRESOLVED"
    return {
        "parent_mode_id": parent_mode_id,
        "verdict": verdict,
        "complete_channel_ledger": bool(complete_channel_ledger),
        "channel_statuses": statuses,
        "experimental_particle_assignment_used": False,
    }


def spectral_exclusion(
    modes: Iterable[SpectralMode],
    mass_window: CertifiedInterval,
    *,
    color_representation: str | None = None,
    electric_charge: CertifiedInterval | None = None,
) -> dict:
    selected = []
    for mode in modes:
        if color_representation is not None and mode.color_representation != color_representation:
            continue
        if electric_charge is not None and (
            mode.electric_charge.upper < electric_charge.lower
            or electric_charge.upper < mode.electric_charge.lower
        ):
            continue
        if not (mode.mass.upper < mass_window.lower or mass_window.upper < mode.mass.lower):
            selected.append(mode.mode_id)
    return {
        "mass_window": [mass_window.lower, mass_window.upper],
        "matching_mode_ids": selected,
        "spectrum_excluded_on_declared_domain": len(selected) == 0,
        "experimental_search_result_used": False,
    }


__all__ = [
    "CertifiedInterval",
    "DecayChannelInterval",
    "SpectralMode",
    "classify_mode_stability",
    "decay_channel_status",
    "spectral_exclusion",
]
