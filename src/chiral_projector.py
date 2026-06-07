"""BHSM v1.3I chiral projector mirror-exclusion channel."""

from __future__ import annotations

from dataclasses import dataclass

from internal_action import weak_doublet_chirality_projector


EXCLUDED_BY_CHIRAL_PROJECTOR = "EXCLUDED_BY_CHIRAL_PROJECTOR"
NOT_EXCLUDED = "NOT_EXCLUDED"
OPEN = "OPEN"


@dataclass(frozen=True)
class ChiralProjectionRule:
    """Model-internal chiral projection rule for protected zero modes."""

    sector: str
    protected_chirality: int
    candidate_chirality: int
    projector_name: str
    source_term: str
    status: str
    derived_from_internal_structure: bool
    rationale: tuple[str, ...]
    limitations: tuple[str, ...]


def protected_kernel_chirality(sector: str) -> int:
    """Return the scaffold protected-kernel chirality for a charged sector."""

    if sector not in {"lepton", "up", "down"}:
        raise ValueError(f"unknown sector: {sector}")
    return -1


def evaluate_chiral_projection(sector: str, candidate_chirality: int) -> ChiralProjectionRule:
    """Evaluate whether the weak chiral projector excludes a candidate."""

    protected = protected_kernel_chirality(sector)
    term = weak_doublet_chirality_projector()
    if candidate_chirality == protected:
        status = NOT_EXCLUDED
        derived = False
        rationale = ("Candidate chirality matches the protected kernel chirality.",)
    else:
        status = EXCLUDED_BY_CHIRAL_PROJECTOR
        derived = True
        rationale = (
            "Candidate chirality is opposite to the protected kernel chirality.",
            "The BHSM weak-doublet chiral projector admits the protected chirality in the zero-mode scaffold.",
        )
    return ChiralProjectionRule(
        sector=sector,
        protected_chirality=protected,
        candidate_chirality=int(candidate_chirality),
        projector_name=term.name,
        source_term=term.id,
        status=status,
        derived_from_internal_structure=derived,
        rationale=rationale,
        limitations=(
            "This is a projector-channel exclusion scaffold, not the full index theorem.",
            "The full operator must still prove that no opposite-chirality kernel survives outside this channel.",
        ),
    )
