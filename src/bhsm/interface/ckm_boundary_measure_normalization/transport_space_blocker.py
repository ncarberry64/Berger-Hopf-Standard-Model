"""Preserve the downstream CKM blockers."""

from .common import STATUS_ACTION, STATUS_IDENTIFICATION, STATUS_PAIRED, STATUS_PROJECTOR, STATUS_TRANSPORT, channel_dimensions, input_guard


def audit_transport_space_blocker() -> dict[str, object]:
    dims = channel_dimensions()
    return {
        "audit": "ckm_transport_space_blocker",
        "normalized_action_status": STATUS_ACTION,
        "projector_sandwich_status": STATUS_PROJECTOR,
        "paired_normalization_status": STATUS_PAIRED,
        "ckm_identification_status": STATUS_IDENTIFICATION,
        "selected_transport_space": None,
        "selected_dimension": None,
        "why_no_selection_if_open": ["normalization gates remain open", "CKM identification theorem remains open"],
        "competing_spaces": {"Hom(V_u,V_d)": dims["one_way_up_down"], "adjoint_pair": dims["bidirectional_adjoint_pair"], "End(V_d)": dims["maximal_self_response"], "sector_self": dims["sector_self_response_sum"], "End(V_ch)": dims["total_charged_endomorphism"]},
        "ckm_exponent_status": "not_derived",
        "status": STATUS_TRANSPORT,
        **input_guard(),
    }
