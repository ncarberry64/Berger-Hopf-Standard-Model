import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_mass_matrix_relations_are_symbolic_for_all_sectors():
    for sector in yo.SECTORS:
        assert yo.mass_matrix_relation(sector) == f"M_{sector}=v/sqrt(2)*Y_{sector}"
    assert yo.numerical_yukawa_values_derived() is False
    assert yo.fermion_mass_ratios_derived() is False


def test_mass_matrix_relation_document_preserves_guardrails():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_mass_matrix_relations.md").read_text()
    assert "M_f = v/sqrt(2) * Y_f" in text
    assert "`v` remains symbolic" in text
    assert "numerical masses are not predicted" in text
    assert "YUKAWA_MASS_MATRIX_RELATIONS_DERIVED_CONDITIONAL" in text
