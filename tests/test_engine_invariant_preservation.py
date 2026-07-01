import numpy as np
import pytest

from bhsm.interface.engine_invariants import build_engine_invariant_report, minkowski_norm_sq


def test_engine_invariant_report_passes_offline():
    report = build_engine_invariant_report()
    assert report["status"] == "ENGINE_INVARIANTS_DETERMINISTIC_OFFLINE_PASS"
    assert all(report["checks"].values())


def test_nonfinite_input_is_rejected():
    with pytest.raises(ValueError):
        minkowski_norm_sq(np.array([[1.0, np.nan, 0.0, 0.0]]))

