"""BHSM v1.3I Higgs-selected U(1) mirror-channel scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from bundle_boundary_conditions import sector_boundary_functional
from internal_action import higgs_u1_boundary_phase


EXCLUDED_BY_HIGGS_U1_PHASE = "EXCLUDED_BY_HIGGS_U1_PHASE"
PHASE_COMPATIBLE = "PHASE_COMPATIBLE"
OPEN = "OPEN"


@dataclass(frozen=True)
class HiggsU1PhaseRule:
    """Higgs-selected U(1) phase compatibility rule for a mirror candidate."""

    sector: str
    candidate_chirality: int
    hypercharge_higgs_boundary: int | None
    source_term: str
    status: str
    derived_from_internal_structure: bool
    rationale: tuple[str, ...]
    limitations: tuple[str, ...]


def evaluate_higgs_u1_phase(sector: str, candidate_chirality: int) -> HiggsU1PhaseRule:
    """Evaluate the Higgs-selected U(1) channel for a mirror candidate.

    The current v1.2 boundary functional supplies a sector U(1) orientation,
    but it does not by itself encode a complete chirality-resolved spectral
    exclusion. Therefore this channel is reported as open unless a future
    action-level rule makes the phase mismatch explicit.
    """

    functional = sector_boundary_functional(sector)
    term = higgs_u1_boundary_phase()
    return HiggsU1PhaseRule(
        sector=sector,
        candidate_chirality=int(candidate_chirality),
        hypercharge_higgs_boundary=functional.hypercharge_higgs_boundary,
        source_term=term.id,
        status=OPEN,
        derived_from_internal_structure=False,
        rationale=(
            "The Higgs-selected U(1) boundary phase is present in the v1.2 parent-action scaffold.",
            "The current scaffold does not yet derive a chirality-resolved phase mismatch for mirror candidates.",
        ),
        limitations=(
            "Higgs-U(1) channel remains open for mirror exclusion.",
            "This does not weaken the separate chiral-projector exclusion channel.",
        ),
    )
