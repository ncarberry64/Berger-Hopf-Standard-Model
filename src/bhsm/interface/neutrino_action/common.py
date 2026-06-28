"""Typed evidence records for neutral action and unit closure."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ACTION_STATUSES = (
    "ARTIFACT_BACKED_NEUTRAL_ACTION_STIFFNESS",
    "CONDITIONAL_NEUTRAL_ACTION_STIFFNESS_CANDIDATE",
    "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
    "OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS",
    "OPEN_MISSING_NEUTRAL_CURVATURE_PENALTY",
    "OPEN_MISSING_NUMERIC_STIFFNESS_LENGTH",
    "ARTIFACT_BACKED_PHYSICAL_NEUTRAL_CURVATURE_MAP",
    "CONDITIONAL_PHYSICAL_NEUTRAL_CURVATURE_MAP_CANDIDATE",
    "OPEN_MISSING_PHYSICAL_CURVATURE_UNIT_MAP",
    "OPEN_MISSING_BOUNDARY_MEASURE_NORMALIZATION",
    "OPEN_MISSING_TRANSPORT_LENGTH",
    "ARTIFACT_BACKED_ACTION_DERIVED_RESPONSE_CONE",
    "CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE",
    "OPEN_MISSING_ACTION_DERIVED_RESPONSE_CONE",
    "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE",
    "DIMENSIONFUL_MASS_AVAILABLE",
    "DIMENSIONFUL_MASS_NOT_AVAILABLE",
    "FORBIDDEN_EMPIRICAL_STIFFNESS",
    "FORBIDDEN_EMPIRICAL_CURVATURE_SCALE",
    "INCONSISTENT_WITH_AUTHOR_ONTOLOGY",
)


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionEvidence(Serializable):
    candidate_key: str
    status: str
    value: float | str | None
    unit: str | None
    dimension: str
    numeric_value: float | None
    symbolic_value: str | None
    source_type: str
    source_artifacts: tuple[str, ...]
    source_equations: tuple[str, ...]
    provenance: tuple[dict[str, Any], ...]
    author_ontology_dependency: str
    empirical_derivation_inputs_used: bool
    reference_values_used_as_theorem_inputs: bool
    electron_neutrino_limit_used_as_derivation_input: bool
    w_mass_used_as_theorem_input: bool
    legacy_particle_tables_used_as_derivation_inputs: bool
    claim_boundary: str
    remaining_missing_object: str

    def __post_init__(self) -> None:
        if self.status not in ACTION_STATUSES:
            raise ValueError(f"unsupported neutral action status: {self.status}")
        if any(
            (
                self.empirical_derivation_inputs_used,
                self.reference_values_used_as_theorem_inputs,
                self.electron_neutrino_limit_used_as_derivation_input,
                self.w_mass_used_as_theorem_input,
                self.legacy_particle_tables_used_as_derivation_inputs,
            )
        ):
            raise ValueError("neutral action closure cannot use empirical theorem inputs")


@dataclass(frozen=True)
class NeutralActionTerm(ActionEvidence):
    term_key: str
    role: str
    coefficient_symbol: str
    coefficient_numeric_available: bool
    action_derived: bool


@dataclass(frozen=True)
class NeutralActionSourceSearchResult(ActionEvidence):
    terms: tuple[NeutralActionTerm, ...]
    artifact_backed_terms_found: bool
    conditional_variational_structure_found: bool
    complete_normalized_action_found: bool


@dataclass(frozen=True)
class NeutralKineticStiffnessResult(ActionEvidence):
    coefficient_symbol: str
    symbolic_available: bool
    numeric_available: bool


@dataclass(frozen=True)
class NeutralCurvaturePenaltyResult(ActionEvidence):
    coefficient_symbol: str
    symbolic_available: bool
    numeric_available: bool
    distinct_from_robin_coefficient: bool


@dataclass(frozen=True)
class NeutralStiffnessLengthResult(ActionEvidence):
    kinetic: NeutralKineticStiffnessResult
    curvature_penalty: NeutralCurvaturePenaltyResult
    ratio_symbolic: str
    numeric_length_available: bool
    stiffness_length_m: float | None


@dataclass(frozen=True)
class PhysicalNeutralCurvatureMapResult(ActionEvidence):
    dimensionless_response_available: bool
    symbolic_physical_map_available: bool
    numeric_per_m2_available: bool
    curvature_per_m2: float | None
    boundary_measure_normalized: bool
    transport_length_available: bool


@dataclass(frozen=True)
class ActionDerivedResponseConeResult(ActionEvidence):
    constraints: tuple[str, ...]
    ontology_support: bool
    partial_action_support: bool
    complete_action_derived: bool
    positivity_proven_on_cone: bool


@dataclass(frozen=True)
class NeutralActionSpectralClosureResult(ActionEvidence):
    stiffness: NeutralStiffnessLengthResult
    curvature_map: PhysicalNeutralCurvatureMapResult
    response_cone: ActionDerivedResponseConeResult
    admissible_positivity_status: str
    inverse_length_gap_per_m: float | None
    energy_joule: float | None
    mass_kg: float | None
    mass_eV: float | None
    mass_GeV: float | None
    dimensionful_mass_available: bool
    dimensionful_mass_status: str


@dataclass(frozen=True)
class NeutralActionClosureReport(ActionEvidence):
    report_name: str
    version: str
    public_status: str
    source_search: NeutralActionSourceSearchResult
    stiffness: NeutralStiffnessLengthResult
    curvature_map: PhysicalNeutralCurvatureMapResult
    response_cone: ActionDerivedResponseConeResult
    spectral_closure: NeutralActionSpectralClosureResult
    frozen_predictions_changed: bool
    production_physics_model_logic_changed: bool
    internet_required: bool
    external_hep_tools_required: bool
    libreoffice_required: bool


def provenance(paths: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "source_path": path,
            "empirical_derivation_input": False,
            "reference_theorem_input": False,
            "legacy_particle_table_input": False,
        }
        for path in paths
    )


def guard_fields() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "reference_values_used_as_theorem_inputs": False,
        "electron_neutrino_limit_used_as_derivation_input": False,
        "w_mass_used_as_theorem_input": False,
        "legacy_particle_tables_used_as_derivation_inputs": False,
    }
