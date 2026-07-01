"""Gate measure and coefficient on same-term support."""

from .common import STATUS_COEFFICIENT, STATUS_MEASURE, STATUS_PAIR, input_guard


def audit_measure_coefficient_pair() -> dict[str, object]:
    return {
        "audit": "ckm_action_measure_coefficient_pair",
        "measure_status": STATUS_MEASURE,
        "coefficient_status": STATUS_COEFFICIENT,
        "paired_action_status": "not_supported",
        "shared_sources": [],
        "same_term_support": False,
        "evidence_for_pairing": [],
        "evidence_against_pairing": ["measure and coefficient occur in different source layers", "no CKM action integral contains both"],
        "missing_requirements": ["same-term measure/coefficient source", "normalized measure", "fixed C_CKM"],
        "status": STATUS_PAIR,
        "claim_boundary": "A measure alone is not enough; a coefficient alone is not enough; both must apply to the same bounded CKM action candidate.",
        **input_guard(),
    }
