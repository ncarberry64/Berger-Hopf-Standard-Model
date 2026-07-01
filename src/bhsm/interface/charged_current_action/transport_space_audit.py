"""Audit candidate transport spaces for the charged-current action term."""

from __future__ import annotations

from .charged_current_term_audit import audit_normalized_charged_current_action_term
from .common import STATUS_MULTIPLE_SPACES, STATUS_OPEN_SPACE, STATUS_RETIRED_MAXIMAL, channel_dimensions, input_guard


def audit_charged_current_transport_space() -> dict[str, object]:
    action = audit_normalized_charged_current_action_term()
    dims = channel_dimensions()
    rows = [
        {
            "space_id": "one_way_up_down",
            "symbolic_space": "Hom(V_u,V_d)",
            "dimension": dims["one_way_up_down"],
            "interpretation": "one-way up/down charged-current map",
            "action_evidence_for": ["target bilinear contains ubar_i ... d_j"],
            "action_evidence_against": ["candidate terms also contain + h.c.; normalized action does not select one-way-only transport"],
            "current_status": STATUS_OPEN_SPACE,
            "what_would_select_it": "a normalized action term declaring J_ud as the transport operator without adjoint-pair channel counting",
            "what_would_falsify_it": "an action theorem requiring Hermitian adjoint-pair closure or a different transport algebra",
        },
        {
            "space_id": "hermitian_adjoint_pair",
            "symbolic_space": "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)",
            "dimension": dims["bidirectional_adjoint_pair"],
            "interpretation": "off-diagonal charged-current map plus Hermitian adjoint",
            "action_evidence_for": ["target/interface expressions include + h.c."],
            "action_evidence_against": ["+ h.c. is not yet tied to normalized BHSM action selection"],
            "current_status": "OPEN_MISSING_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE",
            "what_would_select_it": "a normalized action theorem proving the off-diagonal map and conjugate term are jointly required",
            "what_would_falsify_it": "an action theorem selecting one-way, sector-self, total-endomorphism, or maximal-self transport instead",
        },
        {
            "space_id": "sector_self_response_sum",
            "symbolic_space": "End(V_l) direct_sum End(V_u) direct_sum End(V_d)",
            "dimension": dims["sector_self_response_sum"],
            "interpretation": "sectorwise charged self-response sum",
            "action_evidence_for": ["charged incidence audits track sector dimensions 1, 2, 4"],
            "action_evidence_against": ["not the located charged-current target form"],
            "current_status": STATUS_OPEN_SPACE,
            "what_would_select_it": "a normalized charged action showing CKM transport averages sector self-responses",
            "what_would_falsify_it": "an action theorem restricting transport to off-diagonal charged-current maps",
        },
        {
            "space_id": "total_charged_endomorphism",
            "symbolic_space": "End(V_ch)",
            "dimension": dims["total_charged_endomorphism"],
            "interpretation": "full charged endomorphism algebra",
            "action_evidence_for": ["recorded as a competing algebraic assignment"],
            "action_evidence_against": ["no located charged-current action acts on all charged endomorphisms"],
            "current_status": STATUS_OPEN_SPACE,
            "what_would_select_it": "a normalized action term with domain/codomain V_ch and full End(V_ch) transport",
            "what_would_falsify_it": "a theorem selecting the smaller one-way or adjoint-pair charged-current block",
        },
        {
            "space_id": "maximal_self_response",
            "symbolic_space": "End(V_d)",
            "dimension": dims["maximal_self_response"],
            "interpretation": "maximal down-sector self-response",
            "action_evidence_for": ["same numerical dimension as the adjoint-pair candidate"],
            "action_evidence_against": ["same numerical dimension does not establish physical source"],
            "current_status": STATUS_RETIRED_MAXIMAL,
            "what_would_select_it": "explicit action evidence reviving End(V_d) as charged-current transport",
            "what_would_falsify_it": "an action theorem selecting off-diagonal charged-current transport or another space",
        },
    ]
    return {
        "audit": "charged_current_transport_space",
        "action_term_status": action["status"],
        "spaces": rows,
        "selected_space": None,
        "selected_dimension": None,
        "status": STATUS_MULTIPLE_SPACES,
        "transport_space_status": STATUS_OPEN_SPACE,
        "claim_boundary": "The normalized charged-current action term, not arithmetic channel-count coincidence, must select the CKM transport space.",
        **input_guard(),
    }

