from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_SELECTED_MULTIPLIER_JETS.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_exact_signed_multiplier_certificate_closes() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["identity"]["selected_branch"] == 24
    assert len(payload["rows"]) == 48


def test_signed_cancellation_is_retained() -> None:
    payload = _payload()
    assert payload["summary"]["maximum_multiplier_first_variation_absolute"] < 1.0e-3
    assert payload["summary"]["maximum_multiplier_second_variation_absolute"] < 1.0e-2
    assert payload["validation"]["signed_terms_summed_before_absolute_value"]
    assert payload["validation"]["no_bordered_response_norm_used_in_multiplier_bound"]


def test_saved_signed_jets_are_finite_and_match_rows() -> None:
    payload = _payload()
    with np.load(DATA) as source:
        first = np.asarray(
            source["selected_multiplier_correction_direction_first_variation"]
        )
        second = np.asarray(
            source["selected_multiplier_correction_direction_second_variation"]
        )
    assert first.shape == (48,)
    assert second.shape == (48,)
    assert np.all(np.isfinite(first))
    assert np.all(np.isfinite(second))
    np.testing.assert_allclose(
        first,
        [row["multiplier_first_variation"] for row in payload["rows"]],
        rtol=0.0,
        atol=0.0,
    )


def test_claim_boundary_remains_exact() -> None:
    boundary = _payload()["claim_boundary"]
    assert boundary["retained_center_selected_multiplier_signed_second_jet"] == "DERIVED"
    assert boundary["outward_selected_multiplier_interval_tube"] == "OPEN"
    assert boundary["normalized_numerator_signed_product_tube"] == "OPEN"
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False
