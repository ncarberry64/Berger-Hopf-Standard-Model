"""Bundle boundary conditions for the v1.2 omega action-origin scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from internal_action import InternalActionTerm, sector_boundary_functional_term


class CoefficientDerivationStatus(StrEnum):
    """Status for a coefficient in the omega action-origin scaffold."""

    ASSUMED = "ASSUMED"
    ACTION_LINKED = "ACTION_LINKED"
    DERIVED_FROM_BOUNDARY_FUNCTIONAL = "DERIVED_FROM_BOUNDARY_FUNCTIONAL"
    OPEN = "OPEN"


@dataclass(frozen=True)
class BoundaryCondition:
    """One symbolic boundary condition feeding a sector functional."""

    id: str
    sector: str
    source_term: str
    factor_name: str
    factor_value: int
    status: CoefficientDerivationStatus
    statement: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class BoundaryCoefficient:
    """Derived coefficient plus dependency/status metadata."""

    name: str
    value: int | None
    status: CoefficientDerivationStatus
    source: str
    dependencies: tuple[str, ...]
    open_reason: str | None = None


@dataclass(frozen=True)
class SectorBoundaryFunctional:
    """Action-like sector boundary functional for one charged sector."""

    sector: str
    action_term: InternalActionTerm
    conditions: tuple[BoundaryCondition, ...]
    hopf_fiber_orientation: int | None
    base_node_phase: int | None
    chirality_sign: int | None
    weak_component_sign: int | None
    coframe_participation: int | None
    hypercharge_higgs_boundary: int | None
    family_index: int | None
    sector_winding_multiplier: int | None
    hopf_parity: str
    fiber_status: CoefficientDerivationStatus
    base_status: CoefficientDerivationStatus
    target_status: CoefficientDerivationStatus

    @property
    def fiber_coefficient(self) -> int:
        """Return the coefficient multiplying Hopf charge q."""

        coefficient = derive_fiber_coefficient(self)
        if coefficient.value is None:
            raise ValueError(coefficient.open_reason)
        return coefficient.value

    @property
    def base_coefficient(self) -> int:
        """Return the coefficient multiplying the base node j."""

        coefficient = derive_base_coefficient(self)
        if coefficient.value is None:
            raise ValueError(coefficient.open_reason)
        return coefficient.value

    @property
    def target(self) -> int:
        """Return the generation/winding target."""

        coefficient = derive_target(self)
        if coefficient.value is None:
            raise ValueError(coefficient.open_reason)
        return coefficient.value


def _missing_factor_reason(factors: dict[str, int | None]) -> str | None:
    missing = [name for name, value in factors.items() if value is None]
    if not missing:
        return None
    return "missing boundary-functional input(s): " + ", ".join(missing)


def derive_fiber_coefficient(functional: SectorBoundaryFunctional) -> BoundaryCoefficient:
    """Derive the Hopf-fiber coefficient from functional inputs."""

    factors = {
        "hopf_fiber_orientation": functional.hopf_fiber_orientation,
        "hypercharge_higgs_boundary": functional.hypercharge_higgs_boundary,
    }
    open_reason = _missing_factor_reason(factors)
    source = "hopf_fiber_orientation * hypercharge_higgs_boundary"
    if open_reason is not None:
        return BoundaryCoefficient(
            name="fiber_q",
            value=None,
            status=CoefficientDerivationStatus.OPEN,
            source=source,
            dependencies=("I_HOPF", "I_U1"),
            open_reason=open_reason,
        )
    return BoundaryCoefficient(
        name="fiber_q",
        value=int(functional.hopf_fiber_orientation * functional.hypercharge_higgs_boundary),
        status=functional.fiber_status,
        source=source,
        dependencies=("I_HOPF", "I_U1"),
    )


def derive_base_coefficient(functional: SectorBoundaryFunctional) -> BoundaryCoefficient:
    """Derive the base-node coefficient from functional inputs."""

    factors = {
        "base_node_phase": functional.base_node_phase,
        "chirality_sign": functional.chirality_sign,
        "weak_component_sign": functional.weak_component_sign,
        "coframe_participation": functional.coframe_participation,
    }
    open_reason = _missing_factor_reason(factors)
    source = "base_node_phase * chirality_sign * weak_component_sign * coframe_participation"
    if open_reason is not None:
        return BoundaryCoefficient(
            name="base_j",
            value=None,
            status=CoefficientDerivationStatus.OPEN,
            source=source,
            dependencies=("I_BASE", "I_WEAK", "I_COF"),
            open_reason=open_reason,
        )
    return BoundaryCoefficient(
        name="base_j",
        value=int(
            functional.base_node_phase
            * functional.chirality_sign
            * functional.weak_component_sign
            * functional.coframe_participation
        ),
        status=functional.base_status,
        source=source,
        dependencies=("I_BASE", "I_WEAK", "I_COF"),
    )


def derive_target(functional: SectorBoundaryFunctional) -> BoundaryCoefficient:
    """Derive the boundary target from generation and sector winding."""

    factors = {
        "family_index": functional.family_index,
        "sector_winding_multiplier": functional.sector_winding_multiplier,
    }
    open_reason = _missing_factor_reason(factors)
    source = "family_index * sector_winding_multiplier"
    if open_reason is not None:
        return BoundaryCoefficient(
            name="target",
            value=None,
            status=CoefficientDerivationStatus.OPEN,
            source=source,
            dependencies=("I_BDY",),
            open_reason=open_reason,
        )
    return BoundaryCoefficient(
        name="target",
        value=int(functional.family_index * functional.sector_winding_multiplier),
        status=functional.target_status,
        source=source,
        dependencies=("I_BDY",),
    )


def derived_coefficients(functional: SectorBoundaryFunctional) -> tuple[BoundaryCoefficient, ...]:
    """Return all derived coefficients for a sector boundary functional."""

    return (
        derive_fiber_coefficient(functional),
        derive_base_coefficient(functional),
        derive_target(functional),
    )


def _condition(
    sector: str,
    source_term: str,
    factor_name: str,
    factor_value: int,
    status: CoefficientDerivationStatus,
    statement: str,
) -> BoundaryCondition:
    return BoundaryCondition(
        id=f"{sector}.{factor_name}",
        sector=sector,
        source_term=source_term,
        factor_name=factor_name,
        factor_value=factor_value,
        status=status,
        statement=statement,
        limitations=(
            "Boundary condition is symbolic/action-origin scaffold data.",
            "Full derivation from variation of the internal bundle action remains open.",
        ),
    )


def sector_boundary_functional(sector: str) -> SectorBoundaryFunctional:
    """Return the v1.2 action-origin boundary functional for a sector."""

    n_gen = 3
    derived = CoefficientDerivationStatus.DERIVED_FROM_BOUNDARY_FUNCTIONAL
    linked = CoefficientDerivationStatus.ACTION_LINKED

    if sector == "lepton":
        values = {
            "hopf_fiber_orientation": -1,
            "base_node_phase": 1,
            "chirality_sign": 1,
            "weak_component_sign": 1,
            "coframe_participation": 2,
            "hypercharge_higgs_boundary": 1,
            "sector_winding_multiplier": 1,
            "hopf_parity": "odd",
        }
    elif sector == "up":
        values = {
            "hopf_fiber_orientation": 1,
            "base_node_phase": 1,
            "chirality_sign": -1,
            "weak_component_sign": 1,
            "coframe_participation": 2,
            "hypercharge_higgs_boundary": 1,
            "sector_winding_multiplier": 2,
            "hopf_parity": "even_q_ge_6",
        }
    elif sector == "down":
        values = {
            "hopf_fiber_orientation": 1,
            "base_node_phase": 1,
            "chirality_sign": 1,
            "weak_component_sign": 1,
            "coframe_participation": 4,
            "hypercharge_higgs_boundary": 1,
            "sector_winding_multiplier": 4,
            "hopf_parity": "0_mod_4",
        }
    else:
        raise ValueError(f"unknown sector: {sector}")

    conditions = (
        _condition(
            sector,
            "I_HOPF",
            "hopf_fiber_orientation",
            values["hopf_fiber_orientation"],
            derived,
            "Hopf-fiber phase orientation supplies the q coefficient sign.",
        ),
        _condition(
            sector,
            "I_BASE",
            "base_node_phase",
            values["base_node_phase"],
            derived,
            "Base S^2 node phase supplies one j-node unit.",
        ),
        _condition(
            sector,
            "I_WEAK",
            "chirality_sign",
            values["chirality_sign"],
            derived,
            "Weak chirality fixes the base-phase sign.",
        ),
        _condition(
            sector,
            "I_WEAK",
            "weak_component_sign",
            values["weak_component_sign"],
            derived,
            "Weak component fixes the component boundary sign.",
        ),
        _condition(
            sector,
            "I_COF",
            "coframe_participation",
            values["coframe_participation"],
            linked,
            "Coframe participation sets the base multiplicity.",
        ),
        _condition(
            sector,
            "I_U1",
            "hypercharge_higgs_boundary",
            values["hypercharge_higgs_boundary"],
            linked,
            "Higgs-selected U(1) boundary phase preserves the charged-sector orientation.",
        ),
        _condition(
            sector,
            "I_BDY",
            "sector_winding_multiplier",
            values["sector_winding_multiplier"],
            linked,
            "Sector winding multiplier combines with N_gen to give the target.",
        ),
    )
    return SectorBoundaryFunctional(
        sector=sector,
        action_term=sector_boundary_functional_term(sector),
        conditions=conditions,
        family_index=n_gen,
        fiber_status=derived,
        base_status=derived,
        target_status=derived,
        **values,
    )


def default_sector_boundary_functionals() -> dict[str, SectorBoundaryFunctional]:
    """Return all charged-sector boundary functionals."""

    return {sector: sector_boundary_functional(sector) for sector in ("lepton", "up", "down")}
