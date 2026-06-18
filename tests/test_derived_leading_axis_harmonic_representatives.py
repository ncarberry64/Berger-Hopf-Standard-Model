import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_candidate_harmonic_representatives_exist():
    labels = la.leading_axis_ledgers()
    assert la.candidate_harmonic_representative(labels["reference_charged"][1]) == "D^(5/2)_(1/2,1/2)"
    assert la.candidate_harmonic_representative(labels["cyclic_upper"][2]) == "D^(5)_(4,4)"


def test_representatives_doc_marks_candidate_only():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_leading_axis_harmonic_representatives.md").read_text()
    assert "D^(5/2)_(1/2,1/2)" in text
    assert "LEADING_AXIS_REPRESENTATIVES_CANDIDATE_ONLY" in text
