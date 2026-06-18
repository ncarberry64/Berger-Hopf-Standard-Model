import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_neutral_sector_mass_scaffold_is_symbolic_only():
    scaffold = yo.neutral_sector_mass_scaffold()
    assert scaffold["included"] is True
    assert scaffold["symbolic_mass_matrix"] == "M_N[j,k]=N_N*I_N(S_ref_neutral[j],S_ref_neutral[k])"
    assert scaffold["effective_operator"] == "M_eff=-M_D*M_N^{-1}*M_D^T"
    assert scaffold["mass_scale_predicted"] is False
    assert scaffold["pmns_values_derived"] is False


def test_neutral_sector_mass_scaffold_document_preserves_guardrails():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_neutral_sector_mass_scaffold.md").read_text()
    assert "M_N[j,k]=N_N*I_N(S_ref_neutral[j],S_ref_neutral[k])" in text
    assert "M_eff=-M_D*M_N^{-1}*M_D^T" in text
    assert "no neutral mass scale is predicted" in text
    assert "NEUTRAL_SECTOR_MASS_SCAFFOLD_DERIVED_CONDITIONAL" in text
