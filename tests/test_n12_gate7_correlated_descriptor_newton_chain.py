from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
ENDPOINT = "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE"
REPLAY = "BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY"
REPRODUCIBILITY = "BHSM_N12_GATE7_BINARY64_DESCRIPTOR_RESELECTION_REPRODUCIBILITY_AUDIT"


def _load(name: str) -> dict:
    return json.loads((BASE / f"{name}.json").read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_correlated_descriptor_endpoint_replay_is_self_consistent() -> None:
    record = _load(ENDPOINT)
    assert record["validation_passed"] is True
    assert record["validation"]["descriptor_carried_by_correlated_first_jet_not_binary_eigensolve"] is True
    assert record["validation"]["no_pre_stop_descriptor_required_negative_clipping"] is True
    assert record["summary"]["minimum_transported_unclipped_descriptor"] > 0.0
    assert record["summary"]["maximum_final_scaled_constraint_2_norm"] < 2.0e-14
    assert record["claim_boundary"]["binary64_selected_eigenvalue"] == "DIAGNOSTIC_ONLY_NOT_DESCRIPTOR_AUTHORITY"


def test_correlated_descriptor_step_contracts_global_nonlinear_residual() -> None:
    record = _load(REPLAY)
    summary = record["summary"]
    assert record["validation_passed"] is True
    assert record["status"] == "CORRELATED_DESCRIPTOR_STEP_REDUCES_NONLINEAR_RESIDUAL"
    assert summary["maximum_Hermite_Simpson_shooting_residual_2_norm"] == 1.3706618261694602e-7
    assert summary["maximum_Hermite_Simpson_shooting_residual_owner_interval"] == 330
    assert summary["nonlinear_block_residual_reduction_factor"] == 8.869895355979933
    assert record["adjudication"]["binary64_reselected_second_step"] == "REJECTED_AND_NONAUTHORITATIVE"
    assert record["FULL_BHSM_COMPLETE"] is False


def test_binary64_descriptor_reselection_is_diagnostic_only() -> None:
    record = _load(REPRODUCIBILITY)
    assert record["validation_passed"] is True
    assert record["summary"]["maximum_state_absolute_difference"] < 2.0e-15
    assert record["summary"]["maximum_selected_eigenvalue_absolute_difference"] == 1.2223675212758834e-13
    assert record["summary"]["maximum_normalized_rate_2_norm_difference"] == 6.153628305085485e-6
    assert record["adjudication"]["binary64_selected_eigenvalue"] == "DIAGNOSTIC_ONLY"


def test_correlated_descriptor_artifact_hashes_and_shapes() -> None:
    expected = {
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
