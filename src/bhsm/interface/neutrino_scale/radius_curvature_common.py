"""Typed records for neutral radius and physical-curvature closure."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


RADIUS_CURVATURE_STATUSES = (
    "ARTIFACT_BACKED_PROPAGATION_RADIUS",
    "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE",
    "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS",
    "ARTIFACT_BACKED_PHYSICAL_CURVATURE_MAP",
    "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE",
    "OPEN_MISSING_PHYSICAL_NEUTRAL_CURVATURE_MAP",
    "CONDITIONAL_DIMENSIONFUL_MASS_CANDIDATE",
    "DIMENSIONFUL_MASS_NOT_AVAILABLE",
    "FORBIDDEN_EMPIRICAL_RADIUS",
    "FORBIDDEN_EMPIRICAL_CURVATURE_SCALE",
    "INCONSISTENT_WITH_AUTHOR_ONTOLOGY",
    "DIMENSIONLESS_LENGTH_PROXY",
    "DIMENSIONLESS_CURVATURE_RESPONSE",
    "REFERENCE_ONLY",
    "EMPIRICAL_FORBIDDEN",
    "MISSING",
)


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceRecord(Serializable):
    candidate_key: str
    status: str
    value: float | str | None
    unit: str | None
    dimension: str
    source_type: str
    source_artifacts: tuple[str, ...]
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
        if self.status not in RADIUS_CURVATURE_STATUSES:
            raise ValueError(f"unsupported radius/curvature status: {self.status}")
        if any(
            (
                self.empirical_derivation_inputs_used,
                self.reference_values_used_as_theorem_inputs,
                self.electron_neutrino_limit_used_as_derivation_input,
                self.w_mass_used_as_theorem_input,
                self.legacy_particle_tables_used_as_derivation_inputs,
            )
        ):
            raise ValueError("neutral radius/curvature closure cannot use empirical theorem inputs")


@dataclass(frozen=True)
class PropagationRadiusCandidate(EvidenceRecord):
    numeric_metres_available: bool
    symbolic_length_available: bool
    neutrino_specific: bool
    zero_propagation_consistent: bool


@dataclass(frozen=True)
class PropagationRadiusSearchResult(EvidenceRecord):
    candidates: tuple[PropagationRadiusCandidate, ...]
    numeric_metres_found: bool
    symbolic_candidate_found: bool


@dataclass(frozen=True)
class NeutralPhysicalCurvatureCandidate(EvidenceRecord):
    numeric_per_m2_available: bool
    symbolic_curvature_available: bool
    neutral_specific: bool


@dataclass(frozen=True)
class NeutralPhysicalCurvatureMap(EvidenceRecord):
    candidates: tuple[NeutralPhysicalCurvatureCandidate, ...]
    dimensionless_response_available: bool
    numeric_per_m2_found: bool
    symbolic_candidate_found: bool
    physical_unit_normalization_available: bool


@dataclass(frozen=True)
class BoundaryStiffnessCandidate(EvidenceRecord):
    numeric_energy_density_available: bool
    neutral_kernel_coupling_available: bool


@dataclass(frozen=True)
class TransportNormalizationCandidate(EvidenceRecord):
    dimensionless_transport_available: bool
    physical_transport_normalization_available: bool


@dataclass(frozen=True)
class NeutralRadiusCurvatureClosureResult(EvidenceRecord):
    radius: PropagationRadiusSearchResult
    curvature_map: NeutralPhysicalCurvatureMap
    boundary_stiffness: BoundaryStiffnessCandidate
    transport_normalization: TransportNormalizationCandidate
    symbolic_bridge_available: bool
    numeric_bridge_available: bool
    dimensional_consistency_passed: bool
    legacy_functional_output_dimension: str


@dataclass(frozen=True)
class DimensionfulNeutrinoMassCandidate(EvidenceRecord):
    radius_m: float | None
    curvature_per_m2: float | None
    dimensionful_mass_available: bool
    dimensionful_mass_kg: float | None
    dimensionful_mass_eV: float | None
    dimensionful_mass_GeV: float | None
    dimensional_consistency_passed: bool
    formula_output_dimension: str


def clean_provenance(paths: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "source_path": path,
            "empirical_derivation_input": False,
            "reference_theorem_input": False,
            "legacy_particle_table_input": False,
        }
        for path in paths
    )


def common_guard_fields() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "reference_values_used_as_theorem_inputs": False,
        "electron_neutrino_limit_used_as_derivation_input": False,
        "w_mass_used_as_theorem_input": False,
        "legacy_particle_tables_used_as_derivation_inputs": False,
    }

