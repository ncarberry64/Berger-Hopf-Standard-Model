"""Reduction rules from parent internal action to boundary functional."""

from __future__ import annotations

from dataclasses import dataclass

from bundle_boundary_conditions import (
    BoundaryCoefficient,
    CoefficientDerivationStatus,
    SectorBoundaryFunctional,
    derive_base_coefficient,
    derive_fiber_coefficient,
    derive_target,
)
from internal_action import sector_boundary_functional_term
from parent_internal_action import ParentActionTerm, ParentReductionStatus, parent_action_terms


@dataclass(frozen=True)
class BoundaryReductionStep:
    """One symbolic parent-action reduction step."""

    id: str
    sector: str
    parent_terms: tuple[str, ...]
    output_factors: tuple[str, ...]
    values: dict[str, int | None]
    status: ParentReductionStatus
    open_reason: str | None
    statement: str


@dataclass(frozen=True)
class ReducedBoundaryFunctional:
    """Boundary functional reduced from a parent action scaffold."""

    sector: str
    parent_action_status: ParentReductionStatus
    functional: SectorBoundaryFunctional
    reduction_steps: tuple[BoundaryReductionStep, ...]
    theorem_complete: bool
    limitations: tuple[str, ...]


def _terms_by_id(terms: tuple[ParentActionTerm, ...]) -> dict[str, ParentActionTerm]:
    return {term.id: term for term in terms}


def _missing_terms(required: tuple[str, ...], available: dict[str, ParentActionTerm]) -> tuple[str, ...]:
    return tuple(term for term in required if term not in available)


def _status_for_missing(missing: tuple[str, ...]) -> ParentReductionStatus:
    return ParentReductionStatus.OPEN if missing else ParentReductionStatus.REDUCED_FROM_PARENT_ACTION


def _open_reason(missing: tuple[str, ...]) -> str | None:
    if not missing:
        return None
    return "missing parent action term(s): " + ", ".join(missing)


def _sector_values(sector: str) -> dict[str, int | str]:
    if sector == "lepton":
        return {
            "hopf_fiber_orientation": -1,
            "base_node_phase": 1,
            "chirality_sign": 1,
            "weak_component_sign": 1,
            "coframe_participation": 2,
            "hypercharge_higgs_boundary": 1,
            "family_index": 3,
            "sector_winding_multiplier": 1,
            "hopf_parity": "odd",
        }
    if sector == "up":
        return {
            "hopf_fiber_orientation": 1,
            "base_node_phase": 1,
            "chirality_sign": -1,
            "weak_component_sign": 1,
            "coframe_participation": 2,
            "hypercharge_higgs_boundary": 1,
            "family_index": 3,
            "sector_winding_multiplier": 2,
            "hopf_parity": "even_q_ge_6",
        }
    if sector == "down":
        return {
            "hopf_fiber_orientation": 1,
            "base_node_phase": 1,
            "chirality_sign": 1,
            "weak_component_sign": 1,
            "coframe_participation": 4,
            "hypercharge_higgs_boundary": 1,
            "family_index": 3,
            "sector_winding_multiplier": 4,
            "hopf_parity": "0_mod_4",
        }
    raise ValueError(f"unknown sector: {sector}")


def reduce_hopf_fiber_contribution(
    sector: str,
    terms: tuple[ParentActionTerm, ...],
) -> BoundaryReductionStep:
    """Reduce Hopf and Higgs-U(1) parent terms to fiber inputs."""

    available = _terms_by_id(terms)
    required = ("I_HOPF", "I_U1")
    missing = _missing_terms(required, available)
    values = _sector_values(sector)
    reduced_values = {
        "hopf_fiber_orientation": None if "I_HOPF" in missing else int(values["hopf_fiber_orientation"]),
        "hypercharge_higgs_boundary": None if "I_U1" in missing else int(values["hypercharge_higgs_boundary"]),
    }
    return BoundaryReductionStep(
        id=f"{sector}.fiber_reduction",
        sector=sector,
        parent_terms=required,
        output_factors=tuple(reduced_values),
        values=reduced_values,
        status=_status_for_missing(missing),
        open_reason=_open_reason(missing),
        statement="Hopf fiber and Higgs-U(1) terms reduce to the q-coefficient inputs.",
    )


def reduce_base_contribution(
    sector: str,
    terms: tuple[ParentActionTerm, ...],
) -> BoundaryReductionStep:
    """Reduce base, weak, and coframe parent terms to base inputs."""

    available = _terms_by_id(terms)
    required = ("I_BASE", "I_WEAK", "I_COF")
    missing = _missing_terms(required, available)
    values = _sector_values(sector)
    reduced_values = {
        "base_node_phase": None if "I_BASE" in missing else int(values["base_node_phase"]),
        "chirality_sign": None if "I_WEAK" in missing else int(values["chirality_sign"]),
        "weak_component_sign": None if "I_WEAK" in missing else int(values["weak_component_sign"]),
        "coframe_participation": None if "I_COF" in missing else int(values["coframe_participation"]),
    }
    return BoundaryReductionStep(
        id=f"{sector}.base_reduction",
        sector=sector,
        parent_terms=required,
        output_factors=tuple(reduced_values),
        values=reduced_values,
        status=_status_for_missing(missing),
        open_reason=_open_reason(missing),
        statement="Base, weak/chirality, and coframe terms reduce to the j-coefficient inputs.",
    )


def reduce_boundary_target_contribution(
    sector: str,
    terms: tuple[ParentActionTerm, ...],
) -> BoundaryReductionStep:
    """Reduce boundary winding/index parent term to target inputs."""

    available = _terms_by_id(terms)
    required = ("I_BDY",)
    missing = _missing_terms(required, available)
    values = _sector_values(sector)
    reduced_values = {
        "family_index": None if "I_BDY" in missing else int(values["family_index"]),
        "sector_winding_multiplier": None if "I_BDY" in missing else int(values["sector_winding_multiplier"]),
    }
    return BoundaryReductionStep(
        id=f"{sector}.target_reduction",
        sector=sector,
        parent_terms=required,
        output_factors=tuple(reduced_values),
        values=reduced_values,
        status=_status_for_missing(missing),
        open_reason=_open_reason(missing),
        statement="Boundary winding/index term reduces to the generation target inputs.",
    )


def reduce_parent_action_to_boundary_functional(
    sector: str,
    terms: tuple[ParentActionTerm, ...] | None = None,
) -> ReducedBoundaryFunctional:
    """Reduce parent action terms to the sector boundary functional."""

    terms = parent_action_terms() if terms is None else terms
    values = _sector_values(sector)
    fiber_step = reduce_hopf_fiber_contribution(sector, terms)
    base_step = reduce_base_contribution(sector, terms)
    target_step = reduce_boundary_target_contribution(sector, terms)
    merged = {
        **fiber_step.values,
        **base_step.values,
        **target_step.values,
        "hopf_parity": str(values["hopf_parity"]),
    }
    status = (
        CoefficientDerivationStatus.DERIVED_FROM_BOUNDARY_FUNCTIONAL
        if all(step.status == ParentReductionStatus.REDUCED_FROM_PARENT_ACTION for step in (fiber_step, base_step, target_step))
        else CoefficientDerivationStatus.OPEN
    )
    functional = SectorBoundaryFunctional(
        sector=sector,
        action_term=sector_boundary_functional_term(sector),
        conditions=(),
        fiber_status=status,
        base_status=status,
        target_status=status,
        **merged,
    )
    parent_status = (
        ParentReductionStatus.REDUCED_FROM_PARENT_ACTION
        if all(step.status == ParentReductionStatus.REDUCED_FROM_PARENT_ACTION for step in (fiber_step, base_step, target_step))
        else ParentReductionStatus.OPEN
    )
    return ReducedBoundaryFunctional(
        sector=sector,
        parent_action_status=parent_status,
        functional=functional,
        reduction_steps=(fiber_step, base_step, target_step),
        theorem_complete=False,
        limitations=(
            "Reduction is symbolic and parent-action scaffold level.",
            "Full unique derivation from the complete Berger-Hopf twisted Dirac/bundle action remains open.",
        ),
    )


def reduced_coefficients(reduction: ReducedBoundaryFunctional) -> dict[str, object]:
    """Return fiber/base/target coefficients after parent-action reduction."""

    coefficients = {
        "fiber_q": derive_fiber_coefficient(reduction.functional),
        "base_j": derive_base_coefficient(reduction.functional),
        "target": derive_target(reduction.functional),
    }
    step_by_name = {
        "fiber_q": reduction.reduction_steps[0],
        "base_j": reduction.reduction_steps[1],
        "target": reduction.reduction_steps[2],
    }
    enriched = {}
    for name, coefficient in coefficients.items():
        step = step_by_name[name]
        if coefficient.value is not None or step.open_reason is None:
            enriched[name] = coefficient
            continue
        enriched[name] = BoundaryCoefficient(
            name=coefficient.name,
            value=None,
            status=coefficient.status,
            source=coefficient.source,
            dependencies=coefficient.dependencies,
            open_reason=f"{coefficient.open_reason}; {step.open_reason}",
        )
    return enriched
