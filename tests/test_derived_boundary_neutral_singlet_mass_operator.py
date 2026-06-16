import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_neutral_singlet_mass_operator_allowed_conditionally():
    field = y.boundary_field_inventory()["S_ref_neutral"]
    assert y.neutral_singlet_mass_operator_allowed() is True
    assert field.C == 0
    assert field.Y == 0
    assert field.orientation == "singlet"


def test_neutral_singlet_mass_document_preserves_guardrails():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_neutral_singlet_mass_operator.md").read_text()
    assert "S_ref_neutral S_ref_neutral" in text
    assert "This does not predict a scale." in text
    assert "This does not derive PMNS mixing." in text
    assert "BOUNDARY_NEUTRAL_SINGLET_MASS_OPERATOR_ALLOWED_CONDITIONALLY" in text
