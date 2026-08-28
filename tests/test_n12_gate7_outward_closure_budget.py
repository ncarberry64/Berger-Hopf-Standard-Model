from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_GATE7_OUTWARD_CLOSURE_BUDGET.json"
DATA = RESULT.with_suffix(".npz")


def test_outward_budget_is_a_valid_conditional_theorem() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    thresholds = payload["summary"]["thresholds"]
    assert all(np.isfinite(value) and value > 0.0 for value in thresholds.values())
    assert payload["claim_boundary"]["causal_interval_vector_radius"].startswith("OPEN")


def test_outward_budget_data_preserve_causality_and_dimensions() -> None:
    with np.load(DATA) as source:
        vector = np.asarray(source["signed_center_vector"])
        green = np.asarray(source["causal_green_norm"])
        transverse = np.asarray(source["exact_transverse_curvature_Frobenius"])
    assert vector.shape == (48, 73)
    assert green.shape == (48, 48)
    assert transverse.shape == (48,)
    assert np.allclose(np.triu(green), 0.0, atol=0.0, rtol=0.0)
    assert np.all(np.isfinite(vector))
    assert np.all(transverse > 0.0)
