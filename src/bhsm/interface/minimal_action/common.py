"""Typed records for the minimal BHSM action-closure audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_TAXONOMY = (
    "ESTABLISHED_ACTION_LEVEL",
    "CONDITIONAL_ACTION_THEOREM",
    "CONDITIONAL_PROPAGATION_THEOREM",
    "ACTION_LEVEL_RUNTIME_GATED",
    "ARTIFACT_BACKED",
    "DERIVED_REPRESENTATION_ONLY",
    "RETIRED_TARGET",
    "CANDIDATE",
    "OPEN_MISSING_ACTION_SOURCE",
    "OPEN_MISSING_FIELD_REPRESENTATION",
    "OPEN_MISSING_LORENTZ_STRUCTURE",
    "OPEN_MISSING_GAUGE_ADMISSIBILITY",
    "OPEN_MISSING_COUPLING_NORMALIZATION",
    "OPEN_MISSING_PHYSICAL_BASIS",
    "OPEN_MISSING_DIMENSIONAL_SCALE",
    "OPEN_MISSING_DIRAC_MAJORANA_CONVENTION",
    "FORBIDDEN_BY_ADMISSIBILITY",
    "INCONSISTENT_WITH_EXISTING_ARTIFACTS",
)

PROMOTED_STATUSES = {
    "ESTABLISHED_ACTION_LEVEL",
    "CONDITIONAL_ACTION_THEOREM",
    "CONDITIONAL_PROPAGATION_THEOREM",
    "ACTION_LEVEL_RUNTIME_GATED",
}


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MinimalActionTerm(Serializable):
    key: str
    symbol: str
    expression: str
    role: str
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class SectorProjectorDefinition(Serializable):
    key: str
    basis: tuple[str, ...]
    diagonal: tuple[int, ...]
    rank: int
    admissible_sector: str
    status: str
    source_artifacts: tuple[str, ...]
    claim_boundary: str


@dataclass(frozen=True)
class FieldRepresentation(Serializable):
    symbol: str
    domain: str
    codomain: str
    spin_lorentz_type: str
    gauge_representation: str
    chirality: str
    family_space: str
    conjugation_rule: str
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class LorentzStructure(Serializable):
    expression: str
    free_indices: tuple[str, ...]
    scalar_density: bool
    hermitian: bool
    cp_rule: str
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class GaugeAdmissibilityResult(Serializable):
    projector_key: str
    admissible_sectors: tuple[str, ...]
    excluded_sectors: tuple[str, ...]
    gauge_invariant: bool | None
    passes: bool
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class CouplingNormalization(Serializable):
    symbol: str
    normalization: str
    operator_mass_dimension: str
    coupling_mass_dimension: str
    value_source: str
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class ActionSourceTerm(Serializable):
    symbol: str
    expression: str
    integration_measure: str
    locality: str
    hermitian: bool
    action_derived: bool
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class VariationResult(Serializable):
    varied_field: str
    source_expression: str
    equation_or_current: str
    defined: bool
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str | None = None


@dataclass(frozen=True)
class ProductionRule(Serializable):
    expression: str
    callable_key: str
    callable_available: bool
    production_eligible: bool
    runtime_validation_required: bool
    status: str
    missing_object: str | None = None


@dataclass(frozen=True)
class MinimalActionClosureResult(Serializable):
    theorem_key: str
    status_before: str
    status_after: str
    promoted: bool
    promotion_reason: str
    action_term: MinimalActionTerm
    field_representation: FieldRepresentation
    lorentz_structure: LorentzStructure
    gauge_admissibility: GaugeAdmissibilityResult
    coupling_normalization: CouplingNormalization
    action_source_term: ActionSourceTerm
    variation_or_source_rule: VariationResult
    production_rule: ProductionRule
    callable_key: str
    artifact_sources_used: tuple[str, ...]
    provenance: tuple[dict[str, Any], ...]
    tests_passed: bool
    proof_gates: dict[str, bool]
    registry_updates: tuple[str, ...]
    remaining_missing_object: str | None
    claim_boundary: str
    empirical_derivation_inputs_used: bool = False
    reference_values_used_as_theorem_inputs: bool = False
    pdg_values_used_as_theorem_inputs: bool = False
    w_calibration_used_as_theorem_input: bool = False
    runtime_gates_changed: bool = False
    author_ontology_used: bool = False
    ontology_source: str | None = None
    core_blocker: bool = True
    target_disposition: str = "ACTIVE"
    numerical_closure_open: bool = False
    hep_runtime_readiness_claimed: bool = False

    def __post_init__(self) -> None:
        if self.status_after not in STATUS_TAXONOMY:
            raise ValueError(f"unsupported status: {self.status_after}")
        if self.promoted != (self.status_after in PROMOTED_STATUSES):
            raise ValueError("promotion flag must match action-level status")
        if self.promoted and (self.remaining_missing_object or not all(self.proof_gates.values())):
            raise ValueError("promotion requires all proof gates and no missing object")
        if not self.promoted and self.status_after.startswith("OPEN_") and not self.remaining_missing_object:
            raise ValueError("open theorem requires exactly one named missing object")


@dataclass(frozen=True)
class MinimalActionClosureReport(Serializable):
    action_symbol: str
    action_expression: str
    terms: tuple[MinimalActionTerm, ...]
    sector_projectors: tuple[SectorProjectorDefinition, ...]
    results: tuple[MinimalActionClosureResult, ...]
    status_taxonomy: tuple[str, ...] = STATUS_TAXONOMY
    report_name: str = "BHSM Minimal Action Closure Report"
    version: str = "0.8"
    public_status: str = "structural architecture integrated conditional; numerical closure open"
    internet_required: bool = False
    external_hep_tools_required: bool = False
    empirical_derivation_inputs_used: bool = False
    frozen_predictions_changed: bool = False
    production_physics_model_logic_changed: bool = False


def repository_path(repository: str | Path | None = None) -> Path:
    return Path(repository).resolve() if repository is not None else Path(__file__).resolve().parents[4]


def local_provenance(root: Path, paths: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "source_path": path,
            "source_status": "DISCOVERED" if (root / path).is_file() else "MISSING",
            "empirical_derivation_input": False,
            "reference_theorem_input": False,
            "calibration_theorem_input": False,
        }
        for path in paths
    )
