"""BHSM v2.5 complete-operator identification closure attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complete_twisted_dirac_operator import (
    COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL,
    COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
    build_complete_twisted_dirac_operator_report,
)
from complete_operator_identification_decision import (
    COMPLETE_OPERATOR_IDENTIFICATION_PROVEN as V26_COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
    build_complete_operator_identification_decision,
)


COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP = "COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP"


@dataclass(frozen=True)
class CompleteOperatorIdentificationClosureReport:
    title: str
    source_status: str
    final_status: str
    theorem_complete: bool
    blocking_components: tuple[str, ...]
    exact_obstruction: str
    next_branch: str
    next_target_theorem: str
    limitations: tuple[str, ...]


def build_complete_operator_identification_closure_report() -> CompleteOperatorIdentificationClosureReport:
    """Attempt to close complete-operator identification without overclaiming."""

    report = build_complete_twisted_dirac_operator_report()
    v26_decision = build_complete_operator_identification_decision()
    blocking = tuple(row.component_id for row in report.components if row.status != "COMPONENT_IDENTIFIED")
    proven = (
        report.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
        and not blocking
        and v26_decision.final_result == V26_COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    )
    obstruction = (
        "No obstruction: complete operator is identified."
        if proven
        else v26_decision.exact_obstruction
    )
    return CompleteOperatorIdentificationClosureReport(
        title="BHSM v2.7 Complete-Operator Identification Closure Attempt",
        source_status=v26_decision.operator_identification_status,
        final_status=COMPLETE_OPERATOR_IDENTIFICATION_PROVEN if proven else COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL,
        theorem_complete=proven,
        blocking_components=blocking + ((v26_decision.blocking_term,) if v26_decision.blocking_term else ()),
        exact_obstruction=obstruction,
        next_branch=v26_decision.recommended_next_branch,
        next_target_theorem=v26_decision.recommended_target_theorem,
        limitations=(
            "v2.13 closes the action-level uniqueness step under the explicit BHSM axioms.",
            "Downstream H_T closure still requires commutator, graph-domain, lower-bound, index, and mirror gates.",
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


def export_complete_operator_identification_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_operator_identification_closure_report()), indent=2, sort_keys=True) + "\n")


def export_complete_operator_identification_closure_markdown(path: str | Path) -> None:
    report = build_complete_operator_identification_closure_report()
    lines = [
        "# BHSM v2.7 Complete-Operator Identification Closure Attempt",
        "",
        f"Source status: `{report.source_status}`",
        f"Final status: `{report.final_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Next target theorem: `{report.next_target_theorem}`",
        f"Recommended next branch: `{report.next_branch}`",
        "",
        "## Blocking Components",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.blocking_components)
    lines.extend(["", "## Exact Obstruction", "", report.exact_obstruction, "", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
