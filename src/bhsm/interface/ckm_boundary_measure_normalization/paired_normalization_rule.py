"""Audit shared normalization of forward and adjoint terms."""

from .common import STATUS_PAIRED, input_guard


def audit_paired_normalization_rule() -> dict[str, object]:
    return {
        "audit": "ckm_paired_normalization_rule",
        "forward_term": "ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu",
        "adjoint_term": "h.c. target convention",
        "same_measure_source": False,
        "same_coefficient_source": False,
        "same_projector_rule": False,
        "hermiticity_source": "target-level + h.c.",
        "paired_as_single_action_object": False,
        "evidence_for": ["both target directions are denoted"],
        "evidence_against": ["no shared measure, coefficient, projector, or variational source"],
        "status": STATUS_PAIRED,
        "claim_boundary": "Hermitian-conjugate notation does not supply paired action normalization.",
        **input_guard(),
    }
