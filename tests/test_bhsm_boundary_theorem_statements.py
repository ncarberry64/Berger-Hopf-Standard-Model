import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_boundary_derivation import (  # noqa: E402
    axiom_ledger,
    lemma_ledger,
    theorem_ledger,
    theorem_status_summary,
)


def test_theorem_ledger_has_required_records():
    ledger = theorem_ledger()
    assert len(ledger) >= 8
    assert set(ledger) == {f"THM-BH-{index}" for index in range(1, 9)}
    assert "S_phase" in ledger["THM-BH-1"].conclusion
    assert "H_orientation" in ledger["THM-BH-2"].conclusion
    assert "H_cyclic(3)=18" in ledger["THM-BH-3"].conclusion
    assert "{1,2,3}" in ledger["THM-BH-6"].conclusion


def test_each_theorem_references_valid_dependencies():
    valid = set(axiom_ledger()) | set(lemma_ledger()) | set(theorem_ledger())
    for theorem in theorem_ledger().values():
        assert theorem.assumptions
        assert set(theorem.assumptions) <= valid
        assert theorem.proof_sketch
        assert theorem.missing_proof_obligations


def test_theorem_status_summary_preserves_guardrails():
    summary = theorem_status_summary()
    assert summary["standard_model_fully_derived"] is False
    assert summary["boundary_action_fully_derived"] is False
    assert summary["full_hessian_proof_complete"] is False
    assert summary["bhsm_replacement_claim_allowed"] is False

