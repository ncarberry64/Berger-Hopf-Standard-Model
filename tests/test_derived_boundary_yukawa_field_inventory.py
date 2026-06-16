from fractions import Fraction
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_boundary_yukawa_inventory_exact_fields_and_charges():
    inventory = y.boundary_field_inventory()
    assert set(inventory) == {
        "A_ref",
        "A_cyc",
        "S_ref_neutral",
        "S_ref_charged",
        "S_cyc_upper",
        "S_cyc_lower",
        "H",
        "H_tilde",
    }
    assert inventory["A_ref"].C == 0
    assert inventory["A_ref"].Y == Fraction(-1)
    assert inventory["A_cyc"].C == 1
    assert inventory["A_cyc"].Y == Fraction(1, 3)
    assert inventory["A_cyc"].multiplicity == 3
    assert inventory["S_ref_neutral"].Y == Fraction(0)
    assert inventory["S_ref_charged"].Y == Fraction(2)
    assert inventory["S_cyc_upper"].Y == Fraction(-4, 3)
    assert inventory["S_cyc_lower"].Y == Fraction(2, 3)
    assert inventory["H"].Y == Fraction(1)
    assert inventory["H_tilde"].Y == Fraction(-1)


def test_inventory_document_contains_conditional_status():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_yukawa_field_inventory.md").read_text()
    assert "BOUNDARY_YUKAWA_FIELD_INVENTORY_DERIVED_CONDITIONAL" in text
    for field in y.boundary_field_inventory():
        assert field in text


def test_unknown_boundary_field_raises():
    with pytest.raises(ValueError):
        y.hypercharge_sum("not_a_boundary_field")
