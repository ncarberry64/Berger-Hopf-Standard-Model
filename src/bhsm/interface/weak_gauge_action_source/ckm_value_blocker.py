"""Propagate the weak-action blocker to the CKM coefficient value."""

from .common import STATUS_CKM_VALUE, STATUS_COEFFICIENT, input_guard


def audit_ckm_value_source_blocker() -> dict[str, object]:
    return {
        "ckm_coefficient_form_status": "ARTIFACT_BACKED_CKM_COEFFICIENT_FORM",
        "g2_action_status": "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "alpha2_action_status": "OPEN_MISSING_ALPHA2_BH_ACTION_SOURCE",
        "weak_gauge_action_coefficient_status": STATUS_COEFFICIENT,
        "ckm_coefficient_value_status": STATUS_CKM_VALUE,
        "ckm_exponent_status": "not_derived",
        "blocking_conditions": ["weak action does not fix g2_BH or alpha2_BH", "measure/projector/paired/identification gates remain open"],
        **input_guard(),
    }
