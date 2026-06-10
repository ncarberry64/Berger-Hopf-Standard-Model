"""BHSM v2.6 complete-operator identification decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_identification_theorem import (
    COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM,
    COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
    FAILS_COMPLETE_OPERATOR_IDENTIFICATION,
    build_operator_identification_theorem_report,
)


STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class CompleteOperatorIdentificationDecision:
    title: str
    operator_identification_status: str
    final_result: str
    theorem_complete: bool
    blocking_term: str
    exact_obstruction: str
    recommended_next_branch: str
    recommended_target_theorem: str
    downstream_may_upgrade: bool
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_complete_operator_identification_decision() -> CompleteOperatorIdentificationDecision:
    theorem = build_operator_identification_theorem_report()
    if theorem.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN:
        final = COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    elif theorem.status == FAILS_COMPLETE_OPERATOR_IDENTIFICATION:
        final = BHSM_THEOREM_FAILURE
    else:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    return CompleteOperatorIdentificationDecision(
        title="BHSM v2.7 Complete Operator Identification Decision",
        operator_identification_status=theorem.status,
        final_result=final,
        theorem_complete=final == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
        blocking_term=theorem.blocking_term,
        exact_obstruction=theorem.exact_obstruction,
        recommended_next_branch=theorem.next_branch,
        recommended_target_theorem=theorem.next_target_theorem,
        downstream_may_upgrade=final == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
        final_paper_allowed=False,
        limitations=(
            "This decision concerns only complete-operator identification.",
            "Final paper remains blocked unless the full BHSM theorem package is complete.",
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


def export_complete_operator_identification_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_operator_identification_decision()), indent=2, sort_keys=True) + "\n")


def export_complete_operator_identification_decision_markdown(path: str | Path) -> None:
    report = build_complete_operator_identification_decision()
    lines = [
        "# BHSM v2.7 Complete Operator Identification Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Operator-identification status: `{report.operator_identification_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Downstream may upgrade: `{report.downstream_may_upgrade}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Blocking Term",
        "",
        f"`{report.blocking_term}`",
        "",
        "## Exact Obstruction",
        "",
        report.exact_obstruction,
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
