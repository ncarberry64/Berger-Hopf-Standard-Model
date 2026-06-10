"""BHSM v2.12 bundle curvature formula closure report."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_curvature_term_map import build_bundle_curvature_term_map_report
from curvature_remainder_after_mixed_rule import build_curvature_remainder_after_mixed_rule_report
from mixed_connection_closure_decision import MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, build_mixed_connection_closure_decision


BUNDLE_CURVATURE_FORMULA_CLOSED = "BUNDLE_CURVATURE_FORMULA_CLOSED"
BUNDLE_CURVATURE_FORMULA_OPEN = "BUNDLE_CURVATURE_FORMULA_OPEN"


@dataclass(frozen=True)
class BundleCurvatureFormulaClosureReport:
    title: str
    mixed_connection_classification: str
    all_curvature_terms_classified_once: bool
    r_bundle_classification: str
    lower_bound_requires_new_term: bool
    complete_operator_identification_status: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_bundle_curvature_formula_closure_report() -> BundleCurvatureFormulaClosureReport:
    mixed = build_mixed_connection_closure_decision()
    term_map = build_bundle_curvature_term_map_report()
    remainder = build_curvature_remainder_after_mixed_rule_report()
    closed = (
        mixed.mixed_connection_classification == MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR
        and term_map.theorem_complete
        and remainder.theorem_complete
        and not remainder.lower_bound_requires_new_term
    )
    return BundleCurvatureFormulaClosureReport(
        title="BHSM v2.12 Bundle Curvature Formula Closure Report",
        mixed_connection_classification=mixed.mixed_connection_classification,
        all_curvature_terms_classified_once=term_map.all_contributions_classified_once,
        r_bundle_classification=remainder.r_bundle_classification,
        lower_bound_requires_new_term=remainder.lower_bound_requires_new_term,
        complete_operator_identification_status="COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG",
        status=BUNDLE_CURVATURE_FORMULA_CLOSED if closed else BUNDLE_CURVATURE_FORMULA_OPEN,
        theorem_complete=closed,
        limitations=(
            "The bundle curvature formula is closed under the v2.11 topographic-representation rule.",
            "This does not by itself prove the full H_T theorem or authorize final paper preparation.",
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


def export_bundle_curvature_formula_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_curvature_formula_closure_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_curvature_formula_closure_markdown(path: str | Path) -> None:
    report = build_bundle_curvature_formula_closure_report()
    lines = [
        "# BHSM v2.12 Bundle Curvature Formula Closure Report",
        "",
        f"Status: `{report.status}`",
        f"Mixed connection classification: `{report.mixed_connection_classification}`",
        f"All curvature terms classified once: `{report.all_curvature_terms_classified_once}`",
        f"R_bundle classification: `{report.r_bundle_classification}`",
        f"Lower-bound requires new term: `{report.lower_bound_requires_new_term}`",
        f"Complete-operator identification status: `{report.complete_operator_identification_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

