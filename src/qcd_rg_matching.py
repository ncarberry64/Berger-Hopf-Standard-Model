"""BHSM v1.4 QCD/RG precision matching scaffold.

This module compares frozen BHSM quark ratios against labeled reference-set
scaffolds. It does not alter BHSM predictions and does not implement precision
QCD matching.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log10
from pathlib import Path
from typing import Any

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate
from mass_scheme import build_ratio_reference
from quark_mass_reference_sets import (
    COMMON_SCALE_APPROX,
    MIXED_DEFAULT,
    PRECISION_QCD_PLACEHOLDER,
    THRESHOLD_AWARE_APPROX,
    QuarkMassReferenceSet,
    available_reference_sets,
    reference_sets_asdict,
)
from quark_running import MZ, PLACEHOLDER_PRECISION_QCD, alpha_s_one_loop, alpha_s_piecewise_one_loop
from rg_scheme_ledger import rg_scheme_ledger_asdict


QUARK_RATIO_PAIRS = {
    "c/t": ("up_quark_ratios", "middle", "c", "t"),
    "u/t": ("up_quark_ratios", "light", "u", "t"),
    "s/b": ("down_quark_ratios", "middle", "s", "b"),
    "d/b": ("down_quark_ratios", "light", "d", "b"),
}


@dataclass(frozen=True)
class QCDRGComparisonRow:
    """One BHSM quark-ratio comparison row."""

    branch: str
    quantity: str
    predicted: float
    reference: float | None
    absolute_error: float | None
    relative_error: float | None
    log_error: float | None
    scheme_set: str
    scheme: str
    scale: str
    scheme_consistent: bool
    comparison_final: bool
    status: str
    within_fixed_tolerance: bool | None
    notes: tuple[str, ...]


@dataclass(frozen=True)
class QCDRGMatchingReport:
    """Complete Gate 2 QCD/RG scaffold report."""

    title: str
    target_scale: float
    alpha_s_fixed_nf_at_target: float
    alpha_s_piecewise_at_target: float
    reference_sets: dict[str, Any]
    scheme_ledger: list[dict[str, Any]]
    comparison_rows: tuple[QCDRGComparisonRow, ...]
    final_scheme_consistent_failures: tuple[QCDRGComparisonRow, ...]
    stop_condition_triggered: bool
    theorem_complete: bool
    predictions_changed: bool
    limitations: tuple[str, ...]


def _branch_outputs() -> tuple[Any, Any]:
    return build_bhsm_bare_v1(), build_bhsm_dressed_v1_candidate()


def _predicted_ratio(branch: Any, quantity: str) -> float:
    key, rank, _num, _den = QUARK_RATIO_PAIRS[quantity]
    return float(branch.outputs[key][rank])


def _comparison_row(
    branch: Any,
    quantity: str,
    ref_set: QuarkMassReferenceSet,
    fixed_tolerance: float = 0.25,
) -> QCDRGComparisonRow:
    _key, _rank, numerator, denominator = QUARK_RATIO_PAIRS[quantity]
    predicted = _predicted_ratio(branch, quantity)
    if ref_set.name == PRECISION_QCD_PLACEHOLDER:
        return QCDRGComparisonRow(
            branch=branch.version.branch,
            quantity=quantity,
            predicted=predicted,
            reference=None,
            absolute_error=None,
            relative_error=None,
            log_error=None,
            scheme_set=ref_set.name,
            scheme=PRECISION_QCD_PLACEHOLDER,
            scale=f"{ref_set.target_scale:g} GeV" if ref_set.target_scale is not None else "open",
            scheme_consistent=False,
            comparison_final=False,
            status="PLACEHOLDER_NOT_COMPUTED",
            within_fixed_tolerance=None,
            notes=("Precision QCD placeholder contains no numerical reference.",),
        )
    ref = build_ratio_reference(numerator, denominator, ref_set.references)
    absolute = abs(predicted - ref.ratio)
    relative = absolute / abs(ref.ratio)
    status = ref_set.status
    within = bool(relative <= fixed_tolerance)
    if ref_set.comparison_final and ref_set.scheme_consistent and not within:
        status = "FINAL_SCHEME_CONSISTENT_TENSION"
    return QCDRGComparisonRow(
        branch=branch.version.branch,
        quantity=quantity,
        predicted=predicted,
        reference=float(ref.ratio),
        absolute_error=float(absolute),
        relative_error=float(relative),
        log_error=None if predicted <= 0 or ref.ratio <= 0 else float(log10(predicted / ref.ratio)),
        scheme_set=ref_set.name,
        scheme=ref.scheme,
        scale=ref.scale,
        scheme_consistent=ref_set.scheme_consistent and ref.scheme_consistent,
        comparison_final=ref_set.comparison_final,
        status=status,
        within_fixed_tolerance=within,
        notes=tuple(ref_set.notes + ref.notes),
    )


def build_qcd_rg_matching_report(target_scale: float = MZ) -> QCDRGMatchingReport:
    """Return the Gate 2 QCD/RG matching scaffold report."""

    bare, dressed = _branch_outputs()
    rows: list[QCDRGComparisonRow] = []
    for ref_set in available_reference_sets(target_scale):
        for branch in (bare, dressed):
            for quantity in QUARK_RATIO_PAIRS:
                if branch.version.branch == "BHSM_DRESSED_V1_CANDIDATE" and quantity != "c/t":
                    continue
                rows.append(_comparison_row(branch, quantity, ref_set))
    final_failures = tuple(
        row for row in rows
        if row.comparison_final and row.scheme_consistent and row.within_fixed_tolerance is False
    )
    return QCDRGMatchingReport(
        title="BHSM v1.4 QCD/RG Matching Scaffold",
        target_scale=float(target_scale),
        alpha_s_fixed_nf_at_target=alpha_s_one_loop(target_scale),
        alpha_s_piecewise_at_target=alpha_s_piecewise_one_loop(target_scale),
        reference_sets=reference_sets_asdict(target_scale),
        scheme_ledger=rg_scheme_ledger_asdict(),
        comparison_rows=tuple(rows),
        final_scheme_consistent_failures=final_failures,
        stop_condition_triggered=bool(final_failures),
        theorem_complete=False,
        predictions_changed=False,
        limitations=(
            "MIXED_DEFAULT is scheme-sensitive.",
            "COMMON_SCALE_APPROX and THRESHOLD_AWARE_APPROX are approximate scaffolds, not final precision QCD.",
            f"{PLACEHOLDER_PRECISION_QCD} is intentionally not computed.",
            "BHSM frozen predictions are compared but not changed.",
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


def export_qcd_rg_matching_json(path: str | Path, target_scale: float = MZ) -> None:
    """Export Gate 2 QCD/RG matching scaffold as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_qcd_rg_matching_report(target_scale)), indent=2, sort_keys=True) + "\n")


def export_qcd_rg_matching_markdown(path: str | Path, target_scale: float = MZ) -> None:
    """Export Gate 2 QCD/RG matching scaffold as Markdown."""

    report = build_qcd_rg_matching_report(target_scale)
    lines = [
        "# BHSM v1.4 QCD/RG Matching Scaffold",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Predictions changed: `{report.predictions_changed}`",
        f"Stop condition triggered: `{report.stop_condition_triggered}`",
        "",
        "## Reference Sets",
        "",
        "| Set | Status | Scheme consistent | Final comparison | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report.reference_sets.values():
        lines.append(
            f"| `{item['name']}` | `{item['status']}` | `{item['scheme_consistent']}` | `{item['comparison_final']}` | {'<br>'.join(item['notes'])} |"
        )
    lines.extend(
        [
            "",
            "## Comparison Rows",
            "",
            "| Branch | Quantity | Predicted | Reference | Relative Error | Scheme Set | Status | Final |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.comparison_rows:
        lines.append(
            f"| `{row.branch}` | `{row.quantity}` | `{row.predicted}` | `{row.reference}` | `{row.relative_error}` | `{row.scheme_set}` | `{row.status}` | `{row.comparison_final}` |"
        )
    lines.extend(
        [
            "",
            "## Stop-Condition Assessment",
            "",
            "No final scheme-consistent precision-QCD reference set is available in this scaffold; therefore no Gate 2 structural stop is triggered.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
