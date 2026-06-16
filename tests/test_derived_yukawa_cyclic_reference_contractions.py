import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_cyclic_reference_contractions_close_for_allowed_classes():
    for row in y.allowed_yukawa_operator_classes():
        assert row.cyclic_reference_closes is True


def test_cyclic_reference_mismatches_are_rejected():
    mismatches = {
        row.name: row for row in y.forbidden_yukawa_operator_classes()
    }
    assert mismatches["forbid_reference_active_cyclic_singlet"].cyclic_reference_closes is False
    assert mismatches["forbid_cyclic_active_reference_singlet"].cyclic_reference_closes is False


def test_cyclic_reference_document_contains_status():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_cyclic_reference_contractions.md").read_text()
    assert "reference active sector closes only with reference singlet sector" in text
    assert "cyclic active sector closes with cyclic conjugate-compatible singlet sector" in text
    assert "YUKAWA_CYCLIC_REFERENCE_CONTRACTIONS_DERIVED_CONDITIONAL" in text
