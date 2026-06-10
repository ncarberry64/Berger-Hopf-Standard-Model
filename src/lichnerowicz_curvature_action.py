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
        LichnerowiczActionRow("lepton_sector", "OPEN", "mixed remainder action not computed", "Requires mixed connection coefficients."),
        LichnerowiczActionRow("up_sector", "OPEN", "mixed remainder action not computed", "Requires mixed connection coefficients."),
        LichnerowiczActionRow("down_sector", "OPEN", "mixed remainder action not computed", "Requires mixed connection coefficients."),
        LichnerowiczActionRow("chirality", "OPEN", "chirality preservation or mixing not determined", "Requires Clifford contraction of mixed curvature."),
        LichnerowiczActionRow("formal_kernel", "OPEN", "not proven to vanish on lepton/up/down formal kernel", "Requires explicit action on protected states."),
        LichnerowiczActionRow("H_perp", "OPEN", "not proven lower-bound safe on complement", "Requires PSD/relative-bound/screening proof."),
        LichnerowiczActionRow("mirror_channels", "OPEN", "mirror leakage not excluded", "Requires chirality-resolved mixed curvature action."),
        LichnerowiczActionRow("Hopf_base_fiber_modes", "OPEN", "mixed mode dependence not determined", "Requires complete Hopf/base/fiber mixed curvature formula."),
        LichnerowiczActionRow("boundary_functional", "OPEN", "mixed boundary action not determined", "Requires complete boundary curvature coefficients."),
        LichnerowiczActionRow("Higgs_U1_channel", "OPEN", "mixed Higgs-U1 action not determined", "Requires complete Higgs-U1 curvature contraction."),
    )
    status = "LICHNEROWICZ_CURVATURE_ACTION_OPEN" if formula.status == CURVATURE_FORMULA_OPEN else "LICHNEROWICZ_CURVATURE_ACTION_CONDITIONAL"
    return LichnerowiczCurvatureActionReport(
        title="BHSM v2.9 Lichnerowicz Curvature Action Report",
        curvature_formula_status=formula.status,
        rows=rows,
        status=status,
        theorem_complete=False,
        limitations=(
            "The action of the mixed curvature remainder cannot be computed without the missing connection component.",
            "No kernel/complement or mirror safety claim follows from the current data.",
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
