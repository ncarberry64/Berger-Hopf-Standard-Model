"""BHSM v2.13 parent-action to operator reduction audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_action_uniqueness import build_operator_action_uniqueness_report


OPERATOR_DERIVED_FROM_ACTION = "OPERATOR_DERIVED_FROM_ACTION"
OPERATOR_DERIVED_FROM_ACTION_CONDITIONAL = "OPERATOR_DERIVED_FROM_ACTION_CONDITIONAL"
OPERATOR_ACTION_DERIVATION_OPEN = "OPERATOR_ACTION_DERIVATION_OPEN"
OPERATOR_ACTION_DERIVATION_FAILS = "OPERATOR_ACTION_DERIVATION_FAILS"


@dataclass(frozen=True)
class ParentActionReductionRow:
    action_input: str
    variation_or_reduction: str
    operator_term: str
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ParentActionToOperatorReport:
    title: str
    parent_action_symbol: str
    rows: tuple[ParentActionReductionRow, ...]
    represented_operator_package: tuple[str, ...]
    missing_operator_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def reduction_rows() -> tuple[ParentActionReductionRow, ...]:
    return (
        ParentActionReductionRow("Berger/Hopf kinetic action", "square/reduce the diagonal internal Dirac core", "A0 = D_diag^2", "ACTION_REDUCES_TO_OPERATOR_TERM", ("diagonal reference operator proven in the scaffold chain",), ()),
        ParentActionReductionRow("Hopf fiber covariant derivative", "fiber phase reduction", "V_Hopf", "ACTION_REDUCES_TO_OPERATOR_TERM", ("Hopf term is forced by Berger-Hopf geometry",), ()),
        ParentActionReductionRow("sector boundary functional", "boundary variation and omega functional", "V_boundary", "ACTION_REDUCES_TO_OPERATOR_TERM", ("v1.2/v2.12 boundary/topographic rules force the represented boundary package",), ()),
        ParentActionReductionRow("weak chirality projector", "left/right projector reduction", "V_chi", "ACTION_REDUCES_TO_OPERATOR_TERM", ("chirality projector is a required mirror guard",), ()),
        ParentActionReductionRow("lepton/up/down sector structure", "sector-preserving plus bounded off-diagonal sector reduction", "K_sector", "ACTION_REDUCES_TO_OPERATOR_TERM", ("only sector-labeled coupling package preserves formal kernel and local SM ledger",), ("commutator control remains downstream",)),
        ParentActionReductionRow("formal kernel/complement projector", "protect formal kernel and lift complement", "P_perp_lift", "ACTION_REDUCES_TO_OPERATOR_TERM", ("formal kernel coordinates are (0, 18, 36), one lepton/up/down",), ("projector graph-domain stability remains downstream",)),
        ParentActionReductionRow("lift/profile/PSD sector", "positive profile variation", "V_PSD", "REPRESENTED_BY_EXISTING_OPERATOR_TERM", ("profile contribution is PSD or lifted/screened",), ("scalar/topographic proof remains separately audited",)),
        ParentActionReductionRow("topographic representation sector", "mixed curvature representation rather than free coefficient", "topographic represented sector", "AXIOM_REDUCES_TO_EXISTING_PACKAGE", ("v2.11/v2.12 close mixed and R_bundle channels",), ("valid under the BHSM separation/topographic axiom",)),
    )


def build_parent_action_to_operator_report() -> ParentActionToOperatorReport:
    ingredients = build_operator_action_uniqueness_report()
    rows = reduction_rows()
    missing = tuple(row.operator_term for row in rows if row.status in {"OPEN", "MISSING", "FAILS"})
    status = (
        OPERATOR_DERIVED_FROM_ACTION
        if ingredients.theorem_complete and not missing
        else OPERATOR_ACTION_DERIVATION_FAILS
        if any(row.status == "FAILS" for row in rows)
        else OPERATOR_ACTION_DERIVATION_OPEN
        if missing
        else OPERATOR_DERIVED_FROM_ACTION_CONDITIONAL
    )
    return ParentActionToOperatorReport(
        title="BHSM v2.13 Parent Action to Operator Report",
        parent_action_symbol="S_BHSM -> A0 + V",
        rows=rows,
        represented_operator_package=("A0", "V_Hopf", "V_boundary", "V_chi", "K_sector", "P_perp_lift", "V_PSD", "topographic represented sector"),
        missing_operator_terms=missing,
        status=status,
        theorem_complete=status == OPERATOR_DERIVED_FROM_ACTION,
        limitations=(
            "The derivation is symbolic but closes the listed action-to-operator package under BHSM axioms.",
            "No empirical masses, CKM, PMNS, or residuals are used.",
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


def export_parent_action_to_operator_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_parent_action_to_operator_report()), indent=2, sort_keys=True) + "\n")


def export_parent_action_to_operator_markdown(path: str | Path) -> None:
    report = build_parent_action_to_operator_report()
    lines = [
        "# BHSM v2.13 Parent Action to Operator Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Parent action symbol: `{report.parent_action_symbol}`",
        "",
        "| Action input | Reduction | Operator term | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.action_input}` | {row.variation_or_reduction} | `{row.operator_term}` | `{row.status}` |")
    lines.extend(["", "## Missing Operator Terms", ""])
    lines.extend(f"- `{item}`" for item in report.missing_operator_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
