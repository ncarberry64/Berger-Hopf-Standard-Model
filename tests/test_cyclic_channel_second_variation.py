from fractions import Fraction
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_second_variation import cyclic_hessian_coefficient  # noqa: E402


def test_cyclic_hessian_coefficient_order_three():
    assert cyclic_hessian_coefficient(3) == Fraction(18, 1)


def test_cyclic_hessian_coefficient_general_order():
    assert cyclic_hessian_coefficient(1) == Fraction(2, 1)
    assert cyclic_hessian_coefficient(4) == Fraction(32, 1)


def test_cyclic_hessian_rejects_invalid_order():
    with pytest.raises(ValueError):
        cyclic_hessian_coefficient(0)

