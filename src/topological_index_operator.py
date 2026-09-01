"""BHSM v2.3 topological-index operator scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from index_sector_count import SECTOR_COUNT_PROVEN, build_sector_count_report
from zero_mode_index import build_zero_mode_split_report


INDEX_THEOREM_PROVEN = "INDEX_THEOREM_PROVEN"
INDEX_THEOREM_CANDIDATE = "INDEX_THEOREM_CANDIDATE"
INDEX_THEOREM_CONDITIONAL = "INDEX_THEOREM_CONDITIONAL"
INDEX_THEOREM_OPEN = "INDEX_THEOREM_OPEN"
FAILS_INDEX_THEOREM = "FAILS_INDEX_THEOREM"


@dataclass(frozen=True)
class TopologicalIndexContribution:
    source: str
    contribution: int
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class TopologicalIndexOperatorReport:
    title: str
    target_index: int
    visible_kernel_dimension: int
    sector_count_status: str
    contributions: tuple[TopologicalIndexContribution, ...]
    scaffold_index: int
    exactly_three_visible_states: bool
    lepton_up_down_not_coordinate_artifact: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_topological_index_operator_report() -> TopologicalIndexOperatorReport:
    zero = build_zero_mode_split_report()
    sector = build_sector_count_report()
    contributions = tuple(
        TopologicalIndexContribution(
            source=f"{candidate.sector}_protected_kernel",
            contribution=candidate.index_contribution,
            status="SCAFFOLD_CONTRIBUTION_VERIFIED",
            assumptions=("protected chirality chi=-1", "mirror contribution is excluded or lifted in the mirror-channel audit"),
            limitations=("Not a completed topological density/integral calculation.",),
        )
        for candidate in zero.candidates
    )
    scaffold_index = sum(row.contribution for row in contributions)
    exact_visible = scaffold_index == 3 and sector.status == SECTOR_COUNT_PROVEN
    status = INDEX_THEOREM_CONDITIONAL if exact_visible else FAILS_INDEX_THEOREM
    return TopologicalIndexOperatorReport(
        title="BHSM v2.3 Topological Index Operator Scaffold",
        target_index=3,
        visible_kernel_dimension=len(zero.candidates),
        sector_count_status=sector.status,
        contributions=contributions,
        scaffold_index=scaffold_index,
        exactly_three_visible_states=exact_visible,
        lepton_up_down_not_coordinate_artifact=not sector.duplicate_lepton_coordinate_artifact,
        status=status,
        theorem_complete=False,
        open_obligations=(
            "derive the index density/topological charge formula for the complete twisted Dirac operator",
            "prove no additional hidden protected kernel states exist in the complete Hilbert space",
        ),
        limitations=(
            "The visible sector-labeled index count is exact in the scaffold.",
            "The full topological index theorem is conditional, not proven.",
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


def export_topological_index_operator_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_topological_index_operator_report()), indent=2, sort_keys=True) + "\n")


def export_topological_index_operator_markdown(path: str | Path) -> None:
    report = build_topological_index_operator_report()
    lines = [
        "# BHSM v2.3 Topological Index Operator Scaffold",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Target index: `{report.target_index}`",
        f"Scaffold index: `{report.scaffold_index}`",
        f"Exactly three visible states: `{report.exactly_three_visible_states}`",
        f"Lepton/up/down, not coordinate artifact: `{report.lepton_up_down_not_coordinate_artifact}`",
        "",
        "| Source | Contribution | Status |",
        "| --- | --- | --- |",
    ]
    for row in report.contributions:
        lines.append(f"| `{row.source}` | `{row.contribution}` | `{row.status}` |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
