"""Combined v2.1 action-lemma closure report."""

from __future__ import annotations

from .ckm_application_gate import audit_ckm_log_transport_application
from .log_transport_averaging import prove_log_transport_averaging
from .maximal_overlap_bridge_rule import audit_maximal_overlap_bridge_rule
from .primitive_lattice_rule import audit_primitive_lattice_rule
from .source_search import search_action_lemma_sources


def build_action_lemma_closure_report() -> dict[str, object]:
    return {
        "version": "2.1",
        "status": "ABSTRACT_LOG_LEMMA_PROVEN_ACTION_APPLICATIONS_OPEN",
        "source_search": search_action_lemma_sources(),
        "primitive_lattice": audit_primitive_lattice_rule(),
        "maximal_overlap": audit_maximal_overlap_bridge_rule(),
        "abstract_log_transport": prove_log_transport_averaging(16),
        "ckm_application": audit_ckm_log_transport_application(),
        "frozen_predictions_modified": False,
        "official_predictions_modified": False,
        "full_completion_claimed": False,
        "claim_boundary": "An exact abstract variational lemma is proved; BHSM action and CKM applications remain evidence-gated.",
    }
