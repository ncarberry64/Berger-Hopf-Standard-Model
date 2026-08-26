import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")


def _payload() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_direct_delta_identity_and_one_row_reduction_are_fail_closed() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["direct_signed_Delta_recombination"] == "DERIVED"
    assert payload["adjudication"]["full_98_by_98_D2Delta_norm_required"] is False
    assert payload["adjudication"]["one_dominant_D2Delta_row_sufficient"] is True
    assert payload["adjudication"]["rigorous_dominant_row_enclosure_on_exact_tube"] == "OPEN"
    assert payload["adjudication"]["physical_event_stop_or_zero_force_found"] is False


def test_two_mesh_row_is_only_diagnostic() -> None:
    payload = _payload()
    diagnostic = payload["two_mesh_reconnaissance"]
    assert diagnostic["authority"] == "DIAGNOSTIC_ONLY_NOT_AN_INTERVAL_OR_ANALYTIC_BOUND"
    assert diagnostic["relative_mesh_discrepancy"] < 0.02
    assert diagnostic["fine_row_to_rigorous_ceiling_ratio"] < 1.0e-4
    with np.load(DATA) as data:
        rows = np.asarray(data["direct_D2Delta_rows"], dtype=float)
        assert rows.shape == (2, 98)
        assert int(data["dominant_index"]) == 86


def test_gate_and_downstream_claims_remain_open() -> None:
    claim = _payload()["claim_boundary"]
    assert claim["signed_D_Y_Delta"] == "OPEN_PENDING_RIGOROUS_ROW_REMAINDER"
    assert claim["actual_signed_duration_covector"] == "OPEN"
    assert claim["actual_projected_zero_source_force"] == "OPEN"
    assert claim["Gate8"] == "LOCKED"
    assert claim["chord_03_authorized"] is False
    assert claim["FULL_BHSM_COMPLETE"] is False
