"""Typed records for the BHSM neutrino propagation-mass closure candidate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_TAXONOMY = (
    "ESTABLISHED_ARTIFACT_BACKED",
    "CONDITIONAL_PROPAGATION_THEOREM",
    "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE",
    "NUMERICAL_CLOSURE_CANDIDATE",
    "OPEN_MISSING_PROPAGATION_MAP",
    "OPEN_MISSING_CURVATURE_THRESHOLD",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "OPEN_MISSING_OBSERVABLE_MAP",
    "OPEN_MISSING_ORDERING_POLICY",
    "OPEN_MISSING_DIRAC_MAJORANA_CONVENTION",
    "FORBIDDEN_STATIC_REST_MASS_FRAMING",
    "INCONSISTENT_WITH_AUTHOR_ONTOLOGY",
)


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NeutralBoundaryField(Serializable):
    symbol: str
    basis: tuple[str, ...]
    mode_labels: tuple[tuple[int, int], ...]
    interpretation: str
    status: str
    source_artifacts: tuple[str, ...]


@dataclass(frozen=True)
class NeutralKernelArtifact(Serializable):
    matrix: tuple[tuple[float, ...], ...]
    eta_nu: float
    g_nu: float
    beta_nu: float
    kappa_nu: float
    mode_labels: tuple[tuple[int, int], ...]
    status: str
    source_artifact: str
    empirical_derivation_inputs_used: bool = False


@dataclass(frozen=True)
class PropagationState(Serializable):
    label: str
    amplitudes: tuple[float, ...]
    propagation_response: float
    stopped: bool
    status: str
    claim_boundary: str


@dataclass(frozen=True)
class CurvatureThreshold(Serializable):
    value: float
    symbol: str
    response_law: str
    interpretation: str
    status: str
    source_artifacts: tuple[str, ...]


@dataclass(frozen=True)
class BackgroundCoupling(Serializable):
    value: float
    symbol: str
    status: str
    source_artifact: str


@dataclass(frozen=True)
class NeutralScaleLaw(Serializable):
    dimensionless_scale: float
    scale_symbol: str
    effective_mass_eV_per_unit: float | None
    effective_mass_GeV_per_unit: float | None
    status: str
    source_artifacts: tuple[str, ...]
    missing_object: str
    claim_boundary: str


@dataclass(frozen=True)
class EffectivePropagationMass(Serializable):
    state_label: str
    propagation_response: float
    kernel_response_norm: float
    coupled_response: float
    threshold_excess: float
    effective_mass_dimensionless: float
    effective_mass_eV: float | None
    effective_mass_GeV: float | None
    status: str
    provenance: tuple[dict[str, Any], ...]
    claim_boundary: str


@dataclass(frozen=True)
class NeutrinoObservableMap(Serializable):
    effective_propagation_mass: str
    oscillation_sensitive_mass_differences: str
    electron_neutrino_effective_mass_comparison: str
    cosmological_mass_sum_comparison: str
    static_rest_mass_interpretation: str
    ordering_policy: str
    dirac_majorana_policy: str
    status: str
    claim_boundary: str


@dataclass(frozen=True)
class NeutrinoPropagationClosureResult(Serializable):
    theorem_key: str
    status_before: str
    status_after: str
    promoted: bool
    promotion_reason: str
    neutral_kernel: NeutralKernelArtifact
    propagation_state: tuple[PropagationState, ...]
    curvature_threshold: CurvatureThreshold
    background_coupling: BackgroundCoupling
    scale_law: NeutralScaleLaw
    effective_mass_formula: str
    observable_map: NeutrinoObservableMap
    ordering_policy: str
    dirac_majorana_policy: str
    upper_limit_comparison_policy: str
    artifact_sources_used: tuple[str, ...]
    provenance: tuple[dict[str, Any], ...]
    tests_passed: bool
    registry_updates: tuple[str, ...]
    remaining_missing_object: str | None
    claim_boundary: str
    empirical_derivation_inputs_used: bool = False
    reference_values_used_as_theorem_inputs: bool = False
    electron_neutrino_upper_limit_used_as_derivation_input: bool = False
    w_mass_used_as_theorem_input: bool = False
    frozen_predictions_changed: bool = False
    production_physics_model_logic_changed: bool = False
    internet_required: bool = False
    external_hep_tools_required: bool = False

    def __post_init__(self) -> None:
        if self.status_after not in STATUS_TAXONOMY:
            raise ValueError(f"unsupported neutrino closure status: {self.status_after}")
        forbidden_inputs = (
            self.empirical_derivation_inputs_used,
            self.reference_values_used_as_theorem_inputs,
            self.electron_neutrino_upper_limit_used_as_derivation_input,
            self.w_mass_used_as_theorem_input,
        )
        if any(forbidden_inputs):
            raise ValueError("neutrino closure cannot use empirical or calibration theorem inputs")


@dataclass(frozen=True)
class NeutrinoNumericalClosureReport(Serializable):
    closure: NeutrinoPropagationClosureResult
    field: NeutralBoundaryField
    channel_results: tuple[EffectivePropagationMass, ...]
    report_name: str = "BHSM Neutrino Propagation-Mass Numerical Closure"
    version: str = "0.9"
    public_status: str = "structural architecture integrated conditional; numerical closure open"
    numerical_closure: str = "dimensionless-only"
    frozen_predictions_changed: bool = False
    official_predictions_changed: bool = False
    empirical_validation_claimed: bool = False


def repository_path(repository: str | Path | None = None) -> Path:
    return Path(repository).resolve() if repository is not None else Path(__file__).resolve().parents[4]


def provenance_rows(root: Path, paths: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "source_path": path,
            "source_status": "DISCOVERED" if (root / path).is_file() else "MISSING",
            "empirical_derivation_input": False,
            "reference_theorem_input": False,
            "w_calibration_theorem_input": False,
        }
        for path in paths
    )
