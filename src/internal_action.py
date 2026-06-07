"""Symbolic Berger-Hopf internal action terms for the v1.2 omega program.

These objects are a derivation scaffold. They encode the action-like terms and
boundary sources used by the omega derivation audit, but they do not claim a
completed variation or spectral derivation from the full internal action.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InternalActionTerm:
    """One symbolic term in the Berger-Hopf internal action scaffold."""

    id: str
    name: str
    expression: str
    role: str
    source_factor: str
    status: str
    limitations: tuple[str, ...]


def internal_dirac_kinetic_term() -> InternalActionTerm:
    """Return the symbolic internal Dirac kinetic term."""

    return InternalActionTerm(
        id="I_D",
        name="internal Dirac kinetic term",
        expression=r"\bar\Psi i\widehat D_I \Psi",
        role="supplies the internal mode operator before sector boundary projection",
        source_factor="twisted_dirac_operator",
        status="ACTION_LINKED",
        limitations=("Full twisted Dirac spectrum remains open.",),
    )


def hopf_fiber_covariant_derivative() -> InternalActionTerm:
    """Return the Hopf-fiber covariant derivative source term."""

    return InternalActionTerm(
        id="I_HOPF",
        name="Hopf-fiber covariant derivative",
        expression=r"\bar\Psi \gamma^\chi D_\psi \Psi",
        role="couples boundary phase orientation to Hopf charge q",
        source_factor="hopf_fiber_phase",
        status="DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        limitations=("The fiber orientation is derived inside the finite symbolic boundary functional.",),
    )


def base_angular_derivative() -> InternalActionTerm:
    """Return the base S^2 angular derivative source term."""

    return InternalActionTerm(
        id="I_BASE",
        name="base S^2 angular derivative",
        expression=r"\bar\Psi \gamma^\theta D_\theta \Psi+\bar\Psi \gamma^\phi D_\phi \Psi",
        role="couples weak/base boundary phase to the j node count",
        source_factor="base_node_phase",
        status="DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        limitations=("The base coefficient is derived inside the symbolic boundary functional.",),
    )


def higgs_u1_boundary_phase() -> InternalActionTerm:
    """Return the Higgs-selected U(1) boundary phase source term."""

    return InternalActionTerm(
        id="I_U1",
        name="Higgs-selected U(1) boundary phase",
        expression=r"\Phi_0^\dagger D_{\rm tr} \Phi_0",
        role="locks the admissible trace/U(1) boundary phase for each charged sector",
        source_factor="hypercharge_higgs_boundary",
        status="ACTION_LINKED",
        limitations=("Trace U(1) topological/nondynamical condition remains an assumption.",),
    )


def weak_doublet_chirality_projector() -> InternalActionTerm:
    """Return the weak-doublet chirality projector source term."""

    return InternalActionTerm(
        id="I_WEAK",
        name="weak-doublet chirality projector",
        expression=r"P_{\chi,w}\Psi",
        role="sets the weak-component and chirality sign in the base boundary factor",
        source_factor="chirality_weak_component",
        status="DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        limitations=("The projector algebra is symbolic and finite-sector only.",),
    )


def quark_coframe_triplet_projector() -> InternalActionTerm:
    """Return the quark coframe triplet participation source term."""

    return InternalActionTerm(
        id="I_COF",
        name="quark coframe triplet projector",
        expression=r"P_{\rm cof}^{(3)}\Psi",
        role="records coframe multiplicity in quark-sector boundary winding",
        source_factor="coframe_triplet_participation",
        status="ACTION_LINKED",
        limitations=("Full coframe coupling from the bundle action remains open.",),
    )


def sector_boundary_functional_term(sector: str) -> InternalActionTerm:
    """Return the sector-specific boundary functional term."""

    if sector not in {"lepton", "up", "down"}:
        raise ValueError(f"unknown sector: {sector}")
    return InternalActionTerm(
        id=f"I_BDY_{sector}",
        name=f"{sector} sector boundary functional",
        expression=rf"\mathcal B_{{{sector}}}[\Psi,\Phi_0]",
        role="combines Hopf, base, weak, coframe, U(1), and generation factors",
        source_factor="sector_boundary_functional",
        status="DERIVED_FROM_BOUNDARY_FUNCTIONAL",
        limitations=("This is not yet obtained by varying the full internal action.",),
    )


def default_internal_action_terms() -> tuple[InternalActionTerm, ...]:
    """Return the common symbolic action terms used in the omega scaffold."""

    return (
        internal_dirac_kinetic_term(),
        hopf_fiber_covariant_derivative(),
        base_angular_derivative(),
        higgs_u1_boundary_phase(),
        weak_doublet_chirality_projector(),
        quark_coframe_triplet_projector(),
    )
