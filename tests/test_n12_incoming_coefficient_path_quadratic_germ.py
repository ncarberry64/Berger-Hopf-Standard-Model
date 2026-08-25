from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_forward_boundary_radius import (
    normalized_incoming_log_radius_quadratic_germ,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_INCOMING_COEFFICIENT_PATH_QUADRATIC_GERM.json"


def test_normalized_path_germ_interval_orientation() -> None:
    result = normalized_incoming_log_radius_quadratic_germ(
        np.asarray([0.0, 0.5, 1.0]),
        terminal_log_radius=-0.1,
        terminal_proper_rate_interval=(2.0, 3.0),
        duration_quadratic_coefficient_interval=(5.0, 7.0),
    )
    x = np.asarray(result["log_radius_lambda0_squared_coefficient_interval"])
    scalar = np.asarray(
        result["scalar_relative_potential_lambda0_squared_coefficient_interval"]
    )
    dirac = np.asarray(
        result["dirac_relative_superpotential_lambda0_squared_coefficient_interval"]
    )
    assert np.array_equal(x[0], np.asarray([-21.0, -10.0]))
    assert np.array_equal(x[-1], np.zeros(2))
    assert np.array_equal(scalar[0], np.asarray([20.0, 42.0]))
    assert np.array_equal(dirac[0], np.asarray([10.0, 21.0]))
    assert result["explicit_Euler_Dirac_inverse_formed"] is False
    assert result["acceleration_required"] is False


def test_incoming_path_germ_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["incoming_normalized_log_radius_path_germ"].startswith("CERTIFIED")
    assert payload["claim_boundary"]["complete_finite_positive_amplitude_path"].startswith("OPEN")
    assert payload["claim_boundary"]["sharp_joint_seam_and_full_graded_trace"] == "OPEN"
