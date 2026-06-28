"""Neutral spectral-stiffness and mass-gap theorem interface."""

from .common import (
    AdmissiblePositivityProof,
    LegacyDimensionalGateResult,
    MassGapActionCandidate,
    NeutralCurvaturePenalty,
    NeutralKernelPositivityAudit,
    NeutralKernelExactAudit,
    NeutralAdmissibleDomain,
    NeutralPositivityCounterexample,
    NeutralPositivityReport,
    NeutralPositivityVerdict,
    NeutralQuadraticForm,
    NeutralKineticStiffness,
    NeutralSpectralGapCandidate,
    NeutralSpectralMassReport,
    NeutralStiffnessRatio,
    ProjectedNeutralKernel,
)
from .admissible_domain import derive_or_load_neutral_admissible_domain
from .legacy_dimensional_gate import audit_legacy_gravitational_mass_formula_dimensions
from .mass_gap_action import load_neutral_mass_gap_action
from .neutral_kernel_positivity import audit_neutral_kernel_positivity
from .neutral_quadratic_form import audit_neutral_kernel_exact, build_neutral_quadratic_form
from .neutral_spectral_gap import build_neutral_spectral_gap_candidate
from .spectral_report import (
    ARTIFACT_PATHS,
    PUBLIC_STATUS,
    REQUIRED_STATEMENTS,
    build_neutral_spectral_report,
    neutral_spectral_report_to_markdown,
    write_neutral_spectral_artifacts,
)
from .stiffness_ratio import search_neutral_stiffness_ratio
from .projected_kernel import build_projected_neutral_kernel
from .positivity_counterexample import search_admissible_positivity_counterexample
from .positivity_proof import prove_neutral_positivity_on_domain
from .positivity_report import (
    ARTIFACT_PATHS as POSITIVITY_ARTIFACT_PATHS,
    FINAL_STATUS as POSITIVITY_FINAL_STATUS,
    REQUIRED_STATEMENTS as POSITIVITY_REQUIRED_STATEMENTS,
    build_neutral_positivity_report,
    neutral_positivity_report_to_markdown,
    write_neutral_positivity_artifacts,
)

__all__ = [
    "ARTIFACT_PATHS",
    "POSITIVITY_ARTIFACT_PATHS",
    "POSITIVITY_FINAL_STATUS",
    "POSITIVITY_REQUIRED_STATEMENTS",
    "PUBLIC_STATUS",
    "REQUIRED_STATEMENTS",
    "LegacyDimensionalGateResult",
    "AdmissiblePositivityProof",
    "MassGapActionCandidate",
    "NeutralCurvaturePenalty",
    "NeutralKernelPositivityAudit",
    "NeutralKernelExactAudit",
    "NeutralAdmissibleDomain",
    "NeutralPositivityCounterexample",
    "NeutralPositivityReport",
    "NeutralPositivityVerdict",
    "NeutralQuadraticForm",
    "NeutralKineticStiffness",
    "NeutralSpectralGapCandidate",
    "NeutralSpectralMassReport",
    "NeutralStiffnessRatio",
    "ProjectedNeutralKernel",
    "audit_legacy_gravitational_mass_formula_dimensions",
    "audit_neutral_kernel_positivity",
    "audit_neutral_kernel_exact",
    "build_neutral_quadratic_form",
    "build_neutral_spectral_gap_candidate",
    "build_neutral_spectral_report",
    "build_neutral_positivity_report",
    "build_projected_neutral_kernel",
    "derive_or_load_neutral_admissible_domain",
    "load_neutral_mass_gap_action",
    "neutral_spectral_report_to_markdown",
    "neutral_positivity_report_to_markdown",
    "prove_neutral_positivity_on_domain",
    "search_admissible_positivity_counterexample",
    "search_neutral_stiffness_ratio",
    "write_neutral_spectral_artifacts",
    "write_neutral_positivity_artifacts",
]
