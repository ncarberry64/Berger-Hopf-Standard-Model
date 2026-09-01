"""Fifth-force exclusion scaffold for BHSM v1.6 scalar screening."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from curvature_screening import CurvatureScreeningCondition, curvature_screening_conditions
from derivative_screening import DerivativeScreeningCondition, derivative_screening_conditions
from scalar_action import OPEN_SCALAR_RISK, action_level_scalar_modes
from scalar_screening_action import (
    FAILS_SCREENING,
    FULL_SCREENING_THEOREM_PROVEN,
    SCREENING_SCAFFOLD_PASSES,
    MatterCouplingRule,
    ScreeningActionTerm,
    matter_coupling_audit,
    screening_action_terms,
)


@dataclass(frozen=True)
class FifthForceExclusionReport:
    """Fifth-force exclusion audit for scalar/topographic modes."""

    rules: tuple[MatterCouplingRule, ...]
    excluded_modes: tuple[str, ...]
    open_scalar_risks: tuple[MatterCouplingRule, ...]
    forbidden_unscreened_modes: tuple[MatterCouplingRule, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ScalarScreeningProofReport:
    """Complete v1.6 scalar/topographic screening proof scaffold."""

    title: str
    screening_action_terms: tuple[ScreeningActionTerm, ...]
    derivative_conditions: tuple[DerivativeScreeningCondition, ...]
    curvature_conditions: tuple[CurvatureScreeningCondition, ...]
    matter_coupling_audit: tuple[MatterCouplingRule, ...]
    fifth_force_exclusion: FifthForceExclusionReport
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def fifth_force_exclusion_report() -> FifthForceExclusionReport:
    """Apply the v1.6 fifth-force exclusion rule to the v1.5 scalar modes."""

    rules = matter_coupling_audit()
    open_risks = tuple(row for row in rules if row.open_coupling_risk)
    forbidden = tuple(row for row in rules if row.forbidden_unscreened_light_coupling)
    excluded = tuple(
        row.mode_id
        for row in rules
        if (
            row.heavy_lifted
            or row.derivative_coupling_only
            or row.curvature_coupling_only
            or row.virtual_only
            or row.higgs_projected_sm_scalar
        )
        and not row.ordinary_on_shell_fifth_force_mediator
    )
    if open_risks:
        status = OPEN_SCALAR_RISK
    elif forbidden:
        status = FAILS_SCREENING
    else:
        status = SCREENING_SCAFFOLD_PASSES
    return FifthForceExclusionReport(
        rules=rules,
        excluded_modes=excluded,
        open_scalar_risks=open_risks,
        forbidden_unscreened_modes=forbidden,
        status=status,
        theorem_complete=False,
        limitations=(
            "Fifth-force exclusion is conditional on the v1.6 screening scaffold.",
            "The full scalar/topographic action proof remains open.",
        ),
    )


def build_scalar_screening_proof_report() -> ScalarScreeningProofReport:
    """Build the v1.6 scalar/topographic screening proof scaffold."""

    exclusion = fifth_force_exclusion_report()
    status = exclusion.status
    if status == SCREENING_SCAFFOLD_PASSES:
        final_status = SCREENING_SCAFFOLD_PASSES
    else:
        final_status = status
    return ScalarScreeningProofReport(
        title="BHSM v1.6 Scalar/Topographic Screening Proof Scaffold",
        screening_action_terms=screening_action_terms(),
        derivative_conditions=derivative_screening_conditions(),
        curvature_conditions=curvature_screening_conditions(),
        matter_coupling_audit=exclusion.rules,
        fifth_force_exclusion=exclusion,
        status=final_status,
        theorem_complete=False,
        limitations=(
            "This is not FULL_SCREENING_THEOREM_PROVEN.",
            "Derivative and curvature screening are sufficient action-level scaffold conditions.",
            "No frozen BHSM predictions, constants, tolerances, mode ledgers, or dressing rules are changed.",
        ),
    )


def explicit_direct_light_scalar_failure() -> MatterCouplingRule:
    """Return a synthetic direct light scalar risk row for tests and reports."""

    from scalar_action import FORBIDDEN_UNSCREENED_LIGHT_SCALAR, ScalarMode

    mode = ScalarMode(
        mode_id="direct_light_scalar_risk",
        label="diagnostic direct-coupled light scalar",
        channel=FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
        effective_mass_gev=1.0,
        coupling_to_matter="direct unscreened matter coupling",
        derivative_screened=False,
        curvature_screened=False,
        virtual_only=False,
        on_shell_light_particle=True,
        status=FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
        limitations=("Diagnostic falsifier row; not part of the current scalar inventory.",),
    )
    return matter_coupling_audit((mode,))[0]


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


def export_scalar_screening_json(path: str | Path) -> None:
    """Export the scalar screening proof scaffold as JSON."""

    payload = {
        "report": build_scalar_screening_proof_report(),
        "direct_light_scalar_failure_example": explicit_direct_light_scalar_failure(),
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_fifth_force_exclusion_json(path: str | Path) -> None:
    """Export the fifth-force exclusion report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(fifth_force_exclusion_report()), indent=2, sort_keys=True) + "\n")


def export_scalar_screening_markdown(path: str | Path) -> None:
    """Export the scalar screening proof scaffold as Markdown."""

    report = build_scalar_screening_proof_report()
    lines = [
        "# BHSM v1.6 Scalar/Topographic Screening Proof Scaffold",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Derivative-Screening Conditions",
        "",
        "| ID | Coupling operator | Static long-range force absent | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.derivative_conditions:
        lines.append(f"| `{row.id}` | `{row.coupling_operator}` | `{row.static_long_range_force_absent}` | `{row.status}` |")
    lines.extend(
        [
            "",
            "## Curvature-Screening Conditions",
            "",
            "| ID | Coupling operator | Curvature source | Flat limit suppresses | Status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.curvature_conditions:
        lines.append(f"| `{row.id}` | `{row.coupling_operator}` | `{row.curvature_source}` | `{row.flat_limit_suppresses}` | `{row.status}` |")
    lines.extend(
        [
            "",
            "## Matter-Coupling Audit",
            "",
            "| Mode | Channel | Direct | Derivative only | Curvature only | Virtual | Heavy | Status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.matter_coupling_audit:
        lines.append(
            f"| `{row.mode_id}` | `{row.channel}` | `{row.direct_matter_coupling}` | `{row.derivative_coupling_only}` | `{row.curvature_coupling_only}` | `{row.virtual_only}` | `{row.heavy_lifted}` | `{row.status}` |"
        )
    lines.extend(
        [
            "",
            "## Fifth-Force Exclusion",
            "",
            f"Excluded modes: `{len(report.fifth_force_exclusion.excluded_modes)}`",
            f"Open scalar risks: `{len(report.fifth_force_exclusion.open_scalar_risks)}`",
            f"Forbidden unscreened modes in current inventory: `{len(report.fifth_force_exclusion.forbidden_unscreened_modes)}`",
            "",
            "The direct light scalar channel is retained as a falsifier and is not present in the current v1.5 scalar inventory.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))


def export_fifth_force_exclusion_markdown(path: str | Path) -> None:
    """Export the focused fifth-force exclusion report as Markdown."""

    report = fifth_force_exclusion_report()
    lines = [
        "# BHSM v1.6 Fifth-Force Exclusion Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Mode | Status | Ordinary fifth-force mediator | Open risk |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.rules:
        lines.append(f"| `{row.mode_id}` | `{row.status}` | `{row.ordinary_on_shell_fifth_force_mediator}` | `{row.open_coupling_risk}` |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))


__all__ = [
    "FifthForceExclusionReport",
    "ScalarScreeningProofReport",
    "build_scalar_screening_proof_report",
    "explicit_direct_light_scalar_failure",
    "export_fifth_force_exclusion_json",
    "export_fifth_force_exclusion_markdown",
    "export_scalar_screening_json",
    "export_scalar_screening_markdown",
    "fifth_force_exclusion_report",
    "FULL_SCREENING_THEOREM_PROVEN",
]

