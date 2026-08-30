"""Lorentz-kinematic event observables for BHSM collision predictions.

The input four-momenta and visibility classification must be supplied by the
action-derived channel/event generator.  This module applies only exact
kinematic identities; it contains no detector response, fitted cut, parton
distribution, or experimental particle assignment.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class FourMomentum:
    energy: float
    px: float
    py: float
    pz: float

    def __post_init__(self) -> None:
        values = (self.energy, self.px, self.py, self.pz)
        if any(not math.isfinite(value) for value in values):
            raise ValueError("four-momentum components must be finite")
        if self.energy < 0.0:
            raise ValueError("physical four-momentum energy must be nonnegative")

    @property
    def spatial_squared(self) -> float:
        return self.px**2 + self.py**2 + self.pz**2

    @property
    def mass_squared(self) -> float:
        return self.energy**2 - self.spatial_squared

    @property
    def transverse_momentum(self) -> float:
        return math.hypot(self.px, self.py)

    @property
    def transverse_energy(self) -> float:
        return math.sqrt(max(0.0, self.mass_squared) + self.transverse_momentum**2)

    @property
    def azimuth(self) -> float:
        return math.atan2(self.py, self.px)

    @property
    def rapidity(self) -> float:
        plus = self.energy + self.pz
        minus = self.energy - self.pz
        if plus <= 0.0 or minus <= 0.0:
            raise ValueError("rapidity is not finite for this four-momentum")
        return 0.5 * math.log(plus / minus)

    def require_nonspacelike(self, tolerance: float = 1.0e-10) -> None:
        scale = max(self.energy**2, self.spatial_squared, 1.0)
        if self.mass_squared < -tolerance * scale:
            raise ValueError("external four-momentum must be timelike or null")

    def __add__(self, other: "FourMomentum") -> "FourMomentum":
        return FourMomentum(
            self.energy + other.energy,
            self.px + other.px,
            self.py + other.py,
            self.pz + other.pz,
        )


@dataclass(frozen=True)
class FinalStateMomentum:
    state_id: str
    mode_id: str
    momentum: FourMomentum
    visible: bool

    def __post_init__(self) -> None:
        if not self.state_id or not self.mode_id:
            raise ValueError("final-state and mode ids are required")


@dataclass(frozen=True)
class EventObservableResult:
    initial_invariant_mass: float
    final_invariant_mass: float
    scalar_visible_ht: float
    missing_transverse_px: float
    missing_transverse_py: float
    missing_transverse_momentum: float
    pairwise_invariant_masses: dict[str, float]
    pairwise_delta_r_y: dict[str, float]
    four_momentum_conservation_relative_residual: float
    final_state_ids: tuple[str, ...]
    visible_state_ids: tuple[str, ...]
    complete_final_state_ledger: bool
    gate7_closed: bool
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def require_physical_promotion(self, tolerance: float = 1.0e-10) -> None:
        blockers: list[str] = []
        if not self.gate7_closed:
            blockers.append("Gate7_closed_background")
        if not self.complete_final_state_ledger:
            blockers.append("complete_action_derived_final_state_ledger")
        if self.four_momentum_conservation_relative_residual > tolerance:
            blockers.append("four_momentum_conservation")
        if blockers:
            raise RuntimeError("event-observable promotion blocked by: " + ", ".join(blockers))


def _sum_momenta(momenta: Iterable[FourMomentum]) -> FourMomentum:
    total = FourMomentum(0.0, 0.0, 0.0, 0.0)
    for momentum in momenta:
        total = total + momentum
    return total


def _invariant_mass(momentum: FourMomentum, tolerance: float = 1.0e-10) -> float:
    momentum.require_nonspacelike(tolerance)
    return math.sqrt(max(0.0, momentum.mass_squared))


def _delta_phi(first: float, second: float) -> float:
    return abs((first - second + math.pi) % (2.0 * math.pi) - math.pi)


def build_event_observables(
    incoming_momenta: Iterable[FourMomentum],
    final_states: Iterable[FinalStateMomentum],
    *,
    complete_final_state_ledger: bool,
    gate7_closed: bool,
    action_version: str,
    background_id: str,
    provenance: tuple[str, ...],
) -> EventObservableResult:
    incoming = tuple(incoming_momenta)
    final = tuple(final_states)
    if not incoming or not final:
        raise ValueError("event observables require incoming and final momenta")
    if not action_version or not background_id or not provenance:
        raise ValueError("event-observable action/background provenance is required")
    state_ids = tuple(state.state_id for state in final)
    if len(state_ids) != len(set(state_ids)):
        raise ValueError("final-state ids must be unique")
    for momentum in (*incoming, *(state.momentum for state in final)):
        momentum.require_nonspacelike()

    initial_total = _sum_momenta(incoming)
    final_total = _sum_momenta(state.momentum for state in final)
    visible = tuple(state for state in final if state.visible)
    visible_total = _sum_momenta(state.momentum for state in visible)
    initial_vector = np.asarray([
        initial_total.energy, initial_total.px, initial_total.py, initial_total.pz,
    ])
    final_vector = np.asarray([
        final_total.energy, final_total.px, final_total.py, final_total.pz,
    ])
    conservation = float(
        np.linalg.norm(initial_vector - final_vector)
        / max(np.linalg.norm(initial_vector), np.linalg.norm(final_vector), np.finfo(float).tiny)
    )
    missing_px = initial_total.px - visible_total.px
    missing_py = initial_total.py - visible_total.py

    pairwise_masses: dict[str, float] = {}
    pairwise_delta_r: dict[str, float] = {}
    for first_index, first in enumerate(final):
        for second in final[first_index + 1:]:
            key = f"{first.state_id}|{second.state_id}"
            pairwise_masses[key] = _invariant_mass(first.momentum + second.momentum)
            if first.visible and second.visible:
                delta_y = first.momentum.rapidity - second.momentum.rapidity
                delta_phi = _delta_phi(first.momentum.azimuth, second.momentum.azimuth)
                pairwise_delta_r[key] = math.hypot(delta_y, delta_phi)

    return EventObservableResult(
        initial_invariant_mass=_invariant_mass(initial_total),
        final_invariant_mass=_invariant_mass(final_total),
        scalar_visible_ht=math.fsum(state.momentum.transverse_momentum for state in visible),
        missing_transverse_px=missing_px,
        missing_transverse_py=missing_py,
        missing_transverse_momentum=math.hypot(missing_px, missing_py),
        pairwise_invariant_masses=pairwise_masses,
        pairwise_delta_r_y=pairwise_delta_r,
        four_momentum_conservation_relative_residual=conservation,
        final_state_ids=state_ids,
        visible_state_ids=tuple(state.state_id for state in visible),
        complete_final_state_ledger=bool(complete_final_state_ledger),
        gate7_closed=bool(gate7_closed),
        action_version=action_version,
        background_id=background_id,
        provenance=provenance,
    )


__all__ = [
    "EventObservableResult",
    "FinalStateMomentum",
    "FourMomentum",
    "build_event_observables",
]
