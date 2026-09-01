from __future__ import annotations

import json
from pathlib import Path

from scripts.audit_n12_gate7_two_chord_heat_tail import build_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
)


def test_two_chord_heat_tail_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    regenerated = build_payload()
    assert json.dumps(payload, sort_keys=True) == json.dumps(
        regenerated, sort_keys=True
    )
    assert payload["validation_passed"] is True
    assert payload["certified_coordinate_time_end"] == 2.0e-8
    assert payload["two_chord_heat_test"]["proper_duration_upper"] < 2.3e-8
    assert payload["two_chord_heat_test"][
        "best_case_exp_minus_2_gap_T"
    ] > 0.9999999
    assert payload["two_chord_heat_test"][
        "best_case_constant_gap_endpoint_bound_lower"
    ] > 1.0e7
    adjudication = payload["adjudication"]
    assert adjudication["temporal_state_or_source_tail_certified"] is False
    assert adjudication["two_chord_finite_core_promotable_to_complete_heat_response"] is False
    assert adjudication["chord_03_has_proof_value_from_this_estimate"] is False
    assert adjudication["chord_03_authorized"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_spatial_tail_is_not_temporal_tail() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["spatial_Galerkin_tail_certified"] is True
    assert adjudication["temporal_state_or_source_tail_certified"] is False
    assert payload["validation"][
        "spatial_Galerkin_tail_not_relabelled_as_temporal_tail"
    ] is True
