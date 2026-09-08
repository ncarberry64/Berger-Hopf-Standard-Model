from fractions import Fraction as F
import importlib.util
from pathlib import Path

import numpy as np
import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/certify_n12_gate7_current_green_midpoint_coordinate_pullback.py"
spec = importlib.util.spec_from_file_location("midpoint_coordinate_pullback", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_verified_solve_and_pullback_contains_exact_rational_result():
    basis = np.diag([3., 7.])
    target = np.array([[1., 2.], [3., 4.]])
    approximate = np.linalg.solve(basis, target)
    q = np.array([[2., -1.], [-1., 4.]])
    result = module.certify_stored_pullback(basis, target, approximate,
                                          q[None, :1, :1], q[None, 1:, :1], q[None, 1:, 1:])
    exact = [[F(int(target[i, j]), int(basis[i, i])) for j in range(2)] for i in range(2)]
    error_squared = sum(sum(F(int(q[i, j])) *
                            (exact[i][k] * exact[j][l]
                             - F(float(approximate[i, k])) * F(float(approximate[j, l])))
                            for i in range(2) for j in range(2)) ** 2
                        for k in range(2) for l in range(2))
    assert 0 < error_squared <= F(result["pullback_coordinate_error_frobenius_upper"]) ** 2
    assert result["coordinate_bound_requires_external_verification"] is False
    assert result["operand_binary64_SHA256"]["basis"] == module.coordinate._array_hash(basis)
    assert result["FULL_BHSM_COMPLETE"] is False
    assert result == module.certify_stored_pullback(basis, target, approximate,
                                                   q[None, :1, :1], q[None, 1:, :1], q[None, 1:, 1:])


def test_false_supplemental_validation_stops_before_geometry_load(monkeypatch):
    monkeypatch.setattr(module.blocks, "build_payload", lambda: {"validation_passed": False})
    monkeypatch.setattr(module.supplement, "_load_geometry", lambda: pytest.fail("must not read geometry"))
    with pytest.raises(RuntimeError, match="complete current"):
        module.build_payload()


def test_stale_supplemental_fingerprint_stops_before_geometry_load(monkeypatch):
    monkeypatch.setattr(module.blocks, "build_payload", lambda: {
        "validation_passed": True, "campaign_fingerprint": "old"})
    monkeypatch.setattr(module.supplement, "_fingerprint", lambda: "current")
    monkeypatch.setattr(module.supplement, "_load_geometry", lambda: pytest.fail("must not read geometry"))
    with pytest.raises(RuntimeError, match="fingerprint changed"):
        module.build_payload()


def test_complex_solve_data_rejected_before_silent_cast():
    with pytest.raises(ValueError, match="real binary64"):
        module.certify_stored_pullback(np.eye(2, dtype=complex), np.ones((2, 1)),
                                      np.ones((2, 1)), *[np.ones((1, 1, 1))] * 3)
