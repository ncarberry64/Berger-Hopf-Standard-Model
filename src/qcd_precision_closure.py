"""Precision QCD/RG closure attempt for the BHSM final campaign."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from precision_qcd_inputs import PRECISION_QCD_PLACEHOLDER
from precision_rg_matching import QCDRGMatchingReport, build_precision_qcd_rg_report
from rg_threshold_uncertainty import ThresholdUncertaintyRow, threshold_uncertainty_rows


PRECISION_QCD_MATCHING_COMPLETE = "PRECISION_QCD_MATCHING_COMPLETE"
SCHEME_CONSISTENT_APPROXIMATION = "SCHEME_CONSISTENT_APPROXIMATION"
PRECISION_INPUTS_REQUIRED = "PRECISION_INPUTS_REQUIRED"
REAL_BHSM_TENSION = "REAL_BHSM_TENSION"
OPEN = "OPEN"


@dataclass(frozen=True)
class QCDPrecisionClosureReport:
    """QCD/RG precision closure report."""

    title: str
    matching_report: QCDRGMatchingReport
    uncertainty_rows: tuple[ThresholdUncertaintyRow, ...]
    final_precision_set_supplied: bool
    approximate_scheme_consistent_rows: int
    placeholder_rows: int
    real_tensions: tuple[str, ...]
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_qcd_precision_closure_report() -> QCDPrecisionClosureReport:
    """Build final-campaign QCD/RG precision closure attempt."""

    matching = build_precision_qcd_rg_report()
    final_precision_set_supplied = any(
        ref.name == PRECISION_QCD_PLACEHOLDER and ref.final and not ref.placeholder
        for ref in matching.reference_sets
    )
    approximate_rows = sum(1 for row in matching.comparisons if row.scheme_consistent and row.approximate)
    placeholder_rows = sum(1 for row in matching.comparisons if row.placeholder)
    real_tension_ids = tuple(f"{row.branch}:{row.quantity}:{row.reference_set}" for row in matching.real_tensions)
    if real_tension_ids:
        status = REAL_BHSM_TENSION
    elif not final_precision_set_supplied:
        status = PRECISION_INPUTS_REQUIRED
    elif approximate_rows:
        status = SCHEME_CONSISTENT_APPROXIMATION
    else:
        status = OPEN
    return QCDPrecisionClosureReport(
        title="BHSM QCD/RG Precision Closure Attempt",
        matching_report=matching,
        uncertainty_rows=threshold_uncertainty_rows(),
        final_precision_set_supplied=final_precision_set_supplied,
        approximate_scheme_consistent_rows=approximate_rows,
        placeholder_rows=placeholder_rows,
        real_tensions=real_tension_ids,
        status=status,
        theorem_complete=False,
        open_obligations=(
            "Supply validated precision-QCD common-scheme quark mass inputs.",
            "Implement validated two-/three-loop threshold matching if precision closure is required.",
            "Propagate uncertainties from supplied precision inputs.",
        ),
        limitations=(
            "No precision QCD values are invented.",
            "Approximate scaffold tensions are not final precision-QCD verdicts.",
            "Frozen BHSM predictions are not changed.",
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


def export_qcd_precision_closure_json(path: str | Path) -> None:
    """Export QCD/RG precision closure report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_qcd_precision_closure_report()), indent=2, sort_keys=True) + "\n")


def export_qcd_precision_closure_markdown(path: str | Path) -> None:
    """Export QCD/RG precision closure report as Markdown."""

    report = build_qcd_precision_closure_report()
    lines = [
        "# BHSM QCD/RG Precision Closure Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Final precision set supplied: `{report.final_precision_set_supplied}`",
        "",
        "## Reference Sets",
        "",
        "| Set | Status | Scheme consistent | Approximate | Placeholder | Final |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for ref in report.matching_report.reference_sets:
        lines.append(f"| `{ref.name}` | `{ref.status}` | `{ref.scheme_consistent}` | `{ref.approximate}` | `{ref.placeholder}` | `{ref.final}` |")
    lines.extend(
        [
            "",
            "## Bare/Dressed Quark-Ratio Rows",
            "",
            "| Branch | Quantity | Reference set | Predicted | Reference | Relative error | Classification |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.matching_report.comparisons:
        lines.append(f"| `{row.branch}` | `{row.quantity}` | `{row.reference_set}` | `{row.predicted}` | `{row.reference}` | `{row.relative_error}` | `{row.tolerance_classification}` |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

