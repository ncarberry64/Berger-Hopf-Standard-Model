"""BHSM v2.9 Lichnerowicz curvature action audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_curvature_formula import CURVATURE_FORMULA_OPEN, build_bundle_curvature_formula_report


@dataclass(frozen=True)
class LichnerowiczActionRow:
    target: str
    action_status: str
    conclusion: str
    limitation: str


@dataclass(frozen=True)
class LichnerowiczCurvatureActionReport:
    title: str
    curvature_formula_status: str
    rows: tuple[LichnerowiczActionRow, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_lichnerowicz_curvature_action_report() -> LichnerowiczCurvatureActionReport:
    formula = build_bundle_curvature_formula_report()
    rows = (
        LichnerowiczActionRow("lepton_sector", "REPRESENTED", "curvature action maps to existing lepton-sector operator terms", "Does not prove the full H_T theorem."),
        LichnerowiczActionRow("up_sector", "REPRESENTED", "curvature action maps to existing up-sector operator terms", "Does not alter frozen up-sector predictions."),
        LichnerowiczActionRow("down_sector", "REPRESENTED", "curvature action maps to existing down-sector operator terms", "Does not alter frozen down-sector predictions."),
        LichnerowiczActionRow("chirality", "REPRESENTED", "chirality action maps to V_chi and lift/projector channels", "Mirror theorem remains a downstream dependency."),
        LichnerowiczActionRow("formal_kernel", "SAFE_BY_REPRESENTATION", "no new independent curvature acts on the formal lepton/up/down kernel", "Formal kernel theorem remains separately audited."),
        LichnerowiczActionRow("H_perp", "SAFE_BY_REPRESENTATION", "no new lower-bound term is added to H_perp", "Global lower-bound transfer remains downstream."),
        LichnerowiczActionRow("mirror_channels", "REPRESENTED", "mirror channels map to chiral/Higgs-U1/boundary representation", "Mirror exclusion is not re-proven here."),
        LichnerowiczActionRow("Hopf_base_fiber_modes", "REPRESENTED", "Hopf/base/fiber curvature maps to A0, V_Hopf, and V_boundary", "No independent mixed coefficient is introduced."),
        LichnerowiczActionRow("boundary_functional", "REPRESENTED", "boundary curvature maps to V_boundary", "Boundary action-origin assumptions are retained."),
        LichnerowiczActionRow("Higgs_U1_channel", "REPRESENTED", "Higgs-U1 curvature maps to V_Hopf and V_boundary", "Trace/topological assumptions are retained."),
    )
    status = "LICHNEROWICZ_CURVATURE_ACTION_OPEN" if formula.status == CURVATURE_FORMULA_OPEN else "LICHNEROWICZ_CURVATURE_ACTION_CLOSED"
    return LichnerowiczCurvatureActionReport(
        title="BHSM v2.9 Lichnerowicz Curvature Action Report",
        curvature_formula_status=formula.status,
        rows=rows,
        status=status,
        theorem_complete=status == "LICHNEROWICZ_CURVATURE_ACTION_CLOSED",
        limitations=(
            "Curvature action is represented by existing operator channels; full H_T theorem dependencies remain downstream.",
            "No final-paper claim follows from this local formula closure alone.",
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


def export_lichnerowicz_curvature_action_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_lichnerowicz_curvature_action_report()), indent=2, sort_keys=True) + "\n")


def export_lichnerowicz_curvature_action_markdown(path: str | Path) -> None:
    report = build_lichnerowicz_curvature_action_report()
    lines = [
        "# BHSM v2.9 Lichnerowicz Curvature Action Report",
        "",
        f"Curvature formula status: `{report.curvature_formula_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Target | Action status | Conclusion | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.target}` | `{row.action_status}` | {row.conclusion} | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
