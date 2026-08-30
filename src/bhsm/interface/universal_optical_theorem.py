"""Forward-amplitude optical-theorem reconciliation for BHSM channels.

With the invariant amplitude convention used by the universal phase-space
engine, unitarity gives

    sigma_total(s) = Im M_forward(s, t=0) / sqrt(lambda(s,m1^2,m2^2)).

The forward amplitude and every inclusive channel contribution must come from
the same action, background, LSZ convention, and channel ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from bhsm.interface.universal_decay_collision import kallen


@dataclass(frozen=True)
class OpticalTheoremReport:
    forward_amplitude: complex
    optical_total_cross_section: float
    inclusive_ledger_cross_section: float
    relative_equality_residual: float
    incomplete_ledger_excess: float
    complete_channel_ledger: bool
    absorptive_part_nonnegative: bool
    channel_ids: tuple[str, ...]
    gate7_closed: bool
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def require_consistency(self, tolerance: float = 1.0e-10) -> None:
        blockers: list[str] = []
        if not self.absorptive_part_nonnegative:
            blockers.append("nonnegative_forward_absorptive_part")
        if self.complete_channel_ledger:
            if self.relative_equality_residual > tolerance:
                blockers.append("complete_optical_theorem_equality")
        elif self.incomplete_ledger_excess > tolerance:
            blockers.append("incomplete_ledger_cannot_exceed_optical_total")
        if blockers:
            raise RuntimeError("optical-theorem consistency blocked by: " + ", ".join(blockers))

    def require_physical_promotion(self, tolerance: float = 1.0e-10) -> None:
        self.require_consistency(tolerance)
        blockers: list[str] = []
        if not self.gate7_closed:
            blockers.append("Gate7_closed_background")
        if not self.complete_channel_ledger:
            blockers.append("complete_inclusive_channel_ledger")
        if blockers:
            raise RuntimeError("optical-theorem promotion blocked by: " + ", ".join(blockers))


def reconcile_optical_theorem(
    s: float,
    incoming_masses: tuple[float, float],
    forward_amplitude: complex,
    inclusive_channel_cross_sections: Iterable[tuple[str, float]],
    *,
    complete_channel_ledger: bool,
    gate7_closed: bool,
    action_version: str,
    background_id: str,
    provenance: tuple[str, ...],
) -> OpticalTheoremReport:
    """Compare the forward absorptive part with an inclusive channel ledger."""

    amplitude = complex(forward_amplitude)
    entries = tuple((str(channel_id), float(value)) for channel_id, value in inclusive_channel_cross_sections)
    if not math.isfinite(s) or s <= 0.0 or any(
        not math.isfinite(mass) or mass < 0.0 for mass in incoming_masses
    ):
        raise ValueError("optical-theorem kinematics must be finite and physical")
    if not np.isfinite(amplitude):
        raise ValueError("forward amplitude must be finite")
    if not entries:
        raise ValueError("inclusive channel ledger must be nonempty")
    channel_ids = tuple(channel_id for channel_id, _value in entries)
    if any(not channel_id for channel_id in channel_ids) or len(channel_ids) != len(set(channel_ids)):
        raise ValueError("inclusive channel ids must be nonempty and unique")
    if any(not math.isfinite(value) or value < 0.0 for _channel_id, value in entries):
        raise ValueError("inclusive channel cross sections must be finite and nonnegative")
    if not action_version or not background_id or not provenance:
        raise ValueError("optical-theorem action/background provenance is required")

    flux_squared = kallen(s, incoming_masses[0] ** 2, incoming_masses[1] ** 2)
    if flux_squared <= 0.0:
        raise ValueError("optical theorem requires a strictly open incoming channel")
    invariant_flux = math.sqrt(flux_squared)
    optical = float(amplitude.imag / invariant_flux)
    inclusive = math.fsum(value for _channel_id, value in entries)
    scale = max(abs(optical), inclusive, np.finfo(float).tiny)
    relative = abs(inclusive - optical) / scale
    excess = max(0.0, inclusive - max(0.0, optical)) / scale
    return OpticalTheoremReport(
        forward_amplitude=amplitude,
        optical_total_cross_section=optical,
        inclusive_ledger_cross_section=inclusive,
        relative_equality_residual=relative,
        incomplete_ledger_excess=excess,
        complete_channel_ledger=bool(complete_channel_ledger),
        absorptive_part_nonnegative=optical >= 0.0,
        channel_ids=channel_ids,
        gate7_closed=bool(gate7_closed),
        action_version=action_version,
        background_id=background_id,
        provenance=provenance,
    )


__all__ = ["OpticalTheoremReport", "reconcile_optical_theorem"]
