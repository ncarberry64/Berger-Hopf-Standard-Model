"""Apply the v2.1 abstract lemma only after action-backed adjoint selection."""

from __future__ import annotations

from bhsm.interface.action_lemmas import prove_log_transport_averaging

from .adjoint_pair_audit import audit_ckm_adjoint_pair_selection
from .common import input_guard


def audit_bidirectional_log_transport_application() -> dict[str, object]:
    abstract = prove_log_transport_averaging(16)
    selection = audit_ckm_adjoint_pair_selection()
    gate = abstract["status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA" and selection["selection_rule_proven"]
    return {
        "audit": "ckm_bidirectional_log_transport_application",
        "abstract_log_lemma_status": abstract["status"],
        "adjoint_pair_selection_status": selection["status"],
        "status": "ARTIFACT_BACKED_CKM_LOG_TRANSPORT_APPLICATION" if gate else "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
        "candidate_status": "CONDITIONAL_CKM_LOG_TRANSPORT_APPLICATION",
        "selected_N_CKM": 16 if gate else None,
        "candidate_exponent": "1/16",
        "ckm_exponent_derived": gate,
        "claim_boundary": "The bidirectional count does not derive the CKM exponent unless BHSM proves that transport is governed by the Hermitian charged-current adjoint pair.",
        **input_guard(),
    }

