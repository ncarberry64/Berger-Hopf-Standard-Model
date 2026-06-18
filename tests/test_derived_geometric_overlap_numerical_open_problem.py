import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_geometric_overlap_numerical_open_problem_is_explicit():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_geometric_overlap_numerical_open_problem.md").read_text()

    assert "Psi_A_f_i(y0)" in text
    assert "Psi_S_f_j(y0)" in text
    assert "finite-width overlap moments" in text
    assert "without fitting measured fermion masses" in text
    assert lg.numerical_eigenfunction_amplitudes_computed() is False
    assert lg.numerical_yukawa_values_derived() is False
