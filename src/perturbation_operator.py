"""BHSM v2.0 perturbation-operator inventory."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


PERTURBATION_INVENTORIED = "PERTURBATION_INVENTORIED"
PERTURBATION_CONDITIONAL = "PERTURBATION_CONDITIONAL"


@dataclass(frozen=True)
class PerturbationTerm:
    """One perturbation term relative to A0 = D_diag^2."""

    term_id: str
    symbolic_form: str
    action_on_basis: str
    symmetry_status: str
    domain_status: str
    relative_a: float
    relative_b: float
    finite_scan_evidence_used: bool
    infinite_basis_status: str
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class PerturbationOperatorReport:
    """Inventory of perturbation terms in V."""

    title: str
    reference_operator: str
    perturbation_expression: str
    terms: tuple[PerturbationTerm, ...]
    total_relative_a: float
    total_relative_b: float
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def perturbation_terms() -> tuple[PerturbationTerm, ...]:
    """Return the v2.0 perturbation inventory."""

    return (
        PerturbationTerm(
            "V_Hopf",
            "Hopf fiber twist multiplication/relative diagonal term",
            "depends on q=k-2j and preserves sector, k, j, chi",
            "SYMMETRIC_CANDIDATE",
            "DOMAIN_CONDITIONAL",
            0.0,
            0.0,
            False,
            "CONDITIONAL",
            ("prove q-growth is A0-relative bounded on D(A0)",),
        ),
        PerturbationTerm(
            "V_boundary",
            "sector boundary functional contribution",
            "depends on Omega_f(k,j,q,sector) and preserves basis labels",
            "SYMMETRIC_CANDIDATE",
            "DOMAIN_CONDITIONAL",
            0.0,
            0.0,
            False,
            "CONDITIONAL",
            ("prove Omega_f growth is A0-relative bounded on D(A0)",),
        ),
        PerturbationTerm(
            "V_chi",
            "weak chirality projector contribution",
            "bounded multiplication by chirality/projector data",
            "SYMMETRY_PROVEN",
            "DOMAIN_INCLUDED",
            0.0,
            1.0,
            False,
            "PROVEN_BOUNDED",
            (),
        ),
        PerturbationTerm(
            "K_sector",
            "off-diagonal sector-coupling block",
            "couples sectors while preserving k,j,q,chi in the scaffold rule",
            "SYMMETRIC_CANDIDATE",
            "DOMAIN_CONDITIONAL",
            0.015621013485509948,
            0.0,
            True,
            "CONDITIONAL",
            ("upgrade sparse/banded finite-scan evidence to a complete infinite-basis operator bound",),
        ),
        PerturbationTerm(
            "P_perp_lift",
            "heat lift on the formal complement",
            "PSD complement lift after formal-kernel projection",
            "SYMMETRY_PROVEN",
            "DOMAIN_CONDITIONAL",
            0.0,
            0.0,
            False,
            "CONDITIONAL",
            ("prove formal complement projector preserves D(A0)",),
        ),
        PerturbationTerm(
            "PSD_profile",
            "positive semidefinite profile contribution",
            "nonnegative quadratic-form addition",
            "SYMMETRY_PROVEN",
            "DOMAIN_INCLUDED",
            0.0,
            0.0,
            False,
            "PROVEN_PSD_SCAFFOLD",
            (),
        ),
    )


def build_perturbation_operator_report() -> PerturbationOperatorReport:
    """Build the perturbation inventory report."""

    terms = perturbation_terms()
    return PerturbationOperatorReport(
        title="BHSM v2.0 Perturbation Operator Inventory",
        reference_operator="A0 = D_diag^2",
        perturbation_expression="V = V_Hopf + V_boundary + V_chi + K_sector",
        terms=terms,
        total_relative_a=sum(term.relative_a for term in terms),
        total_relative_b=sum(term.relative_b for term in terms),
        status=PERTURBATION_INVENTORIED,
        theorem_complete=False,
        limitations=(
            "This is an operator-theoretic inventory, not a full perturbation theorem.",
            "Finite-scan evidence is flagged explicitly where used.",
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


def export_perturbation_operator_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_operator_report()), indent=2, sort_keys=True) + "\n")


def export_perturbation_operator_markdown(path: str | Path) -> None:
    report = build_perturbation_operator_report()
    lines = [
        "# BHSM v2.0 Perturbation Operator Inventory",
        "",
        f"Status: `{report.status}`",
        f"Reference operator: `{report.reference_operator}`",
        f"Perturbation: `{report.perturbation_expression}`",
        f"Total relative a: `{report.total_relative_a}`",
        "",
        "| Term | Symmetry | Domain | a | b | Infinite-basis status | Open obligations |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for term in report.terms:
        lines.append(f"| `{term.term_id}` | `{term.symmetry_status}` | `{term.domain_status}` | `{term.relative_a}` | `{term.relative_b}` | `{term.infinite_basis_status}` | {'<br>'.join(term.open_obligations) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

