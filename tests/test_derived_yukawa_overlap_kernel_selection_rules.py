import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_selection_rules_close_and_entries_exist_for_all_sectors():
    ledgers = k.generation_mode_ledgers()
    assert set(ledgers) == set(k.SECTORS)
    for sector in k.SECTORS:
        assert len(ledgers[sector]) == 3
        assert len(k.overlap_kernel_entries(sector)) == 9
        assert all(entry.numerical_value_status == k.NUMERIC_OPEN for entry in k.overlap_kernel_entries(sector))
        assert k.overlap_kernel_symbol(sector, 1, 1) == f"K_{sector}_11"
    with pytest.raises(ValueError):
        k.overlap_kernel_entries("missing")
    with pytest.raises(ValueError):
        k.overlap_kernel_symbol("cyclic_upper", 4, 1)


def test_selection_rule_document_contains_ten_principles():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_overlap_kernel_selection_rules.md").read_text()
    assert text.count(". ") >= 10
    assert "parent operator class is one of the four allowed Yukawa closures" in text
    assert "off-diagonal i!=j requires" in text
    assert "YUKAWA_OVERLAP_KERNEL_SELECTION_RULES_DERIVED_CONDITIONAL" in text
