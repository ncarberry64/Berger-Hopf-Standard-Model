"""BHSM v1.4 precision-oriented QCD/RG matching report."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from math import log10
from pathlib import Path
from typing import Any

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate
from precision_qcd_inputs import (
    COMMON_SCALE_APPROX,
    MIXED_DEFAULT,
    PDG_STYLE_REFERENCE_PLACEHOLDER,
    PRECISION_QCD_PLACEHOLDER,
    THRESHOLD_AWARE_APPROX,
    QCDReferenceSet,
    QuarkMassInput,
    qcd_reference_sets,
)
from quark_ratio_uncertainties import classify_tolerance, propagate_ratio_uncertainty
from quark_running import MZ, QUARK_REFERENCE_SCALES
from quark_threshold_matching import ONE_LOOP_BASELINE, THRESHOLD_AWARE_ONE_LOOP, ThresholdMatchingConfig, alpha_s_at_target, running_mass


QUARK_RATIO_MAP = {
    "c/t": ("up_quark_ratios", "middle", "c", "t"),
    "u/t": ("up_quark_ratios", "light", "u", "t"),
    "s/b": ("down_quark_ratios", "middle", "s", "b"),
    "d/b": ("down_quark_ratios", "light", "d", "b"),
}


@dataclass(frozen=True)
class QuarkRatioComparison:
    """One bare/dressed quark-ratio comparison."""

    branch: str
    quantity: str
    predicted: float
    reference: float | None
    reference_uncertainty: float | None
    absolute_error: float | None
    relative_error: float | None
    log_error: float | None
    pull: float | None
    reference_set: str
    scheme: str
    scale: str
    source_label: str
    scheme_consistent: bool
    final: bool
    approximate: bool
    placeholder: bool
    tolerance_classification: str
    real_tension: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class QCDRGMatchingReport:
    """Complete precision-oriented QCD/RG matching report."""

    title: str
    target_scale_gev: float
    reference_sets: tuple[QCDReferenceSet, ...]
    alpha_s_rows: dict[str, float | None]
    comparisons: tuple[QuarkRatioComparison, ...]
    real_tensions: tuple[QuarkRatioComparison, ...]
    theorem_complete: bool
    frozen_predictions_changed: bool
    limitations: tuple[str, ...]


def _input_lookup(ref_set: QCDReferenceSet) -> dict[str, QuarkMassInput]:
    return {row.particle: row for row in ref_set.inputs}


def _filled_running_reference_set(ref_set: QCDReferenceSet, target_scale_gev: float) -> QCDReferenceSet:
    if ref_set.name not in {COMMON_SCALE_APPROX, THRESHOLD_AWARE_APPROX}:
        return ref_set
    method = ONE_LOOP_BASELINE if ref_set.name == COMMON_SCALE_APPROX else THRESHOLD_AWARE_ONE_LOOP
    config = ThresholdMatchingConfig(target_scale_gev=target_scale_gev, method=method)
    mixed = _input_lookup(next(item for item in qcd_reference_sets(target_scale_gev) if item.name == MIXED_DEFAULT))
    rows = []
    for shell in ref_set.inputs:
        source = mixed[shell.particle]
        result = running_mass(shell.particle, float(source.value), QUARK_REFERENCE_SCALES[shell.particle], config)
        rows.append(
            replace(
                shell,
                value=result.mass_running,
                source_label=result.source_label,
                notes=tuple(shell.notes + result.notes),
            )
        )
    return replace(ref_set, inputs=tuple(rows))


def reference_sets_with_running(target_scale_gev: float = MZ) -> tuple[QCDReferenceSet, ...]:
    """Return reference sets with approximate running values filled where implemented."""

    return tuple(_filled_running_reference_set(item, target_scale_gev) for item in qcd_reference_sets(target_scale_gev))


def _ratio_from_set(
    ref_set: QCDReferenceSet,
    numerator: str,
    denominator: str,
    predicted: float,
) -> tuple[float | None, float | None, float | None, tuple[str, ...]]:
    inputs = _input_lookup(ref_set)
    num = inputs[numerator]
    den = inputs[denominator]
    if num.value is None or den.value is None:
        return None, None, None, ("No numerical reference supplied for placeholder set.",)
    uncertainty = propagate_ratio_uncertainty(num.value, den.value, num.uncertainty, den.uncertainty, predicted)
    return uncertainty.ratio, uncertainty.uncertainty, uncertainty.pull, uncertainty.notes


def _predicted(branch: Any, quantity: str) -> float:
    key, rank, _num, _den = QUARK_RATIO_MAP[quantity]
    return float(branch.outputs[key][rank])


def _comparison(branch: Any, quantity: str, ref_set: QCDReferenceSet) -> QuarkRatioComparison:
    _key, _rank, numerator, denominator = QUARK_RATIO_MAP[quantity]
    predicted = _predicted(branch, quantity)
    reference, reference_uncertainty, pull, uncertainty_notes = _ratio_from_set(ref_set, numerator, denominator, predicted)
    absolute = None if reference is None else abs(predicted - reference)
    relative = None if reference is None else absolute / abs(reference)
    log_error = None if reference is None or reference <= 0 or predicted <= 0 else log10(predicted / reference)
    inputs = _input_lookup(ref_set)
    scheme = inputs[numerator].scheme if inputs[numerator].scheme == inputs[denominator].scheme else f"{inputs[numerator].scheme}/{inputs[denominator].scheme}"
    scale = (
        f"{inputs[numerator].scale_gev:g} GeV"
        if inputs[numerator].scale_gev == inputs[denominator].scale_gev and inputs[numerator].scale_gev is not None
        else f"{inputs[numerator].scale_gev} GeV/{inputs[denominator].scale_gev} GeV"
    )
    classification = classify_tolerance(relative, ref_set.scheme_consistent, ref_set.final, ref_set.approximate)
    return QuarkRatioComparison(
        branch=branch.version.branch,
        quantity=quantity,
        predicted=predicted,
        reference=reference,
        reference_uncertainty=reference_uncertainty,
        absolute_error=absolute,
        relative_error=relative,
        log_error=log_error,
        pull=pull,
        reference_set=ref_set.name,
        scheme=scheme,
        scale=scale,
        source_label=f"{inputs[numerator].source_label}/{inputs[denominator].source_label}",
        scheme_consistent=ref_set.scheme_consistent,
        final=ref_set.final,
        approximate=ref_set.approximate,
        placeholder=ref_set.placeholder,
        tolerance_classification=classification,
        real_tension=classification == "REAL_BHSM_TENSION",
        notes=tuple(ref_set.notes + uncertainty_notes),
    )


def build_precision_qcd_rg_report(target_scale_gev: float = MZ) -> QCDRGMatchingReport:
    """Build the precision-oriented v1.4 QCD/RG matching report."""

    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    ref_sets = reference_sets_with_running(target_scale_gev)
    rows: list[QuarkRatioComparison] = []
    for ref_set in ref_sets:
        for quantity in QUARK_RATIO_MAP:
            rows.append(_comparison(bare, quantity, ref_set))
        rows.append(_comparison(dressed, "c/t", ref_set))
    tensions = tuple(row for row in rows if row.real_tension)
    return QCDRGMatchingReport(
        title="BHSM v1.4 Precision-Oriented QCD/RG Matching Framework",
        target_scale_gev=float(target_scale_gev),
        reference_sets=ref_sets,
        alpha_s_rows={
            ONE_LOOP_BASELINE: alpha_s_at_target(ThresholdMatchingConfig(target_scale_gev=target_scale_gev, method=ONE_LOOP_BASELINE)),
            THRESHOLD_AWARE_ONE_LOOP: alpha_s_at_target(ThresholdMatchingConfig(target_scale_gev=target_scale_gev, method=THRESHOLD_AWARE_ONE_LOOP)),
            "TWO_LOOP_PLACEHOLDER": None,
            "THREE_LOOP_PLACEHOLDER": None,
        },
        comparisons=tuple(rows),
        real_tensions=tensions,
        theorem_complete=False,
        frozen_predictions_changed=False,
        limitations=(
            "No precision QCD constants or external mass inputs are invented.",
            "PDG-style and precision-QCD rows are placeholders until verified inputs are supplied.",
            "Approximate scheme-consistent rows may show scaffold-level tensions but are not final precision verdicts.",
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


def export_precision_qcd_rg_json(path: str | Path, target_scale_gev: float = MZ) -> None:
    """Export precision-oriented QCD/RG report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_precision_qcd_rg_report(target_scale_gev)), indent=2, sort_keys=True) + "\n")


def export_precision_qcd_rg_markdown(path: str | Path, target_scale_gev: float = MZ) -> None:
    """Export precision-oriented QCD/RG report as Markdown."""

    report = build_precision_qcd_rg_report(target_scale_gev)
    lines = [
        "# BHSM v1.4 Precision-Oriented QCD/RG Matching Framework",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Frozen predictions changed: `{report.frozen_predictions_changed}`",
        f"Real tensions: `{len(report.real_tensions)}`",
        "",
        "## Reference Sets",
        "",
        "| Set | Status | Scheme consistent | Approximate | Placeholder | Final |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for ref_set in report.reference_sets:
        lines.append(f"| `{ref_set.name}` | `{ref_set.status}` | `{ref_set.scheme_consistent}` | `{ref_set.approximate}` | `{ref_set.placeholder}` | `{ref_set.final}` |")
    lines.extend([
        "",
        "## Quark Ratio Comparisons",
        "",
        "| Branch | Quantity | Predicted | Reference | Relative Error | Reference Set | Classification | Real tension |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in report.comparisons:
        lines.append(f"| `{row.branch}` | `{row.quantity}` | `{row.predicted}` | `{row.reference}` | `{row.relative_error}` | `{row.reference_set}` | `{row.tolerance_classification}` | `{row.real_tension}` |")
    lines.extend(["", "## Limitations", "", *[f"- {item}" for item in report.limitations], ""])
    Path(path).write_text("\n".join(lines))


def export_quark_ratio_precision_comparison_markdown(path: str | Path, target_scale_gev: float = MZ) -> None:
    """Export a focused quark-ratio comparison table."""

    report = build_precision_qcd_rg_report(target_scale_gev)
    lines = [
        "# BHSM Quark Ratio Precision Comparison",
        "",
        "| Branch | Quantity | Reference Set | Scheme | Scale | Source | Predicted | Reference | Uncertainty | Relative Error | Classification |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.comparisons:
        lines.append(
            f"| `{row.branch}` | `{row.quantity}` | `{row.reference_set}` | `{row.scheme}` | `{row.scale}` | `{row.source_label}` | `{row.predicted}` | `{row.reference}` | `{row.reference_uncertainty}` | `{row.relative_error}` | `{row.tolerance_classification}` |"
        )
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_quark_ratio_precision_comparison_json(path: str | Path, target_scale_gev: float = MZ) -> None:
    """Export focused quark-ratio comparison rows as JSON."""

    report = build_precision_qcd_rg_report(target_scale_gev)
    Path(path).write_text(json.dumps(_jsonable({"comparisons": report.comparisons, "real_tensions": report.real_tensions}), indent=2, sort_keys=True) + "\n")
