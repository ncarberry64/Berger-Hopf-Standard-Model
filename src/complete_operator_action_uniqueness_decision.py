"""BHSM v2.13 complete operator action-uniqueness decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_axiom_uniqueness import (
    COMPLETE_OPERATOR_ACTION_UNIQUENESS_FAILS,
    COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN,
    build_operator_axiom_uniqueness_report,
)


COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED = "COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class CompleteOperatorActionUniquenessDecision:
    title: str
    final_result: str
    uniqueness_status: str
    complete_operator_identification_may_upgrade: bool
    downstream_ht_may_proceed: bool
    theorem_complete: bool
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_complete_operator_action_uniqueness_decision() -> CompleteOperatorActionUniquenessDecision:
    uniqueness = build_operator_axiom_uniqueness_report()
    if uniqueness.status == COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN:
        final = COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED
        gap = ""
        branch = ""
        target = ""
        may_upgrade = True
    elif uniqueness.status == COMPLETE_OPERATOR_ACTION_UNIQUENESS_FAILS:
        final = BHSM_THEOREM_FAILURE
        gap = uniqueness.exact_remaining_gap
        branch = ""
        target = gap
        may_upgrade = False
    else:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        gap = uniqueness.exact_remaining_gap
        branch = uniqueness.recommended_next_branch
        target = uniqueness.recommended_target_theorem
        may_upgrade = False
    return CompleteOperatorActionUniquenessDecision(
        title="BHSM v2.13 Complete Operator Action-Uniqueness Decision",
        final_result=final,
        uniqueness_status=uniqueness.status,
        complete_operator_identification_may_upgrade=may_upgrade,
        downstream_ht_may_proceed=may_upgrade,
        theorem_complete=final == COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED,
        exact_remaining_gap=gap,
        recommended_next_branch=branch,
        recommended_target_theorem=target,
        final_paper_allowed=False,
        limitations=(
            "This decision concerns complete-operator action uniqueness only.",
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


def export_complete_operator_action_uniqueness_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_operator_action_uniqueness_decision()), indent=2, sort_keys=True) + "\n")


def export_complete_operator_action_uniqueness_decision_markdown(path: str | Path) -> None:
    report = build_complete_operator_action_uniqueness_decision()
    lines = [
        "# BHSM v2.13 Complete Operator Action-Uniqueness Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Uniqueness status: `{report.uniqueness_status}`",
        f"Complete-operator identification may upgrade: `{report.complete_operator_identification_may_upgrade}`",
        f"Downstream H_T may proceed: `{report.downstream_ht_may_proceed}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
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
