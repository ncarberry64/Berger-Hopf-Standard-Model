"""BHSM v2.3 full mirror-exclusion closure scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from boundary_mirror_channel import BOUNDARY_MIRROR_CHANNEL_CONDITIONAL, build_boundary_mirror_channel_report
from chiral_projector_closure import CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL, build_chiral_projector_closure_report
from higgs_u1_mirror_channel import HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL, build_higgs_u1_mirror_channel_report
from mirror_mode_exclusion import generate_mirror_mode_candidates


MIRROR_EXCLUSION_PROVEN = "MIRROR_EXCLUSION_PROVEN"
MIRROR_EXCLUSION_CANDIDATE = "MIRROR_EXCLUSION_CANDIDATE"
MIRROR_EXCLUSION_CONDITIONAL = "MIRROR_EXCLUSION_CONDITIONAL"
MIRROR_EXCLUSION_OPEN = "MIRROR_EXCLUSION_OPEN"
FAILS_MIRROR_EXCLUSION = "FAILS_MIRROR_EXCLUSION"


@dataclass(frozen=True)
class FullMirrorExclusionReport:
    title: str
    mirror_candidate_count: int
    chiral_projector_status: str
    higgs_u1_mirror_channel_status: str
    boundary_mirror_channel_status: str
    all_channels_at_least_conditional: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_full_mirror_exclusion_report() -> FullMirrorExclusionReport:
    candidates = generate_mirror_mode_candidates()
    chiral = build_chiral_projector_closure_report()
    higgs = build_higgs_u1_mirror_channel_report()
    boundary = build_boundary_mirror_channel_report()
    conditional = (
        chiral.status == CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL
        and higgs.status == HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL
        and boundary.status == BOUNDARY_MIRROR_CHANNEL_CONDITIONAL
    )
    return FullMirrorExclusionReport(
        title="BHSM v2.3 Full Mirror Exclusion Report",
        mirror_candidate_count=len(candidates),
        chiral_projector_status=chiral.status,
        higgs_u1_mirror_channel_status=higgs.status,
        boundary_mirror_channel_status=boundary.status,
        all_channels_at_least_conditional=conditional,
        status=MIRROR_EXCLUSION_CONDITIONAL if conditional else MIRROR_EXCLUSION_OPEN,
        theorem_complete=False,
        open_obligations=(
            *chiral.limitations,
            *higgs.open_obligations,
            *boundary.open_obligations,
            "prove no mirror state in H_perp lies below the H_T threshold in the complete operator",
        ),
        limitations=(
            "Mirror exclusion is conditionally closed by internal channels in the scaffold.",
            "It is not marked MIRROR_EXCLUSION_PROVEN because Higgs-U1 and boundary channels are not standalone complete-operator proofs.",
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


def export_full_mirror_exclusion_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_full_mirror_exclusion_report()), indent=2, sort_keys=True) + "\n")


def export_full_mirror_exclusion_markdown(path: str | Path) -> None:
    report = build_full_mirror_exclusion_report()
    lines = [
        "# BHSM v2.3 Full Mirror Exclusion Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Mirror candidate count: `{report.mirror_candidate_count}`",
        "",
        "| Channel | Status |",
        "| --- | --- |",
        f"| chiral projector | `{report.chiral_projector_status}` |",
        f"| Higgs-U1 | `{report.higgs_u1_mirror_channel_status}` |",
        f"| boundary functional | `{report.boundary_mirror_channel_status}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
