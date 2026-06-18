import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_non_tautology_keeps_axis_collapse_conditional():
    text = mm.render_non_tautology()
    assert "single m assignment is not forced" in text
    assert "conditional on y0" in text
    assert "no empirical fitting" in text
