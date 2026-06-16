import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_mixing_scaffold_defined_but_not_numerical():
    assert yo.mixing_scaffold_defined() is True
    assert yo.cyclic_mixing_scaffold() == "V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L"
    assert yo.reference_mixing_scaffold() == "V_reference=U_reference_charged_L^dagger U_reference_neutral_L"
    assert yo.ckm_values_derived() is False
    assert yo.pmns_values_derived() is False


def test_mixing_scaffold_document_preserves_guardrails():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_mixing_scaffold.md").read_text()
    assert "U_f_L^dagger Y_f U_f_R = D_f" in text
    assert "CKM values are not derived" in text
    assert "PMNS values are not derived" in text
    assert "YUKAWA_MIXING_SCAFFOLD_DERIVED_CONDITIONAL" in text
