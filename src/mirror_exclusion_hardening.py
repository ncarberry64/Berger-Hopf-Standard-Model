"""No-churn sprint hardening audit for mirror exclusion."""

from __future__ import annotations

from dataclasses import dataclass

from boundary_mirror_channel import build_boundary_mirror_channel_report
from chiral_projector_closure import build_chiral_projector_closure_report
from full_mirror_exclusion import MIRROR_EXCLUSION_PROVEN, build_full_mirror_exclusion_report
from higgs_u1_mirror_channel import build_higgs_u1_mirror_channel_report
from mirror_mode_exclusion import generate_mirror_mode_candidates


MIRROR_EXCLUSION_FINAL_GAP = "MIRROR_EXCLUSION_FINAL_GAP"


@dataclass(frozen=True)
class MirrorExclusionHardeningReport:
    status: str
    theorem_complete: bool
    exact_blocker: str
    mirror_candidate_count: int
    chiral_channel_status: str
    higgs_u1_channel_status: str
    boundary_channel_status: str
    sector_labeled_alignment_used: bool
    topographic_representation_rule_used: bool
    no_mirror_leakage_from_topographic_sector: bool
    limitations: tuple[str, ...]


def build_mirror_exclusion_hardening_report() -> MirrorExclusionHardeningReport:
    mirror = build_full_mirror_exclusion_report()
    chiral = build_chiral_projector_closure_report()
    higgs = build_higgs_u1_mirror_channel_report()
    boundary = build_boundary_mirror_channel_report()
    candidates = generate_mirror_mode_candidates()
    proven = mirror.status == MIRROR_EXCLUSION_PROVEN
    return MirrorExclusionHardeningReport(
        status=MIRROR_EXCLUSION_PROVEN if proven else "MIRROR_EXCLUSION_CONDITIONAL",
        theorem_complete=proven,
        exact_blocker="" if proven else MIRROR_EXCLUSION_FINAL_GAP,
        mirror_candidate_count=len(candidates),
        chiral_channel_status=chiral.status,
        higgs_u1_channel_status=higgs.status,
        boundary_channel_status=boundary.status,
        sector_labeled_alignment_used=True,
        topographic_representation_rule_used=True,
        no_mirror_leakage_from_topographic_sector=proven,
        limitations=(
            "The chiral channel excludes generated scaffold mirror candidates.",
            "Higgs-U1 and boundary mirror channels remain conditional rather than standalone complete-operator proofs.",
            "No mirror leakage from represented topographic sectors is not marked proven until the complete mirror theorem closes.",
        ),
    )
