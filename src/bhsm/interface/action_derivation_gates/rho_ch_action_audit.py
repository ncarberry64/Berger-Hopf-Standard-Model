"""Audit whether the charged Hessian anisotropy rho_ch=3 is selected by action."""

from __future__ import annotations

from .common import FORBIDDEN_INPUTS, source_evidence


def audit_rho_ch_action() -> dict[str, object]:
    evidence = source_evidence(
        (
            "docs/bhsm_charged_hessian_source_audit.md",
            "docs/charged_stiffness_action_selector_v1.md",
            "src/charged_stiffness_action_selector.py",
        ),
        ("rho_ch_exact_value", "OPEN_LOCALIZABLE", "rho_ch=3"),
    )
    return {
        "audit": "rho_ch_action_derivation",
        "status": "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        "target": "rho_ch=k_j/k_q=3",
        "branch_candidates": [1, 2, 3],
        "selected_value": None,
        "evidence": evidence,
        "remaining_blockers": [
            "derive charged q and j stiffness coefficients from one normalized boundary action",
            "show k_j/k_q=3 independently of mass, mixing, or target-ratio comparisons",
        ],
        "forbidden_inputs_used": [],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "claim_boundary": "Rank-three and cyclic arguments motivate rho_ch=3 but do not select it from the action.",
    }
