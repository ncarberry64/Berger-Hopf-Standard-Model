"""BHSM v2.1 Hopf, boundary, and chirality infinite-bound scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


HOPF_BOUNDARY_CHI_BOUNDS_PROVEN = "HOPF_BOUNDARY_CHI_BOUNDS_PROVEN"
HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL = "HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL"
HOPF_BOUNDARY_CHI_BOUNDS_OPEN = "HOPF_BOUNDARY_CHI_BOUNDS_OPEN"
FAILS_HOPF_BOUNDARY_CHI_BOUNDS = "FAILS_HOPF_BOUNDARY_CHI_BOUNDS"


@dataclass(frozen=True)
class HopfBoundaryTermBound:
    term_id: str
    symbolic_form: str
    bound_type: str
    relative_a: float
    relative_b: float
    preserves_domain: bool
    symmetric_on_DA0: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class HopfBoundaryInfiniteBoundReport:
    title: str
    terms: tuple[HopfBoundaryTermBound, ...]
    total_relative_a: float
    total_relative_b: float
    all_terms_controlled: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def hopf_boundary_term_bounds() -> tuple[HopfBoundaryTermBound, ...]:
    return (
        HopfBoundaryTermBound(
            term_id="V_Hopf",
            symbolic_form="Hopf fiber twist controlled by q=k-2j",
            bound_type="relative diagonal domination by Berger action q^2 <= C lambda_diag",
            relative_a=0.0,
            relative_b=0.0,
            preserves_domain=True,
            symmetric_on_DA0=True,
            assumptions=("the q-growth comparison holds for the complete Berger twisted diagonal action",),
            limitations=("The comparison is explicit in the scaffold but not yet an analytic theorem for the complete operator.",),
        ),
        HopfBoundaryTermBound(
            term_id="V_boundary",
            symbolic_form="sector boundary functional Omega_f(k,j,q)",
            bound_type="linear boundary growth controlled by diagonal action",
            relative_a=0.0,
            relative_b=0.0,
            preserves_domain=True,
            symmetric_on_DA0=True,
            assumptions=("Omega_f growth remains at most linearly controlled by the complete diagonal action.",),
            limitations=("The v1.2 action-origin functional is reduced from a symbolic parent scaffold, not the full action.",),
        ),
        HopfBoundaryTermBound(
            term_id="V_chi",
            symbolic_form="weak chirality projector contribution",
            bound_type="bounded projector",
            relative_a=0.0,
            relative_b=1.0,
            preserves_domain=True,
            symmetric_on_DA0=True,
            assumptions=("chirality remains a bounded involutive/projector label in the complete basis",),
            limitations=("This does not settle mirror-mode exclusion by itself.",),
        ),
    )


def build_hopf_boundary_infinite_bound_report() -> HopfBoundaryInfiniteBoundReport:
    terms = hopf_boundary_term_bounds()
    all_controlled = all(term.preserves_domain and term.symmetric_on_DA0 for term in terms)
    return HopfBoundaryInfiniteBoundReport(
        title="BHSM v2.1 Hopf/Boundary/Chirality Infinite Bounds",
        terms=terms,
        total_relative_a=sum(term.relative_a for term in terms),
        total_relative_b=sum(term.relative_b for term in terms),
        all_terms_controlled=all_controlled,
        status=HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL if all_controlled else HOPF_BOUNDARY_CHI_BOUNDS_OPEN,
        theorem_complete=False,
        limitations=(
            "Termwise bounds are explicit under the scaffold comparisons, but the complete twisted Dirac spectrum is not yet analytically derived.",
            "This report does not prove the full H_T theorem.",
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


def export_hopf_boundary_infinite_bound_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_hopf_boundary_infinite_bound_report()), indent=2, sort_keys=True) + "\n")


def export_hopf_boundary_infinite_bound_markdown(path: str | Path) -> None:
    report = build_hopf_boundary_infinite_bound_report()
    lines = [
        "# BHSM v2.1 Hopf/Boundary/Chirality Infinite Bounds",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Total relative a: `{report.total_relative_a}`",
        f"Total relative b: `{report.total_relative_b}`",
        "",
        "| Term | Bound type | a | b | Preserves D(A0) | Symmetric on D(A0) | Assumptions |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for term in report.terms:
        lines.append(f"| `{term.term_id}` | {term.bound_type} | `{term.relative_a}` | `{term.relative_b}` | `{term.preserves_domain}` | `{term.symmetric_on_DA0}` | {'<br>'.join(term.assumptions)} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
