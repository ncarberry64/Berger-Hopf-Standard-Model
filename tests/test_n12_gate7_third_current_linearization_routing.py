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


def test_third_newton_is_replayed_and_rejected() -> None:
    graph = _load("BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN")
    tangent = _load("BHSM_N12_GATE7_SECOND_CURRENT_CENTER_MACRO_TANGENT")
    endpoint = _load("BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE")
    replay = _load("BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY")
    assert graph["validation_passed"] is True
    assert tangent["validation_passed"] is True
    assert endpoint["validation_passed"] is True
    assert replay["validation_passed"] is False
    assert replay["summary"]["flow_defect_reduction_factor"] < 1.0
    assert replay["claim_boundary"]["continuous_action_constrained_center"] == (
        "OPEN_INTERVAL_AUTHORITY"
    )
    assert replay["FULL_BHSM_COMPLETE"] is False


def test_third_newton_data_hashes_and_shapes() -> None:
    shapes = {
        "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_GRAPH_JACOBIAN": (
            "graph_Jacobian_action", (371, 98, 98)
        ),
        "BHSM_N12_GATE7_SECOND_CURRENT_CENTER_MACRO_TANGENT": (
            "physical_tangent_action", (48, 98, 73)
        ),
        "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_ENDPOINT_CANDIDATE": (
            "projected_states", (371, 98)
        ),
        "BHSM_N12_GATE7_THIRD_CURRENT_LINEARIZATION_NEWTON_COLLOCATION_REPLAY": (
            "sampled_augmented_flow_defect", (1110, 99)
        ),
    }
    for name, (array_name, shape) in shapes.items():
        record = _load(name)
        data = ROOT / record["data"]
        assert _sha256(data) == record["data_SHA256"]
        with np.load(data) as source:
            assert source[array_name].shape == shape
