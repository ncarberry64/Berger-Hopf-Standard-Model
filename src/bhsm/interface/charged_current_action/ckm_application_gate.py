"""Fail-closed CKM application gate for charged-current transport space."""

from __future__ import annotations

from bhsm.interface.action_lemmas import prove_log_transport_averaging

from .common import STATUS_OPEN_CKM_SPACE, input_guard
from .transport_space_audit import audit_charged_current_transport_space


def audit_ckm_transport_space_application_gate() -> dict[str, object]:
    transport = audit_charged_current_transport_space()
    lemma = prove_log_transport_averaging(16)
    selected_n = transport["selected_dimension"]
    gate = False
    return {
        "audit": "ckm_transport_space_application_gate",
        "charged_current_space_status": transport["transport_space_status"],
        "ckm_identification_status": STATUS_OPEN_CKM_SPACE,
        "log_transport_lemma_status": lemma["status"],
        "selected_N": selected_n,
        "application_status": "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
        "ckm_exponent_status": "not_derived" if not gate else "derived",
        "ckm_exponent_derived": gate,
        "blocking_conditions": [
            "charged-current transport space is not action-selected",
            "CKM is not proven to be the transport/mixing law on an action-selected space",
            "the abstract log-transport lemma cannot be applied to CKM without the upstream action and identification gates",
        ],
        "claim_boundary": "The Hermitian adjoint-pair channel count is 16, but the CKM exponent remains not derived unless BHSM proves CKM acts on that selected transport space.",
        **input_guard(),
    }

