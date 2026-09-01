"""Checks for the recentered-cone complete response first variation."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RESPONSE_FIRST_VARIATION.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_complete_response_first_variation_is_finite_on_exact_cover() -> None:
    payload = _load(RESULT)
    rows = payload["rows"]
    assert payload["validation_passed"] is True
    assert payload["mesh"] == {
        "parent_cells": 3009,
        "projection_dimension": 101,
        "response_cells": 24072,
    }
    assert len(rows) == 24072
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["projection_dimension"] == 101 for row in rows)
    assert all(row["all_variation_quantities_finite"] for row in rows)
    assert all(
        math.isfinite(
            row[
                "complete_bordered_response_first_coefficient_variation_2_to_2_upper"
            ]
        )
        for row in rows
    )


def test_common_frame_generalized_metric_lift_is_exact_and_small() -> None:
    payload = _load(RESULT)
    for row in payload["rows"]:
        lift = row[
            "child_to_parent_common_frame_direction_lift_2_norm_upper"
        ]
        generalized = row[
            "child_to_parent_generalized_metric_eigenvalue_upper"
        ]
        assert lift >= 1.0
        assert generalized >= 1.0
        assert lift * lift >= generalized
        assert lift <= 1.002
    assert payload["summary"][
        "maximum_child_to_parent_direction_lift_2_norm_upper"
    ] == max(
        row["child_to_parent_common_frame_direction_lift_2_norm_upper"]
        for row in payload["rows"]
    )
    assert payload["summary"][
        "maximum_child_to_parent_direction_lift_2_norm_upper"
    ] <= 1.002


def test_closed_system_reverse_adjoint_claim_boundary() -> None:
    payload = _load(RESULT)
    validation = payload["validation"]
    assert validation[
        "complete_differentiated_bordered_identity_assembled_before_norms"
    ] is True
    assert validation[
        "only_external_Cauchy_birth_source_zero_internal_variation_retained"
    ] is True
    assert validation["no_added_seam_force_or_double_counted_response"] is True
    assert validation["no_full_kinetic_Dirac_or_history_inverse_used"] is True
    assert payload["claim_boundary"][
        "maximal_graded_internal_source_cotangent"
    ] == "CERTIFIED_FINITE"
    assert payload["claim_boundary"][
        "reverse_adjoint_complete_response"
    ] == "CERTIFIED_FINITE"
    assert payload["claim_boundary"][
        "recentered_cone_response_first_variation_tube"
    ] == "CERTIFIED_FINITE"
    assert payload["claim_boundary"]["projected_Cauchy_tail"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_first_variation_input_hashes_match_disk() -> None:
    payload = _load(RESULT)
    for relative, expected in payload["inputs"].items():
        assert _sha256(ROOT / relative) == expected
