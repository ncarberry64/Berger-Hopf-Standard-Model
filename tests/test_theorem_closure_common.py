import json

import pytest

from bhsm.interface.theorem_closure.common import ActionTermCandidate, OperatorDefinition, TheoremClosureResult, TheoremStatement
from bhsm.interface.theorem_closure.proof_gates import build_proof_gates, promotion_allowed


def test_proof_gates_are_explicit_and_fail_closed():
    gates = build_proof_gates({"G01": True})
    assert len(gates) == 17
    assert promotion_allowed(gates) is False
    assert {gate.gate_id for gate in gates} == {f"G{i:02d}" for i in range(1, 18)}


def test_closed_status_cannot_be_claimed_without_promotion():
    gates = build_proof_gates({})
    with pytest.raises(ValueError):
        TheoremClosureResult(
            "bad", "bad", "CLOSED_DERIVED_ACTION_LEVEL", gates,
            TheoremStatement("bad", "bad", (), "bad"), "", "",
            OperatorDefinition("", "", "", "", ""),
            ActionTermCandidate("", "", "", (), ()), "", False, (), (),
            False, False, False, (), "OPEN", "CLOSED", False, "", (), "", (), (),
        )


def test_gate_payload_is_json_serializable():
    json.dumps([gate.__dict__ for gate in build_proof_gates({"G01": True})])
