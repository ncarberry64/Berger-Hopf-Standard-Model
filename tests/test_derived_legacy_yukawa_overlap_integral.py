import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_legacy_yukawa_overlap_integral_is_bridged_symbolically():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_legacy_yukawa_overlap_integral.md").read_text()

    assert lg.legacy_overlap_integral() == "Y_ij^f = g_f integral Psi_L_i^*(y) Phi(y) Psi_R_j(y) dV_int"
    assert lg.legacy_overlap_integral() in text
    assert "Y_f[i,j] = N_f I_f(A_f[i], H_f, S_f[j])" in text
    assert "LEGACY_YUKAWA_OVERLAP_INTEGRAL_BRIDGED_CONDITIONAL" in text
