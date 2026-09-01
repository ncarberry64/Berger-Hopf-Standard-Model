"""BHSM v1.5 scalar/topographic decoupling theorem scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scalar_decoupling import build_scalar_proxy_spectrum, hopf_gap_mass, scalar_decoupling_report
from scalar_state_ledger import FORBIDDEN_EXTRA_LIGHT_SCALAR, OPEN_SCALAR_RISK, scalar_state_ledger
from topographic_screening import topographic_screening_report


@dataclass(frozen=True)
class ScalarDecouplingCondition:
    """One sufficient scalar/topographic decoupling condition."""

    id: str
    statement: str
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ScalarDecouplingTheoremReport:
    """Complete scalar/topographic decoupling scaffold report."""

    title: str
    gap: float
    conditions: tuple[ScalarDecouplingCondition, ...]
    scalar_inventory: dict[str, Any]
    screening: dict[str, Any]
    current_audit: dict[str, Any]
    forbidden_or_open_current_modes: tuple[dict[str, Any], ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def scalar_decoupling_conditions() -> tuple[ScalarDecouplingCondition, ...]:
    """Return sufficient scalar decoupling conditions."""

    return (
        ScalarDecouplingCondition(
            id="SD1",
            statement="Exactly one light Higgs projection is allowed.",
            status="FINITE_BASIS_VERIFIED",
            evidence=("Current proxy inventory has one light Higgs projection.",),
            limitations=("Full scalar action proof remains open.",),
        ),
        ScalarDecouplingCondition(
            id="SD2",
            statement="Every orthogonal scalar is heavy, derivative-filtered, curvature-filtered, or screened.",
            status="SCAFFOLD_VERIFIED",
            evidence=("Current proxy inventory has no unscreened direct-coupled light scalar.",),
            limitations=("Filtered/screened modes are conditional, not fully proven safe.",),
        ),
        ScalarDecouplingCondition(
            id="SD3",
            statement="A screened scalar/topographic mode is not a new on-shell light particle.",
            status="STATE_ONTOLOGY_LINKED",
            evidence=("v1.3F state ontology classifies screened topographic states separately from observable particles.",),
            limitations=("Ontology does not replace an action-level decoupling proof.",),
        ),
        ScalarDecouplingCondition(
            id="SD4",
            statement="Any unscreened direct-coupled light scalar is a falsifier or open scalar risk.",
            status="FALSIFIER_RULE",
            evidence=("Forbidden/open scalar categories are explicit in the scalar state ledger.",),
            limitations=("A future full spectrum could still reveal an open risk.",),
        ),
    )


def build_scalar_decoupling_theorem_report(n_modes: int = 6) -> ScalarDecouplingTheoremReport:
    """Build the Gate 3 scalar/topographic decoupling scaffold report."""

    modes = build_scalar_proxy_spectrum(n_modes)
    gap = hopf_gap_mass(246.21965)
    audit = scalar_decoupling_report(modes, gap)
    ledger = scalar_state_ledger(n_modes)
    current_risks = tuple(
        row for row in ledger["current_inventory"]
        if row["category"] in {FORBIDDEN_EXTRA_LIGHT_SCALAR, OPEN_SCALAR_RISK}
    )
    status = "SCALAR_DECOUPLING_SCAFFOLD_PASSES" if audit["passes"] and not current_risks else "OPEN_SCALAR_RISK"
    return ScalarDecouplingTheoremReport(
        title="BHSM v1.5 Scalar/Topographic Decoupling Scaffold",
        gap=float(gap),
        conditions=scalar_decoupling_conditions(),
        scalar_inventory=ledger,
        screening=topographic_screening_report(),
        current_audit=audit,
        forbidden_or_open_current_modes=current_risks,
        status=status,
        theorem_complete=False,
        limitations=(
            "Full scalar/topographic decoupling from the action remains open.",
            "Conditional filtered/screened modes are scaffold-audited, not fully proven safe.",
            "No frozen BHSM predictions are changed.",
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


def export_scalar_decoupling_theorem_json(path: str | Path) -> None:
    """Export scalar/topographic decoupling theorem scaffold as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_scalar_decoupling_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_scalar_decoupling_theorem_markdown(path: str | Path) -> None:
    """Export scalar/topographic decoupling theorem scaffold as Markdown."""

    report = build_scalar_decoupling_theorem_report()
    lines = [
        "# BHSM v1.5 Scalar/Topographic Decoupling Scaffold",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Status: `{report.status}`",
        f"Hopf gap: `{report.gap}`",
        "",
        "## Sufficient Conditions",
        "",
        "| ID | Status | Statement |",
        "| --- | --- | --- |",
    ]
    for condition in report.conditions:
        lines.append(f"| `{condition.id}` | `{condition.status}` | {condition.statement} |")
    lines.extend(
        [
            "",
            "## Current Scalar Inventory",
            "",
            "| Mode | Category | Status | Light | Allowed | Conditional |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.scalar_inventory["current_inventory"]:
        lines.append(
            f"| `{row['mode_id']}` | `{row['category']}` | `{row['status']}` | `{row['light']}` | `{row['allowed']}` | `{row['conditional']}` |"
        )
    lines.extend(
        [
            "",
            "## Scalar Risk Assessment",
            "",
            f"Forbidden/open current modes: `{len(report.forbidden_or_open_current_modes)}`",
            "",
            "A screened scalar/topographic mode is treated as a conditional screened state, not a new on-shell light particle. An unscreened direct-coupled light scalar is a falsifier/open risk.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
