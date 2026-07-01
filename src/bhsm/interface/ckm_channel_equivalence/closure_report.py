"""Combined v2.2 CKM channel-equivalence report."""

from __future__ import annotations

from .alternative_channel_audit import audit_alternative_channel_assignments
from .channel_count_audit import audit_ckm_channel_counts
from .ckm_application_audit import audit_ckm_channel_application
from .maximal_sector_selection import audit_maximal_sector_selection
from .source_search import search_ckm_channel_sources


def build_ckm_channel_equivalence_report() -> dict[str, object]:
    return {
        "version": "2.2",
        "status": "OPEN_MISSING_CKM_CHANNEL_EQUIVALENCE_THEOREM",
        "source_search": search_ckm_channel_sources(),
        "channel_counts": audit_ckm_channel_counts(),
        "alternatives": audit_alternative_channel_assignments(),
        "maximal_selection": audit_maximal_sector_selection(),
        "application": audit_ckm_channel_application(),
        "frozen_predictions_modified": False,
        "official_predictions_modified": False,
        "ckm_numerical_values_modified": False,
        "full_completion_claimed": False,
        "claim_boundary": "The four channel dimensions are exact; BHSM has not selected N_CKM=16 over the competing assignments.",
    }
