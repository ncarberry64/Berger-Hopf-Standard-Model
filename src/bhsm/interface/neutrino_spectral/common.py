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
    "ARTIFACT_BACKED_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY",
    "CONDITIONAL_ADMISSIBLE_NEUTRAL_POSITIVITY_CANDIDATE",
    "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE",
    "THRESHOLDED_RESPONSE_ONLY_NO_POSITIVITY_PROOF",
    "ADMISSIBLE_POSITIVITY_COUNTEREXAMPLE_FOUND",
    "OPEN_MISSING_ADMISSIBLE_NEUTRAL_DOMAIN",
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
    admissible_positivity_status: str
    dimensionful_mass_available: bool
    remaining_missing_object: str
    frozen_predictions_changed: bool
    production_physics_model_logic_changed: bool
    empirical_derivation_inputs_used: bool
    internet_required: bool
    external_hep_tools_required: bool
    libreoffice_required: bool


@dataclass(frozen=True)
class NeutralPositivityRecord(Serializable):
    candidate_key: str
    status: str
    kernel_matrix_exact: tuple[tuple[str, ...], ...]
    kernel_matrix_numeric: tuple[tuple[float, ...], ...]
    characteristic_polynomial: str
    raw_eigenvalues_exact: tuple[str, ...]
    raw_eigenvalues_numeric: tuple[float, ...]
    raw_psd: bool
    negative_eigendirection: tuple[float, ...] | None
    admissible_domain_defined: bool
    admissible_domain_constraints: tuple[str, ...]
    projection_matrix: tuple[tuple[float, ...], ...] | None
    projected_kernel: tuple[tuple[float, ...], ...] | None
    projected_eigenvalues: tuple[float, ...]
    projected_psd: bool | None
    quadratic_form: str
    minimum_on_admissible_domain: float | str | None
    counterexample: dict[str, Any] | None
    thresholding_used: bool
    positivity_proven_without_thresholding: bool
    counterexample_found: bool
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
            raise ValueError(f"unsupported neutral positivity status: {self.status}")
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
            raise ValueError("neutral positivity cannot use empirical theorem inputs")


@dataclass(frozen=True)
class NeutralKernelExactAudit(NeutralPositivityRecord):
    source_artifact: str


@dataclass(frozen=True)
class NeutralAdmissibleDomain(NeutralPositivityRecord):
    coordinate_interpretation: str
    ontology_sources: tuple[str, ...]
    action_derived: bool


@dataclass(frozen=True)
class NeutralQuadraticForm(NeutralPositivityRecord):
    termwise_nonnegative_on_domain: bool


@dataclass(frozen=True)
class ProjectedNeutralKernel(NeutralPositivityRecord):
    restriction_kind: str


@dataclass(frozen=True)
class AdmissiblePositivityProof(NeutralPositivityRecord):
    proof_method: str
    proof_steps: tuple[str, ...]


@dataclass(frozen=True)
class NeutralPositivityCounterexample(NeutralPositivityRecord):
    search_method: str


@dataclass(frozen=True)
class NeutralPositivityVerdict(NeutralPositivityRecord):
    domain_artifact_backed: bool
    domain_ontology_conditional: bool


@dataclass(frozen=True)
class NeutralPositivityReport(NeutralPositivityRecord):
    exact_audit: NeutralKernelExactAudit
    domain: NeutralAdmissibleDomain
    projected: ProjectedNeutralKernel
    proof: AdmissiblePositivityProof
    counterexample_search: NeutralPositivityCounterexample
    verdict: NeutralPositivityVerdict
    public_status: str
    frozen_predictions_changed: bool
    production_physics_model_logic_changed: bool
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
