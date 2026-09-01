"""BHSM v1.8 infinite-basis Hilbert/domain scaffold.

The objects here define the infinite-basis setting needed for a complete
operator-domain theorem. They are intentionally conservative: a named domain
assumption is not treated as proven merely because finite truncations pass.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


INFINITE_DOMAIN_DEFINED = "INFINITE_DOMAIN_DEFINED"
INFINITE_DOMAIN_CONDITIONAL = "INFINITE_DOMAIN_CONDITIONAL"
INFINITE_DOMAIN_OPEN = "INFINITE_DOMAIN_OPEN"
FAILS_INFINITE_DOMAIN = "FAILS_INFINITE_DOMAIN"

FORMAL_KERNEL_STATES = (
    "|ell,0,0,q=0,chi=-1>",
    "|u,0,0,q=0,chi=-1>",
    "|d,0,0,q=0,chi=-1>",
)


@dataclass(frozen=True)
class InfiniteDomainComponent:
    """One component of the infinite-basis domain scaffold."""

    id: str
    definition: str
    status: str
    evidence: tuple[str, ...]
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class InfiniteBasisDomainReport:
    """Infinite-basis Hilbert/domain report."""

    title: str
    hilbert_space: str
    infinite_basis: str
    dense_core: str
    graph_norm: str
    diagonal_reference_operator: str
    formal_kernel: tuple[str, ...]
    formal_complement: str
    components: tuple[InfiniteDomainComponent, ...]
    old_coordinate_first_kernel_used: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def infinite_domain_components() -> tuple[InfiniteDomainComponent, ...]:
    """Return v1.8 infinite-domain components."""

    return (
        InfiniteDomainComponent(
            "hilbert_basis",
            "H is the l2-completion of sector-labeled modes |sector,k,j,q,chi>.",
            INFINITE_DOMAIN_DEFINED,
            ("mode labels and corrected formal kernel are explicit",),
            (),
        ),
        InfiniteDomainComponent(
            "finite_core",
            "C_fin is the finite-support span of Berger-Hopf twisted spinor modes.",
            INFINITE_DOMAIN_DEFINED,
            ("finite truncations are nested subspaces of the same labeled basis",),
            (),
        ),
        InfiniteDomainComponent(
            "graph_norm_closure",
            "D(D0) is the graph-norm closure of C_fin for the diagonal reference operator D0.",
            INFINITE_DOMAIN_CONDITIONAL,
            ("diagonal eigenvalue scaffold is real and lower bounded",),
            ("prove the complete diagonal Berger/twisted Dirac spectrum and graph-norm closure",),
        ),
        InfiniteDomainComponent(
            "perturbation_domain",
            "Perturbations are defined on D(D0) if relatively bounded or bounded on the graph norm.",
            INFINITE_DOMAIN_CONDITIONAL,
            ("v1.7 relative-a estimates are below one in the scaffold",),
            ("upgrade every finite/scaffold bound to an infinite-basis operator bound",),
        ),
        InfiniteDomainComponent(
            "formal_kernel_domain",
            "K_formal is the span of the three sector-labeled q=0, chi=-1 states.",
            INFINITE_DOMAIN_DEFINED,
            ("the corrected formal kernel is coordinate-free and sector-labeled",),
            (),
        ),
        InfiniteDomainComponent(
            "formal_complement_domain",
            "H_perp is K_formal^perp in the l2 Hilbert space.",
            INFINITE_DOMAIN_CONDITIONAL,
            ("orthogonal complement is well-defined for the finite-rank formal kernel",),
            ("prove the full operator leaves K_formal and/or H_perp invariant or block-controlled",),
        ),
    )


def build_infinite_basis_domain_report() -> InfiniteBasisDomainReport:
    """Build the infinite-basis domain report."""

    components = infinite_domain_components()
    has_open = any(item.open_obligations for item in components)
    return InfiniteBasisDomainReport(
        title="BHSM v1.8 Infinite-Basis Domain Report",
        hilbert_space="H = l2({sector,k,j,q,chi}) over sector in {ell,u,d}, q=k-2j",
        infinite_basis="|sector,k,j,q,chi> with k>=0, 0<=j<=k, chi in {-1,+1}",
        dense_core="C_fin = finite-support span of the infinite labeled basis",
        graph_norm="||psi||_D0^2 = ||psi||^2 + ||D0 psi||^2",
        diagonal_reference_operator="D0^2 = diagonal Berger/twisted Dirac reference square",
        formal_kernel=FORMAL_KERNEL_STATES,
        formal_complement="H_perp = K_formal^perp",
        components=components,
        old_coordinate_first_kernel_used=False,
        status=INFINITE_DOMAIN_CONDITIONAL if has_open else INFINITE_DOMAIN_DEFINED,
        theorem_complete=False,
        limitations=(
            "The infinite Hilbert/domain scaffold is explicit, but graph-norm closure and perturbation domains remain conditional.",
            "The old coordinate-first kernel (0,1,2) is not used.",
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


def export_infinite_basis_domain_json(path: str | Path) -> None:
    """Export the infinite-basis domain report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_infinite_basis_domain_report()), indent=2, sort_keys=True) + "\n")


def export_infinite_basis_domain_markdown(path: str | Path) -> None:
    """Export the infinite-basis domain report as Markdown."""

    report = build_infinite_basis_domain_report()
    lines = [
        "# BHSM v1.8 Infinite-Basis Domain Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Old coordinate-first kernel used: `{report.old_coordinate_first_kernel_used}`",
        "",
        "## Domain Definitions",
        "",
        f"- Hilbert space: `{report.hilbert_space}`",
        f"- Infinite basis: `{report.infinite_basis}`",
        f"- Dense core: `{report.dense_core}`",
        f"- Graph norm: `{report.graph_norm}`",
        f"- Formal complement: `{report.formal_complement}`",
        "",
        "## Formal Kernel",
        "",
    ]
    lines.extend(f"- `{state}`" for state in report.formal_kernel)
    lines.extend(["", "## Components", "", "| ID | Status | Open obligations |", "| --- | --- | --- |"])
    for row in report.components:
        lines.append(f"| `{row.id}` | `{row.status}` | {'<br>'.join(row.open_obligations) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

