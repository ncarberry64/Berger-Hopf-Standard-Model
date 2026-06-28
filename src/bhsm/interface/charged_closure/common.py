"""Data contracts for the BHSM charged-sector closure audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def repository_root(repository: str | Path | None = None) -> Path:
    return Path(repository).resolve() if repository is not None else Path(__file__).resolve().parents[4]


def _ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_ready(item) for item in value]
    if isinstance(value, list):
        return [_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _ready(item) for key, item in value.items()}
    return value


class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return _ready(asdict(self))


@dataclass(frozen=True)
class ChargedSourceSearchResult(Serializable):
    status: str
    source_paths: tuple[str, ...]
    sources_found: tuple[str, ...]
    sources_missing: tuple[str, ...]
    artifact_backed_values_found: tuple[str, ...]
    conditional_sources_found: tuple[str, ...]
    open_sources: tuple[str, ...]
    empirical_inputs_used: bool
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    claim_boundary: str


@dataclass(frozen=True)
class ChargedActionStiffnessResult(Serializable):
    status: str
    action_form: str
    projector_coefficients: dict[str, str]
    charged_coefficients: dict[str, dict[str, str]]
    g_bridge: str
    g_bridge_status: str
    rho_definition: str
    rho_ch_1_status: str
    rho_ch_3_status: str
    rho_ch_selected: str | None
    action_normalization_status: str
    kinetic_stiffness_status: str
    curvature_penalty_status: str
    numeric_stiffness_status: str
    charged_hessian_source_status: str
    dimensional_status: str
    source_artifacts: tuple[str, ...]
    empirical_inputs_used: bool
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    claim_boundary: str


@dataclass(frozen=True)
class EtaLSourceResult(Serializable):
    status: str
    preferred_conditional_formula: str
    fitted_eta_present_in_history: bool
    fitted_eta_used_as_theorem_input: bool
    boundary_projection_status: str
    stochastic_strength_status: str
    action_source_status: str
    transport_normalization_status: str
    exact_value_derived: bool
    source_artifacts: tuple[str, ...]
    empirical_inputs_used: bool
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    remaining_missing_objects: tuple[str, ...]
    claim_boundary: str


@dataclass(frozen=True)
class CKMExponentSourceResult(Serializable):
    status: str
    exponent: str
    candidate_label: str
    historical_candidate_selected_by_residual: bool
    residual_used_as_theorem_input: bool
    action_source_found: bool
    projector_source_found: bool
    cross_scale_transport_status: str
    source_artifacts: tuple[str, ...]
    empirical_inputs_used: bool
    frozen_ckm_changed: bool
    official_prediction_logic_changed: bool
    remaining_missing_object: str
    claim_boundary: str


@dataclass(frozen=True)
class ChargedMixingLawResult(Serializable):
    status: str
    theta12_formula: str
    theta23_formula: str
    theta13_formula: str
    delta_formula: str
    theta12_source_status: str
    theta23_source_status: str
    theta13_source_status: str
    delta_source_status: str
    mixing_law_source_status: str
    source_artifacts: tuple[str, ...]
    empirical_inputs_used: bool
    frozen_ckm_changed: bool
    official_prediction_logic_changed: bool
    remaining_missing_object: str
    claim_boundary: str


@dataclass(frozen=True)
class ChargedDimensionalAuditResult(Serializable):
    status: str
    coefficient_dimensions: dict[str, str]
    formulas_checked: tuple[str, ...]
    inconsistent_formulas: tuple[str, ...]
    physical_stiffness_claim_allowed: bool
    physical_mass_claim_allowed: bool
    empirical_inputs_used: bool
    claim_boundary: str


@dataclass(frozen=True)
class ChargedClosureReport(Serializable):
    report_name: str
    version: str
    public_status: str
    source_search: ChargedSourceSearchResult
    action_stiffness: ChargedActionStiffnessResult
    eta_l: EtaLSourceResult
    ckm_exponent: CKMExponentSourceResult
    mixing_law: ChargedMixingLawResult
    dimensional_audit: ChargedDimensionalAuditResult
    closure_result: str
    status_before: str
    status_after: str
    remaining_blockers: tuple[str, ...]
    completion_claimed: bool
    empirical_inputs_used: bool
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    required_statements: tuple[str, ...]
