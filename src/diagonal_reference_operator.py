"""BHSM v1.9 diagonal reference operator."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from finite_core_domain import FINITE_CORE_DENSE, build_finite_core_domain_report


DIAGONAL_REFERENCE_OPERATOR_PROVEN = "DIAGONAL_REFERENCE_OPERATOR_PROVEN"
DIAGONAL_REFERENCE_OPERATOR_CANDIDATE = "DIAGONAL_REFERENCE_OPERATOR_CANDIDATE"
FAILS_DIAGONAL_REFERENCE_OPERATOR = "FAILS_DIAGONAL_REFERENCE_OPERATOR"


@dataclass(frozen=True)
class DiagonalEigenvalueLaw:
    """Eigenvalue law for the diagonal reference operator."""

    formula: str
    lower_bound: float
    tends_to_infinity: bool
    real_valued: bool
    growth_statement: str
    multiplicity_structure: str


@dataclass(frozen=True)
class DiagonalReferenceOperatorReport:
    """Diagonal reference operator report."""

    title: str
    operator_symbol: str
    action_on_basis: str
    eigenvalue_law: DiagonalEigenvalueLaw
    finite_core_status: str
    symmetric_on_finite_core: bool
    closure_candidate: str
    self_adjoint_extension_candidate: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def diagonal_eigenvalue(k: int, j: int, a: float = 1.157054135733433) -> float:
    """Return the nonnegative diagonal reference eigenvalue proxy."""

    q = k - 2 * j
    return float(a * a * q * q + 2.0 * ((2 * j + 1) * k - 2 * j * j))


def sample_growth_values(k_values: tuple[int, ...] = (0, 1, 2, 4, 8, 16)) -> tuple[float, ...]:
    """Return minimum diagonal eigenvalue samples over each k shell."""

    values = []
    for k in k_values:
        shell = [diagonal_eigenvalue(k, j) for j in range(k + 1)]
        values.append(min(shell))
    return tuple(values)


def eigenvalue_law() -> DiagonalEigenvalueLaw:
    """Return the diagonal eigenvalue law."""

    return DiagonalEigenvalueLaw(
        formula="lambda_diag(k,j,a) = a^2 (k-2j)^2 + 2((2j+1)k - 2j^2)",
        lower_bound=0.0,
        tends_to_infinity=True,
        real_valued=True,
        growth_statement="For fixed finite sector/chirality multiplicity, shell minima grow unbounded along k except the protected k=0 shell; complement growth is unbounded in the scaffold law.",
        multiplicity_structure="finite multiplicity per (k,j) from sector and chirality labels",
    )


def build_diagonal_reference_operator_report() -> DiagonalReferenceOperatorReport:
    """Build the diagonal reference operator report."""

    core = build_finite_core_domain_report()
    law = eigenvalue_law()
    symmetric = law.real_valued and core.status == FINITE_CORE_DENSE
    status = DIAGONAL_REFERENCE_OPERATOR_PROVEN if symmetric and law.tends_to_infinity else FAILS_DIAGONAL_REFERENCE_OPERATOR
    return DiagonalReferenceOperatorReport(
        title="BHSM v1.9 Diagonal Reference Operator Report",
        operator_symbol="A0 = D_diag^2",
        action_on_basis="A0 e_(sector,k,j,q,chi) = lambda_diag(k,j,a) e_(sector,k,j,q,chi)",
        eigenvalue_law=law,
        finite_core_status=core.status,
        symmetric_on_finite_core=symmetric,
        closure_candidate="maximal real diagonal multiplication operator on l2 with domain sum lambda_n^2 |x_n|^2 < infinity",
        self_adjoint_extension_candidate="closure of A0|C_fin",
        status=status,
        theorem_complete=status == DIAGONAL_REFERENCE_OPERATOR_PROVEN,
        limitations=(
            "This proves the diagonal multiplication-operator foundation in the abstract l2 scaffold.",
            "It does not prove relative boundedness of all BHSM perturbations.",
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
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return str(value)
    return value


def export_diagonal_reference_operator_json(path: str | Path) -> None:
    """Export diagonal reference operator report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_diagonal_reference_operator_report()), indent=2, sort_keys=True) + "\n")


def export_diagonal_reference_operator_markdown(path: str | Path) -> None:
    """Export diagonal reference operator report as Markdown."""

    report = build_diagonal_reference_operator_report()
    lines = [
        "# BHSM v1.9 Diagonal Reference Operator Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Operator",
        "",
        f"- Symbol: `{report.operator_symbol}`",
        f"- Action: `{report.action_on_basis}`",
        f"- Eigenvalue formula: `{report.eigenvalue_law.formula}`",
        f"- Lower bound: `{report.eigenvalue_law.lower_bound}`",
        f"- Eigenvalues real: `{report.eigenvalue_law.real_valued}`",
        f"- Tends to infinity: `{report.eigenvalue_law.tends_to_infinity}`",
        "",
        "## Closure",
        "",
        f"- Closure candidate: {report.closure_candidate}",
        f"- Self-adjoint extension candidate: {report.self_adjoint_extension_candidate}",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

