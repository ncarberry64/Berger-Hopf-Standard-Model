"""Formal supported-action family and v11.1 uniqueness obstruction."""

from __future__ import annotations

from typing import Any

from bhsm.interface.envelopment.support_weight_derivation_v11_0 import parent_term_inventory

from .support_representation_category_v11_1 import FUNCTOR_VERDICT, NEXT_EXACT_OBJECT


ACTION_VERDICT = "BHSM_COMPLETE_SUPPORTED_PARENT_ACTION_NOT_SELECTED_BY_CURRENT_ACTION"


def term_ledger() -> list[dict[str, Any]]:
    rows = []
    for source in parent_term_inventory():
        rows.append(
            {
                "term": source["term"],
                "sector": source["sector"],
                "original_formula": source["term"],
                "action_owner": source["action_owner"],
                "existing_action_coefficient": source["original_coefficient"],
                "support_representation": None,
                "weight": None,
                "weight_source": None,
                "integer_or_rational_proof": None,
                "measure_contribution": None,
                "field_contribution": None,
                "connection_contribution": None,
                "boundary_contribution": source["boundary_contribution"],
                "variation": None,
                "support_current": None,
                "stress_contribution": None,
                "frozen_limit": source["term"],
                "status": "BLOCKED_BY_NONUNIQUE_SUPPORT_FUNCTOR",
            }
        )
    return rows


def supported_action_payload() -> dict[str, Any]:
    terms = term_ledger()
    validation = {
        "all_parent_terms_audited": len(terms) == len(parent_term_inventory()),
        "no_support_weight_fabricated": all(row["weight"] is None for row in terms),
        "frozen_limit_retained": all(row["frozen_limit"] == row["original_formula"] for row in terms),
        "no_bare_support_potential": True,
        "no_new_coefficient_adopted": True,
        "no_particle_inputs": True,
    }
    return {
        "artifact": "BHSM_supported_parent_action_v11_1",
        "formal_family": "S[w,lambda_D]=integral_regular sqrt(-G)[-1/2(nabla q_D)^2+sum_a exp(-w_a q_D/lambda_D)L_a]+S_boundary[w]+S_core[w]",
        "formal_support_equation": "Box_G q_D=sum_a (w_a/lambda_D) exp(-w_a q_D/lambda_D)L_a plus boundary/core response",
        "formal_regular_scalar_stress": "T_AB[q_D]=partial_A q_D partial_B q_D-G_AB(partial q_D)^2/2",
        "formal_support_current": "J_D=sum_a (w_a/lambda_D) exp(-w_a q_D/lambda_D)L_a",
        "boundary_terms": None,
        "core_terms": None,
        "complete_conservation_identity": None,
        "frozen_limit": "S[w,lambda_D] at q_D=0 equals the supplied regular parent terms only after boundary/core domains are supplied",
        "bare_support_potential": 0,
        "new_coefficients": [],
        "support_weights": None,
        "lambda_D": None,
        "term_ledger": terms,
        "unique_complete_formula": None,
        "functor_status": FUNCTOR_VERDICT,
        "status": ACTION_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
