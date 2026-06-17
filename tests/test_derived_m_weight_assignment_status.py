import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_m_weight_assignment_status_keeps_all_core_items_open():
    mw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_m_weight_assignment_status.md").read_text()

    assert "| m assignment | `OPEN` |" in text
    assert "| selected harmonic convention | `OPEN` |" in text
    assert "| explicit eigenfunctions | `OPEN` |" in text
    assert mw.selected_harmonic_convention_derived() is False
    assert mw.explicit_eigenfunctions_derived() is False
    assert mw.finite_width_rank_three_derived() is False
