"""BHSM v2.12 topographic representation of curvature contributions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_curvature_term_map import CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, build_bundle_curvature_term_map_report
from mixed_coefficient_rule_decision import MIXED_COEFFICIENT_RULE_CLOSED, build_mixed_coefficient_rule_decision


TOPOGRAPHIC_CURVATURE_REPRESENTATION_CLOSED = "TOPOGRAPHIC_CURVATURE_REPRESENTATION_CLOSED"
TOPOGRAPHIC_CURVATURE_REPRESENTATION_OPEN = "TOPOGRAPHIC_CURVATURE_REPRESENTATION_OPEN"


@dataclass(frozen=True)
class TopographicCurvatureRepresentationReport:
    title: str
    mixed_rule_result: str
    represented_terms: tuple[str, ...]
    mapped_to: str
    contributes_independent_r_bundle: bool
    lower_bound_requires_new_term: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_topographic_curvature_representation_report() -> TopographicCurvatureRepresentationReport:
    mixed = build_mixed_coefficient_rule_decision()
    term_map = build_bundle_curvature_term_map_report()
    represented = tuple(row.contribution_id for row in term_map.rows if row.classification == CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR)
    closed = mixed.final_result == MIXED_COEFFICIENT_RULE_CLOSED and represented and not term_map.r_bundle_contributors
    return TopographicCurvatureRepresentationReport(
        title="BHSM v2.12 Topographic Curvature Representation Report",
        mixed_rule_result=mixed.final_result,
        represented_terms=represented,
        mapped_to="V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift",
        contributes_independent_r_bundle=False,
        lower_bound_requires_new_term=False,
        status=TOPOGRAPHIC_CURVATURE_REPRESENTATION_CLOSED if closed else TOPOGRAPHIC_CURVATURE_REPRESENTATION_OPEN,
        theorem_complete=bool(closed),
        limitations=(
            "Topographic representation closes the mixed curvature formula contribution only.",
            "It does not replace downstream scalar/topographic, projector, index, or mirror theorem checks.",
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


def export_topographic_curvature_representation_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_topographic_curvature_representation_report()), indent=2, sort_keys=True) + "\n")


def export_topographic_curvature_representation_markdown(path: str | Path) -> None:
    report = build_topographic_curvature_representation_report()
    lines = [
        "# BHSM v2.12 Topographic Curvature Representation Report",
        "",
        f"Mixed rule result: `{report.mixed_rule_result}`",
        f"Status: `{report.status}`",
        f"Mapped to: `{report.mapped_to}`",
        f"Independent R_bundle contribution: `{report.contributes_independent_r_bundle}`",
        f"New lower-bound term required: `{report.lower_bound_requires_new_term}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Represented Terms",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.represented_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

