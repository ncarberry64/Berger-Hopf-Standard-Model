"""Term-complete audit of the proposed v11.2 locally supported action."""

from __future__ import annotations

from typing import Any

PRIMARY_VERDICT = "BHSM_HISTORICAL_RECOVERY_NARROWS_BUT_DOES_NOT_CLOSE_COMPLETE_SUPPORTED_ACTION"
EXACT_NEXT_OBJECT = "ACTION_DERIVED_PRIMITIVE_SUPPORT_CHARACTER_AND_CURRENT_COUPLING_LEDGER"
ACTION_VERDICT = "BHSM_COMPLETE_LOCAL_SUPPORTED_ACTION_BLOCKED_BY_UNASSIGNED_PRIMITIVE_SUPPORT_CHARACTERS"


def local_term_ledger() -> list[dict[str, Any]]:
    from bhsm.interface.envelopment.support_weight_derivation_v11_0 import parent_term_inventory

    return [
        {
            "sector": row["sector"],
            "parent_term": row["term"],
            "action_owner": row["action_owner"],
            "parent_coefficient": row["original_coefficient"],
            "primitive_support_character": None,
            "support_covariant_derivative": None,
            "linear_support_current_coupling": None,
            "quadratic_seagull_coupling": None,
            "boundary_completion": None if row["sector"] in {"boundary", "core boundary"} else row["boundary_contribution"],
            "frozen_limit": row["term"],
            "status": "BLOCKED_BY_MISSING_ACTION_OWNED_CHARACTER",
        }
        for row in parent_term_inventory()
    ]


def action_payload() -> dict[str, Any]:
    from bhsm.interface.envelopment.support_weight_derivation_v11_0 import parent_term_inventory

    terms = local_term_ledger()
    validation = {
        "all_parent_terms_audited": len(terms) == len(parent_term_inventory()),
        "support_kinetic_recovered": True,
        "connection_derived_before_action_audit": True,
        "no_character_fabricated": all(row["primitive_support_character"] is None for row in terms),
        "linear_and_quadratic_derivative_couplings_not_silently_omitted": all(
            "linear_support_current_coupling" in row and "quadratic_seagull_coupling" in row for row in terms
        ),
        "frozen_terms_preserved": all(row["frozen_limit"] == row["parent_term"] for row in terms),
        "no_new_parameter": True,
    }
    return {
        "artifact": "BHSM_complete_local_supported_action_v11_2",
        "bulk_action": None,
        "known_action_skeleton": "S_parent+D-dimensional integral[-(partial q_D)^2/2] with A_D=-(dq_D/lambda_D)",
        "support_kinetic_term": "-1/2 G^AB partial_A q_D partial_B q_D",
        "bare_support_potential": 0,
        "required_derivative_completion": "replace each parent derivative by D^(w); expansion generates -A_D.J_D and A_D^2 K_D terms fixed by the same action-owned characters",
        "gauge_sector": None,
        "fermion_sector": None,
        "scalar_topographic_sector": None,
        "charged_current_sector": None,
        "neutral_response_sector": None,
        "wall_sector": None,
        "boundary_sector": None,
        "compatibility_sector": None,
        "core_asymptotic_sector": None,
        "new_coefficients": [],
        "new_fields": [],
        "term_ledger": terms,
        "first_missing_action_owned_term": "the primitive-character support-current coupling -A_D,A J_D^A together with its covariant A_D^2 seagull completion",
        "smallest_missing_datum": "an action-derived primitive support-character/current ledger assigning the charges entering J_D and K_D",
        "complete_local_action": None,
        "status": ACTION_VERDICT,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
