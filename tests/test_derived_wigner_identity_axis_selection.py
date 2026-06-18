import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_wigner_identity_axis_selection_is_candidate_until_y0_is_derived():
    assert la.leading_axis_m_assignment_derived() is False
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_wigner_identity_axis_selection.md").read_text()
    assert "D^ell_{m,n}(e)=delta_{m,n}" in text
    assert "BHSM `y0` axis identification remains open" in text
    assert "Y0_AXIS_SAMPLING_REMAINS_OPEN" in text
