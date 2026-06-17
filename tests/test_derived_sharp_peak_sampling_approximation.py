import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_sharp_peak_sampling_is_leading_focusing_only():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_sharp_peak_sampling_approximation.md").read_text()

    assert lg.sharp_peak_approximation() == "I_f(i,j) approx Phi0 Psi_A_f_i^*(y0) Psi_S_f_j(y0)"
    assert lg.sharp_peak_approximation() in text
    assert "leading focusing approximation" in text
    assert "not a complete rank-three matrix theorem" in text
    assert "SHARP_PEAK_Y0_SAMPLING_APPROXIMATION_DERIVED_CONDITIONAL" in text
