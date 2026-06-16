import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_boundary_derivation import (  # noqa: E402
    is_full_boundary_derivation_complete,
    open_proof_obligations,
    proof_obligation_ledger,
)


def test_proof_obligation_ledger_has_required_open_records():
    ledger = proof_obligation_ledger()
    assert len(ledger) >= 12
    assert set(ledger) == {f"PO-BH-{index}" for index in range(1, 13)}
    assert open_proof_obligations() == [f"PO-BH-{index}" for index in range(1, 13)]
    assert is_full_boundary_derivation_complete() is False


def test_each_proof_obligation_has_evidence_falsifier_and_impact():
    for record in proof_obligation_ledger().values():
        assert record.status == "OPEN"
        assert record.blocking_assumptions
        assert record.required_evidence
        assert record.possible_falsifier
        assert record.downstream_impact

