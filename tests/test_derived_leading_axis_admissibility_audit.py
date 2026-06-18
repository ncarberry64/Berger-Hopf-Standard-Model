import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_all_leading_axis_candidate_labels_are_admissible():
    assert la.all_leading_axis_labels_admissible() is True
    for labels in la.leading_axis_ledgers().values():
        for label in labels:
            assert abs(label.m) <= label.ell
            assert abs(label.n) <= label.ell
            assert label.ell - label.m == label.j
            assert label.ell - label.n == label.j
            assert la.admissible(label)


def test_admissibility_audit_file_contains_all_checks():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_leading_axis_admissibility_audit.md").read_text()
    assert "`|m|<=ell`" in text
    assert "`ell-m=j`" in text
    assert "cyclic_upper" in text
    assert "reference_charged" in text
