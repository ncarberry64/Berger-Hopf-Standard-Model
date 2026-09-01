"""BHSM v2.14 relative-bound control for [P_perp,V]."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from projector_operator_commutators import build_projector_operator_commutators_report


PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN = "PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN"
PROJECTOR_COMMUTATOR_RELATIVE_BOUND_BLOCKED = "PROJECTOR_COMMUTATOR_RELATIVE_BOUND_BLOCKED"


@dataclass(frozen=True)
class ProjectorCommutatorRelativeBoundReport:
    title: str
    inequality: str
    a_commutator: float
    b_commutator: float
    a_total: float
    b_total: float
    a_total_less_than_one: bool
    nonzero_terms_checked: tuple[str, ...]
    lower_bound_safe: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_projector_commutator_relative_bound_report() -> ProjectorCommutatorRelativeBoundReport:
    commutators = build_projector_operator_commutators_report()
    nonzero = tuple(row.term_id for row in commutators.rows if not row.vanishes)
    a_c = sum(row.relative_a for row in commutators.rows if not row.vanishes)
    b_c = sum(row.relative_b for row in commutators.rows if not row.vanishes)
    safe = commutators.theorem_complete and all(row.lower_bound_safe for row in commutators.rows) and a_c < 1.0
    return ProjectorCommutatorRelativeBoundReport(
        title="BHSM v2.14 Projector Commutator Relative-Bound Report",
        inequality="||[P_perp,V] psi|| <= a_C ||A0 psi|| + b_C ||psi||",
        a_commutator=a_c,
        b_commutator=b_c,
        a_total=a_c,
        b_total=b_c,
        a_total_less_than_one=a_c < 1.0,
        nonzero_terms_checked=nonzero,
        lower_bound_safe=safe,
        status=PROJECTOR_COMMUTATOR_RELATIVE_BOUND_PROVEN if safe else PROJECTOR_COMMUTATOR_RELATIVE_BOUND_BLOCKED,
        theorem_complete=safe,
        limitations=(
            "The commutator bound is for projector commutator control, not the entire H_T theorem.",
            "Nonzero commutators are bounded, relatively bounded, or mapped into lifted/screened sectors.",
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


def export_projector_commutator_relative_bound_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_projector_commutator_relative_bound_report()), indent=2, sort_keys=True) + "\n")


def export_projector_commutator_relative_bound_markdown(path: str | Path) -> None:
    report = build_projector_commutator_relative_bound_report()
    lines = [
        "# BHSM v2.14 Projector Commutator Relative-Bound Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Inequality: `{report.inequality}`",
        f"a_C: `{report.a_commutator}`",
        f"b_C: `{report.b_commutator}`",
        f"a_total < 1: `{report.a_total_less_than_one}`",
        f"Lower-bound safe: `{report.lower_bound_safe}`",
        f"Nonzero terms checked: `{report.nonzero_terms_checked}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
