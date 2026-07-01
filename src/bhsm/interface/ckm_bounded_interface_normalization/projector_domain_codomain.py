"""Audit projector evidence and action-selected operator directions."""

from __future__ import annotations

from .common import STATUS_MULTIPLE, STATUS_OPEN_PROJECTORS, STATUS_RETIRED_MAXIMAL, channel_dimensions, input_guard


def audit_projector_domain_codomain() -> dict[str, object]:
    dims = channel_dimensions()
    candidates = [
        {"space": "Hom(V_u,V_d)", "dimension": dims["one_way_up_down"]},
        {"space": "Hom(V_d,V_u)", "dimension": dims["one_way_up_down"]},
        {"space": "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)", "dimension": dims["bidirectional_adjoint_pair"]},
        {"space": "End(V_d)", "dimension": dims["maximal_self_response"], "status": STATUS_RETIRED_MAXIMAL},
        {"space": "End(V_l) direct_sum End(V_u) direct_sum End(V_d)", "dimension": dims["sector_self_response_sum"]},
        {"space": "End(V_ch)", "dimension": dims["total_charged_endomorphism"]},
    ]
    return {
        "audit": "projector_domain_codomain_selection",
        "candidate_spaces": candidates,
        "projector_evidence": ["charged-sector projector identities exist, but are not attached to the bounded CKM term"],
        "domain_codomain_evidence": ["target bilinear suggests up/down directions; no action artifact declares them"],
        "selected_space": None,
        "selected_dimension": None,
        "selection_status": STATUS_OPEN_PROJECTORS,
        "overall_status": STATUS_MULTIPLE,
        "competing_spaces": [row["space"] for row in candidates],
        "blocking_conditions": [
            "no projector sandwich in the bounded term",
            "no action-declared operator domain/codomain",
            "target-level + h.c. does not select adjoint-pair channel counting",
        ],
        **input_guard(),
    }
