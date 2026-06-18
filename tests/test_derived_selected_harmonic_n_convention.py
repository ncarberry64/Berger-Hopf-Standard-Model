import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_selected_n_weight_convention_is_highest_weight_normalization():
    assert hw.selected_n_weight_convention() == "ell=k/2, n=q/2, j=ell-n"
    assert hw.highest_weight_normalization_derived() is True


def test_selected_n_convention_doc():
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_selected_harmonic_n_convention.md").read_text()
    assert "ell=k/2, n=q/2, j=ell-n" in text
    assert "SELECTED_N_WEIGHT_CONVENTION_DERIVED_CONDITIONAL" in text
