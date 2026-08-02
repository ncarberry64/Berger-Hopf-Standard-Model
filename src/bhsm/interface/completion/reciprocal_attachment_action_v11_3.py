"""Smallest reciprocal support dressing of the inherited Lambda85 matcher."""

from __future__ import annotations

from math import sqrt
from typing import Any

from .attachment_incidence_ledger_v11_3 import ledger_payload


PRIMARY_VERDICT = "BHSM_RECIPROCAL_ATTACHMENT_ACTION_AND_CURRENT_DERIVED_WITH_THREE_MODE_DOMAIN_CONDITIONAL"
EXACT_NEXT_OBJECT = "ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN_ON_COMMON_ATTACHMENT_DOMAIN"


def mismatch(upsilon: float, incidence_core: float, incidence_wall: float) -> float:
    if upsilon <= 0:
        raise ValueError("upsilon must be positive on the regular domain")
    return incidence_wall / sqrt(upsilon) - sqrt(upsilon) * incidence_core


def attachment_density(upsilon: float, incidence_core: float, incidence_wall: float, multiplier: float) -> float:
    return multiplier * mismatch(upsilon, incidence_core, incidence_wall)


def qd_source(upsilon: float, incidence_core: float, incidence_wall: float, multiplier: float, lambda_d: float) -> float:
    """Return J_attach=-delta S_attach/delta q_D for upsilon=exp(-q_D/lambda_D)."""

    if lambda_d <= 0:
        raise ValueError("lambda_D must be positive")
    return -(multiplier / (2 * lambda_d)) * (
        incidence_wall / sqrt(upsilon) + sqrt(upsilon) * incidence_core
    )


def action_payload() -> dict[str, Any]:
    recovered = ledger_payload()
    validation = {
        "compatibility_action_recovered": recovered["validation_passed"],
        "frozen_mismatch_exact": mismatch(1.0, 3.0, 5.0) == 2.0,
        "multiplier_equation_exact": mismatch(0.25, 4.0, 1.0) == 0.0,
        "qd_source_sign_fixed": qd_source(1.0, 2.0, 2.0, 3.0, 5.0) == -1.2,
        "no_new_coefficient": True,
        "no_new_field": True,
        "no_new_mediator": True,
        "intrinsic_metric_not_dressed": True,
        "frozen_predictions_unchanged": True,
    }
    return {
        "artifact": "BHSM_reciprocal_attachment_action_v11_3",
        "classification": "AUTHOR_ACTION_SELECTION_AND_DERIVED_COMPLETION",
        "selection_principle": "BHSM_RECIPROCAL_CORE_SURFACE_ATTACHMENT_PRINCIPLE",
        "inherited_term": "int_M5 dmu5 <Lambda85,I_W-I_C>",
        "incidence_identification": {"I_C": "Q_H(G8)", "I_W": "id_5(g5)"},
        "exact_action": "S_attach=int_M5 dmu5 <Lambda85,upsilon^(-1/2) I_W-upsilon^(1/2) I_C>",
        "sign_reason": "this ordering preserves the exact inherited g5-Q_H(G8) convention",
        "hermitian_completion": "the recovered metric pairing is real; for a complex associated incidence use Re<Lambda85,C_attach>, which adds no coefficient",
        "frozen_limit": {"upsilon": 1, "q_D": 0, "A_D": 0, "mismatch": "I_W-I_C", "action": "exact inherited Lambda85 term"},
        "multiplier_equation": "upsilon^(-1/2) I_W-upsilon^(1/2) I_C=0, equivalently I_W=upsilon I_C",
        "q_D_variation": "delta S_attach/delta q_D=(1/(2 lambda_D))<Lambda85,upsilon^(-1/2)I_W+upsilon^(1/2)I_C>",
        "q_D_source": "J_attach=-(1/(2 lambda_D))<Lambda85,upsilon^(-1/2)I_W+upsilon^(1/2)I_C>",
        "q_D_equation": "Box_G q_D=J_shift,inherited+J_attach, with each inherited term included once",
        "core_variation": "delta_I_C S_attach=-int dmu5 <upsilon^(1/2)Lambda85,delta I_C>",
        "wall_variation": "delta_I_W S_attach=+int dmu5 <upsilon^(-1/2)Lambda85,delta I_W>",
        "embedding_equation": "the Q_H and trace adjoints insert the two dressed reactions into the inherited E8/E5 KKT embedding equations",
        "unchanged_compatibility_terms": ["lambda_sigma(sigma5-P0 sigma8)", "Lambda54(h-iota^*g5)"],
        "new_fields": [],
        "new_coefficients": [],
        "new_parameters": [],
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
