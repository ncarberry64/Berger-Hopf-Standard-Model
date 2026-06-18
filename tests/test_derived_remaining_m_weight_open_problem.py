import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_m_weight_remains_open_even_after_n_convention_is_selected():
    assert hw.m_weight_assignment_derived() is False
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_remaining_m_weight_open_problem.md").read_text()
    assert "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN" in text
    assert "boundary-orientation theorem" in text
