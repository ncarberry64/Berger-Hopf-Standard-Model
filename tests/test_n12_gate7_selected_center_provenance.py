from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_GATE7_SELECTED_CENTER_PROVENANCE_RECONCILIATION.json"


def test_selected_center_provenance_defect_is_explicit() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["classification"] == "PROVENANCE_DEFECT"
    assert payload["measurements"]["maximum_half_to_quarter_action_state_2_norm"] > 0.0
    assert payload["measurements"]["maximum_original_to_quarter_action_state_2_norm"] > 0.0
    assert payload["validation"][
        "all_current_prerequisite_scripts_name_quarter_center"
    ] is True
    assert payload["validation"][
        "no_current_prerequisite_script_names_half_center"
    ] is True
    assert payload["validation"][
        "current_common_frame_script_names_only_quarter_center_operands"
    ] is True
    assert payload["claim_boundary"][
        "same_center_exact_directional_mixed_transverse"
    ] == "DERIVED"
    assert payload["claim_boundary"][
        "same_center_common_frame_operands"
    ] == "DERIVED"
    assert payload["claim_boundary"][
        "same_center_DOP853_spectrum_projector_inverse_response"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "same_center_DOP853_response_second_variation"
    ] == "OPEN_SIGNED_CORRELATION_REQUIRED"
    assert payload["claim_boundary"][
        "same_center_DOP853_nonlinear_tube"
    ] == "OPEN_CORRELATED_SELF_MAP"
    assert payload["claim_boundary"][
        "same_center_DOP853_candidate_cone_line_projector_inverse"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "legacy_mixed_center_recentered_cone"
    ] == "HISTORICAL_NOT_CURRENT"


def test_invalidated_compositions_are_not_promoted() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    invalidated = [
        row for row in payload["classification_ledger"]
        if row["classification"] == "INVALIDATED"
    ]
    assert len(invalidated) == 3
    assert payload["claim_boundary"]["causal_interval_vector_radius"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
