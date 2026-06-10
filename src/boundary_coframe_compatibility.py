"""BHSM v2.11 boundary/coframe compatibility audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from coframe_compatibility_rule import build_coframe_compatibility_rule_report


BOUNDARY_COFRAME_CONSTRAINED = "BOUNDARY_COFRAME_CONSTRAINED"
BOUNDARY_COFRAME_REPRESENTED = "BOUNDARY_COFRAME_REPRESENTED"
BOUNDARY_COFRAME_OPEN = "BOUNDARY_COFRAME_OPEN"


@dataclass(frozen=True)
class BoundaryCoframeCompatibilityRow:
    sector: str
    boundary_rule: str
    coframe_channel: str
    coefficient_status: str
    conclusion: str
    limitation: str


@dataclass(frozen=True)
class BoundaryCoframeCompatibilityReport:
    title: str
    rows: tuple[BoundaryCoframeCompatibilityRow, ...]
    status: str
    missing_axiom: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_boundary_coframe_compatibility_report() -> BoundaryCoframeCompatibilityReport:
    coframe = build_coframe_compatibility_rule_report()
    rows = (
        BoundaryCoframeCompatibilityRow(
            "lepton",
            "Omega_l=-q+2j=3",
            "no quark coframe triplet",
            BOUNDARY_COFRAME_CONSTRAINED,
            "lepton sector supplies a control case with no coframe triplet coefficient",
            "Control case does not introduce an independent mixed coefficient.",
        ),
        BoundaryCoframeCompatibilityRow(
            "up",
            "Omega_u=q-2j=6",
            "coframe triplet participates",
            BOUNDARY_COFRAME_REPRESENTED,
            "up-sector boundary/coframe cross coefficient is represented by V_PSD/profile",
            "Full profile positivity remains a separate H_T dependency.",
        ),
        BoundaryCoframeCompatibilityRow(
            "down",
            "Omega_d=q+4j=12",
            "coframe triplet participates",
            BOUNDARY_COFRAME_REPRESENTED,
            "down-sector boundary/coframe cross coefficient is represented by V_PSD/profile",
            "Full profile positivity remains a separate H_T dependency.",
        ),
    )
    fixed = coframe.coefficient_rule_fixed
    return BoundaryCoframeCompatibilityReport(
        title="BHSM v2.11 Boundary/Coframe Compatibility Report",
        rows=rows,
        status=BOUNDARY_COFRAME_REPRESENTED if fixed else BOUNDARY_COFRAME_OPEN,
        missing_axiom="" if fixed else "MIXED_CONNECTION_COMPATIBILITY_AXIOM_GAP",
        theorem_complete=fixed,
        limitations=(
            "Boundary/coframe coefficients are represented through existing BHSM topographic/profile sectors.",
            "No prediction residual is used to choose a boundary/coframe coefficient.",
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


def export_boundary_coframe_compatibility_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_boundary_coframe_compatibility_report()), indent=2, sort_keys=True) + "\n")


def export_boundary_coframe_compatibility_markdown(path: str | Path) -> None:
    report = build_boundary_coframe_compatibility_report()
    lines = [
        "# BHSM v2.11 Boundary/Coframe Compatibility Report",
        "",
        f"Status: `{report.status}`",
        f"Missing axiom: `{report.missing_axiom}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Sector | Boundary rule | Coframe channel | Coefficient status | Conclusion | Limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.sector}` | `{row.boundary_rule}` | {row.coframe_channel} | `{row.coefficient_status}` | {row.conclusion} | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

