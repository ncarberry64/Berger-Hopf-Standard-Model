import json
from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_report import build_cp_o_int_report
from bhsm.interface.theorem_closure.cp_o_int import evaluate_cp_o_int_candidate

ROOT = Path(__file__).resolve().parents[1]


def test_cp_o_int_focused_result_is_serializable_and_offline():
    result = build_cp_o_int_report(repository=ROOT)
    json.dumps(result.to_dict())
    assert result.status_after == "OPEN_MISSING_INTERACTION_ATTACHMENT"
    assert result.deepest_valid_stage == "Stage 2: Phase attachment rule availability"
    assert result.promoted is False
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_theorem_inputs is False
    assert result.calibration_values_used_as_theorem_inputs is False
    assert len(result.proof_gates) == 21


def test_internal_phase_is_not_standalone_interaction():
    result = build_cp_o_int_report(repository=ROOT)
    assert result.phase_attachment_rule["delta_formula"] == "pi/3"
    assert result.phase_attachment_rule["ckm_attachment"] is True
    assert result.phase_attachment_rule["pmns_attachment"] is True
    assert result.phase_attachment_rule["standalone_attachment"] is False
    assert result.callable_available is False


def test_sprint_a_cp_entry_point_remains_callable():
    legacy = evaluate_cp_o_int_candidate(repository=ROOT)
    assert legacy.closure_status == "OPEN_MISSING_INTERACTION_ATTACHMENT"
    assert legacy.promotion_allowed is False
