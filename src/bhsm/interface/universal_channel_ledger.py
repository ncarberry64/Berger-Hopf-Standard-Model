"""Complete action-owned decay and scattering channel inventories.

The ledger enumerates final-state multisets from a declared spectrum and
conserved additive quantum numbers.  It distinguishes exhaustive candidate
enumeration from physical resolution: a channel is resolved only when it is
kinematically closed, has an exact-zero amplitude certificate, or is
kinematically open with a strictly positive amplitude-squared enclosure.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement
import math
from typing import Callable, Iterable

from bhsm.interface.universal_spectral_forecast import CertifiedInterval


@dataclass(frozen=True)
class ChannelMode:
    mode_id: str
    mass: CertifiedInterval
    additive_quantum_numbers: tuple[int, ...]
    spin_twice: int
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.mode_id
            or not math.isfinite(self.mass.lower)
            or not math.isfinite(self.mass.upper)
            or self.mass.lower < 0.0
            or self.spin_twice < 0
        ):
            raise ValueError("channel mode identity, mass, and spin are required")
        if not all(isinstance(value, int) for value in self.additive_quantum_numbers):
            raise ValueError("additive quantum numbers must be exact integers")
        if not self.action_version or not self.background_id or not self.provenance:
            raise ValueError("channel mode action/background provenance is required")


@dataclass(frozen=True)
class InitialChannelState:
    state_id: str
    process_kind: str
    mode_ids: tuple[str, ...]
    center_of_mass_energy: CertifiedInterval
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.process_kind not in {"DECAY", "SCATTERING"}:
            raise ValueError("process kind must be DECAY or SCATTERING")
        expected_count = 1 if self.process_kind == "DECAY" else 2
        if len(self.mode_ids) != expected_count:
            raise ValueError(f"{self.process_kind} initial state needs {expected_count} modes")
        if (
            not self.state_id
            or not math.isfinite(self.center_of_mass_energy.lower)
            or not math.isfinite(self.center_of_mass_energy.upper)
            or self.center_of_mass_energy.lower < 0.0
            or not self.provenance
        ):
            raise ValueError("initial-state identity, energy, and provenance are required")


@dataclass(frozen=True)
class ChannelAmplitudeCertificate:
    initial_state_id: str
    final_mode_ids: tuple[str, ...]
    amplitude_squared: CertifiedInterval
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.initial_state_id or len(self.final_mode_ids) < 2:
            raise ValueError("amplitude certificate needs an initial and final state")
        if tuple(sorted(self.final_mode_ids)) != self.final_mode_ids:
            raise ValueError("final-state mode ids must use canonical sorted order")
        if (
            not math.isfinite(self.amplitude_squared.lower)
            or not math.isfinite(self.amplitude_squared.upper)
            or self.amplitude_squared.lower < 0.0
            or not self.provenance
        ):
            raise ValueError("amplitude enclosure and provenance are required")


@dataclass(frozen=True)
class ChannelLedgerEntry:
    channel_id: str
    initial_state_id: str
    process_kind: str
    initial_mode_ids: tuple[str, ...]
    final_mode_ids: tuple[str, ...]
    threshold: CertifiedInterval
    kinematic_status: str
    amplitude_status: str
    amplitude_squared: CertifiedInterval | None
    identical_final_state_factor: int
    physically_resolved: bool
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class CompleteChannelLedger:
    ledger_id: str
    entries: tuple[ChannelLedgerEntry, ...]
    action_version: str
    background_id: str
    maximum_final_multiplicity: int
    initial_states: tuple[tuple[str, str, bool], ...]
    candidate_inventory_complete: bool
    blockers: tuple[str, ...]
    provenance: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return self.candidate_inventory_complete and not self.blockers

    def require_complete(self) -> None:
        if not self.complete:
            raise RuntimeError("BHSM channel ledger blocked by: " + ", ".join(self.blockers))

    def initial_state_report(self, state_id: str) -> dict:
        state_map = {
            identifier: (kind, certified_open)
            for identifier, kind, certified_open in self.initial_states
        }
        if state_id not in state_map:
            raise KeyError(state_id)
        rows = [entry for entry in self.entries if entry.initial_state_id == state_id]
        kind, initial_state_certified_open = state_map[state_id]
        open_nonzero = [
            entry.channel_id
            for entry in rows
            if entry.kinematic_status == "OPEN"
            and entry.amplitude_status == "NONZERO"
        ]
        unresolved = [entry.channel_id for entry in rows if not entry.physically_resolved]
        state_complete = bool(
            self.candidate_inventory_complete
            and initial_state_certified_open
            and not unresolved
        )
        if kind == "DECAY":
            if open_nonzero:
                verdict = "CERTIFIED_UNSTABLE_HAS_OPEN_NONZERO_CHANNEL"
            elif state_complete:
                verdict = "CERTIFIED_STABLE_ON_COMPLETE_CHANNEL_LEDGER"
            else:
                verdict = "STABILITY_UNRESOLVED"
        else:
            verdict = (
                "COMPLETE_OPEN_CHANNEL_LEDGER"
                if state_complete
                else "OPEN_CHANNEL_LEDGER_UNRESOLVED"
            )
        return {
            "state_id": state_id,
            "process_kind": kind,
            "verdict": verdict,
            "channel_count": len(rows),
            "open_nonzero_channel_ids": open_nonzero,
            "unresolved_channel_ids": unresolved,
            "candidate_inventory_complete": self.candidate_inventory_complete,
            "initial_state_certified_open": initial_state_certified_open,
            "state_ledger_complete": state_complete,
            "ledger_complete": self.complete,
            "experimental_particle_assignment_used": False,
        }

    def metadata(self) -> dict:
        return {
            "ledger_id": self.ledger_id,
            "action_version": self.action_version,
            "background_id": self.background_id,
            "maximum_final_multiplicity": self.maximum_final_multiplicity,
            "initial_state_count": len(self.initial_states),
            "candidate_inventory_complete": self.candidate_inventory_complete,
            "physically_resolved_channel_count": sum(
                entry.physically_resolved for entry in self.entries
            ),
            "channel_count": len(self.entries),
            "blockers": list(self.blockers),
            "complete": self.complete,
            "empirical_input_used": False,
        }


def _sum_quantum_numbers(modes: Iterable[ChannelMode], width: int) -> tuple[int, ...]:
    total = [0] * width
    for mode in modes:
        if len(mode.additive_quantum_numbers) != width:
            raise ValueError("all channel modes must use one quantum-number basis")
        for index, value in enumerate(mode.additive_quantum_numbers):
            total[index] += value
    return tuple(total)


def _conserved(
    initial: tuple[int, ...],
    final: tuple[int, ...],
    moduli: tuple[int | None, ...],
) -> bool:
    for before, after, modulus in zip(initial, final, moduli):
        if modulus is None:
            if before != after:
                return False
        elif (before - after) % modulus != 0:
            return False
    return True


def _symmetry_factor(mode_ids: tuple[str, ...]) -> int:
    return math.prod(math.factorial(count) for count in Counter(mode_ids).values())


def build_complete_channel_ledger(
    ledger_id: str,
    modes: Iterable[ChannelMode],
    initial_states: Iterable[InitialChannelState],
    amplitude_certificates: Iterable[ChannelAmplitudeCertificate],
    *,
    maximum_final_multiplicity: int,
    quantum_number_moduli: tuple[int | None, ...] | None = None,
    allowed_final_mode_ids: Iterable[str] | None = None,
    selection_rule: Callable[[InitialChannelState, tuple[ChannelMode, ...]], bool] | None = None,
    selection_rule_id: str = "ADDITIVE_QUANTUM_NUMBER_CONSERVATION_ONLY",
    spectrum_complete: bool,
    selection_rules_complete: bool,
    provenance: tuple[str, ...],
) -> CompleteChannelLedger:
    """Enumerate and adjudicate all declared ``1->n`` and ``2->n`` channels."""

    mode_rows = tuple(modes)
    state_rows = tuple(initial_states)
    certificates = tuple(amplitude_certificates)
    if (
        not ledger_id
        or not provenance
        or not selection_rule_id
        or maximum_final_multiplicity < 2
    ):
        raise ValueError("ledger identity, provenance, and final multiplicity are required")
    if not mode_rows or not state_rows:
        raise ValueError("channel ledger requires modes and initial states")
    mode_ids = [mode.mode_id for mode in mode_rows]
    state_ids = [state.state_id for state in state_rows]
    if len(mode_ids) != len(set(mode_ids)) or len(state_ids) != len(set(state_ids)):
        raise ValueError("mode and initial-state ids must be unique")
    mode_map = {mode.mode_id: mode for mode in mode_rows}
    action_versions = {mode.action_version for mode in mode_rows}
    backgrounds = {mode.background_id for mode in mode_rows}
    if len(action_versions) != 1 or len(backgrounds) != 1:
        raise ValueError("all channel modes must share one action and background")
    action_version = next(iter(action_versions))
    background_id = next(iter(backgrounds))
    quantum_width = len(mode_rows[0].additive_quantum_numbers)
    moduli = quantum_number_moduli or (None,) * quantum_width
    if len(moduli) != quantum_width or any(
        modulus is not None and modulus < 2 for modulus in moduli
    ):
        raise ValueError("quantum-number moduli must match the declared basis")
    initial_state_metadata: list[tuple[str, str, bool]] = []
    initial_state_blockers: list[str] = []
    for state in state_rows:
        if any(mode_id not in mode_map for mode_id in state.mode_ids):
            raise ValueError("initial state references an unknown mode")
        if state.process_kind == "DECAY":
            parent_mass = mode_map[state.mode_ids[0]].mass
            if state.center_of_mass_energy != parent_mass:
                raise ValueError("decay initial energy must equal the parent mass interval")
            certified_open = True
        else:
            incoming_modes = tuple(mode_map[mode_id] for mode_id in state.mode_ids)
            incoming_threshold_upper = math.fsum(
                mode.mass.upper for mode in incoming_modes
            )
            certified_open = (
                state.center_of_mass_energy.lower > incoming_threshold_upper
            )
            if not certified_open:
                initial_state_blockers.append(
                    f"{state.state_id}:initial_state_not_certified_open"
                )
        initial_state_metadata.append((state.state_id, state.process_kind, certified_open))
    final_ids = (
        tuple(sorted(allowed_final_mode_ids))
        if allowed_final_mode_ids is not None
        else tuple(sorted(mode_map))
    )
    if not final_ids or len(final_ids) != len(set(final_ids)):
        raise ValueError("allowed final mode ids must be unique and nonempty")
    if any(mode_id not in mode_map for mode_id in final_ids):
        raise ValueError("allowed final state references an unknown mode")

    certificate_map: dict[tuple[str, tuple[str, ...]], ChannelAmplitudeCertificate] = {}
    for certificate in certificates:
        key = (certificate.initial_state_id, certificate.final_mode_ids)
        if key in certificate_map:
            raise ValueError("duplicate channel amplitude certificate")
        certificate_map[key] = certificate

    entries: list[ChannelLedgerEntry] = []
    enumerated_keys: set[tuple[str, tuple[str, ...]]] = set()
    for state in state_rows:
        initial_modes = tuple(mode_map[mode_id] for mode_id in state.mode_ids)
        initial_quantum_numbers = _sum_quantum_numbers(initial_modes, quantum_width)
        for multiplicity in range(2, maximum_final_multiplicity + 1):
            for daughters in combinations_with_replacement(final_ids, multiplicity):
                daughter_modes = tuple(mode_map[mode_id] for mode_id in daughters)
                final_quantum_numbers = _sum_quantum_numbers(
                    daughter_modes, quantum_width
                )
                if not _conserved(initial_quantum_numbers, final_quantum_numbers, moduli):
                    continue
                if selection_rule is not None and not selection_rule(state, daughter_modes):
                    continue
                key = (state.state_id, daughters)
                enumerated_keys.add(key)
                certificate = certificate_map.get(key)
                threshold = CertifiedInterval(
                    math.fsum(mode.mass.lower for mode in daughter_modes),
                    math.fsum(mode.mass.upper for mode in daughter_modes),
                )
                energy = state.center_of_mass_energy
                if energy.upper < threshold.lower:
                    kinematic_status = "CLOSED"
                elif energy.lower > threshold.upper:
                    kinematic_status = "OPEN"
                else:
                    kinematic_status = "UNRESOLVED"
                amplitude = None if certificate is None else certificate.amplitude_squared
                if amplitude is None or amplitude.lower == 0.0 < amplitude.upper:
                    amplitude_status = "UNRESOLVED"
                elif amplitude.is_exact_zero():
                    amplitude_status = "EXACT_ZERO"
                else:
                    amplitude_status = "NONZERO"
                physically_resolved = (
                    kinematic_status == "CLOSED"
                    or amplitude_status == "EXACT_ZERO"
                    or (
                        kinematic_status == "OPEN"
                        and amplitude_status == "NONZERO"
                    )
                )
                entries.append(ChannelLedgerEntry(
                    channel_id=f"{state.state_id}->{'+' .join(daughters)}",
                    initial_state_id=state.state_id,
                    process_kind=state.process_kind,
                    initial_mode_ids=state.mode_ids,
                    final_mode_ids=daughters,
                    threshold=threshold,
                    kinematic_status=kinematic_status,
                    amplitude_status=amplitude_status,
                    amplitude_squared=amplitude,
                    identical_final_state_factor=_symmetry_factor(daughters),
                    physically_resolved=physically_resolved,
                    provenance=(selection_rule_id,) + (
                        () if certificate is None else certificate.provenance
                    ),
                ))
    extra_certificates = sorted(set(certificate_map) - enumerated_keys)
    if extra_certificates:
        raise ValueError("amplitude certificate does not match an enumerated channel")

    inventory_complete = bool(spectrum_complete and selection_rules_complete)
    blockers: list[str] = []
    if not spectrum_complete:
        blockers.append("spectrum_not_complete")
    if not selection_rules_complete:
        blockers.append("selection_rules_not_complete")
    blockers.extend(initial_state_blockers)
    blockers.extend(
        f"{entry.channel_id}:physical_channel_status_unresolved"
        for entry in entries
        if not entry.physically_resolved
    )
    return CompleteChannelLedger(
        ledger_id=ledger_id,
        entries=tuple(entries),
        action_version=action_version,
        background_id=background_id,
        maximum_final_multiplicity=maximum_final_multiplicity,
        initial_states=tuple(initial_state_metadata),
        candidate_inventory_complete=inventory_complete,
        blockers=tuple(blockers),
        provenance=provenance,
    )


__all__ = [
    "ChannelAmplitudeCertificate",
    "ChannelLedgerEntry",
    "ChannelMode",
    "CompleteChannelLedger",
    "InitialChannelState",
    "build_complete_channel_ledger",
]
