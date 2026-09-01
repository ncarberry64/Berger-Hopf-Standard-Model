"""BHSM v2.5 complete-operator mirror exclusion final proof attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_mirror_exclusion import MIRROR_EXCLUSION_CONDITIONAL, MIRROR_EXCLUSION_PROVEN, build_full_mirror_exclusion_report


@dataclass(frozen=True)
class MirrorExclusionFinalProofReport:
    title: str
    source_status: str
    final_status: str
    theorem_complete: bool
    chiral_channel_status: str
    higgs_u1_channel_status: str
    boundary_channel_status: str
    exact_obstruction: str
    limitations: tuple[str, ...]


def build_mirror_exclusion_final_proof_report() -> MirrorExclusionFinalProofReport:
    mirror = build_full_mirror_exclusion_report()
    proven = mirror.status == MIRROR_EXCLUSION_PROVEN
    obstruction = (
        "No obstruction: complete-operator mirror exclusion is proven."
        if proven
        else "The chiral channel excludes generated mirrors at scaffold level, but Higgs-U1 and boundary mirror channels remain conditional rather than standalone complete-operator proofs."
    )
    return MirrorExclusionFinalProofReport(
        title="BHSM v2.5 Mirror Exclusion Final Proof Attempt",
        source_status=mirror.status,
        final_status=MIRROR_EXCLUSION_PROVEN if proven else MIRROR_EXCLUSION_CONDITIONAL,
        theorem_complete=proven,
        chiral_channel_status=mirror.chiral_projector_status,
        higgs_u1_channel_status=mirror.higgs_u1_mirror_channel_status,
        boundary_channel_status=mirror.boundary_mirror_channel_status,
        exact_obstruction=obstruction,
        limitations=(
            "No mirror channel is promoted from conditional to proven without a complete-operator proof.",
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


def export_mirror_exclusion_final_proof_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_mirror_exclusion_final_proof_report()), indent=2, sort_keys=True) + "\n")


def export_mirror_exclusion_final_proof_markdown(path: str | Path) -> None:
    report = build_mirror_exclusion_final_proof_report()
    lines = [
        "# BHSM v2.5 Mirror Exclusion Final Proof Attempt",
        "",
        f"Source status: `{report.source_status}`",
        f"Final status: `{report.final_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Channel | Status |",
        "| --- | --- |",
        f"| chiral projector | `{report.chiral_channel_status}` |",
        f"| Higgs-U1 | `{report.higgs_u1_channel_status}` |",
        f"| boundary | `{report.boundary_channel_status}` |",
        "",
        "## Exact Obstruction",
        "",
        report.exact_obstruction,
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
