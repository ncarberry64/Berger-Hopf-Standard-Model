import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_yukawa_rank_three_open_problem_lists_needed_geometry_not_fits():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_rank_three_open_problem.md").read_text()

    assert "three independent matrix structures" in text
    assert "derive the internal Berger/BHSM eigenfunctions" in text
    assert "compute amplitudes and derivatives near `y0`" in text
    assert "compute finite-width profile moments" in text
    assert "without measured fermion masses or CKM/PMNS inputs" in text
    assert fw.numerical_yukawa_values_derived() is False
