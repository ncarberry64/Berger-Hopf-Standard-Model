"""Full BHSM operator/domain theorem scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from self_adjoint_domain import (
    FAILS_DOMAIN_CHECK,
    SELF_ADJOINT_DOMAIN_OPEN,
    SELF_ADJOINT_DOMAIN_PROVEN,
    SelfAdjointDomainReport,
    build_self_adjoint_domain_report,
)


FORMAL_KERNEL_STATES = (
    "|ell,0,0,q=0,chi=-1>",
    "|u,0,0,q=0,chi=-1>",
    "|d,0,0,q=0,chi=-1>",
)


@dataclass(frozen=True)
class FullOperatorTerm:
    """One term in the full formal-kernel operator scaffold."""

    id: str
    expression: str
    role: str
    domain_status: str
    can_lower_gap: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class FullOperatorDomainReport:
    """Full operator/domain report for the theorem-completion branch."""

    title: str
    hilbert_space: str
    mode_basis: str
    formal_kernel: tuple[str, ...]
    complement: str
    operator_expression: str
    terms: tuple[FullOperatorTerm, ...]
    self_adjoint_report: SelfAdjointDomainReport
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    forbidden_claims: tuple[str, ...]


def full_operator_terms() -> tuple[FullOperatorTerm, ...]:
    """Return the full-operator term inventory."""

    return (
        FullOperatorTerm("D_diag_squared", "D_diag^2", "diagonal Berger/twisted Dirac square", "CANDIDATE_DOMAIN", False, ()),
        FullOperatorTerm("V_Hopf", "V_Hopf", "Hopf fiber twist contribution", "DOMAIN_PRESERVATION_OPEN", True, ("complete relative-bound proof needed",)),
        FullOperatorTerm("V_boundary", "V_boundary", "sector boundary functional contribution", "DOMAIN_PRESERVATION_OPEN", True, ("derive complete boundary functional domain action",)),
        FullOperatorTerm("V_chi", "V_chi", "weak chirality projector contribution", "DOMAIN_PRESERVATION_OPEN", True, ("prove projector compatibility in complete operator",)),
        FullOperatorTerm("K_sector", "K_sector", "off-diagonal sector-coupling block", "RELATIVE_BOUND_CANDIDATE", True, ("upgrade finite/uniform scans to complete operator bound",)),
        FullOperatorTerm("P_perp_lift", "P_perp_lift", "heat lift on formal-kernel complement", "PROJECTOR_DOMAIN_OPEN", False, ("prove formal projector for complete Hilbert space",)),
    )


def build_full_operator_domain_report() -> FullOperatorDomainReport:
    """Build the Gate 1 full operator/domain report."""

    self_adjoint = build_self_adjoint_domain_report()
    open_obligations = tuple(
        dict.fromkeys(
            obligation
            for assumption in self_adjoint.assumptions
            for obligation in assumption.open_obligations
        )
    )
    theorem_complete = self_adjoint.status == SELF_ADJOINT_DOMAIN_PROVEN
    status = SELF_ADJOINT_DOMAIN_PROVEN if theorem_complete else SELF_ADJOINT_DOMAIN_OPEN
    if not self_adjoint.finite_matrix_hermitian:
        status = FAILS_DOMAIN_CHECK
    return FullOperatorDomainReport(
        title="BHSM Gate 1 Full Operator and Domain Theorem Attempt",
        hilbert_space="H = l2-completion of sector-labeled Berger-Hopf twisted spinor modes",
        mode_basis="|sector,k,j,q,chi> with q=k-2j and sector in {ell,u,d}",
        formal_kernel=FORMAL_KERNEL_STATES,
        complement="H_perp = K_formal^perp",
        operator_expression="D_FK^2 = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_perp_lift",
        terms=full_operator_terms(),
        self_adjoint_report=self_adjoint,
        status=status,
        theorem_complete=theorem_complete,
        open_obligations=open_obligations,
        forbidden_claims=(
            "Do not promote finite-matrix Hermiticity to full self-adjointness.",
            "Do not claim FULL_HT_THEOREM_PROVEN while SELF_ADJOINT_DOMAIN_OPEN remains.",
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


def export_full_operator_domain_json(path: str | Path) -> None:
    """Export the Gate 1 report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_full_operator_domain_report()), indent=2, sort_keys=True) + "\n")


def export_full_operator_domain_markdown(path: str | Path) -> None:
    """Export the Gate 1 report as Markdown."""

    report = build_full_operator_domain_report()
    lines = [
        "# BHSM Full Operator and Domain Theorem Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Hilbert Space and Kernel",
        "",
        f"Hilbert space: {report.hilbert_space}",
        f"Mode basis: `{report.mode_basis}`",
        "",
        "Formal kernel:",
        "",
    ]
    lines.extend(f"- `{state}`" for state in report.formal_kernel)
    lines.extend(
        [
            "",
            f"Complement: `{report.complement}`",
            f"Operator: `{report.operator_expression}`",
            "",
            "## Operator Terms",
            "",
            "| Term | Expression | Domain status | Can lower gap | Limitations |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for term in report.terms:
        lines.append(f"| `{term.id}` | `{term.expression}` | `{term.domain_status}` | `{term.can_lower_gap}` | {'<br>'.join(term.limitations) or 'none'} |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Forbidden Claims", ""])
    lines.extend(f"- {item}" for item in report.forbidden_claims)
    lines.append("")
    Path(path).write_text("\n".join(lines))

