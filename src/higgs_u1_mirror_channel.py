"""BHSM v2.3 Higgs-U1 mirror-channel audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from higgs_u1_boundary_phase import evaluate_higgs_u1_phase
from mirror_mode_exclusion import generate_mirror_mode_candidates


HIGGS_U1_MIRROR_CHANNEL_CLOSED = "HIGGS_U1_MIRROR_CHANNEL_CLOSED"
HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL = "HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL"
HIGGS_U1_MIRROR_CHANNEL_OPEN = "HIGGS_U1_MIRROR_CHANNEL_OPEN"


@dataclass(frozen=True)
class HiggsU1MirrorChannelReport:
    title: str
    candidate_count: int
    phase_channel_present: bool
    chirality_resolved_exclusion_proven: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_higgs_u1_mirror_channel_report() -> HiggsU1MirrorChannelReport:
    candidates = generate_mirror_mode_candidates()
    rows = [evaluate_higgs_u1_phase(candidate.sector, candidate.chirality) for candidate in candidates]
    present = all(row.hypercharge_higgs_boundary is not None for row in rows)
    return HiggsU1MirrorChannelReport(
        title="BHSM v2.3 Higgs-U1 Mirror Channel Report",
        candidate_count=len(rows),
        phase_channel_present=present,
        chirality_resolved_exclusion_proven=False,
        status=HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL if present else HIGGS_U1_MIRROR_CHANNEL_OPEN,
        theorem_complete=False,
        open_obligations=("derive a chirality-resolved Higgs-selected U1 mirror phase mismatch in the complete operator",),
        limitations=(
            "The Higgs-selected U1 phase is action-linked and present, but it is not a completed standalone mirror-exclusion proof.",
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


def export_higgs_u1_mirror_channel_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_higgs_u1_mirror_channel_report()), indent=2, sort_keys=True) + "\n")


def export_higgs_u1_mirror_channel_markdown(path: str | Path) -> None:
    report = build_higgs_u1_mirror_channel_report()
    lines = [
        "# BHSM v2.3 Higgs-U1 Mirror Channel Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Phase channel present: `{report.phase_channel_present}`",
        f"Chirality-resolved exclusion proven: `{report.chirality_resolved_exclusion_proven}`",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
