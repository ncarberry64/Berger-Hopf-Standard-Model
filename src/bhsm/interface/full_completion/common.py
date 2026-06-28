"""Data contracts for the BHSM full-completion audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


BLOCKER_CLASSES = (
    "ACTION_DERIVATION_BLOCKER",
    "NUMERICAL_NORMALIZATION_BLOCKER",
    "DIMENSIONFUL_UNIT_BLOCKER",
    "DOMAIN_POSITIVITY_BLOCKER",
    "RUNTIME_EXPORT_BLOCKER",
    "REFERENCE_COMPARISON_BLOCKER",
    "CLAIM_POLICY_BLOCKER",
    "DOCUMENTATION_BLOCKER",
    "REPRODUCIBILITY_BLOCKER",
    "ALREADY_CLOSED",
)

CLOSURE_STATUSES = (
    "ARTIFACT_BACKED",
    "CONDITIONAL",
    "OPEN_LOCALIZABLE",
    "OPEN_MISSING_THEOREM",
    "OPEN_MISSING_NUMERIC_NORMALIZATION",
    "OPEN_MISSING_UNIT_MAP",
    "RUNTIME_GATED",
    "REFERENCE_ONLY",
    "RETIRED_TARGET",
)


def repository_root(repository: str | Path | None = None) -> Path:
    return Path(repository).resolve() if repository is not None else Path(__file__).resolve().parents[4]


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


@dataclass(frozen=True)
class CompletionBlocker:
    blocker_id: str
    category_number: int
    sector: str
    title: str
    blocker_class: str
    current_status: str
    source_artifacts: tuple[str, ...]
    source_files: tuple[str, ...]
    why_it_blocks_full_completion: str
    what_would_close_it: str
    expected_difficulty: str
    risk_level: str
    can_be_attempted_now: bool
    requires_new_axiom_or_external_runtime: bool
    forbidden_shortcuts: tuple[str, ...]
    recommended_next_action: str

    def __post_init__(self) -> None:
        if self.blocker_class not in BLOCKER_CLASSES:
            raise ValueError(f"unsupported blocker class: {self.blocker_class}")
        if self.current_status not in CLOSURE_STATUSES:
            raise ValueError(f"unsupported closure status: {self.current_status}")

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class CompletionPriorityRow:
    target_id: str
    title: str
    linked_blockers: tuple[str, ...]
    necessity: int
    artifact_locality: int
    no_empirical_path: int
    cross_sector_leverage: int
    feasibility_now: int
    external_runtime_penalty: int
    total_score: int
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class BoundaryMeasureClosureResult:
    target_id: str
    status_before: str
    status_after: str
    closure_result: str
    selected_by_predeclared_score: bool
    source_search_complete: bool
    source_artifacts: tuple[str, ...]
    collar_jacobian_formula: str
    boundary_normalization_formula: str
    same_scale_transport_formula: str
    collar_shape_derived_conditionally: bool
    boundary_value_exact: bool
    same_scale_transport_exact: bool
    physical_measure_normalization_available: bool
    cross_scale_transport_available: bool
    physical_units_available: bool
    closed_subblockers: tuple[str, ...]
    remaining_subblockers: tuple[str, ...]
    empirical_inputs_used: bool
    official_prediction_logic_changed: bool
    frozen_predictions_changed: bool
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


@dataclass(frozen=True)
class FullCompletionStatusReport:
    report_name: str
    version: str
    full_completion_status: str
    blockers: tuple[CompletionBlocker, ...]
    priority_rows: tuple[CompletionPriorityRow, ...]
    selected_target: CompletionPriorityRow
    closure_attempt: BoundaryMeasureClosureResult
    completion_claimed: bool
    artifact_backed_count: int
    conditional_count: int
    open_count: int
    runtime_gated_count: int
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    empirical_inputs_used: bool
    internet_required: bool
    external_hep_tools_required: bool
    public_status: str
    required_statements: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))
