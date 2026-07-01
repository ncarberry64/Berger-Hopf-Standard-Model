"""Gate application of the abstract averaging lemma to BHSM CKM transport."""

from __future__ import annotations

from .common import input_guard
from .log_transport_averaging import prove_log_transport_averaging
from .source_search import search_action_lemma_sources


def audit_ckm_log_transport_application() -> dict[str, object]:
    abstract = prove_log_transport_averaging(16)
    equivalent_channels = search_action_lemma_sources()["ckm_equivalent_channel_evidence_found"]
    gate_passes = abstract["status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA" and equivalent_channels
    return {
        "application": "BHSM_CKM_log_transport",
        "abstract_lemma_status": abstract["status"],
        "candidate_exponent": "1/16",
        "N_16_equivalent_bilinear_channels_proven": equivalent_channels,
        "application_gate_passes": gate_passes,
        "status": (
            "ARTIFACT_BACKED_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
            if gate_passes
            else "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM"
        ),
        "candidate_status": "CONDITIONAL_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
        "ckm_exponent_derived": gate_passes,
        "claim_boundary": "The CKM exponent remains open unless BHSM proves CKM transport acts over N_16 equivalent bilinear charged-incidence channels.",
        **input_guard(),
    }
