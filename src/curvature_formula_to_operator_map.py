"""BHSM v2.9 map from curvature formula contributions to operator terms."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_curvature_formula import build_bundle_curvature_formula_report


@dataclass(frozen=True)
class OperatorMapRow:
    contribution_id: str
    mapped_to: str
    classification: str
    limitation: str


@dataclass(frozen=True)
class CurvatureFormulaToOperatorMapReport:
    title: str
    rows: tuple[OperatorMapRow, ...]
    all_contributions_classified: bool
    r_bundle_rows: tuple[str, ...]
    r_bundle_classification: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_formula_to_operator_map_report() -> CurvatureFormulaToOperatorMapReport:
    formula = build_bundle_curvature_formula_report()
    rows = tuple(
        OperatorMapRow(
            contribution_id=row.contribution_id,
            mapped_to=row.mapped_operator_term,
            classification="REMAINDER_OPEN" if row.mapped_operator_term == "new R_bundle" else "MAPPED_TO_EXISTING_OPERATOR_PACKAGE",
            limitation=row.limitation,
        )
        for row in formula.contributions
    )
    r_bundle = tuple(row.contribution_id for row in rows if row.mapped_to == "new R_bundle")
    return CurvatureFormulaToOperatorMapReport(
        title="BHSM v2.9 Curvature Formula to Operator Map",
        rows=rows,
        all_contributions_classified=all(row.classification for row in rows),
        r_bundle_rows=r_bundle,
        r_bundle_classification="REMAINDER_OPEN" if r_bundle else "REMAINDER_ZERO",
        theorem_complete=False,
        limitations=(
            "Every curvature contribution is classified.",
            "The mixed curvature contribution maps to new R_bundle and remains open.",
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


def export_curvature_formula_to_operator_map_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_formula_to_operator_map_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_formula_to_operator_map_markdown(path: str | Path) -> None:
    report = build_curvature_formula_to_operator_map_report()
    lines = [
        "# BHSM v2.9 Curvature Formula to Operator Map",
        "",
        f"All contributions classified: `{report.all_contributions_classified}`",
        f"R_bundle classification: `{report.r_bundle_classification}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Contribution | Mapped to | Classification | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.contribution_id}` | `{row.mapped_to}` | `{row.classification}` | {row.limitation} |")
    lines.extend(["", "## R_bundle Rows", ""])
    lines.extend(f"- `{item}`" for item in report.r_bundle_rows)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
