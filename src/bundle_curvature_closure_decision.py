"""BHSM v2.9 complete bundle-connection curvature closure decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_connection_components import build_bundle_connection_components_report
from bundle_curvature_formula import CURVATURE_FORMULA_DERIVED, CURVATURE_FORMULA_OPEN, build_bundle_curvature_formula_report
from curvature_formula_to_operator_map import build_curvature_formula_to_operator_map_report
from lichnerowicz_curvature_action import build_lichnerowicz_curvature_action_report
from mixed_connection_closure_decision import (
    BHSM_THEOREM_FAILURE as MIXED_BHSM_THEOREM_FAILURE,
    MIXED_CONNECTION_CLOSED,
    build_mixed_connection_closure_decision,
)


COMPLETE_BUNDLE_CONNECTION_CURVATURE_CLOSED = "COMPLETE_BUNDLE_CONNECTION_CURVATURE_CLOSED"
STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class BundleCurvatureClosureDecision:
    title: str
    final_result: str
    connection_status: str
    curvature_formula_status: str
    r_bundle_classification: str
    exact_remaining_gap: str
    exact_missing_component: str
    recommended_next_branch: str
    recommended_target_theorem: str
    complete_operator_identification_status: str
    final_paper_allowed: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_bundle_curvature_closure_decision() -> BundleCurvatureClosureDecision:
    components = build_bundle_connection_components_report()
    formula = build_bundle_curvature_formula_report()
    action = build_lichnerowicz_curvature_action_report()
    mapping = build_curvature_formula_to_operator_map_report()
    mixed = build_mixed_connection_closure_decision()
    if mixed.final_result == MIXED_CONNECTION_CLOSED and formula.status == CURVATURE_FORMULA_DERIVED and mapping.r_bundle_classification != "REMAINDER_OPEN":
        final = COMPLETE_BUNDLE_CONNECTION_CURVATURE_CLOSED
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG"
    elif mixed.final_result == MIXED_BHSM_THEOREM_FAILURE:
        final = BHSM_THEOREM_FAILURE
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_FAILS"
    else:
        final = STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
        operator_status = "COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_REMAINDER"
    return BundleCurvatureClosureDecision(
        title="BHSM v2.9 Complete Bundle Connection Curvature Closure Decision",
        final_result=final,
        connection_status="COMPLETE_BUNDLE_CONNECTION_OPEN" if components.blocking_components else "COMPLETE_BUNDLE_CONNECTION_DEFINED",
        curvature_formula_status=formula.status,
        r_bundle_classification=mapping.r_bundle_classification,
        exact_remaining_gap=mixed.exact_remaining_gap,
        exact_missing_component=components.exact_missing_component,
        recommended_next_branch=mixed.recommended_next_branch,
        recommended_target_theorem=mixed.recommended_target_theorem,
        complete_operator_identification_status=operator_status,
        final_paper_allowed=False,
        theorem_complete=final == COMPLETE_BUNDLE_CONNECTION_CURVATURE_CLOSED,
        limitations=(
            "The complete connection is not closed while the mixed Hopf/base/boundary/coframe component is missing.",
            "R_bundle remains open because its mixed curvature action is not computed.",
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


def export_bundle_curvature_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_curvature_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_bundle_curvature_closure_decision_markdown(path: str | Path) -> None:
    report = build_bundle_curvature_closure_decision()
    lines = [
        "# BHSM v2.9 Complete Bundle Connection Curvature Closure Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"Connection status: `{report.connection_status}`",
        f"Curvature formula status: `{report.curvature_formula_status}`",
        f"R_bundle classification: `{report.r_bundle_classification}`",
        f"Complete-operator status: `{report.complete_operator_identification_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final paper allowed: `{report.final_paper_allowed}`",
        "",
        "## Exact Remaining Gap",
        "",
        f"`{report.exact_remaining_gap}`",
        "",
        f"Exact missing component: `{report.exact_missing_component}`",
        f"Recommended next branch: `{report.recommended_next_branch}`",
        f"Recommended target theorem: `{report.recommended_target_theorem}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
