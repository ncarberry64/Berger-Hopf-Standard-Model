"""Compute all predeclared CKM channel-space dimensions exactly."""

from __future__ import annotations

from fractions import Fraction

from .common import S_CH, channel_counts, input_guard


def audit_ckm_channel_counts() -> dict[str, object]:
    counts = channel_counts()
    return {
        "audit": "ckm_channel_count",
        "s_ch": list(S_CH),
        **counts,
        "max_self_reciprocal": "1/16",
        "max_self_reciprocal_exact": Fraction(1, counts["N_max_self"]) == Fraction(1, 16),
        "candidate_assignments": {
            "up_down_cross_Hom": counts["N_ud"],
            "total_charged_End": counts["N_total_end"],
            "sum_sector_self_responses": counts["N_sum_self"],
            "maximal_sector_self_response": counts["N_max_self"],
        },
        "selected_N_CKM": None,
        "selected_N_CKM_status": "OPEN_NO_ACTION_SELECTION_RULE",
        "status": "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS",
        "claim_boundary": "All four dimensions are exact; arithmetic alone does not choose the CKM transport space.",
        **input_guard(),
    }
