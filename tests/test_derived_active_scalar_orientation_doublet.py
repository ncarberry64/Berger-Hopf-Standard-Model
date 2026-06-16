import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_active_scalar_doublet_boundary_constraints():
    assert hs.scalar_C_value() == 0
    assert hs.cyclic_neutral_required() is True
    assert hs.scalar_is_active_orientation_fundamental() is True
    assert hs.scalar_Y_selected_up_to_conjugation() == Fraction(1)
    assert hs.has_neutral_component(Fraction(1)) is True
    assert hs.has_neutral_component(Fraction(-1)) is True
    assert hs.active_orientation_T3(1) == Fraction(1, 2)
    assert hs.active_orientation_T3(-1) == Fraction(-1, 2)
    with pytest.raises(ValueError):
        hs.active_orientation_T3(0)


def test_active_scalar_doublet_documentation():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_active_scalar_orientation_doublet.md").read_text()
    assert "C=0" in text
    assert "fundamental orientation doublet" in text
    assert "Y=+1" in text
    assert "BOUNDARY_ACTIVE_SCALAR_DOUBLET_DERIVED_CONDITIONAL" in text
