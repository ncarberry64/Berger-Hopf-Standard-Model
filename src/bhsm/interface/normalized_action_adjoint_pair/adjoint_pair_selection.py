"""Audit normalized-action selection of the CKM adjoint-pair space."""

from __future__ import annotations

from .common import STATUS_OPEN_SELECTION, channel_dimensions, input_guard
from .hermitian_action_rule import audit_hermitian_charged_current_action_rule
from .source_search import search_normalized_action_adjoint_pair_sources


def audit_normalized_action_adjoint_pair_selection() -> dict[str, object]:
    dims = channel_dimensions()
    search = search_normalized_action_adjoint_pair_sources()
    hermitian = audit_hermitian_charged_current_action_rule()
    return {
        "audit": "normalized_action_adjoint_pair_selection",
        "statement": "Test whether the normalized BHSM charged-current action requires CKM transport on Hom(V_u,V_d) direct_sum Hom(V_d,V_u).",
        "candidate_channel_space": "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)",
        "dimension_count": {
            "dim_V_u": dims["s_u"],
            "dim_V_d": dims["s_d"],
            "dim_Hom_Vu_Vd": dims["one_way_up_down"],
            "dim_Hom_Vd_Vu": dims["one_way_down_up"],
            "N_CKM_candidate": dims["bidirectional_adjoint_pair"],
        },
        "action_sources": [
            "artifacts/BHSM_ckm_adjoint_pair_selection_v2_3.json",
            "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
            "artifacts/BHSM_action_lemma_closure_report_v2_1.json",
        ],
        "hermiticity_sources": hermitian["hermiticity_sources"],
        "normalized_action_sources": [
            "artifacts/BHSM_minimal_action_report_v0_8.json",
            "artifacts/BHSM_action_lemma_closure_report_v2_1.json",
            "artifacts/BHSM_physical_normalization_gate_v2_0.json",
        ],
        "evidence_for": search["evidence_for_adjoint_pair"],
        "evidence_against": search["evidence_against_action_derivation"],
        "competing_assignments": [
            "one-way up/down N=8",
            "bidirectional adjoint-pair N=16",
            "maximal self-response N=16",
            "sector self-response sum N=21",
            "total charged endomorphism N=49",
        ],
        "proof_gap": "No artifact-backed normalized BHSM action theorem selects the off-diagonal Hermitian charged-current adjoint-pair space as the CKM transport target.",
        "status": STATUS_OPEN_SELECTION,
        "selection_rule_proven": False,
        "selected_space": None,
        "selected_dimension": None,
        "claim_boundary": "The bidirectional adjoint-pair channel count is 16, but this is a conditional channel assignment until selected by the normalized action.",
        **input_guard(),
    }

