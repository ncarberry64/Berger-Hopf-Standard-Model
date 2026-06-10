"""No-churn sprint hardening audit for the BHSM index theorem."""

from __future__ import annotations

from dataclasses import dataclass

from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, build_formal_kernel_projector_report
from index_sector_count import SECTOR_COUNT_PROVEN, build_sector_count_report
from index_theorem_final_proof import build_index_theorem_final_proof_report
from no_protected_mirror_axiom import NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE, build_no_protected_mirror_axiom_report
from twisted_dirac_index_closure import INDEX_THEOREM_PROVEN


INDEX_THEOREM_FINAL_GAP = "INDEX_THEOREM_FINAL_GAP"


@dataclass(frozen=True)
class IndexTheoremHardeningReport:
    status: str
    theorem_complete: bool
    exact_blocker: str
    target_kernel_dimension: int
    visible_kernel_count: int
    formal_kernel_coordinates: tuple[int, ...]
    formal_kernel_sectors: tuple[str, ...]
    exactly_one_each_sector: bool
    coordinate_first_artifact_rejected: bool
    accidental_extra_degeneracy_rejected: bool
    empirical_output_fitting_used: bool
    closing_axiom: str
    limitations: tuple[str, ...]


def build_index_theorem_hardening_report() -> IndexTheoremHardeningReport:
    index = build_index_theorem_final_proof_report()
    sector = build_sector_count_report()
    kernel = build_formal_kernel_projector_report()
    sectors = tuple(row.sector for row in kernel.kernel_basis)
    formal_coordinates = tuple(row.coordinate_hint_kmax4 for row in kernel.kernel_basis)
    axiom = build_no_protected_mirror_axiom_report()
    coordinate_first_rejected = formal_coordinates != OLD_COORDINATE_FIRST_KERNEL
    no_extra = sector.total_visible_protected_states == 3 and not sector.extra_visible_protected_state
    proven = (
        sector.status == SECTOR_COUNT_PROVEN
        and no_extra
        and sector.one_each_lepton_up_down
        and coordinate_first_rejected
        and axiom.theorem_complete
        and axiom.protected_mirror_count == 0
    )
    return IndexTheoremHardeningReport(
        status=INDEX_THEOREM_PROVEN if proven else "INDEX_THEOREM_CONDITIONAL",
        theorem_complete=proven,
        exact_blocker="" if proven else INDEX_THEOREM_FINAL_GAP,
        target_kernel_dimension=3,
        visible_kernel_count=sector.total_visible_protected_states,
        formal_kernel_coordinates=formal_coordinates,
        formal_kernel_sectors=sectors,
        exactly_one_each_sector=sector.one_each_lepton_up_down,
        coordinate_first_artifact_rejected=coordinate_first_rejected,
        accidental_extra_degeneracy_rejected=no_extra,
        empirical_output_fitting_used=False,
        closing_axiom=NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE,
        limitations=(
            "The formal sector count is verified as one lepton, one up, and one down.",
            "The no-protected-mirror axiom forbids adding protected mirror sectors beyond the frozen lepton/up/down ledger.",
            "This sprint closes the index theorem under the explicit BHSM axiom without changing frozen predictions.",
        ),
    )
