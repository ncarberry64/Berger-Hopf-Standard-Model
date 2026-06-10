"""Mirror-mode exclusion theorem completion wrapper."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mirror_exclusion_derivation import MirrorExclusionReport, build_mirror_exclusion_report


MIRROR_EXCLUSION_PROVEN = "MIRROR_EXCLUSION_PROVEN"
MIRROR_EXCLUSION_CANDIDATE = "MIRROR_EXCLUSION_CANDIDATE"
MIRROR_EXCLUSION_OPEN = "MIRROR_EXCLUSION_OPEN"
FAILS_INDEX_OR_MIRROR = "FAILS_INDEX_OR_MIRROR"


@dataclass(frozen=True)
class MirrorExclusionTheoremReport:
    """Full-operator mirror exclusion status."""

    title: str
    scaffold_report: MirrorExclusionReport
    chiral_channel_excludes_all_generated: bool
    higgs_u1_channel_closed: bool
    boundary_functional_channel_closed: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_mirror_exclusion_theorem_report() -> MirrorExclusionTheoremReport:
    """Build the conservative mirror-exclusion theorem report."""

    scaffold = build_mirror_exclusion_report()
    chiral_excludes = scaffold.excluded_count == len(scaffold.derivations)
    higgs_closed = False
    boundary_closed = False
    theorem_complete = chiral_excludes and higgs_closed and boundary_closed
    status = MIRROR_EXCLUSION_PROVEN if theorem_complete else MIRROR_EXCLUSION_OPEN
    return MirrorExclusionTheoremReport(
        title="BHSM Full Mirror-Mode Exclusion Theorem Attempt",
        scaffold_report=scaffold,
        chiral_channel_excludes_all_generated=chiral_excludes,
        higgs_u1_channel_closed=higgs_closed,
        boundary_functional_channel_closed=boundary_closed,
        status=status,
        theorem_complete=theorem_complete,
        open_obligations=(
            "close the Higgs-selected U(1) mirror channel in the complete operator",
            "close the boundary-functional mirror channel in the complete operator",
            "connect mirror exclusion to the full topological index theorem",
        ),
        limitations=(
            "The chiral projector scaffold excludes generated mirrors, but full-operator mirror exclusion is not complete.",
            "No empirical masses, CKM values, or residuals enter this report.",
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


def export_mirror_exclusion_theorem_json(path: str | Path) -> None:
    """Export the mirror-exclusion theorem report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_mirror_exclusion_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_mirror_exclusion_theorem_markdown(path: str | Path) -> None:
    """Export the mirror-exclusion theorem report as Markdown."""

    report = build_mirror_exclusion_theorem_report()
    lines = [
        "# BHSM Full Mirror-Mode Exclusion Theorem Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Channel Summary",
        "",
        f"- Chiral channel excludes generated mirrors: `{report.chiral_channel_excludes_all_generated}`",
        f"- Higgs-U1 channel closed: `{report.higgs_u1_channel_closed}`",
        f"- Boundary-functional channel closed: `{report.boundary_functional_channel_closed}`",
        "",
        "## Open Obligations",
        "",
        *[f"- {item}" for item in report.open_obligations],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report.limitations],
        "",
    ]
    Path(path).write_text("\n".join(lines))

