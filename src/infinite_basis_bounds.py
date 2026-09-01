"""BHSM v1.3E infinite-basis sector-bound theorem scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from domain_assumptions import (
    InfiniteBasisAssumption,
    build_infinite_basis_assumptions,
    candidate_a_k_max,
    candidate_structured_margin,
)
from hilbert_space_scaffold import (
    HilbertSpaceDomain,
    UnboundedOperatorDomain,
    build_hilbert_space_domain,
    build_operator_domains,
)


THEOREM_STATUSES = ("THEOREM_SCAFFOLD", "THEOREM_PROVEN", "OPEN")


@dataclass(frozen=True)
class InfiniteRelativeBoundTheorem:
    """Conditional theorem scaffold for the sector-coupling relative bound."""

    title: str
    status: str
    assumptions: tuple[InfiniteBasisAssumption, ...]
    implication: str
    theorem_complete: bool
    proof_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class InfiniteBoundReport:
    """Complete v1.3E infinite-basis/domain report."""

    title: str
    hilbert_domain: HilbertSpaceDomain
    operator_domains: tuple[UnboundedOperatorDomain, ...]
    theorem: InfiniteRelativeBoundTheorem
    finite_evidence_bridge: dict[str, float | int | bool | str]
    conservative_candidate: dict[str, float | bool]
    theorem_complete: bool
    limitations: tuple[str, ...]


def finite_evidence_bridge() -> dict[str, float | int | bool | str]:
    """Return the v1.3D finite evidence summarized for the infinite scaffold."""

    return {
        "source": "theory/uniform_relative_bound_report.json",
        "classification": "UNIFORM_BOUND_CANDIDATE",
        "rows_scanned": 108,
        "k_max_max": 32,
        "all_rows_pass": True,
        "all_b_k_zero": True,
        "observed_max_a_k": 0.03095889839310559,
        "observed_min_structured_lower_bound": 1.418773076862654,
        "observed_min_finite_basis_lower_bound": 1.4599918132873242,
        "max_mode_block_band_width": 2,
        "theorem_complete": False,
    }


def build_infinite_relative_bound_theorem(a_k_max: float | None = None) -> InfiniteRelativeBoundTheorem:
    """Return the conditional infinite-basis theorem scaffold."""

    assumptions = build_infinite_basis_assumptions(a_k_max=a_k_max)
    return InfiniteRelativeBoundTheorem(
        title="Conditional Infinite-Basis Sector-Coupling Relative-Bound Scaffold",
        status="THEOREM_SCAFFOLD",
        assumptions=assumptions,
        implication=(
            "If A1-A6 hold on the full Hilbert-space domain, then K_sector is "
            "D0^2-relative bounded on H_perp and cannot close the required complement gap."
        ),
        theorem_complete=False,
        proof_obligations=(
            "Derive A1-A2 from the full Berger-Hopf twisted Dirac/bundle action.",
            "Prove the A3 relative-bound inequality uniformly on the infinite basis.",
            "Prove the protected zero-mode subspace and complement projector in the full action.",
            "Prove the diagonal complement lower bound A6 on H_perp.",
        ),
        limitations=(
            "The implication is conditional on A1-A6.",
            "Finite v1.3D evidence is not labeled as an infinite-basis proof.",
        ),
    )


def build_infinite_bound_report(a_k_max: float | None = None) -> InfiniteBoundReport:
    """Build the complete v1.3E infinite-basis/domain scaffold report."""

    resolved_a = candidate_a_k_max() if a_k_max is None else float(a_k_max)
    return InfiniteBoundReport(
        title="BHSM v1.3E Hilbert-Space and Infinite Sector-Bound Scaffold",
        hilbert_domain=build_hilbert_space_domain(),
        operator_domains=build_operator_domains(),
        theorem=build_infinite_relative_bound_theorem(resolved_a),
        finite_evidence_bridge=finite_evidence_bridge(),
        conservative_candidate=candidate_structured_margin(resolved_a),
        theorem_complete=False,
        limitations=(
            "This report defines assumptions under which the finite relative-bound evidence would extend beyond truncations.",
            "It does not prove those assumptions or complete the full H_T theorem.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_infinite_sector_bound_json(path: str | Path) -> None:
    """Export the infinite sector-bound theorem scaffold as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_infinite_bound_report()), indent=2, sort_keys=True) + "\n")


def export_infinite_sector_bound_markdown(path: str | Path) -> None:
    """Export the infinite sector-bound theorem scaffold as Markdown."""

    report = build_infinite_bound_report()
    theorem = report.theorem
    margin = report.conservative_candidate
    lines = [
        "# BHSM v1.3E Infinite Sector-Coupling Bound Scaffold",
        "",
        f"Status: `{theorem.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "BHSM v1.3E defines the Hilbert-space/domain assumptions under which the structured sector-coupling relative bound would extend beyond finite truncations. It does not prove the full H_T theorem until those assumptions and the zero-mode/complement split are derived from the complete operator.",
        "",
        "## Finite Evidence Bridge",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
    ]
    for key, value in report.finite_evidence_bridge.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Conservative Candidate",
            "",
            "| Quantity | Value |",
            "| --- | --- |",
        ]
    )
    for key, value in margin.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Assumptions A1-A6",
            "",
            "| ID | Status | Statement | Limitations |",
            "| --- | --- | --- | --- |",
        ]
    )
    for assumption in theorem.assumptions:
        lines.append(
            f"| `{assumption.id}` | `{assumption.status}` | {assumption.statement} | {' '.join(assumption.limitations)} |"
        )
    lines.extend(
        [
            "",
            "## Conditional Implication",
            "",
            theorem.implication,
            "",
            "## Proof Obligations",
            "",
            *[f"- {item}" for item in theorem.proof_obligations],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
