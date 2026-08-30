from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate as collocation  # noqa: E402
import materialize_n12_gate7_rate_consistent_newton_endpoint_candidate as repaired  # noqa: E402


def _load(name: str) -> dict:
    return json.loads((BASE / f"{name}.json").read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_mixed_rate_source_is_superseded_and_repaired_step_contracts() -> None:
    endpoint = _load("BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS")
    source = _load("BHSM_N12_GATE7_FIRST_HS_RATE_CONSISTENT_NONLINEAR_SOURCE")
    predictor = _load("BHSM_N12_GATE7_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR")
    candidate = _load("BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE")
    replay = _load("BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY")
    assert all(record["validation_passed"] is True for record in (
        endpoint, source, predictor, candidate, replay,
    ))
    assert endpoint["adjudication"]["stored_pre_recenter_endpoint_rates"].startswith("SUPERSEDED")
    assert endpoint["summary"]["maximum_endpoint_rate_consistency_difference_2_norm"] > 1.0e-6
    assert source["summary"]["maximum_Hermite_Simpson_shooting_residual_2_norm"] == 1.800590017529095e-6
    assert replay["summary"]["maximum_Hermite_Simpson_shooting_residual_2_norm"] == 1.215762696655947e-6
    assert replay["summary"]["nonlinear_block_residual_reduction_factor"] > 1.48
    assert replay["FULL_BHSM_COMPLETE"] is False


def test_rate_consistent_chain_hashes_and_shapes() -> None:
    shapes = {
        "BHSM_N12_GATE7_FIRST_HS_RECENTERED_RATE_CONSISTENT_ENDPOINTS": ("exact_endpoint_augmented_rates", (371, 99)),
        "BHSM_N12_GATE7_FIRST_HS_RATE_CONSISTENT_NONLINEAR_SOURCE": ("Hermite_Simpson_shooting_residual", (370, 99)),
        "BHSM_N12_GATE7_RATE_CONSISTENT_BLOCK_NEWTON_PREDICTOR": ("endpoint_state_correction_action", (371, 98)),
        "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE": ("projected_states", (371, 98)),
        "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_MIDPOINT_REPLAY": ("exact_midpoint_rates", (370, 99)),
    }
    for name, (array, shape) in shapes.items():
        record = _load(name)
        data = ROOT / record["data"]
        assert _sha256(data) == record["data_SHA256"]
        with np.load(data) as source:
            assert source[array].shape == shape


def test_one_jet_recentered_rate_matches_canonical_fixed_descriptor_field() -> None:
    with np.load(BASE / "BHSM_N12_GATE7_RATE_CONSISTENT_NEWTON_ENDPOINT_CANDIDATE.npz") as source:
        state = np.asarray(source["projected_states"][180], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    rate, eigenvalue, selected, gap = repaired._recentered_rate(state, weights, reference)
    canonical, field = collocation._field(state, max(eigenvalue, 0.0), weights, reference)
    assert selected == int(field["selected_branch"]) == 24
    assert gap > 1.0e-7
    assert np.linalg.norm(rate - canonical) < 2.0e-13


def test_rejected_tangent_restriction_remains_negative_evidence() -> None:
    tangent = _load("BHSM_N12_GATE7_FIRST_HS_NEWTON_ENDPOINT_TANGENT")
    predictor = _load("BHSM_N12_GATE7_FIRST_HS_TANGENT_BLOCK_NEWTON_PREDICTOR")
    endpoint = _load("BHSM_N12_GATE7_FIRST_HS_TANGENT_NEWTON_ENDPOINT_CANDIDATE")
    replay = _load("BHSM_N12_GATE7_FIRST_HS_TANGENT_NEWTON_MIDPOINT_REPLAY")
    assert tangent["validation_passed"] is True
    assert predictor["validation_passed"] is True
    assert endpoint["validation_passed"] is True
    assert replay["validation_passed"] is False
    assert replay["summary"]["nonlinear_block_residual_reduction_factor"] < 1.0
