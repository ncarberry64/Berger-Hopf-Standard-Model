"""Audit primitive charged-lattice normalization by exact gcd arithmetic."""

from __future__ import annotations

from .common import OMEGA_CH, gcd_all, no_empirical_inputs


def audit_rho_gcd_selection() -> dict[str, object]:
    rho = gcd_all(OMEGA_CH)
    primitive = tuple(value // rho for value in OMEGA_CH)
    return {
        "audit": "rho_ch_gcd_selection",
        "omega_ch": list(OMEGA_CH),
        "rho_ch": rho,
        "primitive_incidence": list(primitive),
        "status": "CONDITIONAL_RHO_CH_PRIMITIVE_LATTICE_CANDIDATE",
        "open_status": "OPEN_MISSING_ACTION_PRIMITIVE_LATTICE_NORMALIZATION_RULE",
        "exact_conditional_identity": rho == 3 and primitive == (1, 2, 4),
        "action_normalization_rule_available": False,
        "action_derived": False,
        "claim_boundary": "rho_ch=3 is the exact gcd conditional on Omega_ch=(3,6,12), not an action-selected Hessian coefficient.",
        **no_empirical_inputs(),
    }
