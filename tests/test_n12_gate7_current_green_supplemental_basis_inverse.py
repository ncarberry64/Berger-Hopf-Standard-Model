from __future__ import annotations

import importlib.util
from pathlib import Path
import numpy as np
import pytest
from flint import ctx

PATH = Path(__file__).resolve().parents[1] / "scripts/certify_n12_gate7_current_green_supplemental_basis_inverse.py"
spec = importlib.util.spec_from_file_location("supplemental_basis_inverse", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_verified_inverse_encloses_known_exact_inverse_and_restores_precision():
    previous = ctx.prec
    result = module.certify_basis(np.array([[1., 2.], [3., 5.]]))
    # Exact inverse [[-5,2],[3,-1]] has infinity norm 7.
    assert result["nonsingular"]
    assert result["inverse_infinity_upper"] >= 7
    assert result["residual_infinity_upper"] < 1e-130
    assert ctx.prec == previous


def test_no_small_singular_value_cutoff_discards_valid_scaled_direction():
    result = module.certify_basis(np.diag([1., 2.**-100]))
    assert result["nonsingular"]
    assert result["inverse_infinity_upper"] >= 2.**100


def test_singular_basis_fails_and_restores_precision():
    previous = ctx.prec
    with pytest.raises((ZeroDivisionError, ValueError, RuntimeError)):
        module.certify_basis(np.array([[1., 2.], [2., 4.]]))
    assert ctx.prec == previous


@pytest.mark.parametrize("values", [np.zeros((2, 3)), np.array([[np.nan]]), np.zeros((0, 0))])
def test_invalid_basis_is_rejected(values):
    with pytest.raises(ValueError):
        module.certify_basis(values)
