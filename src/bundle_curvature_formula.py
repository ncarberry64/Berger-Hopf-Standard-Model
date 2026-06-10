"""BHSM v2.9 bundle-curvature formula contribution map."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_connection_components import MISSING, OPEN, CONDITIONAL, build_bundle_connection_components_report
from mixed_connection_closure_decision import MIXED_CONNECTION_CLOSED, build_mixed_connection_closure_decision


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
    mixed = build_mixed_connection_closure_decision()
    mixed_status = CURVATURE_FORMULA_CONDITIONAL if mixed.final_result == MIXED_CONNECTION_CLOSED else CURVATURE_FORMULA_OPEN
    mixed_target = "V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift" if mixed.final_result == MIXED_CONNECTION_CLOSED else "new R_bundle"
    mixed_limitation = "v2.11 represents mixed contribution through existing sectors; no independent coefficient remains." if mixed.final_result == MIXED_CONNECTION_CLOSED else "The mixed connection coefficients and Clifford contraction are not defined."
    return (
        CurvatureContribution("diagonal_curvature_contribution", "[nabla_Berger,nabla_Berger]", "berger_metric_spin_connection", "A0", CURVATURE_FORMULA_DERIVED, "Diagonal curvature is represented by the reference operator package."),
        CurvatureContribution("hopf_curvature_contribution", "[nabla_Hopf,nabla_Hopf]", "hopf_twist_connection", "V_Hopf", CURVATURE_FORMULA_DERIVED, "Hopf contribution is represented at the symbolic operator level."),
        CurvatureContribution("fiber_curvature_contribution", "[nabla_U1/fiber,nabla_U1/fiber]", "u1_fiber_connection", "V_Hopf + V_boundary", CURVATURE_FORMULA_DERIVED, "Trace/topological assumptions remain inherited."),
        CurvatureContribution("base_curvature_contribution", "[nabla_base,nabla_base]", "base_s2_connection", "A0 + V_boundary", CURVATURE_FORMULA_DERIVED, "Mixed base/fiber terms are not included here."),
        CurvatureContribution("boundary_curvature_contribution", "[nabla_boundary,nabla_boundary]", "boundary_functional_connection", "V_boundary", CURVATURE_FORMULA_DERIVED, "Uses v1.2/v2 boundary functional scaffold."),
        CurvatureContribution("chirality_curvature_contribution", "[nabla_chi,nabla_chi]", "chirality_projector_connection", "V_chi", CURVATURE_FORMULA_DERIVED, "Mixed chirality curvature is handled by the mixed remainder row."),
        CurvatureContribution("sector_mixing_curvature_contribution", "[nabla_sector,nabla_sector]", "sector_lepton_up_down_connection", "K_sector", CURVATURE_FORMULA_CONDITIONAL, "Sector curvature is represented but coefficients remain scaffold-level."),
        CurvatureContribution("higgs_u1_curvature_contribution", "[nabla_Higgs-U1,nabla_Higgs-U1]", "higgs_u1_connection", "V_Hopf + V_boundary", CURVATURE_FORMULA_CONDITIONAL, "Mirror-channel curvature action remains conditional."),
        CurvatureContribution("lift_profile_curvature_contribution", "[nabla_lift/profile,nabla_lift/profile]", "lift_profile_heat_connection", "P_perp_lift + V_PSD", CURVATURE_FORMULA_CONDITIONAL, "Safe only when mapped into lift/profile package."),
        CurvatureContribution("scalar_topographic_curvature_contribution", "[nabla_scalar/topographic,nabla_scalar/topographic]", "scalar_topographic_leakage_channel", "scalar/topographic screened sector", CURVATURE_FORMULA_CONDITIONAL, "Full scalar proof remains separate."),
        CurvatureContribution("mirror_curvature_contribution", "[nabla_mirror,nabla_mirror]", "mirror_channel_connection", "V_chi + Higgs-U1 + boundary channels", CURVATURE_FORMULA_CONDITIONAL, "Complete mirror curvature remains conditional."),
        CurvatureContribution("mixed_curvature_remainder", "sum_{i<j} [nabla_i,nabla_j] for mixed Hopf/base/boundary/coframe channels", "mixed_hopf_base_boundary_coframe_connection", mixed_target, mixed_status, mixed_limitation),
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
            "Every curvature contribution is mapped to an operator target or to new R_bundle.",
            "The mixed curvature remainder is represented by the v2.11 topographic rule; remaining conditional rows are separate H_T dependencies.",
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
