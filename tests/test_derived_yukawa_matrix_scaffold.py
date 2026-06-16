import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_four_yukawa_matrix_scaffolds_are_3x3_with_correct_insertions():
    scaffolds = {scaffold.sector: scaffold for scaffold in yo.all_yukawa_matrix_scaffolds()}
    assert set(scaffolds) == set(yo.SECTORS)
    assert yo.each_matrix_is_3x3() is True
    assert yo.operator_class_to_scalar_insertion() == {
        "cyclic_upper": "H",
        "cyclic_lower": "H_tilde",
        "reference_charged": "H_tilde",
        "reference_neutral": "H",
    }
    for sector, scaffold in scaffolds.items():
        assert scaffold.operator_class == yo.OPERATOR_CLASS_BY_SECTOR[sector]
        assert scaffold.scalar_insertion == yo.SCALAR_INSERTION_BY_SECTOR[sector]
        assert len(scaffold.active_modes) == 3
        assert len(scaffold.singlet_modes) == 3
        assert len(scaffold.entries) == 9
        assert yo.selection_rules_close_for_sector(sector) is True
        diagonal = [entry for entry in scaffold.entries if entry.row == entry.col]
        off_diagonal = [entry for entry in scaffold.entries if entry.row != entry.col]
        assert all(entry.status == "DERIVED_DIAGONAL_SYMBOLIC_OVERLAP" for entry in diagonal)
        assert all(entry.status == "CONDITIONAL_OFF_DIAGONAL_OVERLAP" for entry in off_diagonal)


def test_yukawa_matrix_scaffold_document_contains_all_matrices():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_matrix_scaffold.md").read_text()
    for sector in yo.SECTORS:
        assert f"Y_{sector}" in text
        assert f"I_{sector}_11" in text
        assert f"I_{sector}_33" in text
    assert "YUKAWA_MATRIX_SCAFFOLD_DERIVED_CONDITIONAL" in text
