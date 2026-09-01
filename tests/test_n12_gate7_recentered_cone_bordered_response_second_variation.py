from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / (
    "certify_n12_gate7_recentered_cone_bordered_response_second_variation.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("gate7_second", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_recentered_second_variation_certificate_closes() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["mesh"] == {
        "parent_cells": 3009,
        "response_cells": 24072,
        "projection_dimension": 101,
    }
    assert all(payload["validation"].values())


def test_second_variation_claim_boundary_is_not_overpromoted() -> None:
    payload = _module().build_payload()
    boundary = payload["claim_boundary"]
    assert boundary[
        "recentered_cone_bordered_response_second_variation_majorant"
    ] == "CERTIFIED_FINITE"
    assert boundary["signed_common_frame_second_variation"] == "OPEN"
    assert boundary["projected_Cauchy_tail"] == "OPEN"
    assert boundary["causal_interval_vector_radius"] == "OPEN"
    assert boundary["domain_and_first_hit_transfer"] == "OPEN"
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False


def test_second_differentiated_identity_terms_are_positive_and_finite() -> None:
    payload = _module().build_payload()
    for row in payload["rows"]:
        assert row[
            "uniform_child_Hessian_second_coefficient_derivative_2_norm_upper"
        ] >= 0.0
        assert row[
            "uniform_child_selected_line_second_coefficient_derivative_2_norm_upper"
        ] >= 0.0
        assert row[
            "uniform_child_bordered_K_second_coefficient_derivative_2_norm_upper"
        ] >= 0.0
        assert row[
            "complete_bordered_response_second_coefficient_variation_2_to_2_upper"
        ] >= 0.0
        assert row["all_second_variation_quantities_finite"] is True


def test_second_response_owner_is_reproducible() -> None:
    payload = _module().build_payload()
    owner = payload["summary"]["owner"]
    assert owner["seam"] == 45
    assert owner["action_interval"] == [91.99609375, 92.0]
    assert owner["child_within_parent"] == 7
    assert payload["summary"][
        "maximum_complete_bordered_response_second_coefficient_variation_2_to_2_upper"
    ] == owner[
        "complete_bordered_response_second_coefficient_variation_2_to_2_upper"
    ]
