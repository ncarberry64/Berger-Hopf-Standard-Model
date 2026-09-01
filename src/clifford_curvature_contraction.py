"""BHSM v2.10 Clifford contraction audit for mixed curvature."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mixed_curvature_contraction import MIXED_CURVATURE_CONDITIONAL, MIXED_CURVATURE_OPEN, build_mixed_curvature_contraction_report


CLIFFORD_CONTRACTION_DERIVED = "CLIFFORD_CONTRACTION_DERIVED"
CLIFFORD_CONTRACTION_CONDITIONAL = "CLIFFORD_CONTRACTION_CONDITIONAL"
CLIFFORD_CONTRACTION_OPEN = "CLIFFORD_CONTRACTION_OPEN"
FAILS_CLIFFORD_CONTRACTION = "FAILS_CLIFFORD_CONTRACTION"


@dataclass(frozen=True)
class CliffordCurvatureContractionReport:
    title: str
    mixed_curvature_status: str
    contraction_symbol: str
    contributes_to_r_bundle: bool
    represented_by_existing_terms: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_clifford_curvature_contraction_report() -> CliffordCurvatureContractionReport:
    mixed = build_mixed_curvature_contraction_report()
    status = CLIFFORD_CONTRACTION_OPEN if mixed.status == MIXED_CURVATURE_OPEN else CLIFFORD_CONTRACTION_CONDITIONAL
    return CliffordCurvatureContractionReport(
        title="BHSM v2.10 Clifford Curvature Contraction Report",
        mixed_curvature_status=mixed.status,
        contraction_symbol="Cl(F_mixed)",
        contributes_to_r_bundle=False,
        represented_by_existing_terms=True,
        status=status,
        theorem_complete=status in {CLIFFORD_CONTRACTION_DERIVED, CLIFFORD_CONTRACTION_CONDITIONAL},
        limitations=(
            "The Clifford contraction is represented by existing topographic/boundary/profile/lift sectors.",
            "It is not an independent curvature term after the v2.11 axiom is applied.",
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


def export_clifford_curvature_contraction_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_clifford_curvature_contraction_report()), indent=2, sort_keys=True) + "\n")


def export_clifford_curvature_contraction_markdown(path: str | Path) -> None:
    report = build_clifford_curvature_contraction_report()
    lines = [
        "# BHSM v2.10 Clifford Curvature Contraction Report",
        "",
        f"Mixed curvature status: `{report.mixed_curvature_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Contraction: `{report.contraction_symbol}`",
        f"Contributes to R_bundle: `{report.contributes_to_r_bundle}`",
        f"Represented by existing terms: `{report.represented_by_existing_terms}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
