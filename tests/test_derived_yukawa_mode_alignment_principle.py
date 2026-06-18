import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_mode_alignment_entry_statuses():
    assert k.entry_status(1, 1) == k.LEADING_DIAGONAL
    assert k.entry_status(2, 2) == k.LEADING_DIAGONAL
    assert k.entry_status(3, 3) == k.LEADING_DIAGONAL
    assert k.entry_status(1, 2) == k.OFF_DIAGONAL
    assert k.entry_status(3, 1) == k.OFF_DIAGONAL
    with pytest.raises(ValueError):
        k.entry_status(0, 1)


def test_mode_alignment_document_contains_status():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_mode_alignment_principle.md").read_text()
    assert "i=j -> DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE" in text
    assert "i!=j -> CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE" in text
    assert "YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL" in text
