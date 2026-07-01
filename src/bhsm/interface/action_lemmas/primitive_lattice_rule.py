"""Fail-closed primitive-lattice normalization action lemma."""

from __future__ import annotations

from math import gcd

from .common import input_guard
from .source_search import search_action_lemma_sources


def audit_primitive_lattice_rule() -> dict[str, object]:
    omega = (3, 6, 12)
    rho = gcd(gcd(*omega[:2]), omega[2])
    quotient_evidence = search_action_lemma_sources()["action_quotient_evidence_found"]
    return {
        "lemma": "primitive_lattice_normalization",
        "omega_ch": list(omega),
        "rho_ch": rho,
        "primitive_representative": [value // rho for value in omega],
        "exact_gcd_identity": True,
        "candidate_status": "CONDITIONAL_PRIMITIVE_LATTICE_NORMALIZATION_RULE",
        "status": (
            "ARTIFACT_BACKED_PRIMITIVE_LATTICE_NORMALIZATION_RULE"
            if quotient_evidence
            else "OPEN_MISSING_ACTION_PRIMITIVE_LATTICE_NORMALIZATION_RULE"
        ),
        "action_invariant_under_common_rescaling": quotient_evidence,
        "action_derived": quotient_evidence,
        "claim_boundary": "The primitive lattice normalization rule is not action-derived unless the BHSM action is shown to quotient common incidence rescalings.",
        **input_guard(),
    }
