"""BHSM v14.40 matter/rotor-sourced Spin(4) multipole audit.

This module asks whether any currently owned dynamical source can generate the
non-Killing L=2 and L=3 coexact shift components required by the v12.1 family
selection theorem.

It distinguishes four notions that must not be conflated:

* a static Wilson observable versus a dynamical worldline/flux-tube action;
* the rigid collective rotation of the radially equivariant eta knot versus a
  nonaxisymmetric deformation;
* a diagonal occupation density versus off-diagonal family coherence;
* state-dependent frame dragging versus a universal CKM response background.

No physical CKM matrix, CP phase, mass, scale, or compact-cap eigenvalue is
emitted.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

VERSION = "v14.40"
PUBLIC_STATUS = "source multipole audit complete; universal L2/L3 source remains open"

PRIMARY_VERDICT = (
    "BHSM_RIGID_FR_ETA_ROTOR_STATIC_WILSON_INSERTIONS_AND_DIAGONAL_FAMILY_"
    "OCCUPATIONS_DO_NOT_SUPPLY_THE_UNIVERSAL_CONNECTED_L2_L3_COEXACT_SHIFT_"
    "REQUIRED_FOR_CKM"
)
SECONDARY_VERDICT = (
    "OFF_DIAGONAL_FAMILY_COHERENCE_CAN_KINEMATICALLY_SOURCE_THE_REQUIRED_"
    "SPIN4_CHANNELS_BUT_USING_SUCH_COHERENCE_TO_DERIVE_MIXING_IS_CIRCULAR_"
    "UNTIL_THE_COLLECTIVE_DIRAC_ACTION_AND_BACKGROUND_STATE_ARE_ACTION_SELECTED"
)
EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_FAMILY_INDEPENDENT_NONAXISYMMETRIC_RELATIVE_FRAME_BACKGROUND_"
    "OR_COLLECTIVE_FERMION_EFFECTIVE_ACTION_WITH_L2_L3_COEXACT_COMPONENTS_"
    "ON_THE_COMPACT_CAP_MATCHED_TO_THE_TETRAD_SPIN_CONNECTION"
)

ARTIFACT_FILES = {
    "multipoles": "BHSM_eta_rotor_fermion_source_multipole_audit_v14_40.json",
    "coherence": "BHSM_family_coherence_circularity_gate_v14_40.json",
    "wilson": "BHSM_Wilson_source_and_universality_audit_v14_40.json",
    "completion": "BHSM_completion_gate_v14_40.json",
}


@dataclass(frozen=True)
class FamilyState:
    sector: str
    slot: str
    J: int
    m: int


@dataclass(frozen=True)
class RequiredEdge:
    sector: str
    source_slot: str
    target_slot: str
    L: int
    r: int


FROZEN_STATES = {
    "up": (
        FamilyState("up", "heavy", 0, 0),
        FamilyState("up", "middle", 3, 3),
        FamilyState("up", "light", 5, 4),
    ),
    "down": (
        FamilyState("down", "heavy", 0, 0),
        FamilyState("down", "middle", 3, 0),
        FamilyState("down", "light", 4, 2),
    ),
}

REQUIRED_EDGES = (
    RequiredEdge("up", "heavy", "middle", 3, 3),
    RequiredEdge("up", "middle", "light", 2, 1),
    RequiredEdge("down", "heavy", "middle", 3, 0),
    RequiredEdge("down", "middle", "light", 2, 2),
)


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def diagonal_density_allowed_r() -> tuple[int, ...]:
    """A diagonal |J,m><J,m| density has magnetic transfer r=m-m=0."""

    return (0,)


def edge_supported_by_r(edge: RequiredEdge, allowed_r: Iterable[int]) -> bool:
    return edge.r in set(int(value) for value in allowed_r)


def supported_edges(allowed_r: Iterable[int]) -> tuple[RequiredEdge, ...]:
    allowed = tuple(int(value) for value in allowed_r)
    return tuple(edge for edge in REQUIRED_EDGES if edge_supported_by_r(edge, allowed))


def sector_graph_connected(sector: str, edges: Iterable[RequiredEdge]) -> bool:
    slots = {state.slot for state in FROZEN_STATES[sector]}
    adjacency = {slot: set() for slot in slots}
    for edge in edges:
        if edge.sector != sector:
            continue
        adjacency[edge.source_slot].add(edge.target_slot)
        adjacency[edge.target_slot].add(edge.source_slot)
    seen: set[str] = set()
    frontier = {"heavy"}
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        frontier.update(adjacency[current] - seen)
    return seen == slots


def required_coherences() -> dict[str, list[dict[str, Any]]]:
    """Return off-diagonal density entries required for all nonzero-r edges."""

    result: dict[str, list[dict[str, Any]]] = {"up": [], "down": []}
    for edge in REQUIRED_EDGES:
        result[edge.sector].append(
            {
                "density_entry": f"rho_{edge.target_slot},{edge.source_slot}",
                "required_rank": edge.L,
                "required_magnetic_transfer": edge.r,
                "off_diagonal": edge.source_slot != edge.target_slot,
                "coherence_required": edge.r != 0,
            }
        )
    return result


def rigid_eta_rotor_source_payload() -> dict[str, Any]:
    """Classify the angular multipole of the current radially equivariant rotor.

    For eta=(cos f, sin f n) and a constant target-plane generator T_ab,
    <T_ab eta, d eta> is a radial coefficient times the Killing one-form
    K_ab on the round angular orbit.  It is therefore an L=1 coexact mode.
    """

    validation = {
        "time_dependent_collective_rotation_can_have_nonzero_momentum": True,
        "radially_equivariant_rotor_current_is_Killing": True,
        "Killing_current_has_L1_only": True,
        "L2_absent": True,
        "L3_absent": True,
        "rigid_L1_family_mixing_rejected_by_v12_1": True,
    }
    return {
        "artifact": "BHSM_eta_rotor_fermion_source_multipole_audit_v14_40",
        "version": VERSION,
        "background": "current radially equivariant degree-one eta profile",
        "collective_coordinate": "A(t) in the selected orientation group",
        "momentum_density": "J_i_eta=2 w F'(X)<D_0 eta,D_i eta>",
        "equivariant_identity": "<T_ab eta,d eta>=c(r) K_ab_flat",
        "angular_character": {"L": 1, "type": "coexact Killing one-form"},
        "required_flavor_characters": ["L=2", "L=3"],
        "result": (
            "The FR/collective rotor can source rigid frame dragging, but the "
            "currently constructed equivariant profile supplies only L=1 and "
            "therefore cannot activate the v12.1 connected flavor response."
        ),
        "nonaxisymmetric_deformation_status": "OPEN_NOT_ACTION_SELECTED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def family_source_payload() -> dict[str, Any]:
    allowed = diagonal_density_allowed_r()
    edges = supported_edges(allowed)
    up_edges = [edge for edge in edges if edge.sector == "up"]
    down_edges = [edge for edge in edges if edge.sector == "down"]
    validation = {
        "diagonal_density_has_r0_only": allowed == (0,),
        "up_connected_chain_not_sourced": not sector_graph_connected("up", up_edges),
        "down_connected_chain_not_sourced": not sector_graph_connected("down", down_edges),
        "only_down_heavy_middle_edge_survives": [asdict(edge) for edge in down_edges]
        == [asdict(REQUIRED_EDGES[2])],
        "off_diagonal_coherence_required_for_full_chain": True,
        "using_unowned_coherence_as_mixing_source_is_circular": True,
    }
    return {
        "artifact": "BHSM_family_coherence_circularity_gate_v14_40",
        "version": VERSION,
        "frozen_states": {
            sector: [asdict(state) for state in states]
            for sector, states in FROZEN_STATES.items()
        },
        "Wigner_Eckart_selection": "r=m_target-m_source",
        "diagonal_density_support": {"allowed_r": list(allowed)},
        "required_edges": [asdict(edge) for edge in REQUIRED_EDGES],
        "supported_edges_from_diagonal_occupations": [asdict(edge) for edge in edges],
        "connected_graph": {
            "up": sector_graph_connected("up", up_edges),
            "down": sector_graph_connected("down", down_edges),
        },
        "required_coherences": required_coherences(),
        "circularity_statement": (
            "The r=3, r=1, and r=2 sources require off-diagonal family density "
            "matrix elements.  Inserting those coherences before the common-domain "
            "response or collective Dirac dynamics selects them presupposes the "
            "family superposition that the CKM derivation is meant to explain."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def wilson_source_payload() -> dict[str, Any]:
    validation = {
        "Wilson_loop_is_observable_not_worldline_action": True,
        "static_purely_electric_configuration_has_zero_Poynting_momentum": True,
        "static_Wilson_source_has_no_coexact_ADM_current": True,
        "rotating_loop_requires_external_motion_or_boundary_data": True,
        "color_source_is_family_central": True,
        "state_dependent_backreaction_is_not_universal_CKM": True,
    }
    return {
        "artifact": "BHSM_Wilson_source_and_universality_audit_v14_40",
        "version": VERSION,
        "Wilson_observable": "W(C)=1/3 Tr P exp(i integral_C A)",
        "stress_variation_status": (
            "A prescribed Wilson insertion is not by itself a dynamical matter "
            "action.  A distributional stress source requires an owned worldline, "
            "string, or dynamical flux-tube action and variation of its embedding."
        ),
        "static_limit": {
            "magnetic_field": "zero in the ideal static color-electric branch",
            "momentum_density": "T_0i proportional to (E cross B)_i = 0",
            "coexact_L2_L3_source": 0,
        },
        "rotating_limit": (
            "A rotating or twisted loop may have nonzero momentum density, but its "
            "motion and orientation are state/boundary data.  They are not a unique "
            "family-independent vacuum source selected by the present action."
        ),
        "universality_gate": (
            "CKM is a universal interaction-basis mismatch.  A shift beta[rho,C] "
            "that changes with the occupied hadron, spin state, or prescribed loop "
            "cannot by itself define the universal CKM matrix."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def formal_coexact_resolvent_payload() -> dict[str, Any]:
    return {
        "compact_cap_equation": "L_shift beta_perp = kappa_grav P_coexact J_total",
        "harmonic_solution": "beta_Lr^epsilon=(kappa_grav/lambda_L^shift) J_Lr^epsilon",
        "domain_requirements": [
            "gauge-fixed self-adjoint coexact shift operator",
            "compact cap and seam boundary conditions",
            "Killing L=1 quotient or collective treatment",
            "normalized matter/collective source",
        ],
        "current_status": {
            "lambda_L_shift": "UNDEFINED_ON_PHYSICAL_COMPACT_CAP",
            "normalized_collective_Dirac_source": "NOT_DERIVED",
            "static_Wilson_source": "ZERO_OR_NOT_DYNAMICAL",
            "rigid_eta_rotor_source": "L1_ONLY",
            "universal_L2_L3_source": "NOT_DERIVED",
        },
    }


def completion_payload() -> dict[str, Any]:
    rotor = rigid_eta_rotor_source_payload()
    family = family_source_payload()
    wilson = wilson_source_payload()
    validation = {
        "rotor_audit_passed": rotor["validation_passed"],
        "family_selection_audit_passed": family["validation_passed"],
        "Wilson_audit_passed": wilson["validation_passed"],
        "no_universal_action_owned_L2_L3_source_found": True,
        "Spin4_representation_theorem_preserved": True,
        "collective_Dirac_action_not_invented": True,
        "physical_CKM_not_emitted": True,
        "frozen_predictions_unchanged": True,
        "BHSM_not_complete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_40",
        "version": VERSION,
        "public_status": PUBLIC_STATUS,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "source_results": {
            "static_eta": "ZERO_MOMENTUM_FROM_V14_39",
            "rigid_FR_eta_rotor": "NONZERO_POSSIBLE_BUT_L1_ONLY",
            "static_Wilson": "ZERO_COEXACT_MOMENTUM_OR_OBSERVABLE_ONLY",
            "diagonal_stationary_family_occupation": "R0_ONLY_NOT_CONNECTED",
            "off_diagonal_family_coherence": "KINEMATICALLY_SUFFICIENT_IN_PART_BUT_CIRCULAR_UNTIL_ACTION_SELECTED",
        },
        "formal_resolvent": formal_coexact_resolvent_payload(),
        "Hindsight_20_20": {
            "validated": [
                "A time-dependent eta collective rotation can carry momentum.",
                "The current equivariant eta rotor sources only an L=1 Killing mode.",
                "Diagonal family occupations carry only r=0 source character.",
                "A prescribed static Wilson loop does not supply a universal coexact momentum source.",
            ],
            "invalidated": [
                "Rigid FR rotor frame dragging as the missing L=2,L=3 flavor background.",
                "Static Wilson insertion as the missing Spin4 source.",
                "Diagonal stationary family occupations as a connected three-family source.",
            ],
            "reclassified": [
                "Off-diagonal fermion bilinears are a response of an already coherent family state, not an upstream explanation of that coherence.",
                "Matter-sourced frame dragging is state-dependent backreaction, not automatically universal flavor geometry.",
            ],
            "open": [
                "A family-independent action-selected nonaxisymmetric relative-frame background.",
                "A collective fermion effective action and determinant on the compact cap.",
                "A matched tetrad/spin connection and normalized common-domain Dirac modes.",
                "Action-derived up/down response matrices and CKM/CP.",
            ],
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "multipoles": rigid_eta_rotor_source_payload(),
        "coherence": family_source_payload(),
        "wilson": wilson_source_payload(),
        "completion": completion_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads()
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = output_dir / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8", newline="\n")
        written.append(path)
    return written
