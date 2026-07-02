"""Propagate the v3.1 g2 result to the CKM coefficient value."""

from .common import STATUS_CKM, STATUS_G2, input_guard


def audit_ckm_value_source_update() -> dict[str, object]:
    return {
        "ckm_coefficient_form_status": "ARTIFACT_BACKED_CKM_COEFFICIENT_FORM",
        "g2_action_status": STATUS_G2,
        "ckm_value_status": STATUS_CKM,
        "ckm_exponent_status": "not_derived",
        "blocking_conditions": [
            "g2_BH value is not action-derived",
            "measure/projector/paired/identification gates remain open",
        ],
        "status": STATUS_CKM,
        **input_guard(),
    }
