from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.maximal_history_endpoint_jets import moving_endpoint_jets


SCRIPT = ROOT / "scripts/derive_n12_reset_stratum_moving_endpoint_jets.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_analytic_moving_endpoint_witness() -> None:
    payload = _payload()
    witness = payload["witness"]
    assert payload["validation_passed"] is True
    assert witness["maximum_time_jet_residual"] < 1.0e-14
    assert witness["maximum_endpoint_state_jet"] < 1.0e-14
    assert witness["maximum_endpoint_observable_jet"] < 1.0e-14


def test_time_translation_is_intrinsically_quotiented_at_endpoint() -> None:
    payload = _payload()
    witness = payload["witness"]
    assert witness["time_shift_first_endpoint_norm"] < 1.0e-14
    assert witness["time_shift_mixed_endpoint_norm"] < 1.0e-14
    assert abs(witness["time_shift_time_mixed"]) < 1.0e-14
    assert payload["claim_boundary"]["actual_maximal_history"] == "OPEN"


def test_nontransverse_event_is_rejected() -> None:
    with pytest.raises(ValueError, match="transverse event margin"):
        moving_endpoint_jets(
            np.array([0.0]),
            np.array([[1.0]]),
            np.array([1.0]),
            np.array([[0.0]]),
            np.array([1.0]),
            np.array([1.0]),
            np.array([0.0]),
        )
