"""Data contracts and exact arithmetic for the BHSM common-16 audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


def repository_root(repository: str | Path | None = None) -> Path:
    return Path(repository).resolve() if repository is not None else Path(__file__).resolve().parents[4]


def _ready(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
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
class TargetScore(Serializable):
    target_id: str
    required_for_completion: int
    local_artifacts: int
    closes_multiple_blockers: int
    no_empirical_inputs: int
    reviewer_credibility: int
    deterministic_tests: int
    missing_units_penalty: int
    external_runtime_penalty: int
    frozen_change_risk_penalty: int
    total_score: int
    rationale: str


@dataclass(frozen=True)
class TargetSelection(Serializable):
    candidate_targets: tuple[TargetScore, ...]
    scores: dict[str, int]
    selected_target: str
    why_selected: str
    why_others_not_selected: dict[str, str]
    expected_closure_statuses: tuple[str, ...]
    empirical_inputs_used: bool


@dataclass(frozen=True)
class Common16SourceSearch(Serializable):
    status: str
    source_paths: tuple[str, ...]
    source_paths_found: tuple[str, ...]
    source_paths_missing: tuple[str, ...]
    omega_values: dict[str, int]
    rho_ch_candidate: int
    bridge_value: str
    ckm_candidate_exponent: str
    historical_candidate_selected_by_residual: bool
    empirical_residual_used_as_theorem_input: bool
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool


@dataclass(frozen=True)
class Common16IncidenceAudit(Serializable):
    status: str
    omega_values: dict[str, int]
    rho_ch: int
    sector_weights: dict[str, int]
    charged_weight_sum: int
    projector_fractions: dict[str, Fraction]
    n_16: int
    epsilon_ckm_candidate: Fraction
    identities_exact: bool
    omega_source_status: str
    rho_ch_source_status: str
    assumptions: tuple[str, ...]
    claim_boundary: str


@dataclass(frozen=True)
class Common16BridgeBetaAudit(Serializable):
    status: str
    common_16_bridge_formula: str
    incidence_overlap_bridge_formula: str
    common_16_bridge_value: Fraction
    incidence_overlap_bridge_value: Fraction
    bridge_identity_exact: bool
    beta_values: dict[str, Fraction]
    expected_beta_values: dict[str, Fraction]
    beta_identities_exact: bool
    bridge_source_status: str
    common_generator_artifact_backed: bool
    claim_boundary: str


@dataclass(frozen=True)
class CKMTransportAudit(Serializable):
    status: str
    candidate_status: str
    n_16: int
    reciprocal_weight: Fraction
    historical_candidate_selected_by_residual: bool
    residual_used_as_theorem_input: bool
    same_scale_identity_transport_available: bool
    reciprocal_log_transport_theorem_available: bool
    cross_scale_transport_available: bool
    remaining_missing_object: str
    claim_boundary: str


@dataclass(frozen=True)
class Common16ProvenanceAudit(Serializable):
    status: str
    omega_f_source_status: str
    rho_ch_source_status: str
    n_16_source_status: str
    bridge_beta_source_status: str
    ckm_reciprocal_transport_status: str
    ckm_exponent_final_status: str
    fallback_target: str
    fallback_result: str
    artifact_backed_closures: tuple[str, ...]
    conditional_closures: tuple[str, ...]
    open_blockers: tuple[str, ...]
    retired_or_rejected_hypotheses: tuple[str, ...]


@dataclass(frozen=True)
class FinalCompletionReport(Serializable):
    report_name: str
    version: str
    public_status: str
    target_selection: TargetSelection
    source_search: Common16SourceSearch
    incidence: Common16IncidenceAudit
    bridge_beta: Common16BridgeBetaAudit
    ckm_transport: CKMTransportAudit
    provenance: Common16ProvenanceAudit
    closure_result: str
    status_before: str
    status_after: str
    completion_claimed: bool
    empirical_inputs_used: bool
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    required_statements: tuple[str, ...]
