from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_EXACT_AFFINE_72D_HISTORY_FIRST_JET.json"
TRANSFER = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AFFINE_72D_NONLINEAR_TRANSFER_AUDIT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_complete_affine_72d_history_first_jet_is_materialized() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["summary"]["parameter_dimension"] == 72
    assert record["summary"]["history_node_count"] == 48
    assert record["summary"]["macro_map_count"] == 47
    assert record["claim_boundary"]["nonlinear_exact_solution_family_first_jet_transfer"] == "OPEN"
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    with np.load(data) as source:
        assert source["ambient_fixed_time_Jacobi_midpoint"].shape == (48, 98, 72)
        assert source["proper_duration_first_jet_midpoint"].shape == (72,)
        assert source["terminal_first_hit_Jacobi_midpoint"].shape == (98, 72)
        assert source["log_R4_normalized_time_first_jet_midpoint"].shape == (48, 72)
        assert np.all(np.isfinite(source["log_R4_normalized_time_first_jet_radius"]))


def test_affine_history_first_jet_provenance_matches_disk() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    for relative, expected in record["inputs"].items():
        assert _sha256(ROOT / relative) == expected


def test_nonlinear_transfer_fails_closed_and_routes_to_direct_carrier() -> None:
    record = json.loads(TRANSFER.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["summary"]["maximum_causal_contraction_factor_upper"] > 1.0
    assert record["summary"]["terminal_error_to_affine_Jacobi_ratio"] > 1.0
    assert record["adjudication"]["affine_jet_may_be_used_as_complete_operator_authority"] is False
    assert record["adjudication"]["next_route"] == "DIRECT_EXACT_CENTER_VARIATIONAL_CARRIER"
