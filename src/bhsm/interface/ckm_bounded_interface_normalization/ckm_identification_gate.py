"""Gate identification of the bounded current with CKM transport."""

from __future__ import annotations

from .common import STATUS_OPEN_ACTION, STATUS_OPEN_IDENTIFICATION, STATUS_OPEN_PROJECTORS, input_guard


def audit_ckm_identification_gate() -> dict[str, object]:
    return {
        "audit": "ckm_identification_gate",
        "charged_current_term_status": STATUS_OPEN_ACTION,
        "transport_space_status": STATUS_OPEN_PROJECTORS,
        "ckm_identifier_sources": [
            "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",
            "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
        ],
        "mixing_law_sources": ["target uses V_CKM_BH, but no action-selected transport theorem is present"],
        "ckm_identification_status": STATUS_OPEN_IDENTIFICATION,
        "blocking_conditions": [
            "normalized projector-sandwiched action term is missing",
            "charged-current transport space is not selected",
            "no theorem identifies V_CKM_BH as the transport law on an action-selected space",
        ],
        **input_guard(),
    }
