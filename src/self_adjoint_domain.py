"""Self-adjoint domain scaffold for the full BHSM operator.

This module records the domain assumptions needed for a full operator theorem.
It deliberately does not promote finite-matrix Hermiticity to an infinite-basis
self-adjointness proof.
"""

from __future__ import annotations

from dataclasses import dataclass


SELF_ADJOINT_DOMAIN_PROVEN = "SELF_ADJOINT_DOMAIN_PROVEN"
SELF_ADJOINT_DOMAIN_CANDIDATE = "SELF_ADJOINT_DOMAIN_CANDIDATE"
SELF_ADJOINT_DOMAIN_CONDITIONAL = "SELF_ADJOINT_DOMAIN_CONDITIONAL"
SELF_ADJOINT_DOMAIN_OPEN = "SELF_ADJOINT_DOMAIN_OPEN"
FAILS_DOMAIN_CHECK = "FAILS_DOMAIN_CHECK"


@dataclass(frozen=True)
class DomainAssumption:
    """One domain assumption for the complete operator."""

    id: str
    statement: str
    status: str
    evidence: tuple[str, ...]
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class SelfAdjointDomainReport:
    """Self-adjointness status for the full operator domain."""

    operator_name: str
    domain_symbol: str
    assumptions: tuple[DomainAssumption, ...]
    finite_matrix_hermitian: bool
    theorem_complete: bool
    status: str
    limitations: tuple[str, ...]


def domain_assumptions() -> tuple[DomainAssumption, ...]:
    """Return the explicit domain assumptions."""

    return (
        DomainAssumption(
            id="dense_core",
            statement="The finite-support Berger-Hopf mode span is a dense core.",
            status=SELF_ADJOINT_DOMAIN_CANDIDATE,
            evidence=("finite truncations define symmetric matrices",),
            open_obligations=("prove density and core stability in the complete Hilbert space",),
        ),
        DomainAssumption(
            id="diag_self_adjoint",
            statement="The diagonal Berger/twisted Dirac square is self-adjoint on the chosen core.",
            status=SELF_ADJOINT_DOMAIN_CANDIDATE,
            evidence=("diagonal eigenvalue scaffold is real and bounded below",),
            open_obligations=("derive the complete Berger twisted Dirac spectral domain",),
        ),
        DomainAssumption(
            id="perturbation_control",
            statement="Hopf, boundary, chirality, sector-coupling, and profile terms preserve the domain.",
            status=SELF_ADJOINT_DOMAIN_OPEN,
            evidence=("finite and semi-analytic relative-bound audits pass current scaffolds",),
            open_obligations=(
                "prove self-adjointness via Kato-Rellich or equivalent relative-bound conditions in the complete operator",
            ),
        ),
        DomainAssumption(
            id="projector_stability",
            statement="The formal-kernel projector and complement projector commute with the required block split.",
            status=SELF_ADJOINT_DOMAIN_OPEN,
            evidence=("corrected formal-kernel finite projector identities pass",),
            open_obligations=("prove the formal kernel/complement split for the complete Hilbert-space operator",),
        ),
    )


def build_self_adjoint_domain_report() -> SelfAdjointDomainReport:
    """Build the conservative self-adjoint domain report."""

    assumptions = domain_assumptions()
    theorem_complete = all(item.status == SELF_ADJOINT_DOMAIN_PROVEN for item in assumptions)
    status = SELF_ADJOINT_DOMAIN_PROVEN if theorem_complete else SELF_ADJOINT_DOMAIN_OPEN
    return SelfAdjointDomainReport(
        operator_name="D_FK^2 + heat lift + PSD profile terms",
        domain_symbol="D_full = closure of finite-support Berger-Hopf spinor modes subject to formal-kernel boundary conditions",
        assumptions=assumptions,
        finite_matrix_hermitian=True,
        theorem_complete=theorem_complete,
        status=status,
        limitations=(
            "Finite-matrix Hermiticity is not an infinite-basis self-adjointness theorem.",
            "Domain preservation by all perturbations remains an explicit open obligation.",
        ),
    )
