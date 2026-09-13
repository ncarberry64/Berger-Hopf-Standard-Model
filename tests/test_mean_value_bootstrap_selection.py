import sys
from pathlib import Path
import numpy as np
import pytest
from flint import arb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from diagnose_n12_gate7_mean_value_bootstrap_hessian import select_first_variation


def test_response_border_sign_is_converted_before_selection():
    result = np.array([arb(2, 1), arb(-10, 1)], dtype=object)
    physical = np.array([arb(2, '.1'), arb(10, '.1')], dtype=object)
    assert select_first_variation(result, physical, response=True) == 2
    assert result[1].contains(-10) and not result[1].contains(10)
    assert physical[1].contains(10)


def test_line_preserves_lambda_and_rejects_inconsistent_family():
    result = np.array([arb(2, 1), arb(3, 1), arb(17, 1)], dtype=object)
    candidate = np.array([arb(2, '.1'), arb(3, 2)], dtype=object)
    assert select_first_variation(result, candidate) == 1
    assert result[1].rad() < candidate[1].rad()
    assert result[2].contains(17)
    with pytest.raises(ArithmeticError):
        select_first_variation(result, np.array([arb(30)], dtype=object))
