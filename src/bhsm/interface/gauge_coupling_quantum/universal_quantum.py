"""Gate the proposed universal gauge-coupling quantum."""

from .common import STATUS_ATTACHMENT, STATUS_QUANTUM, STATUS_REGISTRY, STATUS_VOLUME, STATUS_WEIGHTS, input_guard


def audit_universal_gauge_coupling_quantum() -> dict[str, object]:
    return {
        "candidate_quantum": "lambda_gauge=1/(6*pi^2)",
        "denominator_status": STATUS_VOLUME,
        "weight_status": STATUS_WEIGHTS,
        "registry_status": STATUS_REGISTRY,
        "action_attachment_status": STATUS_ATTACHMENT,
        "formula": "alpha_i=w_i*lambda_gauge",
        "evidence_for": ["the exact common factor is registry-backed", "the 1,2,7 count is a structural candidate"],
        "evidence_against": [
            "the geometric denominator source remains open",
            "the normalized gauge action does not attach the candidate quantum",
        ],
        "is_action_derived": False,
        "status": STATUS_QUANTUM,
        "claim_boundary": "The registry factor is not a universal action-derived quantum without denominator, weight, and action attachment proofs.",
        **input_guard(),
    }
