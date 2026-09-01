"""BHSM v2.11 Hopf/base mixed coefficient-rule audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from topographic_representation_rule import build_topographic_representation_rule_report


HOPF_BASE_MIXED_CONSTRAINED = "HOPF_BASE_MIXED_CONSTRAINED"
HOPF_BASE_MIXED_REPRESENTED = "HOPF_BASE_MIXED_REPRESENTED"
HOPF_BASE_MIXED_OPEN = "HOPF_BASE_MIXED_OPEN"


@dataclass(frozen=True)
class HopfBaseMixedRow:
    rule_id: str
    geometric_input: str
    coefficient_slot: str
    conclusion: str
    status: str
    limitation: str


@dataclass(frozen=True)
class HopfBaseMixedRuleReport:
    title: str
    rows: tuple[HopfBaseMixedRow, ...]
    preserves_formal_kernel: bool | None
    preserves_h_perp: bool | None
    status: str
    missing_axiom: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_hopf_base_mixed_rule_report() -> HopfBaseMixedRuleReport:
    representation = build_topographic_representation_rule_report()
    rows = (
        HopfBaseMixedRow(
            "vertical_horizontal_split",
            "Hopf fiber/base splitting in Berger-Hopf geometry",
            "hopf_fiber_base_cross",
            "cross curvature is zero/absorbed by vertical-horizontal compatibility",
            HOPF_BASE_MIXED_REPRESENTED,
            "This is a representation rule, not a new fitted coefficient.",
        ),
        HopfBaseMixedRow(
            "boundary_phase_coupling",
            "Higgs-selected U(1) boundary phase and Omega_f",
            "base_boundary_cross",
            "sector-sensitive boundary/base mixing is represented by V_boundary",
            HOPF_BASE_MIXED_REPRESENTED,
            "Boundary phase remains in the existing boundary sector.",
        ),
        HopfBaseMixedRow(
            "formal_kernel_safety",
            "formal protected kernel coordinates (0,18,36)",
            "hopf_boundary_coframe_mixed",
            "mixed contribution is not an independent curvature source on the formal kernel",
            HOPF_BASE_MIXED_REPRESENTED,
            "Full H_T proof still requires downstream operator-domain dependencies.",
        ),
    )
    fixed = representation.all_slots_represented_or_zero
    return HopfBaseMixedRuleReport(
        title="BHSM v2.11 Hopf/Base Mixed Rule Report",
        rows=rows,
        preserves_formal_kernel=True if fixed else None,
        preserves_h_perp=True if fixed else None,
        status=HOPF_BASE_MIXED_REPRESENTED if fixed else HOPF_BASE_MIXED_OPEN,
        missing_axiom="" if fixed else "MIXED_CONNECTION_COMPATIBILITY_AXIOM_GAP",
        theorem_complete=fixed,
        limitations=(
            "The Hopf/base mixed rule is closed as a representation/compatibility rule, not as a numerical coefficient.",
            "No coefficient is selected from empirical outputs.",
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


def export_hopf_base_mixed_rule_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_hopf_base_mixed_rule_report()), indent=2, sort_keys=True) + "\n")


def export_hopf_base_mixed_rule_markdown(path: str | Path) -> None:
    report = build_hopf_base_mixed_rule_report()
    lines = [
        "# BHSM v2.11 Hopf/Base Mixed Rule Report",
        "",
        f"Status: `{report.status}`",
        f"Missing axiom: `{report.missing_axiom}`",
        f"Preserves formal kernel: `{report.preserves_formal_kernel}`",
        f"Preserves H_perp: `{report.preserves_h_perp}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Rule | Geometric input | Coefficient slot | Conclusion | Status | Limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.rule_id}` | {row.geometric_input} | `{row.coefficient_slot}` | {row.conclusion} | `{row.status}` | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

