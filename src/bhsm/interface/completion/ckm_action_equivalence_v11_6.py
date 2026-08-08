"""Action-current versus v11.5 spectral-kernel equivalence audit."""

from __future__ import annotations

from typing import Any

from .parent_action_charged_current_v11_6 import current_reduction_payload


def equivalence_payload() -> dict[str, Any]:
    reduction = current_reduction_payload()
    validation = {
        "rephasing_invariant_used": True,
        "nonzero_residual": reduction["rephasing_invariant_magnitude_residual"] > 1.0e-12,
        "equivalence_rejected": reduction["equivalence_result"].startswith("NOT_EQUIVALENT"),
        "action_derived_claim_not_made": True,
    }
    return {
        "artifact": "BHSM_CKM_action_equivalence_v11_6",
        "version": "v11.6",
        "action_current": "I3 on the live effective-action weak-family basis",
        "candidate_current": "v11.5 author-selected spectral K_ud",
        "allowed_equivalence": "independent diagonal quark-field rephasings on up and down mass eigenstates",
        "invariant": "entrywise magnitudes",
        "residual": reduction["rephasing_invariant_magnitude_residual"],
        "result": reduction["equivalence_result"],
        "physical_CKM_action_derived": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
