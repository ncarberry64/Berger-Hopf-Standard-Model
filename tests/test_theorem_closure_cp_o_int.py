from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int import evaluate_cp_o_int_candidate

ROOT = Path(__file__).resolve().parents[1]


def test_cp_phase_does_not_promote_standalone_o_int():
    result = evaluate_cp_o_int_candidate(repository=ROOT)
    assert result.closure_status == "OPEN_MISSING_INTERACTION_ATTACHMENT"
    assert result.promotion_allowed is False
    assert result.callable_available is False
    assert "standalone interaction operator O_int" in result.missing_objects[0]
    phase = result.provenance[1]
    assert phase["value"]["delta_BH_formula"] == "pi/3"
    assert result.empirical_derivation_inputs_used is False
