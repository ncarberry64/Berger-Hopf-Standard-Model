"""BHSM v2.7 closure decision for the bundle-curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_audit import (
    REMAINDER_OPEN,
    REMAINDER_REAL_MISSING_TERM,
    SAFE_REMAINDER_CLASSIFICATIONS,
    build_curvature_remainder_audit_report,
)
from curvature_remainder_bound import build_curvature_remainder_bound_report
from curvature_remainder_formula_decision import (
    BHSM_THEOREM_FAILURE as FORMULA_BHSM_THEOREM_FAILURE,
    CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED,
    build_curvature_remainder_formula_decision,
)


BUNDLE_CURVATURE_REMAINDER_CLOSED = "BUNDLE_CURVATURE_REMAINDER_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class CurvatureRemainderClosureDecision:
    title: str
    final_result: str
    remainder_classification: str
    theorem_complete: bool
    complete_operator_may_upgrade: bool
    blocking_term: str
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_closure_decision() -> CurvatureRemainderClosureDecision:
    """Return the v2.7 curvature-remainder theorem decision."""

    audit = build_curvature_remainder_audit_report()
    bound = build_curvature_remainder_bound_report()
    formula = build_curvature_remainder_formula_decision()
    if formula.final_result == CURVATURE_REMAINDER_FORMULA_BOUND_CLOSED:
        final = BUNDLE_CURVATURE_REMAINDER_CLOSED
    elif formula.final_result == FORMULA_BHSM_THEOREM_FAILURE or audit.final_classification == REMAINDER_REAL_MISSING_TERM:
        final = BHSM_THEOREM_FAILURE
    else:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    return CurvatureRemainderClosureDecision(
        title="BHSM v2.7 Bundle Curvature Remainder Closure Decision",
        final_result=final,
        remainder_classification=audit.final_classification,
        theorem_complete=final == BUNDLE_CURVATURE_REMAINDER_CLOSED,
        complete_operator_may_upgrade=final == BUNDLE_CURVATURE_REMAINDER_CLOSED,
        blocking_term=audit.term_id,
        exact_remaining_gap=formula.exact_remaining_gap,
        recommended_next_branch=formula.recommended_next_branch,
        recommended_target_theorem=formula.recommended_target_theorem,
        final_paper_allowed=False,
        limitations=(
            "The final paper remains blocked unless the full BHSM theorem package is complete.",
            "The v2.7 audit does not classify the remainder as failure because nonzero uncontrolled action has not been proven.",
            "The v2.7 audit does not classify the remainder as closed because no explicit formula/bound proof is implemented.",
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


def export_curvature_remainder_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_closure_decision_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_closure_decision()
    lines = [
        "# BHSM v2.7 Bundle Curvature Remainder Closure Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Remainder classification: `{report.remainder_classification}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Complete operator may upgrade: `{report.complete_operator_may_upgrade}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Blocking Term",
        "",
        f"`{report.blocking_term}`",
        "",
        "## Exact Remaining Gap",
        "",
        f"`{report.exact_remaining_gap}`",
        "",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
