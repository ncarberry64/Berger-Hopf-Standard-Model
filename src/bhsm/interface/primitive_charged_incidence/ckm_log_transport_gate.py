"""Fail-closed gate for the candidate reciprocal N_16 CKM transport exponent."""

from __future__ import annotations

from fractions import Fraction

from .common import fraction_text, no_empirical_inputs


def audit_ckm_log_transport() -> dict[str, object]:
    n16 = 16
    exponent = Fraction(1, n16)
    return {
        "audit": "ckm_log_transport_gate",
        "N_16": n16,
        "candidate_exponent": fraction_text(exponent),
        "status": "CONDITIONAL_CKM_LOG_TRANSPORT_CANDIDATE",
        "open_status": "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
        "reciprocal_identity_exact": exponent == Fraction(1, 16),
        "log_transport_averaging_theorem_available": False,
        "ckm_exponent_derived": False,
        "claim_boundary": "The reciprocal 1/16 is exact arithmetic; the CKM logarithmic transport averaging theorem remains open.",
        **no_empirical_inputs(),
    }
