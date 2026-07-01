"""Apply the existing abstract log-averaging lemma only after channel selection."""

from __future__ import annotations

from bhsm.interface.action_lemmas import prove_log_transport_averaging

from .common import input_guard
from .maximal_sector_selection import audit_maximal_sector_selection


def audit_ckm_channel_application() -> dict[str, object]:
    abstract = prove_log_transport_averaging(16)
    selection = audit_maximal_sector_selection()
    gate = abstract["status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA" and selection["selection_rule_proven"]
    return {
        "audit": "ckm_log_transport_application_v2_2",
        "abstract_log_lemma_status": abstract["status"],
        "maximal_sector_selection_status": selection["status"],
        "channel_equivalence_status": "ARTIFACT_BACKED_CKM_CHANNEL_EQUIVALENCE_THEOREM" if gate else "CONDITIONAL_CKM_CHANNEL_EQUIVALENCE_CANDIDATE",
        "status": "ARTIFACT_BACKED_CKM_LOG_TRANSPORT_APPLICATION" if gate else "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
        "candidate_status": "CONDITIONAL_CKM_LOG_TRANSPORT_APPLICATION",
        "selected_N_CKM": 16 if gate else None,
        "candidate_exponent": "1/16",
        "ckm_exponent_derived": gate,
        "claim_boundary": "The CKM 1/16 exponent is not derived unless BHSM proves that CKM transport acts over the N_16 charged bilinear channel space.",
        **input_guard(),
    }
