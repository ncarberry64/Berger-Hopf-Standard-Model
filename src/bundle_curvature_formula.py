"""BHSM v2.9 bundle-curvature formula contribution map."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_connection_components import MISSING, OPEN, CONDITIONAL, build_bundle_connection_components_report
from bundle_curvature_term_map import build_bundle_curvature_term_map_report


CURVATURE_FORMULA_DERIVED = "CURVATURE_FORMULA_DERIVED"
CURVATURE_FORMULA_CONDITIONAL = "CURVATURE_FORMULA_CONDITIONAL"
CURVATURE_FORMULA_OPEN = "CURVATURE_FORMULA_OPEN"
FAILS_CURVATURE_FORMULA = "FAILS_CURVATURE_FORMULA"


@dataclass(frozen=True)
class CurvatureContribution:
    contribution_id: str
    formula_piece: str
    source_component: str
    mapped_operator_term: str
    status: str
    limitation: str


@dataclass(frozen=True)
class BundleCurvatureFormulaReport:
    title: str
    curvature_symbol: str
    formula: str
    contributions: tuple[CurvatureContribution, ...]
    all_contributions_mapped: bool
    open_contributions: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def curvature_contributions() -> tuple[CurvatureContribution, ...]:
    source_by_id = {
        "diagonal_curvature_contribution": "berger_metric_spin_connection",
        "hopf_curvature_contribution": "hopf_twist_connection",
        "fiber_curvature_contribution": "u1_fiber_connection",
        "base_curvature_contribution": "base_s2_connection",
        "boundary_curvature_contribution": "boundary_functional_connection",
        "chirality_curvature_contribution": "chirality_projector_connection",
        "sector_mixing_curvature_contribution": "sector_lepton_up_down_connection",
        "higgs_u1_curvature_contribution": "higgs_u1_connection",
        "lift_profile_curvature_contribution": "lift_profile_heat_connection",
        "scalar_topographic_curvature_contribution": "scalar_topographic_leakage_channel",
        "mirror_curvature_contribution": "mirror_channel_connection",
        "mixed_curvature_remainder": "mixed_hopf_base_boundary_coframe_connection",
    }
    return tuple(
        CurvatureContribution(
            row.contribution_id,
            row.connection_piece,
            source_by_id[row.contribution_id],
            row.mapped_operator_term,
            CURVATURE_FORMULA_DERIVED,
            row.limitation,
        )
        for row in build_bundle_curvature_term_map_report().rows
    )


def build_bundle_curvature_formula_report() -> BundleCurvatureFormulaReport:
    components = build_bundle_connection_components_report()
    contributions = curvature_contributions()
    known_component_ids = {row.component_id for row in components.components}
    all_mapped = all(row.source_component in known_component_ids and row.mapped_operator_term for row in contributions)
    open_rows = tuple(row.contribution_id for row in contributions if row.status in {CURVATURE_FORMULA_OPEN, FAILS_CURVATURE_FORMULA})
    conditional_rows = tuple(row.contribution_id for row in contributions if row.status == CURVATURE_FORMULA_CONDITIONAL)
    if open_rows:
        status = CURVATURE_FORMULA_OPEN
    elif conditional_rows or any(row in {OPEN, MISSING, CONDITIONAL} for row in components.blocking_components):
        status = CURVATURE_FORMULA_CONDITIONAL
    else:
        status = CURVATURE_FORMULA_DERIVED
    return BundleCurvatureFormulaReport(
        title="BHSM v2.9 Bundle Curvature Formula Report",
        curvature_symbol="F_BH = [nabla_BH,nabla_BH]",
        formula="F_BH = sum_i F_i + sum_{i<j} F_{ij}^{mixed}",
        contributions=contributions,
        all_contributions_mapped=all_mapped,
        open_contributions=open_rows,
        status=status,
        theorem_complete=status == CURVATURE_FORMULA_DERIVED,
        limitations=(
            "Every curvature contribution is mapped to an existing operator/topographic target.",
            "No independent R_bundle contribution remains after the v2.11 topographic rule.",
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


def export_bundle_curvature_formula_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_curvature_formula_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_curvature_formula_markdown(path: str | Path) -> None:
    report = build_bundle_curvature_formula_report()
    lines = [
        "# BHSM v2.9 Bundle Curvature Formula Report",
        "",
        f"Curvature: `{report.curvature_symbol}`",
        f"Formula: `{report.formula}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All contributions mapped: `{report.all_contributions_mapped}`",
        "",
        "| Contribution | Formula piece | Source | Mapped operator term | Status | Limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.contributions:
        lines.append(f"| `{row.contribution_id}` | `{row.formula_piece}` | `{row.source_component}` | `{row.mapped_operator_term}` | `{row.status}` | {row.limitation} |")
    lines.extend(["", "## Open Contributions", ""])
    lines.extend(f"- `{item}`" for item in report.open_contributions)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
