"""Shared constants for the BHSM v7.0 unified-action audit."""

from __future__ import annotations

import json
from typing import Any


VERSION = "v7.0"
SPRINT = "bhsm-complete-unified-parent-action-v7-0"
SOURCE_MAIN_SHA = "c7abad29688839add1ab06480b0a284c442d6a70"
VERDICT = (
    "BHSM_UNIFIED_PARENT_ACTION_BLOCKED_BY_MISSING_"
    "COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR_SOURCE"
)
MISSING_OBJECT = "COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR"

FROZEN_HASHES = {
    "docs/frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    "docs/frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}

COEFFICIENT_TYPES = {
    "ACTION_DERIVED",
    "GEOMETRICALLY_DERIVED",
    "REPRESENTATION_DERIVED",
    "INDEPENDENT_THEORY_INPUT",
    "ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION",
    "UNLICENSED_ORIGIN_BLOCKER",
    "REMOVED_AS_REDUNDANT",
    "REJECTED_AS_INCOMPATIBLE",
}

GUARDS = {
    "frozen_prediction_changed": False,
    "official_prediction_changed": False,
    "comparison_data_used_in_action": False,
    "fitted_parameter_used": False,
    "lambda5_value_selected": False,
    "lambda5_sign_selected": False,
    "physical_scale_claimed": False,
    "physical_mass_claimed": False,
    "unconditional_stability_claimed": False,
    "quantum_completion_claimed": False,
    "unified_parent_action_claimed_closed": False,
    "bhsm_1_0_release_complete_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def envelope(artifact: str, **body: Any) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        **body,
        **GUARDS,
    }
