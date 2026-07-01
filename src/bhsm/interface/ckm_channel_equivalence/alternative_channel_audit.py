"""Record competing CKM channel assignments and their unresolved provenance."""

from __future__ import annotations

from .common import channel_counts, input_guard


def audit_alternative_channel_assignments() -> dict[str, object]:
    counts = channel_counts()
    rows = [
        {"id": "V_u_tensor_V_d_dual", "dimension": counts["N_ud"], "structural_motive": "cross-sector up/down mixing", "excluded": False},
        {"id": "End_V_ch", "dimension": counts["N_total_end"], "structural_motive": "full charged response algebra", "excluded": False},
        {"id": "direct_sum_End_V_f", "dimension": counts["N_sum_self"], "structural_motive": "sector-preserving self responses", "excluded": False},
        {"id": "End_V_d", "dimension": counts["N_max_self"], "structural_motive": "maximal primitive self response", "excluded": False},
    ]
    return {
        "audit": "ckm_alternative_channel_assignments",
        "rows": rows,
        "unique_surviving_assignment": None,
        "status": "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS",
        "claim_boundary": "No candidate is rejected without an action or representation-selection theorem.",
        **input_guard(),
    }
