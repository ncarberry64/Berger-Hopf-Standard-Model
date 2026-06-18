import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_bhsm_geometric_overlap_kernel_uses_internal_volume_integral():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_bhsm_geometric_overlap_kernel.md").read_text()

    assert lg.bhsm_overlap_kernel() == "I_f(i,j)=integral_{B^3} Psi_A_f_i^*(y) Phi_H_f(y) Psi_S_f_j(y) dV_gamma"
    assert lg.bhsm_overlap_kernel() in text
    assert "B^3" in text
    assert "dV_gamma" in text
    assert "BHSM_GEOMETRIC_OVERLAP_KERNEL_DERIVED_CONDITIONAL" in text
