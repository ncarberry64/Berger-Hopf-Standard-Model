import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_generation_mode_ledgers_for_all_four_sectors():
    ledgers = yo.generation_mode_ledgers()
    assert set(ledgers) == set(yo.SECTORS)
    assert [mode.mode_pair for mode in ledgers["reference_charged"]] == [(0, 0), (5, 2), (9, 3)]
    assert [mode.qj_pair for mode in ledgers["reference_charged"]] == [(0, 0), (1, 2), (3, 3)]
    assert [mode.mode_pair for mode in ledgers["reference_neutral"]] == [(0, 0), (3, 0), (3, 1)]
    assert [mode.qj_pair for mode in ledgers["reference_neutral"]] == [(0, 0), (3, 0), (1, 1)]
    assert [mode.mode_pair for mode in ledgers["cyclic_upper"]] == [(0, 0), (6, 0), (10, 1)]
    assert [mode.qj_pair for mode in ledgers["cyclic_upper"]] == [(0, 0), (6, 0), (8, 1)]
    assert [mode.mode_pair for mode in ledgers["cyclic_lower"]] == [(0, 0), (6, 3), (8, 2)]
    assert [mode.qj_pair for mode in ledgers["cyclic_lower"]] == [(0, 0), (0, 3), (4, 2)]


def test_generation_mode_ledger_document_contains_status():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_generation_mode_ledgers.md").read_text()
    for sector in yo.SECTORS:
        assert sector in text
    assert "YUKAWA_GENERATION_MODE_LEDGERS_DERIVED_CONDITIONAL" in text
