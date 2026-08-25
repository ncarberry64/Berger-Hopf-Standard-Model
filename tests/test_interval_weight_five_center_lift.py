import json
from fractions import Fraction
from pathlib import Path

import pytest


flint = pytest.importorskip("flint")

from bhsm.interface.interval_weight_five_center_lift import (  # noqa: E402
    assemble_interval_weight_five_lift,
    gauss_remainder_bound,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INTERVAL_WEIGHT_FIVE_CENTER_LIFT.json"
)


def test_exact_gauss_remainder_is_below_required_margin():
    remainder = gauss_remainder_bound(128)
    assert isinstance(remainder, Fraction)
    assert remainder > 0
    assert remainder < Fraction(1, 10**100)


def test_arb_center_lift_has_strict_signs_and_verified_residual():
    result = assemble_interval_weight_five_lift(
        points=128, decimal_digits=120
    )
    assert result["residual_contains_zero"] is True
    assert result["q0_strictly_positive"] is True
    assert result["q0_rate_strictly_negative"] is True
    assert result["q0_coefficient"].rel_accuracy_bits() >= 250
    assert result["q0_rate_coefficient"].rel_accuracy_bits() >= 250
    assert result["combined_Euler_Dirac_inverse_used"] is False


def test_interval_artifact_preserves_claim_boundary():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["common_scale_interval"]["strictly_positive"] is True
    assert payload["common_scale_rate_interval"]["strictly_negative"] is True
    assert len(payload["complete_leading_modulation_vector"]) == 74
    assert payload["claim_boundary"]["uniform_full_remainder_outcome"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False
