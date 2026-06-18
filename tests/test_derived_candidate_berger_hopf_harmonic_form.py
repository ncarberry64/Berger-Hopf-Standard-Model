import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_candidate_berger_hopf_harmonic_form_is_not_marked_derived():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_candidate_berger_hopf_harmonic_form.md").read_text()

    assert rh.candidate_berger_harmonic_form() in text
    assert rh.candidate_berger_harmonic_factorized_form() in text
    assert rh.berger_harmonic_form_status() == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert "not a completed harmonic theorem" in text
    assert "BERGER_HARMONIC_FORM_STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
