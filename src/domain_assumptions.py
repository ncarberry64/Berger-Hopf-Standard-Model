"""Infinite-basis assumptions for the BHSM v1.3E sector-bound scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from spectral_bounds import required_dirac_lower_bound
from spectral_gap import MU_H, natural_lambda2


ASSUMPTION_STATUSES = (
    "ASSUMED_FOR_THEOREM_SCAFFOLD",
    "SUPPORTED_BY_FINITE_EVIDENCE",
    "OPEN",
)


@dataclass(frozen=True)
class InfiniteBasisAssumption:
    """One explicit assumption for an infinite-basis relative-bound theorem."""

    id: str
    statement: str
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


def candidate_a_k_max() -> float:
    """Return the conservative v1.3E assumption candidate for a_K."""

    return 0.04


def candidate_diagonal_lower_bound() -> float:
    """Return the scaffold candidate for the diagonal complement lower bound d0."""

    return 1.4641


def candidate_required_dirac_lower_bound() -> float:
    """Return the natural-cutoff required Dirac lower bound."""

    return required_dirac_lower_bound(natural_lambda2(), MU_H)


def candidate_structured_margin(a_k_max: float | None = None, d0: float | None = None) -> dict[str, float | bool]:
    """Evaluate the v1.3E conservative relative-bound candidate margin."""

    resolved_a = candidate_a_k_max() if a_k_max is None else float(a_k_max)
    resolved_d0 = candidate_diagonal_lower_bound() if d0 is None else float(d0)
    required = candidate_required_dirac_lower_bound()
    lower = (1.0 - resolved_a) * resolved_d0
    return {
        "a_k_max": resolved_a,
        "b_k": 0.0,
        "d0_candidate": resolved_d0,
        "required_dirac_lower_bound": required,
        "candidate_structured_lower_bound": lower,
        "margin": lower - required,
        "passes": bool(lower >= required),
    }


def build_infinite_basis_assumptions(a_k_max: float | None = None) -> tuple[InfiniteBasisAssumption, ...]:
    """Return assumptions A1-A6 for the sector-coupling theorem scaffold."""

    margin = candidate_structured_margin(a_k_max=a_k_max)
    return (
        InfiniteBasisAssumption(
            id="A1",
            statement="K_sector preserves (k,j,q,chi) and only mixes charged-sector labels.",
            status="SUPPORTED_BY_FINITE_EVIDENCE",
            evidence=(
                "v1.3C selection-rule audit found preservation of k, j, q, and chirality in every nonzero Dirac-level coupling.",
            ),
            limitations=("This structure is read from DIRAC_PROXY_LEVEL_2 and has not been derived for the full operator.",),
        ),
        InfiniteBasisAssumption(
            id="A2",
            statement="K_sector has uniformly bounded mode-block bandwidth in the (k,j,chi,sector) ordering.",
            status="SUPPORTED_BY_FINITE_EVIDENCE",
            evidence=(
                "v1.3D finite scans through k_max=32 found mode-block bandwidth = 2.",
            ),
            limitations=("A finite ladder does not prove an infinite-basis bandwidth theorem.",),
        ),
        InfiniteBasisAssumption(
            id="A3",
            statement=(
                f"K_sector is D0^2-relative bounded on H_perp with "
                f"a_K <= {margin['a_k_max']} and b_K = 0."
            ),
            status="ASSUMED_FOR_THEOREM_SCAFFOLD",
            evidence=(
                "v1.3D observed max finite a_K = 0.03095889839310559 with all b_K = 0.",
                f"v1.3E uses conservative candidate a_K^max = {margin['a_k_max']} as an assumption, not a fit.",
            ),
            limitations=("The uniform infinite-basis relative bound is not proven here.",),
        ),
        InfiniteBasisAssumption(
            id="A4",
            statement="K_sector vanishes on the protected zero-mode subspace.",
            status="SUPPORTED_BY_FINITE_EVIDENCE",
            evidence=(
                "v1.3C found the Dirac-level and squared sector perturbation blocks vanish on the protected coordinate block.",
            ),
            limitations=("The protected zero-mode subspace itself remains a scaffold until the full kernel is proven.",),
        ),
        InfiniteBasisAssumption(
            id="A5",
            statement="The complement projection P_perp is well-defined and commutes with the relevant mode-block decomposition.",
            status="OPEN",
            evidence=(
                "Finite matrices use an explicit protected-complement projection.",
            ),
            limitations=("The infinite-dimensional complement projector compatibility is an open domain assumption.",),
        ),
        InfiniteBasisAssumption(
            id="A6",
            statement=(
                "The diagonal complement lower bound d0 satisfies "
                "d0 >= d_required/(1-a_K^max), equivalently "
                f"(1-a_K^max)d0 = {margin['candidate_structured_lower_bound']} "
                f">= d_required = {margin['required_dirac_lower_bound']}."
            ),
            status="ASSUMED_FOR_THEOREM_SCAFFOLD",
            evidence=(
                "v1.3D found stable finite-basis lower bound about 1.4630400253.",
                f"v1.3E candidate d0 = {margin['d0_candidate']} gives margin {margin['margin']}.",
            ),
            limitations=("The infinite-basis diagonal complement lower bound is not proven here.",),
        ),
    )
