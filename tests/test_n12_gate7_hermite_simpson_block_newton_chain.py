from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / f"{name}.json").read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_historical_mixed_rate_step_and_stored_derivative_are_superseded() -> None:
    midpoint = _load("BHSM_N12_GATE7_HERMITE_SIMPSON_MIDPOINT_GRAPH_JACOBIAN")
    predictor = _load("BHSM_N12_GATE7_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR")
    endpoint = _load("BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE")
    source = _load("BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE")
    full = _load("BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_NEWTON_MIDPOINT_REPLAY")
    damped = _load("BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_MIDPOINT_REPLAY")
    trust = _load("BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_MIDPOINT_REPLAY")
    verdict = _load("BHSM_N12_GATE7_HERMITE_SIMPSON_PROJECTED_RESIDUAL_JACOBIAN_ADJUDICATION")
    repair = _load("BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS")
    assert midpoint["validation_passed"] is True
    assert predictor["validation_passed"] is True
    assert endpoint["validation_passed"] is True
    assert source["validation_passed"] is True
    assert source["summary"]["nonlinear_block_residual_reduction_factor"] > 2.0
    assert repair["adjudication"]["stored_pre_recenter_endpoint_rates"].startswith("SUPERSEDED")
    assert full["validation_passed"] is False
    assert damped["validation_passed"] is False
    assert trust["validation_passed"] is False
    assert verdict["validation_passed"] is True
    assert verdict["adjudication"]["hybrid_graph_Jacobian_as_complete_block_derivative"] == "REJECTED"
    assert verdict["FULL_BHSM_COMPLETE"] is False


def test_block_newton_chain_data_hashes_and_shapes() -> None:
    shapes = {
        "BHSM_N12_GATE7_HERMITE_SIMPSON_MIDPOINT_GRAPH_JACOBIAN": ("graph_Jacobian_action", (370, 98, 98)),
        "BHSM_N12_GATE7_HERMITE_SIMPSON_BLOCK_NEWTON_PREDICTOR": ("endpoint_state_correction_action", (371, 98)),
        "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_ENDPOINT_CANDIDATE": ("projected_states", (371, 98)),
        "BHSM_N12_GATE7_HERMITE_SIMPSON_NEWTON_NONLINEAR_SOURCE": ("Hermite_Simpson_shooting_residual", (370, 99)),
        "BHSM_N12_GATE7_SECOND_HERMITE_SIMPSON_NEWTON_MIDPOINT_REPLAY": ("exact_midpoint_rates", (370, 99)),
        "BHSM_N12_GATE7_DAMPED_SECOND_HS_NEWTON_MIDPOINT_REPLAY": ("exact_midpoint_rates", (370, 99)),
        "BHSM_N12_GATE7_LOCAL_TRUST_SECOND_HS_MIDPOINT_REPLAY": ("exact_midpoint_rates", (370, 99)),
    }
    for name, (array_name, shape) in shapes.items():
        record = _load(name)
        data = ROOT / record["data"]
        assert _sha256(data) == record["data_SHA256"]
        with np.load(data) as source:
            assert source[array_name].shape == shape
