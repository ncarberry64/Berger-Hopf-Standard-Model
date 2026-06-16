import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_mode_distance_matrices_are_exact_nonnegative_and_diagonal_zero():
    for sector in k.SECTORS:
        l1 = k.distance_matrix_L1(sector)
        l2 = k.distance_matrix_L2_squared(sector)
        assert len(l1) == len(l2) == 3
        for i in range(3):
            assert len(l1[i]) == len(l2[i]) == 3
            assert l1[i][i] == 0
            assert l2[i][i] == 0
            for j in range(3):
                assert isinstance(l1[i][j], int)
                assert isinstance(l2[i][j], int)
                assert l1[i][j] >= 0
                assert l2[i][j] >= 0


def test_reference_and_cyclic_distance_examples():
    assert k.distance_matrix_L1("cyclic_upper") == [[0, 6, 9], [6, 0, 3], [9, 3, 0]]
    assert k.distance_matrix_L2_squared("cyclic_lower") == [[0, 9, 20], [9, 0, 17], [20, 17, 0]]


def test_mode_distance_document_contains_guardrail():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_mode_distance_scaffold.md").read_text()
    assert "D_f(i,j)=|q_i-q_j|+|j_i-j_j|" in text
    assert "These are diagnostic distances, not numerical Yukawa values." in text
    assert "YUKAWA_MODE_DISTANCE_SCAFFOLD_DERIVED_CONDITIONAL" in text
