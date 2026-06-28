"""Typed records and guard fields for neutral spectral-stiffness closure."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


SPECTRAL_STATUSES = (
    "ARTIFACT_BACKED_MASS_GAP_ACTION",
    "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE",
    "ARTIFACT_BACKED_NEUTRAL_STIFFNESS_RATIO",
    "CONDITIONAL_NEUTRAL_STIFFNESS_RATIO_CANDIDATE",
    "OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS",
    "OPEN_MISSING_NEUTRAL_CURVATURE_PENALTY",
    "OPEN_MISSING_NUMERIC_STIFFNESS_RATIO",
    "OPEN_MISSING_PHYSICAL_K_NEUTRAL_MAP",
    "OPEN_MISSING_ADMISSIBLE_NEUTRAL_POSITIVITY_PROOF",
    "LEGACY_GRAVITATIONAL_STIFFNESS_ANSATZ",
    "DIMENSIONALLY_GATED_LEGACY_FUNCTIONAL",
    "DIMENSIONFUL_MASS_NOT_AVAILABLE",
    "FORBIDDEN_EMPIRICAL_STIFFNESS",
    "INCONSISTENT_WITH_AUTHOR_ONTOLOGY",
    "RAW_KERNEL_NOT_POSITIVE_SEMIDEFINITE",
    "RAW_KERNEL_POSITIVE_SEMIDEFINITE",
    "ARTIFACT_BACKED_ADMISSIBLE_NEUTRAL_POSITIVITY",
)


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpectralEvidence(Serializable):
    candidate_key: str
    status: str
    value: float | str | None
    unit: str | None
    dimension: str
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
    legacy_gravitational_formula_used_as_mass_formula: bool
    claim_boundary: str
    remaining_missing_object: str

    def __post_init__(self) -> None:
        if self.status not in SPECTRAL_STATUSES:
            raise ValueError(f"unsupported neutral spectral status: {self.status}")
        if any(
            (
                self.empirical_derivation_inputs_used,
                self.reference_values_used_as_theorem_inputs,
                self.electron_neutrino_limit_used_as_derivation_input,
                self.w_mass_used_as_theorem_input,
                self.legacy_particle_tables_used_as_derivation_inputs,
                self.legacy_gravitational_formula_used_as_mass_formula,
            )
        ):
            raise ValueError("neutral spectral closure cannot use forbidden theorem inputs")


@dataclass(frozen=True)
class MassGapActionCandidate(SpectralEvidence):
    scalar_action_artifact_backed: bool
    neutral_action_generalization_conditional: bool
    action_density: str
    spectral_gap_formula: str


@dataclass(frozen=True)
class NeutralKineticStiffness(SpectralEvidence):
    symbolic_available: bool
    numeric_available: bool


@dataclass(frozen=True)
class NeutralCurvaturePenalty(SpectralEvidence):
    symbolic_available: bool
    numeric_available: bool


@dataclass(frozen=True)
class NeutralStiffnessRatio(SpectralEvidence):
    kinetic_stiffness: NeutralKineticStiffness
    curvature_penalty: NeutralCurvaturePenalty
    symbolic_ratio_available: bool
    numeric_length_available: bool
    stiffness_length_m: float | None


@dataclass(frozen=True)
class NeutralSpectralGapCandidate(SpectralEvidence):
    stiffness_ratio: NeutralStiffnessRatio
    curvature_numeric_per_m2: bool
    inverse_length_gap_available: bool
    inverse_length_gap_per_m: float | None
    dimensionful_mass_available: bool
    dimensionful_mass_kg: float | None
    dimensionful_mass_eV: float | None
    dimensionful_mass_GeV: float | None
    zero_propagation_mass_vanishes: bool


@dataclass(frozen=True)
class NeutralKernelPositivityAudit(SpectralEvidence):
    raw_eigenvalues: tuple[float, ...]
    raw_positive_semidefinite: bool
    projected_response_nonnegative_by_definition: bool
    admissible_positive_response_proven: bool


@dataclass(frozen=True)
class LegacyDimensionalGateResult(SpectralEvidence):
    curvature_dimension: str
    radius_squared_curvature_dimension: str
    prefactor_dimension: str
    formula_output_dimension: str
    physical_mass_dimension_passed: bool
    numeric_particle_mass_output_allowed: bool


@dataclass(frozen=True)
class NeutralSpectralMassReport(Serializable):
    report_name: str
    version: str
    public_status: str
    mass_gap_action: MassGapActionCandidate
    legacy_dimensional_gate: LegacyDimensionalGateResult
    stiffness_ratio: NeutralStiffnessRatio
    spectral_gap: NeutralSpectralGapCandidate
    kernel_positivity: NeutralKernelPositivityAudit
    dimensionful_mass_available: bool
    remaining_missing_object: str
    frozen_predictions_changed: bool
    production_physics_model_logic_changed: bool
    empirical_derivation_inputs_used: bool
    internet_required: bool
    external_hep_tools_required: bool
    libreoffice_required: bool


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


def guard_fields() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "reference_values_used_as_theorem_inputs": False,
        "electron_neutrino_limit_used_as_derivation_input": False,
        "w_mass_used_as_theorem_input": False,
        "legacy_particle_tables_used_as_derivation_inputs": False,
        "legacy_gravitational_formula_used_as_mass_formula": False,
    }
