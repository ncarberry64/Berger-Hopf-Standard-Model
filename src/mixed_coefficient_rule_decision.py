"""BHSM v2.11 final decision for the mixed coefficient-rule audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from boundary_coframe_compatibility import build_boundary_coframe_compatibility_report
from coframe_compatibility_rule import build_coframe_compatibility_rule_report
from hopf_base_mixed_rule import build_hopf_base_mixed_rule_report
from mixed_coefficient_minimality import build_mixed_coefficient_minimality_report
from mixed_coefficient_rule import (
    MIXED_COEFFICIENT_RULE_DERIVED,
    MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
    MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY,
    MIXED_COEFFICIENT_RULE_UNIQUE_BY_AXIOMS,
    build_mixed_coefficient_rule_report,
)


MIXED_COEFFICIENT_RULE_CLOSED = "MIXED_COEFFICIENT_RULE_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class MixedCoefficientRuleDecision:
    title: str
    final_result: str
    rule_status: str
    coframe_status: str
    boundary_coframe_status: str
    hopf_base_status: str
    minimality_status: str
    exact_remaining_gap: str
    exact_missing_axiom: str
    recommended_next_branch: str
    recommended_target_theorem: str
    mixed_connection_may_close: bool
    final_paper_allowed: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_mixed_coefficient_rule_decision() -> MixedCoefficientRuleDecision:
    rule = build_mixed_coefficient_rule_report()
    coframe = build_coframe_compatibility_rule_report()
    boundary = build_boundary_coframe_compatibility_report()
    hopf = build_hopf_base_mixed_rule_report()
    minimality = build_mixed_coefficient_minimality_report()
    closed_statuses = {
        MIXED_COEFFICIENT_RULE_DERIVED,
        MIXED_COEFFICIENT_RULE_UNIQUE_BY_AXIOMS,
        MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
        MIXED_COEFFICIENT_RULE_ZERO_BY_COMPATIBILITY,
    }
    closed = rule.rule_status in closed_statuses and coframe.coefficient_rule_fixed
    final = MIXED_COEFFICIENT_RULE_CLOSED if closed else STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    return MixedCoefficientRuleDecision(
        title="BHSM v2.11 Mixed Coefficient Rule Decision",
        final_result=final,
        rule_status=rule.rule_status,
        coframe_status=coframe.status,
        boundary_coframe_status=boundary.status,
        hopf_base_status=hopf.status,
        minimality_status=minimality.minimality_status,
        exact_remaining_gap="" if closed else "MIXED_CONNECTION_COMPATIBILITY_AXIOM_GAP",
        exact_missing_axiom=rule.exact_missing_axiom,
        recommended_next_branch="" if closed else "bhsm-v2.12-mixed-connection-compatibility-axiom",
        recommended_target_theorem="" if closed else "MIXED_CONNECTION_COMPATIBILITY_AXIOM_GAP",
        mixed_connection_may_close=closed,
        final_paper_allowed=False,
        theorem_complete=closed,
        limitations=(
            "The v2.11 audit closes the free mixed coefficient rule through BHSM bundle separation and topographic representation.",
            "F_mixed and Cl(F_mixed) are classified as represented by existing sectors, not as new independent curvature terms.",
            "No frozen prediction, empirical residual, mass, CKM, PMNS, or prediction-ledger value is used.",
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


def export_mixed_coefficient_rule_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_coefficient_rule_decision()), indent=2, sort_keys=True) + "\n")


def export_mixed_coefficient_rule_decision_markdown(path: str | Path) -> None:
    report = build_mixed_coefficient_rule_decision()
    lines = [
        "# BHSM v2.11 Mixed Coefficient Rule Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Rule status: `{report.rule_status}`",
        f"Coframe status: `{report.coframe_status}`",
        f"Boundary/coframe status: `{report.boundary_coframe_status}`",
        f"Hopf/base status: `{report.hopf_base_status}`",
        f"Minimality status: `{report.minimality_status}`",
        f"Mixed connection may close: `{report.mixed_connection_may_close}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Exact Remaining Gap",
        "",
        f"`{report.exact_remaining_gap}`",
        "",
        f"Exact missing axiom: `{report.exact_missing_axiom}`",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
