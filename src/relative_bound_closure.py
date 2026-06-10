"""BHSM v2.0 relative-bound closure audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from perturbation_operator import perturbation_terms


RELATIVE_BOUND_PROVEN = "RELATIVE_BOUND_PROVEN"
RELATIVE_BOUND_CANDIDATE = "RELATIVE_BOUND_CANDIDATE"
RELATIVE_BOUND_CONDITIONAL = "RELATIVE_BOUND_CONDITIONAL"
RELATIVE_BOUND_OPEN = "RELATIVE_BOUND_OPEN"
FAILS_RELATIVE_BOUND = "FAILS_RELATIVE_BOUND"


@dataclass(frozen=True)
class RelativeBoundClosureReport:
    title: str
    term_bounds: tuple[dict[str, object], ...]
    total_a: float
    total_b: float
    a_less_than_one: bool
    all_infinite_bounds_proven: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_relative_bound_closure_report() -> RelativeBoundClosureReport:
    rows = []
    for term in perturbation_terms():
        proven = term.infinite_basis_status in {"PROVEN_BOUNDED", "PROVEN_PSD_SCAFFOLD"}
        rows.append(
            {
                "term_id": term.term_id,
                "a": term.relative_a,
                "b": term.relative_b,
                "bound_expression": f"||{term.term_id} psi|| <= {term.relative_a} ||A0 psi|| + {term.relative_b} ||psi||",
                "infinite_bound_proven": proven,
                "finite_scan_evidence_used": term.finite_scan_evidence_used,
                "open_obligations": term.open_obligations,
            }
        )
    total_a = sum(float(row["a"]) for row in rows)
    total_b = sum(float(row["b"]) for row in rows)
    all_proven = all(bool(row["infinite_bound_proven"]) for row in rows)
    below = total_a < 1.0
    status = RELATIVE_BOUND_PROVEN if all_proven and below else RELATIVE_BOUND_CONDITIONAL if below else FAILS_RELATIVE_BOUND
    return RelativeBoundClosureReport(
        title="BHSM v2.0 Relative-Bound Closure Report",
        term_bounds=tuple(rows),
        total_a=total_a,
        total_b=total_b,
        a_less_than_one=below,
        all_infinite_bounds_proven=all_proven,
        status=status,
        theorem_complete=status == RELATIVE_BOUND_PROVEN,
        limitations=("a<1 is retained, but not every infinite-basis term bound is proven.",),
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


def export_relative_bound_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_relative_bound_closure_report()), indent=2, sort_keys=True) + "\n")


def export_relative_bound_closure_markdown(path: str | Path) -> None:
    report = build_relative_bound_closure_report()
    lines = [
        "# BHSM v2.0 Relative-Bound Closure Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Total a: `{report.total_a}`",
        f"Total b: `{report.total_b}`",
        f"a < 1: `{report.a_less_than_one}`",
        "",
        "| Term | a | b | Infinite proof | Finite scan used | Open obligations |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.term_bounds:
        lines.append(f"| `{row['term_id']}` | `{row['a']}` | `{row['b']}` | `{row['infinite_bound_proven']}` | `{row['finite_scan_evidence_used']}` | {'<br>'.join(row['open_obligations']) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

