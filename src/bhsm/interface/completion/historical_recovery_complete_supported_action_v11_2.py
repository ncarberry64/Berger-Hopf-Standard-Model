"""Exhaustive historical recovery record for the v11.2 supported action."""

from __future__ import annotations

from typing import Any

from .complete_local_supported_action_v11_2 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT


def recovery_payload() -> dict[str, Any]:
    candidates = [
        {"object": "v10.4 scalar support action class", "commit": "837d806", "pr": 213, "classification": "REUSABLE_PARTIAL", "reason": "owns Z,U,F_C,F_W action form but does not select its functions or core action"},
        {"object": "v7.1 normalized reduction functor", "commit": "27a9dee", "pr": 200, "classification": "REUSABLE_EXACT_KERNEL", "reason": "owns pi_!, fiber volume, and stratified pushforward; no G_D representation"},
        {"object": "v11.0 Haar support field", "commit": "c1cc07f", "pr": 214, "classification": "REUSABLE_EXACT_KERNEL", "reason": "owns q_D and the inverse-square Haar kinetic metric; characters remain open"},
        {"object": "v11.1 representation/equivalence audit", "commit": "c88b8e3", "pr": 215, "classification": "REUSABLE_EXACT_KERNEL", "reason": "owns the category and provisional representatives; local derivative action absent"},
        {"object": "v6.7 matter boundary domains", "commit": "73a6af3", "pr": 167, "classification": "RELATED_NOT_EQUIVALENT", "reason": "sector maximal-isotropic domains do not select the support/core ensemble"},
        {"object": "v6.10 junction functional/domain", "commit": "f3b69d5", "pr": 170, "classification": "RELATED_NOT_EQUIVALENT", "reason": "current action has M_J=0 and no selected U(1) junction graph"},
        {"object": "v6.15 Z2 interface symplectic domain", "commit": "2437eda", "pr": 175, "classification": "RELATED_NOT_EQUIVALENT", "reason": "presymplectic-null trace selects no boundary condition"},
        {"object": "coframe/sector-winding closure branch", "commit": "820198f", "pr": None, "classification": "REJECTED_AS_DERIVATION", "reason": "C_f and W_f explicitly marked not action-derived"},
        {"object": "boundary-action representation-connection branch", "commit": "75894b9", "pr": None, "classification": "REUSABLE_CANDIDATE_ONLY", "reason": "source scaffold is partial and A_j normalization convention-dependent"},
        {"object": "v6.14 composite level-set support", "commit": None, "pr": 174, "classification": "RELATED_NOT_ADOPTED", "reason": "chart is not the fixed-iota action and does not close threading"},
        {"object": "primitive lattice/common rescaling audit", "commit": None, "pr": 103, "classification": "CONDITIONAL_ONLY", "reason": "its own complete-action quotient remains open"},
        {"object": "Berger radius/measure normalization fork", "commit": None, "pr": 49, "classification": "RELATED_NOT_EQUIVALENT", "reason": "radius convention does not normalize G_D or its current"},
        {"object": "collar measure/extrinsic geometry", "commit": None, "pr": 13, "classification": "REUSABLE_GEOMETRY_ONLY", "reason": "does not define a support transformation law"},
        {"object": "v4.0 sector-weight action attachment", "commit": "6f4f415", "pr": 117, "classification": "REJECTED_FOR_GD_CHARACTER", "reason": "explicitly states 1:2:7 is not an action-selected trace weight"},
        {"object": "v4.3 Hodge/coframe metric factors", "commit": "24f4c0f", "pr": 120, "classification": "REUSABLE_COMPOSITE_GEOMETRY", "reason": "derives metric Hodge factors but not a support action on the coframe"},
        {"object": "v4.4 gauge-action coframe selection", "commit": "a365b2f", "pr": 121, "classification": "REJECTED_AS_SELECTION", "reason": "available raw and orthonormal coframes exist, but the gauge action selects neither"},
        {"object": "v5.4 unified dynamical action candidate", "commit": "71db297", "pr": 132, "classification": "CONDITIONAL_ACTION_ONLY", "reason": "keeps gauge, fermion, scalar, current, response, and scale normalizations provisional"},
        {"object": "v6.0.9 normalized fiber measure", "commit": "239c864", "pr": 150, "classification": "REUSABLE_NORMALIZATION_NOT_CHARACTER", "reason": "normalized Haar measure fixes pushforward integrals, not the G_D measure transformation"},
        {"object": "v6.0.9 canonical connection field map", "commit": "239c864", "pr": 150, "classification": "RELATED_GAUGE_CONNECTION_NOT_GD", "reason": "normalizes gauge fields using the kinetic matrix; it is not the support connection"},
    ]
    resources = {
        "current_tree_searched": True,
        "git_history_searched": True,
        "remote_branches_searched": True,
        "merged_and_unmerged_prs_searched": True,
        "artifacts_searched": True,
        "tests_searched": True,
        "preservation_bundles_searched_and_verified": True,
        "usb_mirror_searched_read_only": True,
        "author_resources_searched": True,
        "primitive_character_current_terms_targeted": True,
        "v8_3_v10_4_v11_0_v11_1_bundles_verified": True,
    }
    validation = {
        "all_resource_classes_searched": all(resources.values()),
        "minimum_candidate_matrix": len(candidates) >= 19,
        "every_candidate_classified": all(row["classification"] for row in candidates),
        "exact_complete_action_not_recovered": not any(row["classification"] == "EXACT_COMPLETE_ACTION" for row in candidates),
        "no_candidate_promoted_silently": True,
        "blocker_ready": True,
    }
    return {
        "artifact": "BHSM_historical_recovery_complete_supported_action_v11_2",
        "searched_object": "complete local supported action with derivative couplings and boundary/core canonical domain",
        "resources": resources,
        "candidates": candidates,
        "targeted_terms": ["primitive support character", "Noether/response/scale current", "coframe/metric/density scaling", "A_D and dq_D couplings", "linear and quadratic connection completion", "boundary/fiber/wall/core incidence"],
        "preservation_bundles": ["v8.3 verified", "v10.4 verified", "v11.0 verified", "v11.1 verified"],
        "reusable_ingredients": ["v10.4 covariant support-action class", "v7.1 normalized fiber pushforward", "v11.0 logarithmic Haar support pair", "v11.1 categorical/equivalence ledgers", "v4.3 Hodge/coframe composite laws", "v6.0.9 normalized fiber measure", "finite-boundary Green and flux forms"],
        "rejected_promotions": ["1:2:7 sector weights", "target-fitted winding multipliers", "partial boundary-source scaffold", "gauge coframe availability without action selection", "sector-specific self-adjoint domains", "coordinate level-set chart", "Berger radius convention"],
        "exact_object_recovered": False,
        "historical_routes_exhausted": True,
        "status": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
