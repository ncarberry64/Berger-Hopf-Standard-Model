"""Combined v2.3 Hermitian bidirectional CKM channel report."""

from __future__ import annotations

from .adjoint_pair_audit import audit_ckm_adjoint_pair_selection
from .alternative_resolution_audit import audit_ckm_channel_alternative_resolution
from .bidirectional_channel_count import audit_bidirectional_channel_count
from .ckm_application_gate import audit_bidirectional_log_transport_application
from .source_search import search_ckm_bidirectional_sources


def build_ckm_bidirectional_channel_report() -> dict[str, object]:
    return {
        "version": "2.3",
        "status": "CONDITIONAL_HERMITIAN_BIDIRECTIONAL_CKM_CHANNEL_CANDIDATE",
        "source_search": search_ckm_bidirectional_sources(),
        "channel_count": audit_bidirectional_channel_count(),
        "adjoint_pair_selection": audit_ckm_adjoint_pair_selection(),
        "alternative_resolution": audit_ckm_channel_alternative_resolution(),
        "application": audit_bidirectional_log_transport_application(),
        "frozen_predictions_modified": False,
        "official_prediction_logic_modified": False,
        "physics_validation_claimed": False,
        "full_completion_claimed": False,
        "claim_boundary": "The Hermitian bidirectional channel is the preferred conditional source of 16; action-level adjoint-pair selection and CKM application remain open.",
    }

