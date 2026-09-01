from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
JACOBIAN = "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS"
PREDICTOR = "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR"
ENDPOINT = "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE"
REPLAY = "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY"


def _load(name: str) -> dict:
    return json.loads((BASE / f"{name}.json").read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_augmented_jacobians_use_retained_exact_field_normalization() -> None:
    record = _load(JACOBIAN)
    summary = record["summary"]
    assert record["validation_passed"] is True
    assert record["validation"]["all_graph_normalizations_use_retained_exact_cancelled_fields"] is True
    assert summary["maximum_stored_vs_replayed_exact_augmented_rate_2_norm"] == 0.0
    assert summary["maximum_predictor_vs_retained_cancelled_norm_absolute_mismatch"] > 1.0e-9
    assert summary["minimum_selected_eigenline_gap"] > 1.7e-7


def test_corrected_74d_recurrence_is_well_conditioned_numerically() -> None:
    record = _load(PREDICTOR)
    summary = record["summary"]
    assert record["validation_passed"] is True
    assert summary["maximum_reduced_right_block_condition_2"] < 100.0
    assert summary["maximum_predicted_reduced_residual_2_norm"] < 4.0e-19
    assert summary["minimum_predicted_descriptor"] > 0.0
    assert record["claim_boundary"]["continuous_interval_shadowing"] == "OPEN"


def test_endpoint_candidate_persists_regular_exact_flow_norm_jets() -> None:
    record = _load(ENDPOINT)
    assert record["validation_passed"] is True
    assert record["parameterization"]["stored_abscissa"] == "NORMALIZED_CANCELLED_FIELD_ARC_COLLOCATION_PARAMETER"
    assert max(row["norm_realization_absolute_residual"] for row in record["rows"]) == 0.0
    assert record["summary"]["minimum_independent_signed_descriptor"] > 0.0
    with np.load(BASE / f"{ENDPOINT}.npz") as source:
        assert source["cancelled_field_action_norm"].shape == (371,)
        assert source["cancelled_norm_state_gradient_action"].shape == (371, 98)
        assert source["cancelled_norm_descriptor_derivative"].shape == (371,)
        assert source["endpoint_constraint_tangent_action"].shape == (371, 98, 73)


def test_one_corrected_nonlinear_replay_contracts_and_then_freezes_center() -> None:
    record = _load(REPLAY)
    summary = record["summary"]
    assert record["validation_passed"] is True
    assert record["status"] == "AUGMENTED_FIXED_DESCRIPTOR_STEP_REDUCES_NONLINEAR_RESIDUAL"
    assert summary["maximum_Hermite_Simpson_shooting_residual_2_norm"] == 1.2217621999603292e-7
    assert summary["maximum_Hermite_Simpson_shooting_residual_owner_interval"] == 330
    assert summary["nonlinear_block_residual_reduction_factor"] == 1.121872837622547
    assert summary["maximum_descriptor_shooting_residual_absolute"] < 1.7e-16
    assert record["FULL_BHSM_COMPLETE"] is False


def test_augmented_chain_artifact_hashes_and_shapes() -> None:
    expected = {
        JACOBIAN: ("endpoint_augmented_Jacobian_action", (371, 99, 99)),
        PREDICTOR: ("endpoint_augmented_correction_action", (371, 99)),
        ENDPOINT: ("projected_states", (371, 98)),
        REPLAY: ("Hermite_Simpson_shooting_residual", (370, 99)),
    }
    for name, (key, shape) in expected.items():
        record = _load(name)
        data = ROOT / record["data"]
        assert _sha256(data) == record["data_SHA256"]
        with np.load(data) as source:
            assert source[key].shape == shape
        for relative, digest in record["inputs"].items():
            assert _sha256(ROOT / relative) == digest
