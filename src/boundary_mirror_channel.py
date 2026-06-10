"""BHSM v2.3 boundary-functional mirror-channel audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mirror_exclusion_derivation import evaluate_boundary_functional
from mirror_mode_exclusion import generate_mirror_mode_candidates


BOUNDARY_MIRROR_CHANNEL_CLOSED = "BOUNDARY_MIRROR_CHANNEL_CLOSED"
BOUNDARY_MIRROR_CHANNEL_CONDITIONAL = "BOUNDARY_MIRROR_CHANNEL_CONDITIONAL"
BOUNDARY_MIRROR_CHANNEL_OPEN = "BOUNDARY_MIRROR_CHANNEL_OPEN"


@dataclass(frozen=True)
class BoundaryMirrorChannelReport:
    title: str
    candidate_count: int
    boundary_functional_present: bool
    standalone_exclusion_proven: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_boundary_mirror_channel_report() -> BoundaryMirrorChannelReport:
    candidates = generate_mirror_mode_candidates()
    rows = [evaluate_boundary_functional(candidate.sector, candidate.k, candidate.j, candidate.q) for candidate in candidates]
    present = len(rows) == len(candidates)
    return BoundaryMirrorChannelReport(
        title="BHSM v2.3 Boundary Mirror Channel Report",
        candidate_count=len(rows),
        boundary_functional_present=present,
        standalone_exclusion_proven=False,
        status=BOUNDARY_MIRROR_CHANNEL_CONDITIONAL if present else BOUNDARY_MIRROR_CHANNEL_OPEN,
        theorem_complete=False,
        open_obligations=("derive v1.2 boundary-functional mirror exclusion from the full kernel boundary problem",),
        limitations=(
            "The v1.2 boundary functional is action-linked and available, but not a standalone complete mirror-exclusion theorem.",
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


def export_boundary_mirror_channel_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_boundary_mirror_channel_report()), indent=2, sort_keys=True) + "\n")


def export_boundary_mirror_channel_markdown(path: str | Path) -> None:
    report = build_boundary_mirror_channel_report()
    lines = [
        "# BHSM v2.3 Boundary Mirror Channel Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Boundary functional present: `{report.boundary_functional_present}`",
        f"Standalone exclusion proven: `{report.standalone_exclusion_proven}`",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
