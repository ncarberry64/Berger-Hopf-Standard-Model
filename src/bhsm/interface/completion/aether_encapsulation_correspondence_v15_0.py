"""Executable abstract event-span calculus for BHSM v15.0."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class EventSpan:
    incoming: str
    outgoing: str
    event_word: tuple[str, ...]
    invariant_signature: tuple[tuple[str, str], ...]
    process_depth: Fraction = Fraction(1)

    def __post_init__(self) -> None:
        if self.process_depth < 0:
            raise ValueError("process depth must be nonnegative")
        if not self.event_word and not (
            self.incoming == self.outgoing and self.process_depth == 0
        ):
            raise ValueError("an empty event word is reserved for a zero-depth identity span")

    @classmethod
    def identity(
        cls, boundary: str, invariant_signature: tuple[tuple[str, str], ...]
    ) -> "EventSpan":
        return cls(boundary, boundary, (), invariant_signature, Fraction(0))

    def then(self, other: "EventSpan") -> "EventSpan":
        if self.outgoing != other.incoming:
            raise ValueError("event boundaries do not match")
        if self.invariant_signature != other.invariant_signature:
            raise ValueError("parent invariant signatures do not match")
        return EventSpan(
            self.incoming,
            other.outgoing,
            self.event_word + other.event_word,
            self.invariant_signature,
            self.process_depth + other.process_depth,
        )


def exterior_clock_interval(t_in: float, t_out: float) -> float:
    if t_out < t_in:
        raise ValueError("outgoing exterior clock reading precedes incoming reading")
    return float(t_out - t_in)


def event_correspondence_payload() -> dict[str, Any]:
    signature = (("degree_eta", "1"), ("closed_parent_charge", "Q"))
    first = EventSpan("A_minus", "A_mid", ("E_1",), signature, Fraction(2, 5))
    second = EventSpan("A_mid", "A_plus", ("E_2",), signature, Fraction(3, 5))
    composite = first.then(second)
    return {
        "version": "v15.0",
        "object": "boundary_to_boundary_span_in_the_candidate_Aether_category",
        "incoming_and_outgoing_stratum": "G_A",
        "internal_event_stratum": "C_A",
        "composition": "match_middle_boundary_and_parent_invariant_signature_then_concatenate_event_words",
        "composition_witness": {
            "incoming": composite.incoming,
            "outgoing": composite.outgoing,
            "event_word": list(composite.event_word),
            "process_depth": str(composite.process_depth),
            "invariants": dict(composite.invariant_signature),
        },
        "associative": True,
        "identity": "empty_boundary_correspondence_at_each_geometric_state",
        "invariant_matching_transitive_under_composition": True,
        "exterior_finite_clock_interval": exterior_clock_interval(3.0, 5.0),
        "core_intrinsic_spacetime_position": None,
        "core_intrinsic_duration": None,
        "core_intrinsic_metric_size": None,
        "core_conventional_energy_density": None,
        "finite_exterior_event_implies_core_intrinsic_duration": False,
        "existing_BHSM_action_derives_this_event_law": False,
        "status": "MATHEMATICALLY_WELL_DEFINED_CANDIDATE_NOT_ACTION_OWNED",
        "conservation_boundary": (
            "Abstract parent signatures compose exactly. Their projection to ADM constraints, Brown-York data, "
            "Noether charges, or cap currents remains conditional on an action-owned reconstruction functor and boundary ensemble."
        ),
    }
