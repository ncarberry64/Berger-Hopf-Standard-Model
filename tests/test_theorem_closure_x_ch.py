from pathlib import Path

from bhsm.interface.theorem_closure.x_ch import evaluate_x_ch_candidate

ROOT = Path(__file__).resolve().parents[1]


def test_x_ch_attempt_localizes_but_does_not_promote():
    result = evaluate_x_ch_candidate(repository=ROOT)
    assert result.closure_status == "OPEN_EXACT_MISSING_THEOREM"
    assert result.promotion_allowed is False
    assert result.callable_available is False
    assert "spin" in result.missing_objects[0]
    assert {"G02", "G03", "G04", "G14", "G15"} <= set(result.failed_required_gates)
    assert result.empirical_derivation_inputs_used is False
    assert result.reference_values_used_as_derivation_inputs is False
    assert result.calibration_inputs_used is False
