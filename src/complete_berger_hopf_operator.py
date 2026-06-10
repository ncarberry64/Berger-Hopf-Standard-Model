"""BHSM v2.6 complete Berger-Hopf operator formalization."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from operator_term_inventory import build_operator_term_inventory_report


@dataclass(frozen=True)
class CompleteBergerHopfOperatorReport:
    title: str
    operator_symbol: str
    current_decomposition: str
    domain: str
    represented_terms: tuple[str, ...]
    unresolved_terms: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_complete_berger_hopf_operator_report() -> CompleteBergerHopfOperatorReport:
    inventory = build_operator_term_inventory_report()
    represented = tuple(term.term_id for term in inventory.terms if term.term_id not in inventory.required_open_or_missing_terms)
    unresolved = inventory.required_open_or_missing_terms
    return CompleteBergerHopfOperatorReport(
        title="BHSM v2.6 Complete Berger-Hopf Operator Report",
        operator_symbol="D_BH^2",
        current_decomposition="A0 + V = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_perp_lift + V_PSD",
        domain="D(A0) with formal-kernel/complement projector domain conditions from v2.4",
        represented_terms=represented,
        unresolved_terms=unresolved,
        status="COMPLETE_BERGER_HOPF_OPERATOR_BLOCKED_BY_REMAINDER" if unresolved else "COMPLETE_BERGER_HOPF_OPERATOR_IDENTIFIED",
        theorem_complete=not unresolved,
        limitations=(
            "The current decomposition accounts for the named scaffold terms.",
            "Exact equality D_BH^2 = A0+V is blocked by unresolved bundle-curvature remainder accounting.",
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


def export_complete_berger_hopf_operator_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_berger_hopf_operator_report()), indent=2, sort_keys=True) + "\n")


def export_complete_berger_hopf_operator_markdown(path: str | Path) -> None:
    report = build_complete_berger_hopf_operator_report()
    lines = [
        "# BHSM v2.6 Complete Berger-Hopf Operator Report",
        "",
        f"Operator: `{report.operator_symbol}`",
        f"Decomposition: `{report.current_decomposition}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Represented Terms",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.represented_terms)
    lines.extend(["", "## Unresolved Terms", ""])
    lines.extend(f"- `{item}`" for item in report.unresolved_terms)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
