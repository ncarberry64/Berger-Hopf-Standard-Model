import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_exactly_four_allowed_yukawa_operator_classes():
    rows = y.allowed_yukawa_operator_classes()
    assert y.exactly_four_renormalizable_yukawa_classes() is True
    assert [row.name for row in rows] == [
        "cyclic_upper_closure",
        "cyclic_lower_closure",
        "reference_charged_closure",
        "reference_neutral_closure",
    ]
    for row in rows:
        assert row.hypercharge_sum == 0
        assert row.orientation_closes is True
        assert row.cyclic_reference_closes is True
        assert row.status == "ALLOWED_BOUNDARY_YUKAWA_OPERATOR"


def test_allowed_operator_document_table_contains_all_rows():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_allowed_operator_classes.md").read_text()
    for name in [
        "cyclic_upper_closure",
        "cyclic_lower_closure",
        "reference_charged_closure",
        "reference_neutral_closure",
    ]:
        assert name in text
    assert "YUKAWA_ALLOWED_OPERATOR_CLASSES_DERIVED_CONDITIONAL" in text
