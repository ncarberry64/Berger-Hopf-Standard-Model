import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_m_equals_n_candidate_labels_are_generated():
    for labels in la.leading_axis_ledgers().values():
        for label in labels:
            assert label.m == label.n


def test_m_equals_n_assignment_doc_stays_structural():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_m_equals_n_leading_axis_assignment.md").read_text()
    assert "candidate assignment `m=n`" in text
    assert "M_EQUALS_Q_OVER_2_STRUCTURALLY_MOTIVATED_NOT_DERIVED" in text
