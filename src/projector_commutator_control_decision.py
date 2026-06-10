"""BHSM v2.14 projector commutator control decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from projector_commutator_control import PROJECTOR_DEFINITION_PROVEN, build_projector_definition_audit_report
from projector_commutator_domain_control import PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT, build_projector_commutator_domain_control_report
from projector_commutator_relative_bound import PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN, build_projector_commutator_relative_bound_report
from projector_operator_commutators import build_projector_operator_commutators_report
from projector_termwise_commutator_audit import TERMWISE_COMMUTATOR_AUDIT_CLOSED, build_projector_termwise_commutator_audit_report


PROJECTOR_COMMUTATOR_CONTROL_PROVEN = "PROJECTOR_COMMUTATOR_CONTROL_PROVEN"
PROJECTOR_COMMUTATOR_CONTROL_CONDITIONAL_STRONG = "PROJECTOR_COMMUTATOR_CONTROL_CONDITIONAL_STRONG"
PROJECTOR_COMMUTATOR_CONTROL_BLOCKED_BY_SINGLE_NAMED_GAP = "PROJECTOR_COMMUTATOR_CONTROL_BLOCKED_BY_SINGLE_NAMED_GAP"
PROJECTOR_COMMUTATOR_CONTROL_FAILS = "PROJECTOR_COMMUTATOR_CONTROL_FAILS"

PROJECTOR_COMMUTATOR_CONTROL_CLOSED = "PROJECTOR_COMMUTATOR_CONTROL_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class ProjectorCommutatorControlDecision:
    title: str
    final_result: str
    commutator_status: str
    projector_definition_status: str
    termwise_status: str
    relative_bound_status: str
    domain_control_status: str
    a_total: float
    a_total_less_than_one: bool
    downstream_graph_domain_may_proceed: bool
    theorem_complete: bool
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_projector_commutator_control_decision() -> ProjectorCommutatorControlDecision:
    projector = build_projector_definition_audit_report()
    commutators = build_projector_operator_commutators_report()
    termwise = build_projector_termwise_commutator_audit_report()
    bound = build_projector_commutator_relative_bound_report()
    domain = build_projector_commutator_domain_control_report()
    closed = (
        projector.status == PROJECTOR_DEFINITION_PROVEN
        and commutators.theorem_complete
        and termwise.status == TERMWISE_COMMUTATOR_AUDIT_CLOSED
        and bound.status == PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN
        and domain.status == PROJECTOR_COMMUTATOR_DOMAIN_CONTROL_SUFFICIENT
    )
    fails = any(row.classification == "COMMUTATOR_FAILS" for row in commutators.rows)
    if closed:
        commutator_status = PROJECTOR_COMMUTATOR_CONTROL_PROVEN
        final = PROJECTOR_COMMUTATOR_CONTROL_CLOSED
        gap = ""
        branch = ""
        target = ""
    elif fails:
        commutator_status = PROJECTOR_COMMUTATOR_CONTROL_FAILS
        final = BHSM_THEOREM_FAILURE
        gap = "UNCONTROLLED_PROJECTOR_COMMUTATOR_BREAKS_HT"
        branch = ""
        target = gap
    else:
        commutator_status = PROJECTOR_COMMUTATOR_CONTROL_BLOCKED_BY_SINGLE_NAMED_GAP
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        gap = "PROJECTOR_COMMUTATOR_RESIDUAL_CONTROL_GAP"
        branch = "bhsm-v2.15-projector-commutator-residual-control"
        target = gap
    return ProjectorCommutatorControlDecision(
        title="BHSM v2.14 Projector Commutator Control Decision",
        final_result=final,
        commutator_status=commutator_status,
        projector_definition_status=projector.status,
        termwise_status=termwise.status,
        relative_bound_status=bound.status,
        domain_control_status=domain.status,
        a_total=bound.a_total,
        a_total_less_than_one=bound.a_total_less_than_one,
        downstream_graph_domain_may_proceed=closed,
        theorem_complete=closed,
        exact_remaining_gap=gap,
        recommended_next_branch=branch,
        recommended_target_theorem=target,
        final_paper_allowed=False,
        limitations=(
            "This decision closes projector commutator control only.",
            "Projector graph-domain stability and lower-bound transfer remain separate downstream theorem gates.",
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


def export_projector_commutator_control_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_commutator_control_decision()), indent=2, sort_keys=True) + "\n")


def export_projector_commutator_control_decision_markdown(path: str | Path) -> None:
    report = build_projector_commutator_control_decision()
    lines = [
        "# BHSM v2.14 Projector Commutator Control Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Commutator status: `{report.commutator_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"a_total: `{report.a_total}`",
        f"a_total < 1: `{report.a_total_less_than_one}`",
        f"Downstream graph-domain may proceed: `{report.downstream_graph_domain_may_proceed}`",
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
