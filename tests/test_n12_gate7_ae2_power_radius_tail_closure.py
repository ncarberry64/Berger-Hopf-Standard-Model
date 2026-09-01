from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_sublinear_radius_tail import (
    power_radius_tail_class,
    sublinear_positive_chirality_agmon_action,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_power_radius_tail_closure.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json"


@pytest.mark.parametrize("power", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 3.0])
def test_every_nonnegative_power_tail_is_classified_and_integrable(power: float) -> None:
    assert power_radius_tail_class(power)["factorized_E1_threshold_integrable"] is True


def test_sublinear_agmon_action_grows_and_suppression_beats_powers() -> None:
    coarse = sublinear_positive_chirality_agmon_action(1.5, 0.5, 1.0e-2)
    fine = sublinear_positive_chirality_agmon_action(1.5, 0.5, 3.0e-4)
    assert fine["agmon_action_lower"] > coarse["agmon_action_lower"]
    assert fine["squared_amplitude_suppression_upper"] < 3.0e-4 ** 16


def test_invalid_sublinear_inputs_fail() -> None:
    with pytest.raises(ValueError):
        sublinear_positive_chirality_agmon_action(1.0, 1.0, 0.1)
    with pytest.raises(ValueError):
        power_radius_tail_class(-0.1)


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["all_exact_nonnegative_power_radius_tails"] == "CLOSED"
    assert payload["claim_boundary"]["actual_N12_radius_asymptotic_class"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
