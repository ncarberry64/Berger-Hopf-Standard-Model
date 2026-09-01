"""Finite-mode core for the BHSM infinite Hilbert basis."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from infinite_basis_domain import FORMAL_KERNEL_STATES


FINITE_CORE_DENSE = "FINITE_CORE_DENSE"
FINITE_CORE_CONDITIONAL = "FINITE_CORE_CONDITIONAL"
FAILS_FINITE_CORE = "FAILS_FINITE_CORE"


@dataclass(frozen=True)
class InfiniteBasisLabel:
    """One symbolic basis-label family."""

    sector: str
    k_range: str
    j_range: str
    q_rule: str
    chirality_values: tuple[int, int]
    multiplicity: str


@dataclass(frozen=True)
class FiniteCoreDomainReport:
    """Finite core and density report."""

    title: str
    basis_label: InfiniteBasisLabel
    finite_core: str
    infinite_completion: str
    formal_kernel: tuple[str, ...]
    coordinate_first_kernel_used: bool
    dense_in_l2: bool
    dense_in_graph_norm_for_diagonal_operator: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def bhsm_infinite_basis_label() -> InfiniteBasisLabel:
    """Return the sector-labeled infinite basis family."""

    return InfiniteBasisLabel(
        sector="ell,u,d",
        k_range="k in nonnegative integers",
        j_range="j = 0,1,...,k",
        q_rule="q = k - 2j",
        chirality_values=(-1, 1),
        multiplicity="finite sector/chirality multiplicity for each (k,j)",
    )


def build_finite_core_domain_report() -> FiniteCoreDomainReport:
    """Build the finite-core density report."""

    return FiniteCoreDomainReport(
        title="BHSM v1.9 Finite-Mode Core Domain Report",
        basis_label=bhsm_infinite_basis_label(),
        finite_core="C_fin = finite linear combinations of |sector,k,j,q,chi>",
        infinite_completion="H = l2-completion of the sector-labeled basis",
        formal_kernel=FORMAL_KERNEL_STATES,
        coordinate_first_kernel_used=False,
        dense_in_l2=True,
        dense_in_graph_norm_for_diagonal_operator=True,
        status=FINITE_CORE_DENSE,
        theorem_complete=True,
        limitations=(
            "Density is for the abstract l2 sector-labeled basis and the diagonal graph norm.",
            "This does not prove perturbation-domain preservation for the full operator.",
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


def export_finite_core_domain_json(path: str | Path) -> None:
    """Export finite-core report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_finite_core_domain_report()), indent=2, sort_keys=True) + "\n")


def export_finite_core_domain_markdown(path: str | Path) -> None:
    """Export finite-core report as Markdown."""

    report = build_finite_core_domain_report()
    lines = [
        "# BHSM v1.9 Finite-Mode Core Domain Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Coordinate-first kernel used: `{report.coordinate_first_kernel_used}`",
        "",
        "## Basis",
        "",
        f"- Sectors: `{report.basis_label.sector}`",
        f"- k range: `{report.basis_label.k_range}`",
        f"- j range: `{report.basis_label.j_range}`",
        f"- q rule: `{report.basis_label.q_rule}`",
        f"- chirality: `{report.basis_label.chirality_values}`",
        "",
        "## Formal Kernel",
        "",
    ]
    lines.extend(f"- `{state}`" for state in report.formal_kernel)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

