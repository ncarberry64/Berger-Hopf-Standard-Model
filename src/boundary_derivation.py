"""Gate 25C symbolic scaffold for boundary-operator derivation.

The operators in this module are operational symbolic maps. They are not
claimed to be derived from the full twisted Dirac or bundle action.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from mode_selection import omega_down, omega_lepton, omega_up


class DerivationStatus(StrEnum):
    """Status of a boundary-operator derivation."""

    OPERATIONAL = "OPERATIONAL"
    ACTION_LINKED = "ACTION_LINKED"
    ACTION_DERIVED = "ACTION_DERIVED"
    OPEN = "OPEN"


@dataclass(frozen=True)
class RepresentationBoundary:
    """Representation data and operational boundary coefficients."""

    sector: str
    color_rank: int
    weak_component: str
    hypercharge_numerator: int
    hypercharge_denominator: int
    family_index: int
    hopf_parity: str
    base_weight: int
    fiber_weight: int
    target: int
    derivation_status: DerivationStatus = DerivationStatus.ACTION_LINKED


@dataclass(frozen=True)
class BoundaryPhaseContributions:
    """Symbolic phase factors linking representation data to coefficients."""

    hopf_fiber_phase: int
    base_node_phase: int
    chirality_sign: int
    weak_component_sign: int
    coframe_factor: int
    family_index: int
    hypercharge_factor: int
    sector_winding_multiplier: int


def default_boundaries() -> dict[str, RepresentationBoundary]:
    """Return the supplied Gate 25C operational boundary records."""

    n_gen = 3
    return {
        "lepton": RepresentationBoundary(
            sector="lepton",
            color_rank=1,
            weak_component="lower",
            hypercharge_numerator=-1,
            hypercharge_denominator=2,
            family_index=n_gen,
            hopf_parity="odd",
            base_weight=2,
            fiber_weight=-1,
            target=n_gen,
        ),
        "up": RepresentationBoundary(
            sector="up",
            color_rank=3,
            weak_component="upper",
            hypercharge_numerator=1,
            hypercharge_denominator=6,
            family_index=n_gen,
            hopf_parity="even_q_ge_6",
            base_weight=-2,
            fiber_weight=1,
            target=2 * n_gen,
        ),
        "down": RepresentationBoundary(
            sector="down",
            color_rank=3,
            weak_component="lower",
            hypercharge_numerator=1,
            hypercharge_denominator=6,
            family_index=n_gen,
            hopf_parity="0_mod_4",
            base_weight=4,
            fiber_weight=1,
            target=4 * n_gen,
        ),
    }


def _boundary_for(boundary: RepresentationBoundary | str) -> RepresentationBoundary:
    if isinstance(boundary, RepresentationBoundary):
        return boundary
    boundaries = default_boundaries()
    if boundary not in boundaries:
        raise ValueError(f"unknown boundary sector: {boundary}")
    return boundaries[boundary]


def phase_contributions_for_sector(sector: str) -> BoundaryPhaseContributions:
    """Return symbolic phase factors for a charged sector."""

    if sector == "lepton":
        return BoundaryPhaseContributions(
            hopf_fiber_phase=-1,
            base_node_phase=1,
            chirality_sign=1,
            weak_component_sign=1,
            coframe_factor=2,
            family_index=3,
            hypercharge_factor=-1,
            sector_winding_multiplier=1,
        )
    if sector == "up":
        return BoundaryPhaseContributions(
            hopf_fiber_phase=1,
            base_node_phase=1,
            chirality_sign=-1,
            weak_component_sign=1,
            coframe_factor=2,
            family_index=3,
            hypercharge_factor=1,
            sector_winding_multiplier=2,
        )
    if sector == "down":
        return BoundaryPhaseContributions(
            hopf_fiber_phase=1,
            base_node_phase=1,
            chirality_sign=1,
            weak_component_sign=1,
            coframe_factor=4,
            family_index=3,
            hypercharge_factor=1,
            sector_winding_multiplier=4,
        )
    raise ValueError(f"unknown boundary sector: {sector}")


def coefficients_from_phase_contributions(contribs: BoundaryPhaseContributions) -> tuple[int, int]:
    """Return ``(fiber coefficient on q, base coefficient on j)``."""

    fiber = contribs.hopf_fiber_phase
    base = contribs.base_node_phase * contribs.weak_component_sign * contribs.chirality_sign * contribs.coframe_factor
    return fiber, base


def target_from_phase_contributions(contribs: BoundaryPhaseContributions) -> int:
    """Return target = family index times sector winding multiplier."""

    return contribs.family_index * contribs.sector_winding_multiplier


def derive_omega_from_phases(sector: str) -> RepresentationBoundary:
    """Build an ACTION_LINKED boundary from symbolic phase contributions."""

    existing = _boundary_for(sector)
    contribs = phase_contributions_for_sector(sector)
    fiber, base = coefficients_from_phase_contributions(contribs)
    target = target_from_phase_contributions(contribs)
    return RepresentationBoundary(
        sector=existing.sector,
        color_rank=existing.color_rank,
        weak_component=existing.weak_component,
        hypercharge_numerator=existing.hypercharge_numerator,
        hypercharge_denominator=existing.hypercharge_denominator,
        family_index=existing.family_index,
        hopf_parity=existing.hopf_parity,
        base_weight=base,
        fiber_weight=fiber,
        target=target,
        derivation_status=DerivationStatus.ACTION_LINKED,
    )


def action_link_report(sector: str) -> dict[str, object]:
    """Return a symbolic action-link report without claiming action derivation."""

    contribs = phase_contributions_for_sector(sector)
    boundary = derive_omega_from_phases(sector)
    return {
        "sector": sector,
        "phase_contributions": {
            "hopf_fiber_phase": contribs.hopf_fiber_phase,
            "base_node_phase": contribs.base_node_phase,
            "chirality_sign": contribs.chirality_sign,
            "weak_component_sign": contribs.weak_component_sign,
            "coframe_factor": contribs.coframe_factor,
            "family_index": contribs.family_index,
            "hypercharge_factor": contribs.hypercharge_factor,
            "sector_winding_multiplier": contribs.sector_winding_multiplier,
        },
        "coefficients": derive_boundary_coefficients(boundary),
        "equation": boundary_equation(boundary),
        "derivation_status": boundary.derivation_status.value,
        "action_derived": False,
        "limitation": (
            "ACTION_LINKED symbolic phase rule only; not obtained from variation "
            "or spectrum of the full twisted Dirac/bundle action."
        ),
    }


def omega_from_boundary(k: int, j: int, boundary: RepresentationBoundary) -> int:
    """Evaluate the symbolic operational map ``fiber*q + base*j``."""

    q = k - 2 * j
    return boundary.fiber_weight * q + boundary.base_weight * j


def boundary_equation(boundary: RepresentationBoundary) -> str:
    """Return a manuscript-readable symbolic boundary equation."""

    fiber = f"{boundary.fiber_weight} q"
    base = f"{boundary.base_weight} j"
    return f"Omega_{boundary.sector} = {fiber} + {base} = {boundary.target}"


def derive_boundary_coefficients(boundary: RepresentationBoundary) -> dict[str, int | str]:
    """Return the operational coefficients and their status.

    This function records the current coefficient map; it does not derive the
    coefficients from the full action.
    """

    return {
        "sector": boundary.sector,
        "fiber_coefficient_on_q": boundary.fiber_weight,
        "base_coefficient_on_j": boundary.base_weight,
        "target": boundary.target,
        "derivation_status": boundary.derivation_status.value,
    }


def explain_boundary(boundary: RepresentationBoundary) -> str:
    """Explain the operational scaffold and the remaining derivation gap."""

    return (
        f"{boundary.sector}: representation data "
        f"(color_rank={boundary.color_rank}, weak_component={boundary.weak_component}, "
        f"Y={boundary.hypercharge_numerator}/{boundary.hypercharge_denominator}, "
        f"N_gen={boundary.family_index}, hopf_parity={boundary.hopf_parity}) "
        f"are assigned to the operational equation {boundary_equation(boundary)}. "
        "The remaining open task is to derive the fiber/base coefficients from "
        "chirality, weak component, coframe triplet, and Hopf/base boundary phases "
        "in the twisted Dirac/bundle action."
    )


def compare_to_operational_omega(sector: str) -> dict[str, object]:
    """Compare symbolic scaffold coefficients to Gate 25B operational functions."""

    boundary = _boundary_for(sector)
    sample_modes = {
        "lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    operational = {
        "lepton": omega_lepton,
        "up": omega_up,
        "down": omega_down,
    }
    comparisons = []
    for mode in sample_modes[sector]:
        symbolic = omega_from_boundary(*mode, boundary)
        direct = operational[sector](*mode)
        comparisons.append(
            {
                "mode": mode,
                "symbolic": symbolic,
                "operational": direct,
                "matches": symbolic == direct,
            }
        )
    return {
        "sector": sector,
        "coefficients": derive_boundary_coefficients(boundary),
        "equation": boundary_equation(boundary),
        "matches_operational": all(row["matches"] for row in comparisons),
        "comparisons": comparisons,
    }
