"""BHSM v2.8 sector-action audit for the curvature remainder."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from curvature_remainder_basis_action import REMAINDER_BASIS_ACTION_OPEN, build_curvature_remainder_basis_action_report


@dataclass(frozen=True)
class SectorActionRow:
    sector: str
    action_status: str
    known_represented_terms: tuple[str, ...]
    remainder_action: str
    mirror_risk: str
    limitation: str


@dataclass(frozen=True)
class CurvatureRemainderSectorActionReport:
    title: str
    basis_action_status: str
    rows: tuple[SectorActionRow, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_curvature_remainder_sector_action_report() -> CurvatureRemainderSectorActionReport:
    basis = build_curvature_remainder_basis_action_report()
    rows = (
        SectorActionRow("lepton", "OPEN", ("V_Hopf", "V_boundary", "V_chi"), "not derived for R_bundle", "OPEN", "Lepton-sector curvature remainder cannot be separated from the missing mixed contraction."),
        SectorActionRow("up", "OPEN", ("V_Hopf", "V_boundary", "V_chi", "K_sector"), "not derived for R_bundle", "OPEN", "Up-sector curvature remainder may be affected by sector/coframe connection terms."),
        SectorActionRow("down", "OPEN", ("V_Hopf", "V_boundary", "V_chi", "K_sector"), "not derived for R_bundle", "OPEN", "Down-sector curvature remainder may be affected by sector/coframe connection terms."),
    )
    return CurvatureRemainderSectorActionReport(
        title="BHSM v2.8 Curvature Remainder Sector Action Report",
        basis_action_status=basis.status,
        rows=rows,
        status="REMAINDER_SECTOR_ACTION_OPEN" if basis.status == REMAINDER_BASIS_ACTION_OPEN else "REMAINDER_SECTOR_ACTION_CONDITIONAL",
        theorem_complete=False,
        limitations=(
            "Known sector operators remain represented, but the extra curvature remainder action is not derived.",
            "No sector is assumed safe by fit or by analogy.",
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


def export_curvature_remainder_sector_action_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_curvature_remainder_sector_action_report()), indent=2, sort_keys=True) + "\n")


def export_curvature_remainder_sector_action_markdown(path: str | Path) -> None:
    report = build_curvature_remainder_sector_action_report()
    lines = [
        "# BHSM v2.8 Curvature Remainder Sector Action Report",
        "",
        f"Basis-action status: `{report.basis_action_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Sector | Action status | Known represented terms | Remainder action | Mirror risk | Limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.sector}` | `{row.action_status}` | `{row.known_represented_terms}` | {row.remainder_action} | `{row.mirror_risk}` | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
