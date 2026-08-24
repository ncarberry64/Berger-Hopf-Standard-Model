from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_factorized_source_measure import (
    integrable_reciprocal_radius_normalization,
    reciprocal_radius_integral_from_power_growth,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_integrable_radius_threshold_route.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json"


def test_power_growth_integrates_reciprocal_radius() -> None:
    result = reciprocal_radius_integral_from_power_growth(2.0, 3.0, 0.5)
    assert result["reciprocal_radius_integral_upper"] == 3.0


def test_two_chirality_normalization_sum() -> None:
    result = integrable_reciprocal_radius_normalization(1.5, 0.25, 2, 2)
    expected = 4 * (4.0 / math.pi) * math.cosh(0.75)
    assert result["uniform_near_threshold_normalization_squared_sum_upper"] == pytest.approx(expected)


def test_invalid_growth_or_normalization_inputs_fail() -> None:
    with pytest.raises(ValueError):
        reciprocal_radius_integral_from_power_growth(1.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        integrable_reciprocal_radius_normalization(1.0, math.inf)


def test_artifact_is_validated_deterministic_and_keeps_actual_route_open() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["conditional_integrable_radius_threshold_theorem"] == "CLOSED"
    assert payload["claim_boundary"]["actual_N12_reciprocal_radius_integrability"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
