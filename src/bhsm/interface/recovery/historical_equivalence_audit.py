"""Fail-closed historical equivalence and blocker-readiness audit."""

from __future__ import annotations

from typing import Any

from .historical_object_search import recovery_question, search_ledger
from .provenance_matrix import support_representation_candidates


RECOVERY_VERDICT = "BHSM_HISTORICAL_RECOVERY_NARROWS_BUT_DOES_NOT_CLOSE_CURRENT_OBJECT"


def recovery_payload(object_name: str = "support representation functor") -> dict[str, Any]:
    searched = search_ledger()
    candidates = support_representation_candidates()
    checks = {
        "question_typed": bool(recovery_question(object_name)["defining_property"]),
        "synonyms_searched": len(recovery_question(object_name)["historical_synonyms"]) >= 16,
        "all_resource_classes_searched": all(value is True for key, value in searched.items() if key.endswith("_searched")),
        "bundles_verified": len(searched["preservation_bundles"]) == 3 and all(row["verified"] for row in searched["preservation_bundles"]),
        "provenance_matrix_present": len(candidates) >= 8,
        "every_candidate_classified": all(row["classification"] for row in candidates),
        "no_candidate_silently_promoted": not any(row["classification"] in {"EXACT_CURRENT_OBJECT", "MATHEMATICALLY_EQUIVALENT"} for row in candidates),
    }
    return {
        "artifact": "BHSM_historical_recovery_audit_support_representation_v11_1",
        "current_object": recovery_question(object_name),
        "resources_searched": searched,
        "provenance_matrix": candidates,
        "equivalence_reconstruction": {
            "1_2_7_to_support_character": "REJECTED: active-generator counts are sector screens, not GD characters",
            "coframe_winding_to_primitive_GD_action": "PARTIAL_ONLY: discrete incidence is not derived as the continuous support generator",
            "v7_1_reduction_to_support_functor": "PARTIAL_ONLY: geometric pushforward has no GD representation",
            "primitive_lattice_to_Haar_normalization": "CONDITIONAL_ONLY: its own action quotient gate is open",
            "boundary_measure_to_GD_measure_character": "PARTIAL_ONLY: normalized local measure does not define transformation under GD",
        },
        "reusable_historical_kernel": ["v10.4 supported derivative action class", "v7.1 normalized reduction maps", "exact finite incidence/projector ledgers"],
        "historical_routes_exhausted": True,
        "exact_current_object_recovered": False,
        "new_action_principle_created": False,
        "status": RECOVERY_VERDICT,
        "validation": checks,
        "validation_passed": all(checks.values()),
    }


def blocker_readiness_payload(object_name: str = "support representation functor") -> dict[str, Any]:
    recovery = recovery_payload(object_name)
    return {
        "object": object_name,
        "historical_recovery_complete": recovery["validation_passed"] and recovery["historical_routes_exhausted"],
        "blocker_may_be_emitted": recovery["validation_passed"] and recovery["historical_routes_exhausted"],
        "recovery_status": recovery["status"],
        "first_truly_missing_mathematical_object": "complete local supported action with support-gradient couplings and boundary/core canonical domain",
    }


def command_payload(command: str, object_name: str = "support representation functor") -> dict[str, Any]:
    if command == "historical-object-search":
        return {"question": recovery_question(object_name), "search": search_ledger()}
    if command == "historical-equivalence-audit":
        return recovery_payload(object_name)
    if command == "blocker-readiness-status":
        return blocker_readiness_payload(object_name)
    if command == "historical-recovery-status":
        return recovery_payload(object_name)
    raise ValueError(f"unknown recovery command: {command}")
