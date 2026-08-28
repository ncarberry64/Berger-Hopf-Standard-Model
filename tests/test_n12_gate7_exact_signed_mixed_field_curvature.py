from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_exact_mixed_curvature_certificate_closes() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["summary"]["evaluated_nodes"] == 48
    assert len(payload["rows"]) == 48


def test_mixed_maps_are_finite_and_have_the_physical_shape() -> None:
    with np.load(DATA) as source:
        mixed = np.asarray(
            source["physical_time_transverse_mixed_Green_curvature"]
        )
        nodes = np.asarray(source["node_indices"])
    assert mixed.shape == (48, 72, 72)
    assert np.array_equal(nodes, np.arange(48))
    assert np.all(np.isfinite(mixed))


def test_signed_owner_and_reconnaissance_crosscheck() -> None:
    summary = _payload()["summary"]
    assert summary["mixed_curvature_owner_node"] == 1
    assert summary["maximum_mixed_curvature_operator_2_norm"] < 181.0
    assert summary["maximum_prior_JAX_mixed_operator_relative_difference"] < 1.0e-4


def test_no_forbidden_tensor_or_inverse() -> None:
    validation = _payload()["validation"]
    assert validation["signed_action_contractions_combined_before_operator_norm"]
    assert validation["no_full_response_Hessian_tensor_formed"]
    assert validation["no_JAX_derivative_used_as_action_authority"]
    assert validation["no_kinetic_Dirac_or_history_inverse_formed"]


def test_claim_boundary_remains_exact() -> None:
    boundary = _payload()["claim_boundary"]
    assert boundary["physical_transverse_Green_mixed_center_curvature"] == "DERIVED"
    assert boundary["outward_mixed_curvature_remainder"] == "OPEN"
    assert boundary["full_transverse_curvature"] == "OPEN"
    assert boundary["Gate7"] == "ACTIVE"
    assert boundary["FULL_BHSM_COMPLETE"] is False
