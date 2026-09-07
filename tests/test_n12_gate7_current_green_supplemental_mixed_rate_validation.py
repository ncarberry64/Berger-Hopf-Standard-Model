from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/validate_n12_gate7_current_green_supplemental_mixed_rate.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("supplemental_mixed_validation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_comparison_reports_lossless_identity() -> None:
    module = _module()
    expected = np.arange(12, dtype=float).reshape(4, 3)
    result = module._comparison(expected.copy(), expected)
    assert result == {
        "maximum_absolute_difference": 0.0,
        "Frobenius_difference": 0.0,
        "relative_Frobenius_difference": 0.0,
    }


def test_comparison_rejects_nonfinite_or_mismatched_arrays() -> None:
    module = _module()
    with pytest.raises(ValueError, match="identical matrix shape"):
        module._comparison(np.zeros((2, 2)), np.zeros((2, 3)))
    with pytest.raises(ValueError, match="finite"):
        module._comparison(np.array([[np.nan]]), np.zeros((1, 1)))

