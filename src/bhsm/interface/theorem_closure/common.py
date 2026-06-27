"""Shared data model for executable BHSM theorem-closure attempts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

CLOSURE_STATUSES = (
    "CLOSED_DERIVED_ACTION_LEVEL",
    "DERIVED_CONDITIONAL_AUTHOR_AXIOM",
    "PARTIAL_LOCALIZABLE",
    "OPEN_EXACT_MISSING_THEOREM",
    "OPEN_MISSING_DIMENSIONFUL_SCALE",
    "OPEN_MISSING_PHYSICAL_BASIS",
    "OPEN_MISSING_INTERACTION_ATTACHMENT",
    "OPEN_MISSING_ACTION_SOURCE",
    "FORBIDDEN_UNSUPPORTED",
    "CALLABLE_NOT_AVAILABLE",
    "ARTIFACT_NOT_FOUND",
)


@dataclass(frozen=True)
class TheoremStatement:
    theorem_key: str
    statement: str
    assumptions: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class OperatorDefinition:
    name: str
    domain: str
    codomain: str
    expression: str
    status: str


@dataclass(frozen=True)
class ActionTermCandidate:
    symbol: str
    expression: str
    source_status: str
    source_artifacts: tuple[str, ...]
    missing_objects: tuple[str, ...]


@dataclass(frozen=True)
class CallableTheorem:
    callable_key: str
    callable_path: str | None
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    available: bool


@dataclass(frozen=True)
class ProofGateResult:
    gate_id: str
    name: str
    required: bool
    passes: bool
    evidence: str
    limitations: str


@dataclass(frozen=True)
class TheoremClosureResult:
    theorem_key: str
    display_name: str
    closure_status: str
    proof_gates: tuple[ProofGateResult, ...]
    formal_statement: TheoremStatement
    domain: str
    codomain: str
    operator_definition: OperatorDefinition
    action_term: ActionTermCandidate
    callable_key: str
    callable_available: bool
    artifact_sources: tuple[str, ...]
    provenance: tuple[dict[str, Any], ...]
    empirical_derivation_inputs_used: bool
    reference_values_used_as_derivation_inputs: bool
    calibration_inputs_used: bool
    registry_entries_affected: tuple[str, ...]
    status_before: str
    status_after: str
    promotion_allowed: bool
    promotion_reason: str
    missing_objects: tuple[str, ...]
    claim_boundary: str
    warnings: tuple[str, ...]
    notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.closure_status not in CLOSURE_STATUSES:
            raise ValueError(f"unsupported closure status: {self.closure_status}")
        if self.promotion_allowed and self.closure_status != "CLOSED_DERIVED_ACTION_LEVEL":
            raise ValueError("promotion requires CLOSED_DERIVED_ACTION_LEVEL")
        if self.closure_status == "CLOSED_DERIVED_ACTION_LEVEL" and not self.promotion_allowed:
            raise ValueError("closed action-level theorem must permit promotion")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def failed_required_gates(self) -> tuple[str, ...]:
        return tuple(gate.gate_id for gate in self.proof_gates if gate.required and not gate.passes)


@dataclass(frozen=True)
class TheoremClosureReport:
    results: tuple[TheoremClosureResult, ...]
    report_name: str = "BHSM Theorem Closure Sprint A Report"
    version: str = "0.4"
    public_status: str = "Executable closure attempts added; all unsupported theorem promotions remain blocked."

    def to_dict(self) -> dict[str, Any]:
        rows = [result.to_dict() for result in self.results]
        return {
            "report_name": self.report_name,
            "version": self.version,
            "public_status": self.public_status,
            "results": rows,
            "promotions_allowed": [result.theorem_key for result in self.results if result.promotion_allowed],
            "open_theorems": [result.theorem_key for result in self.results if not result.promotion_allowed],
            "empirical_derivation_inputs_used": any(result.empirical_derivation_inputs_used for result in self.results),
            "reference_values_used_as_derivation_inputs": any(result.reference_values_used_as_derivation_inputs for result in self.results),
            "calibration_inputs_used": any(result.calibration_inputs_used for result in self.results),
            "internet_required": False,
        }
