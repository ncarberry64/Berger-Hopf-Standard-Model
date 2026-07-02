"""Audit the candidate gauge-sector weights 1, 2, and 7."""

from .common import STATUS_WEIGHTS, input_guard


def audit_gauge_sector_weight_source() -> dict[str, object]:
    return {
        "candidate_weights": {"w1": 1, "w2": 2, "w3": 7},
        "weight_sources": [
            "theory/full_bhsm_candidate_theory_line_v0_1.md",
            "theory/full_bhsm_completion_v1_candidate.md",
        ],
        "weak_weight_source": "candidate dim(SU2)-1=2 active-generator count",
        "hypercharge_weight_source": "candidate C_U1=1 convention",
        "strong_weight_source": "candidate dim(SU3)-1=7 active-generator count",
        "trace_sources": ["theory/theorem_discharge_boundary_trace_normalization.md"],
        "finite_algebra_sources": ["theory/finite_boundary_algebra_source_gate.md"],
        "projector_sources": [],
        "charged_trace_sources": [],
        "evidence_for": ["the candidate theory explicitly records active-generator counts 1,2,7"],
        "evidence_against": [
            "the source classifies the rule as a structural candidate",
            "trace weights K1=10/3, K2=K3=2 do not derive 1,2,7",
            "no normalized action selects these counts as coupling coefficients",
        ],
        "status": STATUS_WEIGHTS,
        "claim_boundary": "Sector weights do not by themselves derive the gauge couplings.",
        **input_guard(),
    }
