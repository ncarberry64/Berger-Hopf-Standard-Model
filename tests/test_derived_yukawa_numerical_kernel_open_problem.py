import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_numerical_kernel_open_problem_is_precise():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_numerical_kernel_open_problem.md").read_text()
    assert "I_f(i,j)=K_f(mode_i, mode_j, H_f)" in text
    assert "not from measured masses" in text
    assert d.numerical_overlap_values_derived() is False
    assert d.fermion_mass_ratios_derived() is False
