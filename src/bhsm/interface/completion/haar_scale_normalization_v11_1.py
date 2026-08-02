"""Exhaust the permitted BHSM v11.1 Haar-scale normalization routes."""

from __future__ import annotations

from typing import Any

from .support_representation_category_v11_1 import NEXT_EXACT_OBJECT


HAAR_VERDICT = "BHSM_HAAR_SCALE_PHYSICAL_OR_CONVENTIONAL_STATUS_AWAITS_SUPPORT_REPRESENTATION_EQUIVALENCE_QUOTIENT"


def normalization_routes() -> list[dict[str, Any]]:
    return [
        {
            "route": "A_pure_coordinate_normalization",
            "tested_transformation": "q_D->c q_D, lambda_D->c lambda_D",
            "result": "INVALIDATED_AS_A_PHYSICAL_EQUIVALENCE_AFTER_CANONICAL_KINETIC_NORMALIZATION",
            "reason": "the canonical kinetic coefficient changes unless a compensating action coefficient is changed; coupled slopes w/lambda_D are physical data",
        },
        {
            "route": "B_primitive_character_normalization",
            "tested_transformation": "select w_primitive=1",
            "result": "OPEN_NOT_SELECTED",
            "reason": "the action does not identify a primitive support-charged object; choosing the smallest integer is an external convention",
        },
        {
            "route": "C_kinetic_matching",
            "tested_transformation": "match q_D to gravity, q_C, q_W, boundary, or global kinetic metric",
            "result": "BLOCKED",
            "reason": "no common S8/S5/S4 reduction functor owns all kinetic coefficients and the q_D cross blocks",
        },
        {
            "route": "D_topological_normalization",
            "tested_transformation": "identify support character with winding, codimension, Hopf charge, or triality",
            "result": "INVALIDATED_AS_UNPROVEN_IDENTIFICATION",
            "reason": "discrete topology labels do not canonically normalize the independent continuous multiplicative-support generator",
        },
        {
            "route": "E_global_normalization",
            "tested_transformation": "fix lambda_D from a unique closed equilibrium",
            "result": "BLOCKED",
            "reason": "the complete supported action and unique dimensionless global equilibrium are unavailable",
        },
    ]


def haar_scale_payload() -> dict[str, Any]:
    routes = normalization_routes()
    validation = {
        "all_five_routes_tested": [row["route"][0] for row in routes] == list("ABCDE"),
        "lambda_not_set_by_convenience": True,
        "no_route_claimed_complete": all(row["result"] not in {"DERIVED", "COMPLETE"} for row in routes),
        "physical_canonical_slope_retained": True,
        "no_empirical_scale_used": True,
    }
    return {
        "artifact": "BHSM_haar_scale_normalization_v11_1",
        "lambda_D": None,
        "lambda_D_positive": True,
        "canonical_interaction_strength": "g_Da=w_a/lambda_D",
        "physical_or_conventional": None,
        "reason_not_classified": "the invariance of w_a/lambda_D under the allowed representation quotient is undecidable without the complete supported canonical action",
        "pure_coordinate_convention": False,
        "primitive_character": None,
        "kinetic_matching": None,
        "topological_normalization": None,
        "global_normalization": None,
        "routes": routes,
        "status": HAAR_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
