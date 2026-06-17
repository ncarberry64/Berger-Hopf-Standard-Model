import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_m_weight_assignment_remains_open_and_lists_sources():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_m_weight_assignment_open_problem.md").read_text()

    assert rh.m_weight_assignment_derived() is False
    for source in rh.m_weight_candidate_sources():
        assert source in text
    assert "not guessed" in text
    assert "M_WEIGHT_ASSIGNMENT_REMAINS_OPEN" in text
