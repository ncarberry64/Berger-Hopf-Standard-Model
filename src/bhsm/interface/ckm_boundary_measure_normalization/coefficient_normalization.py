"""Audit the CKM charged-current coefficient."""

from .common import STATUS_COEFFICIENT, input_guard


def audit_coefficient_normalization() -> dict[str, object]:
    return {
        "audit": "ckm_coefficient_normalization",
        "candidate_coefficient": "C_CKM candidate = g2_BH_runtime / sqrt(2)",
        "candidate_source": "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",
        "is_geometric_or_fitted": "runtime/scheme parameter; neither geometric derivation nor empirical fit used here",
        "depends_on_frozen_predictions": False,
        "depends_on_reference_values": False,
        "normalization_rule": None,
        "evidence_for": ["the interface target declares an explicit symbolic coefficient"],
        "evidence_against": ["g2_BH_runtime is explicitly collider-interface runtime input", "no action theorem fixes C_CKM"],
        "missing_requirements": ["fixed geometric coefficient", "action normalization rule", "scheme-independent provenance"],
        "status": STATUS_COEFFICIENT,
        "claim_boundary": "A coefficient normalization alone does not derive the CKM exponent.",
        **input_guard(),
    }
