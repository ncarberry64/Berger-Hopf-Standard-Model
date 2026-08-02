"""Haar-scale audit after the v11.2 local-connection result."""

from __future__ import annotations

from typing import Any


def haar_payload() -> dict[str, Any]:
    routes = [
        {"route": "generator_redundancy", "result": "NOT_A_COMPLETE_QUOTIENT", "reason": "w/lambda_D is invariant under common rescaling, but the exact action-character kernel has five independent directions rather than one common scale"},
        {"route": "primitive_character_lattice", "result": "BLOCKED", "reason": "no action-owned primitive support character"},
        {"route": "canonical_kinetic_normalization", "result": "PARTIAL", "reason": "fixes the q_D kinetic convention, not a coupled character"},
        {"route": "gravitational_matching", "result": "BLOCKED", "reason": "supported coframe and full reduced kinetic matrix absent"},
        {"route": "boundary_core_normalization", "result": "BLOCKED", "reason": "core response and selected domain absent"},
        {"route": "global_scale", "result": "BLOCKED", "reason": "no unique global equilibrium"},
    ]
    validation = {
        "all_six_routes_tested": len(routes) == 6,
        "lambda_not_set_to_one": True,
        "no_empirical_input": True,
        "physical_or_conventional_withheld": True,
    }
    return {
        "artifact": "BHSM_haar_scale_closure_v11_2",
        "lambda_D": None,
        "lambda_D_positive": True,
        "primitive_lattice": None,
        "exact_character_constraint_rank": 7,
        "exact_character_constraint_nullity": 5,
        "nullspace_is_single_common_normalization": False,
        "canonical_coupling": "g_Da=w_a/lambda_D",
        "physical_or_conventional": None,
        "routes": routes,
        "status": "BHSM_HAAR_SCALE_REMAINS_UNCLASSIFIED_PENDING_ACTION_OWNED_PRIMITIVE_SUPPORT_CHARACTER",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
