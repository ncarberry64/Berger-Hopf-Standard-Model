"""BHSM v2.3 chiral-projector mirror-channel closure."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from chiral_projector import EXCLUDED_BY_CHIRAL_PROJECTOR, evaluate_chiral_projection
from mirror_mode_exclusion import generate_mirror_mode_candidates


CHIRAL_PROJECTOR_CLOSURE_PROVEN = "CHIRAL_PROJECTOR_CLOSURE_PROVEN"
CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL = "CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL"
CHIRAL_PROJECTOR_CLOSURE_OPEN = "CHIRAL_PROJECTOR_CLOSURE_OPEN"
FAILS_CHIRAL_PROJECTOR_CLOSURE = "FAILS_CHIRAL_PROJECTOR_CLOSURE"


@dataclass(frozen=True)
class ChiralProjectorClosureReport:
    title: str
    candidate_count: int
    excluded_by_chiral_projector: int
    compatible_with_formal_kernel: bool
    compatible_with_complement_projector: bool
    compatible_with_higgs_u1_channel: bool
    compatible_with_boundary_channel: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_chiral_projector_closure_report() -> ChiralProjectorClosureReport:
    candidates = generate_mirror_mode_candidates()
    rows = [evaluate_chiral_projection(candidate.sector, candidate.chirality) for candidate in candidates]
    excluded = sum(row.status == EXCLUDED_BY_CHIRAL_PROJECTOR and row.derived_from_internal_structure for row in rows)
    all_excluded = excluded == len(rows)
    status = CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL if all_excluded else CHIRAL_PROJECTOR_CLOSURE_OPEN
    return ChiralProjectorClosureReport(
        title="BHSM v2.3 Chiral Projector Closure Report",
        candidate_count=len(rows),
        excluded_by_chiral_projector=excluded,
        compatible_with_formal_kernel=True,
        compatible_with_complement_projector=True,
        compatible_with_higgs_u1_channel=True,
        compatible_with_boundary_channel=True,
        status=status,
        theorem_complete=False,
        limitations=(
            "The chiral projector excludes scaffold mirror candidates by internal chirality data.",
            "The complete operator must still prove no opposite-chirality kernel survives outside this channel.",
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


def export_chiral_projector_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_chiral_projector_closure_report()), indent=2, sort_keys=True) + "\n")


def export_chiral_projector_closure_markdown(path: str | Path) -> None:
    report = build_chiral_projector_closure_report()
    lines = [
        "# BHSM v2.3 Chiral Projector Closure Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Candidate count: `{report.candidate_count}`",
        f"Excluded by chiral projector: `{report.excluded_by_chiral_projector}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
