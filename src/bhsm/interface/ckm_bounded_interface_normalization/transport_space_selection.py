"""Combine all upstream gates for CKM transport-space selection."""

from __future__ import annotations

from .bounded_interface_term import audit_ckm_bounded_interface_term
from .ckm_identification_gate import audit_ckm_identification_gate
from .common import STATUS_MULTIPLE, STATUS_OPEN_SELECTION, input_guard
from .normalized_projector_sandwich import audit_normalized_projector_sandwich
from .paired_term_normalization import audit_paired_term_normalization
from .projector_domain_codomain import audit_projector_domain_codomain


def audit_ckm_transport_space_selection() -> dict[str, object]:
    bounded = audit_ckm_bounded_interface_term()
    action = audit_normalized_projector_sandwich()
    projectors = audit_projector_domain_codomain()
    paired = audit_paired_term_normalization()
    identification = audit_ckm_identification_gate()
    return {
        "audit": "ckm_transport_space_selection",
        "bounded_interface_status": bounded["status"],
        "normalized_action_status": action["status"],
        "projector_domain_codomain_status": projectors["selection_status"],
        "paired_normalization_status": paired["status"],
        "ckm_identification_status": identification["ckm_identification_status"],
        "selected_space": None,
        "selected_dimension": None,
        "selection_status": STATUS_OPEN_SELECTION,
        "overall_status": STATUS_MULTIPLE,
        "ckm_exponent_status": "not_derived",
        "blocking_conditions": [
            *action["missing_requirements"],
            "projector domain/codomain selection",
            "paired-term normalization",
            "CKM identification theorem",
            "log-transport application to the selected CKM space",
        ],
        **input_guard(),
    }
