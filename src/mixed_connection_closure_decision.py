"""BHSM v2.11 closure decision for the mixed connection coefficients."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from clifford_curvature_contraction import CLIFFORD_CONTRACTION_OPEN, build_clifford_curvature_contraction_report
from mixed_connection_coefficients import MIXED_COEFFICIENT_OPEN, build_mixed_connection_coefficients_report
from mixed_connection_remainder_bound import build_mixed_connection_remainder_bound_report
from mixed_curvature_contraction import MIXED_CURVATURE_OPEN, build_mixed_curvature_contraction_report
from mixed_coefficient_rule_decision import build_mixed_coefficient_rule_decision


MIXED_CONNECTION_CLOSED = "MIXED_CONNECTION_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"

MIXED_CONNECTION_ZERO = "MIXED_CONNECTION_ZERO"
MIXED_CONNECTION_REPRESENTED_BY_EXISTING_TERM = "MIXED_CONNECTION_REPRESENTED_BY_EXISTING_TERM"
MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR = "MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"
MIXED_CONNECTION_PSD_PROFILE_CONTROLLED = "MIXED_CONNECTION_PSD_PROFILE_CONTROLLED"
MIXED_CONNECTION_SCREENED_OR_LIFTED = "MIXED_CONNECTION_SCREENED_OR_LIFTED"
MIXED_CONNECTION_RELATIVELY_BOUNDED_SAFE = "MIXED_CONNECTION_RELATIVELY_BOUNDED_SAFE"
MIXED_CONNECTION_REAL_MISSING_TERM_SAFE_AFTER_REAUDIT = "MIXED_CONNECTION_REAL_MISSING_TERM_SAFE_AFTER_REAUDIT"
MIXED_CONNECTION_REAL_MISSING_TERM_BREAKS_HT = "MIXED_CONNECTION_REAL_MISSING_TERM_BREAKS_HT"
MIXED_CONNECTION_OPEN = "MIXED_CONNECTION_OPEN"


@dataclass(frozen=True)
class MixedConnectionClosureDecision:
    title: str
    final_result: str
    mixed_connection_classification: str
    coefficient_status: str
    curvature_status: str
    clifford_status: str
    exact_remaining_gap: str
    exact_missing_rule: str
    recommended_next_branch: str
    recommended_target_theorem: str
    complete_operator_identification_status: str
    final_paper_allowed: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_mixed_connection_closure_decision() -> MixedConnectionClosureDecision:
    coeffs = build_mixed_connection_coefficients_report()
    curvature = build_mixed_curvature_contraction_report()
    clifford = build_clifford_curvature_contraction_report()
    bound = build_mixed_connection_remainder_bound_report()
    rule = build_mixed_coefficient_rule_decision()
    if coeffs.status == MIXED_COEFFICIENT_OPEN or curvature.status == MIXED_CURVATURE_OPEN or clifford.status == CLIFFORD_CONTRACTION_OPEN:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        classification = MIXED_CONNECTION_OPEN
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_REMAINDER"
    elif bound.ht_lower_bound_safe is False:
        final = BHSM_THEOREM_FAILURE
        classification = MIXED_CONNECTION_REAL_MISSING_TERM_BREAKS_HT
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_FAILS"
    else:
        final = MIXED_CONNECTION_CLOSED
        classification = MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG"
    return MixedConnectionClosureDecision(
        title="BHSM v2.11 Mixed Connection Closure Decision",
        final_result=final,
        mixed_connection_classification=classification,
        coefficient_status=coeffs.status,
        curvature_status=curvature.status,
        clifford_status=clifford.status,
        exact_remaining_gap=rule.exact_remaining_gap,
        exact_missing_rule=rule.exact_missing_axiom,
        recommended_next_branch=rule.recommended_next_branch,
        recommended_target_theorem=rule.recommended_target_theorem,
        complete_operator_identification_status=operator_status,
        final_paper_allowed=False,
        theorem_complete=final == MIXED_CONNECTION_CLOSED,
        limitations=(
            "The mixed connection coefficient slots are represented through the BHSM bundle-separation/topographic-representation axiom.",
            "The Clifford contraction is not an independent R_bundle term after this representation.",
            "Final paper preparation remains blocked.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_mixed_connection_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_connection_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_mixed_connection_closure_decision_markdown(path: str | Path) -> None:
    report = build_mixed_connection_closure_decision()
    lines = [
        "# BHSM v2.11 Mixed Connection Closure Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Mixed connection classification: `{report.mixed_connection_classification}`",
        f"Coefficient status: `{report.coefficient_status}`",
        f"Curvature status: `{report.curvature_status}`",
        f"Clifford status: `{report.clifford_status}`",
        f"Complete-operator status: `{report.complete_operator_identification_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Exact Remaining Gap",
        "",
        f"`{report.exact_remaining_gap}`",
        "",
        f"Exact missing rule: `{report.exact_missing_rule}`",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
