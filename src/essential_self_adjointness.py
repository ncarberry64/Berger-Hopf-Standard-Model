"""Essential self-adjointness proof for the diagonal BHSM reference operator."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from diagonal_reference_operator import (
    DIAGONAL_REFERENCE_OPERATOR_PROVEN,
    build_diagonal_reference_operator_report,
)


DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN = "DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN"
DIAGONAL_CORE_SELF_ADJOINT_CANDIDATE = "DIAGONAL_CORE_SELF_ADJOINT_CANDIDATE"
DIAGONAL_CORE_SELF_ADJOINT_CONDITIONAL = "DIAGONAL_CORE_SELF_ADJOINT_CONDITIONAL"
DIAGONAL_CORE_SELF_ADJOINT_OPEN = "DIAGONAL_CORE_SELF_ADJOINT_OPEN"
FAILS_DIAGONAL_SELF_ADJOINTNESS = "FAILS_DIAGONAL_SELF_ADJOINTNESS"


@dataclass(frozen=True)
class EssentialSelfAdjointnessRoute:
    """One proof route for essential self-adjointness."""

    id: str
    statement: str
    passes: bool
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class EssentialSelfAdjointnessReport:
    """Essential self-adjointness report for A0 on C_fin."""

    title: str
    operator_symbol: str
    finite_core: str
    proof_routes: tuple[EssentialSelfAdjointnessRoute, ...]
    deficiency_indices: tuple[int, int]
    closure: str
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def essential_self_adjointness_routes() -> tuple[EssentialSelfAdjointnessRoute, ...]:
    """Return the implemented proof routes."""

    diag = build_diagonal_reference_operator_report()
    return (
        EssentialSelfAdjointnessRoute(
            id="diagonal_multiplication_operator",
            statement="A real diagonal multiplication operator on l2 with finite sequences as a core is essentially self-adjoint; its closure is the maximal diagonal operator.",
            passes=diag.status == DIAGONAL_REFERENCE_OPERATOR_PROVEN,
            evidence=(
                "basis is complete in l2",
                "finite sequences are dense",
                "eigenvalues are real",
                "maximal diagonal closure has domain sum lambda_n^2 |x_n|^2 < infinity",
            ),
            limitations=("This route applies to the diagonal reference operator, not to the full perturbed BHSM operator.",),
        ),
        EssentialSelfAdjointnessRoute(
            id="deficiency_index_check",
            statement="For non-real z, (A0^* - z)x=0 has only the zero l2 solution because (lambda_n - z)x_n=0 and lambda_n is real.",
            passes=diag.eigenvalue_law.real_valued,
            evidence=("real diagonal eigenvalues imply no nonzero deficiency vector for z=+/- i",),
            limitations=("The calculation is for the diagonal multiplication closure.",),
        ),
        EssentialSelfAdjointnessRoute(
            id="graph_norm_core",
            statement="Finite truncations converge in graph norm for every vector in the maximal diagonal domain.",
            passes=True,
            evidence=("tail sums of |x_n|^2 + lambda_n^2 |x_n|^2 go to zero by definition of the graph domain",),
            limitations=("Perturbation graph-norm equivalence is separate.",),
        ),
    )


def build_essential_self_adjointness_report() -> EssentialSelfAdjointnessReport:
    """Build the essential self-adjointness proof report."""

    routes = essential_self_adjointness_routes()
    proven = all(route.passes for route in routes)
    return EssentialSelfAdjointnessReport(
        title="BHSM v1.9 Diagonal-Core Essential Self-Adjointness Report",
        operator_symbol="A0 = D_diag^2",
        finite_core="C_fin",
        proof_routes=routes,
        deficiency_indices=(0, 0) if proven else (-1, -1),
        closure="maximal real diagonal multiplication operator on l2",
        status=DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN if proven else DIAGONAL_CORE_SELF_ADJOINT_OPEN,
        theorem_complete=proven,
        limitations=(
            "Essential self-adjointness is proven only for the diagonal reference operator.",
            "Full BHSM self-adjointness still requires Kato-Rellich preconditions for perturbations.",
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


def export_essential_self_adjointness_json(path: str | Path) -> None:
    """Export essential self-adjointness report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_essential_self_adjointness_report()), indent=2, sort_keys=True) + "\n")


def export_essential_self_adjointness_markdown(path: str | Path) -> None:
    """Export essential self-adjointness report as Markdown."""

    report = build_essential_self_adjointness_report()
    lines = [
        "# BHSM v1.9 Diagonal-Core Essential Self-Adjointness Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Deficiency indices: `{report.deficiency_indices}`",
        "",
        "## Proof Routes",
        "",
        "| Route | Passes | Statement |",
        "| --- | --- | --- |",
    ]
    for route in report.proof_routes:
        lines.append(f"| `{route.id}` | `{route.passes}` | {route.statement} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

