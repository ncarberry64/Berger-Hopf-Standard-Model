"""BHSM v2.15 projector graph-domain closure decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from interacting_graph_domain import GRAPH_DOMAIN_DEFINITIONS_PROVEN, INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN, build_graph_domain_definitions_report, build_interacting_graph_domain_report
from projector_domain_invariance import BLOCKING_DOMAIN_STABILITY_CLASSIFICATIONS, build_projector_domain_invariance_report
from projector_graph_norm_control import PROJECTOR_GRAPH_NORM_CONTROL_PROVEN, build_projector_graph_norm_control_report


PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN = "PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN"
PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL_STRONG = "PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL_STRONG"
PROJECTOR_GRAPH_DOMAIN_STABILITY_BLOCKED_BY_SINGLE_NAMED_GAP = "PROJECTOR_GRAPH_DOMAIN_STABILITY_BLOCKED_BY_SINGLE_NAMED_GAP"
PROJECTOR_GRAPH_DOMAIN_STABILITY_FAILS = "PROJECTOR_GRAPH_DOMAIN_STABILITY_FAILS"

PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED = "PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class ProjectorDomainClosureDecision:
    title: str
    final_result: str
    graph_domain_status: str
    definitions_status: str
    interacting_domain_status: str
    domain_invariance_status: str
    graph_norm_control_status: str
    Pperp_DA0V_subset_DA0V: bool
    theorem_complete: bool
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    final_paper_allowed: bool
    limitations: tuple[str, ...]


def build_projector_domain_closure_decision() -> ProjectorDomainClosureDecision:
    definitions = build_graph_domain_definitions_report()
    interacting = build_interacting_graph_domain_report()
    invariance = build_projector_domain_invariance_report()
    graph_norm = build_projector_graph_norm_control_report()
    blocking = any(row.classification in BLOCKING_DOMAIN_STABILITY_CLASSIFICATIONS for row in invariance.rows)
    fails = any(row.classification == "DOMAIN_STABLE_FAILS" for row in invariance.rows) or graph_norm.status == "PROJECTOR_GRAPH_NORM_CONTROL_FAILS"
    closed = (
        definitions.status == GRAPH_DOMAIN_DEFINITIONS_PROVEN
        and interacting.status == INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN
        and invariance.Pperp_DA0V_subset_DA0V
        and graph_norm.status == PROJECTOR_GRAPH_NORM_CONTROL_PROVEN
        and not blocking
    )
    if closed:
        final = PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED
        status = PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN
        gap = ""
        branch = ""
        target = ""
    elif fails:
        final = BHSM_THEOREM_FAILURE
        status = PROJECTOR_GRAPH_DOMAIN_STABILITY_FAILS
        gap = "PROJECTOR_GRAPH_DOMAIN_STABILITY_FAILURE"
        branch = ""
        target = gap
    else:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        status = PROJECTOR_GRAPH_DOMAIN_STABILITY_BLOCKED_BY_SINGLE_NAMED_GAP
        if interacting.status != INTERACTING_DOMAIN_EQUALS_REFERENCE_DOMAIN_PROVEN:
            gap = "INTERACTING_DOMAIN_EQUALITY_GAP"
        elif graph_norm.status != PROJECTOR_GRAPH_NORM_CONTROL_PROVEN:
            gap = "PROJECTOR_GRAPH_NORM_CONTROL_GAP"
        else:
            gap = "PROJECTOR_TERMWISE_DOMAIN_INVARIANCE_GAP"
        branch = "bhsm-v2.16-projector-domain-residual"
        target = gap
    return ProjectorDomainClosureDecision(
        title="BHSM v2.15 Projector Graph-Domain Closure Decision",
        final_result=final,
        graph_domain_status=status,
        definitions_status=definitions.status,
        interacting_domain_status=interacting.status,
        domain_invariance_status=invariance.status,
        graph_norm_control_status=graph_norm.status,
        Pperp_DA0V_subset_DA0V=invariance.Pperp_DA0V_subset_DA0V and graph_norm.projector_bounded_on_D_A0V,
        theorem_complete=closed,
        exact_remaining_gap=gap,
        recommended_next_branch=branch,
        recommended_target_theorem=target,
        final_paper_allowed=False,
        limitations=(
            "This decision closes projector graph-domain stability only.",
            "Lower-bound transfer, index theorem, and mirror exclusion remain separate downstream theorem gates.",
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


def export_projector_domain_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_domain_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_projector_domain_closure_decision_markdown(path: str | Path) -> None:
    report = build_projector_domain_closure_decision()
    lines = [
        "# BHSM v2.15 Projector Graph-Domain Closure Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Graph-domain status: `{report.graph_domain_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"P_perp D(A0+V) subset D(A0+V): `{report.Pperp_DA0V_subset_DA0V}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "| Input | Status |",
        "| --- | --- |",
        f"| definitions | `{report.definitions_status}` |",
        f"| interacting domain | `{report.interacting_domain_status}` |",
        f"| domain invariance | `{report.domain_invariance_status}` |",
        f"| graph-norm control | `{report.graph_norm_control_status}` |",
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
