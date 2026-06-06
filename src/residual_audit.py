"""Residual diagnostics for the BHSM prediction/screen ledger.

This module audits existing model outputs. It does not tune parameters or
modify prediction values.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite, log10
from pathlib import Path
from typing import Any, Iterable

from prediction_ledger import Prediction


SEVERITIES = {
    "EXACT_OR_STATUS",
    "EXCELLENT",
    "GOOD",
    "MODERATE",
    "WEAK",
    "FAIL",
    "SCHEME_SENSITIVE",
    "PLACEHOLDER",
}


@dataclass(frozen=True)
class ResidualSummary:
    """One residual diagnostic row."""

    prediction_id: str
    sector: str
    quantity: str
    predicted: Any
    reference: Any
    absolute_error: float | None
    relative_error: float | None
    log_error: float | None
    severity: str
    notes: tuple[str, ...]


def log_error(predicted: Any, reference: Any) -> float | None:
    """Return log10(predicted/reference) for positive numeric values."""

    if predicted is None or reference is None:
        return None
    try:
        p = float(predicted)
        r = float(reference)
    except (TypeError, ValueError):
        return None
    if p <= 0 or r <= 0:
        return None
    return float(log10(p / r))


def classify_residual(
    relative_error: float | None = None,
    log_error: float | None = None,
    scheme_sensitive: bool = False,
    placeholder: bool = False,
) -> str:
    """Classify residual severity without changing the underlying value."""

    if placeholder:
        return "PLACEHOLDER"
    if scheme_sensitive:
        return "SCHEME_SENSITIVE"
    if relative_error is None:
        return "EXACT_OR_STATUS"
    rel = abs(float(relative_error))
    if rel == 0:
        return "EXACT_OR_STATUS"
    if rel <= 0.01:
        return "EXCELLENT"
    if rel <= 0.05:
        return "GOOD"
    if rel <= 0.25:
        return "MODERATE"
    if rel <= 1.0:
        return "WEAK"
    return "FAIL"


def _is_scheme_sensitive(row: Prediction) -> bool:
    return bool(row.metadata.get("scheme_sensitive", False))


def _is_placeholder(row: Prediction) -> bool:
    return bool(row.metadata.get("placeholder", False) or row.status == "PLACEHOLDER")


def _notes(row: Prediction, log_delta: float | None, scheme_sensitive: bool) -> tuple[str, ...]:
    notes = list(row.limitations)
    if scheme_sensitive:
        notes.append(
            "Quark mass ratio residual is scheme-sensitive because no consistent quark mass-scheme treatment is implemented."
        )
    if log_delta is not None:
        notes.append(
            "Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh."
        )
    if row.relative_error is None:
        notes.append("No numeric reference residual is available for this row.")
    return tuple(notes)


def build_residual_audit(prediction_ledger: Iterable[Prediction]) -> list[ResidualSummary]:
    """Build residual diagnostics from prediction ledger rows."""

    audit: list[ResidualSummary] = []
    for row in prediction_ledger:
        log_delta = log_error(row.predicted, row.reference)
        scheme_sensitive = _is_scheme_sensitive(row)
        severity = classify_residual(
            relative_error=row.relative_error,
            log_error=log_delta,
            scheme_sensitive=scheme_sensitive,
            placeholder=_is_placeholder(row),
        )
        audit.append(
            ResidualSummary(
                prediction_id=row.id,
                sector=row.sector,
                quantity=row.quantity,
                predicted=row.predicted,
                reference=row.reference,
                absolute_error=row.absolute_error,
                relative_error=row.relative_error,
                log_error=log_delta,
                severity=severity,
                notes=_notes(row, log_delta, scheme_sensitive),
            )
        )
    return audit


def _rank_value(row: ResidualSummary) -> float:
    if row.relative_error is not None and isfinite(float(row.relative_error)):
        return abs(float(row.relative_error))
    if row.log_error is not None and isfinite(float(row.log_error)):
        return abs(float(row.log_error))
    return -1.0


def worst_residuals(audit: Iterable[ResidualSummary], n: int = 10) -> list[ResidualSummary]:
    """Return the n largest numeric residuals."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    return sorted(list(audit), key=_rank_value, reverse=True)[:n]


def sector_residual_summary(audit: Iterable[ResidualSummary]) -> dict[str, dict[str, object]]:
    """Summarize residual counts and worst rows by sector."""

    rows = list(audit)
    sectors = sorted({row.sector for row in rows})
    summary: dict[str, dict[str, object]] = {}
    for sector in sectors:
        sector_rows = [row for row in rows if row.sector == sector]
        finite_rel = [
            abs(float(row.relative_error))
            for row in sector_rows
            if row.relative_error is not None and isfinite(float(row.relative_error))
        ]
        severity_counts: dict[str, int] = {}
        for row in sector_rows:
            severity_counts[row.severity] = severity_counts.get(row.severity, 0) + 1
        worst = worst_residuals(sector_rows, n=1)
        summary[sector] = {
            "count": len(sector_rows),
            "finite_relative_error_count": len(finite_rel),
            "best_relative_error": min(finite_rel) if finite_rel else None,
            "worst_relative_error": max(finite_rel) if finite_rel else None,
            "worst_prediction_id": worst[0].prediction_id if worst else None,
            "severity_counts": severity_counts,
        }
    return summary


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def export_residual_audit_json(audit: Iterable[ResidualSummary], path: str | Path) -> None:
    """Export residual audit rows as JSON."""

    data = [_jsonable(asdict(row)) for row in audit]
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def export_residual_audit_markdown(audit: Iterable[ResidualSummary], path: str | Path) -> None:
    """Export residual audit rows as Markdown."""

    rows = list(audit)
    lines = [
        "# BHSM Residual Audit",
        "",
        "This is a diagnostic residual audit. No model parameters are tuned in this phase.",
        "",
        "| Prediction ID | Sector | Quantity | Predicted | Reference | Relative Error | Log Error | Severity | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        rel = "" if row.relative_error is None else f"{row.relative_error:.12g}"
        log_delta = "" if row.log_error is None else f"{row.log_error:.12g}"
        lines.append(
            "| `{}` | {} | {} | `{}` | `{}` | {} | {} | `{}` | {} |".format(
                row.prediction_id,
                row.sector,
                row.quantity,
                _jsonable(row.predicted),
                _jsonable(row.reference),
                rel,
                log_delta,
                row.severity,
                "<br>".join(row.notes),
            )
        )
    lines.extend(
        [
            "",
            "## Sector Summary",
            "",
            "```json",
            json.dumps(sector_residual_summary(rows), indent=2, sort_keys=True),
            "```",
        ]
    )
    Path(path).write_text("\n".join(lines) + "\n")
