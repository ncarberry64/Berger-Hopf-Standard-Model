from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhsm.interface.action_extension_ae2_factorized_threshold import (
    factorized_constant_core_log_radius_weight,
    factorized_zero_resonance_weight_coefficient,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json"
)


def test_factorized_zero_resonance_has_superlinear_source_weight() -> None:
    exact = factorized_zero_resonance_weight_coefficient(2.0, 0.75)
    assert exact["strict_zero_energy_wronskian_margin"] == 0.0
    assert exact["zero_energy_core_end_value"] > 0.0
    assert exact["weight_over_momentum_squared_limit"] == pytest.approx(
        6.552579915052088
    )
    assert exact["cumulative_weight_over_Lambda_to_three_halves_limit"] > 0.0
    row = factorized_constant_core_log_radius_weight(2.0, 0.75, 1.0e-3)
    assert row["weight_over_momentum_squared"] == pytest.approx(
        exact["weight_over_momentum_squared_limit"], rel=3.0e-5
    )


def test_reclassification_artifact_preserves_claim_boundary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["strict_product_Dirac_Wronskian_required_in_advance"] is False
    assert payload["claim_boundary"]["factorized_N12_low_energy_source_measure"] == "OPEN"
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
