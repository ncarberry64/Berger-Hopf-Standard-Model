"""Audit the conditional maximal primitive overlap 4/3."""

from __future__ import annotations

from fractions import Fraction

from .common import OMEGA_CH, fraction_text, gcd_all, no_empirical_inputs


def audit_overlap_4_over_3() -> dict[str, object]:
    rho = gcd_all(OMEGA_CH)
    primitive = tuple(value // rho for value in OMEGA_CH)
    overlap = Fraction(max(primitive), rho)
    return {
        "audit": "charged_overlap_4_over_3_source",
        "rho_ch": rho,
        "max_primitive_incidence": max(primitive),
        "overlap": fraction_text(overlap),
        "status": "CONDITIONAL_CHARGED_OVERLAP_4_OVER_3_SOURCE_CANDIDATE",
        "open_status": "OPEN_MISSING_ACTION_RULE_THAT_BRIDGE_USES_MAX_PRIMITIVE_OVERLAP",
        "exact_conditional_identity": overlap == Fraction(4, 3),
        "maximal_overlap_action_rule_available": False,
        "action_derived": False,
        "claim_boundary": "The value 4/3 equals s_d/rho_ch conditionally; no action rule yet requires the bridge to use it.",
        **no_empirical_inputs(),
    }
