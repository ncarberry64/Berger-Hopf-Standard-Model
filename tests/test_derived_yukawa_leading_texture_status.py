import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_leading_texture_status_matrices_have_diagonal_d_and_off_diagonal_o():
    for sector in k.SECTORS:
        matrix = k.texture_status_matrix(sector)
        compact = k.compact_texture_matrix(sector)
        assert compact == [["D", "O", "O"], ["O", "D", "O"], ["O", "O", "D"]]
        for i in range(3):
            for j in range(3):
                if i == j:
                    assert matrix[i][j] == k.LEADING_DIAGONAL
                else:
                    assert matrix[i][j] == k.OFF_DIAGONAL
    assert k.texture_summary_counts() == {
        "leading_diagonal_entries": 12,
        "conditional_off_diagonal_entries": 24,
        "forbidden_entries": 0,
        "total_entries": 36,
    }


def test_leading_texture_document_contains_status():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_leading_texture_status.md").read_text()
    assert "DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE" in text
    assert "CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE" in text
    assert "YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL" in text
