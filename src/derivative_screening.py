"""Derivative-screening scaffold for BHSM scalar/topographic modes."""

from __future__ import annotations

from dataclasses import dataclass


DERIVATIVE_SCREENING_DERIVED = "DERIVATIVE_SCREENING_DERIVED"


@dataclass(frozen=True)
class DerivativeScreeningCondition:
    """One sufficient derivative-screening condition."""

    id: str
    coupling_operator: str
    suppression_scale: float | None
    static_long_range_force_absent: bool
    mode_remains_virtual_or_screened: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def derivative_screening_conditions() -> tuple[DerivativeScreeningCondition, ...]:
    """Return action-level derivative-screening conditions."""

    return (
        DerivativeScreeningCondition(
            id="DS1",
            coupling_operator="L_int ~ (1/M_*) partial_mu phi J^mu_topo",
            suppression_scale=None,
            static_long_range_force_absent=True,
            mode_remains_virtual_or_screened=True,
            status=DERIVATIVE_SCREENING_DERIVED,
            assumptions=(
                "The scalar/topographic mode enters matter channels only through a conserved or slowly varying topographic current.",
                "No unscreened non-derivative phi psi_bar psi term is present for this channel.",
            ),
            limitations=(
                "The exact suppression scale M_* is not fixed by this scaffold.",
                "The full scalar/topographic action must prove absence of direct matter coupling globally.",
            ),
        ),
        DerivativeScreeningCondition(
            id="DS2",
            coupling_operator="static limit: partial_mu phi J^mu_topo -> 0 for zero momentum transfer",
            suppression_scale=None,
            static_long_range_force_absent=True,
            mode_remains_virtual_or_screened=True,
            status=DERIVATIVE_SCREENING_DERIVED,
            assumptions=(
                "The fifth-force test is the static, long-wavelength limit.",
                "Boundary terms do not reintroduce an unscreened scalar charge.",
            ),
            limitations=(
                "This is a sufficient screening condition, not a full theorem.",
            ),
        ),
    )


def derivative_suppression_factor(momentum: float, suppression_scale: float) -> float:
    """Return the derivative-screening proxy (p/M_*)^2."""

    if momentum < 0.0:
        raise ValueError("momentum must be nonnegative")
    if suppression_scale <= 0.0:
        raise ValueError("suppression_scale must be positive")
    return float((momentum / suppression_scale) ** 2)

