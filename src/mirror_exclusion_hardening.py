"""No-churn sprint hardening audit for mirror exclusion."""

from __future__ import annotations

from dataclasses import dataclass

from boundary_mirror_channel import build_boundary_mirror_channel_report
from chiral_projector_closure import build_chiral_projector_closure_report
from full_mirror_exclusion import MIRROR_EXCLUSION_PROVEN, build_full_mirror_exclusion_report
from higgs_u1_mirror_channel import build_higgs_u1_mirror_channel_report
from mirror_mode_exclusion import generate_mirror_mode_candidates
from no_protected_mirror_axiom import NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE, build_no_protected_mirror_axiom_report


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
    closing_axiom: str
    protected_mirror_count: int
    new_particle_mode_count: int
    limitations: tuple[str, ...]


def build_mirror_exclusion_hardening_report() -> MirrorExclusionHardeningReport:
    mirror = build_full_mirror_exclusion_report()
    chiral = build_chiral_projector_closure_report()
    higgs = build_higgs_u1_mirror_channel_report()
    boundary = build_boundary_mirror_channel_report()
    candidates = generate_mirror_mode_candidates()
    axiom = build_no_protected_mirror_axiom_report()
    proven = axiom.theorem_complete and axiom.protected_mirror_count == 0 and axiom.new_particle_mode_count == 0
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
        closing_axiom=NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE,
        protected_mirror_count=axiom.protected_mirror_count,
        new_particle_mode_count=axiom.new_particle_mode_count,
        limitations=(
            "The chiral channel excludes generated scaffold mirror candidates.",
            "The no-protected-mirror axiom classifies any residual Higgs-U1, boundary, coordinate-first, or topographic/mixed mirror channel as non-protected unless it would create a forbidden new particle/mode sector.",
            "No frozen sector ledger expansion or prediction retuning is introduced.",
        ),
    )
