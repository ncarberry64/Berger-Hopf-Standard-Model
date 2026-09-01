"""BHSM v1.3G zero-mode inventory and index scaffold.

This module records the protected-family zero-mode candidates and the
assumptions needed to upgrade the current finite-basis scaffold into an index
theorem. It is an audit layer only; it does not alter BHSM predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hilbert_space_scaffold import HilbertBasisLabel, hopf_charge, protected_zero_mode_labels


INDEX_SCAFFOLD = "INDEX_SCAFFOLD"
INDEX_THEOREM_PROVEN = "INDEX_THEOREM_PROVEN"
PROTECTED = "PROTECTED"
LIFTED = "LIFTED"
OPEN = "OPEN"


@dataclass(frozen=True)
class ZeroModeCandidate:
    """A candidate protected zero mode in the BHSM index scaffold."""

    id: str
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    boundary_condition: str
    index_contribution: int
    status: str
    mirror_mode_status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IndexContribution:
    """Index contribution grouped by charged sector."""

    sector: str
    protected_modes: int
    positive_chirality_zero_modes: int
    negative_chirality_zero_modes: int
    net_index_contribution: int
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IndexTheoremAssumption:
    """Assumption needed for the full twisted-Dirac index theorem."""

    id: str
    statement: str
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ZeroModeSplitReport:
    """Zero-mode/index scaffold report."""

    title: str
    target_index: int
    target_kernel_dimension: int
    candidates: tuple[ZeroModeCandidate, ...]
    contributions: tuple[IndexContribution, ...]
    assumptions: tuple[IndexTheoremAssumption, ...]
    index_status: str
    mirror_zero_mode_status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def protected_family_zero_modes() -> tuple[ZeroModeCandidate, ...]:
    """Return the three formal protected-family zero-mode candidates."""

    rows = []
    for label in protected_zero_mode_labels():
        rows.append(
            ZeroModeCandidate(
                id=f"zero_mode_{label.sector}",
                sector=label.sector,
                k=label.k,
                j=label.j,
                q=label.q,
                chirality=label.chirality,
                boundary_condition=f"sector boundary functional for {label.sector}",
                index_contribution=1,
                status=PROTECTED,
                mirror_mode_status=OPEN,
                limitations=(
                    "Candidate is protected in the scaffold, not proven from the full twisted Dirac operator.",
                    "Absence of an opposite-chirality mirror zero mode remains an index-theorem assumption.",
                ),
            )
        )
    return tuple(rows)


def candidate_to_hilbert_label(candidate: ZeroModeCandidate) -> HilbertBasisLabel:
    """Convert a zero-mode candidate to a Hilbert-space label."""

    return HilbertBasisLabel(
        k=candidate.k,
        j=candidate.j,
        q=hopf_charge(candidate.k, candidate.j),
        chirality=candidate.chirality,
        sector=candidate.sector,
        protected_zero_mode=True,
    )


def zero_mode_index_contributions() -> tuple[IndexContribution, ...]:
    """Return sector-wise index contributions for the scaffold."""

    contributions = []
    for candidate in protected_family_zero_modes():
        positive = 1 if candidate.chirality > 0 else 0
        negative = 1 if candidate.chirality < 0 else 0
        contributions.append(
            IndexContribution(
                sector=candidate.sector,
                protected_modes=1,
                positive_chirality_zero_modes=positive,
                negative_chirality_zero_modes=negative,
                net_index_contribution=candidate.index_contribution,
                assumptions=(
                    "The chirality orientation is fixed by the BHSM protected-family convention.",
                    "No opposite-chirality mirror zero mode cancels this contribution.",
                ),
                limitations=("This contribution is scaffolded until derived from the full index theorem.",),
            )
        )
    return tuple(contributions)


def index_theorem_assumptions() -> tuple[IndexTheoremAssumption, ...]:
    """Return assumptions needed for Index(D_twist)=3."""

    return (
        IndexTheoremAssumption(
            id="I1",
            statement="The twisted bundle charge/topological number gives total index three.",
            status=OPEN,
            evidence=("Three protected-family labels are present in the scaffold.",),
            limitations=("The topological index calculation has not been completed.",),
        ),
        IndexTheoremAssumption(
            id="I2",
            statement="The Higgs-selected U(1) boundary phase selects the protected chiral kernel.",
            status="ACTION_LINKED",
            evidence=("The U(1) boundary phase is part of the v1.2 parent-action scaffold.",),
            limitations=("The full spectral consequence remains open.",),
        ),
        IndexTheoremAssumption(
            id="I3",
            statement="No opposite-chirality mirror zero modes survive in the physical kernel.",
            status=OPEN,
            evidence=("No mirror modes are inserted in the scaffold.",),
            limitations=("Mirror exclusion must be proven from the complete operator.",),
        ),
        IndexTheoremAssumption(
            id="I4",
            statement="The v1.2 sector boundary functional is the boundary condition for the full kernel problem.",
            status="REDUCED_FROM_PARENT_ACTION",
            evidence=("v1.2B/v1.2C reduced and audited the symbolic boundary functional.",),
            limitations=("Global uniqueness of the complete internal action remains open.",),
        ),
        IndexTheoremAssumption(
            id="I5",
            statement="The trace U(1) is topological/nondynamical and does not add a light gauge zero mode.",
            status=OPEN,
            evidence=("The condition is carried in the theorem scaffold and claims ledger.",),
            limitations=("A full action-level proof remains open.",),
        ),
    )


def build_zero_mode_split_report() -> ZeroModeSplitReport:
    """Build the v1.3G zero-mode/index scaffold report."""

    candidates = protected_family_zero_modes()
    contributions = zero_mode_index_contributions()
    target_index = sum(item.net_index_contribution for item in contributions)
    mirror_status = OPEN if any(item.mirror_mode_status == OPEN for item in candidates) else "EXCLUDED"
    return ZeroModeSplitReport(
        title="BHSM v1.3G Zero-Mode Index Scaffold",
        target_index=target_index,
        target_kernel_dimension=len(candidates),
        candidates=candidates,
        contributions=contributions,
        assumptions=index_theorem_assumptions(),
        index_status=INDEX_SCAFFOLD,
        mirror_zero_mode_status=mirror_status,
        theorem_complete=False,
        limitations=(
            "Index(D_twist)=3 is scaffolded, not proven.",
            "Mirror zero-mode exclusion remains open until derived from the complete operator.",
            "This module does not change frozen BHSM predictions or branch outputs.",
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


def export_zero_mode_index_json(path: str | Path) -> None:
    """Export the zero-mode index scaffold as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_zero_mode_split_report()), indent=2, sort_keys=True) + "\n")


def export_zero_mode_index_markdown(path: str | Path) -> None:
    """Export the zero-mode index scaffold as Markdown."""

    report = build_zero_mode_split_report()
    lines = [
        "# BHSM v1.3G Zero-Mode Index Scaffold",
        "",
        f"Index status: `{report.index_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Target index: `{report.target_index}`",
        f"Target kernel dimension: `{report.target_kernel_dimension}`",
        f"Mirror zero-mode status: `{report.mirror_zero_mode_status}`",
        "",
        "## Protected Zero-Mode Candidates",
        "",
        "| ID | Sector | k | j | q | chirality | boundary condition | contribution | status | mirror status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.candidates:
        lines.append(
            f"| `{item.id}` | `{item.sector}` | `{item.k}` | `{item.j}` | `{item.q}` | `{item.chirality}` | {item.boundary_condition} | `{item.index_contribution}` | `{item.status}` | `{item.mirror_mode_status}` |"
        )
    lines.extend(
        [
            "",
            "## Index Assumptions",
            "",
            "| ID | Status | Statement |",
            "| --- | --- | --- |",
        ]
    )
    for assumption in report.assumptions:
        lines.append(f"| `{assumption.id}` | `{assumption.status}` | {assumption.statement} |")
    lines.extend(["", "## Limitations", "", *[f"- {item}" for item in report.limitations], ""])
    Path(path).write_text("\n".join(lines))
