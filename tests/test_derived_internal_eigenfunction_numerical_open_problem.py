import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_internal_eigenfunction_numerical_open_problem_excludes_measured_inputs():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_internal_eigenfunction_numerical_open_problem.md").read_text()

    assert "derive explicit internal eigenfunctions `psi_qj(y)`" in text
    assert "values, gradients, and Hessians at `y0`" in text
    assert "finite-width moment contractions" in text
    assert "must not use measured fermion masses, known Yukawa matrices, CKM values, or PMNS values" in text
    assert qj.numerical_yukawa_values_derived() is False
