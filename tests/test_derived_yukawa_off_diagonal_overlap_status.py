import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_off_diagonal_entries_are_conditional_not_forbidden_by_default():
    for sector in k.SECTORS:
        entries = k.overlap_kernel_entries(sector)
        off_diagonal = [entry for entry in entries if entry.row != entry.col]
        assert len(off_diagonal) == 6
        assert all(entry.status == k.OFF_DIAGONAL for entry in off_diagonal)
        assert all(entry.status != k.FORBIDDEN for entry in off_diagonal)


def test_off_diagonal_document_contains_guardrail():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_off_diagonal_overlap_status.md").read_text()
    assert "off-diagonal entries are not zero by assumption" in text
    assert "future mixing" in text
    assert "YUKAWA_OFF_DIAGONAL_OVERLAP_STATUS_DERIVED_CONDITIONAL" in text
