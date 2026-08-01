"""Cosmic unit-anchor eligibility gate for BHSM v10.4."""

from __future__ import annotations

from typing import Any


ANCHOR_VERDICT = "BHSM_COSMIC_UNIT_ANCHOR_INELIGIBLE_BEFORE_GLOBAL_ACTION_OBSERVABLE_IS_SELECTED"


def cosmic_anchor_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_cosmic_unit_anchor_v10_4",
        "author_policy": "at most one action-owned cosmological observable may set units; particle calibration is forbidden",
        "dimensionless_global_geometry_derived": False,
        "eligible_action_owned_global_observables": [],
        "selected_anchor": None,
        "anchor_value": None,
        "anchor_uncertainty": None,
        "unit_map": None,
        "maximum_anchor_count": 1,
        "anchor_count_used": 0,
        "particle_inputs_used": [],
        "dimensionless_predictions_changed": False,
        "absolute_scale": None,
        "verdict": ANCHOR_VERDICT,
        "validation_passed": True,
    }
