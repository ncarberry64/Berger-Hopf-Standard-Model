from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
NAMES = (
    "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_CENTER_GRAPH_JACOBIAN",
    "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_MIDPOINT_GRAPH_JACOBIAN",
    "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR",
    "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE",
    "BHSM_N12_GATE7_SECOND_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY",
)


def _load(name: str) -> dict:
    return json.loads((BASE / f"{name}.json").read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_repaired_center_jacobians_and_predictor_validate() -> None:
    endpoint, midpoint, predictor, candidate, replay = map(_load, NAMES)
    assert all(record["validation_passed"] is True for record in (
        endpoint, midpoint, predictor, candidate,
    ))
    assert endpoint["summary"]["fine_nodes_through_stop"] == 371
    assert midpoint["summary"]["midpoint_count"] == 370
    assert endpoint["summary"]["selected_branches_seen"] == [24]
    assert midpoint["summary"]["minimum_selected_eigenline_gap"] > 1.0e-7
    assert predictor["summary"]["maximum_predicted_linearized_residual_2_norm"] < 1.0e-16
    assert candidate["summary"]["maximum_final_scaled_constraint_2_norm"] < 1.0e-14
    assert replay["validation_passed"] is False


def test_second_repaired_step_is_rejected_by_exact_nonlinear_replay() -> None:
    replay = _load(NAMES[-1])
    summary = replay["summary"]
    assert replay["status"] == "SECOND_RATE_CONSISTENT_NEWTON_STEP_DOES_NOT_REDUCE_NONLINEAR_RESIDUAL"
    assert summary["maximum_Hermite_Simpson_shooting_residual_2_norm"] == 1.429548198240663e-6
    assert summary["parent_maximum_Hermite_Simpson_shooting_residual_2_norm"] == 1.215762696655947e-6
    assert summary["nonlinear_block_residual_reduction_factor"] < 1.0
    assert replay["adjudication"]["second_rate_consistent_Newton_step"] == "REJECTED_BY_EXACT_NONLINEAR_REPLAY"
    assert replay["exact_next_dependency"].endswith(
        "DIFFERENTIATE_THE_COMPLETE_PROJECTED_RECENTERED_RESIDUAL_MAP"
    )
    assert replay["FULL_BHSM_COMPLETE"] is False


def test_second_rate_consistent_artifact_hashes_and_shapes() -> None:
    expected = {
        NAMES[0]: ("graph_Jacobian_action", (371, 98, 98)),
        NAMES[1]: ("graph_Jacobian_action", (370, 98, 98)),
        NAMES[2]: ("endpoint_state_correction_action", (371, 98)),
        NAMES[3]: ("projected_states", (371, 98)),
        NAMES[4]: ("Hermite_Simpson_shooting_residual", (370, 99)),
    }
    for name, (key, shape) in expected.items():
        record = _load(name)
        data = ROOT / record["data"]
        assert _sha256(data) == record["data_SHA256"]
        with np.load(data) as source:
            assert source[key].shape == shape
        for relative, digest in record["inputs"].items():
            assert _sha256(ROOT / relative) == digest
