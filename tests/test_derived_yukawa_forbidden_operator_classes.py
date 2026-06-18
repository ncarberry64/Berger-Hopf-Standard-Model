from fractions import Fraction
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_forbidden_yukawa_operator_classes_report_failures():
    rows = {row.name: row for row in y.forbidden_yukawa_operator_classes()}
    assert rows["forbid_cyclic_upper_wrong_scalar"].hypercharge_sum == Fraction(-2)
    assert rows["forbid_cyclic_lower_wrong_scalar"].hypercharge_sum == Fraction(2)
    assert rows["forbid_reference_charged_wrong_scalar"].hypercharge_sum == Fraction(2)
    assert rows["forbid_reference_neutral_wrong_scalar"].hypercharge_sum == Fraction(-2)
    assert rows["forbid_reference_active_cyclic_singlet"].hypercharge_sum == Fraction(2, 3)
    assert rows["forbid_cyclic_active_reference_singlet"].hypercharge_sum == Fraction(4, 3)
    for row in rows.values():
        assert row.status == "FORBIDDEN_BOUNDARY_YUKAWA_OPERATOR"


def test_forbidden_operator_document_table_contains_negative_examples():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_forbidden_operator_classes.md").read_text()
    for name in [
        "forbid_cyclic_upper_wrong_scalar",
        "forbid_cyclic_lower_wrong_scalar",
        "forbid_reference_charged_wrong_scalar",
        "forbid_reference_neutral_wrong_scalar",
        "forbid_reference_active_cyclic_singlet",
        "forbid_cyclic_active_reference_singlet",
    ]:
        assert name in text
    assert "YUKAWA_FORBIDDEN_OPERATOR_CLASSES_DERIVED_CONDITIONAL" in text
