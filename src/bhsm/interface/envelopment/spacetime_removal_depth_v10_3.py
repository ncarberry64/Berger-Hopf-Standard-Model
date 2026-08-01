"""Gauge-invariant spacetime-removal/depth candidate audit."""

from __future__ import annotations

from typing import Any


DEPTH_VERDICT = "BHSM_SPACETIME_REMOVAL_DEPTH_REQUIRES_A_NEW_ACTION_OWNED_DEGREE"


def candidate_rows() -> list[dict[str, Any]]:
    return [
        {"candidate": "-log(sqrt|G|_local/sqrt|G|_background)", "gauge_invariant": "only after a relational point-identification map", "canonically_normalized": False, "background_zero": True, "monotonic_removal": "unproved", "action_owned_degree": False, "distinct_from_q_C": "unproved", "fatal_reason": "density ratio needs a common relational map and may only repackage metric breathing"},
        {"candidate": "R_ABCD R^ABCD concentration", "gauge_invariant": True, "canonically_normalized": False, "background_zero": False, "monotonic_removal": False, "action_owned_degree": False, "distinct_from_q_C": True, "fatal_reason": "curvature concentration is not an action-selected removal coordinate"},
        {"candidate": "T_AB n^A n^B", "gauge_invariant": "conditional on common tensor and normal", "canonically_normalized": False, "background_zero": "model dependent", "monotonic_removal": False, "action_owned_degree": False, "distinct_from_q_C": True, "fatal_reason": "stress projection is a source, and the common stress tensor is absent"},
        {"candidate": "K_mu_nu K^mu_nu or K^2", "gauge_invariant": "boundary-covariant after support/normal selection", "canonically_normalized": False, "background_zero": False, "monotonic_removal": False, "action_owned_degree": False, "distinct_from_q_C": True, "fatal_reason": "extrinsic concentration is not a canonical depth degree"},
        {"candidate": "fiber-volume deficit -3 delta beta", "gauge_invariant": "within the invariant bundle reduction", "canonically_normalized": True, "background_zero": True, "monotonic_removal": "only fiber volume", "action_owned_degree": True, "distinct_from_q_C": False, "fatal_reason": "identical to the core/Hopf amplitude, forbidden as the third slot"},
        {"candidate": "lapse degeneration", "gauge_invariant": False, "canonically_normalized": False, "background_zero": False, "monotonic_removal": False, "action_owned_degree": False, "distinct_from_q_C": True, "fatal_reason": "lapse is a gauge/constraint multiplier"},
        {"candidate": "normalized effective-support loss", "gauge_invariant": "target property only", "canonically_normalized": False, "background_zero": True, "monotonic_removal": "target property only", "action_owned_degree": False, "distinct_from_q_C": True, "fatal_reason": "no action-selected support functional or measure comparison"},
    ]


def depth_payload() -> dict[str, Any]:
    rows = candidate_rows()
    selected = [row for row in rows if all(row[key] is True for key in ("gauge_invariant", "canonically_normalized", "background_zero", "monotonic_removal", "action_owned_degree", "distinct_from_q_C"))]
    validation = {
        "requested_candidates_audited": len(rows) == 7,
        "no_candidate_selected": selected == [],
        "lapse_rejected_as_coordinate": rows[5]["gauge_invariant"] is False,
        "fiber_deficit_not_duplicated": rows[4]["distinct_from_q_C"] is False,
        "curvature_not_called_removal": rows[1]["monotonic_removal"] is False,
    }
    return {
        "artifact": "BHSM_spacetime_removal_depth_gate_v10_3",
        "author_definition": "gauge-invariant spacetime support removal/compression relative to the selected global background",
        "candidate_audit": rows,
        "selected_depth_functional": None,
        "physical_depth_value": None,
        "action_source": None,
        "canonical_momentum": None,
        "verdict": DEPTH_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
