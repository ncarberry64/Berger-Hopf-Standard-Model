"""Typed records for the BHSM neutral dimensionful-scale audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_TAXONOMY = (
    "ARTIFACT_BACKED_DIMENSIONFUL_SCALE",
    "CONDITIONAL_DIMENSIONFUL_SCALE_CANDIDATE",
    "DIMENSIONLESS_ONLY_CLOSURE",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "OPEN_MISSING_UNIT_ANCHOR",
    "OPEN_MISSING_THRESHOLD_TO_ENERGY_MAP",
    "OPEN_MISSING_BACKGROUND_ENERGY_DENSITY",
    "OPEN_MISSING_BOUNDARY_MEASURE",
    "OPEN_MISSING_TRANSPORT_NORMALIZATION",
    "FORBIDDEN_EMPIRICAL_SCALE",
    "INCONSISTENT_WITH_AUTHOR_ONTOLOGY",
)

SOURCE_CATEGORIES = (
    "DIMENSIONLESS_ARTIFACT",
    "DIMENSIONFUL_ARTIFACT",
    "AUTHOR_ONTOLOGY_CONDITIONAL",
    "REFERENCE_ONLY_FOR_COMPARISON",
    "EMPIRICAL_FORBIDDEN",
    "MISSING",
)


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NeutralScaleSource(Serializable):
    source_key: str
    source_path: str
    source_category: str
    discovered: bool
    machine_readable: bool
    neutral_scale_link_present: bool
    notes: str

    def __post_init__(self) -> None:
        if self.source_category not in SOURCE_CATEGORIES:
            raise ValueError(f"unsupported source category: {self.source_category}")


@dataclass(frozen=True)
class NeutralScaleCandidate(Serializable):
    candidate_key: str
    value: float | str | None
    unit: str | None
    dimension: str
    source: str
    status: str
    can_map_to_eV: bool
    requires_external_calibration: bool
    forbidden_reason: str | None
    neutral_kernel_link: str
    claim_boundary: str


@dataclass(frozen=True)
class BoundaryMeasureCandidate(Serializable):
    measure_symbol: str
    source: str
    status: str
    physical_dimension: str | None
    unit: str | None
    normalization_value: float | None
    couples_to_neutral_kernel: bool
    physical_normalization_available: bool
    background_energy_density_available: bool
    missing_object: str
    claim_boundary: str


@dataclass(frozen=True)
class ThresholdEnergyMap(Serializable):
    map_key: str
    formula: str
    status: str
    threshold_source: str
    energy_scale_source: str | None
    neutral_scale_eV: float | None
    neutral_scale_GeV: float | None
    unit_anchor_available: bool
    transport_normalization_available: bool
    missing_object: str
    claim_boundary: str


@dataclass(frozen=True)
class NeutralUnitMap(Serializable):
    dimensionless_response: float
    neutral_scale_eV: float | None
    neutral_scale_GeV: float | None
    effective_mass_eV: float | None
    effective_mass_GeV: float | None
    status: str
    unit_source: str | None
    claim_boundary: str


@dataclass(frozen=True)
class NeutralDimensionfulScaleResult(Serializable):
    theorem_key: str
    status_before: str
    status_after: str
    scale_candidate_key: str
    scale_value_dimensionless: float
    scale_value_eV: float | None
    scale_value_GeV: float | None
    unit_available: bool
    unit_source: str | None
    candidate_source: str
    artifact_sources_checked: tuple[str, ...]
    artifact_sources_used: tuple[str, ...]
    provenance: tuple[dict[str, Any], ...]
    empirical_derivation_inputs_used: bool
    reference_values_used_as_theorem_inputs: bool
    electron_neutrino_limit_used_as_derivation_input: bool
    w_mass_used_as_theorem_input: bool
    claim_boundary: str
    remaining_missing_object: str

    def __post_init__(self) -> None:
        if self.status_after not in STATUS_TAXONOMY:
            raise ValueError(f"unsupported neutral scale status: {self.status_after}")
        if any(
            (
                self.empirical_derivation_inputs_used,
                self.reference_values_used_as_theorem_inputs,
                self.electron_neutrino_limit_used_as_derivation_input,
                self.w_mass_used_as_theorem_input,
            )
        ):
            raise ValueError("neutral-scale theorem inputs cannot be empirical or calibrated")
        if self.unit_available != (self.scale_value_eV is not None and self.scale_value_GeV is not None):
            raise ValueError("unit availability must match the eV/GeV scale fields")


# Compatibility name used by the propagation evaluator contract.
NeutralScaleClosureResult = NeutralDimensionfulScaleResult


@dataclass(frozen=True)
class NeutralScaleClosureReport(Serializable):
    report_name: str
    version: str
    candidates: tuple[NeutralScaleCandidate, ...]
    boundary_measure: BoundaryMeasureCandidate
    threshold_energy_map: ThresholdEnergyMap
    scale_result: NeutralDimensionfulScaleResult
    dimensionful_mass_attempt: tuple[NeutralUnitMap, ...]
    neutrino_status_before: str
    neutrino_status_after: str
    dimensionful_scale_achieved: bool
    dimensionful_mass_output_produced: bool
    public_status: str
    frozen_predictions_changed: bool = False
    production_physics_model_logic_changed: bool = False
    internet_required: bool = False
    external_hep_tools_required: bool = False


def repository_path(repository: str | Path | None = None) -> Path:
    return Path(repository).resolve() if repository is not None else Path(__file__).resolve().parents[4]


def provenance_rows(root: Path, paths: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "source_path": path,
            "source_status": "DISCOVERED" if (root / path).is_file() else "MISSING",
            "empirical_derivation_input": False,
            "reference_theorem_input": False,
            "electron_neutrino_limit_derivation_input": False,
            "w_calibration_theorem_input": False,
        }
        for path in paths
    )
