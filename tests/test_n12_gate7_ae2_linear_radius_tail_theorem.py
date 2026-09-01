from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_linear_radius_tail import (
    linear_radius_tail_compact_source_weight,
    linear_radius_tail_delta_state,
    linear_radius_tail_source_law,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_linear_radius_tail_theorem.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json"


@pytest.mark.parametrize(
    ("beta", "chirality", "power", "cumulative"),
    [(0.25, 1, 1.5, 1.25), (0.75, 1, 1.5, 1.25), (1.25, 1, 2.5, 1.75), (0.75, -1, 3.5, 2.25)],
)
def test_exact_power_classes(beta: float, chirality: int, power: float, cumulative: float) -> None:
    law = linear_radius_tail_source_law(beta, chirality)
    assert law["power_exponent"] == pytest.approx(power)
    assert law["cumulative_Lambda_exponent"] == pytest.approx(cumulative)
    assert law["E1_threshold_integrable"] is True


def test_critical_half_is_log_Dini_not_divergent() -> None:
    law = linear_radius_tail_source_law(0.5, 1)
    assert law["critical_log_Dini_case"] is True
    assert law["cumulative_source_measure_law"] == "O(Lambda/abs(log(Lambda))^2)"
    assert law["E1_threshold_integrable"] is True


def test_natural_factorized_graph_is_satisfied() -> None:
    _, factor_image = linear_radius_tail_delta_state(0.75, 1, 1.0e-3, 1.0)
    assert abs(factor_image) < 1.0e-14


def test_numerical_source_weight_has_predicted_slope() -> None:
    first = linear_radius_tail_compact_source_weight(1.25, 1, 1.0e-3)
    second = linear_radius_tail_compact_source_weight(1.25, 1, 1.0e-4)
    slope = __import__("math").log(second / first) / __import__("math").log(0.1)
    assert slope == pytest.approx(2.5, abs=1.0e-3)


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["exact_linear_radius_tail_theorem"] == "CLOSED"
    assert payload["claim_boundary"]["actual_N12_radius_asymptotic_class"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
