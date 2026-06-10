"""BHSM v2.10 mixed curvature contraction audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mixed_connection_coefficients import MIXED_COEFFICIENT_OPEN, build_mixed_connection_coefficients_report


MIXED_CURVATURE_DERIVED = "MIXED_CURVATURE_DERIVED"
MIXED_CURVATURE_CONDITIONAL = "MIXED_CURVATURE_CONDITIONAL"
MIXED_CURVATURE_OPEN = "MIXED_CURVATURE_OPEN"
FAILS_MIXED_CURVATURE = "FAILS_MIXED_CURVATURE"


@dataclass(frozen=True)
class MixedCurvatureContractionReport:
    title: str
    coefficient_status: str
    curvature_symbol: str
    contribution_to_f_bh: str
    mapped_to: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_mixed_curvature_contraction_report() -> MixedCurvatureContractionReport:
    coeffs = build_mixed_connection_coefficients_report()
    status = MIXED_CURVATURE_OPEN if coeffs.status == MIXED_COEFFICIENT_OPEN else MIXED_CURVATURE_DERIVED
    return MixedCurvatureContractionReport(
        title="BHSM v2.10 Mixed Curvature Contraction Report",
        coefficient_status=coeffs.status,
        curvature_symbol="F_mixed = sum_{i<j} C_ij [nabla_i,nabla_j]",
        contribution_to_f_bh="mixed contribution to F_BH = [nabla_BH,nabla_BH]",
        mapped_to="lichnerowicz_bundle_curvature_remainder",
        status=status,
        theorem_complete=status == MIXED_CURVATURE_DERIVED,
        limitations=(
            "F_mixed cannot be computed without the mixed coefficient rule.",
            "The contribution remains mapped to R_bundle.",
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


def export_mixed_curvature_contraction_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mixed_curvature_contraction_report()), indent=2, sort_keys=True) + "\n")


def export_mixed_curvature_contraction_markdown(path: str | Path) -> None:
    report = build_mixed_curvature_contraction_report()
    lines = [
        "# BHSM v2.10 Mixed Curvature Contraction Report",
        "",
        f"Coefficient status: `{report.coefficient_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        f"Curvature symbol: `{report.curvature_symbol}`",
        f"Contribution: `{report.contribution_to_f_bh}`",
        f"Mapped to: `{report.mapped_to}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
