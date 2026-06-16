import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_orientation_contractions_close_for_allowed_classes():
    for row in y.allowed_yukawa_operator_classes():
        assert row.orientation_closes is True


def test_orientation_helper_rejects_non_singlet_third_field():
    inventory = y.boundary_field_inventory()
    assert y.orientation_contraction_closes(inventory["A_ref"], inventory["H"], inventory["H_tilde"]) is False


def test_orientation_document_contains_boundary_language():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_orientation_contractions.md").read_text()
    assert "active boundary doublet" in text
    assert "orientation singlet contraction" in text
    assert "YUKAWA_ORIENTATION_CONTRACTIONS_DERIVED_CONDITIONAL" in text
