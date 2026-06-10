"""BHSM v2.12 final decision for bundle curvature formula closure."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_curvature_formula_closure import BUNDLE_CURVATURE_FORMULA_CLOSED, build_bundle_curvature_formula_closure_report


STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP = "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
BHSM_THEOREM_FAILURE = "BHSM_THEOREM_FAILURE"


@dataclass(frozen=True)
class BundleCurvatureFormulaDecision:
    title: str
    final_result: str
    r_bundle_classification: str
    complete_operator_identification_status: str
    exact_remaining_gap: str
    recommended_next_branch: str
    recommended_target_theorem: str
    final_paper_allowed: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_bundle_curvature_formula_decision() -> BundleCurvatureFormulaDecision:
    closure = build_bundle_curvature_formula_closure_report()
    closed = closure.status == BUNDLE_CURVATURE_FORMULA_CLOSED
    return BundleCurvatureFormulaDecision(
        title="BHSM v2.12 Bundle Curvature Formula Decision",
        final_result=BUNDLE_CURVATURE_FORMULA_CLOSED if closed else STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
        r_bundle_classification=closure.r_bundle_classification,
        complete_operator_identification_status=closure.complete_operator_identification_status,
        exact_remaining_gap="" if closed else "BUNDLE_CURVATURE_FORMULA_CONDITIONAL_GAP",
        recommended_next_branch="" if closed else "bhsm-v2.13-complete-operator-identification-upgrade",
        recommended_target_theorem="" if closed else "BUNDLE_CURVATURE_FORMULA_CONDITIONAL_GAP",
        final_paper_allowed=False,
        theorem_complete=closed,
        limitations=(
            "Bundle curvature formula closure may upgrade complete-operator identification, but final paper remains blocked until the full theorem package is complete.",
            "No frozen predictions or tolerance bands are changed.",
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


def export_bundle_curvature_formula_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_curvature_formula_decision()), indent=2, sort_keys=True) + "\n")


def export_bundle_curvature_formula_decision_markdown(path: str | Path) -> None:
    report = build_bundle_curvature_formula_decision()
    lines = [
        "# BHSM v2.12 Bundle Curvature Formula Decision",
        "",
        f"Final result: `{report.final_result}`",
        f"R_bundle classification: `{report.r_bundle_classification}`",
        f"Complete-operator identification status: `{report.complete_operator_identification_status}`",
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

