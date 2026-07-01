"""Derive normalized primitive projector weights conditionally on Omega_ch."""

from __future__ import annotations

from fractions import Fraction

from .common import OMEGA_CH, SECTORS, fraction_text, gcd_all, no_empirical_inputs


def audit_projector_reduction() -> dict[str, object]:
    rho = gcd_all(OMEGA_CH)
    primitive = tuple(value // rho for value in OMEGA_CH)
    total = sum(primitive)
    projectors = tuple(Fraction(value, total) for value in primitive)
    return {
        "audit": "projector_reduction",
        "primitive_incidence": list(primitive),
        "primitive_trace": total,
        "projectors": {sector: fraction_text(value) for sector, value in zip(SECTORS, projectors)},
        "status": "EXACT_CONDITIONAL_PROJECTOR_REDUCTION",
        "projector_sum": fraction_text(sum(projectors, Fraction(0))),
        "action_derived": False,
        "claim_boundary": "The projector fractions follow exactly from normalized primitive incidence conditional on Omega_ch.",
        **no_empirical_inputs(),
    }
