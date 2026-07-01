"""Verify the exact conditional charged bridge and beta identities."""

from __future__ import annotations

from fractions import Fraction

from .common import OMEGA_CH, SECTORS, fraction_text, gcd_all, no_empirical_inputs


def audit_bridge_beta_identity() -> dict[str, object]:
    rho = gcd_all(OMEGA_CH)
    primitive = tuple(value // rho for value in OMEGA_CH)
    primitive_total = sum(primitive)
    incidence_trace = sum(OMEGA_CH)
    projectors = tuple(Fraction(value, primitive_total) for value in primitive)
    overlap = Fraction(max(primitive), rho)
    n16 = max(primitive) ** 2
    bridge = overlap**2 / incidence_trace
    betas = tuple(bridge * projector for projector in projectors)
    return {
        "audit": "bridge_beta_identity",
        "incidence_trace": incidence_trace,
        "overlap": fraction_text(overlap),
        "N_16": n16,
        "g_bridge": fraction_text(bridge),
        "projectors": {sector: fraction_text(value) for sector, value in zip(SECTORS, projectors)},
        "betas": {sector: fraction_text(value) for sector, value in zip(SECTORS, betas)},
        "status": "EXACT_CONDITIONAL_BRIDGE_BETA_IDENTITIES",
        "all_exact_identities_pass": bridge == Fraction(16, 189) and betas == (Fraction(16, 1323), Fraction(32, 1323), Fraction(64, 1323)),
        "action_derived": False,
        "claim_boundary": "Bridge and beta arithmetic is exact conditional on the primitive-lattice and maximal-overlap candidates.",
        **no_empirical_inputs(),
    }
