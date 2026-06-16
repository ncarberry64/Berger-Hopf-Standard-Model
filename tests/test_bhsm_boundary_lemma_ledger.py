import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_boundary_derivation import lemma_ledger  # noqa: E402


def test_lemma_ledger_has_required_records():
    ledger = lemma_ledger()
    assert len(ledger) >= 7
    for code in [f"LEM-BH-{index}" for index in range(1, 8)]:
        assert code in ledger
        assert ledger[code].statement
        assert ledger[code].proof_sketch
        assert ledger[code].dependencies
        assert ledger[code].linked_prior_gate


def test_lemma_ledger_contains_required_math_lemmas():
    ledger = lemma_ledger()
    assert "d^2 epsilon^2" in ledger["LEM-BH-1"].statement
    assert "4 sum epsilon_i^2" in ledger["LEM-BH-2"].statement
    assert "n^2 epsilon^2" in ledger["LEM-BH-3"].statement
    assert "End(C^d)=M_d(C)" in ledger["LEM-BH-4"].statement

