"""Compute one-way, bidirectional, self-response, and total dimensions."""

from __future__ import annotations

from fractions import Fraction

from .common import channel_dimensions, input_guard


def audit_bidirectional_channel_count() -> dict[str, object]:
    counts = channel_dimensions()
    return {
        "audit": "ckm_bidirectional_channel_count",
        **counts,
        "bidirectional_space": "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)",
        "bidirectional_reciprocal": "1/16",
        "bidirectional_reciprocal_exact": Fraction(1, counts["N_bidirectional_ud_du"]) == Fraction(1, 16),
        "same_number_distinct_sources": counts["N_bidirectional_ud_du"] == counts["N_max_self"],
        "status": "CONDITIONAL_HERMITIAN_BIDIRECTIONAL_CKM_CHANNEL_CANDIDATE",
        "claim_boundary": "The dimensions are exact; counting both directions does not prove that the BHSM action selects this transport space.",
        **input_guard(),
    }

