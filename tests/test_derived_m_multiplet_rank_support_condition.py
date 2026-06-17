import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_rank_three_remains_open():
    condition = mm.rank_support_condition()
    assert condition["finite_width_rank_three_derived"] is False
    assert mm.finite_width_rank_three_derived() is False
    assert "moment" in condition["condition"]
