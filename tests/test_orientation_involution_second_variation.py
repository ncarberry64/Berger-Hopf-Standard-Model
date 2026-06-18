from fractions import Fraction
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_second_variation import (  # noqa: E402
    orientation_hessian_matrix,
    orientation_hessian_positive_diagonal,
    orientation_pair_hessian_matrix,
)


def test_orientation_pair_hessian_matrix_is_8i_plus_2lambda_j():
    assert orientation_pair_hessian_matrix(Fraction(1, 1)) == (
        (Fraction(10, 1), Fraction(2, 1)),
        (Fraction(2, 1), Fraction(10, 1)),
    )
    assert orientation_pair_hessian_matrix(Fraction(2, 1)) == (
        (Fraction(12, 1), Fraction(4, 1)),
        (Fraction(4, 1), Fraction(12, 1)),
    )


def test_orientation_hessian_positive_diagonal():
    matrix = orientation_pair_hessian_matrix(Fraction(1, 1))
    assert orientation_hessian_positive_diagonal(matrix)


def test_orientation_hessian_rejects_invalid_size():
    with pytest.raises(ValueError):
        orientation_hessian_matrix(0)

