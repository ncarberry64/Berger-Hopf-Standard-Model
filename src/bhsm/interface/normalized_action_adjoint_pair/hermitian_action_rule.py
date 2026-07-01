"""Audit the Hermitian charged-current action rule without deriving CKM."""

from __future__ import annotations

from .common import STATUS_CONDITIONAL_HERMITIAN, input_guard
from .source_search import search_normalized_action_adjoint_pair_sources


def audit_hermitian_charged_current_action_rule() -> dict[str, object]:
    search = search_normalized_action_adjoint_pair_sources()
    return {
        "audit": "hermitian_charged_current_action_rule",
        "statement": "A real/Hermitian charged-current action term must include the adjoint of an off-diagonal charged-current transport term.",
        "general_hermitian_rule": "CONDITIONAL: real-action Hermiticity supports term plus Hermitian conjugate at the rule level.",
        "bhsm_charged_current_rule": "OPEN: located BHSM artifacts identify a CKM charged-current target with + h.c., but do not derive it from the normalized BHSM action.",
        "ckm_transport_application": "OPEN: the CKM exponent is not derived from the existence of the Hermitian-conjugate term.",
        "hermiticity_sources": [
            "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
            "artifacts/BHSM_ckm_adjoint_pair_selection_v2_3.json",
            "docs/ckm_bidirectional_channel.md",
        ],
        "evidence_for": search["evidence_for_adjoint_pair"],
        "evidence_against": [
            "the CKM target convention is not the same thing as normalized-action derivation",
            "Hermitian conjugation alone does not identify the CKM log-transport averaging space",
        ],
        "status": STATUS_CONDITIONAL_HERMITIAN,
        "claim_boundary": "The existence of a Hermitian-conjugate charged-current term does not by itself derive the CKM exponent.",
        **input_guard(),
    }

