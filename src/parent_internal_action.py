"""Parent Berger-Hopf internal action scaffold for v1.2B.

The objects here are symbolic parent-action records. They are intended to
constrain the existing sector boundary functional, not to claim a complete
unique derivation from the full Berger-Hopf twisted Dirac/bundle action.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ParentReductionStatus(StrEnum):
    """Status levels for parent-action reduction."""

    OPEN = "OPEN"
    ACTION_SCAFFOLD = "ACTION_SCAFFOLD"
    REDUCED_FROM_PARENT_ACTION = "REDUCED_FROM_PARENT_ACTION"
    FULL_ACTION_DERIVED = "FULL_ACTION_DERIVED"


@dataclass(frozen=True)
class ParentActionTerm:
    """One term in the symbolic parent internal action."""

    id: str
    name: str
    expression: str
    contribution: str
    status: ParentReductionStatus
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class InternalBundleField:
    """Symbolic internal bundle field participating in the parent action."""

    id: str
    name: str
    representation_role: str
    boundary_role: str
    status: ParentReductionStatus


@dataclass(frozen=True)
class ProjectionOperator:
    """Symbolic projection operator used in the boundary reduction."""

    id: str
    name: str
    expression: str
    acts_on: str
    contribution: str
    status: ParentReductionStatus


def parent_action_terms() -> tuple[ParentActionTerm, ...]:
    """Return the parent internal-action terms used in v1.2B."""

    scaffold = ParentReductionStatus.ACTION_SCAFFOLD
    reduced = ParentReductionStatus.REDUCED_FROM_PARENT_ACTION
    common_limit = (
        "Symbolic parent-action scaffold only.",
        "Full unique action derivation remains open.",
    )
    return (
        ParentActionTerm(
            id="I_D",
            name="Berger twisted Dirac kinetic term",
            expression=r"\bar\Psi i\slashed D_{\rm Berger}\Psi",
            contribution="parent kinetic operator and mode domain",
            status=scaffold,
            limitations=common_limit,
        ),
        ParentActionTerm(
            id="I_HOPF",
            name="Hopf-fiber connection",
            expression=r"\bar\Psi A_{\rm Hopf}\Psi",
            contribution="hopf_fiber_orientation",
            status=reduced,
            limitations=common_limit,
        ),
        ParentActionTerm(
            id="I_U1",
            name="Higgs-selected U(1) boundary connection",
            expression=r"\bar\Psi A_{\rm Higgs-U(1)}\Psi",
            contribution="hypercharge_higgs_boundary",
            status=reduced,
            limitations=common_limit,
        ),
        ParentActionTerm(
            id="I_BASE",
            name="base S^2 angular connection",
            expression=r"\bar\Psi A_{\rm base}\Psi",
            contribution="base_node_phase",
            status=reduced,
            limitations=common_limit,
        ),
        ParentActionTerm(
            id="I_WEAK",
            name="weak/chirality projector term",
            expression=r"\bar\Psi P_L\Psi",
            contribution="chirality_sign and weak_component_sign",
            status=reduced,
            limitations=common_limit,
        ),
        ParentActionTerm(
            id="I_COF",
            name="coframe triplet projector term",
            expression=r"\bar\Psi P_{\rm cof}\Psi",
            contribution="coframe_participation",
            status=reduced,
            limitations=common_limit,
        ),
        ParentActionTerm(
            id="I_BDY",
            name="sector boundary winding/index term",
            expression=r"S_{\rm boundary}[\Psi,\Phi_0]",
            contribution="family_index and sector_winding_multiplier",
            status=reduced,
            limitations=common_limit,
        ),
    )


def default_internal_bundle_fields() -> tuple[InternalBundleField, ...]:
    """Return symbolic fields in the parent action scaffold."""

    status = ParentReductionStatus.ACTION_SCAFFOLD
    return (
        InternalBundleField(
            id="Psi",
            name="internal twisted spinor",
            representation_role="charged-sector fermion ledger",
            boundary_role="carries Hopf charge q and base node j",
            status=status,
        ),
        InternalBundleField(
            id="Phi0",
            name="Higgs-selected internal profile",
            representation_role="Higgs-selected U(1) direction",
            boundary_role="locks trace/U(1) boundary orientation",
            status=status,
        ),
    )


def default_projection_operators() -> tuple[ProjectionOperator, ...]:
    """Return symbolic projection operators in the parent action scaffold."""

    reduced = ParentReductionStatus.REDUCED_FROM_PARENT_ACTION
    return (
        ProjectionOperator(
            id="P_L",
            name="weak chirality projector",
            expression=r"P_L",
            acts_on="Psi",
            contribution="chirality_sign",
            status=reduced,
        ),
        ProjectionOperator(
            id="P_w",
            name="weak component projector",
            expression=r"P_w",
            acts_on="Psi",
            contribution="weak_component_sign",
            status=reduced,
        ),
        ProjectionOperator(
            id="P_cof",
            name="coframe participation projector",
            expression=r"P_{\rm cof}",
            acts_on="Psi",
            contribution="coframe_participation",
            status=reduced,
        ),
    )


def symbolic_parent_action_expression() -> str:
    """Return the symbolic parent action requested for v1.2B."""

    return (
        "S_int = int_I bar(Psi)(i slash D_Berger + A_Hopf + A_base + "
        "A_Higgs-U(1) + P_L + P_cof)Psi + S_boundary"
    )
