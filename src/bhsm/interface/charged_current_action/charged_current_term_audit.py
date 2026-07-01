"""Audit whether BHSM has a normalized charged-current action term."""

from __future__ import annotations

from .common import STATUS_OPEN_ACTION, input_guard
from .source_search import candidate_action_terms


def audit_normalized_charged_current_action_term() -> dict[str, object]:
    terms = candidate_action_terms()
    bounded = next(term for term in terms if term["term_id"] == "L_CKM_charged_current_bounded")
    return {
        "audit": "normalized_charged_current_action_term",
        "candidate_term": bounded["term_id"],
        "symbolic_form": bounded["symbolic_expression"],
        "normalization_sources": [
            "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",
            "artifacts/BHSM_chiral_current_attachment_map_v0_6.json",
            "artifacts/BHSM_canonical_production_basis_theorem_v0_8.json",
        ],
        "projector_sources": [
            "artifacts/BHSM_primitive_charged_incidence_closure_report_v2_0.json",
            "artifacts/BHSM_projector_reduction_audit_v2_0.json",
        ],
        "domain": "unresolved by normalized action; target convention suggests V_u input sector",
        "codomain": "unresolved by normalized action; target convention suggests V_d output sector plus h.c.",
        "adjoint_required": "unresolved_by_normalized_action",
        "action_reality_or_hermiticity_source": "target expression contains + h.c.; no normalized BHSM action source requires the conjugate term",
        "artifact_sources": [term["source"] for term in terms],
        "test_sources": [
            "tests/test_phase_three_d_canonical_current_attachment.py",
            "tests/test_phase_three_j_minimal_collider_lagrangian.py",
            "tests/test_normalized_action_adjoint_pair_selection.py",
        ],
        "evidence_for": [
            "bounded CKM charged-current target term is present",
            "candidate and bounded expressions include + h.c.",
            "CKM source matrix is local and artifact-backed",
        ],
        "evidence_against": [
            "minimal bounded subset states it is not the complete BHSM 4D Lagrangian",
            "Lorentz and gauge structures are STANDARD_HEP_TARGET_CONVENTION or target partial",
            "canonical normalization is TARGET_CONVENTION_PARTIAL or translation/runtime scoped",
            "no artifact states a normalized BHSM charged-current action term with operator domain/codomain",
        ],
        "status": STATUS_OPEN_ACTION,
        "claim_boundary": "A bounded charged-current target term is located, but the normalized BHSM charged-current action term and its operator domain/codomain remain missing.",
        **input_guard(),
    }
