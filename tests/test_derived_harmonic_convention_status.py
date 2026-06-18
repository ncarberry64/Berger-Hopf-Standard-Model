import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_harmonic_convention_status_lists_a_b_c_d_and_no_selected_derivation():
    mw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_harmonic_convention_status.md").read_text()
    names = {c.name for c in mw.candidate_harmonic_conventions()}

    assert {"A: ell=k/2, n=j", "B: ell=k, n=j", "C: ell=k/2, n=j/2", "D: ell=k/2, n=q/2"} <= names
    assert mw.selected_harmonic_convention_derived() is False
    assert "SELECTED_HARMONIC_CONVENTION_REMAINS_OPEN" in text
