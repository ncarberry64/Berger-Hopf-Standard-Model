from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_exact_directional_curvature_certificate_closes() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert len(payload["rows"]) == 48


def test_exact_directional_curvature_is_finite() -> None:
    payload = _payload()
    assert np.isfinite(payload["summary"]["maximum_directional_curvature_2_norm"])
    with np.load(DATA) as source:
        directional = np.asarray(
            source["physical_time_transverse_directional_curvature"]
        )
    assert directional.shape == (48, 72)
    assert np.all(np.isfinite(directional))


def test_no_forbidden_inverse_or_derivative_authority() -> None:
    validation = _payload()["validation"]
    assert validation["no_ambient_Hessian_second_matrix_or_response_tensor_formed"]
    assert validation["no_JAX_derivative_used_as_action_authority"]
    assert validation["no_kinetic_Dirac_or_history_inverse_formed"]


def test_claim_boundary_remains_exact() -> None:
    boundary = _payload()["claim_boundary"]
    assert boundary["physical_transverse_Green_direction_center_curvature"] == "DERIVED"
    assert boundary["outward_directional_curvature_remainder"] == "OPEN"
    assert boundary["mixed_Green_transverse_curvature"] == "OPEN"
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False
