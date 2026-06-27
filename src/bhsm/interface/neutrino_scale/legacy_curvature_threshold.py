"""Typed records for the BHSM legacy curvature-threshold scale audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


LEGACY_STATUSES = (
    "ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL",
    "CONDITIONAL_DIMENSIONFUL_SCALE_CANDIDATE",
    "LEGACY_THEORY_SCALE_CANDIDATE",
    "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS",
    "OPEN_MISSING_NEUTRAL_CURVATURE_MAPPING",
    "OPEN_MISSING_UNIT_ANCHOR",
    "OPEN_MISSING_BOUNDARY_MEASURE",
    "FORBIDDEN_EMPIRICAL_SCALE",
)


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LegacyCurvatureArtifact(Serializable):
    artifact_key: str
    source_file: str
    source_document_title: str
    recognized_formulas: tuple[str, ...]
    candidate_status: str
    use_allowed_for_theory: bool
    use_allowed_for_empirical_calibration: bool
    sha256: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class CurvatureMassFunctional(Serializable):
    artifact_key: str
    source_file: str
    source_document_title: str
    source_equation: str
    mass_formula: str
    energy_formula: str
    candidate_status: str
    physical_dimensions: tuple[str, ...]
    action_derived: bool
    matching_ansatz_disclosed: bool
    claim_boundary: str


@dataclass(frozen=True)
class CurvatureActivation(Serializable):
    curvature_operator: str
    effective_local_curvature: str
    activation_number: str
    single_activation_normalization: str
    stability_conditions: tuple[str, ...]
    source_file: str
    candidate_status: str


@dataclass(frozen=True)
class PropagationLocalizationRadius(Serializable):
    symbol: str
    status: str
    value_m: float | None
    source_file: str | None
    candidates_checked: tuple[str, ...]
    empirical_radius_rejected: bool
    claim_boundary: str
    remaining_missing_object: str


@dataclass(frozen=True)
class NeutralCurvatureMapping(Serializable):
    mapping_formula: str
    status: str
    dimensionless_curvature_response_available: bool
    physical_curvature_units_available: bool
    curvature_value_per_m2: float | None
    source_artifacts: tuple[str, ...]
    claim_boundary: str
    remaining_missing_object: str


@dataclass(frozen=True)
class LegacyNeutralScaleCandidate(Serializable):
    candidate_key: str
    candidate_status: str
    mass_functional_available: bool
    propagation_radius_available: bool
    neutral_curvature_mapping_available: bool
    physical_curvature_units_available: bool
    dimensionful_mass_possible: bool
    dimensionful_mass_eV: float | None
    dimensionful_mass_GeV: float | None
    claim_boundary: str
    remaining_missing_object: str


@dataclass(frozen=True)
class LegacyCurvatureScaleResult(Serializable):
    artifact_key: str
    source_file: str
    source_document_title: str
    source_equation: str
    extracted_formula: str
    candidate_status: str
    mass_functional_available: bool
    curvature_operator_available: bool
    activation_number_available: bool
    mass_gap_action_available: bool
    propagation_radius_available: bool
    neutral_curvature_mapping_available: bool
    dimensionful_mass_possible: bool
    dimensionful_mass_eV: float | None
    dimensionful_mass_GeV: float | None
    empirical_derivation_inputs_used: bool
    reference_values_used_as_theorem_inputs: bool
    electron_neutrino_limit_used_as_derivation_input: bool
    w_mass_used_as_theorem_input: bool
    claim_boundary: str
    remaining_missing_object: str

    def __post_init__(self) -> None:
        if self.candidate_status not in LEGACY_STATUSES:
            raise ValueError(f"unsupported legacy scale status: {self.candidate_status}")
        if any(
            (
                self.empirical_derivation_inputs_used,
                self.reference_values_used_as_theorem_inputs,
                self.electron_neutrino_limit_used_as_derivation_input,
                self.w_mass_used_as_theorem_input,
            )
        ):
            raise ValueError("legacy neutral-scale theorem inputs cannot be empirical")
        if not self.dimensionful_mass_possible and (
            self.dimensionful_mass_eV is not None or self.dimensionful_mass_GeV is not None
        ):
            raise ValueError("dimensionful mass output requires all scale ingredients")


@dataclass(frozen=True)
class LegacyCurvatureScaleReport(Serializable):
    report_name: str
    version: str
    artifacts: tuple[LegacyCurvatureArtifact, ...]
    curvature_mass_functional: CurvatureMassFunctional
    curvature_activation: CurvatureActivation
    propagation_radius: PropagationLocalizationRadius
    neutral_curvature_mapping: NeutralCurvatureMapping
    scale_candidate: LegacyNeutralScaleCandidate
    result: LegacyCurvatureScaleResult
    mass_gap_action_support: str
    hyperspherical_action_support: str
    legacy_particle_tables_used_as_derivation_inputs: bool
    frozen_predictions_changed: bool
    production_physics_model_logic_changed: bool
    internet_required: bool
    external_hep_tools_required: bool
    public_status: str

