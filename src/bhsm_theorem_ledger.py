"""Integrated BHSM theorem/status ledger."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_dependency_graph import (
    ADOPTION_CANDIDATE,
    BASIS_REALIZED,
    BOUNDARY_FUNCTIONAL_DERIVED,
    FINITE_BASIS_SCAFFOLD,
    FROZEN_PREDICTION,
    OPEN,
    PARENT_ACTION_REDUCED,
    SEMI_ANALYTIC_SCAFFOLD,
    build_dependency_graph_report,
)


@dataclass(frozen=True)
class TheoremLedgerRow:
    """One theorem/output status row."""

    id: str
    claim: str
    status: str
    completed: bool
    blockers: tuple[str, ...]
    allowed_claim: str
    forbidden_upgrade: str


def theorem_status_rows() -> tuple[TheoremLedgerRow, ...]:
    """Return the integrated theorem/status ledger."""

    return (
        TheoremLedgerRow("frozen_v1_predictions", "BHSM v1.0/v1.1 frozen outputs", FROZEN_PREDICTION, True, (), "Frozen no-retuning model outputs are reproducible.", "Do not claim all entries are final confirmed predictions."),
        TheoremLedgerRow("omega_f", "charged-sector boundary operators", BOUNDARY_FUNCTIONAL_DERIVED, False, ("derive full boundary functional from complete action",), "Derived from symbolic sector boundary functional and parent-action scaffold.", "Do not claim complete action derivation."),
        TheoremLedgerRow("parent_action", "parent internal action scaffold", PARENT_ACTION_REDUCED, False, ("prove global uniqueness of complete Berger-Hopf internal action",), "Reduced from symbolic parent scaffold under current axioms.", "Do not claim full internal action proven."),
        TheoremLedgerRow("formal_kernel", "formal kernel K_formal", BASIS_REALIZED, False, ("prove full topological index theorem", "prove infinite-basis split"), "Coordinate-free scaffold and finite basis realization are implemented.", "Do not claim full index theorem."),
        TheoremLedgerRow("ht_gap", "H_T no-extra-light gap", SEMI_ANALYTIC_SCAFFOLD, False, ("full H_T spectrum", "profile positivity", "infinite-basis complement bound"), "Corrected formal-kernel finite/semi-analytic scaffold clears current thresholds.", "Do not claim no-extra-light-state theorem proven."),
        TheoremLedgerRow("scalar_decoupling", "scalar/topographic decoupling", FINITE_BASIS_SCAFFOLD, False, ("full scalar/topographic action proof", "global absence of unscreened light scalar risks"), "v1.5 action-level scaffold has exactly one Higgs projection and no current forbidden/open scalar risks.", "Do not claim scalar decoupling fully proven."),
        TheoremLedgerRow("qcd_rg", "QCD/RG matching", OPEN, False, ("precision threshold matching", "uncertainty propagation"), "Approximate/reference-set scaffolds are implemented.", "Do not claim precision QCD matching complete."),
        TheoremLedgerRow("virtual_dressing", "dressed candidate branch", ADOPTION_CANDIDATE, False, ("canonical adoption decision",), "Dressed branch remains candidate and changes only c/t.", "Do not claim dressed branch final."),
    )


def build_theorem_status_ledger() -> dict[str, Any]:
    """Build theorem status ledger and graph consistency summary."""

    graph = build_dependency_graph_report()
    rows = theorem_status_rows()
    return {
        "title": "BHSM Theorem Status Ledger",
        "rows": rows,
        "status_counts": {
            status: sum(1 for row in rows if row.status == status)
            for status in sorted({row.status for row in rows})
        },
        "hidden_circularity_detected": graph.hidden_circularity_detected,
        "empirical_residual_dependency_detected": graph.empirical_residual_dependency_detected,
        "theorem_complete": False,
        "open_obligations": graph.open_obligations,
    }


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


def export_theorem_status_ledger_json(path: str | Path) -> None:
    """Export theorem status ledger as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_theorem_status_ledger()), indent=2, sort_keys=True) + "\n")


def export_theorem_status_ledger_markdown(path: str | Path) -> None:
    """Export theorem status ledger as Markdown."""

    ledger = build_theorem_status_ledger()
    lines = [
        "# BHSM Theorem Status Ledger",
        "",
        f"Theorem complete: `{ledger['theorem_complete']}`",
        f"Hidden circularity detected: `{ledger['hidden_circularity_detected']}`",
        f"Empirical residual dependency detected: `{ledger['empirical_residual_dependency_detected']}`",
        "",
        "## Ledger Rows",
        "",
        "| ID | Status | Completed | Allowed claim | Forbidden upgrade |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in ledger["rows"]:
        lines.append(f"| `{row.id}` | `{row.status}` | `{row.completed}` | {row.allowed_claim} | {row.forbidden_upgrade} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(ledger["open_obligations"], start=1))
    lines.append("")
    Path(path).write_text("\n".join(lines))
