"""Fail-closed interface from a canonical stop to physical encapsulation.

This module does not add a BHSM action term or identify a new particle.  It
encodes the minimum evidence conjunction required before an already-certified
mathematical stop may be promoted to an action-owned physical encapsulation
event and geometric child.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


BRIDGE_VERSION = "BHSM-AE2-PHYSICAL-ENCAPSULATION-BRIDGE-1.0.0"


@dataclass(frozen=True)
class IdentificationRequirement:
    """One independently auditable physical-identification obligation."""

    requirement_id: str
    name: str
    layer: str
    required_for_generic_identification: bool
    statement: str


REQUIREMENTS = (
    IdentificationRequirement(
        "PEI_01",
        "canonical_stop",
        "mathematical_carrier",
        True,
        "A same-action physical parent history reaches an action-selected "
        "canonical stop before any earlier physical-domain exit.",
    ),
    IdentificationRequirement(
        "PEI_02",
        "event_child_relation",
        "mathematical_carrier",
        True,
        "The stop lies in a regular nonempty event-to-complete-child relation.",
    ),
    IdentificationRequirement(
        "PEI_03",
        "route_selector",
        "physical_domain",
        True,
        "The unchanged action selects exactly which admissible enclosure route "
        "is realized: same-spacetime local enclosure, geometric boundary/collar "
        "enclosure, or spacetime-edge transition.",
    ),
    IdentificationRequirement(
        "PEI_04",
        "enclosure_carrier",
        "physical_domain",
        True,
        "An action-owned local carrier supplies intrinsic enclosure data and "
        "external embedding, normal, extrinsic-curvature, collar, and attachment "
        "data on a declared domain.",
    ),
    IdentificationRequirement(
        "PEI_05",
        "matching_and_junction_domain",
        "physical_domain",
        True,
        "Induced-metric, lapse/shift, momentum/flux, field-trace, and junction "
        "conditions are selected by the action on one compatible domain.",
    ),
    IdentificationRequirement(
        "PEI_06",
        "full_field_restriction",
        "full_action",
        True,
        "Gauge/ghost, fermion, scalar/HS, and geometry blocks participate, or "
        "their vanishing is proved to define an invariant same-action subdomain.",
    ),
    IdentificationRequirement(
        "PEI_07",
        "event_balance",
        "full_action",
        True,
        "Constraints, the complete parent/event/child Noether-Hamiltonian balance, "
        "and all interface contact terms close through the event.",
    ),
    IdentificationRequirement(
        "PEI_08",
        "nonlinear_local_completion",
        "physical_identification",
        True,
        "The stop produces a nontrivial localized completed configuration rather "
        "than only a Hessian zero, proof cutoff, chart failure, or relabeling.",
    ),
    IdentificationRequirement(
        "PEI_09",
        "child_inheritance",
        "physical_identification",
        True,
        "The event-to-child map transports the selected enclosure geometry, "
        "boundary incidence/topology, full-field traces, and conserved data into "
        "the child class.",
    ),
    IdentificationRequirement(
        "PEI_10",
        "positive_duration_separation",
        "chronology",
        True,
        "The identified child has positive-duration evolution, while stability, "
        "decay, and later events remain separate claims.",
    ),
    IdentificationRequirement(
        "PEI_11",
        "upstream_particle_state_transport",
        "particle_manifestation",
        False,
        "The provenance-frozen BHSM family/mode, representation, projector, "
        "current, and topological state is attached to the parent and transported "
        "through the event-child enclosure map into its existing Standard Model "
        "manifestation class without rederiving the particle spectrum.",
    ),
)


ENCLOSURE_ROUTES = (
    "LOCAL_SAME_SPACETIME_ENCLOSURE",
    "CORE_BOUNDARY_OR_COLLAR_ENCLOSURE",
    "SPACETIME_EDGE_TRANSITION",
)


def evaluate_identification(
    evidence: Mapping[str, bool],
    *,
    particle_state_transport_claimed: bool = False,
) -> dict[str, object]:
    """Evaluate the bridge without substituting interpretation for evidence.

    Missing keys fail closed.  ``PEI_11`` becomes mandatory when the bridge is
    used to carry an existing BHSM family/mode state into its Standard Model
    particle manifestation.  It imports that state; it does not rederive it.
    """

    rows: list[dict[str, object]] = []
    missing: list[str] = []
    for requirement in REQUIREMENTS:
        required = requirement.required_for_generic_identification or (
            particle_state_transport_claimed
            and requirement.requirement_id == "PEI_11"
        )
        satisfied = bool(evidence.get(requirement.requirement_id, False))
        if required and not satisfied:
            missing.append(requirement.requirement_id)
        rows.append(
            {
                "id": requirement.requirement_id,
                "name": requirement.name,
                "layer": requirement.layer,
                "required": required,
                "satisfied": satisfied,
                "statement": requirement.statement,
            }
        )

    identified = not missing
    return {
        "bridge_version": BRIDGE_VERSION,
        "particle_state_transport_claimed": particle_state_transport_claimed,
        "requirements": rows,
        "missing_required_obligations": missing,
        "physical_encapsulation_identified": identified,
        "classification": (
            "PHYSICAL_ENCAPSULATION_IDENTIFIED"
            if identified
            else "PHYSICAL_ENCAPSULATION_IDENTIFICATION_OPEN"
        ),
    }


def assert_no_forbidden_equivalence(
    *,
    lambda24_equals_two_pi: bool,
    canonical_stop_equals_spacetime_edge: bool,
    positive_duration_equals_stability: bool,
) -> None:
    """Reject the three ontology substitutions ruled out by current evidence."""

    forbidden = {
        "lambda24_equals_two_pi": lambda24_equals_two_pi,
        "canonical_stop_equals_spacetime_edge": canonical_stop_equals_spacetime_edge,
        "positive_duration_equals_stability": positive_duration_equals_stability,
    }
    promoted = [name for name, value in forbidden.items() if value]
    if promoted:
        raise ValueError("unsupported physical equivalence: " + ", ".join(promoted))
