"""Conservative BHSM v15.0 stratified Aether extension schema."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


GEOMETRIC_STRATUM = "G_A"
CORE_STRATUM = "C_A"


@dataclass(frozen=True)
class AetherState:
    state_id: str
    stratum: str
    data: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.stratum not in {GEOMETRIC_STRATUM, CORE_STRATUM}:
            raise ValueError("unknown Aether stratum")
        forbidden = {"spacetime_coordinates", "time", "duration", "energy", "energy_density", "velocity", "preferred_frame"}
        if self.stratum == CORE_STRATUM and (forbidden & set(self.data)):
            raise ValueError("non-geometric core data cannot carry spacetime, time, energy, velocity, or frame fields")
        if self.stratum == CORE_STRATUM and "upsilon" in self.data:
            raise ValueError("upsilon is undefined on the separate Aether core stratum")
        if self.stratum == GEOMETRIC_STRATUM:
            u = self.data.get("upsilon")
            if u is None or not (0.0 < float(u) <= 1.0):
                raise ValueError("geometric states require regular upsilon in (0,1]")


def geometric_state(state_id: str, upsilon: float = 1.0, **diagnostics: Any) -> AetherState:
    return AetherState(state_id, GEOMETRIC_STRATUM, {"upsilon": float(upsilon), **diagnostics})


def core_state(state_id: str, **invariants: Any) -> AetherState:
    return AetherState(state_id, CORE_STRATUM, dict(invariants))


def reconstruct_bhsm(state: AetherState) -> dict[str, Any] | None:
    if state.stratum != GEOMETRIC_STRATUM:
        return None
    return {
        "regular_support": {"upsilon": state.data["upsilon"]},
        "stratification": ["M8", "M5_plus", "M5_minus", "M4"],
        "incidence": "M8<->(M5_plus,M5_minus)<->M4",
        "legacy_action_and_domains_retained": True,
    }


def parent_stratification_payload() -> dict[str, Any]:
    core = core_state("core_schema", invariant_signature="abstract_only")
    regular = geometric_state("regular_schema", 0.5)
    return {
        "version": "v15.0",
        "technical_term": "BHSM Aether",
        "BHSM_AETHER_NOT_LUMINIFEROUS_ETHER": True,
        "ontology": "pre_geometric_relational_parent_structure_not_a_material_medium",
        "state_space": "S=G_A disjoint_union C_A",
        "option_B_branch": "MATHEMATICALLY_ADMISSIBLE_CONSERVATIVE_EXTENSION",
        "core_nonidentification": "C_A != {upsilon=0}",
        "upsilon_defined_on": GEOMETRIC_STRATUM,
        "regular_example": {"state_id": regular.state_id, "stratum": regular.stratum, "data": dict(regular.data)},
        "core_example": {"state_id": core.state_id, "stratum": core.stratum, "data": dict(core.data)},
        "core_has_spacetime_coordinates": False,
        "core_has_conventional_time": False,
        "core_has_conventional_energy": False,
        "core_has_metric_size": False,
        "fundamental_schema_status": "CANDIDATE_TYPED_EXTENSION_NOT_DERIVED_PARENT_ACTION",
        "schema_reuse": {
            "S": "existing stratified sectors plus separate nongeometric object class",
            "R": "existing envelopment/boundary correspondences on G_A; core adjacency missing",
            "H_and_D": "existing relative/boundary or unbounded KK candidates; no duplicate operator adopted",
            "rho": "abstract state functional only; no new M8/M5/M4 scalar",
            "I": "invariant signatures to be selected by a parent law",
        },
        "new_fundamental_dynamical_field_introduced": False,
        "new_continuous_parameter_introduced": False,
        "additional_structure_required": "action_owned_pregeometric_core_adjacency_and_transition_law",
    }
