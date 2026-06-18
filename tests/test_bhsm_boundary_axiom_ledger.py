import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_boundary_derivation import ALLOWED_STATUSES, axiom_ledger  # noqa: E402


def test_boundary_axiom_ledger_has_required_records_and_statuses():
    ledger = axiom_ledger()
    assert len(ledger) >= 9
    assert set(ledger) == {f"AX-BH-{index}" for index in range(1, 10)}
    for record in ledger.values():
        assert record.name
        assert record.statement
        assert record.role
        assert record.discharge_condition
        assert record.status in ALLOWED_STATUSES
        assert record.status != "PROVEN"


def test_boundary_axiom_ledger_contains_required_axioms():
    ledger = axiom_ledger()
    assert ledger["AX-BH-2"].name == "Hopf fiber phase closure"
    assert ledger["AX-BH-3"].name == "Boundary orientation involution"
    assert ledger["AX-BH-4"].name == "Cyclic channel closure"
    assert ledger["AX-BH-9"].name == "Anomaly bridge"

