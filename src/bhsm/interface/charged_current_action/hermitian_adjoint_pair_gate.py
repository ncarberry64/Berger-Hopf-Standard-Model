"""Gate Hermitian adjoint-pair transport on normalized action evidence."""

from __future__ import annotations

from .charged_current_term_audit import audit_normalized_charged_current_action_term
from .common import STATUS_OPEN_ADJOINT, input_guard


def audit_hermitian_adjoint_pair_transport_gate() -> dict[str, object]:
    action = audit_normalized_charged_current_action_term()
    off_diagonal = "ubar_i" in action["symbolic_form"] and "d_j" in action["symbolic_form"]
    hermiticity = "+ h.c." in action["symbolic_form"]
    gate = False
    return {
        "audit": "hermitian_adjoint_pair_transport_gate",
        "off_diagonal_map_present": off_diagonal,
        "hermiticity_required": hermiticity,
        "conjugate_term_required": False,
        "normalization_ties_both_terms": False,
        "selected_space": None,
        "selected_dimension": None,
        "status": STATUS_OPEN_ADJOINT if not gate else "ARTIFACT_BACKED_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE",
        "blocking_conditions": [
            "located off-diagonal and + h.c. evidence is target/interface level",
            "no normalized BHSM charged-current action source requires the conjugate term",
            "no normalization artifact ties J_ud and J_ud dagger into the selected transport space",
        ],
        "claim_boundary": "The existence of a Hermitian-conjugate term supports action reality but does not by itself derive CKM transport-space selection.",
        **input_guard(),
    }
