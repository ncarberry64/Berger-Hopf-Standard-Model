"""BHSM v2.0 perturbation symmetry audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from perturbation_operator import perturbation_terms


PERTURBATION_SYMMETRY_PROVEN = "PERTURBATION_SYMMETRY_PROVEN"
PERTURBATION_SYMMETRY_CONDITIONAL = "PERTURBATION_SYMMETRY_CONDITIONAL"
PERTURBATION_SYMMETRY_OPEN = "PERTURBATION_SYMMETRY_OPEN"
FAILS_PERTURBATION_SYMMETRY = "FAILS_PERTURBATION_SYMMETRY"


@dataclass(frozen=True)
class PerturbationSymmetryReport:
    title: str
    term_statuses: tuple[dict[str, object], ...]
    all_symmetric_on_core: bool
    all_extend_to_domain: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_perturbation_symmetry_report() -> PerturbationSymmetryReport:
    rows = []
    for term in perturbation_terms():
        symmetric_on_core = term.symmetry_status in {"SYMMETRY_PROVEN", "SYMMETRIC_CANDIDATE"}
        extends = term.symmetry_status == "SYMMETRY_PROVEN" and term.domain_status == "DOMAIN_INCLUDED"
        rows.append(
            {
                "term_id": term.term_id,
                "symmetry_status": term.symmetry_status,
                "symmetric_on_core": symmetric_on_core,
                "extends_to_DA0": extends,
                "open_obligations": term.open_obligations,
            }
        )
    all_core = all(row["symmetric_on_core"] for row in rows)
    all_extends = all(row["extends_to_DA0"] for row in rows)
    status = PERTURBATION_SYMMETRY_PROVEN if all_extends else PERTURBATION_SYMMETRY_CONDITIONAL if all_core else PERTURBATION_SYMMETRY_OPEN
    return PerturbationSymmetryReport(
        title="BHSM v2.0 Perturbation Symmetry Report",
        term_statuses=tuple(rows),
        all_symmetric_on_core=all_core,
        all_extend_to_domain=all_extends,
        status=status,
        theorem_complete=status == PERTURBATION_SYMMETRY_PROVEN,
        limitations=("Core symmetry is stronger than before, but D(A0)-level extension remains conditional for several terms.",),
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


def export_perturbation_symmetry_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_symmetry_report()), indent=2, sort_keys=True) + "\n")


def export_perturbation_symmetry_markdown(path: str | Path) -> None:
    report = build_perturbation_symmetry_report()
    lines = [
        "# BHSM v2.0 Perturbation Symmetry Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All symmetric on core: `{report.all_symmetric_on_core}`",
        f"All extend to D(A0): `{report.all_extend_to_domain}`",
        "",
        "| Term | Symmetric on core | Extends to D(A0) | Open obligations |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.term_statuses:
        lines.append(f"| `{row['term_id']}` | `{row['symmetric_on_core']}` | `{row['extends_to_DA0']}` | {'<br>'.join(row['open_obligations']) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

