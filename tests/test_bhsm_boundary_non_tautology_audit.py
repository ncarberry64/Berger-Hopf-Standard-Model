import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_theorem_boundary_derivation import non_tautology_rows  # noqa: E402


def test_non_tautology_audit_includes_required_rows():
    rows = non_tautology_rows()
    steps = {row.step for row in rows}
    assert {
        "Hopf phase closure",
        "Z2 orientation involution",
        "order-3 cyclic channel",
        "finite algebra blocks C, M2(C), M3(C)",
        "C, ell, sigma, w primitive bridge",
        "T3, Y, Q formulas",
        "anomaly closure",
        "closure spectrum {1,2,3}",
        "excess-sector gap",
    } <= steps


def test_non_tautology_rows_report_imported_structure_and_required_fix():
    for row in non_tautology_rows():
        assert row.claim
        assert row.risk_of_circularity
        assert row.imported_structure
        assert row.current_status
        assert row.required_fix

