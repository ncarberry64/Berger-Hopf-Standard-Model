import json
from pathlib import Path

import mpmath as mp

from bhsm.interface.analytic_weight_five_center_lift import (
    assemble_weight_five_lift,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ANALYTIC_LOCAL_BLOCK_CENTER_LIFT.json"
)


def test_analytic_local_block_lift_is_high_precision_and_sign_stable():
    result = assemble_weight_five_lift(points=48, decimal_digits=60)
    assert result["relative_residual"] < mp.mpf("1e-50")
    assert result["q0_coefficient"] > 0
    assert result["q0_rate_coefficient"] < 0


def test_independent_generic_jet_crosscheck_is_recorded_without_overpromotion():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    crosscheck = payload["independent_generic_98_variable_crosscheck"]
    assert mp.mpf(crosscheck["matrix_maximum_absolute_difference"]) < mp.mpf(
        "1e-60"
    )
    assert mp.mpf(crosscheck["source_maximum_absolute_difference"]) < mp.mpf(
        "1e-60"
    )
    assert mp.mpf(crosscheck["q0_absolute_difference"]) < mp.mpf("1e-60")
    assert mp.mpf(crosscheck["generic_relative_solve_residual"]) < mp.mpf(
        "1e-60"
    )
    assert crosscheck["directed_interval_certified"] is False
    assert payload["claim_boundary"]["uniform_full_remainder_outcome"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
