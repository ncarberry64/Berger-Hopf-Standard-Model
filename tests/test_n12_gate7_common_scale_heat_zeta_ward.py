from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"


def test_common_scale_heat_zeta_ward_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["common_scale_source_contraction_formula"] == "CLOSED"
    assert payload["adjudication"]["common_scale_zeta_moving_duration_completion"] == "CLOSED_ZERO"
    assert payload["adjudication"]["actual_common_scale_numeric_force"].startswith("OPEN")
    assert payload["witness"]["heat_absolute_residual"] < 1.0e-9
    assert payload["witness"]["zeta_absolute_residual"] < 1.0e-12
