import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_finite_width_overlap_moment_expansion_formula_and_tensors():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_finite_width_overlap_moment_expansion.md").read_text()

    assert fw.moment_expansion_formula() == (
        "I_ij=M0 a_i^* b_j + M_ab (partial_a a_i^*)(partial_b b_j) + higher finite-width moments"
    )
    assert fw.moment_tensor_formula("M0") == "M0=integral Phi(y) dV_gamma"
    assert fw.moment_tensor_formula("Mab") == "M_ab=integral xi_a xi_b Phi(y) dV_gamma"
    assert fw.moment_tensor_formula("Mabcd") == "M_abcd=integral xi_a xi_b xi_c xi_d Phi(y) dV_gamma"
    assert fw.local_mode_expansion("A") in text
    assert fw.local_mode_expansion("S") in text
    assert fw.moment_expansion_formula() in text
    assert "FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL" in text
