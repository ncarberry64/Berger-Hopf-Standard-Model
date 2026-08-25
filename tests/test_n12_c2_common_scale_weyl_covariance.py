from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"


def test_common_scale_weyl_covariance_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["physical_common_scale_geometry_pullback"] == "CLOSED"
    assert payload["adjudication"]["moving_duration_contribution"] == "INCLUDED_EXACTLY"
    assert payload["adjudication"]["non_scale_reset_quotient_geometry_pullback"] == "OPEN"
    assert Decimal(payload["maximum_relative_residual_decimal"]) <= Decimal("1e-70")
    assert len(payload["sampled_arbitrary_precision_crosschecks"]) == 18
    for row in payload["sampled_arbitrary_precision_crosschecks"]:
        assert Decimal(row["relative_residual_decimal"]) <= Decimal("1e-70")
