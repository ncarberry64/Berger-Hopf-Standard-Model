"""BHSM v2.5 projector-commutator closure attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_operator_identification_closure import build_complete_operator_identification_closure_report
from perturbation_projector_commutator import (
    PROJECTOR_COMMUTATORS_CONDITIONAL,
    PROJECTOR_COMMUTATORS_CONTROLLED,
    build_perturbation_projector_commutator_report,
)
from projector_commutator_control_decision import (
    PROJECTOR_COMMUTATOR_CONTROL_CLOSED,
    build_projector_commutator_control_decision,
)


@dataclass(frozen=True)
class ProjectorCommutatorClosureReport:
    title: str
    source_status: str
    final_status: str
    theorem_complete: bool
    conditional_commutators: tuple[str, ...]
    exact_obstruction: str
    limitations: tuple[str, ...]


def build_projector_commutator_closure_report() -> ProjectorCommutatorClosureReport:
    report = build_perturbation_projector_commutator_report()
    operator = build_complete_operator_identification_closure_report()
    decision = build_projector_commutator_control_decision()
    conditional = tuple(row.term_id for row in report.rows if row.status == "COMMUTATOR_CONDITIONAL")
    proven = decision.final_result == PROJECTOR_COMMUTATOR_CONTROL_CLOSED and operator.theorem_complete
    obstruction = (
        "No obstruction: all projector commutators are controlled on the complete graph domain."
        if proven
        else "The commutator rows are scaffold-controlled, but nonzero conditional commutators still require complete graph-domain commutator control."
    )
    return ProjectorCommutatorClosureReport(
        title="BHSM v2.5 Projector-Commutator Closure Attempt",
        source_status=report.status,
        final_status=PROJECTOR_COMMUTATORS_CONTROLLED if proven else PROJECTOR_COMMUTATORS_CONDITIONAL,
        theorem_complete=proven,
        conditional_commutators=() if proven else conditional,
        exact_obstruction=obstruction,
        limitations=(
            "No commutator is marked complete-operator controlled from conditional scaffold assumptions.",
            "This closure depends on the complete-operator identification theorem.",
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


def export_projector_commutator_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_commutator_closure_report()), indent=2, sort_keys=True) + "\n")


def export_projector_commutator_closure_markdown(path: str | Path) -> None:
    report = build_projector_commutator_closure_report()
    lines = [
        "# BHSM v2.5 Projector-Commutator Closure Attempt",
        "",
        f"Source status: `{report.source_status}`",
        f"Final status: `{report.final_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Conditional Commutators",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.conditional_commutators)
    lines.extend(["", "## Exact Obstruction", "", report.exact_obstruction, "", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
