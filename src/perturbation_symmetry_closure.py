"""BHSM v2.1 termwise perturbation symmetry closure scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from hopf_boundary_infinite_bound import build_hopf_boundary_infinite_bound_report
from lift_projector_domain import build_lift_projector_domain_report
from sector_coupling_infinite_bound import build_sector_coupling_infinite_bound_report


PERTURBATION_SYMMETRY_PROVEN = "PERTURBATION_SYMMETRY_PROVEN"
PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL = "PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL"
PERTURBATION_SYMMETRY_CORE_ONLY = "PERTURBATION_SYMMETRY_CORE_ONLY"
PERTURBATION_SYMMETRY_OPEN = "PERTURBATION_SYMMETRY_OPEN"
FAILS_PERTURBATION_SYMMETRY = "FAILS_PERTURBATION_SYMMETRY"


@dataclass(frozen=True)
class SymmetryTermClosure:
    term_id: str
    symmetric_on_finite_core: bool
    symmetric_on_DA0: bool
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class PerturbationSymmetryClosureReport:
    title: str
    terms: tuple[SymmetryTermClosure, ...]
    all_symmetric_on_core: bool
    all_termwise_symmetric_on_DA0: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_perturbation_symmetry_closure_report() -> PerturbationSymmetryClosureReport:
    hopf = build_hopf_boundary_infinite_bound_report()
    sector = build_sector_coupling_infinite_bound_report()
    lift = build_lift_projector_domain_report()
    rows: list[SymmetryTermClosure] = []
    for term in hopf.terms:
        rows.append(
            SymmetryTermClosure(
                term.term_id,
                True,
                term.symmetric_on_DA0,
                "SYMMETRIC_ON_DA0_CONDITIONAL",
                (term.bound_type, *term.assumptions),
                term.limitations,
            )
        )
    rows.append(
        SymmetryTermClosure(
            "K_sector",
            True,
            True,
            "SYMMETRIC_ON_DA0_CONDITIONAL",
            ("sector-coupling matrix is symmetric by paired sector block rule", *sector.pattern.assumptions),
            sector.limitations,
        )
    )
    for term in lift.terms:
        rows.append(
            SymmetryTermClosure(
                term.term_id,
                True,
                term.symmetric_on_DA0,
                "SYMMETRIC_ON_DA0_CONDITIONAL",
                (term.operator_role, *term.assumptions),
                term.limitations,
            )
        )
    all_core = all(row.symmetric_on_finite_core for row in rows)
    all_DA0 = all(row.symmetric_on_DA0 for row in rows)
    return PerturbationSymmetryClosureReport(
        title="BHSM v2.1 Perturbation Symmetry Closure",
        terms=tuple(rows),
        all_symmetric_on_core=all_core,
        all_termwise_symmetric_on_DA0=all_DA0,
        status=PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL if all_DA0 else PERTURBATION_SYMMETRY_OPEN,
        theorem_complete=False,
        open_obligations=(
            "identify each symmetric scaffold term with the corresponding complete operator term on D(A0)",
            "prove the complete sector-coupling block remains symmetric under the infinite-basis pairing rule",
        ),
        limitations=(
            "Termwise symmetry is explicit under v2.1 scaffold assumptions.",
            "It is not upgraded to PERTURBATION_SYMMETRY_PROVEN for the complete operator.",
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


def export_perturbation_symmetry_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_symmetry_closure_report()), indent=2, sort_keys=True) + "\n")


def export_perturbation_symmetry_closure_markdown(path: str | Path) -> None:
    report = build_perturbation_symmetry_closure_report()
    lines = [
        "# BHSM v2.1 Perturbation Symmetry Closure",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All symmetric on finite core: `{report.all_symmetric_on_core}`",
        f"All termwise symmetric on D(A0): `{report.all_termwise_symmetric_on_DA0}`",
        "",
        "| Term | Core symmetry | D(A0) symmetry | Status | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.terms:
        lines.append(f"| `{row.term_id}` | `{row.symmetric_on_finite_core}` | `{row.symmetric_on_DA0}` | `{row.status}` | {'<br>'.join(row.evidence)} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
