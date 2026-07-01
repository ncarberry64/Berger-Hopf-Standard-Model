"""Fail-closed CKM transport-space gate for the normalized-action audit."""

from __future__ import annotations

from bhsm.interface.action_lemmas import prove_log_transport_averaging

from .adjoint_pair_selection import audit_normalized_action_adjoint_pair_selection
from .common import STATUS_OPEN_LOG_APPLICATION, STATUS_OPEN_TRANSPORT, input_guard


def audit_ckm_transport_space_gate() -> dict[str, object]:
    selection = audit_normalized_action_adjoint_pair_selection()
    lemma = prove_log_transport_averaging(16)
    selection_passes = selection["status"] == "ARTIFACT_BACKED_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"
    lemma_passes = lemma["status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA"
    gate_passes = selection_passes and lemma_passes
    return {
        "audit": "ckm_transport_space_gate",
        "selected_space": selection["selected_space"],
        "selected_dimension": selection["selected_dimension"],
        "selection_status": selection["status"],
        "log_transport_lemma_status": lemma["status"],
        "application_status": "ARTIFACT_BACKED_CKM_LOG_TRANSPORT_APPLICATION" if gate_passes else STATUS_OPEN_LOG_APPLICATION,
        "ckm_exponent_status": "derived_1_over_16" if gate_passes else "not_derived",
        "ckm_exponent_derived": gate_passes,
        "candidate_exponent": "1/16",
        "transport_space_theorem_status": "ARTIFACT_BACKED_CKM_TRANSPORT_SPACE_THEOREM" if gate_passes else STATUS_OPEN_TRANSPORT,
        "blocking_conditions": [] if gate_passes else [
            "normalized action has not selected Hom(V_u,V_d) direct_sum Hom(V_d,V_u) as the CKM transport space",
            "the abstract log-transport lemma cannot be applied to CKM until the CKM transport space theorem passes",
        ],
        "claim_boundary": "The CKM exponent remains open unless BHSM proves that CKM transport acts on the normalized Hermitian adjoint-pair charged-current space.",
        **input_guard(),
    }

